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
calling-it-yet shape. Left `doing`.
