Set WshShell = CreateObject("WScript.Shell")
Set oShellLink = WshShell.CreateShortcut("C:\Users\DELL\Desktop\NeuroRepurposing Explorer.lnk")
oShellLink.TargetPath = "D:\alzheimer\run_dashboard.ps1"
oShellLink.WorkingDirectory = "D:\alzheimer"
oShellLink.IconLocation = "C:\Windows\System32\SHELL32.dll, 13"
oShellLink.Description = "Open the Alzheimer repurposing dashboard"
oShellLink.Save
