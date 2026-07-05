Set shell = CreateObject("WScript.Shell")
command = "powershell.exe -ExecutionPolicy Bypass -File " & Chr(34) & "D:\alzheimer\run_dashboard.ps1" & Chr(34)
shell.Run command, 0, False