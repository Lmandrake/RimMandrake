# Waveglass rename — prose pass, 2026-09-26

Owner ruling (typed, verbatim): *"love what you made but just call it waveglass"*.
The Twilight Sea's ceiling organism is **the waveglass**; the Deepwater call it *the lid*;
what it sheds is *veil-fall*. Never "mold", never "mat". Mechanism unchanged.

## 1. Sweep (instrument + sanity probe)
Python walk over the repo (`.xml .md .json .py .cs .txt .csv .html`, skipping `.git`,
`Transient/`, `deployed/`, and another agent's worktree under `.claude/worktrees/`),
case-insensitive patterns `mold`, `mat-roof|roof-mat`, `mat-?fall`, `MoldMat`, `\bthe mats?\b`,
`\bmats?\b`. **Sanity probe:** `Twilight Sea` matched 43,601 times, so the instrument sees text.
Raw hit lines: mold 628 · mat-roof 74 · mat-fall 12 · MoldMat 4 · "the mat" 253 · bare "mat" 1022.
Filtered by hand to the Twilight ceiling; the rest were the Rot's pimmik mold, `BMT_FloorMold`,
the Scald's crowncarpet mats, "material/format", and LuminousPigment's `matSeen` (crowncarpet).

## 2. `RM_MoldMatRoof` — deliberately NOT renamed (scope change mid-pass)
The coordinator relayed a fresh owner ruling while this pass ran: the ceiling organism is
**not a plant on the floor at all** — it is "a big panel that occasionally floats down and can
be harvested", an event plus an item. `RM_MoldMatRoof` is therefore being retired and
redesigned, not renamed. Left exactly as found: the def, label and description in
`src/RimMandrake/TerminalBiomes/Defs/ThingDefs_Plants/RM_TwilightSeaFlora.xml`, that file's
header, and the `<RM_MoldMatRoof>3.0</RM_MoldMatRoof>` row plus its comment block in
`src/RimMandrake/TerminalBiomes/Defs/BiomeDefs/RM_TwilightSea.xml`. References the sweep
found (all left for the redesign to retire together): those two files (4 lines), the artpipe
art-list row `twilightsea_moldmatroof` in
`infrastructure/artpipe/art_lists/terminal_seas_floor_dressing.csv`, the failed job
`infrastructure/artpipe/failed/twilightsea_moldmatroof.{json,manifest.json}` and its rendered
`_artsrc/twilightsea_moldmatroof/twilightsea_moldmatroof.png` (a felted mold-mat plant sprite
— wrong subject now on two counts; not deleted, generated art is not disposable).

## 3. Files changed
_(pending)_

## 4. Places kept close to the old shape, and why
_(pending)_

## 5. Not on the brief's list
_(pending)_

## 6. Mechanical defects seen and left alone
_(pending)_

## 7. Validation and commits
_(pending)_
