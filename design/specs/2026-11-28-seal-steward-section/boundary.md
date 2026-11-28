# BOUNDARY: maturation.py's sealed "Steward's decisions" stay out of a blind judge's brief file

Code: `src/RimMandrake/rimflow/maturation.py`. **This page covers only the seal**: `SEAL_MARK`, `seal_steward` and its
call in the blind-challenge launch of `launch_mod`. Each promise below has a test of its name in
`src/RimMandrake/rimflow/selftest_seal_steward_section.py`, which runs the real `launch_mod` on the blind fixture of
`selftest_maturation.py` with a fake detached helper. Item RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST.

Why: a detached run's launch line orders it to read its whole brief file. The blind judge's brief ended with the sealed
section, so the judge of FlowWorks blind cycle 5 read the steward's decisions before lane 1 (its own SUMMARY.md,
"Blindness record", 2026-11-27).

## ACCEPTS (the only inputs the seal is built for)

- **a-brief-text-from-brief-text.** The text that `brief_text` returned, with a preface, a reconcile step or a resume
  text put in front of it, as `launch_mod` does. The sealed section is the last section of a blind brief.
- **a-brief-path-in-brief-dir.** The path of the brief file that `launch_mod` is about to write, in `brief_dir()`.

## DOES NOT SURVIVE (not handled)

- **a-judge-that-opens-the-file-early.** The handed brief says to open the sealed file only after lane 1 is committed;
  nothing stops a judge that opens it earlier.
- **the-steward-preview.** `maturation.py brief <Mod>` still prints the sealed section at the end. That text is for the
  steward, not for a launched judge.

## PROMISES (each one is owed a test of the same name)

- **handed-holds-no-sealed-line.** At the blind challenge, the brief file handed to the detached helper holds no line of
  the sealed section: not its heading, not its preamble, not its decisions.
- **sealed-file-named-with-its-time.** The sealed section is written whole to its own file beside the brief
  (`<brief>.sealed.md`). The handed brief names that file and says to open it only after lane 1 is committed.
- **no-section-launches-as-today.** A brief with no sealed section, where none is expected (any stage but the blind
  challenge), passes through unchanged and writes no sealed file.
- **missing-marker-refuses-by-name.** At the blind challenge, a brief whose marker cannot be found is refused before
  launch (exit 2) and launches nothing; the refusal names the marker. It is never launched whole.

## LIMITS

None: the seal is a string partition and one file write.

## Offline simulation

Yes: the real `launch_mod` on a fixture tree with a fake detached helper (the test above).
