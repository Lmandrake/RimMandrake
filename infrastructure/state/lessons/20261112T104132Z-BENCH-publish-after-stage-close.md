After designer_stage.py close lands result.<run>.json on origin (landed: PUBLISHED), the local working copy of that file stays untracked; the next ./publish then fails 'Untracked working tree file ... would be overwritten by merge' and parks dirty files. Fix: cmp the local file against origin/main's, delete it if identical, re-run ./publish.
item: NONE
home: src/RimMandrake/rimflow/roles/designer.md
