## disposition — 2026-09-26, FOUNDRY

Triaged all 5 named subjects (floodedcanyon 53, webwork 30, thesump 14, contagion 13,
therot 13) by reloading each `proof_<biome>` tier standalone and capturing the FULL
Player.log — `results.tsv` only ever had counts, never the actual error text, so a real
triage needed a fresh reload per subject. Logs: `Transient/biome_load_proof/<biome>_full.log`.

### NOT BUGS (3 of 5), confirmed by direct evidence

- **floodedcanyon** (53 distinct / 102 lines): all from `RM_LiquidProperties`' own
  self-authored authoring-lint validator, which explicitly logs "not a hard error" in
  its own message text. Working as intended.
- **thesump** (13): caused entirely by 3 files FOUNDRY itself HELD from deployment
  2026-09-25/26 ("no art yet") — `RM_SumpFauna.xml`/`RM_SumpFlora.xml`/
  `RM_SumpFloraItems.xml`. The biome's `wildAnimals`/`wildPlants` rows correctly can't
  resolve them under a minimal tier missing those held files. Expected mid-hold state,
  not a defect. Left held.
- **contagion** (13): `RM_Contagion.xml`'s own header comment already discloses this
  explicitly ("NOT donor-free... not this build's scope to fix") — hard AB_/GU_ donor
  refs with no MayRequire, inherited verbatim from the frozen RUT twin. Already known
  and disclosed; out of scope here.

### REAL BUGS FOUND AND FIXED (2 of 5)

**therot** (13): header comment CLAIMED "13 AB_ donor rows... MayRequire'd on
sarg.alphabiomes where the def dump needs it" but none of the 13 `wildPlants` rows
actually carried the attribute. Added `MayRequire="sarg.alphabiomes"` to all 13
(AB_Bryolux, AB_Glowstool, AB_Agarilux, AB_GiantAgarilux, AB_GlowingAgarilux,
AB_LilacBeacon, AB_WitchesOyster, AB_RecurvedStropharia, AB_ArbuscularMycorrhiza,
AB_SlimyPholiota, AB_AgaricusDomeCap, AB_DribblingCap, AB_AgariluxPrime). Reloaded
standalone: 0 cfg errors, 0 xref errors — clean.

**webwork** (30, 9cfg/23xref on the first fresh reload): root cause was NOT the 5
originally-visible errors but a massive DEPLOY DRIFT — the deployed mod was missing 13
repo-only files including an entire creature (RM_Ollathrix + egg + textures), a spit
weapon, nest content, and had a stale DLL/About.xml/BiomeDef. Deployed the drift (18
files), which surfaced the REAL pre-existing bugs in that newly-shipped content:

- `RM_WebworkFlora.xml`: ALL 15 plant ThingDefs threw
  `Exception parsing RimWorld.PlantPurpose from "None"` (only Food/Health/Beauty/Misc
  are valid members — "None" was never one), so the WHOLE FILE failed to load, which is
  why 16 "missing ThingDef" wildPlants cross-refs appeared even though the plants are
  correctly authored in-mod. Removed the 15 invalid `<purpose>None</purpose>` lines.
- `RM_Quarrok`'s ThingDef carried
  `<modExtensions><li Class="RimMandrake.CreatureBehaviors.RM_ChewAnchorsConsumerExtension" /></modExtensions>`
  referencing a real, correctly-namespaced, already-csproj-included class — but the
  DEPLOYED `CreatureBehaviors.dll` was stale (never rebuilt after that file was added),
  so the type genuinely didn't exist in the loaded assembly, throwing an exception that
  aborted the ENTIRE `RM_Quarrok` ThingDef parse (explaining "no race" + "ThingDef not
  found" cascading from one root cause). Rebuilt `RM_CreatureBehaviors.csproj` via
  `dotnet.exe` (Release), 0 errors, deployed.
- `RM_Quarrok` also had `<butcherProducts>` nested INSIDE `<race>` (RaceProperties has
  no such field) instead of as a ThingDef-level sibling — moved it out.
- `RM_Ollathrix` ThingDef carried an invalid `<labelPlural>` (that field is on
  PawnKindDef, not ThingDef) — removed; its `CompProperties_CanBeDormant` needed the
  ThingDef's own `<receivesSignals>true</receivesSignals>` — added.
- `RM_OllathrixEgg`'s `CompRottable` needs `tickerType` Rare/Normal but the ThingDef
  (ParentName=ResourceBase) never set one (defaults to Never) — added
  `<tickerType>Normal</tickerType>`.
- `RM_Fellome` and webwork's own copy of `RM_TavroskLiquor` used a nonexistent
  `Pawn_Melee_SmallBash_*` sound triad (typo — every sibling creature in the same file
  correctly uses `Pawn_Melee_SmallScratch_*`) — fixed both, and the same typo in
  TheSump's held `RM_SumpFauna.xml` (not yet deployed, but now correct for when it is).

Reloaded standalone after each fix wave; final state: 0 cfg errors, 2 xref lines
remaining — both `Pawn_Insect_Ambient` (a pre-existing, repo-wide convention already
shipped unguarded in FeverWood/Greentide/etc, non-fatal "using undefined sound instead",
genuinely out of scope for a single-biome triage).

A late unrelated "Caught exception while loading play data" self-recovery on the final
verification run reset ModsConfig to 6 mods — confirmed via `modlist_swap`'s own
diagnostic as RimWorld's own known play-data-load safety net, NOT a def-load/config-error
symptom (def loading — where cfg/xref checks happen — completes before that phase, and
the captured log already showed the clean cfg=0/xref=2 result before the later crash).
Owner's 630-mod list restored and verified (md5 4cbcbf186303b966fd46f973bfbcea6e).

### Remaining known gaps NOT fixed here (out of scope for a triage pass)

- `RM_Cravvet`/`RM_Vennick`/`RM_Ollathrix`: tool `linkedBodyPartsGroup` "Teeth" doesn't
  exist on their assigned bodies (TurtleLike/BeetleLike/BeetleLikeWithClaw) — needs
  checking the actual BodyDef part-group names, a real fix but needs body-def
  cross-referencing, not a one-line change.
- `RM_Fellome`/`RM_TavroskLiquor`: Nutrition==0 with a non-NeverForNutrition
  preferability — needs a content decision (give it real nutrition, or fix
  preferability), not guessed here.
- Missing BodyPartGroupDef `HindlegsFrontClaws` for a kick tool somewhere in webwork's
  content.
- `Pawn_Insect_Ambient` (repo-wide, pre-existing, non-fatal) — a real cleanup but spans
  many mods beyond this item's 5 named subjects.
