"""validation.py -- modcheck suite for RimUtinni: Birth & Hatch Demo
(mandrake.rut.birthhatchdemo).

🔴 DEMONSTRATION MOD, NOT CAMPAIGN CONTENT (both this mod's own About.xml
and its one ThingDef's own XML comment say so explicitly). It exists to
answer one question the owner asked 2026-09-02 (LIVE_BIRTH_AND_HATCH_DEMO_1):
can the bridge drive RimWorld's reproduction chain through to a hatched
baby Jawa? Per the item's own note, this mod is meant to be DELETED once the
answer is recorded -- this validation.py is written now, for this backfill
pass, on the same terms as the other 5: it will need deleting alongside the
mod, not kept as permanent campaign-content coverage.

Pure-Defs mod: no Source/, no Assemblies/, no ModSettings class -- only
About/About.xml and one ThingDef file (`Defs/ThingDefs_Items/
RUT_DemoEgg.xml`), both read in full before writing this.
`suite.toggles = []`, every component `beyond_toggle=True`.

THE MECHANISM, per the ThingDef's own XML comment (which cites exact 1.6
source lines, not assumed):
  - `RUT_DemoEggJawa` (`ParentName="EggFertBase"`, the same parent/comp
    shape as Core's `EggChickenFertilized`, copied not invented) carries
    exactly one `CompProperties_Hatcher` with `hatcherDaystoHatch=0.1`
    (~2.4 in-game hours -- long enough to be a real hatch, short enough to
    watch on a fast clock) and `hatcherPawn=RSW_Jawa`.
  - `CompProperties_Hatcher.hatcherPawn` is a `PawnKindDef`, not an
    animal-only field (`CompProperties_Hatcher.cs:9`), so a humanlike kind
    (`RSW_Jawa`, confirmed a real, loaded PawnKindDef in
    `src/RimStarWars/StarWarsRaces/Defs/PawnKindDefs/SW_RescuedKinds.xml`)
    is a legal hatcherPawn target.
  - `CompHatcher` builds its `PawnGenerationRequest` with
    `DevelopmentalStage.Newborn` (`CompHatcher.cs:85`) -- whatever hatches
    arrives as a BABY by construction, which is exactly the "baby Jawa" the
    owner asked for.

🔴 TWO REAL RISKS THE DEF'S OWN COMMENT FLAGS, AND THIS SUITE MUST NOT
ASSUME AWAY (per the mod's own header, quoted, not paraphrased):
  1. `CompHatcher.cs:85` passes `forceGenerateNewPawn: false` -- the SAME
     defect class as SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1 (fixed elsewhere
     for `jawa/spawn_pawn`, but vanilla's own hatcher still has it
     unpatched). A hatch could hand back a RECYCLED world pawn instead of a
     genuinely new one, silently draining a faction's population. This
     suite takes a `jawa/list_pawns` baseline BEFORE spawning the egg and
     checks the post-hatch pawn's ThingID is NOT in that baseline -- the
     walk doc's own step 3/7 method -- rather than trusting "a pawn
     appeared" alone.
  2. `CompHatcher.cs:54` reads the hatcherPawn's own race for
     `CompProperties_EggLayer`; a humanlike race has none, so that lookup
     returns null. This suite does not assert anything about that lookup's
     result directly (no bridge tool was found that reads it), but notes it
     as a documented risk the hatch could still trip on in a way invisible
     to this suite's own checks (see gap #2).

WHY THE WAIT IS REAL TICKS, NOT A CLOCK JUMP: the walk doc is explicit
(step 6) that `rimworld/step_game_ticks` (real simulation) is required, NOT
`jawa/time_set_ticks` (jumps the counter without simulating `CompTick`) --
the latter would never actually fire `CompHatcher.CompTick`'s hatch check.
6000 ticks = 0.1 day at `GenDate.TicksPerDay=60000`; this suite waits 6100
for margin, matching the walk doc exactly.

Still not proven / real gaps:
  1. No independent check of `CompHatcher.cs:54`'s `CompProperties_EggLayer`
     null-lookup path (risk #2 above) -- no bridge tool was found that
     reads a comp's internal null-check outcome; only the END RESULT (did
     a new Newborn RSW_Jawa appear, was the egg consumed) is observable
     here.
  2. `jawa/pawn_get`'s exact field name for developmental stage was read
     from other suites' own usage patterns in this repo (not independently
     re-measured against a live bridge call before writing this) --
     `developmentalStage`/`DevelopmentalStage.Newborn`'s exact string
     representation in that tool's JSON is asserted defensively (substring
     match against "Newborn"), not as an exact-equality guess.
  3. This is a genuinely disposable demo -- once LIVE_BIRTH_AND_HATCH_DEMO_1
     is answered and the mod is deleted (per its own About.xml), this
     validation.py should be deleted with it, not left as an orphaned
     entry in modcheck's mod list.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("BirthHatchDemo")
suite.toggles = []   # no Source/, no ModSettings -- every component beyond_toggle

EGG_DEF = "RUT_DemoEggJawa"
HATCH_KIND = "RSW_Jawa"
HATCH_TICKS = 6100   # 0.1 day (6000 ticks, GenDate.TicksPerDay=60000) + margin, per walk doc


def _live(t):
    """Distinguishes a real chain run from the offline declaration probe."""
    return t.session is not None and not t.upstream_failed


def _list_pawn_ids(t):
    r = t.bridge_call("jawa/list_pawns", limit=500)
    return {p.get("id") for p in ((r or {}).get("pawns") or []) if p.get("id")}


def _egg_thing_defs(t):
    r = t.bridge_call("jawa/list_things",
                      rect="%d,%d,20,20" % (t.anchor[0] - 10, t.anchor[1] - 10))
    return [row for row in ((r or {}).get("things") or []) if row.get("def") == EGG_DEF]


@suite.chain("egg_hatches_into_new_baby_jawa")
def egg_hatches_into_new_baby_jawa(t):
    """The whole reproduction-chain proof, in one chain per the walk doc's
    own sequencing: baseline pawns -> spawn egg -> confirm exactly one egg
    present -> real-tick wait -> confirm a genuinely NEW Newborn RSW_Jawa
    appeared -> confirm the egg was consumed."""
    t.clear_area(size=20)

    baseline_ids = _list_pawn_ids(t) if _live(t) else set()

    t.spawn(EGG_DEF, count=1, at="point")

    with t.component("egg_spawns_findable", beyond_toggle=True):
        eggs = _egg_thing_defs(t) if _live(t) else []
        if _live(t):
            if len(eggs) != 1:
                raise ExpectationFailed(
                    "expected exactly 1 %s near the anchor after spawning, "
                    "found %d: %r" % (EGG_DEF, len(eggs), eggs))
        t.screenshot()

    with t.component("hatch_produces_new_newborn_jawa", beyond_toggle=True):
        t.wait_ticks(HATCH_TICKS)

        if _live(t):
            post_ids = _list_pawn_ids(t)
            new_ids = post_ids - baseline_ids
            if not new_ids:
                raise ExpectationFailed(
                    "no new pawn ThingID appeared after waiting %d ticks -- "
                    "either the hatch never fired, or (risk #1 in this "
                    "file's own docstring) CompHatcher's "
                    "forceGenerateNewPawn:false handed back a pawn already "
                    "counted in the baseline" % HATCH_TICKS)

            hatched = None
            for pid in new_ids:
                pd = t.bridge_call("jawa/pawn_get", pawn=pid)
                row = ((pd or {}).get("pawns") or [{}])[0]
                if row.get("kindDef") == HATCH_KIND:
                    hatched = row
                    break
            if hatched is None:
                raise ExpectationFailed(
                    "new pawn ThingID(s) %r appeared but none has "
                    "kindDef=%s -- hatch produced the wrong kind, or a "
                    "coincidental unrelated pawn spawn" % (new_ids, HATCH_KIND))

            stage = str(hatched.get("developmentalStage")
                       or hatched.get("lifeStage") or "")
            if "Newborn" not in stage:
                raise ExpectationFailed(
                    "hatched %s pawn's developmental stage is %r, expected "
                    "to contain 'Newborn' (CompHatcher.cs:85 builds its "
                    "PawnGenerationRequest with DevelopmentalStage.Newborn)"
                    % (HATCH_KIND, stage))

            remaining_eggs = _egg_thing_defs(t)
            if remaining_eggs:
                raise ExpectationFailed(
                    "%d %s still present after the hatch window -- vanilla "
                    "CompHatcher is expected to consume/despawn the egg on "
                    "hatch: %r" % (len(remaining_eggs), EGG_DEF, remaining_eggs))
        t.screenshot()
