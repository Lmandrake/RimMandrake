# AGENT_OPS_state.md — where OPS is

## 🔴 WRAP 2026-08-13 ~21:0x — this section supersedes everything below it

**Game was LIVE this session** (up 17:30, quicktest map). **Bridge taken twice
and RELEASED both times**, announced to BRIDGE each way.

**Left on the map (quicktest, NOT the campaign):** four art-check pawns at
(30/32/42/48, 210), faction none, alive. My downed `KotORDroidGood_3C` at
(60,60) is **gone** — downed, not killed, so something finished it. Nothing
destroyed by me, no terrain written, **never unpaused**.

### Owed / carry forward

| item | note |
|---|---|
| 🔴 **Steam Cloud restores deleted saves** | 26 `.rws`, 701 MB, came back at the 17:30 launch with ORIGINAL mtimes. **Cloud must be DISABLED for RimWorld before deleting, or the next launch undoes it again.** Owner's call; I am not touching it. |
| **Pin the 6 `loadBottom`+`loadAfter` userRules** | wants the game DOWN. Order is correct TODAY but rides a tie-break, not a constraint. `loadBottom` outranks `loadAfter`; keep it only on `rimdefdump`. |
| **`refresh.py`** | wants the game DOWN. |
| **Retire `mandrake.missingartfixes`** | all 7 textures md5-identical to the per-donor successors; blocking dep cleared. Drop from `ModsConfig.xml` on a mod-list pass. |
| **Restore 3 pruned textures?** | OPTIONAL and unrelated to the graphics scare (withdrawn). Recoverable from `6f52185`. Only affects the shadowing question. |

### Still open in my queue
**O3, O5, O8** offline. **O4** is the only one needing a live game — a
one-minute Faction Customizer persistence check. **Closed today: O1, O2, O7, O9.**

### The one thing a successor must not re-derive
🔴 **`v1` row 2 (worldgen faction cut) is UNEXECUTED.** The checklist is
ratified and ready at `infrastructure/state/WORLDGEN_FACTION_CHECKLIST.md`.
⚠️ **A quicktest map's faction roster PROVES NOTHING about it** — a debug
quicktest never visits the Configure Factions page, so every faction is present
by default. That reading nearly triggered a needless 25–30 minute regeneration
today. **State which map any census came from.**

### Systemic finding of the session
**Four tools reported success for work that never happened** — a validator's exit
code discarded, `--defnames` claiming checks it had not run, a def dump that
accumulates orphan types while looking fresh, and a provenance stamp written on
failure. **In this codebase "success" is usually asserted by whatever wrote last,
not by whatever checked.** All four fixed; the pattern is the finding.

---


**Cross-session address:** `uds:/run/user/1000/cc-socks/88807.sock`
(session resumed 2026-08-13 ~14:58, wrapped ~15:10 on PROJECT's reboot order.
⚠️ **Dead once this session exits** — recompute on the next resume, first thing:)

```bash
echo "**Cross-session address:** \`uds:/run/user/1000/cc-socks/$PPID.sock\`"
```

Identity: `infrastructure/agents/OPS.md`, injected automatically. Queue: `infrastructure/state/queue/OPS.md`.

---

## Where I stopped — 2026-08-13, wrap on PROJECT's order

**Game was DOWN the whole session** — `Player.log` mtime 10:04, no RimWorld
process. **Bridge never taken, so nothing to release and nothing left on any
map.** The six pawn states below are from the PREVIOUS session and still stand.

✅ **Log baseline re-confirmed clean.** `Player.log` (10:04) holds **25**
`Could not resolve cross-reference` and **0** `Could not load reference to`.
The 25 decompose exactly as `vendor/wisdom/benign_log_errors.md:407` predicts:
16 × `Pawn_Melee_Punch_HitBuilding` (§1.6) + 8 × `BMT_*` (§1.11) +
1 × `VWE_Tool_Whip` (§1.1). **No unexplained cross-reference. Nothing owed here.**

🔴 **v1 row 2 is BLOCKED on the owner, not on work.** Asked: *does v1 ship the
existing world or regenerate one?* Faction Control only acts at worldgen, and
`New Arrivals2.rws` already holds all 53 factions. Full measured writeup —
settlement counts, the 21 unreachable factions, the two doc corrections, and two
savegame parse traps — is in `infrastructure/state/queue/OPS.md` under the v1 row. **Answer the
question first; the config edit is ten minutes after that.**

⚠️ **Owed to PROJECT:** `V1_SCOPE.md:233` says 32 Faction Control entries; the
real count is 41. Their file, so filed not edited.

✅ **The dropped subagent DID return, just after the wrap — and it kills row 2's
premise.** `FactionDensity` serialises three fields (`faction`, `density`,
`enabled`) and **none of them suppresses a faction**; `density` is a clumping
radius (`__result = dist < fd.Density;`). Faction removal is a worldgen-time
choice on vanilla's Configure Factions page, not a writable setting. The English
key *"setting to 0 disables the faction"* is a pre-1.3 leftover and is what the
row was built on. Full writeup and the one unverified field (`enabled`) are in
`infrastructure/state/queue/OPS.md` §5b.

✅ **RULED, same session: no savegames are being kept, so v1 REGENERATES.**
`OWNER_DECISIONS.md` #11 is answered. Row 2 survives, but **as a worldgen-time
checklist, not offline config** — the boxes get unticked on vanilla's Configure
Factions page during the run that creates the new world. My proposed exclusion
list (fantasy, Predator, horror/bug) and the two cautions on hidden factions are
in `infrastructure/state/queue/OPS.md` under the v1 row. **It is a player-zero proposal; VISION
ratifies what should exist, not me.**

🔴 **Two rows in `V1_SCOPE.md` are now stale and are NOT mine to edit** — row 2
still reads *"NO — closable offline today"* (it needs the game now), and row 7
reads *"verify only"* (worldgen is something we will DO). Filed to PROJECT and
BRIDGE respectively.

🔴 **Watch at the next worldgen: `OuterRim_RebelAlliance` is configured in
Faction Control's 41 but was ABSENT from the save's 53** — it did not generate
last time. If it fails again that is a defect, not taste, and no log line will
report it.

## ✅ CLOSED — live game state I created no longer matters

Owner, 2026-08-13: ***"We are keeping no savegames at this time."*** The six
pawn states I left on the colony (four prisoners, two spawned
`OuterRim_BinaryStarRaiders` Drifters as slaves) rode in `New Arrivals*.rws` and
**there is now nothing to undo.**

### 🔴 DELETED on the owner's explicit order, 2026-08-13 — 205 files, 986 MB

Owner: *"Delete all old savegames and screenshots, yes."* **Irreversible; there
is no backup and no recycle bin on these paths.** Folders kept, contents gone:

| path | removed | bytes |
|---|---|---|
| `…\RimWorld by Ludeon Studios\Saves\` | 27 `.rws` / `.bak` | 764,681,335 |
| `…\RimWorld by Ludeon Studios\Screenshots\` | 124 `.png` | 255,804,786 |
| `…\Steam\userdata\40784075\760\remote\294100\screenshots\` | 54 `.jpg` + thumbs | 13,993,893 |

**Everything is gone, including the campaign** — `New Arrivals1.rws`,
`New Arrivals2.rws`, the `PRE-W6-TEST` backup, all 20 `rimbridge_save_*`
autosaves, `w6_faction_check.rws` and `rimbench_terrain_test.rws`. The Steam set
was the owner's own F10 captures; the RimWorld set was agent test captures.
⚠️ **No other Steam game's screenshots were touched** — `294100` was the only
appid present under `760\remote\`.

⚠️ **Any doc that reads a savegame is now unrunnable**, including
`src/RimMandrake/Utils/Savegame_*.py`. The measurements in `infrastructure/state/queue/OPS.md` were taken *before*
the deletion and stand as historical record; **do not try to re-derive them, the
source file no longer exists.**

Bridge RELEASED, nothing left on the quicktest map — my six test droids destroyed
and verified absent. BRIDGE's ship and props are theirs.

## 🔴 Blockers to play

1. **Gravship radius — unresolved, the expensive one.** Bigger Gravships is set to
   34 in `Config/Mod_3522759531_GravshipSizeSettings.xml`, but it bakes radii into
   defs at **startup** via a Harmony prefix on `DefGenerator.GenerateImpliedDefs`.
   If this session's defs carry the ~25.9 defaults, **a ship built now will not
   lift and nothing logs why.** `jawa/get_def GravEngine` exposes no radius field —
   only `SubstructureSupport 632.7954`, matching neither π·34² nor π·25.9².
   **Do not build a ship until settled**; BRIDGE owes the `get_def
   GravFieldExtender` call that settles it.
2. **`matathias.ruthlessmechanoids` is NOT in `ModsConfig`.** Downloaded, 1.6,
   deps present. **The whole pursuit design is inert until enabled**, and enabling
   is mod-list work (rule 7) that must happen with the game down.
3. **Mechanoids still on**, against the owner's ruling. Needs (2) first.
4. ~~Five companion fixes undeployed~~ — ✅ deployed 2026-08-13 10:05 as BRIDGE's B0.

## Standing restrictions — do not re-litigate

- **V2 Ideology: `[v2]`, owner-deferred. STOP WORK.** Unverified, not failing.
- **Warcasket Heat stays `Cap(0.90)`** — owner: *"Keep 0.90 for now. They're
  terrifying."* Frightening is **wanted**. Do not re-propose 0.35.
- **Warcasket deploy: "ship neither."** Both retune files stay in the repo
  undeployed, permanently — that is **intended state, not drift**. Stop reporting
  it. Asked three ways and answered; re-opening costs the owner twice.
