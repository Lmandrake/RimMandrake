# Modcheck suite corrections 2026-10-02 (MODCHECK_SUITE_CORRECTIONS_1)

## Evidence inventory
Evidence exists under `D:\Luke\dev\RimMandrake\Transient\modcheck\` (clone: /home/mandrake/rm/foundry/Transient/modcheck) for
Inhabited, Aftermath, Antiquities, Droidworks (09-13 run plus 10-02 UTC situational re-run).
ABSENT for RimProperty and Graffiti: no summary or html exists for either (aborted/desynced 09-13 runs left nothing).

## Corrections made
No new edits this pass. Every failure still RED in the 10-02 evidence was already corrected in commit 7b90a82bc
(18:52 PDT 10-01, after the runs): per-assertion table in `Transient/suite_corrections_2026-10-01.md`
rows 9-15, 22. Inhabited (stock chain world-object leak), Aftermath (ThreatBig CanFireNow gate),
Antiquities (chunked wait under tick cap, f9d1b4c70), Droidworks (rows 10-14) all carry CORRECTED markers.
RimProperty: suite already calls t.ensure_faction("Pirate") before set_thing_props (PirateWaster replacesFaction).
Graffiti: library already drops late replies to timed-out requests (rimbridge_client.py `abandoned`), which is the
"unexpected response id" cause; suite already advances the clock itself. All six validation.py py_compile clean.
No mod defects filed (none shown by this evidence).

## Needs live run
All six: corrected suites have only offline proof (selftest_suite_corrections.py). Live re-run on min16 owed for
Inhabited, Aftermath, Antiquities, Droidworks, RimProperty (faction claim), Graffiti (desync survival).
