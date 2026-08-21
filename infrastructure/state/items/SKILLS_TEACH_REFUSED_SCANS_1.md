## spec
15 sites across 9 skills instruct an agent to run `strings <dll> | grep …`,
`grep <pattern> <save>.rws` or `grep <pattern> Player.log`. All are refused by
`.claude/hooks/block_blind_scan.py` as of 2026-08-21, so the agent hits a wall
and the skill is simply wrong. Audited 2026-08-21; ranked by how likely a seat
is to hit them.

🔴 **The sharpest one first — a TOOL that prints refused advice:**
  `skills/rimworld-quests/scripts/validate_quest.py:519` prints
  *"the namespace with: strings <mod>/Assemblies/*.dll | grep {short}"* as its
  own remediation text. A validator telling you to run a refused command is the
  worst version of this.

Then, in order:
  `skills/rimbridge/SKILL.md:177`          the tool census — this is the exact
                                           16-of-115 incident, framed as the gate
  `skills/rimworld-savegame/SKILL.md:30,35` headline §2 teaches grepping a .rws
  `skills/rimworld-debug-testing/SKILL.md:240` and `references/disk-vs-runtime.md:92`
  `skills/rimworld-quests/references/mod_patterns.md:45,273,274`  274 is a
                                           "run on every quest def before it ships" gate
  `skills/rimworld-quests/SKILL.md:371`
  `skills/rimworld-modding/references/player-log-triage.md:10`   step 1 of triage
  `skills/rimworld-quests/references/vanilla_corpus.md:374`
  `skills/rimworld-ideoligion/references/validation.md:290,371`
  `skills/rimworld-modding/references/traps-xml-and-defs.md:45`
  `skills/rimworld-xenotypes/references/closure.md:83`
  `skills/rimworld-world-editing/references/debug-surface.md:79`
  `skills/rimbridge/references/traps.md:61`

✅ **The model to copy is already in the repo:** `skills/rimbridge/references/traps.md:465`
already says *"⛔ Not a grep of the `.rws`"* and names the right tool. Every fix
should read like that line.

⚠️ For a LITERAL-string search the command is still correct — the fix there is to
say `MEASURE_ALLOW_SCAN=1` and why, not to delete the advice. `rimworld-savegame`
is the main case: its `grep '<def>NAME</def>'` idiom is legitimate.

## verify
for each of the 15 sites, feed the command it teaches through
`.claude/hooks/block_blind_scan.py` and confirm it is either no longer taught, or
taught with the MEASURE_ALLOW_SCAN override and a one-line reason. Paste the
before/after for the three ranked highest.

## criteria
an agent following any skill in the repo never composes a command the hook
refuses without the skill having told it why and what to run instead.

## notes
Filed by BUILD 2026-08-21 from three audits run after the owner asked
whether the new instrument was actually adopted. It was not.
