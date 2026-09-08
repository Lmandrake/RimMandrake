## spec
Thin when filed — no spec/verify/criteria in the queue entry itself. Specced
here from `design/Jawa/droids/DROID_UNIFIED_FRAMEWORK_DESIGN.md` §5 packet C6
(inputs: ruling 2, "Hutt settlement/dungeon work"; outputs: "captive droids as
a site feature: rescue (they join, bolted or resentful) or purchase"; verify:
"site spawns them; both outcomes tested"; after: C1, `done`).

## The site-generation question, investigated first (this decided the whole scope)
`design/Jawa/templates/hutt_holding_pens.lua` is a real, compiled Lua template
(`src/RimMandrake/Inhabited/Templates/hutt_holding_pens.txt`) and IS registered
by label ("holding pens") in
`GenStep_ComposeSettlementDistrict.TemplateFiles` — so the template itself is
not dormant/unused content. But two things stop it (or anything in it) from
ever reaching a real map today:

1. **Only `districts[0]` ever composes.** `GenStep_ComposeSettlementDistrict`'s
   own doc comment: "v1 SCOPE... only `districts[0]` is composed" — a "stretch
   goal, not done here." Gorga the Immense's Palace
   (`SettlementManifestDefs_GorgaPalace.xml`) lists `["palace hall", "cistern
   court", "holding pens", "spicehouse"]` in that order — "holding pens" is
   `districts[2]`, never composed. `DISTRICT_TEMPLATE_LIBRARY_1.md` (still
   `doing`) already records this as its own unbuilt stretch goal.
2. **No `InhabitedCastDef` exists for the Hutt Cartel at all.**
   `SettlementManifestDefs_GorgaPalace.xml`'s own header: "no InhabitedCastDef
   exists for any Cartel place yet." `WorldObject_Inhabited.Cast` reads
   `castDef ?? placeDef?.defaultCast` — never `SettlementManifestDef.castSlots`
   — and `RM_InhabitedPlace_Palace` (`Places_Inhabited.xml`) has no
   `defaultCast`. Read `CastAssignmentSlot`'s own class doc
   (`SettlementManifestDef.cs`): "SCHEMA ONLY... this slot only records which
   role a district wants one for" — the "guard"/"debtor" roles the manifest
   already names against "holding pens" are proven, by the engine code, never
   read by anything. **Gorga's Palace spawns zero cast pawns of any kind
   today**, in any district.

So "the Hutt settlement/dungeon work" §5 points at is real geometry with no
real occupants — not a site a droid packet should try to finish wiring
end-to-end (multi-district spatial composition + a whole faction's first
`InhabitedCastDef`, neither owned by this program). `DROID_FACTION_LOADOUTS_1`
(C1, `done`) already reached the same conclusion and recorded "Hutt captives in
the torture chambers" as its own deferred line pointing at this item — so this
gap was expected, not a surprise this packet is inventing to dodge scope.
No `HUTT_SITE_*`/`DUNGEON_*` item exists that already owns finishing the site
(checked `infrastructure/state/items/` and `dungeons_arc_spec.md` — the latter
is the unrelated Assailant/Forsaken vault arc). **Not filing a fresh
prerequisite item**: the exact plug-in point is recorded below, and whoever
next touches `DISTRICT_TEMPLATE_LIBRARY_1`'s multi-district stretch goal or
authors the Hutt Cartel's first `InhabitedCastDef` is the natural owner.

## Scoped to: the droid-specific content, ready to plug in
Two mechanisms, both real and independently playable without the site:

**Purchase** — `StockGenerator_DWHuttCaptives : StockGenerator_DWDroids`
(`Source/Droidworks/StockGenerator_DWHuttCaptives.cs`), reusing
`StockGenerator_DWDroids`'s `GenerateThings`/`HandlesThingDef` rather than
duplicating the `PawnGenerationRequest` plumbing (DROID_FACTION_LOADOUTS_1's
own hard-won lesson: no third-party `StockGenerator` class survives this
program's retirement waves or is silently inert — ours already doesn't). The
only new behaviour: every generated pawn is stamped via
`DroidworksBoltUtility.ApplyCaptiveBolt` — a new third application route
(`DroidworksBoltUtility.cs`) alongside the existing two
(`Recipe_InstallRestrainingBolt`, `JobDriver_DWClampBolt`), for a pawn that
arrives already bolted rather than being bolted in front of the player. It
installs `RSW_DW_RestrainingBolt` if missing, seeds `RSW_DW_BoltResentment`
through the existing `EnsureBoltResentment` gate, then raises resentment
severity to at least a random roll in `resentmentSeverityRange` (default
0.2–0.8, **FOUNDRY's own flavor number for "how long a debtor has been held" —
no owner ruling exists for this**) — "at least" because
`HediffComp_DWBoltResentment`'s whole contract is that resentment never
decays, so this only ever raises a floor. Wired live: `RUT_Caravan_
HuttCartel_Captives` (`RUT_HuttCartel_Captives.xml`), added to
`Jawa_HuttCartel`'s `caravanTraderKinds` (`JawaHuttCartel.xml`) — a real
purchase route TODAY via caravan trade, no map/site dependency. 800–2000
silver on the trader, 1–3 captives per visit from four non-combat colonist-
tier kinds already MEASURED live in `RUT_TradeMootDroids.xml`'s own stock
(`RSW_DW_KotORDroidColonist_{GE3LD,GE3PD,T3UD}`,
`RSW_DW_OuterRim_ProtocolDroid`) — a debtor droid is a household/labour/
protocol unit that displeased its master, not war machinery; Hutt's existing
combat guards are untouched.

**Rescue** — `RSW_DW_LiberateHuttCaptive`
(`RecipeDefs_Droidworks.xml` / `Recipe_LiberateHuttCaptive.cs`), wired onto
every droid race via `DW_Race_Base`'s `<recipes>` (`Races_Base.xml`), same as
the other three Droidworks recipes. Gate: prisoner AND already carrying
`RSW_DW_RestrainingBolt` (custom `GetPartsToApplyOn`, same shape as
`Recipe_RemoveRestrainingBolt`'s own — no single vanilla field expresses that
pair). `ApplyOnPawn` does a straight `pawn.SetFaction(Faction.OfPlayer)`,
shaped after vanilla `Recipe_GhoulInfusion` (confirmed live precedent for a
surgery-style bill converting allegiance outright, no resistance/will grind —
`Pawn.SetFaction` already clears guest status and surgery bills internally).
**Deliberately does not touch the bolt or resentment at all** — "rescue" (cut
free of captivity) and "remove the bolt" (cut free of the Hutts' hold on its
mind) are the two different acts ruling 2 names, and only the second is
`Recipe_RemoveRestrainingBolt`, left completely untouched, rebellion-on-
removal check (`DROIDWORKS_BOLT_PAYOFF_1`) fully intact if the player chooses
it afterward. This is the "bolted or resentful" outcome the packet's outputs
line names — both, simultaneously, by construction.

**The exact plug-in point**, for whoever finishes the site: give "holding
pens"'s `debtor` cast role (already named in the manifest, currently inert
schema) an `InhabitedCastDef` whose roles use these same pawn kinds, and route
their spawn through `DroidworksBoltUtility.ApplyCaptiveBolt` the same way
`StockGenerator_DWHuttCaptives` does. Nothing else needs to change.

## A correction recorded against a same-session sibling item
`DROIDWORKS_HEADS_BRAINS_SPIKES_1` (B3, `done`, this session) keyed its Hutt
data-spike to `OuterRim_BinaryStarRaiders`, asserting "no dedicated Hutt Cartel
FactionDef exists anywhere in the stack." **That assertion is wrong**:
`Jawa_HuttCartel` (`src/RimUtinni/UtinniPatches/Defs/FactionDefs/
JawaHuttCartel.xml`, authored 2026-08-14) is our own real, loadable
`FactionDef` — `SettlementManifestDefs_GorgaPalace.xml`'s own
`factionDefName`, with its own settlements, ideo, and pawnGroupMakers already
live. This item's captives are keyed to `Jawa_HuttCartel`, correctly. Not
re-opening or fixing B3 here (out of scope for C6, and it is already `done`
with its own recorded assumption) — flagged so nobody re-derives the wrong
convention from it a second time.

## Offline verification (bridge held by a concurrent FOUNDRY session, live check owed but not done)
- `python3 -c "import xml.etree.ElementTree as ET; ET.parse(...)"`: clean on
  all four touched/new XML files.
- `dotnet build Droidworks.csproj -c Release`: **0 errors, 0 warnings.**
- `deploy_custom_mods.py --mod Droidworks` (plan only, not applied): shows
  exactly my three touched files as drift (`Assemblies/Droidworks.dll`,
  `Defs/Races_Base.xml`, `Defs/RecipeDefs/RecipeDefs_Droidworks.xml`) plus one
  file NOT mine (`Patches/BTD_DistressCall_Repoint.xml`, another window's
  in-flight C7 work) — **not applied**, per Charter: never deploy over
  another window's uncommitted files.
- `deploy_custom_mods.py --mod UtinniPatches` (plan only): shows my two files
  as drift, and reports `mandrake.rut.patches` **not enabled in ModsConfig** —
  this content cannot be live-tested without a mod-list change regardless of
  bridge state.
- `rimflow bridge who`: held by a concurrent FOUNDRY session (idle 7 min, well
  under the 45-min staleness bar) for C4 — not stale, not force-taken per this
  item's own instructions ("if held, don't wait").

**Not proven live**: a captive spawning bolted+resentful from the trader stock,
and the liberate recipe actually flipping faction on a live pawn. Both are
genuinely new C# paths (`StockGenerator_DWHuttCaptives`,
`Recipe_LiberateHuttCaptive`) that have never been observed running — a live
check is owed per FOUNDRY doctrine, just not obtainable this pass. Left
`doing`, not closed.

## Assumptions recorded (Charter: "record what you assumed")
1. Purchased/rescued captives arrive **still bolted** (not a clean unbolted
   purchase) — FOUNDRY's own call: it reuses the existing resentment/rebellion
   payoff mechanism instead of a no-op transaction, and is the more
   thematically apt reading of "torture chambers" ("you bought/found a debtor
   as-is; earning its trust by cutting the bolt is a separate choice").
2. `resentmentSeverityRange` default 0.2–0.8 (spanning
   `Recipe_RemoveRestrainingBolt.RebellionThreshold`, 0.6) is FOUNDRY's own
   flavor number for "how long a debtor has been held" — no owner ruling
   exists for this.
3. Pawn-kind selection (four non-combat, colonist-tier Droidworks kinds) is
   FOUNDRY's own narrative judgment call, not an owner ruling.
4. `RSW_DW_LiberateHuttCaptive` gates on `RSW_DW_Research_Bolting` (same
   prerequisite as install/remove) rather than being free — consistent with
   the existing bolt-recipe family, not separately ruled.
