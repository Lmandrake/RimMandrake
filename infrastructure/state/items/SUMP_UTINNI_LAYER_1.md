# SUMP_UTINNI_LAYER_1 — the Sump's campaign layer

The Utinni-tier patches over `RM_TheSump`, from the 2026-09-24 sitting rulings.
Additive only (Q11/Q11a): the free mod is whole without any of this.

## spec

1. **Sumpgas rename**: the campaign renames the green gas to **Sumpgas** — owner,
   typed, verbatim: *"But the utinni layer should rename it to our own form of
   gas. Let's call it Sumpgas."* (Label/description patch over the gas the RM mod
   uses — `SUMP_GASLIGHT_1` builds the chemistry.)
2. **The holy act**: flame statuary as worship of the evil sun god — an ideoligion
   patch giving the statues ritual/holy meaning (owner: *"That could be a holy
   act to the evil sun god."* Split ruled by card: statues RM-tier secular,
   worship campaign-tier).
3. **`RSW_Hssiss`**: the biome's one seated canon beast (ruled 2026-09-10) rides
   the new `UtinniPatches/Patches/WildAnimals_Sump.xml` onto `RM_TheSump` at
   0.18 — per the fauna roster §7/§8 and `THESUMP_RM_MOD_BUILD_1` §3.
4. Campaign labels (the Junker stations fiction, faction hooks) stay with
   `SUMP_INHABITED_NOTES_1` — not this item.

## verify

With the Utinni layer active: the gas reads Sumpgas everywhere player-facing; the
flame statue carries its ideoligion meaning; the Hssiss spawns in the Sump. With
it inactive: none of the above, and the RM mod is unaffected.

## criteria

The campaign deepens the Sump without the Sump needing the campaign.

## build status — FOUNDRY, 2026-09-26, all three pieces satisfied, needs live proof on piece 2

**Pieces 1 and 3 were already done before this pass started** — found by searching first,
per the standing "check for existing work before building" law:

- **§1 Sumpgas rename**: `SUMP_GASLIGHT_1` (closed same sitting, 2026-09-24) built the gas
  resource directly as `RUT_Sumpgas.xml` (UtinniPatches) with `<label>Sumpgas</label>` from
  its own creation — the owner's exact naming ruling is quoted verbatim in that file's own
  header. There is no separate "generic RM-tier gas" needing a rename patch: the owner's
  ruling put the whole resource at Utinni tier by his own explicit word, not a relabel over
  an RM-tier original. Nothing to build.
- **§3 Hssiss patch**: `src/RimUtinni/UtinniPatches/Patches/WildAnimals_Sump.xml` already
  exists (new file, 2026-09-25, built during `THESUMP_RM_MOD_BUILD_1`), wiring `RSW_Hssiss`
  onto `RM_TheSump`'s wildAnimals at 0.18 behind `MayRequire="mandrake.rsw.swbestiary"`,
  exactly per this item's own §3. Re-verified this pass with `validate_patch.py --live --defs`
  against the fresh `2026-09-26T01-08-12Z` dump: the two ERRORs it reports ("RM_TheSump does
  not exist in the LIVE game") are because `mandrake.rm.thesump` is not yet an ACTIVE mod in
  the live 628-mod `ModsConfig.xml` — a known, already-documented state
  (`THESUMP_RM_MOD_BUILD_1`'s own build note: "TheSump is not currently enabled in
  ModsConfig — enabling it ... is a separate call, not this item's"), not a defect this file
  or this item introduced.

**§2 the holy act — built this pass, new content:**

Investigated the mechanism before writing any XML (`rimworld-ideoligion` skill +
`HistoryEventDefOf.cs`/`PreceptComp_SelfTookMemoryThought.cs`/`CompUsable.cs`/
`CompUseEffect.cs`/`MemeDef.cs` read in full from the decompiled reference,
`/mnt/d/Luke/dev/reference/rimworld-decompiled`): a precept can only grant a thought off a
`HistoryEventDef`, `PreceptComp_SelfTookMemoryThought` filters on the event def alone (no
per-Thing filter), and no vanilla "admired art" event exists in this game version to
reuse — so a scoped, dedicated event was required, fired from a small new comp, not a guess
at an existing one.

Deity name resolved from `design/Jawa/divine_satiation_engine.md` §8 (the Pantheon of
record, names LOCKED): **Sh'kaar the All-Searing**, "the evil sun ... an EVIL god" — not
invented here.

Built, all in `mandrake.rut.patches` (UtinniPatches):
- `Defs/HistoryEventDefs/RUT_HolyFlameEvents.xml` — `RUT_PerformedHolyFlameAct`.
- `Defs/IssueDefs/RUT_HolyFlameIssue.xml` — new `RUT_HolyFlame` issue (no existing issue fit).
- `Defs/ThoughtDefs/RUT_HolyFlameThoughts.xml` — `RUT_PerformedHolyFlameAct` memory, +6 mood.
- `Defs/PreceptDefs/RUT_HolyFlamePrecepts.xml` — `RUT_HolyFlame_Revered`
  (`PreceptComp_SelfTookMemoryThought`).
- `Defs/JobDefs/RUT_HolyFlameJobs.xml` — `RUT_PerformHolyFlameAct`, `driverClass
  JobDriver_UseItem` (vanilla's own generic Use driver — no custom JobDriver written).
- `Source/RUT_CompUseEffect_HolyFlame.cs` — `RUT_CompProperties_HolyFlameEffect` /
  `RUT_CompUseEffect_HolyFlame`, fires the event from `DoEffect`, `GetNamedSilentFail`
  guarded so it degrades to a no-op rather than a hard error if Ideology is ever absent.
- `Patches/FlameStatuary_HolyAct.xml` — adds `CompProperties_Usable` (float-menu "perform
  the sun-rite") + the new effect comp onto `RM_FlameStatuary` (EnvironmentalHazards,
  SUMP_GASLIGHT_1's RM-tier secular statue — confirmed its own `<comps>` is fully explicit,
  not `ParentName`-inherited, so `PatchOperationAdd` is safe). Gated by a new Mod Settings
  toggle (`holyFlameActEnabled`, default on) via the existing `PatchOperationSettingGate`.
- `Patches/HolyFlame_RitualistWiring.xml` — appends `RUT_HolyFlame_Revered` as a new
  `requireOne` group on the vanilla Anomaly meme `Ritualist` (impact 2). **Necessary, not
  decorative**: `MemeDef.requireOne` is a `List<List<PreceptDef>>` — a precept nowhere in any
  meme's `requireOne` can never be selected by any ideoligion, player or NPC. Confirmed the
  xpath actually matches live (`Anomaly: Memes_Misc.xml`, 1 hit).
- `UtinniPatchesSettings.cs`/`PatchOperationSettingGate.cs` — the new toggle + its
  named-switch case.

**Deliberately NOT done, flagged rather than guessed:**
- `RUT_HolyFlame_Revered` is reachable by any ideoligion with the `Ritualist` meme, but is
  **not** retroactively added to the campaign's own saved ideoligion ("The Salvation",
  `src/Jawa/ideoligion/The Salvation.rid`). A `.rid` is Scribe output baked at world
  creation; adding a precept to an already-baked live `Ideo` needs the in-game dev-mode ideo
  editor — a live, manual, one-time action, not an offline XML patch. Owed as a live-session
  follow-up, not a new item (small enough to fold into any future Sump/statue live pass).
- `RUT_Idol_Shkaar_Grand` (the eventual flame idol from `STATUE_ART_EXPANSION_1`, still
  `proposed`, unbuilt) is a SEPARATE, much larger item (two new mods, 16 defs, an art
  pipeline). `design/RimMandrake/statue_mods_spec.md` §2.5 says the holy-act precept should
  eventually target that def instead of `RM_FlameStatuary` once it ships — this pass targets
  what actually exists today per this item's own (older, still-valid) spec text, and the
  retarget is that item's own build-order step 3, not invented or guessed at here.

**Validated offline**: `dotnet build RimMandrake.Utinni.UtinniPatches.csproj -c Release` — 0
warnings/errors (1 new .cs file, csproj entry, `.dll`+`.srchash` regenerated).
`validate_patch.py --live --defs` against the live 628-mod set (Data+Workshop+Mods) plus the
fresh `2026-09-26T01-08-12Z` dump: all 7 new/touched files 0 errors/0 warnings, xpath hits
confirmed live for both the `RM_FlameStatuary` comps target (1 match, isolated test) and the
`Ritualist` requireOne target (1 match, `Anomaly: Memes_Misc.xml`).

**What a live proof needs** (no bridge access this pass): confirm "perform the sun-rite"
appears in the float menu on a built `RM_FlameStatuary` with a colonist selected; confirm the
job completes and `RUT_PerformedHolyFlameAct` fires (only observable via an ideoligion that
actually holds `RUT_HolyFlame_Revered`, so this also needs a test ideo built with the
`Ritualist` meme choosing this precept); confirm the +6 mood memory appears; confirm the Mod
Settings toggle actually gates the comp addition (off → no float-menu option, same behavior
as before this pass).
