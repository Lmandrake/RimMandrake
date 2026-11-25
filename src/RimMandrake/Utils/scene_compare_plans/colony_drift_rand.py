"""colony_drift.py plus the random state itself as a track (static Verse.Rand seed and iterations; reading a field draws nothing), to
see on which tick runs from one save and one written-back state first draw differently. Item
RIMMANDRAKE_MEASURE_PLAY_AGAINST_PAUSED_STEP_NEVER_COMPARED."""
SAVE = "rm_fixture_play_vs_step"
LIMIT = 300
CALM = "standard"
CAST = ("Human193", "Human196", "Human199", "Donkey12045")


def plan(c):
    return dict(until=LIMIT, record=[c.track("static:Verse.Rand", "iterations"), c.track("static:Verse.Rand", "seed")] +
                [c.track(t, p) for t in CAST for p in ("Position", "CurJobDef")])
