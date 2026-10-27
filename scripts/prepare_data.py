from pathlib import Path
import hashlib,json,random,urllib.request
R=Path(__file__).resolve().parents[1]; raw=R/'data/raw/dev-v2.0.json'; url='https://raw.githubusercontent.com/rajpurkar/SQuAD-explorer/master/dataset/dev-v2.0.json'; sha='80a5225e94905956a6446d296ca1093975c4d3b3260f1d6c8f68bc2ab77182d8'
for x in ['data/raw','data/processed','data/splits','data/manifests','models/trained','results/logs','results/plots','results/tables','results/annotation','deliverables','paper/figures','paper/tables','presentation','app','docs']: (R/x).mkdir(parents=True,exist_ok=True)
if not raw.exists(): urllib.request.urlretrieve(url,raw)
assert hashlib.sha256(raw.read_bytes()).hexdigest()==sha
d=json.loads(raw.read_text()); docs=[]; qs=[]
for ai,a in enumerate(d['data']):
 for pi,p in enumerate(a['paragraphs']):
  did=f'squad2-a{ai:04d}-p{pi:03d}'; docs.append({'id':did,'title':a['title'],'text':p['context'],'article_id':ai})
  for q in p['qas']:
   if not q.get('is_impossible') and q.get('answers'): qs.append({'id':q['id'],'question':q['question'],'answers':sorted(set(x['text'] for x in q['answers'])),'doc_id':did,'article_id':ai})
r=random.Random(2026); arts=list(set(x['article_id'] for x in qs)); r.shuffle(arts); sizes={'train':360,'calibration':100,'validation':100,'test':150}; out={}; used=set(); seen=set()
for name,n in sizes.items():
 pool=[x for x in qs if x['article_id'] not in used and x['id'] not in seen]; r.shuffle(pool); take=pool[:n]; out[name]=take; used|={x['article_id'] for x in take}; seen|={x['id'] for x in take}
 if len(take)<n:
  extra=[x for x in qs if x['id'] not in seen][:n-len(take)]; out[name]+=extra; seen|={x['id'] for x in extra}
(R/'data/processed/corpus.jsonl').write_text('\n'.join(map(json.dumps,docs))+'\n')
for k,v in out.items():(R/f'data/splits/{k}.json').write_text(json.dumps(v,indent=2))
manifest={'dataset':'SQuAD 2.0 dev-v2.0','source':url,'sha256':sha,'license':'CC BY-SA 4.0 per official repository','corpus_documents':len(docs),'answerable_questions':len(qs),'split_counts':{k:len(v) for k,v in out.items()},'seed':2026}
(R/'data/manifests/dataset.json').write_text(json.dumps(manifest,indent=2)); (R/'data/manifests/leakage_audit.json').write_text(json.dumps([{'a':a,'b':b,'question_overlap':len({x['id'] for x in out[a]}&{x['id'] for x in out[b]}),'article_overlap':len({x['article_id'] for x in out[a]}&{x['article_id'] for x in out[b]})} for a in out for b in out if a<b],indent=2)); print(manifest)

