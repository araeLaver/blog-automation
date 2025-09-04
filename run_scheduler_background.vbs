Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd /c cd /d C:\Develop\unble\blog-automation && python src\scheduler.py schedule > scheduler.log 2>&1", 0, False