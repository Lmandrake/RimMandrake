# Polish beside design/specs/2026-11-27-launch-behind/boundary.md

- `src/RimMandrake/Utils/game_instance.py` `_launch_a`: a Steam start of ArchBig fired in the seconds when another run
  starts ArchSmall directly is taken by Steam as ArchSmall's start ("Game process added" names b's exe), and ArchBig never
  starts. risk: seen once on 2026-11-27 23:26 PST; the launch reads "no ArchBig process 120 s after the launch, through
  Steam (Steam is launching it)" and a retry passes.
