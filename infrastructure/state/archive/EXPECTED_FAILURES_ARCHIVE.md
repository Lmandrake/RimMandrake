# EXPECTED_FAILURES — ARCHIVE of closed load blocks

Moved out of `infrastructure/state/EXPECTED_FAILURES_next_load.md` on 2026-08-25 to bring
that file back inside its 1800-line budget (it was 2133). ⛔ **Nothing was deleted.** These
three blocks are all headed CLOSED and their results are filled in below; they are kept
verbatim because a signature written before a load and the result measured after it are
evidence, and evidence is not deleted for space.

⚠️ A block here is a DUPLICATE of a ledger item; when the two disagree, the ledger is right.

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
