@echo off
chcp 65001 >nul
echo =================================================================
echo        KİRA VE TAHLİYE TAAHHÜDÜ SİSTEMİ BAŞLATICI
echo =================================================================
echo.
echo Sunucu hazırlanıyor ve başlatılıyor...
echo Port: 8092
echo.
start "" http://localhost:8092
python server.py
pause
