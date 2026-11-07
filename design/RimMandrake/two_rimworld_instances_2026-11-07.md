# Two RimWorld instances on one machine (design, 2026-11-07)

Status: design finished, trial ready and NOT run. Nothing here launched, stopped or touched a game, Steam, the bridge or ModsConfig. Every reading was a look at disk or at the running system. It closes `LIVELANE_PROBE_SECOND_GAME_INSTANCE` once the trial has run.

Owner's words, 2026-11-07: "design a way to have two instances of Rimworld running. It would likely require running Steam in a protected environment without access to the Web. This might not be required though, so we should try it simply first. Just be prepared that we may have to do so. I'm not sure Steam will be happy with us launching two versions otherwise, so a one-two research punch. Fingers crossed it's easy."

## The answer

Published practice says it is easy, and the protected Steam looks unnecessary. The obstacle people report is Steam's Play button, which a directly started `RimWorldWin64.exe` does not go through. The game's own `-savedatafolder` already splits Config, ModsConfig, Prefs and Saves. Unity's `-logfile` splits the log. The bridge takes its port and token from two environment variables. Our Python tools already follow environment variables for paths and the endpoint.

One thing no source settles: whether Steam gives a second running game a working Steam connection. It matters, because the bridge mod itself is a Workshop item on Archmagi. The trial answers it in about half an hour.

Recommended: rung one on SteveDesktop, which has 105.9 GB free. Archmagi has 7.3 GB free and cannot take a second game without shrinking the agents' WSL. The real cost is in our tools: about 25 files assume one game, and some of them kill or pick whichever game they find first. A second game is not safe beside a running loop until those are fixed, so the trial needs a quiet machine.

## Part 1, what the web says

Pages I opened and read:

- RimWorld Multiplayer developers' wiki, https://hackmd.io/@rimworldmultiplayer/dev-home . The best recipe. It describes `-savedatafolder=DevSaveData` as a shortcut argument that saves "the config and games" separately, and says plainly "You can run multiple instances of the same `\RimWorldWin64.exe` and connect over LAN." It also suggests copying the game folder, but that is to keep a pristine install, not because two games need it. Its Mac note: "If Rimworld is not launched through Steam, it cannot connect to the Steam API, and things like workshop mods are unavailable. To resolve this create a file `steam_appid.txt` with contents `294100`".
- Multiplayer mod source, https://github.com/rwmt/Multiplayer , `Source/Client/Networking/HostUtil.cs`. Its `StartArbiter` starts a second copy of the same running exe with `-batchmode -nographics -arbiter -logfile arbiter_log.txt -connect=127.0.0.1:<port>`, plus `-savedatafolder=` when one is set. So a widely used mod starts a second copy from the same folder as routine behaviour. It also shows a headless second game is possible.
- Steam guide "Double RimWorld" by Milkboy, 2019, https://steamcommunity.com/sharedfiles/filedetails/?id=1953019803 . The source for "Normally if you want to run more than one instance of RimWorld, Steam will stop you." It copies the folder, junctions Workshop into the copy's `Mods`, and launches the copy as a Non-Steam Game. It warns against one save in two games, and says both need Run in background ticked. The page carries a removed-from-community banner, reason not shown, so treat it as a witness, not a recommendation. A commenter says RimPy opens as many instances as you like.
- Steam discussion "2 installs", https://steamcommunity.com/app/294100/discussions/0/600784500009651640/ . Same idea: copy the folder and launch the exe directly. A July 2025 post says to feed one copy a command line that moves its config.
- `steam-multibox-easysetup`, https://github.com/dreamware-media/steam-multibox-easysetup . A second Steam client needs a separate Windows user and a `master_ipc_name_override`; the game finds its client through `steam_master_ipc_name_override`. Useful only as the measure of how much work a second client is.
- Steamworks API overview, https://partner.steamgames.com/doc/sdk/api . `steam_appid.txt` next to the exe is the documented developer mechanism for running outside Steam, and with it present `RestartAppIfNecessary` returns false. Also opened: https://partner.steamgames.com/doc/features/drm .
- Unity 2022.3 player arguments, https://docs.unity3d.com/2022.3/Documentation/Manual/PlayerCommandLineArguments.html . `-logFile <pathname>`, `-batchmode`, `-screen-*`, `-monitor N`. Force Single Instance is a build setting; the hackmd line and the arbiter show RimWorld is not built with it.
- Lib.GAB and RimBridgeServer source, https://github.com/pardeike/Lib.GAB and https://github.com/pardeike/RimBridgeServer . See `SECOND_BRIDGE_NEEDS_PORT_AND_TOKEN` below.
- Sandboxie, https://sandboxie-plus.com/sandboxie/ , and Windows Sandbox, https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-overview . General isolation pages. Neither says anything about Steam.

Tried without useful result: the Steam Offline Mode FAQ (https://help.steampowered.com/en/faqs/view/0E18-319B-E34B-B2C8) gave my fetcher navigation only, so nothing is taken from it. A Ludeon forum thread (topic 54169) returned HTTP 403. Reddit returned nothing. https://www.gog.com/forum/general/rimworld_can_it_be_installed_more_than_once_on_the_same_pc and https://rimworldwiki.com/wiki/Save_file opened but added nothing.

What matters in the terms, for one licensed owner on his own machine. This is my reading, not legal advice.

- Ludeon, https://rimworldgame.com/getmygame/ : "Legally, you own one copy of the game for your own use only. This system just lets you access it in several ways, for your convenience." The game's `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\EULA.txt` allows install and use for personal use and forbids selling, sharing or modifying. https://rimworldgame.com/ sells it as a DRM-free download. Nothing I read limits how many copies he runs at once.
- Steam Subscriber Agreement, https://store.steampowered.com/subscriber_agreement/ : personal, non-commercial use. It says you may not copy Content and Services without consent except as allowed, which bears on the second-folder rung, since the Steam copy has no carve-out in that text. It says you may be required to run the Steam client and keep an internet connection. It forbids emulating or redirecting Steam's protocols. A search of it for "more than one", "one computer", "same time" and "simultaneous" found only a line about hardware shipped in several packages, so running two at once is neither allowed nor forbidden in words.
- Left out, because they defeat a protection: Steam API emulators, patched or replaced `steam_api64.dll`, and anything else that makes Steam or the game believe something false about ownership. `steam_appid.txt` is not one of these. It is Valve's documented mechanism, and Steam still checks that the logged-in account owns the game.

## Part 2, what the code and machines say

### What separates cleanly (read in `D:\ClaudeWork\rimmandrake\decomp\rw16\all\Verse\GenFilePaths.cs`)

`SAVEDATAFOLDER_SPLITS_CONFIG_NOT_MODS`. `-savedatafolder=<dir>` moves Config, ModsConfig.xml, Prefs.xml, KeyPrefs.xml, Knowledge.xml, Saves, Scenarios, ModLists, Ideos, Xenotypes, Xenogerms, CameraConfigs, External, Screenshots and DevOutput. Each game can therefore hold its own mod list over one Mods folder. The companion writes `JawaBench`, tps and DefDump under the save-data folder, so those split too. The lesson `D:\Luke\dev\RimMandrake\infrastructure\state\lessons\20261025T230159Z-BENCH-rimworld-launched-directly-as-rimworldwin64-exe.md` records this on a real direct launch.

Still shared with `-savedatafolder`:

- `Mods` and `Data`, which derive from the exe's folder.
- `Application.temporaryCachePath`.
- Unity's `Player.log` unless `-logfile` is given.
- The Unity keys under `HKCU\Software\Ludeon Studios\RimWorld by Ludeon Studios`, which hold screen size and window position (MEASURED present: 2246x941, mode 3, position 1026,0 on Archmagi).

### Steam

`Verse.Steam.SteamManager` calls `SteamAPI.RestartAppIfNecessary(AppId_t.Invalid)`, then `SteamAPI.Init()`. If Init fails it logs `[Steamworks.NET] SteamAPI.Init() failed` and carries on. `ModLister` then adds no Workshop items. So a refusal from Steam is not a crash: it is a game with only the local `Mods` folder.

That matters because `SECOND_GAME_BRIDGE_IS_A_WORKSHOP_MOD`: on Archmagi the bridge sits at `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\3727949765\1.6\Assemblies\Lib.GAB.dll` (MEASURED). A refused game has no bridge, and looks fine on screen.

MEASURED 2026-11-07:

- SteveDesktop runs `D:\SteamLibrary\steamapps\common\RimWorld\RimWorldWin64.exe` directly with no arguments, and that folder holds a `steam_appid.txt`. No script in the repo places it, so it was probably placed by hand. The game logs no Steamworks warning and its bridge answers on 5174. Direct launch with the file is already production there, for one game.
- Archmagi runs through `steam://rungameid/294100`, parent `steam.exe -silent`, arguments `-disable-compute-shaders`. No repo file mentions that flag, so it is presumably a Steam launch option, and a direct launch must pass it by hand. Its folder has no `steam_appid.txt`.

UNMEASURED, and the one thing the trial exists to learn: a second `SteamAPI.Init()` for the same app while one game is already connected. No source I read tested this and stated the result.

### The bridge

`SECOND_BRIDGE_NEEDS_PORT_AND_TOKEN`. This settles the question left UNVERIFIED in `D:\Luke\dev\RimMandrake\design\RimMandrake\bridge_system.md`. `Source/RimBridgeStartup.cs` builds its server with `UseGabsEnvironmentIfAvailable()` and then `UsePortIfNotSet(5174)`. `Lib.GAB/GabpServerBuilder.cs` honours the environment only when BOTH `GABP_SERVER_PORT` and `GABP_TOKEN` are set; `GABS_GAME_ID` is optional. `TcpTransport.cs` listens on loopback with no port fallback. Three consequences:

- A second game with no environment fails to bind 5174 and logs `[RimBridge] Failed to start server`. The game runs with no bridge.
- With the pair set it listens on the chosen port and logs `[RimBridge] GABP server connected to GABS on port N`. That wording is only a label; no GABS is involved.
- `BRIDGE_TOKEN_LINE_GONE_IN_ENV_MODE`: in that mode the `Bridge token:` line is not written. 22 scripts mention that string. Log discovery cannot serve B, but `src/RimMandrake/Utils/rimbridge_client.py` `resolve_endpoint` already takes the env pair ahead of the log.

This source is the published repository; the deployed DLL's version was not compared. Literal-string scans of that DLL (run with `MEASURE_ALLOW_SCAN=1`) found the two variable names and both log lines, and the trial proves the rest.

### Every place that assumes one game

The good news first. `src/RimMandrake/Utils/game_paths.py` already reads `RM_GAME_USERDATA`, `RM_GAME_LOGDIR` and `RM_STEAMAPPS` (SteveDesktop's `testcentre_env.sh` relies on it). `src/RimMandrake/rimflow/driver_lock.py` reads `RIMFLOW_DRIVER_LOCK`. 187 non-test files use `game_paths` and 179 use `rimbridge_client`; those follow the environment and need no edit. `infrastructure/stevedesktop/rw_game.sh` takes its paths from the same variables, so its `init` can already seed a new data folder.

Keep `Player.log` directly in the instance's data folder, because `src/RimMandrake/Utils/modset_builder.py` builds `PLAYERLOG` from the data folder rather than the log folder. One folder then satisfies both. Whether Unity still rotates to `Player-prev.log` under `-logfile` is UNMEASURED; the trial records it.

File counts below are from `git grep` over `src/RimMandrake` and `*.sh`, excluding selftests (MEASURED; a count says the words occur, not that each is a bug).

`KILL_BY_NAME_TAKES_BOTH` (5 files). `taskkill /IM RimWorldWin64.exe` stops every game on the machine: `Utils/northstar_driver/live_session.py:58`, `rimflow/relentless_stage.py:134`, `Utils/loadsweep/biome_load_proof.sh`, `Utils/loadsweep/sweep_load.sh`, `Utils/rimbench/gl_sheet_run.sh`.

`FIRST_PROCESS_PICKS_EITHER` (7 files use `Select -First 1` on the game process). This includes `infrastructure/stevedesktop/rw_game.sh` `pid_of`, whose `down` can stop the wrong game, plus `Utils/belt_watchdog.py:254`, `Utils/coldstart_crashes.py:125`, `Utils/focus_heal.py:39` and `Utils/game_focus.py:158`. `Utils/load_policy.py:34` holds the image name as a constant. In all, 31 files name the process or exe. `belt_watchdog` already lists all games (MUST 9) but identifies "the game" from the first.

`ANY_GAME_MEANS_THE_GAME_IS_UP` (5 files with a tasklist check). `Utils/modset_builder.py:1181` refuses to write ModsConfig while any game runs, so game B would block a list change for game A in a different data folder. The others are `Utils/art/enact.py`, `Utils/belt_watchdog.py`, `Utils/modcheck/live_queue/prep_wsl.py`, `Utils/running_now.py`.

`STEAM_LAUNCH_SITES` (4 live files). `steam://rungameid/294100` in `Utils/northstar_driver/live_session.py`, `bridgetools/launch_ready.py:294`, `rimflow/relentless_stage.py:149`, `Utils/modcheck/live_queue/prep_wsl.py`. These can only ever start A, or fail because A is running.

`ONE_LOCK_ONE_GAME`. `BRIDGE_HOSTS = ("archmagi", "stevedesktop")` in `rimflow/model.py:1151` keys the ledger's lock, `rimflow bridge take --host` (`rimflow/cli.py:3666`) and `D:\Luke\dev\RimMandrake\infrastructure\state\BRIDGE` by machine. `rimflow/host_guard.py` says in its first line "one driver per game, per MACHINE", and `D:\ClaudeWork\rimmandrake\scratch\DRIVER_LOCK.json` and `BRIDGE_SHARED.json` are single files. 12 non-test files touch these locks. The machine-level design was the right step on the way: an instance key extends it.

`THE_GATE_IS_A_ONE_GAME_QUEUE`. The gate lives in each loop's own untracked copy, not in the repo: `/home/mandrake/rm/scratch/BENCH/ralph_pyrelands/ralph/game_gate.py` and `loop.sh`, with copies for `ralph_gss` and `ralph_graffiti`. Its `AHEAD` list names loops that have the game first, and it refuses a regex of game commands (including `RimWorldWin64`, `steam://`, `Start-Process`, `taskkill`, `system_click`, `system_screenshot`) while they run. It has no machine or instance in it. MEASURED: the running units are `rm-ralph-pyrelands`, `rm-ralph-gss-steve` and `rm-ralph-graffiti3`, while the lists name `rm-ralph-graffiti`, `rm-ralph-gss` and `rm-ralph-gss2`. So the Pyrelands gate no longer sees Graffiti. `ralph_graffiti/ralph/NEED_GAME` exists now, so one loop is waiting for a game as of this writing.

`WINDOW_TOOLS_DONT_FIND_WINDOWS`. `Utils/system_click.py` clicks absolute screen coordinates. `Utils/system_screenshot.py` grabs the whole virtual desktop. Neither looks for a window, so with two games each hits whatever is on top. Both games have the title "RimWorld by Ludeon Studios" (MEASURED for the one running; B's is the same exe). Finding a window means process id to window handle, which no tool does today, though the focus tools have process-based code to reuse. Bridge screenshots are per game and unaffected, so the answer for B is to use only those and never desktop clicks.

`SHARED_MODS_FOLDER`. `Utils/deploy_custom_mods.py` writes into the one `Mods` folder and reports files "locked by the running game". With two games up, a mod's DLL can only be replaced when neither has it loaded, and the companion is loaded by both. A non-DLL deploy into a mod the other game is loading can give that game a half-written view. It works if each game's writable mods are disjoint; otherwise it needs rung three.

Smaller single-instance readers: 3 non-test files under the grep name 5174 (`rimbridge_client.py` as the default, `bridgetools/launch_ready.py:181` as a fallback, `Utils/vivify_world.py` in a comment), plus `FlowWorks/northstar/liquid_checks.py` and `suspension_bridge_proof.py` in the same vein. 38 non-test files contain the string `LocalLow`; how many are live paths rather than comments is UNMEASURED. `gamestate_probe.json`, `.belt_state` and the health observers keep one state each (5 files).

Other tools the brief named: `Utils/modlist_swap.py` follows `game_paths.MODS_CONFIG`, so it follows the environment, and its store of lists is shared, which is fine. `FlowWorks/northstar/live_session.py` takes its log from `game_paths` or `FW_PLAYER_LOG`, also fine. `testq` assumes one worker per machine under `host_guard`.

### Capacity, MEASURED 2026-11-07

Archmagi: Core Ultra 5 245K, 14 logical. RAM 63.3 GB, 7.3 GB free, commit free 9.9 GB. `vmmemWSL` holds 30.2 GB. RTX 5080 with 5.2 of 16.3 GB VRAM in use. C: 2141 GB free, D: 1674 GB free. The running game has 6.2 GB private and 1.4 GB working set on the Pyrelands loop's list.

SteveDesktop: i9-10900K reporting 9 cores, 18 logical, at 3696 MHz with no turbo (the fault state the owner's "Don't keep rebooting it" card accepts). RAM 127.9 GB, 105.9 GB free. RTX 2080 Ti with 2.1 of 11.3 GB VRAM in use. C: 51 GB free, D: 9.8 TB free. Running game has 2.7 GB private.

The owner's full list uses about 30 GB and loads in 15 to 21 minutes (`D:\Luke\dev\RimMandrake\design\RimMandrake\mod_audit\OWNER_CARDS.md`, line 253).

`ARCHMAGI_HAS_NO_ROOM`. Archmagi could hold a second small-list game only down to about 3 GB of commit, and no second full list at all without taking WSL's memory. SteveDesktop has room for about three full lists by RAM, or several tier lists; VRAM and CPU interference are UNMEASURED. That machine's own fault also becomes a shared risk: one machine fault now loses two games.

Second game folder cost, MEASURED apparent sizes: `Data` 486 MB, `RimWorldWin64_Data` 394 MB, `Mods` 1.6 GB, `MonoBleedingEdge` 8.8 MB, exe and `UnityPlayer.dll` 32 MB. About 2.5 GB in total. It would not repeat Workshop (1269 items; size UNMEASURED because `du` passed 60 s) as long as Steam serves them. Disk is not the limit on either machine.

## Part 3, the ladder

Stop at the first rung that passes.

### Rung one: same folder, second game started directly, own data folder, own log, own port

Run in PowerShell on the machine, from a process with no leftover `GABP_` variables. On SteveDesktop:

```powershell
$i = 'D:\ClaudeWork\rimmandrake\instances\b'
$env:GABP_SERVER_PORT = '5175'
$env:GABP_TOKEN = [guid]::NewGuid().Guid
Set-Content "$i\bridge_token.txt" $env:GABP_TOKEN
Start-Process -FilePath 'D:\SteamLibrary\steamapps\common\RimWorld\RimWorldWin64.exe' `
  -WorkingDirectory 'D:\SteamLibrary\steamapps\common\RimWorld' `
  -ArgumentList "-savedatafolder=$i", '-logfile', "$i\Player.log", '-screen-fullscreen', '0', '-screen-width', '1280', '-screen-height', '720'
```

On Archmagi the path is `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64.exe`, adding `-disable-compute-shaders` and `$env:SteamAppId = '294100'`. Steam sets that variable itself on games it launches; this is from memory, not a page I opened, so if it does not work the documented alternative is `steam_appid.txt`. Do not trial on Archmagi first.

Client for B: `GABP_SERVER_PORT=5175 GABP_TOKEN=<token> RM_GAME_USERDATA=<dir> RM_GAME_LOGDIR=<dir>`.

Expected: no Steam dialog, since the launcher is not involved. B loads its own list, logs "Save data folder overridden to", then `[RimBridge] GABP server connected to GABS on port 5175`. A keeps running and its files do not change. Steam shows RimWorld as running, as it already does.

What a refusal looks like, in order of likelihood:

- **Steam refuses B's connection.** `[Steamworks.NET] SteamAPI.Init() failed` in `<i>\Player.log`, Workshop mods missing, a mod-missing list at the main menu, no bridge line at all, and port 5175 not listening. Go to rung three.
- **Steam disturbs A.** A's log shows a Steamworks error, or its Workshop calls start failing. Stop B and record it.
- **Port.** `[RimBridge] Failed to start server` means the variables did not carry. That is a recipe bug, not a refusal.
- **Pause.** B stops advancing without focus: Prefs was not seeded with runInBackground. Recipe bug.
- **Single-instance.** B exits at once with no new log. No source predicts this, and the arbiter says otherwise.

Cost: 10 minutes to run. Risk: registry window prefs get B's size on exit (exported and restored in the trial). B takes the foreground on launch, which breaks the no-focus rule if the owner is at the machine; hence SteveDesktop, and on Archmagi only when he is away. Gives up: nothing, beyond the shared Mods folder.

### Rung two: direct exe with Steam's connection deliberately absent

Only possible where the folder holds no `steam_appid.txt`, so Archmagi as it stands, and with no `SteamAppId`. B cannot reach Steam by design, and only `Mods` is available. That needs its whole list in the local folder: at least Harmony and the bridge, plus VFE core, Alien Races and the other third-party mods on a list. A local copy of a Workshop mod beside a subscribed one makes A see duplicates. The mod-list cost makes this worse than rung three for anything real. Gives up: Workshop. Keep it only as a one-off diagnostic that isolates Steam from everything else.

### Rung three: a second game folder

`D:\ClaudeWork\rimmandrake\instances\b\game\` with its own `Mods`, so B can have a different build of our mods, a free companion DLL, and deploys that never collide. Cost about 2.5 GB and 5 minutes (MEASURED sizes), less if `Data` and `RimWorldWin64_Data` are junctions; whether Unity tolerates those is UNMEASURED. `deploy_custom_mods.py` then needs a target instance (small: its folder comes from `game_paths`, so `RM_STEAMAPPS` nearly does it, though the layout must match `common\RimWorld`). Add `steam_appid.txt` in the copy so Workshop keeps working, if rung one showed Steam allows it. If Steam refused at rung one, the copy runs with no Steam and needs a local mod set, as in the Milkboy guide's junction of Workshop into `Mods`.

Licence: this is the one rung that copies game files, and the Subscriber Agreement's wording on copying has no carve-out. The Multiplayer developers publish exactly this recipe and Ludeon sells the same game DRM-free, so I think the risk is small, but it is not nothing. If he bought from Ludeon rather than Steam (UNMEASURED; the owner would know), the DRM-free download is the clean version: it has no Steam dependency at all and needs no copy of Steam's install. Do not do this rung unless shared `Mods` actually hurts.

### Rung four: a second Windows user

Own LocalLow, own HKCU, own log with no flags. The Steam connection is per user, so it needs a second Steam client signed in there, and the same account signed in twice is UNMEASURED and likely to fight over who is playing. Rendering needs a live session; a disconnected or locked one is often not rendering. Hours to set up, every tool's paths change, and WSL interop does not start processes in that session. Gives up: all the simple plumbing. Not recommended; everything it isolates, the flags already isolate.

### Rung five: Steam offline or sandboxed with no web

The owner's idea, kept ready. There are three forms.

- **Steam Offline Mode, or a firewall rule blocking `steam.exe` outbound.** Minutes to do. It does not start a second client, so it changes nothing about two games on one Steam: there is no sign that the web is what limits this, since every report concerns the local launcher. It costs Workshop updates and logins, and the owner's own play and the loops' downloads while it is on. The Agreement says a connection may be required, and blocking one is not defeating a protection, but Offline Mode has to be entered while signed in. Use only if the trial shows Steam's server side interferes, which I do not expect.
- **Sandboxie box holding a second Steam client.** It needs its own login in the box, the same account twice as in rung four, and its file virtualisation sits in the way of `D:\ClaudeWork` paths and the bridge's tooling. UNMEASURED whether Steam runs usefully there; the vendor's page says nothing about Steam. Half a day to try.
- **Windows Sandbox.** It discards everything on close, including Steam's 1269-item Workshop, and a login each time. Ruled out for a test lane. (Needs Pro, which both machines have; it does have vGPU.)

### Rung six: a virtual machine

Hyper-V on Windows Pro. GPU is the problem: a stock VM renders in software, and partitioning the GPU into it is a fragile, unsupported path on a consumer card (UNMEASURED, and from general knowledge). It needs a Windows licence for the guest, 40 GB or more of RAM for a full list, and a second Steam sign-in. A day or more, with the worst performance and the most tools to change. Not recommended, and on Archmagi impossible by memory.

### Rung seven: more machines

Already the proven pattern: SteveDesktop is exactly this. One licence on several machines appears fine for use, per the EULA's "all your machines", though Steam will object to two machines playing at once on one account (general knowledge, UNMEASURED; SteveDesktop's account setup was not examined here). Costs hardware. All the tooling exists. It is what to buy if a machine's memory becomes the limit.

### A sideways option once rung one passes

`-batchmode -nographics` as the Multiplayer arbiter does it: no window, no focus problem, no VRAM, so a headless B suits proofs with no picture. UNMEASURED with our tools. Bridge screenshots will not work, and anything that depends on a rendered frame will not run. Worth a single test after rung one, not before.

## Tooling changes to drive N games

An instance is a name plus one small set of environment values: `RM_GAME_USERDATA`, `RM_GAME_LOGDIR`, `GABP_SERVER_PORT`, `GABP_TOKEN`, `RIMFLOW_DRIVER_LOCK`. Default instance `a` is today's game with none set, so nothing changes for anyone who has not asked. This is launching and locking only. It needs no new rule, judging layer or `relentless_rules.json` key, so it sits inside the Relentless freeze; a lane-opening decision still belongs to the Conductor.

**First, to run one loop on B safely beside a loop on A, about 25 files, ESTIMATE one builder sitting offline:**

1. New `src/RimMandrake/Utils/game_instance.py`, about 150 lines. Instance name to environment; `launch`, `pid` (matches `-savedatafolder=` in the process command line), `stop <pid>`, `status`. Port is 5174 plus index. One small `rw_game.sh` change to use it.
2. The 5 `KILL_BY_NAME_TAKES_BOTH` sites become stop-by-pid via the helper. This is the first thing, since it is what can kill someone else's game.
3. The 7 `FIRST_PROCESS_PICKS_EITHER` sites, and the 5 `ANY_GAME_MEANS_THE_GAME_IS_UP` sites where they act on the result (`modset_builder.py` matters most).
4. The 4 `STEAM_LAUNCH_SITES`: B never uses them. A keeps them.
5. `BRIDGE_TOKEN_LINE_GONE_IN_ENV_MODE`: the 7 central waiters (`rimbridge_client.py`, `logwait.py`, `bridgetools/launch_ready.py`, `preflight_bridge.py`, `northstar_driver/live_session.py`, `modcheck/launch_gate.py`, `rimflow/relentless_stage.py`) accept the port line. The prove scripts can wait, as they run with the env pair.
6. `ONE_LOCK_ONE_GAME`: `BRIDGE_HOSTS` in `rimflow/model.py`, `rimflow/cli.py`, `rimflow/host_guard.py` take an instance key such as `stevedesktop.b`. Their selftests move with them. The `BRIDGE` mirror grows a line.
7. `THE_GATE_IS_A_ONE_GAME_QUEUE`: a loop's copy of `game_gate.py` and `loop.sh` gets its instance and an `AHEAD` naming only loops on that instance. Also correct the stale unit names, which are wrong today regardless.

**Can wait:**

- `belt_watchdog.py` watching N games.
- `testq` running two workers (its machine lock and worker would each need the instance; `Utils/testq/` has 23 files).
- Health observers and `gamestate_probe.json` per instance.
- `rimflow who` displays.
- Window-finding in `system_click.py` and `system_screenshot.py`; rule B out of them instead.
- The 38 `LocalLow` files, audited when one misbehaves.
- The prove scripts that grep the token line.
- `deploy_custom_mods.py` instance target, until rung three.
- The owner's live looks. BENCH stays on A alone.

The trial itself needs none of the above, because it holds the whole machine.

## Trial plan for rung one

Not run; ready for a helper to run on the Conductor's word.

**Where and when.** SteveDesktop, since it has the memory and no one at the desktop. It must be a quiet machine: `rm-ralph-gss-steve` finished or stopped between passes, no `testq` job running, and `rimflow bridge who --host stevedesktop` free. **It is not safe beside a running loop:** that loop's `modset_builder` would see B and refuse to write its list; a `rw_game.sh down` could pick B or A at random; and a `taskkill /IM` would take B with it. So a trial beside a loop puts the loop's game at risk through these tools, before Steam even enters.

**Steps**, all on SteveDesktop, about 30 minutes, one driver:

1. `rimflow bridge take --host stevedesktop --for "second game trial"`. Record baselines: `reg export` of the Unity key to the instance folder, md5 of A's `ModsConfig.xml` and `Prefs.xml`, and free RAM, commit and VRAM.
2. Bring up A with `rw_game.sh up` on the list it already has, and start a quicktest world. Record A's process id, its TPS alone over 2 minutes from `JawaBench\tps`, and working set and private memory.
3. Create `D:\ClaudeWork\rimmandrake\instances\b`. Seed with `RM_GAME_USERDATA=<wsl path> RM_GAME_LOGDIR=<wsl path> rw_game.sh init`, which writes the companion profile and runInBackground Prefs. Copy `infrastructure/state/modlists/ModsConfig.MINIMAL.xml` to `<i>\Config\ModsConfig.xml`. It has 27 active mods including `brrainz.rimbridgeserver`; confirm with `modset_builder`'s reader that each resolves on this machine, since SteveDesktop has only 64 Workshop items and 33 in `Mods`. If some do not, take that list minus those mods.
4. Run the rung-one command. Note the time and B's process id from its command line. Never use a tool that looks up "the" game while B is up, except by id.
5. Wait for the port line in `<i>\Player.log`, and read its Steamworks lines and the Workshop mods seen.
6. Over the env pair, `rimworld/start_debug_game_ready` on B, and check its map from the bridge. Check A on 5174 with its own token, ask each for its colony or map identity and a state read, and advance each a little. Spawn a marker thing on B only and confirm that A does not have it.
7. Record, with both running, for 2 minutes: A's and B's TPS, working set and private memory, commit free, VRAM, CPU, `Get-NetTCPConnection -State Listen -LocalPort 5174,5175`.
8. Stop B by id: `taskkill /PID`, then `/F` after 90 s, as `rw_game.sh down` does. Confirm A is still alive, its bridge answering and its Player.log still growing. Stop A with `rw_game.sh down` only when B is gone. Run a final check that A's `ModsConfig.xml` and `Prefs.xml` md5 still match. Then the same round reversed if time allows.

**Pass:** two games at once; each answers its own bridge on its own port with its own token; each has its own map, shown by the marker; and each log is clean: no Steamworks warning, no bridge failure, no new error attributable to the other game. A's files unchanged.

**A partial pass still answers something.** If B runs but Steam refused it, that is a clear answer for rung three. Name it `STEAM_REFUSES_SECOND_INIT` and stop.

**Readings for the record:** Steam's reaction, including any window (bridge screenshot is blind to Steam's window; `system_screenshot` is allowed for this single check on a machine nobody is using); B's start to first bridge reply; both TPS figures against A alone; memory and VRAM per game; and whether `Player-prev.log` moved. Write these into the item `LIVELANE_PROBE_SECOND_GAME_INSTANCE`, with evidence under `D:\ClaudeWork\rimmandrake\instances\b\trial\`, and copy anything a human should read to `Transient\`.

**Back-out:** stop B by id; `reg import` the exported key; the instance folder stays as evidence and holds everything B wrote. Nothing was written in the game folder, Steam, or A's data folder. Release the bridge. If A or Steam misbehaves afterwards, `rw_game.sh down` and up restore the usual state, as a game restart does rather than a machine reboot, per the owner's card of today.

**What the trial needs from the Conductor:** a window of about 30 minutes with SteveDesktop quiet, in other words stop `rm-ralph-gss-steve` at a pass boundary or wait until it ends. Also pause `testq` there. One helper to drive it, on rung one's commands.

## What this buys, honestly

At best about twice the game-minutes per machine when both are busy, on SteveDesktop only (ESTIMATE; interference UNMEASURED, and the fault-limited clock leaves less headroom than the core count suggests). More exactly, it removes the queue. Graffiti's loop is sitting on `NEED_GAME` now behind two others, and a second game on SteveDesktop lets one of those proceed. So this is a real, immediate gain.

What it does not change:

- **Tokens.** One driver per game means two games need two working sessions, so tokens burn about twice as fast during live work, and loops already cost real budget.
- **Time in the game is often not the shortage.** The fast-testing work measured utilisation falling from 31% to 5 to 10% after Relentless took the game (`D:\Luke\dev\RimMandrake\design\RimMandrake\fast_testing_2026-11-05\ideas_inside.md`, C26 to C28), and on 2026-10-31 the bridge was held 1.5% of 24 hours (`D:\Luke\dev\RimMandrake\design\RimMandrake\parallel_review_2026-10-31\use_now.md`). Queueing came with the Artisan loops, and those are what this addresses. Past three or four loops, thinking time and tokens will bind before games do. A loop waiting behind two others this morning does not by itself show that a second game would stay busy all week.
- **Cold starts.** Median 17 minutes from start to first row, 42 cold starts in 84 hours on the 2026-11-05 measure. Two games load two lists, each at its own full cost. Small lists remain the larger lever; `-savedatafolder` lists on a shared `Mods` make them cheaper to hold side by side.
- **Memory on Archmagi.** No second full-list game there, and the agents' WSL competes for the same RAM. The owner's live looks stay one game on Archmagi.
- **Deploys.** Shared `Mods` makes the companion DLL a both-games-down event. Rung three cures that at a licence-question cost.
- **Machine faults.** One SteveDesktop fault now costs two games' runs.

Do the trial next. If it passes, do items 1 and 2 of the tooling first, then the rest, then put one loop on B.
