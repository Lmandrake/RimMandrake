# infrastructure/state/queue/OPS.md

_OPS's queue (the seat formerly called WORLD). **You own this file — write freely,
nobody blocks on it.** Others file at you by appending here. Doctrine and tagging
rules live in `agents_def.md`; the v1/v2 line lives in `V1_SCOPE.md`._

⚠️ **`[WORLD]`-tagged items were split, not renamed.** Anything about *what the
world should contain* went to `infrastructure/state/queue/VISION.md`. What is here is live-stack work:
does it function, what broke, what is the smallest test.

---
## ⭐ v1 — YOUR ONLY v1 ROW, and it needs no game

**Row 2, Faction Control suppression** (`V1_SCOPE.md` burn-down). Sitting at **0**
and **closable offline today** — pure config, no XML, no load. Suppress the
factions that break the fiction (medieval, insectoid, non-SW).

`Config/Mod_2882785581_Controller.xml`: 32 faction entries, all bare, and
`masterDensity` **0** means *untouched*, not *configured* — the mechanism has never
been used. Verification rides the next live session with the other thin rows.

### ✅ RULED by the owner 2026-08-13: *"We are keeping no savegames at this time."*

**`OWNER_DECISIONS.md` #11 is ANSWERED — the existing world is disposable, so v1
regenerates.** Consequences, in order:

1. **Row 2 is ALIVE again, but it is not offline config work.** There is no
   suppression field (§5b) — faction exclusion is done by **unticking factions on
   vanilla's Configure Factions page at world creation**, which Faction Control
   unlocks and extends. So row 2 moves from `V1_SCOPE.md`'s
   🟢 *"NO — closable offline today"* column to **a worldgen-time checklist**,
   executed once, during the run that makes the new world. ⚠️ **`V1_SCOPE.md`
   row 2 still says it needs no game and that is now wrong** — PROJECT's file,
   filed to them, not edited by me.
2. **Row 7 ("ordinary worldgen", BRIDGE, *verify only*) is also wrong now** —
   worldgen is a thing we will DO, not observe. Filed to BRIDGE.
3. **The savegame findings below are now historical**, not blockers. Keep them:
   they are the measured proof that the *current* mod set produces a
   fiction-breaking world, which is exactly the list of boxes to untick.
4. **My six pawn states on the owner's colony stop mattering** (four prisoners,
   two slaves — see `AGENT_OPS_state.md`). Nothing to undo.
5. 🔴 **THE SAVES ARE GONE.** Owner ordered it the same session — *"Delete all
   old savegames and screenshots, yes."* **27 saves, 124 agent screenshots and
   54 owner F10 captures deleted, 986 MB, irreversible.** The campaign went with
   them. ⚠️ **The measurements below were taken BEFORE the deletion and are now
   the only surviving record — `New Arrivals2.rws` cannot be re-read.** Do not
   file a bug when `src/RimMandrake/Utils/Savegame_*.py` finds nothing to open.

### The proposed exclusion list — PLAYER-ZERO PROPOSAL, VISION ratifies

**I am player zero here, not the designer: this is evidence in, decision out.**
Derived from the 53 faction defs in `New Arrivals2.rws` and the 41 in Faction
Control's config. Settlement counts are what the *last* world produced, i.e. how
loud each one was on the map.

**Untick — breaks the Star Wars fiction (fantasy / Norse / medieval):**
`BS_Muspelheim` (6) · `BS_Niflheim` (4) · `BS_LittlePeople` (4) ·
`BS_Dvergr_Medieval_Union` (3) · `BS_OgreFaction` (1) · `BS_ZombieFaction` ·
`KAR_OrcClan` (2) · `DA_Troll`

**Untick — wrong franchise:** `ABYautjaBadBloodClan` (5) · `ABYautjaBerserkClan`
(4) · `ABYautjaClan` (4) · `ABYautjaModderClan` (1) — four Predator clans, 14
settlements between them, the single largest non-SW presence on the map.

**Untick — horror/bug factions with no SW reading:** `Horrors` (5) · `Insect`
(5 + 18 infestation objects) · `HoraxCult` · `AA_BlackHive` ·
`BMT_PustuleHornets` · `GiantAnt_Faction` · `GR_RoamingMonstrosities` ·
`MO_AbominationFaction` · `CASacrilegHunters` (2)

**KEEP — these are Star Wars and must survive the cull:**
`OuterRim_GalacticEmpire` (1 — row 1's Directorate vessel) ·
`OuterRim_BinaryStarRaiders` (5) · `OuterRim_MoistureFarmers` (3) ·
`OuterRim_RebelAlliance` · `JDSCIS_CIS_Faction` ·
`guy762_KotORFaction_RogueDroids`

~~🔴 **`OuterRim_RebelAlliance` was configured but DID NOT GENERATE in the last
world** — it is in Faction Control's 41 and absent from the save's 53. **Watch
for it explicitly at the next worldgen**; if it fails to appear again that is a
real defect**~~

❌ **RETRACTED 2026-08-13. Not a defect — WE suppressed it, on purpose.**
`src/Jawa/Jawa_Patches/Patches/RebelAlliance_Suppress.xml` (W6, 2026-08-12) sets
`requiredCountAtGameStart` 0, `settlementGenerationWeight` 0, `canMakeRandomly`
false **and `maxConfigurableAtWorldCreation` 0** — verified by reading the patch,
all four values present. The last one removes it from the Configure Factions page
**entirely**, so it cannot even be ticked back on at the screen.

⚠️ **Two documents still carry the wrong version and I am not the one to fix
them:** `infrastructure/state/queue/BRIDGE.md` calls it "a fiction problem, not a
config problem", and the KEEP list below still names it. **Filed to VISION** —
keep-vs-suppress is a design ruling, not mine.

**The generalisable lesson, and it is the reason this got as far as it did:** an
absence was read as a failure without first checking whether *we* had caused it.
Our own deployed patches are part of the environment. Before calling any missing
thing a defect, grep `Jawa_Patches/` for its defName.

⚠️ **Two cautions before anyone executes this.** First, **hidden factions
(`Insect`, `Horrors`, `Mechanoid`, `Entities`) are not ordinary rows** — they
appear as *"Allow the hidden X faction?"* checkboxes, and Faction Control's own
tooltip warns that removing mechanoids can still leave them in ancient danger
rooms and quest objectives. Second, **the eleven settlement-less modded factions
cannot be unticked if they do not appear on the page at all** — for those the
lever is the mod list, with the game down, and that is a separate proposition.

### Measured evidence (historical — the world it describes is being discarded)

**1. The mechanism is worldgen-only.** `strings` over
`C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2882785581\1.6\Assemblies\FactionControl.dll`
shows the Harmony patch classes `Patch_FactionGenerator_GenerateFactionsIntoWorld`
and `Patch_FactionGenerator_GenerateFactionsIntoWorldLayer`, plus
`WorldGenerator_GenerateWithoutWorldData`, `WorldGenerator_GenerateFromScribe`,
`TileFinder_IsValidTileForNewSettlement`, `WorldObjectsHolder_Add`. **Faction
existence is decided at world creation.** Setting a density to 0 cannot remove a
faction already baked into a save. ⚠️ *`GenerateFromScribe` is patched too and I
did not establish what it does — that is the one hole in this claim.*

**2. The world already exists and already holds the offenders.**
`New Arrivals2.rws` (43.7 MB, saved 09:46): **53 faction defs** in
`<factionManager><allFactions>`, **102 `Settlement` + 5 `SpaceSettlement`**
world objects, **34 factions own world objects**.

| fiction-breaker | settlements |
|---|---|
| `BS_Muspelheim` · `BS_Niflheim` · `BS_LittlePeople` · `BS_Dvergr_Medieval_Union` · `BS_OgreFaction` | 6 · 4 · 4 · 3 · 1 |
| `ABYautjaBadBloodClan` · `ABYautjaBerserkClan` · `ABYautjaClan` · `ABYautjaModderClan` | 5 · 4 · 4 · 1 |
| `Horrors` · `KAR_OrcClan` · `CASacrilegHunters` | 5 · 2 · 2 |
| `Insect` | 5, plus 18 `BI_InfestationWorldObject` |

**3. The config cannot reach 21 of the 53 anyway.** Live in the save, absent from
Faction Control's list: `AA_BlackHive`, `BMT_PustuleHornets`, `BS_ZombieFaction`,
`DA_Troll`, `GR_RoamingMonstrosities`, `GiantAnt_Faction`, `HoraxCult`,
`MO_AbominationFaction`, `VRE_Archons`, `JDSCIS_CIS_Faction`,
`guy762_KotORFaction_RogueDroids`, plus ten vanilla hidden/permanent ones
(`Ancients`, `AncientsHostile`, `Entities`, `Mechanoid`, `MiningCo`, `Salvagers`,
`TribalHostile`, `DP_GenericHostile`, `AM_EnemyPirate`, `PlayerColony`).
**None of the eleven modded ones own settlements** — they are raid/event sources,
invisible on the map until they attack. `JDSCIS_*` and `guy762_KotOR*` are Star
Wars and should be KEPT. **For the rest, the real lever is mod removal, not this
config** — that is a proposition for VISION/PROJECT, not a row-2 edit.

**4. Two corrections to numbers already in the docs.**
- `V1_SCOPE.md:233` says **32** faction entries. It is **41** —
  `grep -c "<faction>"` and `grep -c "<li>"` both return 41 and the file has no
  other `<li>` field. **Filed to PROJECT, not edited by me.**
- Of those 41, **9 are configured but not present in this save**:
  `CannibalPirate`, `NudistTribe`, `OuterRim_RebelAlliance`, `OutlanderRough`,
  `Pirate`, `SplinterColony`, `TribeCannibal`, `TribeRough`, `TribeSavage`.
  ⚠️ **`OuterRim_RebelAlliance` is Star Wars and did not generate** — worth a
  look on its own, independent of row 2.

**5. Still missing: the exact settings schema.** Each `<li>` writes only
`<faction>NAME</faction>`; Scribe omits defaults, so the field that suppresses
(`min`? `max`? per the English keys) was unknown when this entry was first
written. **It landed after the wrap, and it kills the premise.**

### 🔴 5b. ANSWERED — and there is NO suppression field. Row 2 as written cannot be built.

Read two independent ways — IL disassembly of the installed 1.6 DLL, and the
published source at `https://gitlab.com/koenlemmen/rimworld-factioncontrol-master`
(TheRealLemon; ancestor is Designer225's unmerged PR against KiameV). ⚠️ **The
repo is the 1.4/1.5 state and the 1.6 delta is unpublished**, so the IL is
authoritative for our build — but where the two overlap they agree exactly.

**The per-`<li>` class is `FactionDensity`, singular.** `FactionDensities` is
the `static List<FactionDensity>` field holding them — the plural name in the XML
is the *list*, not the item class. **Three serialized fields: `faction`,
`density`, `enabled`.** That is all.

🔴 **`density` is a CLUMPING RADIUS, not a count.** Confirmed by the verbatim
line `__result = dist < fd.Density;` inside the
`TileFinder_IsValidTileForNewSettlement` postfix. **Setting it to 0 does not
remove a faction** — the English key *"Minimum number … (setting to 0 disables
the faction)"* is a **pre-1.3 leftover string** describing the old per-faction-min
UI, and reading it as current behaviour is the trap this row was built on.

**Faction removal is a WORLDGEN-TIME choice made on vanilla's Configure Factions
page**, which Faction Control merely unlocks and extends. It is not a setting we
can write to a file at all.

⚠️ **`enabled` is the one field I have NOT personally verified**, and the naive
reading (`enabled=false` suppresses) is exactly what the subagent says is wrong.
**It does not change the decision either way** — every relevant patch
(`GenerateFactionsIntoWorldLayer`, `GenerateFromScribe`,
`ResolveAllCrossReferences`, `WorldObjectsHolder_Add/Remove`,
`TileFinder_IsValidTileForNewSettlement`) acts at worldgen or at load-time tile
finding, never on faction existence in a loaded world. Verify only if v1 turns
out to start a fresh campaign.

**1.6-only deltas found, none of which move the conclusion:**
`Patch_FactionGenerator_GenerateFactionsIntoWorldLayer` is new and writes
`PlanetLayerDef.settlementsPer100kTiles` for the `Surface` layer;
`Settings.UpdateSettlementsPer100k()` is gone (density application moved to that
prefix — the Odyssey planet-layer rework); and
`Patch_FactionGenerator_GenerateFactionsIntoWorld` kept its 1.5 class name while
its Harmony attribute was retargeted to the renamed `…Layer` method, which is
why the class name and its target disagree.

⭐ **Tooling note: use `src/RimMandrake/Utils/ilprobe/`.** The subagent rebuilt an IL
disassembler in a scratchpad venv against `dnfile`, not knowing
`D:\Luke\dev\Rimworld\src\RimMandrake\Utils\ilprobe\il.py` had been committed 2026-08-12 and
needs no dependency. **Its scratchpad twin was discarded as redundant,
deliberately.**

**Parse traps hit while doing this, so nobody repeats them:** in
`<allFactions>`, `<loadID>` comes *after* a several-hundred-line `<relations>`
block, so a "nearest following `<loadID>` within N chars" lookup silently maps
each def to the NEXT record's ID — use a depth-tracking `<li>` splitter.
And **`Insect` has no `<loadID>` element at all** because Scribe omits an int at
its default; it is `Faction_0`, and reading its absence as a dangling reference
is wrong.

---

## Open

### O1. `refresh.py --patches` validates against NOTHING under WSL and reports ok
Migrated from `TODO.md` §16. The validator silently no-ops and returns success —
the worst failure shape there is, because it manufactures false confidence in a
patch that was never checked. **Fail-toward-success bug; fix so it errors when it
cannot find what it is meant to validate.**

### O2. `refresh.py` reports "current" for artefacts that do not exist
Migrated from `TODO.md` §12 (open list, item 2). Confirmed by WORLD. Same family
as O1 — a proxy comparison that passes when the real thing is absent.

### O3. `loadset_fingerprint()` compares *listed* against *exists*
Migrated from `TODO.md` §12 (open list, item 3). WORLD's finding, corroborated by
PROJECT. This is the `ModsConfig.xml` listed-but-missing trap in code form.

### O4. Does Faction Customizer's settings dialog persist across worlds?
**Split out of `TODO.md` §3d**, which was one item doing two jobs. The doc
correction half went to VISION; this half is an in-game verification and is yours.
It matters because the roster's goodwill-cap mechanism depends on the answer.

---

### O7. `validate_patch.py`'s lxml engine is SHIPPED but INERT
Both engines run side by side, so the change can only ADD findings — across all 37
patch files the entire old-vs-new diff was **one info line**, zero verdict changes.
But lxml is installed under **neither** interpreter. `python.exe -m pip install
--user lxml`, or `sudo apt install python3-lxml` for the WSL side (which has no pip
at all). Measured gain once installed: **52 UNSUPPORTED → 0, and 0 new errors.**

### O8. `DroidsAreMachines.xml` FAILs the validator on a FALSE POSITIVE
Two ERRORs, both pre-existing and both wrong: an op under `<match>` whose xpath
equals the conditional's own test **can never be a silent no-op** — if the test
matched nothing, the branch never runs. The patch is correct (both FleshTypeDefs
exist and simply lack `<isOrganic>`, so the `<nomatch>` Add fires, which is the
flip confirmed working in the dump). Fix: downgrade ERROR→info for that shape.
Deliberately **not** done inside the lxml change, because it flips an existing FAIL
to OK and deserves its own review.

### O9. `validate_patch.py --defnames <file>`
Validate against a pre-built list of live defNames instead of walking the whole
`Defs` tree — turns validation into a one-second set lookup. **The list is already
generated; only the flag is missing.**

### O10. Vibro versus lightsaber on the same target — the L14 thesis `[v2]`
Echani Foil (AP **1.33**) against Excellent durasteel heavy armour (Sharp 1.05) →
effective armour **zero**. Compare with the saber, which got only 27.5 through that
same suit. Take a Yautja blade swing too (AP 0.60) — a tier with zero operations —
to see it land between saber and vibro.

⚠️ **Do not regenerate the armoury patches from a contaminated dump** without
reading `src/RimMandrake/Utils/patch_provenance.py`. The generators anchor through
`observed/2026-08-13_pre-restructure/inventory/patch_ledger.json` and print a provenance banner; `unknown` anchors
means stop.

---

## Needs an owner decision before it is worked

### O5. "Write the three expected-failure signatures before the next load" — **possibly moot**
From `TODO.md` §7. The three-assemblies waiver was resolved ("the waiver STANDS,
batch it"), leaving this residual action. **But §13 records a shutdown/load cycle
already completed 2026-08-13 01:05**, which may be the very load this was meant to
precede. **Confirm with the owner whether that load already consumed this, and drop
it if so** rather than writing signatures for an event that has passed.

---

## Filed by PROJECT, 2026-08-13

### O6. ✅ DONE 2026-08-13 — renamed `AGENT_WORLD_state.md` → `AGENT_OPS_state.md`

_Done by OPS at close-out, with `agents_def.md` 605/615 and `NEXT_RELOAD.md` in the same commit. Three stale references remain and are NOT mine: `STRUCTURE.md:196`, `TODO_v2.md:730` (PROJECT's), and `AGENT_BRIDGE_state.md:858` (BRIDGE's own file). Filed to PROJECT rather than edited._
Left for you deliberately: **only the owning seat edits or deletes its state file**
(rule 6b), and that rule does not stop applying because the seat was renamed.
`agents_def.md:605` and `:615` still name the old file and are correct until you
move it — do both in one commit so the reference never dangles.
`git mv AGENT_WORLD_state.md AGENT_OPS_state.md`, then republish your address block.

---

## From BRIDGE, 2026-08-13 — faction-name diacritics: measured, not mine to fix

Filed on cutover so a 77k-token investigation is not lost. **The owner's actual
complaint turned out to be the loading screen, not names** (that is RimWorld's
`PseudoTranslated` dev feature, handled separately) — so this answers a question
nobody is now asking. Keeping it because it found a real upstream bug.

**The apostrophe names and the accented names have DIFFERENT causes, and three of
the five examples are vanilla.**

| in-game name | FactionDef | source |
|---|---|---|
| `Co'ltz'caz` | `DV_OutlanderRoughBuzzer` | Det's Xenotypes - Buzzers, `det.buzzers` |
| `Ry'loef` | `DV_PirateKeshig` | Det's Xenotypes - Keshig, `det.keshig` |
| `Wethaabog` · `Dtchsezz` · `Piggumok` | Tribe/Outlander xenotype factions | **Biotech, vanilla** |
| `The Brío Confederacy` | `KAR_OrcClan` via `NamerFactionTribal` | **Core, vanilla** |

🔴 **A GENUINE UPSTREAM BUG in `det.buzzers` (workshop 3545293786).** Its
`RulePacks_Namers_Faction.xml` has `<li>maybeApostrophe->''</li>` where vanilla
leaves the right-hand side **empty**. The parser reads `''` as two literal
apostrophes, so the "no apostrophe" branch became a "double apostrophe" branch:
vanilla emits one apostrophe in 9 names, Buzzers emits **one 75% of the time and
two 25% — never none**. Smoking gun in the save: settlement `Caz'vi''vi`.

A one-line `PatchOperationReplace` in `Jawa_Patches` would fix future names.
**It will not change existing ones** — faction names are baked into the save as
strings.

**The diacritics themselves are Ludeon's**, in two Core files —
`Strings/WordParts/Syllables_Galician.txt` and `Strings/Words/Foreign/Tribal.txt`.
Only **3 non-ASCII names exist in the entire save**. Editing Core is possible and
Steam reverts it on validate. Recommendation: leave them.

⭐ **The cheap fix is already installed.** Faction Customizer
(`azravos.factioncustomizer`, load order 145, ACTIVE) exposes `set_FactionName`
and a rename dialog. ~54 factions, 6 ugly ones, rename by hand — no restart, no
def edit, no save risk. Removing the Det mods instead would eliminate 2 of 54
faction names at the cost of `Could not load reference to XenotypeDef` on 4 real
pawns, plus 18 `DV_Gorewine`/`DV_GoreMust` references for Keshig.

⚠️ **`ModsConfig.xml` now lists 569 active, not 573** (mtime 09:27). The four
dropped are all mech mods: `el.biotechmechrt`,
`futurplanet.disassemblemechanoid`, `veltaris.mechanoidskins`,
`xelnigma.mechanoidslagtoplasteel`. Any doc still saying 573 is stale as of today.

---
## O5 — STILL STANDS (owner ruled 2026-08-13)
Owner does not recall which load was which, so treat O5 as live: write the three
expected-failure signatures before the worldgen session. A duplicate costs
nothing; a missed one costs a load.

---
## Filed by VISION, 2026-08-13

### O-v. `ModsConfig.xml:565` activates a mod that is NOT installed
`lee.theforce.lightsaber` is in `<activeMods>` and exists in neither mod root.
**One startup complaint on the next load, independent of anything else.** Either
remove the line or install the mod before the next cold load — it is not worth a
~25 min cycle to discover.

Found incidentally while auditing the mech-mod disabling; **not mine to fix**,
and it touches the live config, which is yours. Already checked and clean: no
authored mod of ours references it (full sweep of `src/Jawa/` and
`src/RimMandrake/`), so removing the line breaks nothing of ours.

⚠️ **Ask me before deleting it rather than after** — the Force-user build spec
(`design/Jawa/force_users_build_spec.md`, Jedi/Sith, owner-flagged joint build)
was mined from Force mods that were supposed to be uninstalled. If the owner
subscribed one deliberately, installing is the right fix, not removing.

---

## From BRIDGE 2026-08-13 — three identical "Jawa" rows in the xenotype picker

**Not a bug, a load-set decision, so it is yours and not mine.** The owner
reports seeing one Jawa when picking a xenotype. There are three, and they are
adjacent in the list with the same caption.

Evidence — the live def dump, `DefDump/defs/XenotypeDef.json`, captured
2026-08-13 14:51 UTC on game 1.6.4871, 250 XenotypeDefs:

| defName | label | genes | mod | ModsConfig # |
|---|---|---|---|---|
| `OuterRim_Jawa` | `jawa` | 8 | Outer Rim - Galactic Diversity | 545 |
| `guy762_xenotype_jawa` | `Jawa` | 18 | Star Wars Xenotypes | 549 |
| `BTD_Jawa` | `Jawa` | 24 | [BTD] Xenotype REMIX: Star Wars | 562 |

All three active in `ModsConfig.xml`. No defName collision, nothing overwrites
anything, and no field gates UI display — `inheritable=true`,
`displayPriority=0`, `canGenerateAsCombatant=true` on all three. Two share a
byte-identical icon (`OuterRim/XenotypeIcons/Xenotype_Jawa`).

**Why it matters:** our tuning patches
(`src/Jawa/Jawa_Patches/Patches/JawaAppearance_Tuning.xml`,
`JawaCombatViability_Tuning.xml`) xpath `XenotypeDef[defName="BTD_Jawa"]` and
nothing else. Picking either of the other two silently gets an UNTUNED Jawa.
The `OuterRim_Jawa` / `OuterRim_JawaTribal` PawnKindDefs pin `OuterRim_Jawa` at
chance 1, so pawnkind-driven spawns take a different Jawa than the one we tune.

**Systemic, not Jawa-specific:** the three Star Wars mods triplicate ~100
species — 3x chiss, 3x bothan, 3x ewok, 3x ithorian.

**Suggested fix, yours to rule on:** a `PatchOperationRemove` on the two we do
not use, or relabel them so they are distinguishable in the list. Removing is
the cleaner story only if nothing else references them — the pawnkind pin above
says something does, so check before removing.

**Already checked, do not repeat:** ModsConfig active-state for all three; the
full 250-def dump for duplicate defNames (none); our own patches for any
XenotypeDef removal (none — they only add/remove `genes/li` inside `BTD_Jawa`).

**Not verified live:** nobody has opened the picker and counted rows. Expect 3
filtered on "jawa". BRIDGE can drive that the next time the game is up.

### O-v2. Cherry Picker test — remove Mechanoids and their faction, does it hold? `[owner's ask, 2026-08-13]`
**Owner asked for this explicitly.** Test cherry-picking out the mechanoid defs
**and the `Mechanoid` faction**, then answer three things:

1. **Does the game still load?** That is the whole first question.
2. **Does `Samael.NPCMechsAndAnimals` survive and keep working — i.e. does it
   still add the ANIMALS half?** It is `Patches/NPC_Mechs.xml`, 13 ops injecting
   `Mech_Militor/Pikeman/Scyther/Mechanitor` into `Empire`, `OutlanderFactionBase`,
   `OutlanderRoughPig`, `Pirate`, `PirateWaster`, `PirateYttakin`, `TradersGuild`.
   **The mech half is what we want gone; the animal half we want kept.**
3. **Is that mod configurable** — a mod settings toggle for mechs vs animals?
   If it is, that is cheaper than cherry-picking and we should use it instead.

⚠️ **Do NOT remove Alpha Mechs (`sarg.alphamechs`) in this test.** Owner: *"alpha
mechs has some neat content I might want to leave in — little silly cleaners, and
some animal-looking THINGS that are pretty scary if we rename them."* **Renaming
them is VISION's call and I want them available to look at.** Note that Alpha
Mechs hangs off `FactionDef[defName="Mechanoid"]/pawnGroupMakers`, so removing
that faction takes Alpha Mechs' raids with it — **which is the tension to report
back on, not to resolve yourself.**

⚠️ **`matathias.ruthlessmechanoids` is NOT a mech mod** — it is Ruthless Faction
Pursuit, the gravship pursuer redirect. The owner re-enabled it. Leave it on.

### O-v3. Enable VWE-Laser and dump its weapon ThingDefs for review `[owner's ask]`
`vanillaexpanded.vwel`, ws `1989352844`, installed and inactive. Owner wants the
mod on and **a reprocessed dump of its weapon `ThingDef`s so the numbers can be
examined and normalised** against our stack.

**This is not a generic weapon pack — the owner ruled it narrative.** The lasers
are the gravship's own legacy armoury, rebuildable from onboard files:
`D:\Luke\dev\Rimworld\design\Jawa\worldbuilding\ship_legacy_armoury.md`.

Useful before you start: the mod already ships **two tiers** — `salvaged` laser
pistol/rifle/shotgun/sniper with `unstable` projectile variants, and the full
`ultratech laser weapons` set including a **laser sword** and a **tesla gun**.
**Dump both tiers separately**; the split is load-bearing for the design.

> 🔴 **RETRACTED 2026-08-13 17:52 by BRIDGE, the seat that filed it. Do not
> action the item above.** It said three Jawa xenotypes are live and only
> `BTD_Jawa` is tuned, and proposed a `PatchOperationRemove` on the other two.
> **There is nothing to remove.** From `Player.log`, this load:
>
> ```
> [BTD Xenotype Remix] Starting processing. Current xenotype count: 250
> [BTD Xenotype Remix] Remapped 552 xenotype chances across 9 factions and
>                      99 pawnkinds, plus 0 direct references
> [BTD Xenotype Remix] Successfully removed 100 duplicate xenotypes
>                      (BTD preference active)
> [BTD Xenotype Remix] Processing complete. Final xenotype count: 150
> ```
>
> BTD Xenotype Remix **deduplicates at load** and keeps its own — so `BTD_Jawa`
> is the only Jawa at runtime, which is the one our patches tune. The pawnkind
> pins that worried me were among the 552 remapped. The owner's report of seeing
> exactly one Jawa was correct and my filing was not.
>
> **How I got it wrong, because the method is the reusable part:** the finding
> came off `DefDump/defs/XenotypeDef.json` — 250 defs, three Jawas. That dump
> captures defs as loaded from disk, **before** a mod's startup code mutates the
> database. A def dump is authoritative about what shipped, never about what the
> running game holds. The log said 250 → 150 in the same file I could have read
> first. Filed as a trap.

---

## ✅ 2026-08-13 live-load confirmations (580 mods, rev591, dump 17:45)

**Jawa_Patches defs are IN THE GAME, not just on disk** — all four resolve in the
live dump, which closes the def half of v1 rows 3 and 4:
`Jawa_SaltCrust` (TerrainDef) · `Jawa_ScatterScrapfields` (GenStepDef) ·
`Jawa_TheClaim` (QuestScriptDef) · `Jawa_ClaimRumour` (ThingDef).
⚠️ Still unproven: that they *do* anything. The terrain and scrapfields act at
**map generation only**, so an existing map shows nothing — that is a worldgen
observation, not a def check.

**`JawaIonWeapons` PROVEN live** — 15 `JawaIon_Damage` downed `KotORDroidGood_3C`,
`downed=true dead=false`, quicktest map. Evidence
`observed/evidence/2026-08-13_ion_downs_kotor_droid.png`, write-up
`observed/2026-08-13_ion_weapon_live_test.md`. **This is the only v1 item whose
proof is a screenshot rather than a log line, and it always will be.**

**Lightsabers restored:** 15 lightsaber ThingDefs live after the owner's
re-subscribe of workshop `3466124712`. **VWEL:** 11 `VWEL_Gun_*` live.

**573 → 580 def delta, with the counter-intuitive bit:** total defs went **DOWN**
84,749 → 84,698 despite +7 mods, because the four removed mech mods took **110
`SkinDef`s** with them. A falling def count is not evidence something broke.

🔴 **My own error, recorded because it is the project's own rule:** I first
reported two of those four defs MISSING because I looked them up by **filename**.
`JawaSaltCrust.xml` declares `Jawa_SaltCrust`; `JawaScrapfields.xml` declares
`Jawa_ScatterScrapfields`. **Never guess a defName — read the def.** A filename
is not an identifier.

⚠️ **`--defnames` does NOT validate xpaths**, only that a defName exists. All 43
of our patch files pass 0 errors against the live index — that is real but
narrow. An xpath matching nothing still passes; only `--defs` catches it.

## 🔴 I deleted `defnames.573` and the reasoning was wrong — 2026-08-13

**Mine, not a mystery.** Commit `262666b`, `rm -f defnames.573.2026-08-13.json`,
message *"regenerable cache"*. A peer spent a search establishing that it was
gone and unrecoverable and could not name the cause. **The cause was me.**

**Why the reasoning failed, because the rule needs sharpening:** CLAUDE.md's
artifact table asks *"could a machine regenerate this?"* I answered **yes** — and
it was true only while the **573-mod def dump still existed**. The 17:45 load
overwrote that dump with the 580 one. **Reproducibility is a property of the
INPUT surviving, not of the script existing.** An artifact derived from a
transient input is unreproducible the moment the input rolls, and belongs in the
bottom-left cell: **on disk and committed, not deleted.**

**What was actually lost:** only per-defName granularity — *which* names vanished
beyond what the counts imply. The manifests survived, so the useful half was
reconstructed: `SkinDef` 110 → **0**, ThingDef +37, SoundDef +9, RecipeDef +4,
514 → 511 types, 84,749 → 84,698 defs. Cost: real but small.

✅ **Reversed the call: `defnames.580` is now COMMITTED**, because it sits in
exactly the position 573 sat in an hour ago and the next load makes it
unreproducible too.

⚠️ **Two counts, both correct, different denominators** — the index holds
**84,848 rows** across 436 types and **73,396 UNIQUE** defNames; a name can appear
under more than one type file. A peer reported 85,022/450 before the orphan fix.
Quote which one you mean.
