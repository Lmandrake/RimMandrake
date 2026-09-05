## spec
Filed by BENCH 2026-09-04: The Rites shipped with zero gating despite the
owner's ruling that they are "revealed-not-bought" — a 5-row locked tree,
the reveal mechanism being Antiquities. `RUT_Rites_Research.xml` carried no
`hiddenPrerequisites`/`discoveryPrerequisites` (measured: grep 0), so as
shipped every row was an ordinary buyable research project.

Open design question the item flagged: vanilla `hiddenPrerequisites` gates
`CanStartNow` (starting the project) but does NOT hide the row from the
research tree UI — verified against the shipped source before asking
(`RimWorld/MainTabWindow_Research.cs`'s `VisibleResearchProjects` filters
only on `hideWhen`/`IsCurrentProject`, never on prerequisites of any kind).
So "revealed" could mean either visible-locked (cheap, vanilla-native) or
truly hidden (needs a Harmony patch on that filter). Asked the owner
directly since he was active in-session: **ruled visible-locked** — ship
with plain `hiddenPrerequisites`, no new C#.

## what changed
`src/RimUtinni/Rites/Defs/RUT_Rites_Research.xml`: added
`<hiddenPrerequisites>` to the four tiers past the Scrap Shrine, matching
design/Jawa/antiquities_design.md section 2 exactly:
- `RUT_Rites_ConduitChoir` → `RUT_Antiq_Language`
- `RUT_Rites_GodSpeakerArray` → `RUT_Antiq_Religion`
- `RUT_Rites_HullLiturgy` → `RUT_Antiq_Culture`
- `RUT_Rites_GodsSpeakBack` → `RUT_Antiq_Voice`

`src/RimUtinni/Rites/About/About.xml`: added `modDependencies`/`loadAfter`
on `mandrake.rut.antiquities` (these hiddenPrerequisites defNames now come
from that mod — a hard cross-mod reference between two of our own mods, not
a patch on someone else's, so no `PatchOperationConditional` guard is
needed) and corrected the stale "until that build lands these rows are
researchable like any other" description text now that
ANTIQUITIES_TREE_BUILD_1 slice 1 has actually landed.

Also added `mandrake.rut.antiquities` to the live `ModsConfig.xml` and
`ModsConfig.FULL.LATEST.xml` — Rites is already scheduled to activate on
the next full-list load (`COLD_LOAD_RUN_SHEET_3`), and it would throw
`Could not resolve cross-reference` errors for every `RUT_Antiq_*` name
without Antiquities also active. (Found already present with a 595-mod
count when I went to add it — someone else had already added it live.)

## verify
- XML well-formedness: both edited files parse clean.
- Deployed via `deploy_custom_mods.py --mod Rites --apply` — in sync.
- `Antiquities`'s DLL shows drift against the deployed copy but the game is
  currently UP (owner active) — **not forced**, since assembly writes are
  refused while RimWorld holds the file and forcing a restart of the
  owner's live session for this would be exactly the kind of collision
  tonight already had two of. Owed at the next game-down window.
- Live visual confirmation (a Rites row past Scrap Shrine actually renders
  greyed/locked in the research tab until its Antiquities stage finishes)
  NOT yet run — needs the next full-list load, already tracked in
  `COLD_LOAD_RUN_SHEET_3`. Add this as a decision string there: expect
  `RUT_Rites_ConduitChoir` greyed at game start (LANGUAGE unstarted), and
  expect it to unlock the moment `RUT_Antiq_Language.IsFinished` (read via
  `jawa/research_progress`).

## criteria
- Four Rites tiers carry the exact hiddenPrerequisites mapping from the
  design doc; Scrap Shrine itself stays ungated (it's the always-available
  first rite).
- No `PatchOperationConditional`/silent-no-op risk — this is direct XML on
  our own defs, not a patch.
- Visible-locked chosen deliberately (owner ruling), not a fallback because
  hiding was too hard — recorded so a future reviewer doesn't "fix" it.
