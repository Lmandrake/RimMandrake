# Weekly cleaning wave 2 — rules for every WRITING agent (2026-10-11)

Read first: the audit reports in /home/mandrake/rm/bench/Transient/weekly_cleaning_2026-10-11/ (01_handoffs, 02_claudemd_and_specs, 03_skills, 04_lessons_and_memory, 05_git_and_disk, 06_telemetry_design, 07_rimflow_rimpulse). They are evidence, not truth: re-check a claim before acting on it.

Owner card answers (2026-10-11, decision taken by question card):
- Idle compaction: KEEP it, adapt the ritual (hand off on idle unprompted; file lessons as learned; recover handoff from transcript after a compaction).
- New skills this cycle, owner-named: `clone-landing-commits`, `live-debugging-proof-harness`, `night-shift-orchestration`, and a review-sheet skill whose shape awaits a trade study. Owner typed: "And let's make these skills have great, clear names".
- Disk: delete clean stray clones AND compact the WSL disk; plus design how to use the machine's many other SSDs.
- Telemetry: deep design pass first (SQLite / RimPulse / VictoriaMetrics / Grafana); 1/min is too slow for bridge live tests at speed 3.

Rules:
- Work in /home/mandrake/rm/bench. Other agents are writing in the same clone at the same time: touch ONLY the paths your brief names. Never `git add -A`/`.`, never `reset --hard`, `checkout --`, `stash`, `--autostash`. Keep file writes and git commands in SEPARATE Bash calls (hooks refuse compound commands whole).
- Publish each finished unit: `git add -- <new files>` (untracked files only), then `git commit <explicit paths> -F <msgfile>`, then `LAND_REPO=/home/mandrake/rm/bench /home/mandrake/.seat-tmp/land.sh <sha> <paths>` (prints PUBLISHED <sha>). Do NOT `git pull --rebase` in this clone (the tree is dirty with served sheet files; that is a known root cause someone else is fixing). Commit messages: subject + ≤2 lines, ending with
  Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
- Files outside git (~/.claude, memory dir, ~/dev/Lodestar, ~/dev/Machinist): back up before deleting (tar into ~/.claude/backups/weekly_cleaning_2026-10-11/), and ~/dev repos get their own commit+push with explicit paths.
- Create your progress file as a SKELETON FIRST, update it per milestone (600 s silence kills you). Foreground commands only; never background-and-wait. Never `pkill -f` (kills your own shell); kill by PID.
- Skills: use the skill-creator skill's guidance for SKILL.md structure (frontmatter name + trigger-form description ≤1024 chars, lean SKILL.md, detail in references/). Project skills live in /home/mandrake/rm/bench/skills/<name>/ and are wired by a symlink in .claude/skills/ (check how existing ones are wired and copy that). Update skills/README.md roster lines for anything you add/remove (one line each; another agent rewrites the README's stale header — touch only roster rows).
- Owner rulings quoted verbatim must survive any move. Wrong content is deleted, not annotated.
- Report back in ≤8 lines: what changed, PUBLISHED shas, anything left for the owner.
