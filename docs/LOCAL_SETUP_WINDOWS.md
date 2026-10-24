# Local setup — Windows

## Requirements
- Windows 10/11
- Python 3.11 or 3.12
- Git (optional if downloading the ZIP from GitHub)

## Run locally
1. Clone or download this repository.
2. Open PowerShell in the project folder.
3. Create and activate a virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Copy the environment template and enter your credentials locally:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   Keep `.env` private. Never commit API tokens to GitHub.

6. Start the API:

   ```powershell
   uvicorn app.main:app --reload
   ```

7. Open http://127.0.0.1:8000, /health, or /docs.

## Run tests
```powershell
pytest
```

## Current stage limitations
This is the initial runnable scaffold. Dhan authentication/data requests, the strategy plugin registry, backtesting, database persistence, dashboard, and paper-trading simulator are not implemented yet. The status endpoint only checks whether credentials are present; it does not validate them. Live order execution is intentionally not implemented.
