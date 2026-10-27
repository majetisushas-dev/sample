from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle
from reportlab.lib import colors
import pandas as pd,json
R=Path(__file__).resolve().parents[1]; M=pd.read_csv(R/'results/metrics.csv'); S=json.loads((R/'results/summary_metrics.json').read_text()); styles=getSampleStyleSheet(); story=[Paragraph('Evidence-Calibrated Self-Correcting RAG — Guide Results',styles['Title']),Paragraph('Measured Linux CPU pilot',styles['Heading2']),Paragraph('Built: bounded hybrid retrieval, extractive candidate selection, project-trained answer-bearing-evidence proxy, one retrieval-changing correction, exact-match calibration, citations, and abstention.',styles['BodyText']),Spacer(1,12)]
data=[list(M.columns)]+[[str(x)[:12] for x in row] for row in M.round(3).itertuples(index=False,name=None)]; t=Table(data,repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#17324d')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('FONTSIZE',(0,0),(-1,-1),6),('GRID',(0,0),(-1,-1),.25,colors.grey)])); story += [t,Spacer(1,12),Paragraph(f"Calibration: ECE {S['ece_10_equal_width']:.3f}; Brier {S['brier_exact_match']:.3f}; AURC {S['aurc_trapezoid']:.3f}.",styles['BodyText']),Paragraph('Important limitations: rule-based extractive generator, support proxy rather than entailment, bounded SQuAD corpus, no human labels, Linux-only execution. Full-system zero coverage is a negative result, not a zero-risk guarantee.',styles['BodyText']),Paragraph('Inspect results/dashboard.html, plots/, tables/, example_outputs.json, and per_question_predictions.jsonl.',styles['BodyText'])]
SimpleDocTemplate(str(R/'results/guide_results.pdf'),pagesize=A4).build(story)

