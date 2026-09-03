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
