## spec
Author `design/Jawa/bridge/INHABITED_CAST_DEEPWATER.md` to parity with the other eleven
`INHABITED_CAST_*.md` rosters — same structure, same depth, same numbering convention
(they self-number cast 01–11; this is 12).

**Why this one is not a rounding error.** `INHABITED_DESIGN.md` §5.9 tabulates **twelve**
factions carrying dossiers, and `design/Jawa/bridge/` holds **eleven** cast files. The
Deepwater Compact is the missing one, and it is not a marginal faction: it holds **5
settlements**, and its faith is **`the Balance`** — *"the seas, measured and rationed…
people for whom excess is the sin"*. On a planet that is **8.14% water in exactly three
seas**, that is the water politics every other faction's water doctrine reacts to. It
currently ships with no named inhabitants at all.

## verify
`ls design/Jawa/bridge/INHABITED_CAST_*.md | wc -l` returns **12**, and
`python3 src/RimMandrake/Utils/check_doc_links.py --require-status` still passes (the new
file needs a `<!-- status: -->` header like its eleven siblings).

## criteria
A reader can name the Compact's people the way they can name the Hutts' or the Junkers'.
The roster's water doctrine agrees with `canon.yml > planet.water_pct` (8.14%, three seas,
`The Scald` painted `Lake`) and with `design/Jawa/worldbuilding/water_doctrine.md`.

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready

**filed:** BUILD, 2026-08-20, on the owner's ruling

**notes:** Owner's ruling, 2026-08-20, on the question filed as `DOSSIER_WITHOUT_CAST_ROSTER_1`:
**author the missing roster.** Found during the W3 status-header sweep, not by looking for
it — the eleven rosters self-number 01–11 and Deepwater is the only §5.9 row with no
numbered file.
⚠️ `INHABITED_CAST_HOMESTEAD.md:15` says *"the hardest brief of the twelve"* — that counts
briefs, not files, and is correct. Do not "fix" it to eleven.
