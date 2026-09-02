# GRAFFITI_FRAMEWORK_BUILD_1

## spec

`design/Jawa/graffiti_spec.md` — full design, all four owner rulings made
(§7): supersede `Mlie.GraffitiMod` now (absorb the spree mechanic,
retire it from the mod list at build time), taunt-funneling ships in
v1, cant renders as a faint scrawl to outsiders. Two mods:
`mandrake.rm.graffiti` (engine: `RM_GraffitiDef` class, jobs, viewer
comp, mural/jest/taunt/cant concepts) + `mandrake.rut.marks` (content:
nine sacred marks, cant glyphs, taunt theology — folds in the existing
`SacredGraffiti`/`mandrake.rm.sacredgraffiti` mod per the rename map).

## FOUNDRY scope decision, 2026-08-31 (owner AFK)

This is a genuinely large build: a new JobDriver/JoyGiver pair replacing
a currently-active mod's mechanic, a viewer `ThoughtWorker`, a
`RitualOutcomeEffect` subclass, a raid-AI breach-bias hook explicitly
described as **"shared with the engine's Ishko-delivers work"** — a
dependency on another system not confirmed built — and ~34 art assets
(spec §3). Larger in scope than this session's other two builds
(`GenStep_RimplacePlan`, `mandrake.rsw.beastnorm`), and its central ask
— retiring an active mod from the live 588-mod `ModsConfig.xml` — is
exactly the kind of live-stack-affecting action to not pull solo with no
owner present to confirm the timing.

**Done this pass:**
- ✅ **License check** (the item's own explicitly named gate): `Mlie.GraffitiMod`
  (workshop id `2986996933`) ships `LICENSE.md`, **MIT** — fully
  permissive. Reusing/reskinning its six vandal textures for the
  absorbed spree mechanic is legally clear; the only obligation is
  keeping the copyright notice in credits. **No blocker.**
- Confirmed `SacredGraffiti` (`mandrake.rm.sacredgraffiti`,
  `src/RimMandrake/SacredGraffiti/`) already exists with a working
  `Defs/SacredMarks.xml`, `RitualOutcomeEffects.xml`, and C#
  (`Source/SacredGraffiti.cs`) — this is real prior groundwork for the
  SACRED family (①) and the `RitualOutcomeEffect` hook (spec §2b),
  not a green field. The spec's own migration note says this mod folds
  into `mandrake.rut.marks` at execution time — it has NOT been
  renamed/folded yet.

**Not done — needs a session with room to build AND test the C#, and
the owner present for the mod-list retirement call:**
- The `RM_GraffitiDef` class, the absorbed JobDriver/JoyGiver spree
  mechanic, the viewer `ThoughtWorker` (families ②③④).
- The raid-AI breach-bias hook (family ④'s "Come And Take It") — its
  own spec text flags a dependency on "the engine's Ishko-delivers
  work" that this pass did not go verify exists.
- All ~34 art assets (spec §3).
- Retiring `Mlie.GraffitiMod` from `ModsConfig.xml` and folding
  `SacredGraffiti` into `mandrake.rut.marks`.

Left `doing`, not closed — this is a scoping/prerequisite pass, not a
shipped slice.

## 2026-08-31, second pass (FOUNDRY) — the data-layer engine piece built

Built `mandrake.rm.graffiti` (`src/RimMandrake/Graffiti/`):
`ModExtension_Graffiti` (a `DefModExtension`, not a parallel Def
hierarchy — the same idiom SWCP_Core's `ModExtension_FactionPermanentlyHostileTo`
uses, read this session while fixing `EMPIRE_WHITELIST_OVERRIDDEN_1`) with
`category` (Sacred/Mural/Jest/Taunt/Cant), `visibility`
(Public/ClanOnly per §1's Cant rule), `supportsQuality`, `hasSubject`,
`tracksMaker`, a `viewerReactionThought` seam, and a `godSatiationHook`
string field so a RUT content pack can call into `mandrake.rm.ninefold`'s
`ApplyDelta` without this engine mod hard-depending on the pantheon.
Builds clean (0 errors/warnings), deployed.

**Deliberately still just the data layer — nothing reads these fields
yet.** No JobDriver/JoyGiver, no ThoughtWorker, no raid-AI hook, no
content (ships zero marks). This is the exact vocabulary the larger
build (still not attempted solo, per the reasons above) will write
against, mirroring `mandrake.rm.ninefold`'s own `Adjust()`-with-nothing-
calling-it-yet shape.

## 2026-08-31, third pass (FOUNDRY) — owner authorized the full absorb-and-retire build

Owner: "Full authorization on 1 and 2" (restart control, and this build
including retiring `Mlie.GraffitiMod`). Built the absorbed spree
mechanic for real:

- **`RM_Graffiti_Vandal`** — the vandal mark, `ParentName="RM_BaseGraffiti"`
  (our OWN abstract parent, `thingClass` plain vanilla `Filth` — verified
  via fresh RimSage research that `CornerFiller` linking is a
  `GraphicData`/`Graphic_Linked` concern, not a `thingClass` concern, so
  no custom subclass is needed). Six texture variants are the donor
  mod's own art, copied byte-for-byte under its MIT license
  (`LICENSE-THIRD-PARTY.md`, full notice).
- **`JobDriver_PaintGraffiti`** + **`JoyGiver_PaintGraffiti`** — fresh C#
  against the real vanilla toil API (the donor mod ships no source to
  reuse — compiled-only DLL). Modeled on two verified vanilla analogs,
  not guessed: `JobDriver_RelaxAlone`'s goto-and-gain-Joy-via-
  `JoyUtility.JoyTickCheckEnd` shape, and `JobDriver_Floordrawing`'s
  `FilthMaker.TryMakeFilth`-on-completion shape. `JoyGiver_PaintGraffiti`
  scans for a nearby wall cell itself (no vanilla `RCellFinder` helper
  exists for this, confirmed absent).
- **`RM_GraffitiPaintingSpreeBreak`/`State`** + `JobGiver_GraffitiPaintingSpree`
  — the mental-break spree, same `ThinkTreeDef` shape
  (`insertTag: Humanlike_PostMentalState`) as the donor's own
  `SubTrees_Misc.xml`.
- **Caught and fixed a real dependency break before it shipped**:
  `mandrake.rm.sacredgraffiti`'s existing `RM_SacredMark_Ishko`
  inherited `ParentName="BaseGraffiti"` from the DONOR mod's own abstract
  def — retiring `Mlie.GraffitiMod` would have silently discarded the
  already-shipped Ishko mark. Repointed to `RM_BaseGraffiti`, updated
  `About.xml` deps/loadAfter, revalidated clean (0 errors, `ParentName`
  resolves against the deployed mod).
- `Mlie.GraffitiMod` removed from `ModsConfig.xml`.
- Builds clean (0 warnings, 0 errors). `validate_patch.py`: 0 errors on
  both `mandrake.rm.graffiti` (6 files) and `mandrake.rm.sacredgraffiti`
  (3 files, once the deployed `Mods/` folder is included as a `--defs`
  root — my own dev mods aren't in the Workshop-scanned path, a known
  validator blind spot, not a real defect).

**Deploy timing note**: the game was mid-restart when this landed. XML/
textures deployed clean; the assembly deploy hit the expected Windows
file-lock (`OSError [WinError 1224]`-class error, DLL memory-mapped by
the in-flight load) — this build's C# will not be live until the NEXT
restart, which I'm now authorized to trigger myself.

**Still not built**: all sacred/mural/jest/taunt/cant CONTENT beyond
the one generic vandal mark (`mandrake.rut.marks`) — owner-voice work,
not attempted here.

## 2026-09-02 (FOUNDRY) — the two remaining mechanisms built (content still owed)

Built both pieces named above as MECHANISM ONLY — no flavor text, no new
ThingDef/ThoughtDef content, both designed to be driven entirely by fields
`ModExtension_Graffiti` already carried:

- **`ThoughtWorker_ViewedGraffitiMark`** (`Source/ThoughtWorker_ViewedGraffitiMark.cs`):
  a reusable situational `ThoughtWorker`, pattern-verified against real
  vanilla `RimWorld.ThoughtWorker_PyromaniacNearFlames` (room+radius scan,
  same idiom). Scans an 8-cell radius for a mark whose
  `ModExtension_Graffiti.viewerReactionThought` points back at `def` (the
  ThoughtDef this worker instance is attached to) — so ANY future
  Sacred/Mural/Jest/Taunt reaction ThoughtDef can reuse this one class by
  setting `<thoughtClass>` to it and pointing its mark's
  `viewerReactionThought` at itself. No content ThoughtDef ships yet.
- **`BreachBiasHook`** (`Source/BreachBiasHook.cs`): Harmony postfix on
  `Verse.AI.BreachingGrid.FindBuildingToBreach()` — the real, RimSage-
  verified sole method `LordToil_AssaultColonyBreaching` calls to pick
  which building a raid breaches (a pure nearest-with-most-reachable-sides
  flood-fill, no existing scoring hook). If any live mark has
  `ModExtension_Graffiti.breachLure = true`, the postfix looks for an
  eligible breach target within its 9-cell footprint (same
  `BreachingUtility.ShouldBreachBuilding`/`IsWorthBreachingBuilding`/
  reachable-side gates the original algorithm used — never overrides
  toward a building the original would have rejected) and substitutes it
  in. Added `ModExtension_Graffiti.breachLure` (bool) for this.
- Added a `HarmonyLib`/`0Harmony.dll` reference to `Graffiti.csproj`
  (matching `FireEcologyHook.csproj`'s own pattern) — this mod's first
  Harmony patch.
- `dotnet build`: 0 warnings/0 errors. `validate_patch.py` (594-mod set,
  Data+Mods+Workshop): 0 errors/0 warnings, all 6 files.
- **Not deployed this pass**: the game is mid-restart (a sibling fork's
  WeatherSuite verification), `mandrake.rm.graffiti` is already active,
  and the assembly copy hit the expected `OSError` file-lock
  (DLL memory-mapped by the running game) — same shape as the third
  pass's own deploy-timing note. Compiled and committed, not yet copied
  into the live `Mods/` folder; ride the next game-down window.

**Still owed**: all content (sacred/mural/jest/taunt/cant text and defs,
owner-voice), the deploy once the game is down, and a live quicktest
proving both mechanisms actually fire (a colonist near a reaction mark
gains the thought; a raid with a `breachLure` mark active actually
breaches there) — cannot be tested without content defs to attach to, so
this also needs at least one placeholder mark of each kind before a live
proof is possible. Left `doing`.
