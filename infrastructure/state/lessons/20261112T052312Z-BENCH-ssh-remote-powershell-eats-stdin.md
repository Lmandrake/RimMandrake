2026-11-11: 'ssh host bash -s < script.sh' silently stops partway when a command in the script starts a Windows child (powershell.exe via interop, e.g. wc.py diskfree): the child reads the ssh stdin and swallows the rest of the script, with no error. Copy the script over (scp) and run 'ssh host "bash ~/script.sh </dev/null"' instead. Also: PowerShell over ssh needs -EncodedCommand (UTF-16LE base64 from iconv); a quoted -Command string fails with 'ScriptBlock should only be specified as a value of the Command parameter'.
item: NONE
home: wsl-windows-plumbing
