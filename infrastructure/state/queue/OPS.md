# infrastructure/state/queue/OPS.md

_OPS's queue. **You own this file — write freely, nobody blocks on it.** Others
file at you by appending. Doctrine is in `agents_def.md`; the v1/v2 line is in
`V1_SCOPE.md`. **Closed items are ONE line in `infrastructure/state/CLOSED.md`,
with the hash — `git show <hash>` has the story. Never keep the body here.**_

⚠️ **`[WORLD]`-tagged items were split, not renamed.** What the world should
*contain* went to `queue/VISION.md`. This file is live-stack work: does it
function, what broke, what is the smallest test.

---

## 🔴 PENDING OWNER DECISION — O12, the droid relations NRE. **NOT CHOSEN YET.**

**Recorded 2026-08-14 12:5x by OPS at the owner's instruction, at shutdown.**
🔴 **The owner asked for the choice to be recorded, and did NOT state which
route. Nobody has picked one. Do not read a preference into this block, and do
not implement any route until the owner names it.** Evidence and the full chain:
row **O12** below, and `observed/2026-08-14_O12_har_pawngen_nre.md`.

**What is broken:** our `Jawa_Doctrine/Patches/DroidsAreMachines.xml` sets
`isOrganic=false` on the KotOR flesh type ⇒ `IsFlesh` false ⇒ no
`Pawn_RelationsTracker` ⇒ HAR NREs on the **2nd and later same-race droid**.
Worldgen is unaffected (four grounds, in O12). `RogueDroids` **raids** are — and
that faction is the KotOR distress call's antagonist and a **v1 KEEP**.

| route | cost | side effects |
|---|---|---|
| **1 — drop the KotOR flesh type from our patch** | one xpath, no assembly | restores tending on droids; **loses vanilla EMP behaviour** on them; ⭐ **does NOT affect our ion weapon** — its guard moved to `IsMechanoid` on 08-13 |
| **2 — ~5 lines of Harmony** in an assembly we already ship | a build + a deploy + a load | give Humanlike pawns a relations tracker regardless of `IsFlesh`; keeps both the machine framing and working raids |
| **3 — accept broken droid raids** | free | the quest antagonist cannot raid past its first pawn |
| ⛔ **excluded** | — | retargeting to vanilla `Mechanoid` — it would make our own ion weapon block them |

**Before implementing whichever is chosen:** the 30-second live confirmation —
spawn `KotORDroidGood_3C` twice on any map, the second must NRE. If it does not,
the chain is wrong and all three routes are moot.

---

## ⭐ v1 — Row 2, the worldgen faction cut. UNEXECUTED.

🔴 **The whole body of this item is now
`D:\Luke\dev\Rimworld\infrastructure\state\WORLDGEN_FACTION_CHECKLIST.md`** —
ratified, executable, and it *corrects* the proposal that used to live here. Do
not re-derive the exclusion list from this file; it is not here any more.

**Three things a successor must not get wrong, and they are the reason this
section still exists at all:**

1. ⚠️ **A quicktest map's faction roster PROVES NOTHING about the cut.** A debug
   quicktest never visits the Configure Factions page, so every faction is
   present by default. That reading nearly triggered a needless 25–30 min
   regeneration. **State which map any faction census came from.**
2. **Faction removal is a worldgen-time choice at the screen, not a setting.**
   Faction Control's `density` is a **clumping radius** (`__result = dist <
   fd.Density;`), not a count; the English key *"setting to 0 disables the
   faction"* is a pre-1.3 leftover and is what row 2 was originally built on.
   **There is no file we can write to suppress a faction.**
3. **Before calling any missing faction a defect, grep `Jawa_Patches/` for its
   defName.** `OuterRim_RebelAlliance` was reported as a failed generation; we
   had suppressed it ourselves, deliberately, in `RebelAlliance_Suppress.xml`.
   Our own deployed patches are part of the environment.

---

## 🔴 THE SHUTDOWN-WINDOW DEPLOY LIST — mine, and nobody calls the window without me

**Plan run 2026-08-14, read-only, `deploy_custom_mods.py` with no `--apply`: 7 files drifted,
4 `DEPLOY_HOLD.txt` patterns honoured.** ⚠️ **`--apply` overwrites the game copy with whatever is
in the repo AT THAT MOMENT — scope it with `--mod`, never run it bare.**

### SHIP
| file | why it is ready |
|---|---|
| `+ Jawa_Patches/Patches/BuzzerApostrophe_Fix.xml` | committed `3822ef9`, `validate_patch.py` clean, both namer sites. **Worth shipping ONLY before worldgen** — names bake into the save as strings. |
| `~ Jawa_Patches/Defs/MapGeneration/JawaScrapfields.xml` | CREATE's `de1018b` drops `isJunk`; `clusterSize` 8-12 still inbound. Deployed copy is still **08-13 16:42:35 with `isJunk` present**. |
| `~ Jawa_Patches/Defs/MapGeneration/JawaGroundHulk.xml` | same edit. ⚠️ Both are **map-generation** defs: they need a cold load **AND a map generated after it**. |
| `~ Jawa_Patches/Patches/AnimalBiomeDuplicates_Fix.xml` | committed and clean — confirm the owning seat before it rides. |

### 🔴 HOLD — do not let these ride the window
| file | why |
|---|---|
| `~ Jawa_Armoury/Patches/Armoury_MeleePower.xml` · `Armoury_RangedDamage.xml` | **Swept into `81939e1`, whose subject is genome tooling** — committed under an unrelated message, never reviewed, and carrying **no provenance banner**. The queue rule stands: `unknown` anchors means stop. Re-run the generator and read the banner before these ship. |
| `~ JawaSeaShaper/1.6/Assemblies/JawaSeaShaper.dll` | ⚠️ **Reason UPDATED — my earlier "stale build" is no longer true.** CREATE committed DLL and source together in `c3ee8e7`, so the repo pair is consistent and clean. 🔴 **The live fact that replaces it: the game is running a DIFFERENT binary.** Repo DLL md5 `b7730027a639`; deployed/loaded DLL md5 `82b48e53e668`, mtime **08-13 23:57:29**, which predates the 01:03:26 launch. ⇒ **the arc-distance and elongation work verified in `c3ee8e7` is NOT in the running game** — G1 is done in the repo and live nowhere. **The assembly is loaded and therefore locked: this deploy can only happen while the game is DOWN, and a new assembly goes SOLO** so the load that carries it can attribute what it does. |


## ⭐ THE ART-OBSERVATION BATCH — runnable on ANY live map, no fresh map, no load

**CREATE supplied defNames, file:line and the broken FACING for each. All three tools
already exist in the live 147** — `jawa/spawn_pawn`, `jawa/set_pawn_style`,
`jawa/set_pawn_rotation` — **so this needs no new capability and no map generation.**
⚠️ Observation only. The owner's stop on art *fixing* stands; looking is not fixing.

🔴 **A pawnkind spawn ALONE tests none of these.** All three are HairDef/apparel
`texPath`s, not pawnkind art — **the style has to be SET**, or you photograph a default
and call it passed.

| item | spawn | then set | face |
|---|---|---|---|
| **CereanManeFix** | pawnkind `OuterRim_Cerean` (forces the xenotype, weight 999) | hair `OuterRim_CereanMane` — a fresh Cerean rolls it ~1 in 5, so **set it, do not hope** | **SOUTH** |
| **SauridFrillFix** | pawnkind `VRESaurids_Villager_Saurid` | hair `VRESaurids_Littlefoot` (`texPath Pawn/CenterFrill/CenterFrill8`) | **NORTH** — the donor ships `CenterFrill8_north-.png` with a **trailing hyphen**; `CenterFrill7_north.png` next to it is named correctly. North is the ONLY broken rotation |

**Both leave `NEXT_RELOAD.md` §7.** They were parked there for "no pawnkind defName";
CREATE found both, with file and line.

### Still uncollectable, and now for a proven reason
**ToolBeltFix.** `VAEA_Apparel_ToolBelt` is spawned by **no** PawnKindDef — CREATE
grepped the workshop tree, `Mods/` and `Data/`: zero hits in `apparelRequired`,
`specificApparelRequirements` or any fixed list, and its only tag
`VAEA_Utility_Industrial` appears in no pawnkind, so there is no random path either.
Every other reference is loot. ⇒ **needs dev-spawn plus a FORCE-EQUIP, which is the
route BRIDGE is building. Hold it for that tool, NOT for a load.** When it lands:
face **WEST** (`ToolBelt_west.png` is 753 bytes against `ToolBelt_east.png` at 16,945),
and ⚠️ `renderUtilityAsPack` is true so it draws in the pack layer — **check from
behind as well as straight west.**


## Open — offline, no game needed

| # | item | note |
|---|---|---|
| **O3** | `loadset_fingerprint()` compares *listed* against *exists* | The `ModsConfig.xml` listed-but-missing trap in code form. WORLD's finding, corroborated by PROJECT. |
| ~~**O8**~~ | ✅ **DONE — already fixed in `6b37e88` (2026-08-13). Do not re-do it.** | `_guarded_by_identical_test()` in `validate_patch.py` downgrades ERROR→info for an op in a conditional's `<match>` whose xpath equals the test. **Re-verified 2026-08-14 against the real load set** (34k def files, 49 Jawa patch files): `DroidsAreMachines.xml` FAIL(2 errors) → **OK (0 errors, 2 warnings)**, and it is the **only** file whose verdict moves. `<nomatch>` is deliberately excluded — there the identical xpath is a *guaranteed* no-op, so it must stay an ERROR (proven with a synthetic case). |
| ~~**O14**~~ | ✅ **DONE — fixed by CREATE in `d00829a`.** | Verified by me 2026-08-14 at `src/RimMandrake/Utils/preload_check.py:150-156`: `GP.WORKSHOP`/`GP.LOCAL_MODS`, both `/mnt/c` literals gone, and a missing root is a **FAIL** carrying the 'are you on python.exe?' hint — not a `continue`. ⚠️ **The path is `Utils/`, not `bridgetools/`** — the original row named the wrong directory. |
| **O12** | 🔴 **SETTLED 2026-08-14 — REAL DEFECT, AND WE CAUSED IT. Do NOT waive; do NOT add to the benign list.** **Chain, verified this session:** our `src/Jawa/Jawa_Doctrine/Patches/DroidsAreMachines.xml` (owner-authorised 08-11) sets `isOrganic=false` on `ABF_FleshType_Synstruct_Base` — confirmed live in the def dump, and confirmed independently by `validate_patch.py --defs`, which shows both ops targeting `/Defs/FleshTypeDef[...]/isOrganic`. From `Assembly-CSharp.dll`: `RaceProperties.IsFlesh => FleshType.isOrganic`, and `PawnComponentsUtility.CreateInitialComponents` builds `Pawn_RelationsTracker` **only `if (pawn.RaceProps.IsFlesh)`**. ⇒ every KotOR droid has `relations == null`, and HAR derefs it unguarded at `HarmonyPatches.cs:2670`. **Faction is irrelevant — that hypothesis is dead.** ⭐ **Exact trigger:** HAR's candidate list is same-`def` pawns only ⇒ **the FIRST droid of a race always succeeds, the SECOND and later always throw** while the first is still in the world. That is the ion-test note's 'first spawn worked, later attempts NRE'd', and why `ID-662`/`KM1`/`ID-825`/`R-8009` were clean (each first-of-its-def). **Two corrections to the original entry: there is no 9th occurrence** (one burst of 9, all `Ref E66AFB4E` — the head was counted apart from its own duplicates), and **it is not silent** — it is a `Log.Error` that rethrows. ✅ **WORLDGEN IS CLEAR on four independent grounds** — `RogueDroids` has `humanlikeFaction=false`, `hidden=true` and both `factionLeader` entries commented out (`PawnKinds_RogueDroids.xml:797,872`) so `TryGenerateNewLeader` gets an empty list; CIS droids are `ToolUser` and early-return; no KEEP faction has a droid leader; two measured worldgens produced zero. **This does not block the worldgen load.** 🔴 **What IS broken: `guy762_KotORFaction_RogueDroids` RAIDS** — repeated same-race droids, so the 2nd pawn onward throws. That faction is the quest-critical antagonist of the KotOR distress call and a **v1 KEEP**. **OWNER DECISION OWED, three routes:** (1) drop the KotOR flesh type from our patch — restores tending, loses vanilla EMP on them, **does not touch our ion weapon** (its guard moved to `IsMechanoid` on 08-13); (2) ~5 lines of Harmony in an assembly we already ship, giving Humanlike pawns a relations tracker regardless of `IsFlesh`; (3) accept broken droid raids. **Retargeting to vanilla `Mechanoid` is EXCLUDED** — it would make our own ion weapon block them. **30-second live confirmation, any map:** spawn `KotORDroidGood_3C` twice; the second must NRE. If it does not, the chain is wrong and this re-opens. Full write-up: `observed/2026-08-14_O12_har_pawngen_nre.md`. |
| **O13** | `BTDGravshipQuest_GrammarFix.xml` is authored, validated and committed — **NOT DEPLOYED** | `57b6f69`. **xpath CONFIRMED against installed defs** — lxml 6.0.2.0, 34,719 def files, **exactly 1 match, in `[BTD] Gravship Blueprints: Script_BTD_DownedGravship.xml`**. Not a guess and not a static-only pass. Writing a file is not deploying it; the game reads `…\common\RimWorld\Mods\Jawa_Patches`, and nothing syncs the two. Ride the next deploy pass. **Success is a POSITIVE observation** — the Downed Gravship quest showing description text in the Quests tab. The disappearance of `Grammar unresolvable` proves nothing on its own, because the quest may simply not have fired. |
| **O11** | `det.buzzers` emits doubled apostrophes in faction names — a real upstream bug | `RulePacks_Namers_Faction.xml` has `<li>maybeApostrophe->''</li>` where vanilla leaves the RHS **empty**, so the "no apostrophe" branch became a "double apostrophe" branch: one 75% of the time, two 25%, never none. Smoking gun `Caz'vi''vi`. **A one-line `PatchOperationReplace` fixes FUTURE names only** — names bake into the save as strings. 🔴 **So it is worth doing only if it lands BEFORE the new worldgen.** After that, worthless. |
| **O16** | 🔴 **Every WSL `--defs` validation before `a1483e7` was UNSCOPED — re-check any conclusion that rested on a match count** | `validate_patch.py`'s default ModsConfig path was built from `expanduser("~")`, which under WSL is `/home/<user>` and never the Windows profile. The file was silently not found and the tool fell back to its unscoped mode — **1,271 installed mods / 34,719 def files instead of 585 active / 8,972** — while still printing OK. ⇒ **a '0 matches' verdict was trustworthy** (nothing anywhere matched), but **any non-zero count may have come from an INACTIVE mod**, and 'matches N in <mod>' named mods the game never loads. Fixed `a1483e7`; re-run anything whose conclusion was a count. |
| **O17** | `validate_patch.py`: an op in a `<nomatch>` branch whose xpath equals the conditional's test is STATICALLY DEAD | The mirror of O8, and the opposite verdict: reaching `<nomatch>` proves the test matched **nothing**, so an identical-xpath op there can never do anything — provable **without** `--defs`. Currently it is only caught as a 0-match ERROR when defs are loaded. Cheap enhancement, not urgent. |
| **O18** | Re-run the **scoped** full-patch sweep — it has never completed against the real load set | Started 2026-08-14, killed unfinished at shutdown. Every earlier sweep ran UNSCOPED (see O16), so no `src/Jawa` result on record describes the running game. One command, no game needed, ~10+ min: `python3 skills/rimworld-modding/scripts/validate_patch.py src/Jawa --defs "/mnt/c/Program Files (x86)/Steam/steamapps/workshop/content/294100" --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods" --defs "/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Data" > observed/2026-08-1X_patch_sweep_scoped.txt` — **write it into `observed/`, not the scratchpad** (the last run died with the tmpfs). Expect the header to read `585 active mods, 585 found on disk`; if it says `unscoped`, stop and fix the invocation. |

| **O15** | 🔴 **REFRAMED 2026-08-14 — "11 measured" was never a measurement, and the offline audit closed the two obvious causes.** **Provenance of the number:** `observed/2026-08-14_row4_live.md:97-101` is 9 rects of 30x30 = 8,100 cells, ~13% of the map, holding **1** `ChunkSlagSteel` on each of two maps, extrapolated by /0.13 to **~7 map-wide**. ⚠️ **The queue's "11" never matched its own source, and WHERE the 9 rects sat is recorded nowhere** — so the uniform-coverage assumption behind the extrapolation was never established. **An extrapolation is not a count.** **Two hypotheses now DEAD, both from `Assembly-CSharp.dll` rev591:** (1) *silent give-up* does not exist — the bound is 1000 (`CellFinderLoose::TryFindRandomNotEdgeCellWith` IL_002e), the give-up **is logged** (`GenStep_Scatterer::TryFindScatterCell` IL_0083 gates on `warnOnFail`, default **true** at `.ctor` IL_0051, unset in our def) and it warns **once per step** because the fail path is `ret`, not `continue` (`GenStep_ScatterThings::Generate` IL_00b3); (2) *units mismatch* is ruled out — `clusterSize` landed at `2ddd388` (08-14 02:38) **after** the measurement, the measured def is `73ca76c`, and `ChunkSlagSteel` inherits `stackLimit 1`, so one loop iteration = one chunk. `minSpacing 4` is not binding. 🔴 **The contradiction that reframes it:** the hulk warned (`Player.log:6759`) ⇒ factor >= 1 ⇒ scrapfields count >= 75; scrapfields did **NOT** warn ⇒ its loop **completed** ⇒ **the chunks were spawned.** Only two survivors: **(a) the sample is unrepresentative** (now the leading candidate), or **(b) removal after order 960** — weak, the only vanilla candidate is `GravshipMarker` order 1700 at a few percent of cells. **Smallest test, rides any loaded map, no fresh map needed:** a full-map `listerThings` count of `ChunkSlagSteel` — **no sampling** — plus `TileInfo.Mutators` and map size. >=75 closes this as a MEASUREMENT defect; ~7-11 leaves the mutator product as the only remaining term. ⚠️ **Match the band to the def the map was BUILT with:** 75-125 pre-`de1018b`, 44-56 in 4-6 clumps after. Full audit: `observed/2026-08-14_O15_scrapfields_offline.md`. |

## Open — needs the live game

| # | item | note |
|---|---|---|
| **O4** | Does Faction Customizer's settings dialog persist across worlds? | One minute at the keyboard. The roster's goodwill-cap mechanism depends on the answer. |
| **O5** | Write the three expected-failure signatures **before** the worldgen session | Owner ruled it still stands (does not recall which load was which). A duplicate costs nothing; a missed one costs a load. |

## Open — `[v2]`, not now

| # | item | note |
|---|---|---|
| **O10** | Vibro versus lightsaber on the same target — the L14 thesis | Echani Foil (AP **1.33**) vs Excellent durasteel heavy armour (Sharp 1.05) → effective armour **zero**; the saber got only 27.5 through the same suit. Add a Yautja blade (AP 0.60) to land a tier between them. |

⚠️ **Do not regenerate the armoury patches from a contaminated dump** without
reading `src/RimMandrake/Utils/patch_provenance.py`. The generators anchor
through `observed/2026-08-13/inventory/patch_ledger.json` and print a provenance
banner; `unknown` anchors means **stop**.

---

## 🔴 The game-down batch — mod-list work, mine exclusively, free right now

**A mod-list change only lands on a restart, so all of this is free while the
game is down and costs a ~25 min cycle afterwards.** Collect every seat's pending
request and do them in ONE pass before the next launch.

| ☐ | item | why |
|---|---|---|
| ☐ | Pin the 6 `loadBottom`+`loadAfter` userRules | Order is correct **today** but rides a tie-break, not a constraint. `loadBottom` outranks `loadAfter` — keep it only on `rimdefdump`. |
| ☐ | Retire `mandrake.missingartfixes` (`ModsConfig.xml:560`) | All 7 textures md5-identical to the per-donor successors; blocking dep cleared. |
| ☐ | Run `refresh.py` | Wants the game down. |
| ☐ | **O-v2 — Cherry Picker: remove mechanoid defs AND the `Mechanoid` faction** | Owner's explicit ask. Answer three things: (1) **does the game still load?** (2) does `Samael.NPCMechsAndAnimals` survive and keep its ANIMALS half — `Patches/NPC_Mechs.xml`, 13 ops into `Empire`/`Outlander*`/`Pirate*`/`TradersGuild`? We want the mech half gone, the animal half kept. (3) is that mod configurable — a settings toggle would be cheaper than cherry-picking. ⚠️ **Do NOT remove Alpha Mechs (`sarg.alphamechs`)** — owner wants its cleaners and its animal-looking things available to look at. **Tension to REPORT, not resolve:** Alpha Mechs hangs off `FactionDef[defName="Mechanoid"]/pawnGroupMakers`, so cutting that faction takes its raids too. ⚠️ `matathias.ruthlessmechanoids` is **not** a mech mod — it is the gravship pursuer redirect; leave it on. |
| ☐ | **O-v3 — Enable `vanillaexpanded.vwel` and dump its weapon ThingDefs** | Owner's ask; ws `1989352844`, installed and inactive. **Not a generic weapon pack — owner ruled it narrative:** these are the gravship's legacy armoury, `design/Jawa/worldbuilding/ship_legacy_armoury.md`. **Dump the two tiers SEPARATELY** — `salvaged` (pistol/rifle/shotgun/sniper + `unstable` projectile variants) and `ultratech` (incl. a laser sword and a tesla gun). The split is load-bearing for the design. |

⚠️ **RimSort writes `ModsConfig.xml` too — read its mtime before you write**, or
you clobber a re-sort you cannot see. Measured: the file moved twice in twenty
minutes with the game down.

---

## Standing facts — do not re-derive

**Counts, with their derivation, because quoting a bare number is my
characteristic failure mode:** `grep -c "<li>" ModsConfig.xml` = **585**, minus
**5** `<knownExpansions>` = **580 active**. The def index holds **84,848 rows**
across 436 types but **73,396 UNIQUE** defNames — a name can appear under more
than one type file. **Say which one you mean.**

🔴 **`manifest.json`'s `allDefs` is NOT comparable to earlier dumps — it is a NEW key.**
Measured 2026-08-14: the live 585 manifest carries `allDefs: 30742`, while the
committed **573 / 574 / 580** manifests do not have the key **at all**. The figure
this project has always quoted (84,749 → 84,698) is **`sum(defCounts)`**.
Comparing the two reads as a **64% def collapse** that did not happen: the real
number is **84,698 → 85,057, up 359** — `ThingDef` **+243**, `RecipeDef` +28,
`EffecterDef` +17, `FleckDef` +17, all consistent with GravTech loading.
**Always compare `sum(defCounts)`, and say which figure you mean.**

**`live_mod_inventory.md` is the single source of truth for mod identity** —
existence, packageId, Workshop ID, author, versions. It is GENERATED; regenerate,
never hand-edit. Any doc claiming 562 or 573 active is stale.

⚠️ **`--defnames` does NOT validate xpaths**, only that a defName exists. All 43
patch files passing 0 errors against the live index is real but narrow — an xpath
matching nothing still passes. **Only `--defs` catches that.**

🔴 **Steam Cloud restores deleted saves on launch.** Cloud must be DISABLED for
RimWorld before deleting or the next launch undoes it. Owner's call; not touching
it. Full entry: `traps-mods-and-managers.md`.

**Blockers to play that are not mine to clear:**
1. **Gravship radius unresolved** — Bigger Gravships set to 34 in
   `Config/Mod_3522759531_GravshipSizeSettings.xml`, but it bakes radii into defs
   at **startup**. If this session's defs carry the ~25.9 defaults, **a ship built
   now will not lift and nothing logs why.** BRIDGE owes the `get_def
   GravFieldExtender` call that settles it. **Do not build a ship until then.**

**Do not re-litigate:**
- **V2 Ideology — `[v2]`, owner-deferred. STOP WORK.** Unverified, not failing.
- **Warcasket Heat stays `Cap(0.90)`** — owner: *"They're terrifying."* Wanted.
- **Warcasket deploy: "ship neither."** Both retune files stay in the repo
  undeployed, **permanently — intended state, not drift. Stop reporting it.**
  Asked three ways and answered; re-opening costs the owner twice.

---

## ✅ 2026-08-14 pre-launch deploy — DONE. 4 files shipped, game confirmed down.

`deploy_custom_mods.py --mod Jawa_Patches --apply` → `-> VERIFIED in sync`, 4 files:
`BuzzerApostrophe_Fix.xml` (new, `3822ef9` — the deadline item, **shipped before
worldgen**), `JawaGroundHulk.xml`, `JawaScrapfields.xml` (`isJunk` off, `de1018b`),
`AnimalBiomeDuplicates_Fix.xml` (`9acddd3`). Nothing was dropped; the window held.

**§1d row 1 (companion DLL) was already stale-as-owed — it is DEPLOYED.** Repo
`src/RimMandrake/bridgetools/artifacts/BridgeTools/JawaBench/JawaBench.BridgeTools.dll`
and the game copy are **md5-identical** (`55b23629…`), 292,864 B @ 08-14 12:25.
26 `jawa/` tool names; `get_defs`, `fire_quest`, `fire_incident` and `send_letter`
all present ⇒ it was built **with `--gm`**, nothing stripped. ⚠️ `strings -a` proves
NAMES only, never a method body (§1c). **Do not re-deploy it.**

Held, deliberately: `JawaSeaShaper.dll` (SOLO, own load — repo/game still differ),
Armoury ×2 (scope), WreckedMachines ×14 + GravshipAstronautFix ×1 (`DEPLOY_HOLD.txt`).

### 🔴 New — `--plan` lists a mod §1d does not: **StrandedQuest, 3 files, NOT DEPLOYED**

`src/Jawa/StrandedQuest/` — `About/About.xml`,
`Defs/HistoryEventDefs/HistoryEvents_Stranded.xml`,
`Defs/QuestScriptDefs/Quest_Stranded.xml`. **Not enabled in `ModsConfig.xml`**, so
deploying it alone is inert and enabling it is a mod-list act that adds an
unannounced quest surface to this load. **Left out on purpose.** Also not deployed
and not enabled: `KotORBandolierNorthFix`, `MissingArtFixes`, `PhytokinBarkHeadFix`.

⇒ **Ask CREATE/VISION whether StrandedQuest is v1 and wanted in the world about to
be generated. If yes, it is an enable + deploy and it must happen before launch;
if not, it stays inert and costs nothing.** Do not enable it on a peer's say-so.

**Row 6 (`BTDGravshipQuest_GrammarFix.xml`, O13, `57b6f69`) was never owed — it is
LIVE.** Repo and game copy md5-identical `d68bea3f…`; it is a `Jawa_Patches` file,
so the `--mod Jawa_Patches` run covered it and found no drift. It shipped with the
08-13 deploy. ⇒ **§1d row 6 is satisfied, not pending. Nothing further owed before
this launch.**

## ✅ O18 CLOSED — the scoped sweep ran: **72 files, 0 errors, 1608 warnings, all four classes accounted for**

Findings: `D:\Luke\dev\Rimworld\observed\2026-08-14_patch_sweep_scoped_findings.md`.
Raw 1.7 MB left untracked at `observed/2026-08-14_patch_sweep_scoped.txt` — reproducible,
and the value is in the findings file.

**Scoped, header verbatim: `585 active mods, 585 found on disk, target 1.6 -> 8,978 def
files`.** ⇒ this is the FIRST `src/Jawa` result that describes the running game; every
pre-`a1483e7` sweep (O16) is superseded, not merely old.

**1,536 of 1,608 warnings are the add-if-missing idiom** the validator itself calls
intentional; `MegafaunaYield.xml` alone holds 1,206. 🔴 **Read the classes, never the
count** — a future sweep will print a similar number and it means nothing on its own.

**59 load-order warnings CHECKED AND SATISFIED**: doctrine 567 / armoury 579 / patches
581 of 585, all after Royalty 5, Biotech 7, VFE Core 20, Alpha Biomes 50 and — the only
close one — Facial Animation Compat Project 564 vs `HeadSetForFA_Revive.xml` at 581.
**Do not re-derive this next sweep; the warnings recur because the validator cannot see
runtime-created nodes.**

**Two items left open, both deliberately cheap:**
- 3 double-match `Replace`s in `MegafaunaYield.xml` (same value to both nodes; a player
  cannot see it). 8 more sit in HELD `Armoury_RangedDamage.xml` — deal with them when
  the Armoury ships, not before.
- 2 unresolvable `iconPath`s — `Jawa_Head_Plain` → `UI/Icons/Genes/Gene_Hair`,
  `Jawa_Xeno_Gamorrean` → `UI/Icons/Xenotypes/Pigskin`. ⛔ **Not settleable offline**
  (vanilla textures are in asset bundles). **Eyes-on in the xenotype picker this load:
  a pink/blank square is the defect, both drawing closes it permanently.**

## 📌 NEXT SHUTDOWN WINDOW — two DLLs owed, and they CAN share the window

Recorded 2026-08-14 by OPS while the game sits at `Entry`.

| item | attribution cost | why |
|---|---|---|
| `JawaSeaShaper.dll` — repo md5 `b7730027` vs deployed `82b48e53` | 🔴 **SOLO** | a new **game assembly** in the mod stack; it patches the world and poisons attribution for anything loaded beside it |
| **BridgeTools `JawaBench.BridgeTools.dll`** — 28 tools, md5 `d3ace1f6c26fd12f9c326b42145d02e4`, built by BRIDGE 2026-08-14 | ✅ **free — rides any window** | **it is NOT in the mod stack.** `C:\Program Files (x86)\Steam\steamapps\common\RimWorld\BridgeTools\`, loaded by the bridge, not by RimWorld's mod loader ⇒ it cannot change what the game does and **consumes no attribution** |

⇒ **"New assembly ⇒ solo load" applies to MOD assemblies, not to every DLL we ship.**
The test is *does the game's mod loader read it* — BridgeTools fails that test, so it
is deploy-and-forget. ⚠️ Both writes **fail `OSError 22` while the game runs** (loaded
and locked); the refusal is safe and cannot truncate.

**What the new bridge DLL buys, and it is worth taking the moment it is possible:**
`TicksGameSafe()` fixes `ticksGame = Find.TickManager?.TicksGame ?? -1` across all 25
sites — `?.` guarded the RESULT while the getter dereferenced `Current.Game` and threw
first, so **every tool NRE'd at the main menu, in response construction, after the
lookup had already succeeded.** Fixing it makes **def reads possible with no game
loaded**, which is a class of check we have been paying map prices for. Measured live
by BRIDGE, not read off IL.

## ✅ L4 / O12 — EVIDENCE PHASE CLOSED. Chain confirmed live, frame is sharper than recorded.

Write-up appended to `D:\Luke\dev\Rimworld\observed\2026-08-14_O12_har_pawngen_nre.md`.
2nd same-def droid NRE'd as predicted. **Attribution airtight: `GeneratePawnRelations`
was 0 in the log before any spawn and 9 after**, with the two deliberate spawns the only
generation events between — a positive observation, not an absence argument.

🔴 **The throw is `AlienRace.HarmonyPatches.GenerationChanceGenderless` (HarmonyPatches.cs:2669),
inside the weight selector iterating pawns that ALREADY EXIST.** ⇒ the pawn whose
`Pawn_RelationsTracker` is missing is **`current`, the previously-spawned droid** — not
the one being generated. That is why spawn #1 is always clean: empty collection, nothing
dereferenced. ⇒ **a fix at the generation site alone would not cover `current`; route 2
would, because it fixes per-pawn construction.** Bug scales with population — a
RogueDroids raid is precisely the trigger shape.

**Still blocked on the owner's route choice. No seat should read a preference into it.**

## ✅ O11 CLOSED — on the LOG, not on the name sample. The 135 is the wrong denominator.

**Closed by:** `Player.log` holds exactly **5** `Failed to find a node with the given
xpath` lines and **all 5 are other mods'** (Vanilla Mining Outpost, Biomes! Caverns,
Intimacy - Gender Works ×3); **zero name `Buzzer`, `DV_Namer` or `rulePack`.** The patch
is `PatchOperationFindMod("Det's Xenotypes - Buzzers")` → `Sequence` → two
`PatchOperationReplace`; a `Replace` matching nothing logs that line and aborts the
sequence. The mod is present (`det.buzzers`, `DV_OutlanderRoughBuzzer` rolled) ⇒ FindMod
matched ⇒ **both Replaces matched. Deterministic.**

🔴 **NOT closed by "zero doubled apostrophes across 135 generated names" — that is the
wrong population and it nearly became the record.** Pre-fix the symbol had two
alternatives, **neither empty**: `maybeApostrophe(p=3)->'` (w3) and `maybeApostrophe->''`
(w1). So unpatched, every Buzzer name carries an apostrophe and ~25% carry a doubled one.
BRIDGE's own data shows **exactly one Buzzer name in the set has an apostrophe at all**
(`Ji'rocrak`; `Pob'Zoyom` is Saurid, a different namer) ⇒ the informative n is **≈1**, and
**P(zero `''` | unpatched, n=1) = 0.75.** A broken build had a 3-in-4 chance of producing
that exact observation.

⇒ **Threshold met, stop here.** A doubled apostrophe is cosmetic; the campaign world will
generate more names for free if anyone ever wants a bigger sample. **Do not reopen.**

---

## ⭐ FROM CREATE, 2026-08-14 — the Jawa ideoligion is loadable NOW. Owner review item.

**File, on disk, ready:**
`C:\Users\Mandrake\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Ideos\The Salvation (CREATE).rid`

⚠️ **The owner's original `The Salvation.rid` is UNTOUCHED and sits beside it.** Both
appear in the ideo browser; the owner compares them there. Do not delete either.

**Not a mod, not a deploy, not yours to enable.** A `.rid` lives in AppData, not under
`common\RimWorld\`, so it needed no deploy window and it changes nothing about the mod
list. ⇒ **No ModsConfig action, no load-order action.** This entry is here so the round
knows the artifact exists.

**Click path:** ideo browser → load ideoligion → *The Salvation* (the one marked CREATE).

**What to look at, in order of what would actually be wrong:**
1. **Does it load at all** — 103 precepts, 6 of them hand-added. A rejected precept is the
   realistic failure and it will say so on load.
2. **The description** — the nine gods are written into it (~2.3 KB). It should render as
   scripture, not as a wall. If it is unreadably long in the panel, that is a real finding.
3. **The six added precepts show a position** — barracks · lighting · combat in darkness ·
   combat prowess · weapons (noble *Ranged* / despised *Melee*) · apparel desire
   (`OuterRim_DesertHood`).
4. **One relic, not three** — "The Founding Ion Blaster".

**Built by** `python3 src/RimMandrake/Utils/build_salvation_rid.py --check|--write`,
which never rewrites the source and asserts IDs stay unique with no dangling
`Precept_<ID>`. Re-runs are byte-identical.

🔴 **STILL OPEN, and it is the owner's call, not OPS's:** whether `Nomad`/`Tunneler`
join the meme set. The owner asked for the nomadism trigger to be measured first —
specifically whether the penalty counts *settlement age* (a gravship jump would reset it)
or *owning a base at all* (it would not). **Do not adopt either meme on anyone's say-so
until that lands.**
