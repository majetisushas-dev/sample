from pathlib import Path
import zipfile,hashlib,json
R=Path(__file__).resolve().parents[1]; out=R/'deliverables/ecsc_rag_pilot.zip'; skip={'.git','.venv','__pycache__','data/raw'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
 for p in R.rglob('*'):
  rel=p.relative_to(R)
  if p.is_file() and not any(x in rel.parts for x in skip) and p!=out: z.write(p,rel)
h=hashlib.sha256(out.read_bytes()).hexdigest(); (R/'deliverables/package_manifest.json').write_text(json.dumps({'file':out.name,'sha256':h,'offline_capable':False,'reason':'initial SQuAD download required; trained demo works offline once corpus is prepared'},indent=2)); print(out,h)
