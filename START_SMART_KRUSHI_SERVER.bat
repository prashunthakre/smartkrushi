@echo off
title SmartKrushi Production Server (Python + Scikit-Learn ML + SQLite)
cd /d "%~dp0"
echo Starting SmartKrushi Production Server on http://localhost:8000 ...
start "" "http://localhost:8000/index.html"
python smart_krushi_server.py
pause

