# Boundary: the blind judge's sealed "Steward's decisions" stay out of its brief file

Item: RIMMANDRAKE_SEAL_STEWARD_SECTION_BLIND_JUDGE_READ_IT_FIRST. Code: `src/RimMandrake/rimflow/maturation.py`
(`seal_steward`, `SEAL_MARK`, and the blind-challenge branch of `launch_mod`). Test:
`src/RimMandrake/rimflow/selftest_seal_steward_section.py`.

## Why

A detached run's launch line orders it to read its whole brief file. The blind judge's brief ended with the sealed
section "Steward's decisions (SEALED: read only after lane 1 is committed)", so the judge of FlowWorks blind cycle 5
read the steward's decisions before lane 1 (its own SUMMARY.md, "Blindness record", 2026-11-27).

## What it accepts

- The text of a brief that `brief_text` wrote, and the path of the brief file that `launch_mod` is about to write.
- `expect`: true when the stage is the blind challenge (its brief always carries the sealed section).

## What it promises

- `handed_holds_no_sealed_line`: at the blind challenge, the brief file handed to the detached helper holds no line of
  the sealed section: not its heading, not its preamble, not its decisions.
- `sealed_file_named_with_its_time`: the sealed section is written whole to its own file beside the brief
  (`<brief>.sealed.md`). The handed brief names that file and says to open it only after lane 1 is committed.
- `no_section_launches_as_today`: a brief with no sealed section, where none is expected, passes through unchanged.
- `missing_marker_refuses_by_name`: at the blind challenge, a brief whose sealed marker cannot be found is refused before
  launch (exit 2), and the refusal names the marker. It is never launched whole.

## Failures it does not survive

- A judge that opens the sealed file before lane 1 is committed. The brief tells it when; nothing enforces it.
- A preview from `maturation.py brief <Mod>` still prints the sealed section at its end: that text is for the steward,
  not a launched judge.

## Limits

None. The split is a string partition.

## Offline simulation

Yes: the test runs the real `launch_mod` on the blind fixture of `selftest_maturation.py` with a fake detached helper.
