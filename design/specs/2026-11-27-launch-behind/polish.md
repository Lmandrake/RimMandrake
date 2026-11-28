# Polish beside design/specs/2026-11-27-launch-behind/boundary.md

- `src/RimMandrake/Utils/game_instance.py` `_launch_a`: a Steam start of ArchBig fired in the seconds when another run
  starts ArchSmall directly is taken by Steam as ArchSmall's start ("Game process added" names b's exe), and ArchBig never
  starts. risk: seen once on 2026-11-27 23:26 PST; the launch reads "no ArchBig process 120 s after the launch, through
  Steam (Steam is launching it)" and a retry passes.

## (fresh read, WB-pipeline-read-utils-20261128-092119, 2026-11-28)
- `src/RimMandrake/Utils/launch_behind.py` the guard writes READY before its hook thread is up. risk: a steal in that gap is put back only by the 100 ms poll, not at once.
- `src/RimMandrake/Utils/focus_probe.py` the new `idle` field of the probe's samples has not run live. risk: if the field does not arrive, a hand-off to an old game reads `other` (GREEN) as before; the next `focus_probe.py run` shows it.
- not handled (for the page's DOES NOT SURVIVE): a single 10 Hz sample inside a guard put-back of a handed-off old game (no foreground event) now reads RED; the flicker exemption covers only flickers that an event measured.
