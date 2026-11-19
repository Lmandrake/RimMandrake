On Archmagi D:\Luke\dev\RimMandrake (~/dev/RimMandrake) is an export with no .git folder, so a tool that matches repos by origin url cannot pair it with the bench clone; it counted RimMandrake twice. Match by the origin's repo name instead, and run fleet scripts from the seat clone so the live tree, not the export, is the one measured (crystallize retro_metrics.py now does this).
item: RIMMANDRAKE_IMPROVE_CRYSTALLIZE_SKILL_WHILE_FINDINGS_ARE_FRESH
home: infrastructure/state/facts/instrument_traps.md
