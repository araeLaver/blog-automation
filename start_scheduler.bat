@echo off
echo [%date% %time%] Starting Blog Automation Scheduler...
cd /d C:\Develop\unble\blog-automation
python src\scheduler.py schedule
pause