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
