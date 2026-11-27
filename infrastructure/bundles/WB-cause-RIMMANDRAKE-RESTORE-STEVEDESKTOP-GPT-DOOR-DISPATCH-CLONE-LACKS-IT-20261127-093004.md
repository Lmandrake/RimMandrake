# WB-cause-RIMMANDRAKE-RESTORE-STEVEDESKTOP-GPT-DOOR-DISPATCH-CLONE-LACKS-IT-20261127-093004

Step 1 (class): RIMMANDRAKE_RENEW_STEVEDESKTOP_CODEX_LOGIN_REFRESH_REVOKED is REAL. SteveDesktop gpt_door status --probe gave EXPIRED, probe=AUTH, rc=20.

Group 1 (done, 2026-11-27 01:40 PST): the agent did the device login (tool_traps.md: re-login is the agent's act). gpt_door.py renew --no-open ran on SteveDesktop, and the device page was finished in the Windows Chrome on Archmagi with OS-level screenshot, click and SendKeys. Result: SIGNED_IN, probe=ANSWERED. The outcome check holds. Evidence: /mnt/d/ClaudeWork/scratch/codexlogin_steve_20261127/after.log.

A fault found on the way and fixed: win_reexec.py mangled a Windows-native out path given to system_screenshot.py. The file landed in the cwd and the tool crashed. Fixed at 732768e, test first, with selftest_system_tools_wsl.py red before and green after. The fresh-reader ticket is filed.
