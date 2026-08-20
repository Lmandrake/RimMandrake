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

| block | load event | date | status |
|---|---|---|---|
| **§1** | three-assemblies batch, reload of the (now deleted) campaign — quicktest map | started **2026-08-13 17:30:59**, harvested 18:11, game up to ~21:10 | ✅ **CLOSED 2026-08-13** — Results filled, incl. two rows honestly marked NOT COLLECTED |
| **§2** | 🔴 **NEW WORLD GENERATION** — v1 rows 2 + 7 in one irreversible run, plus Anomaly-to-zero | written **2026-08-13**, game DOWN. **Load not yet run.** | ⬜ **OPEN** — signatures written, Results blank |
| **§3** | the **2026-08-15 deploy-window load** — two assemblies + one XML/PNG mod + a mod-list change, on a **quicktest** map. ⛔ **not worldgen** | written **2026-08-15 ~15:50**, game DOWN, before launch | ⬜ **OPEN** — signatures written, Results blank |

🔴 **§2 and §3 are both open and they are DIFFERENT EVENTS. Do not fill §2's Results
from this load's log.** §2 is the irreversible worldgen run, which is the owner's and
is not scheduled. This load runs against **§3** only. §2's S1–S8 are not re-booked
here; where §3 needs the same check it restates it, and **§3's T4 REVERSES one of
§2's S8 rows** — read T4, do not carry S8 forward.

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
`ImperialDesertDirectorate.xml` puts its `OuterRim_ImpStorm*` pawn kinds into vanilla
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
| 🔴 **CORRECTED B23.** Vanilla **`Empire`** renders as **"The Galactic Empire"** with an **Emperor** | R15/R11 landed. The Empire moved onto the VANILLA Royalty vessel; `label` "The Galactic Empire", `fixedName` "Galactic Empire", `leaderTitle` "Emperor" | reads **"shattered empire"** with a **"high stellarch"** → `ImperialDesertDirectorate.xml` did not land. Record and carry on; do NOT abort |
| ~~⚠️ **`OuterRim_GalacticEmpire` now reads "Galactic Empire" and THAT IS CORRECT**~~ ⛔ **DEAD ROW 2026-08-20 — do not check it at all.** The def is not the vessel and not in the design; whatever label it shows is not a signal. See `infrastructure/state/OWNER_DECISIONS.md`. Original text kept below. | **This block used to demand "Imperial Desert Directorate" here, and that is now the FAILING string.** B40 re-pointed the file off this def onto vanilla `Empire`; nothing patches `OuterRim_GalacticEmpire` any more, so it shows its own shipped label. **Do not read this as a deploy miss and do not regenerate.** | reads "Imperial Desert Directorate" → an OLD `Jawa_Patches` is deployed; the current one has not landed |
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
| ~~S4~~ | ~~`OuterRim_GalacticEmpire` label reads "Imperial Desert Directorate" (observation, not a gate)~~ ⛔ **DEAD 2026-08-20 — the vessel is vanilla `Empire`; nothing patches this def. Do not record it.** See OWNER_DECISIONS.md. | — | — |
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

# §3 — LOAD 2026-08-15, the deploy window. ⬜ OPEN

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
