$ErrorActionPreference = 'Stop'
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -e .
Write-Host 'Setup complete. Windows compatibility has not been execution-tested by the supplied Linux run.'
