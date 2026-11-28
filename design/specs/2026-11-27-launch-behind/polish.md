# Polish beside design/specs/2026-11-27-launch-behind/boundary.md

- `src/RimMandrake/Utils/game_instance.py` `_launch_a`: a Steam start of ArchBig fired in the seconds when another run
  starts ArchSmall directly is taken by Steam as ArchSmall's start ("Game process added" names b's exe), and ArchBig never
  starts. risk: seen once on 2026-11-27 23:26 PST; the launch reads "no ArchBig process 120 s after the launch, through
  Steam (Steam is launching it)" and a retry passes.
- `src/RimMandrake/Utils/focus_probe.py`: a full run of a Steam start of ArchBig (no other game up, so Steam itself starts
  it) has no green reading yet; the one try lost the race above. risk: Steam's own start is shaped by the guard alone;
  its Launching window was undone within 24 ms in the direct-start runs.
