# DOORBELL_HARDEN_SPARE_OWNER_TYPING

An asyncRewake ring wakes a window that `claude agents` reports idle, even when the owner is composing text at that
prompt: there is no input-focus or draft check. Seat windows are agent windows, so the risk is small, but it is real.
Find a signal (prompt draft, terminal focus, recent keystrokes) or accept the risk explicitly.
Review evidence: D:\ClaudeWork\rimmandrake\review_dispatcher\gpt_a.md (finding 14).

## Decision (BENCH helper, 2026-10-27): risk ACCEPTED, no code
Signals looked at, from WSL:
- Prompt draft: Claude Code exposes no draft text to hooks, `claude agents` or the session files. Not readable.
- Terminal focus: `idle_probe` already reads the foreground PROCESS name (powershell/user32), but every seat window is
  a Windows Terminal tab under one wt.exe process; the foreground process cannot say which tab (which seat) has focus.
- Recent keystrokes: GetLastInputInfo is machine-wide. It says "the owner touched the machine", not "typed into
  window X". Gating every ring on it would also stall all wakes whenever he browses, i.e. trade a rare collision for
  routine starvation; a guess we should not build.
Why the risk is small: a woken window receives the ring as a system reminder at the prompt; it does not delete or send
a half-typed draft, and the message tells the window to finish any mid-task work first. Game-touching work is already
guarded separately (ringed `next` re-measures the owner; `bridge take` idle rule). Reopen if a signal appears
(e.g. Claude Code exposing an input-draft flag to hooks).
