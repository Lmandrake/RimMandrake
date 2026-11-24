# Polish

- `src/RimMandrake/Utils/leftovers.py` `canon_save_names` and `saves_prune.py` read canonical names by their own rules.
- `src/RimMandrake/Utils/remake/repaint_stamp.py` calls `jawa/world_mutators_audit` (heavy-diagnostic) with R3 loaded; the
  guard refuses that one read. Load a copy of R3 under another name for the repaint.
