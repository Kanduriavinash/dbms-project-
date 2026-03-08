@echo off
REM Batch file to run app with PostgreSQL
echo Setting DATABASE_URL...
set DATABASE_URL=postgresql://postgres:avinash@localhost:5432/retail_db
echo.
echo Starting application...
echo.
python app.py

