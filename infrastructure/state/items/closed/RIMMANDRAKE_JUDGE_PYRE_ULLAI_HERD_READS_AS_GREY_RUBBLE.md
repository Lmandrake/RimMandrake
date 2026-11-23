## spec
Pyrelands 0.1.0, in-game visit 5 (ArchBig, tier pyrelands, 2026-11-22). Strange thing, class MOD (art readability), for an
art judge. The ullai herd cannot be told apart at play zoom: the sc_ullai capture (herd_follows_two_day_old_burn) and a
capture framed on the 16 living ullai alone (scripts/herd_look.py: list_pawns read them at (50..85, 147..158), then
screenshot_cell_rect over them) both show no recognisable animal, only small flat grey blobs and bent grey sticks in the
grass, the size of a loose stone chunk. The texture (Textures/Things/Pawn/Animal/Pyrelands/Ullai/Ullai_*.png, 256 px) is a
tall, thin, giraffe-like grey body; at adult drawSize 2.0 seen from above, resting or head-on, it reads as rubble. Visit 4
saw the same at the walk save's creatures station ("thin slivers, hard to recognise"). Owner rule: each graphic object is
recognisable as what it is.
Evidence: design/concepts/Pyrelands/version/in_game/visit_5/screenshots/herd_look__ullai_lying_crop.jpg and
herd_look__rimbridge_20261122_064207__cell_rect.jpg; evidence/script_herd_look.log (the 16 cells).

## verify
An art judge (design/RimMandrake/art_judge_brief.md) is shown an in-game capture of a resting and a standing ullai herd at
play zoom beside a vanilla muffalo, and says whether an ullai is recognisable as an animal. If he kept this art, its
replacement is his act (five acts, 2): the judge's reading then goes to him.

## criteria
- An ullai at play zoom, standing and resting, reads as an animal to a judge who did not make it.

## Acceptance test
none, a taste reading by an art judge (not a tuning number).

## refs
file: src/RimMandrake/Pyrelands/Textures/Things/Pawn/Animal/Pyrelands/Ullai/Ullai_south.png
def: PawnKindDef/RM_Ullai
