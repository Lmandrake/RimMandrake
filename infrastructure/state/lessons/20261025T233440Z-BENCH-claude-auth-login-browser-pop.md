'claude auth login' run headless on a WSL box prints 'Opening browser to sign in' and may open a tab on that machine's Windows desktop; set BROWSER=true in its environment when the owner is meant to open the URL on his own device. It accepts --email as login_hint only; verify the logged-in email afterwards.
home: claude-remote-control
