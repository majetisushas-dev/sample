from pathlib import Path
import json,random,time,joblib,platform,sys
import numpy as np,pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix,accuracy_score,f1_score,brier_score_loss
from ecsc_rag.core import sentences,normalize,feat,Pipeline,em,f1
R=Path(__file__).resolve().parents[1]; docs=[json.loads(x) for x in (R/'data/processed/corpus.jsonl').read_text().splitlines()]; byid={x['id']:x for x in docs}; rng=random.Random(2026)
train=json.loads((R/'data/splits/train.json').read_text()); arts=list(set(q['article_id'] for q in train)); rng.shuffle(arts); trarts=set(arts[:int(.8*len(arts))]); X=[]; y=[]; istrain=[]
for q in train:
 ss=sentences(byid[q['doc_id']]['text']); pos=[s for s in ss if any(normalize(a) in normalize(s) for a in q['answers'])]; neg=[s for s in ss if not any(normalize(a) in normalize(s) for a in q['answers'])]
 if pos and neg:
  for s,label,a in [(pos[0],1,q['answers'][0]),(rng.choice(neg),0,rng.choice(neg)[:80])]: X.append(feat(q['question'],a,s)[0]); y.append(label); istrain.append(q['article_id'] in trarts)
X=np.array(X); y=np.array(y); m=np.array(istrain); verifier=LogisticRegression(max_iter=1000,class_weight='balanced',random_state=2026).fit(X[m],y[m]); pred=verifier.predict(X[~m]); report={'task':'answer-bearing cited-sentence proxy, not semantic entailment','labels':{'1':'contains annotated gold answer string','0':'same-passage sentence without annotated answer; weak and possibly ambiguous'},'seed':2026,'split_unit':'article_id','train_pairs':int(m.sum()),'heldout_pairs':int((~m).sum()),'accuracy':accuracy_score(y[~m],pred),'macro_f1':f1_score(y[~m],pred,average='macro'),'class_report':classification_report(y[~m],pred,output_dict=True,zero_division=0),'confusion_matrix':confusion_matrix(y[~m],pred).tolist(),'majority_baseline_accuracy':max(np.mean(y[~m]),1-np.mean(y[~m]))}
joblib.dump(verifier,R/'models/trained/verifier.joblib'); (R/'models/trained/verifier_config.json').write_text(json.dumps(report,indent=2)); (R/'results/classifier_report.json').write_text(json.dumps(report,indent=2)); (R/'results/logs/verifier_training.jsonl').write_text(json.dumps(report)+'\n')
pipe=Pipeline(docs,verifier)
def raw(rows):
 out=[]
 for q in rows:
  z=pipe.answer(q['question'],'B3_corrected'); x=feat(q['question'],z['raw_candidate'],z['evidence'][0]['text'],z['events'][-1]['support_probability'],len(z['events'])-1); out.append((q,z,np.c_[x,[[z['support_probability']]]][0],em(z['raw_candidate'],q['answers'])))
 return out
cal=raw(json.loads((R/'data/splits/calibration.json').read_text())); C=LogisticRegression(max_iter=1000,class_weight='balanced',random_state=2026).fit(np.array([x[2] for x in cal]),np.array([x[3] for x in cal])); val=raw(json.loads((R/'data/splits/validation.json').read_text())); vp=C.predict_proba(np.array([x[2] for x in val]))[:,1]; vy=np.array([x[3] for x in val]); choices=[]
for t in sorted(set(vp)):
 z=vp>=t; choices.append((1-vy[z].mean() if z.any() else 1,z.mean(),t))
ok=[x for x in choices if x[0]<=.2 and x[1]>0]; ch=max(ok,key=lambda x:x[1]) if ok else min(choices,key=lambda x:x[0]); pipe.calibrator=C; pipe.threshold=float(ch[2]); joblib.dump(C,R/'models/trained/calibrator.joblib'); (R/'models/trained/calibrator_meta.json').write_text(json.dumps({'target':'exact-match correctness','fit_split':'calibration','threshold_split':'validation','threshold':pipe.threshold,'target_risk':.2,'validation_risk':ch[0],'validation_coverage':ch[1],'note':'empirical objective, not guarantee'},indent=2))
test=json.loads((R/'data/splits/test.json').read_text()); rows=[]; methods=['B0_closed_book','B1_bm25','B2_hybrid','B3_corrected','B4_full']
for q in test:
 for method in methods:
  z=pipe.answer(q['question'],method); rows.append({'question_id':q['id'],'question':q['question'],'gold_answers':q['answers'],'gold_doc_id':q['doc_id'],'method':method,**z,'em':em(z['answer'],q['answers']),'f1':f1(z['answer'],q['answers']),'gold_retrieved':any(e['chunk_id']==q['doc_id'] for e in z['evidence'])})
for q in test[:50]:
 p2=Pipeline([d for d in docs if d['id']!=q['doc_id']],verifier,C,pipe.threshold); z=p2.answer(q['question']); rows.append({'question_id':q['id']+'::withheld','question':q['question'],'gold_answers':q['answers'],'gold_doc_id':q['doc_id'],'condition':'controlled_gold_document_withheld','method':'B4_full_withheld',**z,'em':em(z['answer'],q['answers']),'f1':f1(z['answer'],q['answers']),'gold_retrieved':False})
(R/'results/per_question_predictions.jsonl').write_text('\n'.join(map(json.dumps,rows))+'\n'); print(f'trained and wrote {len(rows)} predictions')
