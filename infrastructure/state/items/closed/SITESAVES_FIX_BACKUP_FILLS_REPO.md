# SITESAVES_FIX_BACKUP_FILLS_REPO

## proof (corrected 2026-11-17, drain of the retired judge)
A code reading, not a run — the defect is in the default itself:

    grep -n -e '--work' -e 'Transient.*test_site_saves' -e 'saves_backup_' src/RimMandrake/Utils/modcheck/test_site_saves.py

Pass = no default work directory inside the repo, and no `saves_backup_*` written under it.

## what it reads, measured 2026-11-17 — the bug is STILL THERE, and nothing has landed
`src/RimMandrake/Utils/modcheck/test_site_saves.py`:
  line 730  ap.add_argument("--work", default=None, help="evidence dir (default Transient/test_site_saves)")
  line 745  work = a.work or os.path.join(root, "Transient", "test_site_saves")
  lines 584, 818  rec["backup"]["dir"] = os.path.join(work_dir, "saves_backup_%s" % stamp)

So an unflagged run still defaults its evidence directory into the repo and drops save backups there. And
`git log --grep` finds ZERO commits citing this item: the work was never done, which is why no sha could be
cited and why the block could never lift on a proof.
Evidence: /Users/mandrake/ClaudeWork/scratch/rm-drain-logs/probe5.txt

Next worker: default `--work` to a path under D:\ClaudeWork\rimmandrake (agent scratch), never the repo, and
re-run the grep above.
