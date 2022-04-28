@echo off

call %~dp0watermark_bot\venv\scripts\activate

cd %~dp0watermark_bot

set TOKEN_TELEGRAM=5025388636:AAGYoKcekA651jA65C6gLIDiMaWGal9-GiA

python bot_telegram.py

pause