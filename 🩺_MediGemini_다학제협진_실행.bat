@echo off
chcp 65001 > nul
title Medi-Gemini v7.0 - 1인 대학병원 다학제 협진 콘솔
echo ===============================================================
echo   Medi-Gemini v7.0 로컬 진료실 다학제 협진 웹 앱 시작 중...
echo   브라우저가 자동으로 열립니다 (http://127.0.0.1:8765)
echo ===============================================================
python -X utf8 "%~dp0app\medi_gemini_local_app.py" --port 8765
pause
