# CRACKEDLANDS_FIVE_BEATS_AUDIO_1 — bespoke audio for the five beats, and the tarruq's call

Split from `CRACKEDLANDS_GPT_ENRICHMENT_1` §2. The MECHANISM is built: herald window, beats 1–3,
chimes tolling far→near at positions, the roar sustainer, and the tarruq hush (Harmony gate on
`Pawn_CallTracker.TryDoCall`). Every sound currently plays a **vanilla clip retinted by pitch and
distance** (`src/RimMandrake/FloodedCanyon/Defs/SoundDefs/RM_CanyonBeats.xml`).

## ruling

Owner, 2026-10-03, typed: *"Just use vanilla until we get around to sound work."* The vanilla clips in
`RM_CanyonBeats.xml` ship as final; no bespoke audio and no retuning are owed.

## owed

**The tarruq's call.** `RM_Tarruq` ships with no `soundCall`, so the hush gate is live but there is nothing
to silence yet. Give it a vanilla call SoundDef as it stands (no retint), so the hush has something to
silence. The bible's call: "long low tones the canyon carries for hundreds of meters, each animal answering
its neighbors down the line" — pick the vanilla call closest to that.

## criteria

Each beat audibly distinct in a joint session with the owner. The tarruq calls on an ordinary day,
and `DebugStateReport` shows `tarruqSilenced=True` from beat 3 until the recede.

## spec

The `## owed` and `## criteria` sections above are the spec (the owner's 2026-10-03 vanilla-audio ruling bounds it).

## verify

`cd src/RimMandrake/CrackedLands && python3 -c "import validation as v; assert not v._tarruq_call_findings()"` (the static check `tarruq_call`); live: `DebugStateReport` `tarruqSilenced`.

## refs
file: src/RimMandrake/CrackedLands/Defs/ThingDefs_Races/RM_IrqitTarruq.xml
file: src/RimMandrake/CrackedLands/Source/RM_TarruqHushPatch.cs
def: ThingDef/RM_Tarruq
