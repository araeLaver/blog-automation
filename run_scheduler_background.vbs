Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d C:\Develop\unble\blog-automation && python run_scheduler.py schedule > auto_publisher_v2.log 2>&1", 0, False