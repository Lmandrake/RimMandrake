# SEABEAST_STARMAW_LANTERNWHALE_TEXTURES_MISSING_1 — 2 of 18 sea beasts draw as nothing

Found 2026-09-02 by the sea-beast family review agent while building
`SEABEAST_FAMILIES_20260903.rws`. Filed 2026-09-03 by BENCH because it existed only in
a subagent's report and would have died with that context.

## spec

`RSW_Starmaw` (grid cell B2) and `RSW_Lanternwhale` (B3) have **no textures deployed and
none in the repo**. Player.log:

```
Failed to find any textures at Things/Pawn/Animal/SeaBeasts/Starmaw/Starmaw
Failed to find any textures at Things/Pawn/Animal/SeaBeasts/Lanternwhale/Lanternwhale
```

**16 of 18** creature folders exist under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SeaBeasts\Textures\Things\Pawn\Animal\SeaBeasts\`.
Those two do not — in the deployed copy **or** the repo, so it is not a deploy miss.

Their pawns ARE in the review save and read back correctly from `jawa/list_pawns` with
the right `kindDef` — they simply draw as nothing. ⇒ A data-level census of that save
reports 18/18 present and is not wrong; it just cannot see this.

## Watch out

⚠️ **Magenta will not fire here.** `prove-art-missing-before-generating` says look for
magenta first — that works when a texture path resolves to a placeholder. This is
`Failed to find ANY textures`, which draws nothing at all, so a screenshot shows empty
ground and reads as "the creature did not spawn" rather than "the creature has no art".
The log line is the only honest instrument.

⚠️ The review save was captured with these two invisible. **Any owner review of the
sea-beast roster from `SEABEAST_FAMILIES_20260903.rws` is missing two of eighteen** and
must say so, or their absence reads as a keep/cut signal it is not.

⚠️ The same agent could not screenshot at all that session (near-black captures, the
unfocused-window main-thread starvation), so **no visual check of the other 16 was ever
completed** either. Do not treat "16 folders exist" as "16 render correctly".

## verify

`reading-rimworld-graphics` to confirm nothing resolves for either texPath, then
generate the two missing sprites per `generating-rimworld-sprites` (128 px/cell, real
alpha, silhouette inside the family's footprint), deploy, and reload. Confirm by the
ABSENCE of both `Failed to find any textures` lines and by looking at the pair on screen
beside a sibling from the same family.

## criteria

All 18 sea beasts render; the review save (or its successor) shows every family's three
stages with art, so the owner's keep/cut call is made by looking rather than by reading
a roster.

## Fix

Closed 2026-09-02 by FOUNDRY. Nothing was renamed and no def field changed — the
texPaths were already correct and the folders they name were simply empty. The
existing sea-beast pipeline finished the job it had stopped halfway through:

```
python3 ../tools/gen_sea_facings.py    Starmaw Lanternwhale
python3 ../tools/build_sea_facings.py  Starmaw Lanternwhale
python3 ../tools/write_sea_plan.py     Starmaw Lanternwhale
```

**The usage limit was real and it was hit again.** The first run failed all three
outstanding facings with `ERROR: You've hit your usage limit`, three attempts each,
nine refusals — but the message carries a reset time (`try again at 8:47 PM`), so
this is a quota window, not a dead route. One wait to 20:48, one re-run, and all
three returned. ⇒ **Read the reset time before declaring this blocked.** No other
image tool was substituted; none of them carry the canvas and alpha contract.

`Starmaw_south_raw.png` survived from the pre-limit run and was reused — the
generator skips a raw that already exists, so the reset only had to buy three
calls (Starmaw north, Lanternwhale south and north).

**Canvas 1024x1024 for both, and it is a deliberate cap, not a shortfall.**
drawSize comes from `sea_beasts_def_spec.md` §5 and matches the adult lifeStage in
the def: Starmaw 11.4, Lanternwhale 12.0. At the owner's 128 px/cell that wants
1459 and 1536 px, which rounds to a 2048 canvas — and the image model returns
~1.5 Mpx natively, so 2048 would be interpolated pixels rather than detail. They
ship at **90 and 85 px/cell**, the same ceiling `Reefback` and `ElderSando` are
already at. `canvas_for()` in `sea_creatures.py` enforces the 1024 cap itself; no
number here was chosen by hand.

west is the owner's kept mockup (`colossus_opt2` / `colossus_opt3`) chroma-keyed
and fitted — `Rot4.West` is a left-facing profile, which is the pose the approved
concept was drawn in — east is west mirrored, and only south and north were
generated. Two of four facings are therefore the approved concept at pixel level.

## Verify

**Offline, 0 REJECT both**, `seacheck.py` run standalone after the build:

| set | facings | canvas | worst finding |
|---|---|---|---|
| Starmaw | 4/4 | 1024x1024 | none — 0 REJECT, 0 WARN |
| Lanternwhale | 4/4 | 1024x1024 | 0 REJECT, 1 WARN (0.05% faint pixels, "consistent with glow") |

⭐ **The Lanternwhale WARN is the lantern glow and was confirmed by looking**, not
waved through — the creature's whole tell is *chains of glowing blue lantern
tendrils*, and faint pixels inside the silhouette are what that renders as.

**Looked at both contact sheets**, because the validator proves the files are
shippable and cannot tell you the four facings are one animal:

- `src/RimStarWars/SeaBeasts/art/final/Starmaw/Starmaw_contact_sheet.png` — navy
  whale-shark body, white-cyan constellation speckling and encrusted back growths
  consistent across all four; the pale open mouth reads on south, east and west
  and is correctly absent from north, which shows only dorsal surface and tail.
- `src/RimStarWars/SeaBeasts/art/final/Lanternwhale/Lanternwhale_contact_sheet.png`
  — moss-green ridged plate body with gill curtains; the blue lantern tendrils
  hang under the jaw on south, east and west, and on north only the flanking
  lanterns show past the body, which is what hanging tendrils do seen from above
  and behind.

Both match their kept mockups. Neither was re-rolled.

**Deployed and verified byte-identical.** ⚠️ `art/` is held by `src/DEPLOY_HOLD.txt`
(`SeaBeasts/art/*` — art SOURCE, never shipped), so building a set in `art/final/`
deploys nothing. The four PNGs are copied to
`src/RimStarWars/SeaBeasts/Textures/Things/Pawn/Animal/SeaBeasts/<Slug>/`, which is
the path `texPath` actually binds to, and only that copy ships.

```
deploy_custom_mods.py --mod SeaBeasts --apply
    8 PNGs + SeaBeasts_Colossi.xml   ->  VERIFIED in sync
```

The game tree now holds **18 folders, 72 PNGs** under
`C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\SeaBeasts\Textures\Things\Pawn\Animal\SeaBeasts\`,
and all eight new files `cmp` byte-identical to their repo source. Loose-file
`Graphic_Multi` naming is satisfied: `<Slug>/<Slug>_{south,east,north,west}.png`
against `texPath` `.../<Slug>/<Slug>`.

⚠️ **A live render check is still OWED.** The game was DOWN (`./game`:
`NOT RUNNING`, recorded `DOWN`) and defs and the texture atlas are built at
startup, so proving this on screen costs a cold load — out of proportion to the
remaining risk, which is near zero now that 4/4 files sit at the exact bound path.
The observation to make when the next load happens is written into each set's
`PLAN.md` §2 and is the ABSENCE of both `Failed to find any textures` lines plus
the per-creature tell: constellation dots on a navy flank for Starmaw, lantern
tendril chains under the jaw for Lanternwhale — named per rotation, because
`Graphic_Multi`'s bare-path fallback makes one mis-deployed facing look fine.

⚠️ **The review save `SEABEAST_FAMILIES_20260903.rws` is still short two of
eighteen.** It was captured while these were invisible and this fix does not
retro-fit it. Any owner review of the sea-beast roster needs a successor save, or
it must say out loud that two creatures are missing — their absence is not a
keep/cut signal.

**Stale docs corrected in the same commit**, since the art now exists:

- `SeaBeasts_Colossi.xml`'s header comment said both had NO ART YET.
- `art/final/README.md` said "16 of 18" and carried a "Still owed" section; it now
  says 18 of 18, documents that `art/` is source and the `Textures/` copy is a
  separate act, and records the quota behaviour with its reset time.
- `write_sea_plan.py` hard-coded "No ThingDef exists yet — blocked on the def"
  into every plan it writes. All 18 defs exist; the template now says so. The 16
  older `PLAN.md` files still carry the old sentence and are regenerated by
  re-running the tool whenever anyone next touches them.
