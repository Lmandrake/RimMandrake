"""validation.py -- modcheck suite for RimUtinni Antiquities (mandrake.rut.antiquities).

Grounded in this mod's actual Source (WorkGiver_ExamineAntiquity.cs,
JobDriver_ExamineAntiquity.cs, CompAntiquity.cs, AntiquityUtility.cs,
AntiquityStageExtension.cs, DefOfs.cs) and its own Defs (RUT_Antiquities_Items.xml,
RUT_Antiquities_Buildings.xml, RUT_Antiquities_Research.xml,
RUT_Antiquities_WorkGivers.xml, RUT_Antiquities_Jobs.xml) -- never the mod's name
or design/Jawa/antiquities_design.md's aspirations for it.

WHAT THIS MOD ACTUALLY DOES AT RUNTIME: entirely self-contained (no soft-hooks,
no companion-mod defs, one ludeon.rimworld dependency) --

  A pawn hauls one of three uncatalogued item defs (RUT_Antiquity_Urn/_Stele/
  _Gravegood, each carrying CompAntiquity) to a RUT_AntiquityReadingStation and
  spends a Wait toil there (JobDriver_ExamineAntiquity) whose length is
  FullDayTicks or HalfDayTicks (once LANGUAGE is finished) scaled by the
  pawn's own Intellectual+Artistic skill average and by
  AntiquitiesSettings.durationMultiplier. On completion it flips
  CompAntiquity.catalogued (once, non-destructively -- "spent for knowledge,
  intact for silver") and calls Find.ResearchManager.AddProgress on
  AntiquityUtility.CurrentStage() (the first of the five RUT_Antiq_* projects
  not yet IsFinished) for baseCost/artifactsRequired points -- entirely
  independent of vanilla's own research-bench system, since every stage's
  requiredResearchBuilding names RUT_AntiquityCipherBench, a
  Building_ResearchBench that never appears in the architect menu (no
  designationCategory, no recipe) and so can never make
  PlayerHasAnyAppropriateResearchBench true -- see
  RUT_Antiquities_Research.xml's own header for the full mechanism. Once all
  five stages finish, WorkGiver_ExamineAntiquity.ShouldSkip returns true
  (AntiquityUtility.CurrentStage() == null) and the driver-wide
  `this.FailOn(() => AntiquityUtility.CurrentStage() == null)` guard makes
  even a FORCED job for the driver end immediately without cataloguing
  anything.

MOD SETTINGS -- suite.toggles below. Only ONE of the four is actually
covered, and here is why the other three are not (the mandatory register,
not an oversight):

  AntiquitiesSettings declares its four fields `public static`
  (readingEnabled, durationMultiplier, keyTextBonusEnabled,
  keyTextChanceScale) -- the identical shape the Pits pilot already found
  live 2026-09-12 makes `rimworld/update_mod_settings` (t.set_setting)
  refuse (that tool's reflection walks INSTANCE fields on the ModSettings
  object; see src/RimMandrake/Pits/validation.py's own note after
  `uncover_disarms`). This suite therefore cannot flip any of the four away
  from its shipped default, and instead:

    * `readingEnabled` (default true) IS covered -- both chains below
      exercise its DEFAULT-ON behavior (the reading job is actually
      offered/pickable and actually runs), which is the one thing provable
      without a working setter. Tagged `toggle="readingEnabled"` per the
      Pits precedent of tagging default-ON coverage rather than leaving the
      toggle name entirely unmentioned.
    * `durationMultiplier` (default 1x) is UNCOVERED: proving the
      MULTIPLIER specifically (as opposed to "a read takes roughly one
      pawn-day") needs two runs at two different values to compare, which
      needs a working setter.
    * `keyTextBonusEnabled` / `keyTextChanceScale` are UNCOVERED for two
      independent reasons: no working setter, AND the bonus is a single
      `Rand.Chance` roll per read -- this project's own house lesson
      ("one negative is not a mechanism" / Pits' own struggle-clock note)
      is that asserting on one roll's outcome proves nothing either way.

Still not proven / likely first-live-run corrections:
  1. `wait_ticks(95000)` in `reading_completes_and_advances_research` is far
     larger than any wait_ticks call measured so far in this suite family
     (Pits' largest was 1200) -- untested at this scale. If
     `rimworld/step_game_ticks` has a practical ceiling or wall-clock
     budget below that, this component will need to split the wait into
     several `wait_ticks` calls rather than one.
  2. The fresh colonist's actual Intellectual+Artistic skill average (and
     therefore the real `skillFactor` and real duration) is not pinned by
     this chain -- `jawa/spawn_pawn` for kindDef "Colonist" does not let a
     caller fix skills, so 95000 ticks is sized for the WORST case
     (skillAvg=0 -> skillFactor=1.5 -> 90000 ticks) plus a buffer; a
     higher-skill colonist finishes earlier and the extra ticks are idle,
     not wrong.
  3. `jawa/inspect_string`'s line-splitting of GetInspectString() was read
     from its tool Description, not measured live -- the assertion below
     searches every returned line for the expected keyed string rather
     than assuming a fixed line index.

CompAntiquity.CompInspectStringExtra() returns a TRANSLATE()'d string, not
the raw keyed name -- the assertions below check for the actual English
text in Languages/English/Keyed/RUT_Antiquities.xml ("Catalogued" /
"Not yet read"), not "RUT_Antiquity_Catalogued" itself.
"""
from modcheck import Suite, ExpectationFailed

suite = Suite("Antiquities")
suite.toggles = ["readingEnabled", "durationMultiplier", "keyTextBonusEnabled",
                 "keyTextChanceScale"]

STATION = "RUT_AntiquityReadingStation"
URN = "RUT_Antiquity_Urn"
JOB = "RUT_ExamineAntiquity"
WORK_TYPE = "RUT_ExamineAntiquities"
STAGES = ["RUT_Antiq_Language", "RUT_Antiq_Religion", "RUT_Antiq_Culture",
          "RUT_Antiq_Cartography", "RUT_Antiq_Voice"]

# FullDayTicks(60000) * worst-case skillFactor(1.5, skillAvg=0) + buffer.
# See module docstring #1/#2 for why this is sized to the worst case.
READ_WAIT_TICKS = 95000


def _inspect_contains(t, thing_id, needle):
    r = t.bridge_call("jawa/inspect_string", thingIds=thing_id)
    things = (r or {}).get("things") or []
    lines = []
    for row in things if isinstance(things, list) else []:
        lines.extend((row or {}).get("inspect") or [])
    text = "\n".join(str(l) for l in lines)
    if needle not in text:
        raise ExpectationFailed(
            "jawa/inspect_string(%r) does not contain %r -- raw: %r" % (thing_id, needle, r))
    return r


@suite.chain("reading_completes_and_advances_research")
def reading_completes_and_advances_research(t):
    """The whole reading loop, forced via jawa/ordered_job with the driver's
    own two targets (antiquity=A, station=B) rather than waiting on the
    WorkGiver's own auto-assignment -- this still exercises the REAL
    JobDriver_ExamineAntiquity (goto/carry/wait/CompleteReading), just not
    the separate "will a pawn pick this up on their own" question, which
    `no_more_reading_once_all_stages_done` below covers instead. Tagged
    `toggle="readingEnabled"`: this is the mechanism that toggle's default
    (true) actually gates (see module docstring)."""
    t.clear_area(size=20)
    x, z = t.anchor
    t.spawn(STATION, count=1, at="point")
    urn_cells = t.spawn(URN, count=1, at="point")
    reader = t.spawn_pawn("Colonist", hostile=False, beyond=urn_cells)

    with t.component("ordered_reading_job_catalogues_and_adds_progress",
                      toggle="readingEnabled"):
        # Resolve the two things' own thingIDs -- ordered_job needs a
        # thingId, not a defName, for each target.
        things = t.bridge_call("jawa/list_things", rect="%d,%d,20,20" % (x - 10, z - 10))
        rows = (things or {}).get("things") or []
        urn_id = next((r.get("id") for r in rows if r.get("def") == URN), None)
        station_id = next((r.get("id") for r in rows if r.get("def") == STATION), None)
        if not urn_id or not station_id:
            raise ExpectationFailed(
                "could not resolve urn/station thingIds from jawa/list_things: %r" % rows)

        r = t.bridge_call("jawa/ordered_job", pawnId=reader, jobDef=JOB,
                          targetAId=urn_id, targetBId=station_id, waitTicks=60)
        if not (r or {}).get("accepted"):
            raise ExpectationFailed("jawa/ordered_job(%s) was not accepted: %r" % (JOB, r))

        t.wait_ticks(READ_WAIT_TICKS)

        _inspect_contains(t, urn_id, "Catalogued")

        research = t.bridge_call("jawa/research_progress", project="RUT_Antiq_Language",
                                 action="add", amount=0)
        result = (research or {}).get("result") or {}
        if not (result.get("progress") or 0) > 0:
            raise ExpectationFailed(
                "RUT_Antiq_Language progress is not > 0 after a completed read: %r" % research)
        t.screenshot()


@suite.chain("no_more_reading_once_all_stages_done")
def no_more_reading_once_all_stages_done(t):
    """Beyond-toggle: JobDriver_ExamineAntiquity's own driver-wide
    `FailOn(() => AntiquityUtility.CurrentStage() == null)` guard -- once
    every RUT_Antiq_* stage is finished, even a FORCED reading job must die
    before completing, and the antiquity must stay uncatalogued."""
    t.clear_area(size=20)
    x, z = t.anchor
    t.spawn(STATION, count=1, at="point")
    urn_cells = t.spawn(URN, count=1, at="point")
    reader = t.spawn_pawn("Colonist", hostile=False, beyond=urn_cells)

    with t.component("stage_completion_gate", beyond_toggle=True):
        for stage in STAGES:
            r = t.bridge_call("jawa/research_finish_project", project=stage)
            if not (r or {}).get("success"):
                raise ExpectationFailed("could not finish %s: %r" % (stage, r))

        things = t.bridge_call("jawa/list_things", rect="%d,%d,20,20" % (x - 10, z - 10))
        rows = (things or {}).get("things") or []
        urn_id = next((r.get("id") for r in rows if r.get("def") == URN), None)
        station_id = next((r.get("id") for r in rows if r.get("def") == STATION), None)
        if not urn_id or not station_id:
            raise ExpectationFailed(
                "could not resolve urn/station thingIds from jawa/list_things: %r" % rows)

        t.bridge_call("jawa/ordered_job", pawnId=reader, jobDef=JOB,
                     targetAId=urn_id, targetBId=station_id, waitTicks=120)
        t.wait_ticks(600)

        _inspect_contains(t, urn_id, "Not yet read")
        t.screenshot()
