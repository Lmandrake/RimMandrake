# RIMMANDRAKE_GREEN_GIMMESOMESLACK_T_STUB_ART_CENSUS_RED_DECIDER

## spec
Gimme Some Slack's offline decider T_STUB_ART_CENSUS (bar cords_join_stubs_on_position_and_slope,
`python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py`) is recorded red (rc 1) since the dispatch
certificate rerun rm-cert-rerun-gimmesomeslack-1794945398 (table published 2a1b8d88ed, 2026-11-17 12:12 PM PST). Cause
as measured at filing: a8d27a3f6b (02:46 AM PST) added the cut box textures Junction_X_p1-p14 and Junction_Tin_p1-p14,
and StubArt.Census (src/RimMandrake/GimmeSomeSlack/Source/Core/StubJoinAudit.cs) classes only p4 of them: 26 textures
have no census row. The certificate refuses the in-game visit on it.

This is the mod's work, done by the builder the Maturation Pipeline routes to it
(RIMMANDRAKE_ROUTE_RED_DECIDER_AT_VISIT_AND_CYCLE_GATES: the offline build's red-decider route, cert_launch, which reuses
this item because it is open under the route's own name). Not fixed by hand. The builder first learns what the decider
is telling it: was each new texture meant to be classed (stubbed, position only, loose end, cord), and does T_STUB_JOINS,
which reads the same textures, agree with the class it gets? If greening one would redden the other, map both (the
owner's "How a bar is shown to hold") instead of nudging a list. Never loosen the census (a planted unknown texture must
still go red).

## refs
file: src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py
file: src/RimMandrake/GimmeSomeSlack/Source/Core/StubJoinAudit.cs
file: src/RimMandrake/GimmeSomeSlack/Textures (Junction_X_p*, Junction_Tin_p*)
file: design/concepts/GimmeSomeSlack/version/test_table.json (T_STUB_ART_CENSUS, T_STUB_JOINS)
commit: a8d27a3f6b (the textures), 2a1b8d88ed (the table that recorded it red)

## criteria
- Every texture under GimmeSomeSlack/Textures has exactly one StubArt.Census class; the census selftest prints its count
  of textures read (not round, matching a file count) and exits 0; its planted-unknown mutant still goes red.
- T_STUB_JOINS stays green on the same build (the two read the same art).
- `python3 src/RimMandrake/rimflow/maturation.py certificate GimmeSomeSlack --run` then `certificate GimmeSomeSlack --to in_game`
  exits 0 (or every remaining refusal is named on this item with a `LEFT OPEN:` note), and the table is landed.

## verify
python3 src/RimMandrake/GimmeSomeSlack/selftest_gss_stub_art_census.py
python3 src/RimMandrake/rimflow/maturation.py certificate GimmeSomeSlack --to in_game
