# EXPECTED_FAILURES — expected-failure signatures, written BEFORE each load

**Why this file exists.** The owner granted the three-assemblies waiver
(`skills/rimworld-load-round/SKILL.md` §3) on one mandatory condition: *write the
expected-failure signatures down before launching.* **A signature invented after
reading the log is not evidence, it is a story that fits.**

**Two standing rules, and the second was learned the hard way:**

1. **Do not edit a block's signatures after that load's log exists.** Fill the
   block's Results table instead.
2. 🔴 **Every load gets its OWN numbered block, with the event and date in the
   heading. Never reuse a block for a second load.** On 2026-08-13 this file was
   written for the 17:30 load, that load ran and was harvested, the Results table
   stayed blank, and the file was about to be spent again on a completely
   different event — a new world generation, against signatures written for a
   campaign reload. **A blank Results table means UNFINISHED, not stale. Do not
   launch against a block that still has one.**

**Log path for every grep in this file:**

```bash
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
```

⚠️ **`Player.log` is rotated by the launcher, not appended.** On launch the
current log becomes `Player-prev.log` and the old `Player-prev.log` is destroyed.
Harvested logs are gitignored (`0d398c0`), so **a block's log evidence survives
exactly one further launch.** Quote line numbers into the Results table while the
log still exists.

---

## INDEX OF LOADS

⚠️ **This index is the file's only map and it drifted badly — rebuilt 2026-08-22.** It
said §6 was OPEN while §6's own header said CLOSED, and it listed only §1–§4 while the
body carried §6 and §7. **A map that disagrees with the territory sends the next seat to
re-run settled work**, which is exactly what it did.

| block | load event | date | status |
|---|---|---|---|
| **§1** | three-assemblies batch, reload of the (now deleted) campaign — quicktest map | started **2026-08-13 17:30:59**, harvested 18:11, game up to ~21:10 | ✅ **CLOSED 2026-08-13** — Results filled, incl. two rows honestly marked NOT COLLECTED |
| **§2** | 🔴 **NEW WORLD GENERATION** — v1 rows 2 + 7 in one irreversible run, plus Anomaly-to-zero | written **2026-08-13**, game DOWN. **Load not yet run.** | ⬜ **OPEN** — signatures written, Results blank |
| **§3** | the **2026-08-15 deploy-window load** — two assemblies + one XML/PNG mod + a mod-list change, on a **quicktest** map. ⛔ **not worldgen** | written **2026-08-15 ~15:50**, game DOWN, before launch | ⚰️ **CLOSED 2026-08-20 — EVIDENCE UNRECOVERABLE.** Results never filled and the log is gone: `Player.log` rotates every launch and at least five have happened since. **Nothing here can now be answered.** Do not re-run against these signatures — re-book any row that still matters as a NEW block |
| **§4** | the **2026-08-20 morning load** — the owner's full 577 list, no new assembly. Exercises the **six new companion tools** for the first time | written **2026-08-20 07:4x**, game DOWN, before launch | ✅ **CLOSED** — Results filled below. 🔑 §4 is the block `score_inhabited_load.py` parses; leave its signature strings alone |
| **§6** | the **2026-08-21 15:25 load** — one new assembly (Inhabited + its 12 rosters), a free def-dump recapture, three carried greps | written **2026-08-21 ~13:35** | ✅ **CLOSED 2026-08-21** — Results filled in the body, incl. the 824-def hole closed |
| **§7** | the **2026-08-21 ~16:15 restart**, harvested against the **22:44** load | written before the game closed | 🔴 **CLOSED 2026-08-22 — S1 FAILED.** The 101 cast discards did not come back. ⚠️ Its evidence file is missing; Results are transcribed from the `verify` event |

🔴 **§2 IS THE ONLY BLOCK STILL OPEN, AND IT HAS NEVER RUN.** It is the irreversible
worldgen run — the owner's, never scheduled, and its Results are blank because the load
it was written for did not happen.

⚠️ **Read it as a DRAFT, not as a plan.** It was written 2026-08-13 against a world that
no longer exists: the owner said 2026-08-22 *"I am working with DECIDE to remake the
planet an entirely different way, so there is no current frozen world"*, and `canon.yml`
carries `planet.status: remaking`. ⛔ **Its deploy-state table, its expected values and
its faction rows all describe the superseded world** and must be re-derived before any
of it is used. ✅ **It is kept, not cut** — the SHAPE of a pre-worldgen signature block
is worth having when a new world is finally generated, and only the numbers are dead.

⚰️ **§3 is closed EVIDENCE UNRECOVERABLE** — `Player.log` rotates every launch and many
have happened since. ⛔ Do not re-run against §3's signatures; re-book anything that
still matters as a NEW block. **§3's T4 REVERSES one of §2's S8 rows** — read T4, never
carry S8 forward.

---

# §1 — LOAD 2026-08-13 17:30. **CLOSED.**

**Event:** cold load of the three-assemblies batch (the load following the
2026-08-13 10:05 companion deploy). Queue item **O5**, ruled LIVE by the owner.
Session ran on a **quicktest** map; the campaign save had already been deleted.

⚠️ **Signatures below are as written before the load. Compressed at close-out —
the greps and verdict tables are unaltered; the pre-load descriptive prose about
what each assembly is was dropped, as it is now history.**

## §1 deploy state at the time (verified on disk, game down)

| # | assembly | deployed to | size | mtime |
|---|---|---|---|---|
| A1 | `JawaBench.BridgeTools` | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll` | 154,112 B | 2026-08-13 10:05 |
| A2 | `JawaIonWeapons` | `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\JawaIonWeapons\Assemblies\JawaIonWeapons.dll` | 5,120 B | 2026-08-12 21:53 |
| A3 | `OuterRimGalacticEmpire` | `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2919248699\1.6\Assemblies\OuterRimGalacticEmpire.dll` | 10,752 B | 2026-08-12 16:06 |

⚠️ **A clean log proved NOTHING here.** A1 and A2 emit zero bytes to `Player.log`
in any state. For those, the positive sighting was the whole test.

## §1 A1 — signatures as written

Gate: `python.exe src/RimMandrake/bridgetools/prove_new_tools.py`, census line 0.
17 = pass · 16 = pre-`list_factions` · 14 = pre-roof · 7 = old seven · 0 = bundle
never loaded. *(At the time `ALL_TOOLS` held only 16 names, so a correct deploy
printed `17 of 16` as a FAIL and that FAIL was the pass.)*

Log negative — all strings VERIFIED in the `#US` heap of `RimBridgeServer.dll`:

```bash
grep -nE "\[RimBridge\] (Failed to (load|scan|inspect|prepare|register)|Loader exception|Skipping companion|Could not resolve global BridgeTools|Ignoring companion-local SDK|STARTUP_INIT_FAILURE|Failed to start server)|Companion references RimBridgeServer\.Sdk" "$LOG"
```
Want zero lines. Then the bridge came up at all:
```bash
grep -nE "\[RimBridge\] (GABP server running standalone|Startup conditions satisfied|STARTUP_TIMING phase=tools\.register-extensions)" "$LOG"
```

**Silent-failure mode:** a companion deploy attempted while the game runs cannot
write the file and *nothing* says so; the host then loads the OLD companion
cleanly. **That is why the census, not the log, is the A1 gate.**

## §1 A2 — signatures as written

`JawaIonWeapons.dll`'s `#US` heap is **4 bytes, all `0x00`** — the assembly cannot
log anything, in any state. Every signature is RimWorld's own error shape.

| signature | means |
|---|---|
| `Could not find type named JawaIonWeapons.DamageWorker_IonBuildup` | the DLL did not load, or the type name drifted |
| `Exception loading def from file DamageDefs_JawaIon.xml` | the def failed to parse |
| `Could not resolve cross-reference: No Verse.HediffDef named JawaIon_Stun found` | the hediff def did not load |
| `Could not resolve cross-reference: No Verse.ThingDef named JawaIon_Bullet found` | the bullet def did not load |
| `NullReferenceException` naming `Verse.DamageDef.get_Worker` or `DamageWorker_IonBuildup.Apply` | `get_Worker` has no null check on `workerClass` — throws on the first bolt |

```bash
grep -nE "JawaIon|DamageWorker_IonBuildup|jawaionweapons" "$LOG"
grep -nE "Could not find type named JawaIonWeapons|Exception loading def from file DamageDefs_JawaIon|No Verse\.(HediffDef|ThingDef|DamageDef) named JawaIon" "$LOG"
```
*(Written as: "want exactly one hit, the mod-list entry; any second hit is the
failure." **That rule was wrong — see the Results.**)*

Live gate: spawn `KotORDroidBad_KM1MD` hostile, apply `JawaIon_Damage` ~14×,
`JawaIon_Stun` severity climbs 0.35 → 0.65 → 0.9, `downed: true`, **pawn still
exists — not a corpse.**

**Silent-failure mode:** `Apply` has four unlogged early returns. **For A2 the log
is not evidence in either direction; the live droid test is the ONLY gate.**

## §1 A3 — signatures as written

Positive: a verbatim single-line success marker, `Log.Message` at the top of the
mod constructor, *before* `Harmony.PatchAll`:

```
<color=#00FFFFFF>:: Outer Rim - Galactic Empire :: </color>1.6.9308 ::
```
```bash
grep -n "Outer Rim - Galactic Empire" "$LOG"
```
Want exactly one line, version still `1.6.9308`. **The banner alone is not
sufficient** — it prints before `PatchAll`, so pair it with the negative grep.

| signature | means |
|---|---|
| **absence** of the banner | the mod class never constructed — shows as a missing line, not an error |
| `HarmonyException` naming `Patch_OuterRimCoreMod_Settings` or `DoOptionsCategoryContents` | Outer Rim - Core renamed/removed the patch target |
| `ReflectionTypeLoadException` naming `TabulaRasa` | `neronix17.toolbox` disabled/updated — an **undeclared** hard dependency |
| `Could not find type named TabulaRasa.PawnGroupMaker_Temperature` / `…DefModExt_FactionExtension` | same cause, seen from `FactionDefs.xml` |
| `Could not resolve cross-reference: No Verse.PawnKindDef named OuterRim_ImpStormtrooper found` | the pawnkind defs did not load; the faction has no members |

```bash
grep -nE "Outer Rim - Galactic Empire|OuterRimGalacticEmpire|Patch_OuterRimCoreMod_Settings|TabulaRasa|OuterRim_GalacticEmpire|OuterRim_ImpStorm" "$LOG"
```
⛔ **GATE CORRECTED 2026-08-20 — the vessel is vanilla `Empire`.** Owner:
*"OuterRim_GalacticEmpire is no longer in the game, we patch Empire."*
~~Live gate: `jawa/list_factions` returns `OuterRim_GalacticEmpire`,~~ → **live gate:
`jawa/list_factions` returns `Empire`, and a settlement of it actually exists on the
world map.** 🔑 **The rest of this A3 section stands unchanged** — the *Outer Rim -
Galactic Empire* MOD is still in the stack and still required, because
`GalacticEmpire.xml` puts its `OuterRim_ImpStorm*` pawn kinds into vanilla
`Empire`'s combat groups. So `jawa/get_def PawnKindDef OuterRim_ImpStormtrooper` **must
still resolve**; only the FACTION half of the gate moved. The grep line above is also
still correct — it is looking for the mod's own load failures, not for the faction.
**And a settlement actually exists on the world map** — `OuterRim_RebelAlliance` was
configured, present, and never generated, so "the faction resolves" ≠ "it is in the
world". See `infrastructure/state/OWNER_DECISIONS.md`.

---

## §1 RESULTS — filled 2026-08-13 against the 17:30 log, game down

**Log used:** the live `Player.log`, confirmed as this load — single `Mono path[0]`,
first timestamped line `[17:31:34]` at 644, 8,700 lines, mtime 21:10.
**It is not harvested to the repo and survives one further launch as
`Player-prev.log`. The line numbers below are the only durable record.**

| assembly | log grep | live gate | verdict |
|---|---|---|---|
| **A1 BridgeTools** | ✅ **PASS** — the `[RimBridge]` failure grep returned **zero lines**. All three startup markers present: `Startup conditions satisfied` 5771, `STARTUP_TIMING phase=tools.register-extensions` 5782, `GABP server running standalone on port 5174` 5788. *(File predicted 5794/5805/5811 off the 07:55 baseline; present is what mattered.)* | ⬜ **NOT COLLECTED.** No record anywhere in the repo of `prove_new_tools.py` being run against this load. | 🟨 **UNVERIFIED at its own named gate.** Companion tools demonstrably ran all session — `jawa/damage` (18:03), `set_terrain` (20:46), `spawn_batch`/`set_terrain_batch`/`set_roof_batch` (20:56) — which proves the bundle loaded, but **does not distinguish 16 from 17**, and the census existed for exactly that. ⚙️ One negative datum: `13ee5c5` (20:47) records `order_pawn` as *needing a deploy*, so the build running was pre-`order_pawn`. |
| **A2 JawaIonWeapons** | ✅ **PASS.** Def-loader grep: **zero hits**. 🔴 **But the written rule "exactly one hit, any second is the failure" is WRONG and would have raised a false alarm.** The log holds **two** `  - mandrake.jawaionweapons` lines, 6687 and 8241 — **RimWorld printed the active-mod list twice this run** (1,163 `  - ` lines total). Both hits are mod-list entries; neither is an error. **Corrected rule: want only mod-list lines, and there are two dumps per run.** | ✅ **PASS** — `ad3e9b0` 18:03, `observed/2026-08-13_ion_weapon_live_test.md`, screenshot `observed/evidence/2026-08-13_ion_downs_kotor_droid.png`. | 🟩 **PASS**, with three stated deviations from the written gate: target was **`KotORDroidGood_3C`**, not `KotORDroidBad_KM1MD` (which NREs in the pawn generator in *every* faction tried — a separate, real KotOR-mod defect); **15 damage in one application**, not 14; and ⬜ **the `JawaIon_Stun` severity ladder was NOT recorded** — the test closed on `downed=True, dead=False, pawn still on map`. The "severity climbs 0.35→0.65→0.9" half is NOT COLLECTED; the "downed, alive, not a corpse" half passed. |
| **A3 GalacticEmpire** | ✅ **PASS.** Banner present at **line 716**, exactly one hit, version reads **`1.6.9308`** as predicted. Negative grep clean: no `HarmonyException`, no `Could not find type named TabulaRasa.*`, no `OuterRim_*` cross-reference failure. The three `TabulaRasa` hits (5269, 5383, 6832) are Harmony patch-listing lines for `Neronix17.TabulaRasa.RimWorld` — the dependency **present and patching**, the opposite of the failure shape. | ⬜ **NOT COLLECTED on this load.** | 🟨 **Log half PASS, live gate not collected.** v1 row 1 closed earlier the same day (`CLOSED.md:12`, hash `fad8bab`) against the world that has since been deleted; nothing ties a faction read to the 17:30 session. ⚙️ **And it could not have counted anyway:** the session ran on a quicktest, and a quicktest never visits Configure Factions (a retired seat's trap, `2d1685e`), so a faction census there says nothing about the campaign. **A3's live half is re-booked into §2 S3.** |

### §1 close-out notes worth carrying

- **Two of three live gates were never run.** The log greps are cheap and all three
  passed; the gates that actually decide A1 and A3 were skipped. That is the
  recurring shape — *a clean log read as a result.*
- ⚠️ **`CLOSED.md:11` and `:12` cite `7bd8b60` and `fad8bab`, and neither hash
  resolves in this working tree.** Not mine to fix — **filed for DECIDE**, who
  owns `CLOSED.md`. Both are the sole citation for a closed v1 claim.

---


# §7 — RESTART 2026-08-21 ~16:15. **🔴 CLOSED 2026-08-22 — S1 FAILED.**
*Results below. The 101 cast discards did not come back; the fix did not take.*

Deploy state verified on disk with the game still UP, minutes before the restart:

| artifact | state | evidence |
|---|---|---|
| all six assemblies | **unchanged** | md5-identical repo↔game: `Inhabited` `6d4fd4ff`, `JawaBench.BridgeTools` `600954ed`, `RimDefDump` `8b9e89bb`, plus JawaIonWeapons, JawaPlantGrowth, DesertVehicleReskin. **Nothing needs the shutdown window** |
| `Inhabited/Defs/CastRosters/*` (12) | 🆕 **NEWLY DEPLOYED** | the `SkillGain` shape fix; `deploy_custom_mods` reports in sync |
| `dump_request.txt` | **deleted** | the marker is not consumed. No dump this restart — one was taken at 15:44 and frozen |
| frozen target | `OFFICIAL-2026-08-21T22-44-59Z` | 78,813 defs, `shadowed=0 ambiguous=0` |

🔑 **ONE change rides this restart**: pure XML, one mod, no assembly. Attribution is
unambiguous by construction.

## §7 S1 — the 101 discarded cast members come back

```
EXPECT           harvest_log.py `DEFS DISCARDED` reads exactly 2
BASELINE         103 on the 15:44 log — attributed line by line, not estimated:
                   101  CastRoster_*.xml   (ours, the SkillGain shape bug)
                     2  ElectricTorches_DarkAgesCrypts_Thoughts.xml  (Onimods, benign,
                        and exactly harvest_log's standing baseline of 2)
EXPECT ABSENT    any line matching `Exception loading def from file CastRoster_`
EXPECT PRESENT   `[Inhabited] ready:` with its count — and the count must now
                 INCLUDE the 101, not merely be non-zero
```

⚠️ **Absence alone is not sufficient, and here the trap is specific.** If `Inhabited`
failed to load at all there would be no discard lines *and* no `ready:` line — a
silent pass. Both readings are required. 🔑 And `ready: 269` alone was never
sufficient either: the OLD log carried a `ready:` count while 101 of those
characters had been thrown away by the def loader before the mod ever saw them.

**Per-file baseline, so a partial fix is visible rather than a round number:**

```
DEEPWATER 12 · BLACKSTAR 11 · GEONOSIAN 10 · JUNKERS 9 · TUSKEN 9 · DROIDS 8
HELIX 8 · HOMESTEAD 8 · WILDSTEAM 8 · EMPIRE 7 · HUTT 7 · JAWA 4
```

⇒ **If discards land between 2 and 103, the per-file counts name which roster
still has the old shape.** A single number could not.

## §7 S2 — carry-over, free

```
EXPECT           patchfail still 5   (held at exactly 5 on the 15:44 load ✅)
EXPECT           dead mods 0, type-load 0, texture failures 0, Harmony 1
EXPECT ABSENT    a `captures/` directory under DefDump/ — the producer is still
                 unchanged, so the flat layout is the correct outcome
EXPECT PRESENT   DefDump/.keep — written by the freeze; ⛔ do NOT sweep it away
🔴 NOT EXPECTED  a new def dump. `dump_request.txt` was deleted after the 15:44
                 capture. If `[RimDefDump]` appears, something re-armed it
```

⚠️ **Two counts were ALSO above baseline on the 15:44 log and are NOT addressed by
this restart** — they are open questions, not regressions this fix touches:
`cross-reference (def loader)` **128** against baseline 25, and
`stale saved data (Scribe)` **8** against baseline 0. 🔑 **Some of the 128 may be
downstream of the 101 discards** — a discarded `CharacterDef` is a dangling
reference for anything that named it — so re-read this one AFTER the restart before
filing anything about it.

## §7 RESULTS — filled 2026-08-22 from the ledger, **not** from the log

🔴 **THE FIX DID NOT TAKE. S1 FAILED.** `NEXT_LOAD_LOG_HARVEST_1` `verify` at
**2026-08-21T23:11:49Z**, `result: partial`, `config: full-578-2026-08-21T22:44Z`,
sha `2000242`:

| clause | expected | measured | verdict |
|---|---|---|---|
| **S1** `DEFS DISCARDED` | exactly **2** | **103** — our **101** + the 2 benign, fully attributed | 🔴 **FAIL — the 101 cast discards did NOT come back** |
| **S1** `[Inhabited] ready:` | present, count INCLUDING the 101 | printed | ⚠️ **PARTIAL** — presence confirmed, the count is not in the record, and §7 warned that presence alone is insufficient |
| **S2** patch operations failed | 5 | **5** | ✅ PASS |
| **S2** texture path failures | 0 | **0** — the 148 did not recur | ✅ PASS |
| **S2** dead mods | 0 | **0**, both counters; RimAI Core booted | ✅ PASS |
| carried question — cross-reference | (open, baseline 25) | **128** | ⬜ still open, and see below |
| carried question — stale Scribe | (open, baseline 0) | **8**, all `guy762_*` GeneDefs | ⬜ still open |

🔑 **§7 predicted this correctly and it is the useful part.** It said *"some of the 128
may be downstream of the 101 discards — a discarded `CharacterDef` is a dangling
reference for anything that named it."* The 101 did not come back, and cross-reference
stayed at 128. **Those two numbers are consistent with one cause**, which is a real lead
and not a new mystery. ⛔ It is NOT proof — nobody has attributed the 128 line by line.

⛔ **`B59 MEGAFAUNA YIELDS` is UNMEASURED, not passed.** A no-op patch logs nothing, so
the log cannot answer it; it was settled on screen only. Do not read it as green.

✅ **THE EVIDENCE IS ON DISK AND RE-READABLE:** `observed/2026-08-21_harvest_2244load.txt`
(5,604 bytes, 2026-08-21 16:11). Its lines 16 and 18 read
`RED DEFS DISCARDED 103 ABOVE baseline 2` and
`RED cross-reference (def loader) 128 ABOVE baseline 25`, which is where the table above
comes from — measured output, re-countable, not quoted from memory.

⚠️ **THERE ARE TWO `observed/` DIRECTORIES AND THEY ARE DIFFERENT PLACES.** Harvests and
saved logs live at the **repo root**, `observed/`; per-experiment output lives under
`infrastructure/state/observed/`. REP searched only the second on 2026-08-22, declared
this evidence missing, and had to correct it — **check both before calling any evidence
gone.** The ledger's evidence strings are written relative to the repo root.

---

# §6 — LOAD 2026-08-21 15:25. **✅ CLOSED — results filled in below.**

Deploy state verified on disk with the game DOWN (`tasklist.exe` = 0 `RimWorldWin64`),
minutes before launch:

| artifact | state | evidence |
|---|---|---|
| `Inhabited.dll` | 🆕 **NEWLY DEPLOYED** | `6d4fd4ff…` both copies; BUILD's hold lifted on its own release condition (`d05836f`) |
| `Inhabited/Defs/CastRosters/*` (12 files) | 🆕 **NEWLY DEPLOYED** | deployed in the SAME `--apply` as the DLL, which the hold required |
| `JawaBench.BridgeTools.dll` | unchanged | `600954ed…` both copies — **not** a new assembly this load |
| `RimDefDump.dll` | unchanged since 10:02 | `8b9e89bb…` both copies, 26,112 bytes |
| mod list | 578 active, `factioncontrol` ABSENT | parsed from `<activeMods>`, not grepped |
| `dump_request.txt` | `all` — armed | a clean capture rides this load free |

🔑 **ONE new assembly, not two.** The three-assembly waiver is not being invoked. The 12
roster XMLs are not independently attributable and are not meant to be — they and the DLL
are one unit, because the rosters carry four fields the OLD DLL could not parse.

## §6 S1 — the Inhabited assembly and its rosters loaded as one unit

```
EXPECT PRESENT   [Inhabited] ready:  with a count of 269
EXPECT ABSENT    any XML parse error naming <weapon>, <items>, <apparel> or <skills>
BASELINE         the previous log (observed/2026-08-21_Player.log.pre-inhabited-deploy)
                 predates this deploy entirely — there is no prior reading of this pair
```

🔴 **THE FALSE PASS TO FEAR, and it is the reason the hold existed.** If the DLL had NOT
landed and the rosters had, RimWorld logs one XML error per unknown field across **123
characters** and then loads the defs *fine* — every one of those characters silently
carrying no weapon, no kit and no skills. **So `[Inhabited] ready: 269` alone is NOT
sufficient.** A count of 269 is compatible with 123 of them being empty. The
`<weapon>`-parse-error line must be ABSENT as well, and that absence is the load-bearing
half of this signature.

⚠️ **And absence alone is not sufficient either** (§2 of the load-round skill): if the
mod failed to load at all, there are no parse errors *and* no `ready:` line. Both
readings, or the signature has not fired.

## §6 S2 — the def dump recovers the 824 collided defs

```
EXPECT PRESENT   [RimDefDump] at the main menu, ~27 s, ~1.2 GB
EXPECT           manifest.json gains a defTypes index; colliding types written as
                 <FullName>.json instead of <SimpleName>.json
BASELINE         OFFICIAL-2026-08-21 capture: 78,057 defs, 536 types, 824 lost to
                 8 filename collisions
PREDICT          the new capture is ABOVE 78,057 by roughly 824, and AbilityDef is
                 non-empty (it read 0 before; vanilla alone has 612)
```

🔴 **ASK FOR IT BY ITS FULL NAME.** `measure count AbilityDef` will now REFUSE —
correctly — because three distinct types share that simple name and summing them
would invent a quantity nothing measured. The command that answers is:

```
python3 ~/.claude/skills/measuring-large-artifacts/scripts/measure/cli.py count RimWorld.AbilityDef
```

⚠️ **And rebuild first: `measure build`.** The reader was fixed this afternoon
(`measuring-large-artifacts` `80551ae`, SCHEMA_VERSION 2 -> 3) after a synthetic of
this very capture showed the OLD reader would discard both AbilityDef slices and
report a total it did not hold. Any `defs.sqlite` from before that refuses until
rebuilt, which is the guard working.

🔴 **CORRECTED 2026-08-21 15:30 by CHECK, after BUILD measured it (`7a57678`). READ THE
CAPTURE, NOT THE DATABASE.** The prediction above is about the **files on disk** and it
stands. It must NOT be verified through `measure` or `defs.sqlite`:

- `measure` keys coverage on the record's **simple** `defType` and never reads
  `defTypeFullName`, the filename, or the new `defTypes` index — so the producer's whole
  disambiguation is **invisible on arrival**.
- `capture.def_type` is a `TEXT PRIMARY KEY`, so the schema **cannot hold two types that
  share a simple name** at all.
- `build` counts `defs_inserted` **before** shadowed rows are removed. BUILD measured it
  reporting **615 defs while the table held 3**.

⚠️ **And this load is what ARMS that bug.** It could not fire while `AbilityDef` declared
0; the fixed producer supplies exactly the 824 defs that make it fire. ⇒ A post-load
`measure count AbilityDef` is expected to return a **confidently wrong number**.

✅ **The honest route:** read `manifest.json`'s `defCounts` and the `defs/*.json` files
directly, and record anything the db cannot answer as **UNMEASURED**, never as 0 or as a
pass (`infrastructure/agents/CHECK.md`, "Numbers you report").

🔑 **The load still buys the irreversible half regardless: the 824 defs stop being lost
on disk.** The reader defect is a separate, offline, fixable thing.

⚠️ **`refresh.py` will report `REPLACED` afterwards. That is the freeze detector working,
not a fault.** Only the owner re-freezes:
`python3 src/RimMandrake/Utils/refresh.py --freeze --by owner`
⚠️ **Corrected 2026-08-21 by BUILD — `freeze_dump.py` no longer exists.** It was
folded into `refresh.py` under `FREEZE_SHA_UNREPRODUCIBLE_1` (`9078a15`), because
two commands that both append a freeze are two answers. Drop `--by owner` for a
dry run.

## ✅ §6 S2 — RESULT, measured 2026-08-21 15:50. **The 824-def hole is closed.**

The capture landed at `capturedUtc 2026-08-21T22:44:59Z`, 578 mods, carrying the
`defTypes` index for all **533** types and **13 named collisions**, each resolved
to a full type name and a file.

| | before (`OFFICIAL-2026-08-21`) | after |
|---|---|---|
| defs in the db | 78,057 | **78,813** |
| types | 536 | 552 |
| `shadowed` | **8** | **0** |
| `ambiguous` | **5** | **0** |
| `orphan` | 19 | 19 |

⇒ **756 defs recovered**, and every type this capture holds is now `complete`.

```
measure count RimWorld.AbilityDef   MEASURED 612       <- was UNMEASURED/shadowed
measure count AbilityDef            UNMEASURED, correctly — three distinct types
                                    share that simple name (612 / 18 / 0)
measure coverage                    complete=533 orphan=19
build total vs SELECT COUNT(*)      78813 == 78813
```

⚠️ **The prediction said ~824 and the measurement says 756. Both are right, and the
difference is worth knowing.** 824 counted every def the PRODUCER lost to a
filename collision; 756 is what the DB gained. Several collision losers held 0 defs
to begin with (`AbilityUser.AbilityDef=0`, `Fortified.Structures.SymbolDef=0`, five
more), and most of the gain is actually the WINNERS — a `shadowed` type had its rows
deleted outright, so `AbilityDef`'s 612 and `FacialAnimation.FaceTypeDef`'s 152 were
missing too.

⚠️ **It is `RimWorld.AbilityDef`, not `Verse.AbilityDef`.** BUILD wrote the wrong
namespace into three files before a real capture existed to check it against — the
synthetic guessed. The manifest's `defTypes` index is what answers it, which is
what that index is for.

🔴 **The 19 orphans did not go away and were never going to.** They are stale
`defs/*.json` from captures on 2026-08-10…15 whose mods are gone, and nothing prunes
the directory. `DUMP_PRODUCER_DATED_CAPTURES_1` is what fixes that, and it is now
unblocked — the clean capture it was waiting behind exists.

⛔ **`refresh.py` now reports `REPLACED`. That is the freeze detector working, not a
fault.** The frozen target is still the 08-21T08:20:20Z capture; the better one is on
disk. **Only the owner re-freezes.**

## §6 S3 — the three greps that ride free (`NEXT_LOAD_LOG_HARVEST_1`)

Fixed list, written before the log exists. ⛔ Nothing is added to it at collection time.

```
B59        Megafauna butcher yields are the intended ones, AND the ~50 patch operations
           sequenced after the previously-aborted one apply again
PRELOAD    JawaBench and Inhabited each print their own init line, so a failure is
           attributable to the right assembly rather than to "the load broke"
BIOMESKIT  the 148 missing-texture errors are ReGrowth's absent snow variants, NOT
           damage our repaint caused
```

## §6 S5 — two BUILD changes that landed AFTER this file was written

Both are repo-side only; neither touches the producer, so both are **expected to be
invisible**. They are here because their signature is an ABSENCE that would otherwise
read as "nothing happened".

```
EXPECT ABSENT    a `captures/` directory under DefDump/ after this load
WHY              `DUMP_STORAGE_LAYOUT_RULING_1` (owner: "Option (a) all the way. Keep
                 last three.") moved the READERS onto dated captures — `game_paths.
                 DEF_DUMP` resolves captures/<newest> when it exists and the flat
                 DefDump/ when it does not. `DefDumper.cs` is DELIBERATELY UNCHANGED
                 this load, so the flat fallback is the correct outcome.
🔴 IF captures/ APPEARS, something deployed a producer that must not have been
   deployed yet — the armed collision fix has to write its capture FIRST
   (DUMP_PRODUCER_DATED_CAPTURES_1 opens with that rule).
CHECK IT WITH    python3 src/RimMandrake/Utils/game_paths.py
                 `current capture` must equal `DefDump root` while the layout is flat.
```

```
EXPECT PRESENT   a `.keep` file inside the frozen capture — but ONLY after the owner
                 re-freezes, not from the load itself
WHY              retention will keep the newest three captures and delete the rest;
                 the OFFICIAL one must not age out, so `refresh.py --freeze` marks it.
⛔ DO NOT DELETE IT as stray junk. Removing `.keep` silently removes the design
   target's protection from a prune that does not exist yet — the worst kind of
   time bomb, because nothing fails until the fourth capture.
```

⚠️ **Neither of these can fail loudly**, which is exactly why they are written down: a
silent change with no expected string is indistinguishable from a change that never
happened (§2 of the load-round skill).

## §6 S6 — our 52 deployed patches contribute ZERO patch failures

Not a new check — `harvest_log.py`'s `patchfail` already covers it. This turns its
baseline into an **attributed** prediction, which is the stronger claim:

```
EXPECT           harvest_log.py `patchfail` still reads exactly 5
BASELINE         5 = 3x Intimecy-Gender-Works + 1x Vanilla Mining Outpost +
                 1x Biomes! Caverns — all OTHER people's mods, measured 2026-08-12
                 by diffing a 568-mod load against a 573-mod one
PREDICT          a 6th is NEW, and it is NOT ours: validated offline the same
                 afternoon, our four deployed patch folders are 52 files,
                 0 errors  (observed/preload/PATCH_VALIDATION_2026-08-21.md)
READ IT WITH     python.exe src/RimMandrake/Utils/harvest_log.py --show patchfail
```

⚠️ **Two of ours are unguarded and could in principle log red** —
`Jawa_Patches/Patches/ForceGremlin_NoHair.xml` and `.../JawaWorld_Name.xml` carry a
bare `PatchOperationAdd`/`Replace` with no `PatchOperationConditional`. Checked
individually: one targets **our own** `RimMandrake - Star Wars Races` def and the
other targets **Core**, and each matches exactly one node today. Neither target can
go absent from a mod-list change, so **neither can fire on this load**. If one does,
the cause is a game-version change to the def upstream, not the mod list — and the
filename in the error names which.

🔑 **A patch that matches nothing logs NOTHING** (`CLAUDE.md`), so `patchfail == 5`
is not by itself proof our patches applied. It only proves none of them errored.
Whether they *did* something is what the fresh dump plus `validate_patch --live`
answers afterwards — and 172 of this run's warnings are exactly the nodes an
on-disk scan cannot see because another mod's patch creates them.

## §6 S4 — carry-over, free

```
EXPECT ABSENT    FactionControl.CrossRefHandler_ResolveAllCrossReferences.Postfix
                 (the mod is out of the list; three saves aborted on it)
EXPECT           harvest_log.py exits 0, or names what is above baseline
```

## §6 RESULTS — ⬜ to be filled from the log, not from memory

# §2 — NEXT LOAD: **NEW WORLD GENERATION**. ⬜ OPEN

🔴 **READ THIS BEFORE THE BLOCK — OWNER RULING 2026-08-15.** *"There is no auto
worldgen we are building. The world will be user-made and frozen. We are NOT enabling
worldgen, we will provide players a savegame with a fixed world, period. True worldgen
is OUT of any version, even v2."* — *"(but designing worldgen by hand and design
documents to guide that are in)"*

⇒ **This block is NOT dead, and it is NOT a feature.** It describes the **owner's own
single hand-built run** — the one event that brings the frozen world into existence.
It is a checklist for a human at a screen, not a task any seat or tool executes.
- ⛔ **No seat runs this.** Nothing here schedules worldgen, automates it, or ships it.
- ⛔ **Never fill this table from a quicktest log.** A quicktest proves defs LOAD; it
  says nothing about which factions a generated world HOLDS.
- 🔑 **There is no second run.** The world is built once, frozen, and shipped to players
  as a savegame. **A faction, ideoligion or setting missed at the screen is missed
  forever** — no regenerate, no patch afterwards.
- 📌 What is collectable AFTER the fact is more than it looks: the deliverable is a
  `.rws`, so the roster question can be answered by reading the save at leisure. **The
  genuinely one-shot part is the owner's tick pass at the Configure Factions page**,
  and nothing written here can repair a missed tick.

**Event:** a **new world generated from the main menu** — not a save load. This is
v1 **rows 2 and 7**, which `V1_SCOPE.md` establishes are **one irreversible event**,
plus the owner's **Anomaly-to-zero** ruling ticked on the same screens.
**Written 2026-08-13, game DOWN, before the load.**

🔴 **AMENDED 2026-08-14, still before the load (B23).** Between the writing and
now, the entire faction and ideoligion layer was built and deployed: **eleven
FactionDefs and eleven authored ideos**, plus five vanilla reskins. That is a
material change to what this run will show, so three signatures below were WRONG
as written and are corrected, and S7/S8 are new. **Editing is legal here and only
here — this block's load has still never run, so no log exists to fit a story to.**

🔴 **§1's signatures do NOT carry over wholesale.** They were written against a
campaign reload. Everything below is scoped to *this* event; §1's A2 and A3 log
greps are re-run only as free regression checks (S6), and their live gates are not
re-booked.

## §2 deploy state — what changed on disk since §1

| # | assembly | size | mtime | changed since §1? |
|---|---|---|---|---|
| **B1** | `JawaBench.BridgeTools` — `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll` | **227,840 B** | **2026-08-13 22:23** | 🔴 **YES — a new build that has NEVER been loaded.** 154,112 B → 227,840 B. **21 tools, was 17**; adds `order_pawn`, `set_pawn_rotation`, `set_pawn_style`, `set_pawn_xenotype`. md5 `b9aef17f79ee7bef101a4b5ada7f1c7a`, **byte-identical** to the repo artifact `D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\artifacts\BridgeTools\JawaBench\JawaBench.BridgeTools.dll`. |
| **B2** | `JawaIonWeapons` | 5,120 B | 2026-08-12 21:53 | no |
| **B3** | `OuterRimGalacticEmpire` | 10,752 B | 2026-08-12 16:06 | no |

**Game version for every VERIFIED string below:** `RimWorld 1.6.4871 rev591`,
strings dumped from the deployed
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\RimWorldWin64_Data\Managed\Assembly-CSharp.dll`.

---

## S1 — the companion bundle, **first load of this build**

🔴 **The only assembly that changed, so it is the only genuinely new assembly risk
this load.**

**Gate:** `python.exe src/RimMandrake/bridgetools/prove_new_tools.py` → read line 0,
the deploy census.

✅ **Use `--census`. It is read-only and SAFE ON THE CAMPAIGN MAP** (`2312d7f`):
it reads line 0 and exits before anything is spawned, damaged, roofed or fired,
and deliberately before the paused-game guard, so taking a read needs no pause.

```bash
python.exe src/RimMandrake/bridgetools/prove_new_tools.py --census
```

🔴 **The BARE invocation is NOT a read — never run it on the campaign map.** With no
`--census` it is a full live harness: it spawns pawns, damages them to death, sets
plants, builds roofs, fires incidents and sends letters, and its own selftest scripts
a `*** CLEANUP INCOMPLETE *** Pawn(s) ... are STILL ALIVE` case.

⭐ **It NAMES, it does not count** — which is the point. Verified live 2026-08-14: 22
tools listed by name, plus an explicit **STOP — built but NOT deployed:
`jawa/fire_quest`, `jawa/get_defs`**. ⚠️ **My own prediction of "22, PASS" was wrong
and the tool was right:** it compares artifact against game copy as well as game copy
against registered, so it reports the deploy we owe. **A matching count proves nothing
about which items matched.**

✅ Safe from anywhere, no game needed: `python3 ... --selftest` (WSL cannot reach the
bridge at all, so it exercises the mock worlds and touches no game).

🔴 **DO NOT WRITE THE EXPECTED NUMBER HERE. DERIVE IT AT CENSUS TIME.** This block
used to say *"21 = PASS"*. The gate script already held **22**, the live game already
reported **22**, and the artifact source holds **24** — so the prose would have
**failed a correct deploy on the run we cannot repeat.** A hardcoded count goes stale
at every deploy, silently, and then fails the good build.

```bash
# what the companion SHOULD expose, from the artifact — this is the expected value
grep -rhoE '"jawa/[a-z_]+"' src/RimMandrake/bridgetools/ | sort -u | wc -l
# what the gate script will compare against — MUST agree with the line above
python3 -c "import re;s=open('src/RimMandrake/bridgetools/prove_new_tools.py').read();\
m=re.search(r'ALL_TOOLS\s*=\s*\[(.*?)\]',s,re.S);print(len(re.findall(r'"[^"]+"',m.group(1))))"
```

| census against the derived number | meaning |
|---|---|
| **equal** | ✅ the new build is live. **S1 PASSES.** |
| **short by exactly 2** | the `get_defs` + `fire_quest` deploy did not take |
| **short by more** | an older bundle loaded — read which names are missing, not just how many |
| **0** | the bundle never loaded at all |

⚠️ **If the two commands above disagree with each other, STOP** — the gate script's
`ALL_TOOLS` (`prove_new_tools.py:92-103`) is stale and will fail a correct deploy.
That is CHECK's file; it must be regenerated in the same commit that ships a new
tool. **Gates compare measurements to measurements, never to prose.**

Cheaper second positive: `rimbridge/get_bridge_status` →
`companions.diagnostics` — want `companionErrorCount = 0`, `companionCount` non-zero.

**Log negative — host is unchanged, so §1's grep stands verbatim:**

```bash
grep -nE "\[RimBridge\] (Failed to (load|scan|inspect|prepare|register)|Loader exception|Skipping companion|Could not resolve global BridgeTools|Ignoring companion-local SDK|STARTUP_INIT_FAILURE|Failed to start server)|Companion references RimBridgeServer\.Sdk" "$LOG"
```
**Pass:** zero lines **and** the census equal to the number DERIVED by the two
commands above, at census time. **Fail:** any line, or a census that disagrees
with the derived number — then read WHICH names are missing, not just how many.
🔴 **This used to read "census 21" and that was the very error the box above
forbids.** The gate script already held 22, the live game reported 22, and the
artifact holds 24, so the literal would have failed a correct deploy.

**Silent-failure mode, unchanged:** a companion deploy attempted while the game
runs cannot write the file and nothing says so. The 22:23 deploy landed with the
game down and is md5-verified against the repo artifact, so this should not bite —
**the census is what settles it, not the log.**

---

## S2 — worldgen itself completes (v1 row 7)

🔴 **New for this load. §1 had nothing about worldgen because §1 was a reload.**

| signature — **VERIFIED verbatim** in `Assembly-CSharp.dll` | means |
|---|---|
| `Error in WorldGenStep: ` | a worldgen step threw. **The top-level worldgen catch — this is the one that matters.** |
| `Could not generate world features of def ` | a world-feature generator failed; the world exists but is malformed |
| `Failed to find faction base tile for ` | a faction that had to be placed had nowhere to go — **the expected over-exclusion shape** |
| `No terrain found in biome ` | a biome has no terrain to lay — a real risk on a modded desert world |
| `Could not find player faction.` | worldgen produced no player faction |
| `Could not generate starting map because there is no any player faction base.` | the run is dead at the landing step |
| `No tiles on layer ` | a planet layer never initialised |

```bash
grep -nE "Error in WorldGenStep: |Could not generate world features of def |Failed to find faction base tile for |No terrain found in biome |Could not find player faction\.|Could not generate starting map because there is no any player faction base\.|No tiles on layer " "$LOG"
```

**Pass:** zero lines. **Fail:** any line — and `Error in WorldGenStep:` alone is
enough to distrust the world.

🔴 **There is no worldgen success banner. I looked — RimWorld emits none.** So the
positive sighting is an **observation, not a grep**: the world map renders and the
player reaches the landing-site screen.

> **Evidence command: `rimworld/take_screenshot` at the world map, before landing.**
> That screenshot **is** row 7's gate — `V1_SCOPE.md`'s bar is *seen working
> in-game once*, and a world map on screen is that.

---

## S3 — faction exclusion took (v1 row 2)

**The list is `D:\Luke\dev\Rimworld\infrastructure\state\WORLDGEN_FACTION_CHECKLIST.md`**
— RATIFIED by a retired seat: **20 untick** (12 ordinary count rows in its §1, 8 hidden
checkboxes in its §2), **6 keep** (its §4), plus `OuterRim_RebelAlliance` recorded
present/absent (its §5).

🔴 **Row 2's evidence is NOT a log grep. Nothing in `Player.log` records what was
ticked.** The only call that produces the evidence:

> **`jawa/list_factions`, run AFTER the world exists**, compared against the
> checklist's CUT and KEEP columns.

| result | verdict |
|---|---|
| every CUT defName **absent** AND every KEEP defName **present** | ✅ **PASS** |
| any CUT defName present | that box did not take — **record WHICH one; do not regenerate** |
| any KEEP defName absent | 🔴 worse than a stray cut — a faction the world exists for is missing |

⚠️ **Do not read this off a quicktest.** A debug quicktest never visits Configure
Factions and shows all 54 factions by default — a retired seat's trap, `2d1685e`, which
nearly triggered a needless regeneration. **`list_factions` is evidence only on
the world you just generated.**

**Downstream signatures — what OVER-exclusion looks like afterwards.** All
**VERIFIED verbatim** in `Assembly-CSharp.dll`:

| signature | means |
|---|---|
| `No valid factions found for trade caravans` | 🔴 cut too deep — no trade partners left |
| `Could not find any valid faction for ` · `Could not find any valid faction for this site.` | a quest or site had no faction to hang on |
| `No factions with royal titles found.` | the vanilla `Empire` KEEP entry did not survive |
| `No raid strategy found, defaulting to ImmediateAttack. Faction=` | a kept faction lost its raid config |
| `QuestNode_GetPawn tried generating pawn but couldn't find a proper faction for new pawn.` | quest pawn generation has no faction pool |

```bash
grep -nE "No valid factions found for trade caravans|Could not find any valid faction for|No factions with royal titles found\.|No raid strategy found, defaulting to ImmediateAttack\. Faction=|couldn't find a proper faction for new pawn" "$LOG"
```

**Want zero. ⚠️ These fire during PLAY, not at load — re-grep at session end, not
only after the load completes.**

---

## S4 — the two label checks that catch a deploy miss **before** the irreversible click

Both are read off the Configure Factions page itself, **before** generating.
Evidence: eyes on the page plus `rimworld/take_screenshot`.

| check | pass | fail |
|---|---|---|
| 🔴 **CORRECTED B23.** Vanilla **`Empire`** renders as **"The Galactic Empire"** with an **Emperor** | R15/R11 landed. The Empire moved onto the VANILLA Royalty vessel; `label` "The Galactic Empire", `fixedName` "Galactic Empire", `leaderTitle` "Emperor" | reads **"shattered empire"** with a **"high stellarch"** → `GalacticEmpire.xml` did not land. Record and carry on; do NOT abort |
| ~~⚠️ **`OuterRim_GalacticEmpire` now reads "Galactic Empire" and THAT IS CORRECT**~~ ⛔ **DEAD ROW 2026-08-20 — do not check it at all.** The def is not the vessel and not in the design; whatever label it shows is not a signal. See `infrastructure/state/OWNER_DECISIONS.md`. Original text kept below. | **This block used to demand "the Galactic Empire" here, and that is now the FAILING string.** B40 re-pointed the file off this def onto vanilla `Empire`; nothing patches `OuterRim_GalacticEmpire` any more, so it shows its own shipped label. **Do not read this as a deploy miss and do not regenerate.** | reads "the Galactic Empire" → an OLD `Jawa_Patches` is deployed; the current one has not landed |
| `OuterRim_RebelAlliance` is **ABSENT** from the page | `RebelAlliance_Suppress.xml` set `maxConfigurableAtWorldCreation` to 0 — **absence is the DESIRED outcome, not a defect** | **present and settable** → the patch did not land; file it. **Present but locked at 0** → harmless, worth a line. **Do not revert the patch at the screen.** |

**Also record, as an observation with no pass/fail:** vanilla `Empire`'s name is
**generated**, so the page will probably not say "Fallen Dominion". Screenshot it —
per the checklist, that string is the only record of it.

---

## S5 — Anomaly at zero (owner's ruling, same run)

**Setting:** the Anomaly playstyle, and it is **`AnomalyPlaystyleDef`** — exactly three
defs ship: `Standard` · `AmbientHorror` · `Disabled`
(`…\Data\Anomaly\Defs\AnomalyPlaystyles\AnomalyPlaystyles.xml`).
**Want `AmbientHorror` with the threat fraction dragged to 0.**

🔴 `AnomalyFrequency_None` · `_VeryRare` · `_Rare` · `_Balanced` · `_Intense` ·
`_Overwhelming` are **TRANSLATION KEYS, not defNames** —
`…\Data\Anomaly\Languages\English\Keyed\Misc_Gameplay.xml:499-504`, the labels
`Dialog_AnomalySettings.GetFrequencyLabel` prints beside the slider. Nothing can ever
read back as one.

**Why `AmbientHorror` and not `Disabled`:** `Disabled` carries
`enableAnomalyContent:false`, which kills study, the research tab, the codex and tome
trading. `AmbientHorror` keeps all of it, does not generate the monolith, and — with the
fraction at 0 — spawns nothing on its own while leaving `PitGate`/`FleshmassHeart`
available to fire deliberately.

⚠️ **The slider still exists under `AmbientHorror` and it does NOT start at zero.**
`displayThreatFractionSliders:false` only suppresses the per-category sliders;
`overrideThreatFraction:true` makes `Dialog_AnomalySettings:166-170` draw a single
0..1 slider instead, and `StorytellerUI:239` seeds it at **0.15**. It must be dragged
down. Custom difficulty is required — `overrideAnomalyThreatsFraction` is not a
`DifficultyDef` field at all; it lives on the runtime `Difficulty` object
(`Difficulty.cs:121,374`) and scribes into the save's `<customDifficulty>`.

🔴 **Both are world-creation-permanent.** The "Anomaly settings…" button is drawn under
a `ProgramState.Entry` guard and is simply absent in an existing save.

**Evidence command:**

```
rimworld/save_game        # then grep the .rws on disk:
grep -o "anomalyPlaystyleDef>[^<]*" <the .rws>
grep -o "overrideAnomalyThreatsFraction>[^<]*" <the .rws>
```

**Pass:** the first reads `AmbientHorror` and the second reads `0`. **Fail:** anything
else, including the second being absent — absent means the override was never set.

⚠️ **This costs one save, and there is no other read-back.**
`rimworld/get_game_info` returns only `ticksGame` and `mapCount` and cannot answer
it. **If the save is not taken, S5 is NOT COLLECTED** — the setup screen is gone
and the answer is unrecoverable short of another worldgen.

---

## S6 — carry-over regression, free (B2 and B3, unchanged on disk)

Both passed their §1 log greps and neither DLL changed. Re-run both — two seconds —
purely to confirm the new load did not regress them:

```bash
grep -nE "JawaIon|DamageWorker_IonBuildup|jawaionweapons" "$LOG"   # want ONLY mod-list lines
grep -n "Outer Rim - Galactic Empire" "$LOG"                        # want one hit, version 1.6.9308
```

🔴 **Expect TWO `mandrake.jawaionweapons` hits, not one** — RimWorld prints the
active-mod list twice per run (measured in §1: 6687 and 8241). §1's "any second hit
is the failure" rule was wrong; it is corrected here so nobody re-raises it.

**No live gate is booked for either.** A2's is closed (`ad3e9b0`); A3's live half
is now S3's KEEP check on ~~`OuterRim_GalacticEmpire`~~ ⛔ **vanilla `Empire`**
(re-pointed 2026-08-20; `infrastructure/state/OWNER_DECISIONS.md`) — plus the
`OuterRim_ImpStormtrooper` pawnkind resolve, which is what actually proves the *Outer
Rim - Galactic Empire* mod loaded.

---

## 🔪 DROPPED — signatures with no collectable evidence, and why

**A signature whose evidence cannot be collected is not a signature, it is a wish.**
`V1_SCOPE.md` counts eleven gates that failed this way in one day. These four were
considered and cut rather than written:

| dropped | why |
|---|---|
| *"the desert world is actually desert"* as a **signature** | `V1_SCOPE`'s row-4 correction demands a live `BiomeDef` read, and `jawa/get_def BiomeDef <name>` can supply one — **but only once the landing tile's biome NAME is known, and no call reads a tile's biome back.** Kept instead as S2's screenshot observation, which is what row 7's gate actually asks for. |
| *"the tick-list was ticked correctly at the screen"* | **There is no read-back of the Configure Factions page.** The only evidence is `list_factions` on the world afterwards, which is S3. A second row for the screen itself would be unfalsifiable. |
| *"the Fallen Dominion's generated name is X"* | `Empire`'s name is generated at worldgen and nothing greps it out of the log. Recorded in S4 as a screenshot **observation**, deliberately with no pass/fail. |
| *`OuterRim_ImpStormtrooper` resolves* | A def-existence check. It was already true at §1 and worldgen cannot change it. **Not a worldgen signature.** |

---

## S7 — the eleven new factions exist and are settable 🔴 NEW, B23

**Nothing in §2 as first written knew these existed.** Built and deployed
2026-08-14; `WORLDGEN_FACTION_CHECKLIST.md` predates them and does NOT list them,
so a strict checklist diff will show eleven "unexpected" entries. **That is the
expected outcome, not a defect.**

| must appear on the Configure Factions page | vessel |
|---|---|
| Hutt Cartel · Free Droid Enclaves · Wildsteam Clan · Deepwater Compact · Geonosian Foundry Hive · Ascendant Helix · the Junkers | AUTHORED (`Jawa_*`) |
| Jawa Trade Moot | authored, was "Jawa tribes" |
| The Galactic Empire · Homestead Defense League · Deep Desert Tribes · Blackstar Company · the Forgotten Arsenal | reskinned vanilla vessels |

🔴 **These must be SET TO AT LEAST 1 at the screen, or the campaign's own factions
do not exist in the world.**

🔴 **CORRECTED 2026-08-15 by BUILD, still before this block's load. The previous
sentence here was FALSE and it was dangerous.** It read: *"Seven are authored defs
with `requiredCountAtGameStart 1`, so they should be forced."* **They are not.**
Measured on disk, game down: **only `Jawa_IndigenousTribes` carries
`requiredCountAtGameStart`** (1, max 2). The other seven have `canMakeRandomly
true` and **no required count at all**, so they arrive at the screen defaulting to
**0** and nothing forces them. The reskins ride their vessel's existing count.
⇒ **Every one of the seven must be ticked up BY HAND, or the world simply will not
contain them.** Filed as `seven-factions-have-no-required-count-9c4e17` in
`queue/DECIDE.md`. **A faction absent here cannot be added later — the world is
generated once.**

⚠️ **The Unbound Hive is NOT in this list on purpose.** It was cut 2026-08-14
because its vessel, vanilla `Insect`, is an untick row in §2 of the checklist.

**Evidence:** `jawa/list_factions` after the world exists — the same call as S3 —
plus a screenshot of the page before the click.

---

## S8 — EXPECTED AND HARMLESS. Do not regenerate for these. 🔴 NEW, B23

**This is the section B23 exists for.** Each of these is a red line that is a
correct outcome. Verbatim shapes confirmed in `Assembly-CSharp.dll`.

| signature | why it is harmless |
|---|---|
| `[Jawa Patches] Patch operation Verse.PatchOperationRemove failed` naming `requiredMemes`, `structureMemeWeights`, `classicIdeo` or `disallowedMemes` | We remove six generation-steering nodes that an authored `fixedIdeo` makes dead. **If another mod removed one first, our Remove matches nothing and logs red — but the desired end state, node absent, is already true.** The log line is the only symptom and it means the job is done twice, not undone. |
| `Could not resolve cross-reference: No Verse.XenotypeDef named BTD_<species> found` | R27 puts 31 `BTD_*` xenotypes on seven factions. Three packs ship overlapping species and **BTD Remix dedups at load**; the fact that `BTD_` is the survivor is measured for Jawa and GENERALISED to the rest. A miss degrades one species in one faction — it does not break the faction or the world. **Record WHICH name; the fallback is `guy762_xenotype_*`, never `OuterRim_*`.** |
| `Could not resolve cross-reference: No Verse.PawnKindDef named JDSCIS_*` | The Geonosian hive mixes Separatist droid kinds from a mod that may be off. They are `MayRequire`-wrapped; the group simply fields fewer kinds. |

⚠️ **The failure that is NOT harmless and shares the shape:** a cross-reference
error naming `Jawa_Tribal_Scavenger`, `Jawa_Tribal_Slinger`, `Jawa_Tribal_Elder`
or `Jawa_Colonist`. Those are OURS; they were silently discarded once already
(`c06e89e`) and a recurrence means the ParentName fix regressed. **That one is
worth stopping for.**

```bash
grep -nE "Patch operation Verse\.PatchOperationRemove failed|No Verse\.XenotypeDef named BTD_|No Verse\.PawnKindDef named (JDSCIS_|Jawa_)" "$LOG"
```

---

## §2 execution order

**Before the irreversible click:**
1. **S4** — both label checks on the Configure Factions page. A miss here means
   **stop and fix the deploy**, and it is the only point where that is still cheap.
2. **S3, the act** — drive the 20 unticks and confirm the 6 keeps, from
   `WORLDGEN_FACTION_CHECKLIST.md`. Set **Anomaly → `AmbientHorror`, threat slider
   dragged to 0** on the same screens (S5).

**Immediately after the world exists:**
3. **S2** — the worldgen grep. Want zero lines. Screenshot the world map (row 7's gate).
4. **S3, the evidence** — `jawa/list_factions`, diff against the checklist.
5. **S1** — `prove_new_tools.py --census`; derive the expected number first (S1's two
   commands), then compare. **No literal count belongs in this step.**
6. **S5** — `rimworld/save_game`, then grep the `.rws` for `anomalyPlaystyleDef`
   AND `overrideAnomalyThreatsFraction`. The playstyle alone is not a pass.

**At session end, before the next launch destroys the log:**
7. **S6** plus a re-run of **S3's downstream grep** — those fire during play, not at load.

🔴 **Anything unrun stays UNVERIFIED. An unrun check is not a pass** — §1 closed
with two live gates never run, and that is exactly what this line existed to
prevent.

---

## §2 RESULTS — **for the NEW WORLD GENERATION load only.** Fill in AFTER it runs.

⬜ **Blank as of 2026-08-13, game down. This load has NOT yet run.**
🔴 **If you are reading this table blank after a load has happened, the load was
spent without closing it — say so, and mark the rows NOT COLLECTED. Do not
reconstruct a result from the log.**

| # | check | evidence collected? | result |
|---|---|---|---|
| S1 | companion census = the number derived at census time (record BOTH: derived, and observed) | | |
| S1 | `[RimBridge]` failure grep = 0 | | |
| S2 | worldgen error grep = 0 | | |
| S2 | world map screenshot (row 7 gate) | | |
| S3 | `jawa/list_factions` vs checklist — 20 CUT absent | | |
| S3 | `jawa/list_factions` vs checklist — 6 KEEP present | | |
| S3 | downstream over-exclusion grep = 0 (at session end) | | |
| ~~S4~~ | ~~`OuterRim_GalacticEmpire` label reads "the Galactic Empire" (observation, not a gate)~~ ⛔ **DEAD 2026-08-20 — the vessel is vanilla `Empire`; nothing patches this def. Do not record it.** See OWNER_DECISIONS.md. | — | — |
| S4 | ⭐ **vanilla `Empire`** label reads **"The Galactic Empire"**, `fixedName` **"Galactic Empire"**, `leaderTitle` **"Emperor"** (replaces the struck row above) | | |
| S4 | `OuterRim_RebelAlliance` absent from the page | | |
| S5 | `.rws` `anomalyPlaystyleDef` = `AmbientHorror` AND `overrideAnomalyThreatsFraction` = `0` | | |
| S6 | A2 / A3 log greps unchanged | | |
| S7 | eleven campaign factions present on the page, each set ≥ 1 | | |
| S7 | `jawa/list_factions` returns all eleven after worldgen | | |
| S8 | `PatchOperationRemove` failures — record which, then IGNORE | | |
| S8 | `BTD_*` xenotype misses — record WHICH names | | |
| S8 | 🔴 zero cross-reference errors naming `Jawa_Tribal_*` / `Jawa_Colonist` | | |

---

# §3 — LOAD 2026-08-15, the deploy window. ⚰️ CLOSED 2026-08-20, EVIDENCE UNRECOVERABLE

> 🔴 **Nothing below was ever collected, and nothing below can be collected now.**
> The Results tables stayed blank, and `Player.log` is rotated by the launcher on
> every start — at least five launches have happened since, so the log this block
> was written against no longer exists on disk or in `deployed/logs/`.
> **Read this block as a record of what was ONCE intended, never as a finding.**
> If a row here still matters, re-book it in a new block; do not launch against these.

**Event:** the load following the 2026-08-15 deploy window (`NEXT_RELOAD.md` §1.0).
A **quicktest** session, not a save load and **not worldgen**. Written **before
launch, game DOWN**, by BUILD. Closes queue item **B23** for this block.

## §3 deploy state — verified on disk, game down, 15:47

| # | artifact | state entering this load |
|---|---|---|
| **D1** | `JawaBench.BridgeTools` companion — `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\JawaBench.BridgeTools.dll` | deployed; md5 `f0d4e6e7…` matches the repo artifact (REP, this window). **Built with `--gm`** is the claim under test — without it `jawa/fire_incident` and `jawa/send_letter` are stripped and §5's L3 cannot fire at all |
| **D2** | `JawaPlantGrowth.dll` — `…\Mods\JawaPlantGrowth\Assemblies\JawaPlantGrowth.dll`, 8,704 B, mtime 2026-08-15 10:31 | 🔴 **an assembly that has NEVER been loaded.** `mandrake.jawaplantgrowth` sits at index **571**, after `brrainz.harmony` (index 1) — the Harmony postfix can bind |
| **D3** | `DesertVehicleReskin` — `…\Mods\DesertVehicleReskin` | XML + loose PNGs, an **update** to an installed mod. `mandrake.desertvehiclereskin` at **541**, after `sarg.alphavehiclesneolithic` (**528**) |
| **D4** | `ModsConfig.xml` | `<activeMods>` **575**, down from 576: `com.yayo.yayoani.continued` removed this window (BUILD, 15:47). All three xenotype donors — `btd.xenotyperemix.starwars`, `guy762.starwarsxenotypes`, `neronix17.outerrim.galacticdiversity` — **absent**; `mandrake.starwarsraces` (562) stands alone |
| **D5** | def dump | armed at 13:27 via `dump_request.txt` = `all`; re-read happens at **this** startup, after D1–D4 |

---

## T1 — the companion bundle loaded and is the build we measured

**Gate is a derived number, never a literal.** Derive first, then census:

```bash
grep -rhoE --include='*.cs' '"jawa/[a-z_]+"' src/RimMandrake/bridgetools/ | sort -u | wc -l
```
🔴 `--include='*.cs'` is load-bearing — without it a commented `[Tool("jawa/…")]`
in `prove_new_tools.py:112` inflates the count by one and fails a correct build.
Then `rimbridge/list_tools` and count the `jawa/*` names.

| observed | verdict |
|---|---|
| = derived count | ✅ pass, built **with `--gm`** |
| = derived count **− 2** | 🔴 built **without `--gm`** — `fire_incident` and `send_letter` stripped. **L3 is uncollectable; do not report it as a failure of the Empire** |
| anything else | ⛔ **STOP.** The deployed companion is not the one measured; every `jawa/*` result this load is evidence of nothing |

Log negative — strings VERIFIED in the `#US` heap of `RimBridgeServer.dll` (§1):

```bash
grep -nE "\[RimBridge\] (Failed to (load|scan|inspect|prepare|register)|Loader exception|Skipping companion|Could not resolve global BridgeTools|Ignoring companion-local SDK|STARTUP_INIT_FAILURE|Failed to start server)|Companion references RimBridgeServer\.Sdk" "$LOG"
```
Want **zero lines**.

---

## T2 — `JawaPlantGrowth` bound at all. **First load of this assembly.**

Strings below are VERIFIED in the `#US` heap of the **deployed**
`JawaPlantGrowth.dll` (`strings -a -el`, 15:49) — not guessed from the source.

```bash
grep -nE "\[JawaPlantGrowth\]" "$LOG"
```

| line | meaning |
|---|---|
| `[JawaPlantGrowth] scaling <N> plant defs (default x4, tree x2.5), <M> exempt, <K> terminator biome(s) at x0.4.` | ✅ **the only positive evidence the assembly ran.** Record N, M and K verbatim |
| `[JawaPlantGrowth] failed to build the growth tables, leaving growth vanilla: <ex>` | 🔴 **real defect.** The mod loaded and gave up; growth is vanilla. Capture the exception |
| `[JawaPlantGrowth] terminator biome '<name>'` | informational — record which biome it resolved |
| **nothing at all** | 🔴 the answer is **"not deployed / not in ModsConfig"**, **NOT** "no effect". Everything under §5 L6 is then uninterpretable and must be marked NOT COLLECTED, not FAILED |

⚠️ **A silent Harmony failure has no string of its own.** If the startup line is
present but growth reads vanilla in L6, that is a *patch* failure, not a *load*
failure, and the two must not be written up as one.

---

## T3 — `DesertVehicleReskin` — 🚫 **NO LOG EVIDENCE IS POSSIBLE**

Filed so nobody greps for it. Pure XML + loose PNGs: a texPath override reaches
every def whether or not a patch ran, and `Failed to find any textures at` fires
only when **every** direction of a `Graphic_Multi` is missing. **It settles on the
Architect menu and the labels (§5 L5) or it does not settle.** A clean log is not
a pass here.

🔴 **B62 is UNBUILT.** Only `eopie sled` can pass this load. Seeing `Ox cart`,
`Chariot`, `Covered carriage`, `War chariot` is the **expected pre-B62 baseline**,
not a failure, and must not be written up as one.

---

## T4 — EXPECTED AND HARMLESS. Do not stop for these. 🔴 **T4 REVERSES §2's S8**

| signature | verdict for **this** load |
|---|---|
| `[Jawa Patches] Patch operation Verse.PatchOperationRemove failed` naming `requiredMemes`, `structureMemeWeights`, `classicIdeo` or `disallowedMemes` | ✅ **harmless, unchanged from S8.** We remove six generation-steering nodes an authored `fixedIdeo` makes dead. If another mod removed one first our Remove matches nothing and logs red — the desired end state, node absent, is already true. The line means the job was done twice, not undone |
| `Could not resolve cross-reference: No Verse.PawnKindDef named JDSCIS_*` | ✅ **harmless, unchanged from S8.** The Geonosian hive mixes Separatist droid kinds from a mod that may be off; they are `MayRequire`-wrapped and the group simply fields fewer kinds. Source: `src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaGeonosianFoundryHive.xml` |
| `Could not resolve cross-reference: No Verse.XenotypeDef named BTD_*` (also `guy762_*`, `OuterRim_*`) | 🔴 **NO LONGER HARMLESS — this is the reversal.** S8 called these benign because the donor packs were installed and BTD Remix dedup'd at load. **All three donors are OFF in D4.** Under the donors-off configuration this exact grep IS check **C36**, and a hit is a **C36 FAILURE**: a def in `mandrake.starwarsraces` or `Jawa_Patches` still points at a donor that no longer loads. **Record every name.** `Jawa_Patches` carries `BTD_` references in at least five files (`JawaJunkers.xml`, `AlienSpawnEnablers.xml`, `GamorreanXenotype.xml`, …) — those are the suspects |

🔴 **The failure that is NOT harmless and shares the crossref shape:** any
cross-reference naming `Jawa_Tribal_Scavenger`, `Jawa_Tribal_Slinger`,
`Jawa_Tribal_Elder` or `Jawa_Colonist`. Those are OURS; they were silently
discarded once (`c06e89e`) and a recurrence means the ParentName fix regressed.
**Worth stopping for.**

```bash
grep -nE "Patch operation Verse\.PatchOperationRemove failed|Could not resolve cross-reference.*(BTD_|guy762_|OuterRim_)|No Verse\.PawnKindDef named (JDSCIS_|Jawa_)|Could not find type named" "$LOG"
```

---

## T5 — the mod-list change (D4), and the one gap it does NOT close

`com.yayo.yayoani.continued` is gone from `<activeMods>`. Expected: **zero**
`com.yayo` / `yayoAni` lines, and the lightsaber no longer flies up-and-behind on
draft (observation, §5, not a gate).

⚠️ **Nothing is loaded from a save this load**, so `Could not load reference to`
(Scribe, a dead name held in a SAVE) must not appear at all. If it does, someone
loaded a save and this block does not describe that event.

📌 **`RG_BoilingForest` gap:** the *pre-load* dump held defs from
`regrowth.botr.boilingforest`, which no longer loads — an xpath onto those
validates clean and matches nothing in game (live instance:
`JawaWorld_BiomeMix.xml:140`). D5 re-arms the dump, which closes it **at this
startup**. **Any `--defs` verdict quoted from the OLD dump is void.**

---

## T6 — the eight authored factions. 🔴 **The owner asked for this test by name.**

**Two questions that look like one and are not.** Answer them in this order and do
not let the second contaminate the first.

### T6a — do the defs LOAD? (this is the one that closes B56)

Five of the eight were being **discarded at load** on 2026-08-15: `xenotypeChances`
is a **dictionary-keyed** field and they used the `<li>` list shape, so
`XenotypeChance.LoadDataFromXmlCustom` hit `ParseFloat(null)` and RimWorld threw the
whole `FactionDef` away. Fixed offline in `fe6b460`.

**Verified on disk before this launch, game down:** zero `<li>` under
`xenotypeChances` in all 8 files, and the 8 deployed copies under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Defs\FactionDefs\`
are **byte-identical to the repo** (md5, all 8). So the fix is genuinely in the
game copy, not just in `src/`.

```bash
grep -nE "Exception loading def from file Jawa.*\.xml|XenotypeChance\.LoadDataFromXmlCustom|ParseAndReturnDef_RimWorld_FactionDef" "$LOG"
```
Want **zero lines**. Then all eight resolve — `jawa/get_def` or the refreshed dump:

`Jawa_IndigenousTribes` · `Jawa_HuttCartel` · `Jawa_Junkers` ·
`Jawa_DeepwaterCompact` · `Jawa_GeonosianFoundryHive` · `Jawa_WildsteamClan` ·
`Jawa_AscendantHelix` · `Jawa_FreeDroidEnclaves`

📌 **Free side-effect worth measuring:** the five discards were costing ~19,613
`Possible Matches` lines EACH — about 98,000 of the previous load's 99,700 lines,
~8 MB to C: with a per-line flush. **A log that is suddenly ~2% of its old size is
corroboration that T6a passed.** A log still near 100k lines means it did not.

### T6b — do the factions get GENERATED into the world? ⚠️ **Expect NO for seven**

🔴 **This is the trap, and it will read exactly like the bug coming back.** A def
that loads and a faction that exists in a world are different questions. Measured on
disk: **only `Jawa_IndigenousTribes` has `requiredCountAtGameStart`** (1, max 2).
The other seven are `canMakeRandomly true` with **no required count**, so a
quicktest world — which nobody hand-configures — will very likely contain **none of
them**.

| `jawa/list_factions` on the quicktest shows | ruling |
|---|---|
| `Jawa_IndigenousTribes` present | ✅ expected |
| the other seven absent | ✅ **EXPECTED, NOT A DEFECT.** Record it and move on |
| the other seven absent **AND** T6a's grep is non-empty | 🔴 the load bug is back — that combination, not absence alone |
| any of the seven **present** | ✅ also fine — `canMakeRandomly` can roll them in |

⛔ **Do not "fix" anything on the strength of T6b.** Whether the seven should carry
`requiredCountAtGameStart` is a scope call, filed as
`seven-factions-have-no-required-count-9c4e17` in `queue/DECIDE.md`. It matters at
**worldgen**, which is not this load.

---

## §3 execution order

1. **Startup log FIRST**, before any bridge call that mutates anything —
   `python.exe src/RimMandrake/Utils/harvest_log.py`. The open
   `GeneratePawnRelations` NRE cluster becomes unattributable the moment anyone
   calls `jawa/spawn_pawn`.
2. **T2** and **T4** off that same first harvest — both are startup-time.
3. **T1**, the census. Nothing `jawa/*` below it is interpretable until it passes.
4. Then `NEXT_RELOAD.md` §5 in its own order — **L0 first**, it is one screenshot
   and it decides a large body of art work.
5. **T3** at §5 L5, on the Architect menu. There is nothing to grep.

🔴 **Anything unrun stays UNVERIFIED. An unrun check is not a pass** — §1 closed
with two live gates never run, and that is the line that exists to prevent it.

---

## §3 RESULTS — fill in AFTER the load, from the log while it still exists

⬜ **Blank as of 2026-08-15 15:50, game down. This load has NOT yet run.**
🔴 **If you are reading this table blank after the load happened, the load was spent
without closing it — say so and mark the rows NOT COLLECTED. Do not reconstruct a
result from the log.**

| # | check | evidence collected? | result |
|---|---|---|---|
| T1 | derived `jawa/*` count (record it) vs observed census (record it) | | |
| T1 | `--gm` verdict: full count, count−2, or STOP | | |
| T1 | `[RimBridge]` failure grep = 0 | | |
| T2 | `[JawaPlantGrowth] scaling …` present — record N / M / K | | |
| T2 | `failed to build the growth tables` absent | | |
| T3 | 🚫 no log evidence exists — settled at §5 L5 or not at all | n/a | |
| T4 | `PatchOperationRemove` failures — record which, then IGNORE | | |
| T4 | 🔴 `BTD_` / `guy762_` / `OuterRim_` crossrefs = **0** (this is C36) — record every name | | |
| T4 | `JDSCIS_` misses — record which, then IGNORE | | |
| T4 | 🔴 zero crossrefs naming `Jawa_Tribal_*` / `Jawa_Colonist` | | |
| T5 | zero `com.yayo` / `yayoAni` lines | | |
| T6a | zero `Exception loading def from file Jawa*.xml` | | |
| T6a | all 8 Jawa faction defNames resolve (list which, if any, do not) | | |
| T6a | log line count — record it; ~2% of the previous ~99,700 corroborates | | |
| T6b | `jawa/list_factions` — which of the 8 the quicktest world actually holds | | |
| T5 | zero `Could not load reference to` (nothing was loaded from a save) | | |

---

## S7 — BUILD's items, 2026-08-20. Eight greps, all decided from the startup log or the dump.

**Run these on `Player.log` the moment the main menu appears, before anything touches the
game.** Every one is a number that already has a known "before", so a result is a verdict
rather than a reading.

```bash
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"

grep -c "Failed to find any textures at"        "$LOG"   # D-CHK2 magenta heads. was 3, want 0
grep -c "not <li>.*biomeConfigs"                "$LOG"   # B63 biome mix.       was 28, want 0
grep -c "OuterRim_Jawa"                         "$LOG"   # B58 dead defName.    want 0
grep -nE "Jawa_Patches|mandrake\.jawa\.patches" "$LOG" | grep -i error   # want nothing
grep -c "Could not resolve cross-reference"     "$LOG"   # the re-tag + 48 kinds. see below
```

🔴 **THE ONE THAT MATTERS MOST IS NOT A GREP.** After the load, run

```bash
python3 src/RimMandrake/Utils/weapon_tag_audit.py
```

with **no `--anyway`**. It refuses unless the dump's mod set matches `ModsConfig.xml`, so a
clean run is itself the proof that the census is finally authoritative. Then read two
numbers off it:
* **pawn kinds with every weapon tag empty** — was **49** provisionally. Want it in the
  low teens, and 🔴 **zero of ours**.
* **emptied tags** — was 35. The re-tag patch adds 154 weapons' worth of vanilla role
  tags, so most of the vanilla rungs should be full again.

🔴 **THE MOD LIST IS 576 AS OF 2026-08-20 — the owner swapped the terrain and world-map
retexture mods, and this is now the current set.** Recorded in
`infrastructure/state/modlists/ModsConfig.FULL.LATEST.xml`.

```
OUT (4)  zal.worldmapenhanced · noxilie.regrow.wmb.advancedbiomes
         noxilie.regrow.wmb.alphabiomes · noxilie.regrow.wmb.morevanillabiomes
IN  (2)  grimterra.terrainretexturemod · grimterra.worldmap
```

⇒ **The provisional counts above were taken at 578 and are now one mod-set stale.**
They remain the right ORDER of magnitude and the right list of names to look for, but
re-derive rather than diffing against them. This is exactly why
`weapon_tag_audit.py` refuses to run when the dump and the list disagree.
⭐ Retextures, so no def should change: all four removed mods and both added ones ship
textures, not weapons or pawn kinds. If the weapon census moves by more than a rounding
of the counts, something else changed and it is worth finding out what.
✅ Checked already: nothing under `src/` references the removed packageIds except the
provenance blocks of `The Salvation.rid` and `MandrakeJawa.xtp`, which record the mod
list at SAVE time and are not functional references. `validate_save_artifact.py` re-run
against the new set: **251/267 resolve, no dangling names.**
🪤 **Count the children of `<activeMods>`, never `<li>` elements in the file.** A bare
`grep -c '<li>'` also sweeps in the five `<knownExpansions>` entries and reports a number
five too high — which I did, and it would have sent someone hunting five mods that were
never added. Same family as the knownExpansions overcount recorded in the deploy skill.

✅ **LOAD ORDER CHECKED, and it is clean.** `mandrake.jawa.patches` sits at **573/578** with
`jawafactionslate`, `zal.worldmapenhanced`, `guy762.kotordroids`,
`btd.gbp.shippack.kotor.vge` and `rimdefdump` after it. Every `defName` targeted by every
patch in `Jawa_Patches/Patches/` was resolved to its owning mod and compared against that
position: **0 targets are owned by a mod that loads later.** A patch whose target has not
loaded yet matches nothing and logs nothing, so this was worth the two minutes.

⚠️ `Could not resolve cross-reference` has a known pre-existing floor from the cherrypick
(25 across 2 defs at the last measurement). What matters is whether any line names a
`Jawa_*` pawn kind, a `Jawa_Ion*` tag or a stormtrooper/Mandalorian apparel defName — those
would be MINE, and `apparelRequired` is the loud half of the 48-kind build.

**On the Configure Factions page, before generating:**
* all eight `Jawa_*` factions arrive at a count of **at least 1** untouched.
* Configure Planet reads **Scale 7 · Coverage 100%**. 🔴 If Scale reads 10 the Worldbuilder
  preset lost its parameters — ABORT, do not generate.

### S7b — the re-sort after WME went back in, 2026-08-20. Two faults found, both fixed.

The list is **577** (WME restored). RimSort's re-sort broke two orderings that nothing in
the mod metadata was defending:

🔴 **`mandrake.jawafactionslate` had been moved to 184 of 577, and it must be LAST.**
It patches `startingCountAtWorldCreation` to 0 on every faction that is not ours, and every
operation is a `PatchOperationConditional` with **no `<nomatch>`** — deliberate, so a def
from a dropped mod is silent instead of a red error, but the price is that a faction whose
mod has not loaded yet is *also* silent. Measured at position 184: **24 of the 48 factions
it patches were defined by mods loading after it**, so half the slate would have appeared
on the Configure Factions page anyway — and a world generates once.
⇒ Moved to **576/577**, and `<loadBottom>true</loadBottom>` added to its `About.xml` so a
future re-sort cannot undo it. Re-measured: **0 factions missed.**

🔴 **`grimterra.worldmap` was at 443, before `regrowth.botr.core` at 461.** ReGrowth
rewrites the same two `<texture>` fields GRimTerra repoints (AridShrubland, Tundra) and the
last patch applied wins, so ReGrowth was overwriting GRimTerra on AridShrubland — **9.1% of
the planet**. Moved to 460, immediately after ReGrowth at 459. This is the SECOND time this
pair has come out wrong from a sort; if it happens again, the durable fix is a `loadAfter`
on GRimTerra rather than another manual move.

✅ WME is back at 411, below GRimTerra at 460 — the base-coat/top-coat arrangement DECIDE
ruled for, so the 23.9% GRimTerra does not cover (Ocean, Wasteland, PoisonForest…) renders
in WME's art rather than vanilla's.
✅ Re-checked after the sort: **0** `Jawa_Patches` targets are owned by a mod that loads
later.

### The Tidal Lock settings: in place, and there is nothing else to write

* **The Worldbuilder preset IS the planet type**, and it is installed at LocalLow
  `Worldbuilder/TidallyLocked/Preset.xml` — byte-identical to
  `design/Jawa/worldbuilding/TidallyLocked_Preset.xml`, carrying `myLittlePlanetSubcount 7`,
  `planetCoverage 1`, `saveGenerationParameters True` and the 15 `Jawa_*` faction counts.
* ⛔ **There is no AlienWorlds settings file to deploy, and writing one would be inert.**
  Read off `AlienWorldsFramework.cs:34-42`: when the backend is anything but `Standalone` —
  i.e. whenever Worldbuilder is present — `selectedPlanetType` is unconditionally
  overwritten with `"Unknown"`. `ferny.worldbuilder` is active at 412.
* ⛔ **There is no MyLittlePlanet setting file either.** `WorldGenRules.subcount` is a static
  field defaulting to **10** (`TileSize.cs:16`), set at runtime from the world page. The
  preset is what drives it to 7 — which is exactly why **Scale 7 is an ABORT check** and not
  a formality.


---

# §4 — LOAD 2026-08-20, the owner's morning load. **✅ CLOSED 2026-08-20 — PASS.**
*Results below, plus a CORRECTION block filled from the 578-mod load.*
🔑 **This is the block `score_inhabited_load.py` parses — leave its signature strings alone.**

**Run sheet is not here.** It is `infrastructure/state/queue/CHECK.md` →
`MORNING_RELOAD_PLAN_1`, and it is ordered. This block records only the thing that
cannot be recovered after launch: **the state the machine was in before it started.**

## §4 deploy state — measured on disk 2026-08-20 07:4x, game DOWN

| # | artifact | state entering this load |
|---|---|---|
| **E1** | `JawaBench.BridgeTools.dll` — `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\JawaBench\` | md5 **`04cb0977e66af0cb58d9c6f6ecf40acc`**, byte-identical to CHECK's build claim. **112 `jawa/` tool names in the assembly against 106 live last session — six new, none ever exercised in a running game.** |
| **E2** | all four mod assemblies | `Inhabited.dll`, `JawaIonWeapons.dll`, `JawaPlantGrowth.dll`, `RimDefDump.dll` — **every one md5-identical repo↔game.** No assembly is ahead of its deployed copy, so this load carries **no new DLL** and nothing needs the shutdown window |
| **E3** | `ModsConfig.xml` | `<activeMods>` **578**, md5 `deefb393e95824c48a700efa0fa734bb`, rewritten **07:37:24** — ⚠️ **updated after this block was first written: the owner enabled Inhabited himself in RimSort.** Frozen `ModsConfig.FULL.LATEST.xml` matches, so a later `modlist_swap --restore` will NOT silently switch it back off |
| **E4** | `mandrake.inhabited` | 🟢 **NOW ENABLED — index 577 of 578, last in load order, after `brrainz.harmony` (1) as its `loadAfter` requires.** 17 files in sync, 269 `CharacterDef`s across 11 cast rosters. 🔴 **This is a C# assembly the engine has NEVER loaded**, so it rides with the world stages against the skill's solo rule — signatures below are what make that affordable |
| **E5** | def dump | 🟢 **ARMED, and now unambiguously CORRECT.** The dump on disk (`fcdc0322cf61d672`) described the 577-mod set and **lapsed the moment E4 was ticked**; this load must retake it or every `--live` check afterwards is measured against a game that no longer exists. ⚠️ **The marker is not consumed — delete `dump_request.txt` after this load** or every future one pays ~27 s and ~1.2 GB again |
| **E7** | savegame mod records | `sync_mod_state.py --apply` reconciled 6 files to **578 mods / rev591** (`WORLDMAP_gen`, `_sub7`, `_sub7b`, `_sub8`, `rt_probe`, plus `ModsConfig`'s `<version>`). Backups alongside as `*.bak-sync_mod_state`. ⇒ **no mod-list mismatch warning when a WORLDMAP save is opened** |
| **E6** | `Jawa_Patches` and every other deployed mod | plan reports **in sync**, no `-` line anywhere. `GalacticEmpire.xml` validates **0 errors, 14/14 operations matching exactly 1 node** against the full 577-mod def set |

## §4 the one signature worth writing down in advance

The run sheet's own criteria are the owner LOOKING at the planet, which is right and is
not a log string. The one thing a log can settle that eyes cannot:

| signature | verdict |
|---|---|
| `first_light.py` reports **112** `jawa/` tools | ✅ the deployed companion is the one measured; every `jawa/*` result this load is evidence |
| it reports **106**, or any other number | ⛔ **STOP.** The game loaded a different companion than the one byte-verified at E1 — most likely a stale copy elsewhere on the path. Nothing from the six new tools counts until that is explained |
| `world_links_import` refuses `world/ASHKARR_WORLDMAP_links.csv` | 🔴 **the known risk, stage 2 of 7.** The format fix landed in `47dcaf0` and has **never run**. Debug it before stages 3–7; do not skip past it, because every later stage renders on top of links |

## §4 the Inhabited signatures — MANDATORY, it is an assembly that has never run

🔴 **Written before launch, per the waiver condition.** `Inhabited` calls
`PatchAll` on two Harmony patches whose targets resolve **at startup**, so the
dangerous failures all land in the first seconds and are distinguishable from the
world-stage work by their prefix alone. Every line below is `[Inhabited]` or names
the mod's own types — **nothing here can be confused with a `jawa/world_*` failure**,
which is what makes batching it with the seven world stages affordable.

| signature | verdict |
|---|---|
| 🔑 **`[Inhabited] ready: 2 patches, 269 characters, 0 places, 0 casts.`** | ✅ **THE PASS. Predicted in full, before launch.** BUILD added this line at 07:44 for exactly this purpose — a successful load is otherwise completely silent. **Derived, not guessed:** 2 `[HarmonyPatch(typeof(…))]` classes (`Game`, `QuestGen_Pawns`); 269 `Inhabited.CharacterDef` instances across 11 cast rosters; and `Defs/` ships **no** `InhabitedPlaceDef` or `InhabitedCastDef` instance at all |
| ⚠️ **`0 places, 0 casts` is CORRECT and must not be read as a fault** | The C# classes exist (`InhabitedPlaceDef.cs`, `InhabitedCastDef.cs`) but no XML instance ships. Places are made at runtime by *Create place at current tile*. **Zero here means "none authored yet", never "the def type failed to load"** — and the two are indistinguishable from the number alone, which is why it is written down before the log exists |
| `2 patches` reads **0** or **1** | 🔴 **the patches did not bind.** The counts after it can still be right, so the rest of the line looks healthy — this field is the only one that proves Harmony worked |
| `269 characters` reads anything else | 🔴 partial parse of the cast rosters. The roster is not what was authored; do not judge the cast from a spawn menu |
| **nothing at all with an `[Inhabited]` prefix, anywhere in the log** | 🔴 **NOT LOADED — not "no effect".** The `ready:` line is unconditional in a `[StaticConstructorOnStartup]` constructor, so its absence means the assembly never ran. Check the packageId survived RimSort's write before concluding anything else |
| `HarmonyException` / `AmbiguousMatchException` naming `QuestGen_Pawns.GeneratePawn` | 🔴 **the predicted failure, and the most likely one.** `Patch_BeggarsFromPool` pins a specific overload by parameter list; the source comment flags that a wrong list throws at startup. **The whole mod's patches fail together** — `PatchAll` is not per-patch |
| `HarmonyException` naming `Game.DeinitAndRemoveMap` | 🔴 same class, `Patch_MapRemoval`. Survivors would not return to the roster |
| `[Inhabited] WorldObjectDef Inhabited_Place did not load.` | 🔴 the def half failed while the assembly loaded. Places cannot be created; every debug action below is uncollectable |
| `[Inhabited] no CharacterDefs loaded. Run cast_to_xml.py --write and redeploy.` | 🔴 the 269 cast defs did not parse. **Predict 269** — any other number is a partial parse and the roster is not what was authored |
| `[Inhabited] created <name> at tile <N>` | ✅ **the positive observation.** Dev mode → debug actions → `Inhabited` → *Create place at current tile* |
| `[Inhabited] roster of <place> now holds 3.` | ✅ *Stuff roster (3 pawns)* worked; the `ThingOwner<Pawn>` accepted real pawns |
| `[Inhabited] roster refused <pawn>` | 🔴 the container rejected a pawn — the architecture claim itself is in doubt |

⚠️ **The false pass, and BUILD closed it at 07:44.** `PatchAll` throwing does **not**
stop the defs loading, so `Spawn authored character` can still list all 269 people and
look perfectly healthy while **both Harmony patches are dead** — nothing returns to a
roster, no beggar is ever drawn from the pool. **A working spawn menu is not evidence
the patches bound.** Before this morning the only counter-evidence was the *absence* of
a `HarmonyException`, which is the weakest kind. Now the `ready:` line carries
`<n> patches` as a positive count. 🔑 **Read that field first; it is the one number
that cannot be faked by a healthy-looking menu.**

⚠️ **E2 is superseded and this is deliberate.** `Inhabited.dll` was rebuilt and
redeployed at **07:44:23** while this block was being written — repo and game both
md5 `f362b782942f6b4e83ef36f2c16a93b9`, verified after the change, so the deploy is
current. The DLL the game will load is **not** the one E2 recorded. Trust this
paragraph over E2's hash.

## §4 Results — filled 2026-08-20 from the live load. ✅ **PASS**

**The prediction landed character for character.** Recorded here before the log rotates.

```
[Inhabited] ready: 2 patches, 269 characters, 0 places, 0 casts.
```

| # | predicted | observed | verdict |
|---|---|---|---|
| **patches** | 2 | **2** | ✅ **both Harmony patches bound.** This is the field that could not be faked by a healthy spawn menu, and it is green. `Game.DeinitAndRemoveMap` and `QuestGen_Pawns.GeneratePawn` both resolved their targets at startup |
| **characters** | 269 | **269** | ✅ every authored `CharacterDef` across the 11 cast rosters parsed. No partial parse |
| **places** | 0 | **0** | ✅ correct, and correctly NOT a fault — no `InhabitedPlaceDef` instance ships; places are made at runtime |
| **casts** | 0 | **0** | ✅ same |
| `HarmonyException` / `AmbiguousMatchException` | absent | **0 occurrences** | ✅ the predicted most-likely failure did not occur |
| any error naming `Inhabited` | absent | **none** | ✅ clean |

**E5 — the def dump retook itself as required.** `[RimDefDump] wrote 532 def-type files
… done in 16397 ms`, against 529 types before: **Inhabited's three new def types are in
the dump**, so `--live` checks now measure the 578-mod game rather than the lapsed
577-mod one. 🔑 **`dump_request.txt` deleted after the load** — the marker does not
consume itself and would otherwise have charged every future load ~16 s and ~1.2 GB.

⚠️ **NOT closed by this block: 16 red errors in the load, none of them Inhabited's.**
Triage belongs to whoever harvests (`harvest_log.py`), not here — this block only ever
claimed the Inhabited assembly and the dump. **Do not read this ✅ as "the load was
clean."**

⚠️ **What this does NOT prove.** The patches *bound*; nothing here shows they *work*.
No pawn has entered or left a roster, and no beggar has been drawn from the displaced
pool. `ROSTER_SOAK_100_DAYS_1` in `CHECK.md` is the architecture gate and it is
untouched by this result.

## §4 CORRECTION — written by DECIDE 2026-08-20 07:5x, BEFORE the log exists

⚠️ **Legitimate under this file's rule 1.** That rule forbids editing signatures *after that
load's log exists*; this load has not started. E1, E2, E5 and E6 stand unchanged. **E3 and
E4 were overtaken by the owner while the block was being written** and both are now false in
a way that changes what is collectable.

| # | ⛔ what it says | ✅ what is true at 07:5x, game DOWN |
|---|---|---|
| **E3** | ~~`<activeMods>` **577**, mtime 00:49, md5 `5cb6857188…`~~ | **578**, mtime **07:37**, md5 **`deefb393e95824c48a700efa0fa734bb`**. `ModsConfig.FULL.LATEST.xml` moved with it, so LIVE still matches FULL — this is the owner's real list, not a spike |
| **E4** | ~~**DEPLOYED BUT NOT ENABLED — deliberately, the owner's call.** The packageId is absent from `ModsConfig.xml`. ⇒ `Inhabited.dll` has still never been loaded. Every `Inhabited` debug action is uncollectable until he ticks it~~ | 🔴 **HE TICKED IT.** `mandrake.inhabited` is in `<activeMods>` (commit `1254026`, *"the set is 578 for this load"*). ⇒ **Every `Inhabited` debug action IS collectable on this load**, and `ROSTER_SURVIVES_OFFMAP_PROOF_1` — the architecture gate — can be started tonight rather than next cycle |

### 🔴 The signature E2 does not carry, and this load needs it

E2 reasons from **md5 repo↔game** and concludes *"this load carries no new DLL."* That is
true about *drift* and false about *risk*: `Inhabited.dll` is 16 source files that the engine
has **never once loaded**. A first load of an assembly is exactly the case the
load-round skill says to run **solo**, and it is not solo — it rides a 578-mod list.
⇒ The waiver's condition applies, so the signature goes here, before launch:

| signature in `Player.log` | verdict |
|---|---|
| no `Inhabited` line at all, anywhere | ⛔ **the mod did not load.** Check the packageId resolved; do not interpret any other Inhabited result this load |
| `Could not load reference to` naming an `Inhabited.*` type | 🔴 a Def references a class the DLL does not export — name mismatch between XML and C#. Expected first-run failure #1 |
| `Exception in static constructor` / `Harmony` + `Patch_BeggarsFromPool` | 🔴 the beggars patch missed its target. **Expected first-run failure #2, and the most likely of the three** — the design doc named a class (`GiveQuest_Beggars`) that does not exist, and the real one is `QuestNode_Root_Beggars` at `:103`, Ideology-gated at `:44` |
| `XML error` / `Could not find type named Inhabited.` in a `WorldObjectDef` or `CharacterDef` | 🔴 def↔class binding. Expected first-run failure #3 |
| ⭐ **expected-PRESENT:** the `Inhabited` debug actions appear in the dev menu | ✅ absence of errors is necessary and NOT sufficient — a mod that loads and does nothing logs nothing. This is the positive sighting that makes a clean log mean something |

## §4 CORRECTION Results — filled 2026-08-20 from the 578-mod load, log EXITED

| prediction | result |
|---|---|
| no `Inhabited` line at all ⇒ the mod did not load | ⭐ **DID NOT FIRE.** The log carries exactly one: `[Inhabited] ready: 2 patches, 269 characters, 0 places, 0 casts.` |
| `Could not load reference to` naming an `Inhabited.*` type | ✅ none |
| `Harmony` exception on `Patch_BeggarsFromPool` | ✅ none — **both patches bound.** This was the one I called likeliest to bite, because the design doc named a class that does not exist; BUILD had already corrected it to `QuestNode_Root_Beggars` |
| `Could not find type named Inhabited.` in a def | ✅ none |
| ⭐ expected-PRESENT: the mod announces itself | ✅ **satisfied by the `ready:` line, and this is the finding that matters.** `269 characters` means every authored person parsed into a def. `0 places, 0 casts` is correct for a first run — nothing has been placed yet |

⇒ **`Inhabited` loaded clean on its first ever run, on a 578-mod list.** The architecture
soak (`ROSTER_SOAK_100_DAYS_1`) is now the only thing between it and being real.

### 🔴 Two RED lines in `harvest_log.py`, and only one of them is new

| check | count | verdict |
|---|---|---|
| texture path failures | **2** vs baseline 0 | ⚠️ **NOT NEW.** These are the GRiNDTerra juvenile typos already filed as `GRIMTERRA_TEXPATH_TYPOS_1`, whose own criteria say *"Baseline today is 2"*. The harvester's baseline is the stale number, not the item's |
| stale saved data (Scribe) | **8** vs baseline 0 | 3 × `guy762_*` GeneDef + 5 × `RG_*` ThingDef (Owlbeast, Boilberries) |

🔑 **The Scribe 8 is NOT ours, and I nearly filed it as though it were.** The three gene
failures sit directly under three `Loaded file (Xenotype)` lines, which reads exactly like our
Jawa xenotype dropping genes — the failure `the-shipping-xenotype-drops-four-of-our-own-genes-7e31aa`
predicts and warns is *invisible to disk evidence*. Measured instead of assumed:
**`pokean.xtp` contains all three `guy762_*` gene names; `MandrakeJawa.xtp` contains ZERO.**
Our file's four `guy762` hits are **packageIds in its `<modIds>` provenance block**
(`guy762.kotordroids`, `.kotorweapons`, `.mm.kotorcore`, `.starwarsxenotypes`) — dotted, not
underscored, and not gene references at all.
⚠️ **What this does NOT prove:** only three `.xtp` files loaded out of six in the folder, so a
clean log does not establish that ours was one of them. `7e31aa` stays open on its own terms.

---

## §4 — the 2026-08-20 MORNING load: W9 world import + `Inhabited`'s first load

**Written 2026-08-20 07:5x, game DOWN, BEFORE launch.** Mod list `578` active
(577 + `mandrake.inhabited`, enabled by the owner in RimSort at 07:42:46).
**Results table blank = this block is UNFINISHED. Do not launch a second load against it.**

```bash
LOG="/mnt/c/Users/Mandrake/AppData/LocalLow/Ludeon Studios/RimWorld by Ludeon Studios/Player.log"
```

### What is riding, and the attribution risk

| change | kind | can it steal another item's blame? |
|---|---|---|
| **`Inhabited`** — new mod: 1 new assembly, 4 def files, 269 `CharacterDef`s, 2 Harmony patches | 🔴 **new C# assembly** | **No, and here is why it is allowed to ride.** Its two Harmony targets are `Game.DeinitAndRemoveMap` and `QuestGen_Pawns.GeneratePawn` — neither is touched by the world-import work, and neither runs at all before a map is destroyed or a beggars quest is generated. It adds defs and patches nothing of anyone else's. Every failure mode below names `Inhabited` or `mandrake.inhabited` explicitly |
| **W9 world import**, 7 stages, `MORNING_RELOAD_PLAN_1` | bridge calls, post-load | no |
| `Jawa_Patches/About/About.xml` prose | text only | no — **not verifiable in a log and no signature is claimed for it** |
| def dump re-take (`dump_request.txt` = `all`, armed) | startup artefact | no |

🔴 **THE DEF DUMP RE-TAKE IS NOW MANDATORY, NOT OPTIONAL.** The 2026-08-20 ruling that
the dump is definitive holds *"until a mod is added or removed"*. Enabling `Inhabited`
took the list 577 → 578, so **the ratification has lapsed and the current dump is
stale by exactly one mod.** The marker is armed; reach the main menu and it re-takes
(~27 s, ~1.2 GB). ⚠️ **The marker is NOT consumed — delete it afterwards** or every
future load pays that again.

### Expected PRESENT — the strings that prove it loaded

⚠️ Absence of an error is NOT proof of success. `Inhabited` does nothing visible on a
good load, so it now says so itself.

| # | expected string | baseline | what it means |
|---|---|---|---|
| P1 | `[Inhabited] ready: N patches, 269 characters, 0 places, 0 casts.` | **never seen — first load** | ⭐ **THE ONE LINE THAT SETTLES THE WHOLE MOD.** `269 characters` is the number to read: it proves the assembly loaded, the def type resolved, and all eleven `CastRoster_*.xml` parsed. `0 places, 0 casts` is **CORRECT and expected** — no `InhabitedPlaceDef`/`InhabitedCastDef` instance exists yet; that content is blocked on DECIDE |
| P2 | `[RimDefDump]` | seen every armed load | the dump re-take ran. Then check the manifest reports **578** |

```bash
grep -n "\[Inhabited\] ready" "$LOG"
```

**Read P1's counts, do not just check the line exists.** `269 characters` is a pass;
anything less means def files failed to parse and the exact count says how many.

### Expected ABSENT — one signature per way this can fail

| # | signature | baseline | what it means if present |
|---|---|---|---|
| F1 | `Inhabited` + `ReflectionTypeLoadException` \| `Could not load assembly` | 0 | the DLL did not load at all. Nothing else below is meaningful. **Check first** |
| F2 | `Could not find Verse.DutyDef named Inhabited_Resident` \| `DefOfHelper` | 0 | `Defs/DutyDefs/Duties_Inhabited.xml` did not load. Deliberate tripwire: `InhabitedDefOf` names that duty precisely so a def file that fails to parse is loud instead of producing a silently duty-less mod |
| F3 | `Could not find type named Inhabited.CharacterDef` \| `Inhabited.WorldObject_Inhabited` \| `Inhabited.GenStep_InhabitedCast` \| `Inhabited.JobGiver_SleepAtNight` | 0 | a def names a class the assembly does not expose. Means F1 in disguise, or a namespace typo |
| F4 | `Config error in Inhabited_` | 0 | a `CharacterDef` failed its own `ConfigErrors`. ⚠️ **The most likely single failure in this block**, because all 807 traits were resolved against a **577**-mod dump and the live set is now 578. The defName in the message names the person |
| F5 | `mandrake.inhabited` near `Exception` \| `HarmonyException` \| `patching` | 0 | a Harmony target moved. ⚠️ **Should be impossible** — both targets are bound to a delegate of the same signature at compile time, so a moved target fails the BUILD. If this fires, that proof was wrong and it is the more interesting finding |
| F6 | `CastRoster_` near `XML error` \| `Exception loading` | 0 | a generated roster file is malformed. All eleven parse under Python; this would mean RimWorld's parser disagrees |
| F7 | `Could not resolve cross-reference` naming a `TraitDef` | 🔴 **25**, not 33 — see the correction below | a trait in a roster does not exist in the live set. **25 is the number to beat, not zero** |

🔴 **CORRECTION, made before launch and before any log existed: the F7 baseline was
written as 33 and 33 was two errors added together.** Re-counted on the archived
`Player.2026-08-20_0258_preload.log`:

| string | count | what it actually is |
|---|---|---|
| `Could not resolve cross-reference` | **25** | the DEF LOADER, against the live mod set |
| `Could not load reference to` | **8** | **Scribe** — the SAVE holds a name no def provides. No mod change fixes it |

They have different causes and different remedies, and adding them produced a
baseline that would have scored a real regression as a pass. F7 tracks the **25**.
The 8 belong to the save, not to the load set, and are not Inhabited's business.

```bash
grep -nE "Inhabited|mandrake\.inhabited" "$LOG" | grep -viE "\[Inhabited\] ready" | head -40
grep -c "Could not resolve cross-reference" "$LOG"     # baseline 33
```

### Results — FILL THIS IN AFTER THE LOAD. Blank means unfinished.

✅ **ALL NINE ROWS PASSED — 2026-08-20 08:08, scored by
`python3 src/RimMandrake/Utils/score_inhabited_load.py`, not by eye.**

| # | outcome | evidence |
|---|---|---|
| P1 | ✅ present | line 5060: `[Inhabited] ready: 2 patches, 269 characters, 0 places, 0 casts.` — **269 is the pass**; 2 patches means both Harmony targets bound; 0 places / 0 casts is correct, that content is blocked on DECIDE |
| P2 | ✅ present | line 5056 `[RimDefDump] starting`, line 5059 `done in 16397 ms`. Manifest reports **modCount 578**, fingerprint `5ef6eec3daf6c325`, and `refresh.py` now calls the dump **current** |
| F1 | ✅ clean | no `ReflectionTypeLoadException` / `Could not load assembly` near Inhabited |
| F2 | ✅ clean | the `Inhabited_Resident` DefOf tripwire did not fire |
| F3 | ✅ clean | no `Could not find type named Inhabited.*` |
| F4 | ✅ clean | no `Config error in Inhabited_`. ⭐ **And independently re-proven, not just absent:** `cast_to_xml.py` re-run against the NEW 578-mod dump reports *"every trait and degree resolved"* — all 807 |
| F5 | ✅ clean | no Harmony exception naming `mandrake.inhabited`. The compile-time delegate proof held |
| F6 | ✅ clean | no `CastRoster_*` parse error |
| F7 | ✅ = baseline | **25** `Could not resolve cross-reference`, **0** naming a `TraitDef` |

⭐ **THE STRONGEST SINGLE PIECE OF EVIDENCE IS NOT IN THE LOG AT ALL.** The engine's own
def dump now carries `CharacterDef.json` with **269 defs**, attributed to `Inhabited
(local)` — plus empty `InhabitedPlaceDef.json` and `InhabitedCastDef.json`, which is the
correct reading of "the mechanism is in and the content is not". That is RimWorld
reporting our def types back to us, which no log line could establish on its own.

---

## §5 — the 2026-08-22 EVENING load. Written 21:5x, BEFORE the game started.

**What is riding it.** Two assemblies and a full 578-mod stack:

| assembly | deployed | what is new since it last ran |
|---|---|---|
| `JawaBench.BridgeTools.dll` | md5 `1b24c77e`, 2026-08-22, `--gm` | **121 `jawa/` tools** (was 106 at last publish). New: `jawa/world_cache_audit` (CHECK, `fe4c081c`+`63e63907`), `jawa/vehicle_components` (peer, `9e79e3d2`) |
| `Inhabited` | in sync, 18 files | the cast roster fix — `cast_to_xml.py` no longer emits the `<li><skill>` shape that discarded 101 defs |

🔑 **These two fail in completely different places**, which is what makes batching them
affordable: the companion fails at bridge startup (or a tool is simply absent from
`tools/list`), `Inhabited` fails at def load or at its own ready line. **Neither can steal
the other's blame.**

### Expected PRESENT — absence of these IS the failure

| # | string | value that passes |
|---|---|---|
| P1 | `[Inhabited] ready:` | 🔴 **294 characters.** 193 means the cast fix did not reach the game and NOTHING downstream of it counts |
| P2 | `[JawaBench] ready:` | 🔴 **121 tools.** 120 means `vehicle_components` is missing; 119 means the whole 2026-08-22 build did not land; 106 means the deploy never happened |
| P3 | `[RimDefDump] starting` … `done in` | only if the dump is armed — see the launch note |

### Expected ABSENT — any hit is a failure

| # | grep | baseline |
|---|---|---|
| F1 | `Exception loading def from file CastRoster_` | **0** |
| F2 | `SkillDef named li` | **0** — this was 101 before the fix; it is the single most diagnostic string on the whole load |
| F3 | `ReflectionTypeLoadException` / `Could not load assembly` near `JawaBench` | 0 |
| F4 | `Could not find type named JawaBench.` | 0 |
| F5 | Harmony exception naming `mandrake.inhabited` | 0 |
| F6 | `Could not resolve cross-reference` | ⚠️ **baseline 25**, not 0. Above 25 is a regression; at 25 is clean |

### 🪤 The trap specific to THIS load

⚠️ **`jawa/world_cache_audit` has NEVER RUN.** It resolves four private `Tile` fields by
reflection at static-init time. **If RimWorld renamed any of them, the tool returns a
REFUSAL naming which field failed — it does NOT return zero divergences.** That refusal is
a PASS for the load (the guard works) and a FAIL for the tool. Distinguish them; do not
score a refusal as a broken load.

⚠️ **A tool missing from `tools/list` is NOT the same as the companion failing to load.**
P2 separates them: a wrong count with a present ready line means one tool; an absent ready
line means the assembly.

### Results — SCORED 2026-08-22 23:0x by CHECK, one Python pass over all 1,058,800 log lines.

**Seven of eight pass. F6 is a real and large regression, and it has a named cause.**

| # | outcome | evidence |
|---|---|---|
| P1 | ✅ **PASS** | L1058179 `[Inhabited] ready: 2 patches, 294 characters, 0 places, 0 casts.` — **294**, the passing value. The cast fix reached the game; 193 would have voided everything downstream |
| P2 | ✅ **PASS** | L1058800 `[JawaBench] ready: 121 tools, build d49eaf42545b` — **121**, exactly the value under test. ⭐ Independently corroborated off the LIVE bridge, not the log: `tools/list` returns **246 tools, 121 of them `jawa/`** |
| F1 | ✅ clean | 0 `Exception loading def from file CastRoster_` |
| F2 | ✅ clean | 0 `SkillDef named li` — the string that was **101** before the fix. The single most diagnostic line on this load, and it is gone |
| F3 | ✅ clean | 0 `ReflectionTypeLoadException`, 0 `Could not load assembly` |
| F4 | ✅ clean | 0 `Could not find type named JawaBench.` |
| F5 | ✅ clean | 0 `mandrake.inhabited` |
| F6 | 🔴 **FAIL — 3,037 against a baseline of 25** | and the cause is measured, not guessed: **the desert and ice BiomeDefs do not exist in the running game.** See the block below |

⚠️ **P3 also fired, unasked:** L1058161 `[RimDefDump] starting, mode=all,
capture=2026-08-23T05-05-29Z`. The dump WAS armed; `dump_request.txt` lives inside
`DefDump\`, not beside it, and is still unconsumed — it will fire again next load.

🔑 **A correction to this section's own instrument.** §5 says *"an absent ready line
means the assembly [failed]"*. Both ready lines are the **last two lines of the file** and
were not yet written while the game was still loading, so an absent line during a load
means only that the load has not finished. **Score P1/P2 off `tools/list` and the def dump
when the answer is needed early**; the log lines arrive last.

### 🔴 F6 — what the 3,037 actually are, and why it blocks the planet

**MEASURED from the LIVE game via `jawa/get_defs`, calibrated against known-good defs
(`ThingDef/Steel` resolves, `BiomeDef/Tundra` resolves, so the instrument works):**

| present in the running game | ABSENT from the running game |
|---|---|
| `Ocean` `Lake` `BorealForest` `Tundra` `TemperateForest` `TropicalRainforest` `ColdBog` `Underground` | `Desert` `ExtremeDesert` `AridShrubland` `IceSheet` `SeaIce` `Wasteland` `Volcano` `LavaField` `Scarlands` `PoisonForest` `HorrorWastes` — plus every `AB_*`, `ZBiome_*` and `BMT_*` biome the map uses |

Every one of those absences is a Core or active-mod biome, and the 3,037 cross-reference
failures are overwhelmingly `No RimWorld.BiomeDef named <one of them> found to give to
RimWorld.AnimalBiomeRecord` — mods' animal biome records dangling on biomes that are gone.
99% of the log's bulk is the "Possible Matches:" candidate dump attached to each.

🔴 **This blocks the planet stamp, and that is the point of recording it here.**
`world\ASHKARR_WORLDMAP_tiles.csv` names **28 distinct biomes over 21,872 tiles**, and
**26 of them — 20,737 tiles, 94.8% of Ash'karr — do not resolve in the running game.**
Stamping would put almost the whole planet on biomes that do not exist, and the failure
is silent. The read-only re-check is:

```
python.exe D:\Luke\dev\Rimworld\src\RimMandrake\bridgetools\check_map_biomes_live.py
```

⚠️ **Cherry Picker is NOT the cause and its own biome cuts are not landing.** Its
`<keys>` removal list names `BorealForest`, `Tundra`, `TemperateForest`, `ColdBog`,
`Savanna`, `Wetland` and 20 more — and every one of those **survived**. It does not name
`Desert`, `AridShrubland`, `IceSheet` or `SeaIce` at all. The inversion is unexplained and
is itself a finding.

⚠️ **`Could not load reference to` is 0**, so nothing here is save-side. This is the
def loader against the live mod set, and a mod-list change is what would move it.

---

## §6 — the BIOME RESTORATION load. Written 2026-08-22 23:2x, BEFORE the game restarted.

**What is riding it.** One XML file, `Jawa_Patches/Patches/BiomeCast_Ashkarr.xml`,
regenerated by a fixed `design/Jawa/fauna/gen_cast_patch.py` and deployed (`0efc38ba`,
`VERIFIED in sync`). 26 `PatchOperationConditional` → `PatchOperationReplace` operations,
744 emitted records, 2 deliberately skipped.

🔑 **The change is the record SHAPE and nothing else.** `<li><animal>X</animal>
<commonality>N</commonality></li>` became `<X>N</X>`. Same 26 biomes, same animals, same
commonalities, same xpaths, same MayRequire guards.

### Expected PRESENT — absence of these IS the failure

| # | string / probe | value that passes |
|---|---|---|
| P1 | a def-dump capture's `BiomeDef.json` | 🔴 **80 records.** 54 means the fix did not reach the game — check the deploy before anything else |
| P2 | `check_map_biomes_live.py` | 🔴 **`every biome the map names exists in the running game`.** Any MISSING line names a biome still being discarded |
| P3 | `[Inhabited] ready:` | **294 characters**, unchanged — this load must not regress §5's pass |
| P4 | `[JawaBench] ready:` | **121 tools**, unchanged |

### Expected ABSENT — any hit is a failure

| # | grep | baseline |
|---|---|---|
| F1 | `Exception loading def from file Biomes_` | 🔴 **0.** It was **22**. This is the single most diagnostic string on this load — it is the exception that discarded the biomes |
| F2 | `BiomeAnimalRecord.LoadDataFromXmlCustom` | 🔴 **0.** It was 1 (one stack, 22 throws) |
| F3 | `There are 54 defs of this type loaded` | 🔴 **0.** It was **26**. ⚠️ A hit with a *different* number is not a pass — read the number; it says how many biomes survived |
| F4 | `Could not resolve cross-reference` | ⚠️ **back to ~25**, from **3,037**. Anything in the hundreds means biomes are still being dropped |
| F5 | `Could not resolve cross-reference` naming `SWPotF_RaceDef_ysalamir` or `GiantAnt_Race` | **0** — these two are ThingDefs, not PawnKindDefs, and are now skipped rather than emitted. A hit means the skip did not work |

### 🪤 The traps specific to THIS load

⚠️ **A patch that matches nothing logs nothing.** All 26 operations are
`PatchOperationConditional`, which returns true on no match *by design* — so if the
biomes are still absent for some other reason, this patch goes quiet and F1–F3 read
clean while P1/P2 fail. 🔑 **Score P1 and P2 first; the ABSENT table cannot detect this
class of failure on its own.**

⚠️ **`Ikee_Rename.xml` patches `Wasteland`, `ExtremeDesert` and `ZBiome_DesertOasis`
too**, in the correct form, and those biomes still died — because both patches land in
the same def and one malformed record discards it. So a surviving Ikee entry is **not**
independent evidence; there is no A/B here.

⚠️ 🪤 **The dump is still armed.** `DefDump\dump_request.txt` reads `all` and is not
consumed, so this load pays ~27 s and ~1.2 GB again. That is *wanted* this once — P1 is
read straight off the new capture — but delete it afterwards.

### Results — FILL THIS IN AFTER THE LOAD. Blank means unfinished.

| # | outcome | evidence |
|---|---|---|
| P1 | | |
| P2 | | |
| P3 | | |
| P4 | | |
| F1 | | |
| F2 | | |
| F3 | | |
| F4 | | |
| F5 | | |
