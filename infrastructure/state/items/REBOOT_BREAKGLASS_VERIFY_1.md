# REBOOT_BREAKGLASS_VERIFY_1

Verify the break-glass path survives a Windows reboot: `WSL Keepalive` must bring
tailscaled back before login, and the fleet may need a hand.

Filed 2026-09-19 by BENCH, after building Layer 3 (`claude-remote-control` skill,
`D:\Luke\dev\claude-remote-control`). Everything below works TODAY, measured; what is
unknown is whether it survives the one event that will happen while the owner is away.

## Why it matters

A week-long trip's whole recovery story is: phone → Tailscale → SSH into WSL → `rc`.
If a Windows Update reboot leaves the machine at the lock screen, `WSL Keepalive` is a
**logon** task and will not have run — WSL is down, tailscaled with it, and the phone
cannot reach the machine at all. That is the trip-ending failure the layer exists to
prevent, so it must be tested deliberately rather than discovered.

## spec

Do this at the desk, on a day when losing the fleet for ten minutes is fine.

1. Note the current state: `rc` (tailscale peers, live windows, server), `tailscale ip -4`.
2. Reboot Windows. **Do not log in.** Wait ~3 minutes.
3. From the phone (cellular, not the house wifi — proves the tailnet, not the LAN):
   open Termius → `mandrake@archmagi-wsl`.
   - **connects** → the logon task is not needed at the lock screen; record that and stop.
   - **refused / no route** → expected; log in to Windows, wait 60 s, try again. If it
     then connects, the task works but only after login — convert it to a *startup*
     task (`-AtStartup`, run whether or not the user is logged on) and repeat from 2.
4. Once in: does `rc` show the fleet? The Desktop shortcut is not an autostart, so the
   likely answer is no windows at all. Decide with the owner whether the fleet should
   autostart at logon (same shortcut, a second scheduled task) or stay manual.
5. Check `rc account` still lists both slots with their token days — a reboot must not
   disturb `~/.claude/accounts/`.

## verify

Record each answer as a row in
`D:\Luke\dev\claude-remote-control\references\incident-log.md`, with the date and the
exact text of any refusal. Close this item on that commit.

## Traps

- A *logon* task is not a *startup* task; the difference only shows at a lock screen.
- Test over cellular. On house wifi Tailscale may route directly over the LAN, which
  proves nothing about reachability from an airport.
- `rc fleet` needs Windows interop — MEASURED available from a Tailscale SSH shell
  2026-09-19, but that was with a user logged in; unknown at the lock screen.
