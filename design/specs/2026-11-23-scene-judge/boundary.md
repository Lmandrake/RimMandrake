# BOUNDARY: the offline scene judge

Code: `src/RimMandrake/rimflow/scene_judge.py`, `src/RimMandrake/rimflow/selftest_scene_judge.py`, the judge
entry point of `src/RimMandrake/Utils/scene.py`, and the offline condition builders of
`src/RimMandrake/Utils/scene_cond.py`.

The instrument contract is [the Bridge v2 boundary](../2026-11-23-bridge-v2/boundary.md). The checker is Python
condition data saved in `contract.json`. It selects a kept request when a session has several calls. The
physical call facts come from that trace and its receipts. The checker can name `kind` (A by default or B),
`opportunity`, `exposure`, `success`, `forbidden`, `allowed_miss` (B only), `external` (tap names) and
`cast_activity` (a condition that detects cast or tested-mod activity toward the spoiler). It can also have a
`claim`, `version` and `request`. Conditions use the existing tree operators and named track and tap probes
described in `scene_contracts/judge.md`. Exposure must occur after the first sample, success is read at the
last sample, opportunity must hold throughout, and forbidden effects can occur anywhere. The writer's
`open.tracks` and `open.acts` describe the call, and optional `open.taps` lists the armed taps.
When `open.cond.sample.probes` gives the probes behind track labels, typed conditions use those bindings.

The landed writers emit tracks and acts. Tap and alias link fixtures extend that envelope with
`rec: tap` (`name`, `enterSeq`, `exitSeq`, `parentSeq`, `data`) and `rec: link` (`alias`, `old`, `new`).
A row with an `alias` and `object` certifies that object as the subject of the row. Row 4 needs an external tap
that predates the act or records entry into the station, and a recorded cast-activity check that stays false
up to and including the spoiler's tick. A mod's advisory records provide no condition values.

## DOES NOT SURVIVE

- A span with missing rows, unreadable decisive conditions, or an alias that changes without a recorded link.
- Sub-tick questions about tracks, unrecorded observations, or aggregating several calls into a new trace.
- Concurrent editing of a kept folder's inputs while judging.

## PROMISES

- **classifier-rows.** The nine rows decide in order, with observed values beside the failed condition. The
  receipts must establish the build, game, session, tick span and stamps. Bar credit requires an accepted,
  unstamped SUCCESS on an identified commit.
- **no-closing-record.** The envelope needs a `scene_trace_v1` opening and a paused close on the end tick,
  with consistent run, row numbers, sequence, ticks, phases and track labels. An empty trace gives COULD NOT LOOK.
- **dropped-span.** Loss in the window cannot prove a zero or a forbidden effect's absence.
- **missing-first-sample.** The opening list must have a first sample for every track. Samples must be ordered,
  declared and unique in their phase or tick, and a decisive condition needs readable values.
- **missing-last-sample.** The closing sample is required for every opening track.
- **missing-tap.** The named tap must have been armed, including when the query asks for zero events. Its
  records must have valid entry and exit sequences, including for nesting.
- **success-at-first-sample.** A success already true before any act is an apparatus fault.
- **success-without-exposure.** An unexposed run cannot succeed.
- **advisory-record.** A mod's assertion alone supplies no verdict.
- **cast-went-to-hazard.** A cast that moves toward the spoiler leaves the opportunity failure unresolved.
- **giver-refusal.** The tested giver's refusal is a result of a delivered act. The trace needs the act
  declarations, delivery records and a following sample.
- **same-checker-adds-history.** Rejudgement preserves the classification and appends a versioned line.
- **unrecorded-value-named.** Typed probes can read a track by its recorded binding. Rejudgement names a
  missing track or tap and leaves verdict files alone.
- **first-outcome-kept.** A new reading leaves the original verdict intact. Changed evidence is refused, and
  applying a changed checker requires rejudgement.
- **alias-needs-link.** An object change without a named link joining the recorded objects gives COULD NOT LOOK.
- **exit-codes.** The CLI has a distinct exit code for every outcome. Unreadable kept inputs or a missing
  matching receipt give COULD NOT LOOK.
- **unknown-key-named.** An unknown checker key is refused with its name. Invalid checker data or conditions,
  an absent or ambiguous call selection, and rejudgement without a first verdict are refused by name.
- **standard-cast-and-world-tracks-are-read.** The companion's twelve cast tracks of each cast member (`<alias>.pos`, `.job`, ...)
  and its six world tracks (`world.weather`, ...) are read although the open row does not list them. Each joins at its first
  sample and is held to the first-and-last rule of a declared track. Any other undeclared name gives COULD NOT LOOK.
- **in-tick-tap-rows-are-read-in-the-span.** A cast or world tap row (phase `in_tick`: `job_start`, `job_end`, `link`, ...) inside
  the run's ticks is read. A track with phase `in_tick` gives COULD NOT LOOK.
