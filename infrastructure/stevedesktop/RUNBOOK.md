# SteveDesktop bring-up runbook (2026-10-25)

**Goal:** by Monday morning SteveDesktop (Windows 10, Home or Pro) runs on its own for a week.
It must come back after reboots, Windows Update and power cuts, stay reachable and controllable
from Archmagi (192.168.86.221), and keep itself up to date (git pull, apt, winget, Claude Code).

**Plan this serves:** `design/RimMandrake/stevedesktop_bringup_plan_2026-10-24.md` (Phase 1 plus
the unattended part of Phase 2). The principle stands: SteveDesktop is a token-free runner, not a
second agent farm.

**Files here:**

| File | Runs on | What it does |
|---|---|---|
| `bootstrap.ps1` | SteveDesktop, once, elevated | Everything on Windows that can be scripted. Logs `C:\SteveDesktop\bootstrap.log`, state `C:\SteveDesktop\status.json` |
| `bootstrap_wsl.sh` | SteveDesktop WSL, as root (called by bootstrap.ps1) | apt, git, gh, node, Claude Code, keys, runner clone, systemd, Tailscale, self-upgrade timer |
| `serve_bootstrap.sh` / `serve_bootstrap.py` | Archmagi | Serves the bootstrap on the LAN, and receives its reports into `D:\ClaudeWork\stevedesktop\serve\reports\` |
| `verify_from_archmagi.sh` | Archmagi WSL | One line per door and health check |

Legend: **YOU** = the owner at SteveDesktop's keyboard. **AGENT** = an agent on Archmagi, remotely.
Times are hands-on minutes; waits are listed separately.

---

## How the script gets onto SteveDesktop (ranked)

1. **Archmagi serves it over HTTP on the LAN (chosen).** One typed line, no media. MEASURED
   2026-10-25 on Archmagi: Windows python serves `/b`, `/archmagi.pub` and `POST /report` on
   192.168.86.221:8767 (`serve_bootstrap.sh --test`). Archmagi's LAN profile is Private, and the
   firewall already has an inbound Allow rule for the Store python3.13.exe on Private and Public.
   A request from another LAN machine is UNMEASURED until step 1. It needs Archmagi awake with
   the server running (AGENT step A0).
2. **USB stick.** AGENT runs `serve_bootstrap.sh --stage` and copies `D:\ClaudeWork\stevedesktop\serve`
   to a stick. On SteveDesktop: Win+R, then
   `powershell -ep bypass -f E:\serve\bootstrap.ps1` (use the stick's drive letter). The
   script stages from the stick rather than the network. Its reports then do not reach Archmagi, so
   read the IP off the screen.
3. **Google Drive for desktop**, if SteveDesktop has it: the same as USB from `G:\My Drive\...`.
   UNMEASURED whether it is installed there.
4. GitHub raw: no. The repo is private and that would need a token on the machine.

---

## Recommended doors (and why)

| # | Door | Needs a Windows logon? | Survives an IP change? | Why it is here |
|---|---|---|---|---|
| 1 | **LAN SSH** into Windows OpenSSH (`ssh <user>@<LAN IP>`) | no (a service) | no (the DHCP reservation covers it) | No third party involved. The first door to open (step 1) |
| 2 | **Tailscale, Windows client** to the same sshd (`ssh <user>@stevedesktop`) | no (`--unattended` service) | **yes** | Works from the phone and off the LAN. The main door for the week |
| 3 | **Tailscale SSH into WSL** (node `stevedesktop-wsl`, like Archmagi's `archmagi-wsl`) | yes (autologon + WSL Keepalive) | yes | Does not depend on Windows sshd. Through `powershell.exe` interop it can repair Windows if door 1/2 breaks |
| 4 | **WSL via Windows SSH** (`ssh <win> "wsl -d Ubuntu -- ..."`) | no (it starts WSL) | as door 1/2 | Reaches WSL even when WSL's own Tailscale is down |
| GUI | **Chrome Remote Desktop** | no (a SYSTEM service; shows the sign-in screen) | yes (relayed by Google) | For dialogs nobody can script: UAC, Steam, BIOS-less recovery, Windows "Restart now" prompts |
| GUI-2 | RDP, **Pro only** (LAN and Tailscale only) | no | via Tailscale | Fallback. It takes over and locks the console session, which can upset a running game |

**Tailscale vs plain LAN SSH:** use both. Plain LAN SSH has no outside dependency and is the
fastest to open. But it breaks if the IP changes, and it is unreachable from the phone. Tailscale
fixes both and costs two logins plus one console setting (steps 3, 4, 6). Tailscale SSH (door 3)
runs only on Linux, so the Windows node uses ordinary OpenSSH over the tailnet.

**Why Chrome Remote Desktop, not RustDesk or RDP:** CRD shares the console session the game
runs in (RDP replaces it). It runs as a service that works at the sign-in screen. Google updates
it and relays it, so it opens no inbound port, and it works from Archmagi's browser and the phone
app. RustDesk is not in the winget catalogue (checked 2026-10-25: only GitHub release 1.5.0).
Its updates are manual, and without a self-hosted relay it depends on public relays. RDP does not
exist on Home.

---

## AGENT step A0: before he walks over (Archmagi, 1 min)

```bash
/home/mandrake/rm/bench/infrastructure/stevedesktop/serve_bootstrap.sh
```
You should see: `serving: http://192.168.86.221:8767/b http=200`. The server exits by itself
after 4 hours (`--stop` ends it sooner). Keep Archmagi awake until step 6 is done.

---

## YOU: at SteveDesktop (12 steps, about 45 min hands-on, about 90 min elapsed)

Log in to Windows with the account you normally use there. It must be an administrator.

### Step 1: open the SSH door (2 min hands-on, 3-6 min wait)
1. Press **Win+R**, type `powershell`, press Enter.
2. Type exactly this and press Enter:
   ```
   irm http://192.168.86.221:8767/b | iex
   ```
3. Click **Yes** on the User Account Control prompt. A second, blue admin window opens and does the work.

**You should see**, within about 6 minutes, a green box in the admin window:
`SSH READY - Archmagi can log in now`, with **IP**, **MAC**, user and edition. Leave the
window open: it carries on by itself (phase B, about 15 min). Tell the agent "step 1 done".
If you see a red `SSH NOT READY` box, read the FAIL line above it. The usual cause is Windows
Update being unreachable, which blocks the OpenSSH download. The script then tries winget. Carry on
with step 2 anyway; the agent fixes it over Chrome Remote Desktop later.

### Step 2: DHCP reservation (3 min, phone)
Google Home app → **Wi-Fi** → **Settings** (gear) → **Advanced networking** → **DHCP IP
reservations** → **+** → pick the device whose MAC matches the green box → keep the IP it
shows (the one in the green box) → **Save**.
**You should see** SteveDesktop listed with that fixed IP.
Checked 2026-10-25: no agent route exists. The router is a Nest Wifi Pro: its local API is a single
read-only endpoint, there are no Wi-Fi settings on home.google.com, there is no HA write integration and no
emulator. Details are in Custos `docs/INTEGRATIONS.md`, "Router: DHCP reservations cannot be automated".
SteveDesktop is on **Wi-Fi 2**, MAC `04:33:c2:68:51:5a`, and currently leases **192.168.86.87**, so reserve that.

### Step 3: Tailscale on Windows (2 min)
When phase B reaches Tailscale, a browser tab opens at `login.tailscale.com`. If none opens,
click the Tailscale tray icon → **Log in**. Sign in with **Google, lukas.mandrake@gmail.com**. That is the
tailnet Archmagi and your phone are on, **not** `lmandrake.github`. Click **Connect**.
**You should see** "Login successful". In the tray, Tailscale shows Connected as `stevedesktop`.

### Step 4: Tailscale console settings (3 min, any browser, including Archmagi's)
At https://login.tailscale.com/admin/machines:
1. On **stevedesktop**: the **...** menu → **Disable key expiry**. Repeat this for **stevedesktop-wsl** after step 6.
2. **Access controls** tab: if the `"ssh"` section says `"action": "check"`, change it to
   `"accept"` for `autogroup:member` → `autogroup:self`. Otherwise every agent SSH into
   `stevedesktop-wsl` stops at a browser re-auth. (Archmagi's own rule is UNMEASURED; the agent
   checks it with `verify_from_archmagi.sh`.)

**You should see** "Expiry disabled" next to the machine.

### Step 5: reboot through the BIOS (10 min)
When the admin window says `PHASE B DONE - a reboot is needed`, press **Enter**. As the
screen goes black, tap **Del** (or **F2**; the board name is in `status.json`, so ask the agent if
unsure) to enter BIOS setup. Set these three; their names vary by vendor:
- **Restore on AC Power Loss** / *AC Back* / *After Power Failure* → **Power On**
- **Wake on LAN** / *Power On by PCI-E* / *Resume by LAN* → **Enabled**
- **ErP** / *EuP* / *Deep Sleep* → **Disabled**. When enabled it cuts power to the NIC, which kills Wake-on-LAN.

Save and exit (usually **F10**). Log in to Windows.
If no yellow reboot box appears (WSL was already switched on), the window goes straight on to
step 6: do this BIOS part during the step 11 reboot instead.
**You should see** a blue admin window open by itself: the bootstrap resuming.
(SteveDesktop on Wi-Fi rather than a cable: Wake-on-LAN will not work. The green box says
`wired: False`. AC power restore still works.)

### Step 6: let it finish WSL; log in the WSL Tailscale node (2 min, 10-25 min wait)
The resumed window installs Ubuntu and runs `bootstrap_wsl.sh` (apt, gh, node, Claude Code,
Tailscale). A second Tailscale login tab opens, for the node `stevedesktop-wsl`: sign in the same way
as step 3. Then disable its key expiry (step 4.1).
**You should see** `BOOTSTRAP COMPLETE - go to RUNBOOK step 7` in green. If it says
`DONE WITH FAILURES: ...` in yellow, carry on with steps 7-10 while the agent repairs them over
SSH. **Do not leave on Monday** until the agent reports those repaired and steps 11-12 have passed.
A failed WSL step keeps a resume task, so the next logon retries it.
If an Ubuntu window ever asks you to "Create a default Unix user account", type `mandrake`
and any password. The script normally creates that user itself (UNMEASURED on this Windows build).

### Step 7: automatic sign-in (2 min)
Win+R → `C:\SteveDesktop\tools\Autologon64.exe` → **Agree** → Username and Domain are
pre-filled → type the Windows password → **Enable**.
- For a Microsoft-account login, type the account email and its password, not the PIN.
- If you sign in with a PIN only and have forgotten the password, stop here and tell the agent:
  autologon cannot work without a password.

**You should see** "Autologon successfully configured. The autologon password is encrypted."
Why: after an update reboot, Windows must log in by itself, or Steam and WSL never start.

### Step 8: Chrome Remote Desktop (3 min)
In a browser on SteveDesktop open https://remotedesktop.google.com/access, sign in with Google.
Under **Set up remote access**, click **Turn on** (the host is already installed). Name it
`SteveDesktop`, choose a PIN of 6 digits or more, and click **Start**. Keep the PIN yourself: agents
never need it.
**You should see** SteveDesktop listed as **Online**. Check it from Archmagi's browser at the
same address before you leave.

### Step 9: Claude Code login in WSL (3 min)
Start menu → **Ubuntu** → type `claude` → pick **Claude account with subscription** → copy
the URL it prints into the browser → **Authorize** → paste the code back → type `/exit`.
**You should see** the Claude prompt with your account name before you exit.
⚠ Do this in **one** window only, and before anything else uses Claude on SteveDesktop. Never
`/login` in one window while other windows hold Remote Control (the claude-remote-control skill:
every machine-wide Remote Control drop on record was a `/login` in some window). This login is on
SteveDesktop's own credentials and does not touch Archmagi's windows. Do **not** turn on Remote
Control on SteveDesktop.

### Step 10: Steam (3 min)
Open Steam. If asked, sign in with the SteveDesktop account and tick **Remember me**.
1. **Steam → Settings → Interface → Run Steam when my computer starts**: on.
2. Library → RimWorld → **DLC**: Royalty, Ideology, Biotech, Anomaly and Odyssey all show **Installed**.
   Tell the agent which are missing. The every-DLC rule needs all five.
3. Launch RimWorld once to the main menu and quit. This clears the first-run dialogs.
4. Leave Steam **online**, not in Offline Mode. Offline Mode needs a recent online login to
   start, and it blocks the updates that keep it in step with Archmagi.

**You should see** the RimWorld main menu, then Steam left in the tray.

### Step 11: reboot test (1 min hands-on, 5 min wait)
Tell the agent "reboot it". AGENT: `ssh <win> "Restart-Computer -Force"`, then
`verify_from_archmagi.sh`.
**You should see** Windows come back to the desktop **without anyone typing**, and Steam open.
The agent then gets PASS on every door.

### Step 12: power-cut and Wake-on-LAN test (3 min)
1. Shut Windows down cleanly first: Start → Power → **Shut down**. Wait until it is off. Only then
   switch off the PSU switch at the back (or pull the plug) for 10 s, and switch it back on. Never
   cut power while Windows runs: that risks the update store and the WSL disk just before the week.
   **You should see** the PC start by itself (step 5 BIOS), then sign in by itself.
2. AGENT: `ssh <win> "Stop-Computer -Force"`, wait 30 s, `verify_from_archmagi.sh --wake`.
   **You should see** the PC power on with nobody touching it (wired only).

---

## AGENT steps (remote, between and after his steps)

- **A1, after step 1.** Read `/mnt/d/ClaudeWork/stevedesktop/serve/reports/latest.json` (IP, MAC,
  user, edition, Steam DLC folders). Add `~/.ssh/config` hosts `stevedesktop-lan`
  (`HostName <ip>`, `User <user>`) and `stevedesktop` (the Tailscale name). Run `ssh stevedesktop-lan hostname`.
  Record the IP and MAC in Machinist `knowledge/remote-access-relayed.md`.
- **A2, after steps 5-6.** `ssh stevedesktop-lan "Get-Content C:\SteveDesktop\status.json"`. Fix
  every `ok: false` step over SSH; the script is idempotent:
  `ssh stevedesktop-lan "powershell -ep bypass -f C:\SteveDesktop\bootstrap.ps1"`. Phase A/B
  re-runs fast, and it will not reboot without someone pressing Enter (the window would hang, so
  prefer fixing single steps by hand). Report DLC folders against the five.
- **A3, deploy key and runner clone.** On Archmagi, with Archmagi's own gh login:
  ```bash
  ssh stevedesktop-lan "wsl -d Ubuntu -- cat /home/mandrake/.ssh/id_ed25519.pub" > /tmp/steve_wsl.pub
  gh repo deploy-key add /tmp/steve_wsl.pub --repo Lmandrake/RimMandrake --title stevedesktop-wsl-runner --allow-write
  ssh stevedesktop-lan "wsl -d Ubuntu -u root -- bash /mnt/c/SteveDesktop/bootstrap_wsl.sh clone"
  ```
  A deploy key reaches one repo only, and no GitHub password is typed on SteveDesktop. `--allow-write` is
  there because the RUNNER publishes results. `gh auth login` on SteveDesktop is not needed for Phase 1.
- **A4, after step 12.** `verify_from_archmagi.sh`: all PASS, with WARN only for self-upgrade stamps
  that have not run yet. Then trigger one self-upgrade to prove it:
  `ssh stevedesktop "wsl -d Ubuntu -u root -- systemctl start runner-selfupgrade.service"` and
  `ssh stevedesktop "Start-ScheduledTask -TaskName 'SteveDesktop SelfUpgrade'"`, and verify again.
- **A5, during the week.** Run `verify_from_archmagi.sh` daily. Reboot it on purpose when
  `reboot_pending` shows. Phase 2 harness work continues under its own items.

- **A6, switching Claude accounts** (owner rulings 2026-10-25: whole machine, close every Claude window,
  relaunch the Fleet). Built in `claude-remote-control` (`accounts/`, `scripts/claude_account*.py`);
  design and owner steps: `D:\Luke\dev\claude-remote-control\docs\2026-10-25-account-switching-design.md`
  sections 15-19. SteveDesktop was migrated off the old `~/.claude-active` / `CLAUDE_CONFIG_DIR` layout:
  the live login is `~/.claude` + `~/.claude.json` (lukas), dormant logins sit in `~/.claude-accounts/<acct>/`.
  - **See:** `ssh stevedesktop-wsl claude-account status`, or `http://stevedesktop-wsl:8765/` on the tailnet.
  - **Switch:** `ssh -t stevedesktop-wsl claude-account-switch stevedesktop <lukas|steven|system>` (asks for the
    machine name), the page, or Archmagi's desktop folder `Claude accounts`. Closes every Claude window here,
    never the game.
  - **Add a login:** the page's *Log in* button, or `claude-account enroll <acct>` then
    `claude-account code <acct> --op <id>` (code at a hidden prompt, never in argv).
  - **Fleet** (delegated call): `C:\SteveDesktop\claude_fleet.ps1` opens "Claude Server (SteveDesktop)"
    (`claude remote-control`) and "Claude Runner (SteveDesktop)" in `~/rm/runner`. This supersedes step 9's
    "do not turn on Remote Control" now that the owner wants SteveDesktop controllable from his phone.
  - **Reinstall:** copy the repo to `~/src/claude-account` and run `bash accounts/install.sh stevedesktop`.
  - The `sjlewis` user's `~/.claude/.credentials.json` is a superseded copy of the lukas grant (the token has
    rotated since); do not use or copy it.

---

## Maintenance kit (installed 2026-10-25 over SSH, for the owner logging in)

Everything free, nothing signed in. Files: `kit/wt_settings.json` (Terminal settings) and `kit/status.ps1`, both copied to `C:\SteveDesktop\`.

| Item | How | Notes |
|---|---|---|
| Windows Terminal 1.25 | `winget install -e --id Microsoft.WindowsTerminal` | Win10 19045 supports it. Settings from `kit/wt_settings.json` (old file kept as `settings.json.bak-kit`): Cascadia Code 11, 32000 lines scrollback, copy-on-select, Ctrl+Shift+C/V. Win10 has no OS-level "default terminal" switch, so the desktop shortcuts are the way in |
| Terminal profiles | in `settings.json` | **Ubuntu (mandrake)** is the default, then Ubuntu (sjlewis), PowerShell 7, Windows PowerShell, cmd, **SSH Archmagi (WSL)** (`ssh mandrake@archmagi-wsl`, tested from SteveDesktop, Tailscale SSH, no password), SSH SteveDesktop WSL |
| PowerShell 7.6 | `winget install -e --id Microsoft.PowerShell` | |
| VS Code + extensions | `winget install -e --id Microsoft.VisualStudioCode`; `code --install-extension` ms-vscode-remote.remote-wsl, remote-ssh, ms-vscode.powershell | per-user (sjlewis); no Settings Sync sign-in |
| GitHub CLI (Windows) | `winget install -e --id GitHub.cli` | not logged in |
| Sysinternals | winget `Microsoft.Sysinternals.ProcessExplorer`, `.ProcessMonitor`, `.TCPView` | |
| JetBrainsMono Nerd Font | winget `DEVCOM.JetBrainsMonoNerdFont` | installed; pick it per profile if wanted |
| Already present | Git for Windows, 7-Zip, Tailscale, Chrome Remote Desktop, WSL git/gh/tmux/htop/jq/curl/rsync/python3/node | verified, not reinstalled |
| WSL extras | `apt-get install ripgrep tree ncdu pipx fd-find bat` as root | |
| Desktop shortcuts (all users) | `Terminal - Ubuntu`, `Terminal - SteveDesktop status` (runs `status.ps1`: uptime, disks, IPs, services, Steam, Tailscale, WSL), `Terminal - Archmagi (SSH)` | |

**Trap learned:** `winget install` of MSI and MSIX packages (PowerShell, Terminal) fails over SSH with
`0x80070520 logon session does not exist`. Run it as a scheduled task with an Interactive principal for the
logged-on user (`Register-ScheduledTask ... -LogonType Interactive`, then `Start-ScheduledTask`); EXE/zip
packages (VS Code, gh, Sysinternals) install fine straight over SSH. `winget source update` reports
"Failed ... winget" but installs still work.

`verify_from_archmagi.sh` has a `kit_*` check for all of the above.

---

## Test centre: running a modcheck there (proved 2026-10-25)

**The game is ours (owner, 2026-10-25, verbatim):** "Steve no longer plays Rimworld, so you never
have to worry about 'disrupting his modlist' or 'harming his save games.' No such concerns, this
game is ours to play with." The runner owns RimWorld's ModsConfig, Prefs and Saves on this
machine; nothing here protects another player's state.

First remote run GREEN: `JawaIonWeapons --chains def_wiring`, driven from Archmagi
(STEVEDESKTOP_MODCHECK_PROVE_FIRST_REMOTE_RUN). First measured run, 2026-10-25 23:28Z:
`--sync FlowWorks` then `--chains flow_doors,canal_spikes`, 9/9 PASS; sync 39 s, cold load 54 s
(MINIMAL list, 26 mods), run 34 s. The pieces, all in this folder:

- `testcentre_env.sh`: sourced from line 2 of `~/.bashrc` in the WSL. Points game_paths at
  `D:\SteamLibrary` and at the game's normal userdata folder (`sjlewis`'s LocalLow).
- `rw_game.sh status|up [--wait]|down|init`: `up` starts Steam if it is not running (`-silent`),
  then the game, in session 1 (the desktop), with no special arguments. `init` renews the test
  companion profile and sets Prefs runInBackground.
- `sync_test_mods.py [--apply]`: from Archmagi, copies the MINIMAL list's Workshop mods and the
  JawaBench companion. Copying, not subscribing, because a Workshop subscription needs the Steam UI.
- `remote_modcheck.sh [--sync] [--deploy M1,M2] [--no-run] <Mod> [modcheck args]`: from Archmagi.
  **The one command for code updates is `--sync`:** the runner pulls origin/main, plans a deploy of
  `<Mod>` and every `--deploy` mod, and only if anything drifted stops the game and applies it.
  Then init, `up --wait`, the run, and the sheet is copied back. Prints `PHASE sync|load|run N s`.
- `sps.sh`: PowerShell over Windows OpenSSH. Short scripts go as `-EncodedCommand`. Scripts over
  8000 encoded characters (cmd.exe caps a command line at 8191) are copied over scp and run with
  `-File`; the script deletes itself.
- `kit/automation.ps1`: the idempotent "nobody at the keyboard" fixes, run elevated over SSH
  (see the audit below).

Switch lists with `modlist_swap.py --minimal|--restore --apply` on the runner (game down).
The runner is not a seat, so record the printed `rimflow verify` line from a seat clone.

## Full-automation audit (2026-10-25)

Owner, 2026-10-25, verbatim: "everything on SteveDesktop must be fully automated. I won't have
physical access to it, so you need to be able to do anything needed for testing."

| Area | State (measured over SSH) | Action |
|---|---|---|
| Remote admin | Windows OpenSSH sessions are elevated (admin); UAC left as shipped | none needed |
| Sign-in | Autologon (`sjlewis`) | none needed |
| Game launch | needs the desktop session: WSL interop lands in session 1; OpenSSH is session 0 | `rw_game.sh` launches through WSL interop |
| Steam | AutoLoginUser + RememberPassword; Run key `steam.exe -silent` | `rw_game.sh up` starts it if absent |
| Code update + deploy | was manual on the runner | `remote_modcheck.sh --sync` |
| Crash dialogs | WER UI would block on a crash | `DontShowUI=1` (machine + user), `automation.ps1` |
| Screensaver | Ribbons after 60 min | off (registry + applied live) |
| Post-update "finish setting up" screen | possible after a feature update | `ScoobeSystemSettingEnabled=0`, suggestion content off |
| Driver updates | could swap the GPU driver | `ExcludeWUDriversInQualityUpdate=1` |
| Sleep / hibernate | standby on AC never | standby + hibernate never on AC, hibernate off |
| Windows Update reboot | AUOptions=4, no auto reboot while signed in, active hours 7-1 | none needed |
| WSL alive | `\WSL Keepalive` at logon | none needed |

**Still needs a human (no remote route):** a Steam Guard code or re-login after a password change
or token expiry (Steam UI plus the account's phone); anything before Windows starts (BIOS,
BitLocker recovery, disk check), because every door runs inside Windows; the browser half of a
Claude `/login` (phone). An RDP connection would take the console session that the game needs;
`tscon <id> /dest:console` should hand it back (not measured), so use CRD, not RDP.

## Claude support kit (WSL, 2026-10-25)

- `~/dev`: Lodestar, Machinist, Dispatch, claude-remote-control, MandrakeWorkflows,
  MandrakeVisualize. Each clone uses its own **read-only deploy key** `~/.ssh/deploy_<repo>`
  (set as the clone's `core.sshCommand`; added from Archmagi with
  `gh repo deploy-key add ... --title stevedesktop-wsl-readonly`). They pull, they cannot push.
  `gh` stays logged out: no personal token on this machine. Household and private repos are not cloned.
- `~/.claude/CLAUDE.md` is rendered by `~/dev/Lodestar/bin/claudeconf.py render` from machine key
  `stevedesktop` (Lodestar `machines.md` row and `claude/global/machines/stevedesktop.md`);
  `claudeconf.py skills --apply` links the skills whose repos are present.
- Git identity: `sh ~/dev/Machinist/tools/install-git-identity.sh`.
- Claude logins belong to the claude-remote-control account switcher; never edit them by hand.

## Before you leave Monday: checklist

- [ ] Step 1: green SSH READY box seen; the agent confirmed `lan_ssh PASS`
- [ ] Step 2: DHCP reservation saved for SteveDesktop's MAC `04:33:c2:68:51:5a` → 192.168.86.87 (phone app only; agent route ruled out 2026-10-25)
- [ ] Step 3/6: Tailscale connected, both `stevedesktop` and `stevedesktop-wsl`
- [ ] Step 4: key expiry disabled on **both** nodes; SSH rule is `accept`
- [ ] Step 5: BIOS AC-restore = Power On, WoL on, ErP off
- [ ] Step 7: Autologon enabled
- [ ] Step 8: Chrome Remote Desktop shows SteveDesktop **Online**, and you opened it once from Archmagi
- [ ] Step 9: Claude Code logged in inside Ubuntu
- [ ] Step 10: Steam remembers you, starts at login (rw_game.sh also starts it); all five DLCs installed (or the missing ones named)
- [ ] Step 11: rebooted remotely, came back to the desktop alone
- [ ] Step 12: power-cut restart worked; the WoL wake worked (wired only)
- [ ] The agent's `verify_from_archmagi.sh` shows no FAIL
- [ ] The PC is on a cable rather than Wi-Fi if possible, the monitor can stay off, and nothing sits on the keyboard

---

## Survives the week

| Failure | Mitigation in place | Residual risk |
|---|---|---|
| **Windows Update reboot** | Updates still install (`AUOptions=4`, daily 03:00). On **Pro**, restart is held while a user is logged on (`NoAutoRebootWithLoggedOnUsers`, honoured only with `AUOptions=4`), active hours 07:00-01:00. When it does reboot: autologon + Steam at login + `\WSL Keepalive` bring everything back. sshd, Windows Tailscale and CRD are services and come up before logon. Agents reboot on purpose when `reboot_pending` shows | On **Home** Group Policy keys are not honoured, so a reboot can land mid-run; the recovery path is the same. A feature update can sit at a "Let's finish setting up" (OOBE-style) screen after its reboot: CRD reaches it |
| **Power cut** | BIOS restore-on-AC = Power On. Autologon. All services automatic. Hibernate and Fast Startup off | A BIOS that ignores the setting after a long outage; a router that comes up after the PC (sshd and Tailscale retry by themselves). Anything before Windows starts (boot repair, a disk check prompt, a BitLocker recovery-key screen) needs a person: CRD, SSH and Tailscale all run inside Windows |
| **IP change** | DHCP reservation (step 2). Tailscale doors do not use the LAN IP. A new IP shows in `tailscale status` and in a fresh report | Reservation lost on a router reset: Tailscale and CRD still work |
| **Tailscale key expiry** | Expiry disabled on both nodes (step 4) | Forgetting the WSL node (the checklist covers it); verify warns via `ts_expiry_*` |
| **Claude login expiry** | The native installer self-updates; OAuth refreshes itself. If `/login` is ever needed, an agent opens `claude` in tmux over SSH and you open the printed URL on your phone | Needs your phone for the browser half. The runner is token-free by design, so a dead login does not stop runs |
| **WSL not starting without a logon** | Autologon + `\WSL Keepalive` (a copy of Archmagi's logon task). Door 4 (`ssh <win> wsl ...`) starts WSL from an SSH session even with nobody logged on | If autologon fails (password changed), door 3 is down until someone logs in through CRD. Doors 1, 2 and 4 still work |
| **Disk full** | Storage Sense weekly. apt clean + autoremove weekly, journald capped at 200 MB, self-upgrade log rotates at 5 MB. `verify` FAILs below 20 GB free on C: | The WSL ext4.vhdx only grows; a runaway run log can still fill it; cleaning is manual over SSH |
| **Steam updates** | Steam stays online and updates RimWorld as Archmagi's does. Every run result carries the game version (plan Phase 3) | A game update mid-week can make the two machines differ until both update; a Steam re-login prompt (password change, Guard) needs CRD and your phone |
| **A self-upgrade breaks something** | Daily `git pull --ff-only` never forces. apt runs `--force-confold`. Everything logs (`/var/log/runner-selfupgrade.log`, `C:\SteveDesktop\selfupgrade.log`) | `winget upgrade --all` may restart Tailscale or CRD for a few seconds. A bad Claude Code release: rerun `claude update` or pin it over SSH |

| **No more security updates** | Bootstrap records `display_version` and `build` in the report. Agents keep the machine off untrusted inbound paths: SSH from LAN + Tailscale only, CRD dials out | Windows 10 left support on 2025-10-14. Consumer Extended Security Updates were published to run to 2026-10-13, which is before this week. So unless the machine is on a paid commercial ESU, Windows Update brings little or nothing now (Microsoft's published dates; not measured on this machine). That means fewer surprise reboots but no new patches. The machine must be on 22H2 (`display_version` 22H2, build 19045) for WSL to update |

## Lockout safety (what the bootstrap never does)

- It never edits `sshd_config`, so password logins on the LAN stay as Windows ships them.
- It deletes no firewall rule. It only narrows the OpenSSH (and, on Pro, RDP) rules to LAN + Tailscale ranges.
- It changes no account, password or UAC setting. The only security-relevant change is turning off the
  "Windows Hello sign-in only" flag, which Autologon needs.
- Network-adapter changes (Wake-on-LAN) use `-NoRestart` and run only when a value differs, so a
  rerun over SSH never bounces the NIC under its own session. WSL is restarted (Ubuntu only,
  never `wsl --shutdown`) only when systemd is not yet PID 1.
- It reboots at most twice by itself, and only after you press Enter. After that it stops and reports.
- Each step is logged and failure-isolated. Re-running it is safe.

## Open questions only you can answer

- Is SteveDesktop wired or on Wi-Fi? (Wake-on-LAN needs a cable.) The green box will say.
- Is it on Windows 10 22H2 (build 19045)? The report shows it. If it is older, Windows Update must
  bring it to 22H2 before WSL can install, which adds about an hour.
- Does its Steam account own all five DLCs? (Step 10.)
- The Windows account's password, for Autologon. Does it log in with a PIN only?
- Deploy key with write access to `Lmandrake/RimMandrake` (A3): fine, or would you rather it used your own GitHub account?
