import json,math,re,time
from pathlib import Path
import joblib,numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
T=re.compile(r'(?u)\b\w\w+\b')
def tokens(s): return T.findall(s.lower())
def sentences(s): return [x.strip() for x in re.split(r'(?<=[.!?])\s+',s) if x.strip()]
def normalize(s): return ' '.join(re.sub(r'[^a-z0-9 ]',' ',re.sub(r'\b(a|an|the)\b',' ',s.lower())).split())
def em(p,gs): return float(any(normalize(p)==normalize(g) for g in gs))
def f1(p,gs):
 pt=tokens(normalize(p)); best=0
 for g in gs:
  gt=tokens(normalize(g)); c=sum(min(pt.count(x),gt.count(x)) for x in set(pt)); pr=c/len(pt) if pt else 0; rc=c/len(gt) if gt else 0; best=max(best,2*pr*rc/(pr+rc) if pr+rc else float(pt==gt))
 return best
def feat(q,a,e,score=0,rounds=0):
 q,a,e=set(tokens(q)),set(tokens(a)),set(tokens(e)); return np.array([[len(a&e)/(len(a)or 1),len(q&e)/(len(q)or 1),float(a<=e),min(len(a)/20,3),min(len(e)/60,3),score,rounds,1]])

class Retriever:
 def __init__(self,docs):
  self.docs=docs; self.v=TfidfVectorizer(stop_words='english',ngram_range=(1,2),min_df=2,sublinear_tf=True); self.X=self.v.fit_transform([d['text'] for d in docs]); n=max(2,min(64,*self.X.shape)); self.svd=TruncatedSVD(n-1,random_state=2026); self.D=Normalizer().fit_transform(self.svd.fit_transform(self.X))
 def search(self,q,k=5,mode='hybrid',exclude=()):
  st=time.perf_counter(); x=self.v.transform([q]); s=(self.X@x.T).toarray().ravel(); d=(self.D@Normalizer().fit_transform(self.svd.transform(x)).T).ravel()
  def rank(z): o=np.lexsort((np.arange(len(z)),-z)); r=np.empty(len(z),int); r[o]=np.arange(len(z)); return r
  z=s if mode=='bm25' else 1/(60+rank(s))+1/(60+rank(d)); out=[]
  for i in np.lexsort((np.arange(len(z)),-z)):
   if self.docs[i]['id'] in exclude: continue
   out.append({**self.docs[i],'score':float(z[i]),'rank':len(out)+1})
   if len(out)==k: break
  return out,(time.perf_counter()-st)*1000
def evidence(q,hits):
 qs=set(tokens(q)); choices=[]
 for h in hits:
  for j,s in enumerate(sentences(h['text'])): choices.append((len(qs&set(tokens(s)))/math.sqrt(len(tokens(s))+1),-h['rank'],-j,h,s))
 x=max(choices,key=lambda z:z[:3]); return x[3],x[4]
def extract(q,s):
 ql=q.lower()
 if re.search(r'when|what year|which year',ql):
  m=re.search(r'\b(?:1[5-9]\d{2}|20\d{2})\b',s)
  if m:return m.group()
 if re.search(r'how many|how much|what percent',ql):
  m=re.search(r'\b\d[\d,.]*(?:\s*(?:percent|%|million|billion))?',s,re.I)
  if m:return m.group()
 if ql.startswith('who'):
  ns=[x.strip() for x in re.findall(r'\b(?:[A-Z][\w-]+(?:\s+|$)){1,4}',s) if normalize(x) not in normalize(q)]
  if ns:return max(ns,key=len)
 if ql.startswith('where'):
  m=re.search(r'\b(?:in|at|from|near)\s+([A-Z][\w-]*(?:\s+[A-Z][\w-]*){0,3})',s)
  if m:return m.group(1)
 return s.strip().rstrip('.')

class Pipeline:
 def __init__(self,docs,verifier,calibrator=None,threshold=.5): self.docs=docs; self.verifier=verifier; self.calibrator=calibrator; self.threshold=threshold; self.r=Retriever(docs)
 def answer(self,q,method='B4_full'):
  st=time.perf_counter()
  if method=='B0_closed_book': return {'answer':'','raw_candidate':'','abstained':True,'confidence':0.,'evidence':[],'events':[],'latency_ms':0.,'retrieval_calls':0,'generation_calls':0,'support_probability':0.}
  hits,rt=self.r.search(q,mode='bm25' if method=='B1_bm25' else 'hybrid'); h,e=evidence(q,hits); a=extract(q,e); x=feat(q,a,e,h['score']); sp=float(self.verifier.predict_proba(x)[0,1]); events=[{'round':0,'query':q,'candidate':a,'chunk_id':h['id'],'support_probability':sp,'retrieval_ms':rt}]; calls=1
  if method in ('B3_corrected','B4_full') and sp<.62:
   q2=q+' '+' '.join([w for w in tokens(e) if w not in set(tokens(q))][:8]); hs,rt=self.r.search(q2,mode='hybrid',exclude=[h['id']]); calls=2; h2,e2=evidence(q,hits+hs); a2=extract(q,e2); x2=feat(q,a2,e2,h2['score'],1); sp2=float(self.verifier.predict_proba(x2)[0,1]); events.append({'round':1,'query':q2,'candidate':a2,'chunk_id':h2['id'],'support_probability':sp2,'retrieval_ms':rt,'reason':'support below 0.62; changed retrieval'})
   if sp2>sp: h,e,a,x,sp=h2,e2,a2,x2,sp2
  conf=sp; abst=False
  if method=='B4_full' and self.calibrator is not None: conf=float(self.calibrator.predict_proba(np.c_[x,[[sp]]])[0,1]); abst=conf<self.threshold
  return {'answer':'' if abst else a,'raw_candidate':a,'abstained':abst,'confidence':conf,'confidence_meaning':'estimated exact-match correctness for B4; evidence proxy otherwise','support_probability':sp,'evidence':[{'chunk_id':h['id'],'title':h['title'],'text':e,'quote_valid':e in h['text']}],'events':events,'latency_ms':(time.perf_counter()-st)*1000,'retrieval_calls':calls,'generation_calls':len(events)}
def load(root=Path('.')):
 docs=[json.loads(x) for x in (root/'data/processed/corpus.jsonl').read_text().splitlines()]; v=joblib.load(root/'models/trained/verifier.joblib'); c=joblib.load(root/'models/trained/calibrator.joblib'); meta=json.loads((root/'models/trained/calibrator_meta.json').read_text()); return Pipeline(docs,v,c,meta['threshold'])
