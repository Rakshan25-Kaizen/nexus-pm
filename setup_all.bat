@echo off
cd /d "%~dp0"
del nexuspm.db
python -m data.seed
python -m scripts.check_hindsight
