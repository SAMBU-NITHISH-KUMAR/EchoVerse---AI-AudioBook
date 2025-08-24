---

### 8. scripts/run_app.bat (Windows)
```batch
@echo off
echo Starting EchoVerse Application...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements if needed
pip install -r requirements.txt

REM Run the application
echo.
echo Opening EchoVerse in your browser...
echo Press Ctrl+C to stop the application
echo.
streamlit run echoverse_app.py

pause