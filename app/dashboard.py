from pathlib import Path
import streamlit as st
from ecsc_rag.core import load
st.set_page_config(page_title='ECSCRAG',layout='wide'); st.title('Evidence-Calibrated Self-Correcting RAG'); st.caption('Local bounded-corpus demo; confidence is not a guarantee.')
@st.cache_resource
def get_pipe(): return load(Path(__file__).resolve().parents[1])
q=st.text_input('Question','When did Beyoncé release her first solo album?'); method=st.selectbox('System',['B4_full','B3_corrected','B2_hybrid','B1_bm25','B0_closed_book'])
if st.button('Answer'):
 try:
  z=get_pipe().answer(q,method); st.subheader('Result'); st.write('I could not find enough supporting evidence to answer reliably.' if z['abstained'] else z['answer']); st.metric('Confidence',f"{z['confidence']:.1%}"); st.caption(z['confidence_meaning']); st.write(f"Latency {z['latency_ms']:.1f} ms; {z['retrieval_calls']} retrieval call(s)")
  st.subheader('Evidence');
  for e in z['evidence']: st.markdown(f"**{e['chunk_id']} — {e['title']}**\n\n> {e['text']}")
  st.subheader('Correction events'); st.json(z['events'])
 except FileNotFoundError as e: st.error(f'Missing local artifact: {e}. Run preparation/training scripts.')

