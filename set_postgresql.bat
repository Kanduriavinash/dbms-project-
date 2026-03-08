@echo off
REM Batch script to set PostgreSQL connection
REM Run this BEFORE running python app.py

echo ========================================
echo PostgreSQL Setup for RIMS
echo ========================================
echo.

set /p username="PostgreSQL Username [postgres]: "
if "%username%"=="" set username=postgres

set /p password="PostgreSQL Password: "

set /p host="Host [localhost]: "
if "%host%"=="" set host=localhost

set /p port="Port [5432]: "
if "%port%"=="" set port=5432

set /p database="Database Name [rims_db]: "
if "%database%"=="" set database=rims_db

REM Build connection string
set DATABASE_URL=postgresql://%username%:%password%@%host%:%port%/%database%

echo.
echo ========================================
echo DATABASE_URL SET!
echo ========================================
echo.
echo Connection string: %DATABASE_URL%
echo.
echo Now run:
echo   python check_database.py
echo   python app.py
echo.

