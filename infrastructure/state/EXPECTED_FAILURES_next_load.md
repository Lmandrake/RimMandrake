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
Live gate: `jawa/list_factions` returns `OuterRim_GalacticEmpire`,
`jawa/get_def PawnKindDef OuterRim_ImpStormtrooper` resolves, **and a settlement
actually exists on the world map** — `OuterRim_RebelAlliance` was configured,
present, and never generated, so "the faction resolves" ≠ "it is in the world".

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
| **A3 GalacticEmpire** | ✅ **PASS.** Banner present at **line 716**, exactly one hit, version reads **`1.6.9308`** as predicted. Negative grep clean: no `HarmonyException`, no `Could not find type named TabulaRasa.*`, no `OuterRim_*` cross-reference failure. The three `TabulaRasa` hits (5269, 5383, 6832) are Harmony patch-listing lines for `Neronix17.TabulaRasa.RimWorld` — the dependency **present and patching**, the opposite of the failure shape. | ⬜ **NOT COLLECTED on this load.** | 🟨 **Log half PASS, live gate not collected.** v1 row 1 closed earlier the same day (`CLOSED.md:12`, hash `fad8bab`) against the world that has since been deleted; nothing ties a faction read to the 17:30 session. ⚙️ **And it could not have counted anyway:** the session ran on a quicktest, and a quicktest never visits Configure Factions (OPS's trap, `2d1685e`), so a faction census there says nothing about the campaign. **A3's live half is re-booked into §2 S3.** |

### §1 close-out notes worth carrying

- **Two of three live gates were never run.** The log greps are cheap and all three
  passed; the gates that actually decide A1 and A3 were skipped. That is the
  recurring shape — *a clean log read as a result.*
- ⚠️ **`CLOSED.md:11` and `:12` cite `7bd8b60` and `fad8bab`, and neither hash
  resolves in this working tree.** Not mine to fix — **filed for PROJECT**, who
  owns `CLOSED.md`. Both are the sole citation for a closed v1 claim.

---

# §2 — NEXT LOAD: **NEW WORLD GENERATION**. ⬜ OPEN

**Event:** a **new world generated from the main menu** — not a save load. This is
v1 **rows 2 and 7**, which `V1_SCOPE.md` establishes are **one irreversible event**,
plus the owner's **Anomaly-to-zero** ruling ticked on the same screens.
**Written 2026-08-13, game DOWN, before the load.**

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

## S1 — the 21-tool companion, **first load of this build**

🔴 **The only assembly that changed, so it is the only genuinely new assembly
risk this load.**

**Gate:** `python.exe src/RimMandrake/bridgetools/prove_new_tools.py` → read line 0,
the deploy census.

| census reads | meaning |
|---|---|
| **21** | ✅ the 22:23 build is live. **S1 PASSES.** |
| 20 | pre-`order_pawn` build — the 22:23 deploy did not take |
| 17 | the §1 build loaded — deploy did not take |
| 7 / 0 | old seven / bundle never loaded at all |

🔴 **§1's "the FAIL is the pass" inversion is DEAD — do not carry it forward.**
`ALL_TOOLS` was corrected at `68a0a30` (16:38) and now holds **21** names
(`prove_new_tools.py:93-102`), matching the deployed DLL's string heap exactly.
**A correct deploy now prints PASS. A FAIL now means a real miss.**

Cheaper second positive: `rimbridge/get_bridge_status` →
`companions.diagnostics` — want `companionErrorCount = 0`, `companionCount` non-zero.

**Log negative — host is unchanged, so §1's grep stands verbatim:**

```bash
grep -nE "\[RimBridge\] (Failed to (load|scan|inspect|prepare|register)|Loader exception|Skipping companion|Could not resolve global BridgeTools|Ignoring companion-local SDK|STARTUP_INIT_FAILURE|Failed to start server)|Companion references RimBridgeServer\.Sdk" "$LOG"
```
**Pass:** zero lines **and** census 21. **Fail:** any line, or census ≠ 21.

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
— RATIFIED by VISION: **20 untick** (12 ordinary count rows in its §1, 8 hidden
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
Factions and shows all 54 factions by default — OPS's trap, `2d1685e`, which
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
| `OuterRim_GalacticEmpire` renders as **"Imperial Desert Galactic Empire"** | the `Jawa_Patches` label patch is live | reads **"Galactic Empire"** → 🔴 **STOP before generating.** The Jawa_Patches deploy did not land — check `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches` |
| `OuterRim_RebelAlliance` is **ABSENT** from the page | `RebelAlliance_Suppress.xml` set `maxConfigurableAtWorldCreation` to 0 — **absence is the DESIRED outcome, not a defect** | **present and settable** → the patch did not land; file it. **Present but locked at 0** → harmless, worth a line. **Do not revert the patch at the screen.** |

**Also record, as an observation with no pass/fail:** vanilla `Empire`'s name is
**generated**, so the page will probably not say "Fallen Dominion". Screenshot it —
per the checklist, that string is the only record of it.

---

## S5 — Anomaly at zero (owner's ruling, same run)

**Setting:** the Anomaly playstyle. defNames **VERIFIED** in `Assembly-CSharp.dll`:
`AnomalyFrequency_None` · `_VeryRare` · `_Rare` · `_Balanced` · `_Intense` ·
`_Overwhelming`. **Want `AnomalyFrequency_None`.** The DLC stays **enabled** — only
the storyline is off; its creatures and abilities remain ours to reskin.

**Evidence command:**

```
rimworld/save_game        # then grep the .rws on disk:
grep -o "anomalyPlaystyleDef>[^<]*" <the .rws>
```

`anomalyPlaystyleDef` is the serialised field name, **verified in
`Assembly-CSharp.dll`**. **Pass:** it reads `AnomalyFrequency_None`. **Fail:**
anything else.

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
is now S3's KEEP check on `OuterRim_GalacticEmpire`.

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

## §2 execution order

**Before the irreversible click:**
1. **S4** — both label checks on the Configure Factions page. A miss here means
   **stop and fix the deploy**, and it is the only point where that is still cheap.
2. **S3, the act** — drive the 20 unticks and confirm the 6 keeps, from
   `WORLDGEN_FACTION_CHECKLIST.md`. Tick **Anomaly → `AnomalyFrequency_None`** on
   the same screens (S5).

**Immediately after the world exists:**
3. **S2** — the worldgen grep. Want zero lines. Screenshot the world map (row 7's gate).
4. **S3, the evidence** — `jawa/list_factions`, diff against the checklist.
5. **S1** — `prove_new_tools.py`; census must read **21**, and it should print PASS.
6. **S5** — `rimworld/save_game`, then grep the `.rws` for `anomalyPlaystyleDef`.

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
| S1 | companion census = 21 | | |
| S1 | `[RimBridge]` failure grep = 0 | | |
| S2 | worldgen error grep = 0 | | |
| S2 | world map screenshot (row 7 gate) | | |
| S3 | `jawa/list_factions` vs checklist — 20 CUT absent | | |
| S3 | `jawa/list_factions` vs checklist — 6 KEEP present | | |
| S3 | downstream over-exclusion grep = 0 (at session end) | | |
| S4 | Empire label reads "Imperial Desert Galactic Empire" | | |
| S4 | `OuterRim_RebelAlliance` absent from the page | | |
| S5 | `.rws` `anomalyPlaystyleDef` = `AnomalyFrequency_None` | | |
| S6 | A2 / A3 log greps unchanged | | |
