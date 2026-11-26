Killing the WSL2 interop shim of a Windows python.exe (killpg, TERM or KILL) ends that python.exe, but never its own Windows children: they live on with a dead ParentProcessId (measured on Archmagi 2026-11-26). To end a Windows tree from WSL, tag the root's command line (python.exe -X <tag>=<id>), read Win32_Process, and taskkill the tagged roots and their descendants BEFORE the Linux side dies.
item: RIMMANDRAKE_KILL_WINDOWS_CHILD_ON_TESTQ_CANCEL_ORPHAN_DROVE_STEVE2
home: skills/wsl-windows-plumbing
