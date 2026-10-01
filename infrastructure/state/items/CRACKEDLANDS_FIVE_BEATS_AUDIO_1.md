# CRACKEDLANDS_FIVE_BEATS_AUDIO_1 — bespoke audio for the five beats, and the tarruq's call

Split from `CRACKEDLANDS_GPT_ENRICHMENT_1` §2. The MECHANISM is built: herald window, beats 1–3,
chimes tolling far→near at positions, the roar sustainer, and the tarruq hush (Harmony gate on
`Pawn_CallTracker.TryDoCall`). Every sound currently plays a **vanilla clip retinted by pitch and
distance** (`src/RimMandrake/FloodedCanyon/Defs/SoundDefs/RM_CanyonBeats.xml`).

## owed

1. Bespoke audio for the six defNames in that file: `RM_CanyonBeat_SlotWind`,
   `RM_CanyonBeat_PanTick`, `RM_CanyonChime_Far/_Mid/_Near` (the mechanics item rules 3–4 chime
   tones), `RM_CanyonFlood_Roar`. Swap the `grains`; the code binds to the defNames.
2. **The tarruq's call.** `RM_Tarruq` ships with no `soundCall`, so the hush gate is live but there
   is nothing to silence yet. The bible's call: "long low tones the canyon carries for hundreds of
   meters, each animal answering its neighbors down the line."

## open question (owner)

Where does bespoke audio come from? The bible names "slate E's pipeline", and no audio pipeline
item could be found to cite. A vanilla call such as `Pawn_Monkey_Call`, retinted, would be a
cosmetic choice, so it was not made here.

## criteria

Each beat audibly distinct in a joint session with the owner. The tarruq calls on an ordinary day,
and `DebugStateReport` shows `tarruqSilenced=True` from beat 3 until the recede.
