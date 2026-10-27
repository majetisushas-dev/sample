# Windows CPU reproducibility

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe scripts\prepare_data.py
.\.venv\Scripts\python.exe scripts\run_all.py
.\.venv\Scripts\python.exe scripts\generate_results.py
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\streamlit.exe run app\dashboard.py
.\.venv\Scripts\python.exe scripts\build_presentation.py
pdflatex -interaction=nonstopmode -output-directory paper paper\manuscript.tex
.\.venv\Scripts\python.exe scripts\audit_artifacts.py
.\.venv\Scripts\python.exe scripts\package_deliverables.py
```

Initial downloads require a network; inference is local afterward. The recorded test used Linux, 3 vCPUs and 9.7 GiB RAM. Windows compatibility is designed, not execution-tested.

