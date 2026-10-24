@echo off
:loop
docker cp cowrie:/cowrie/cowrie-git/var/log/cowrie/cowrie.json live.json >nul 2>&1
timeout /t 5 /nobreak >nul
goto loop