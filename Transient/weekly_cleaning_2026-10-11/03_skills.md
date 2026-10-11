# 03 — Skills audit (weekly cleaning 2026-10-11)

Auditor dimension: skills. Read-only; this file is the only write.

## 0. Method and measurements

All numbers below came from python scripts run this session (scratchpad `inv.py`, `use.py`, `stale.py`, `topics.py`), not from grep counts.

- **Inventory:** `/home/mandrake/rm/bench/skills/` has **34 skill dirs** plus `README.md` and `validate_skills.py`. The brief said 36; the extra two are those files. `~/.claude/skills/` has **44 symlinks** plus `synced/`, which holds two claude.ai-synced buckets of **13 and 21 skills**. The `anthropic-skills:*` entries come from there.
- **Wiring:** `.claude/skills/` holds **33 symlinks**. It covers 32 of the 34 project skills and adds `review-sheets` by absolute path. The two project skills with no symlink are:
  - `scaled-game-image-review`, which is real and used, so it is a gap.
  - `README.md`, which is not a skill.
- **Usage over the last 30 days (MEASURED):** `use.py` streamed **4,035** transcript jsonl files under `~/.claude/projects/{-home-mandrake-rm-bench,-home-mandrake-rm-foundry,-mnt-d-Luke-dev-RimMandrake}`, keeping files modified in the last 30 days. It counted two things:
  - `Skill` tool invocations, matched by `"name":"Skill","input":{"skill":"X"`.
  - `tool_use` lines that name `skills/X/SKILL.md`, meaning the file was opened by path.

  Scope is RimMandrake transcripts only, so global skills used in other projects read low here, and that is expected.
- **`validate_skills.py`** (run as-is) reports **6 ERRORs and 3 WARNs**: dead `jawa/` tool names in rimbridge, rimbridge-companion and rimworld-live-review; `gravship-layout` and `rimbridge` bodies over 500 lines; and the unreferenced `generating-images/references/queue_worker_AGENTS.md`.
- **Listing visibility (OBSERVED in this session's own skill listing):** only **26 of 77** user, project and global skills (plus the `broadcast` command) showed their description. The other **51 appeared name-only**: 13 project skills and 38 global ones. A name-only skill can only fire when someone names it.
  - The total description text installed is about **58 K chars** (project 24.8 K, global 33.5 K). The synced buckets add another 22.7 K, of which about half is the same skills twice.
  - I did not establish the harness's selection rule, so the mechanism is UNMEASURED. The likely cause is a listing size budget. Description volume is now a cost: every long description pushes another skill out of view.

## 1. Inventory table

Some columns need a key:
- **invoked / opened** means `Skill`-tool invocations / tool_use lines naming its SKILL.md, over 30 days of RimMandrake transcripts.
- **description** gives the description's character count, and whether it was shown in this session's listing or name-only.
- **source** for a global skill is the symlink target repo.

| skill | home | source | SKILL.md lines | total (text files) | description | invoked / SKILL.md opened (30d) | last SKILL.md commit | staleness signals |
|---|---|---|---|---|---|---|---|---|
| `agent-fanout-research` | project | skills/agent-fanout-research | 228 | 13 KB / 1 f | 633 ch; NAME-ONLY in listing | 0 / 3 | 2026-10-01 | 0 invocations/30d; overlaps efficient-subagents |
| `calibrating-binary-formats` | project | skills/calibrating-binary-formats | 187 | 9 KB / 1 f | 652 ch; NAME-ONLY in listing | 0 / 3 | 2026-10-02 | 0 invocations/30d; generic |
| `deciding-and-superseding` | project | skills/deciding-and-superseding | 269 | 20 KB / 2 f | 724 ch; desc shown | 9 / 24 | 2026-10-11 |  |
| `editing-images` | project | skills/editing-images | 159 | 12 KB / 2 f | 480 ch; desc shown | 22 / 15 | 2026-09-23 |  |
| `efficient-subagents` | project | skills/efficient-subagents | 298 | 16 KB / 1 f | 254 ch; desc shown | 29 / 51 | 2026-10-02 | generic; carries a model-ladder note though CLAUDE.md says ladder lives only in Agent_Policy.md |
| `frozen-artifacts` | project | skills/frozen-artifacts | 207 | 11 KB / 1 f | 934 ch; NAME-ONLY in listing | 3 / 4 | 2026-10-02 | generic |
| `generating-images` | project | skills/generating-images | 235 | 177 KB / 17 f | 519 ch; desc shown | 18 / 26 | 2026-09-23 |  |
| `generating-rimworld-sprites` | project | skills/generating-rimworld-sprites | 384 | 61 KB / 6 f | 515 ch; desc shown | 86 / 124 | 2026-10-11 | cites retired POLICY.md (line 353) |
| `gravship-layout` | project | skills/gravship-layout | 511 | 33 KB / 2 f | 334 ch; desc shown | 2 / 8 | 2026-09-04 | 511 L (>500); last edit 2026-09-04; 2 uses/30d |
| `reading-rimworld-graphics` | project | skills/reading-rimworld-graphics | 377 | 18 KB / 1 f | 492 ch; desc shown | 20 / 51 | 2026-09-23 |  |
| `rimbridge` | project | skills/rimbridge | 575 | 221 KB / 11 f | 379 ch; desc shown | 110 / 270 | 2026-10-10 | SKILL.md 575 L (>500); validate_skills: 2 dead tool names in references/silent-failures.md; mirror path; "~25 min" load figure x2 (CLAUDE.md now ~15 min) |
| `rimbridge-companion` | project | skills/rimbridge-companion | 260 | 19 KB / 2 f | 632 ch; desc shown | 27 / 82 | 2026-10-02 | validate_skills: 2 dead tool names |
| `rimworld-canon-references` | project | skills/rimworld-canon-references | 255 | 13 KB / 1 f | 762 ch; desc shown | 13 / 37 | 2026-10-09 |  |
| `rimworld-content-moderation` | project | skills/rimworld-content-moderation | 375 | 21 KB / 1 f | 894 ch; NAME-ONLY in listing | 8 / 27 | 2026-09-29 |  |
| `rimworld-crew-and-nemesis-events` | project | skills/rimworld-crew-and-nemesis-events | 106 | 16 KB / 3 f | 1351 ch; NAME-ONLY in listing, >1024 | 0 / 8 | 2026-10-10 | description 1351 chars (>1024 spec limit) |
| `rimworld-custom-incidents` | project | skills/rimworld-custom-incidents | 94 | 22 KB / 3 f | 1020 ch; NAME-ONLY in listing | 0 / 7 | 2026-10-10 | description 1020 chars (at limit) |
| `rimworld-debug-testing` | project | skills/rimworld-debug-testing | 497 | 36 KB / 3 f | 760 ch; desc shown | 80 / 110 | 2026-10-11 | 497 L; cites retired infrastructure/agents/POLICY.md (line 34) |
| `rimworld-deploy` | project | skills/rimworld-deploy | 373 | 22 KB / 1 f | 976 ch; desc shown | 26 / 88 | 2026-10-11 |  |
| `rimworld-ideoligion` | project | skills/rimworld-ideoligion | 278 | 111 KB / 5 f | 1011 ch; NAME-ONLY in listing | 2 / 5 | 2026-10-02 | references/validation.md has 6 /mnt/d/Luke/dev/RimMandrake paths (mirror is read-only since 2026-10-02; line 67 `cd` into it) |
| `rimworld-layout-layers` | project | skills/rimworld-layout-layers | 341 | 41 KB / 4 f | 808 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-04 | 0 uses/30d; last edit 2026-09-04; missing from README seat table |
| `rimworld-live-review` | project | skills/rimworld-live-review | 444 | 26 KB / 1 f | 950 ch; desc shown | 10 / 109 | 2026-10-11 | validate_skills: 2 dead tool names (jawa/get_cell_info, jawa/clear_log) |
| `rimworld-load-round` | project | skills/rimworld-load-round | 378 | 21 KB / 1 f | 866 ch; desc shown | 63 / 163 | 2026-10-11 | "~25 min" in description area; CLAUDE.md MEASURED ~15 min 2026-09-07 |
| `rimworld-modding` | project | skills/rimworld-modding | 452 | 328 KB / 16 f | 645 ch; desc shown | 73 / 108 | 2026-09-23 | "~25 min" figure; duplicated by stale claude.ai-synced copy anthropic-skills:rimworld-modding (2026-09-17 snapshot) |
| `rimworld-quests` | project | skills/rimworld-quests | 429 | 165 KB / 5 f | 904 ch; desc shown | 13 / 37 | 2026-09-23 | mirror path x1; "~25 min" figure |
| `rimworld-savegame` | project | skills/rimworld-savegame | 221 | 12 KB / 1 f | 824 ch; desc shown | 25 / 21 | 2026-09-23 |  |
| `rimworld-scenario-building` | project | skills/rimworld-scenario-building | 192 | 11 KB / 1 f | 557 ch; NAME-ONLY in listing | 0 / 0 | 2026-08-15 | last edit 2026-08-15; 0 uses/30d |
| `rimworld-scene-composition` | project | skills/rimworld-scene-composition | 220 | 16 KB / 1 f | 648 ch; NAME-ONLY in listing | 0 / 1 | 2026-09-06 | 0 invocations/30d |
| `rimworld-sprite-facings` | project | skills/rimworld-sprite-facings | 348 | 24 KB / 2 f | 506 ch; NAME-ONLY in listing | 0 / 23 | 2026-09-27 |  |
| `rimworld-start-prep` | project | skills/rimworld-start-prep | 452 | 48 KB / 2 f | 1013 ch; desc shown | 12 / 24 | 2026-09-23 |  |
| `rimworld-world-editing` | project | skills/rimworld-world-editing | 414 | 112 KB / 9 f | 768 ch; desc shown | 15 / 57 | 2026-09-23 | "~25 min" figure |
| `rimworld-xenotypes` | project | skills/rimworld-xenotypes | 492 | 39 KB / 4 f | 917 ch; NAME-ONLY in listing | 1 / 15 | 2026-10-02 | "~25 min" figure; 492 L |
| `scaled-game-image-review` | project | skills/scaled-game-image-review | 131 | 10 KB / 1 f | 772 ch; NAME-ONLY in listing | 0 / 46 | 2026-10-08 | NOT WIRED: no .claude/skills symlink, absent from listing; owed art.py enact pointer (lesson 20261008T174112Z) |
| `using-rimflow` | project | skills/using-rimflow | 262 | 15 KB / 1 f | 594 ch; desc shown | 272 / 120 | 2026-10-11 |  |
| `verify-before-you-escalate` | project | skills/verify-before-you-escalate | 168 | 8 KB / 1 f | 690 ch; NAME-ONLY in listing | 0 / 13 | 2026-09-23 | 0 invocations/30d; generic (0 RimMandrake refs); overlaps global confident-wrong-numbers |
| `blind-evaluation` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/blind-evaluation | 238 | 14 KB / 1 f | 890 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-29 |  |
| `claim-provenance` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/claim-provenance | 251 | 17 KB / 1 f | 1221 ch; NAME-ONLY in listing, >1024 | 0 / 0 | 2026-09-29 | desc 1221 chars |
| `claude-remote-control` | global | D:\Luke\dev\ claude-remote-control | 269 | 41 KB / 7 f | 770 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-02 | 45 BENCH/FOUNDRY/RimMandrake refs in a global skill (machine-specific, acceptable) |
| `confident-wrong-numbers` | global | D:\Luke\dev\ confident-wrong-numbers | 125 | 37 KB / 4 f | 566 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-05 |  |
| `consult-jev` | global | D:\Luke\dev\ ConsultJev | 153 | 1073 KB / 12 f | 1383 ch; NAME-ONLY in listing, >1024 | 1 / 4 | 2026-09-28 | desc 1383 chars (>1024) |
| `defeat-recitation` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/defeat-recitation | 202 | 13 KB / 1 f | 1118 ch; NAME-ONLY in listing, >1024 | 0 / 0 | 2026-09-29 | desc 1118 |
| `delegate-router` | global | D:\Luke\dev\ DispatchOpenCode/skills/delegate-router | 180 | 10 KB / 1 f | 855 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-01 |  |
| `dialexis-access` | global | D:\Luke\dev\ Dialexis/.claude/skills/dialexis-access | 186 | 10 KB / 1 f | 912 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-07 |  |
| `dialexis-architecture` | global | D:\Luke\dev\ Dialexis/.claude/skills/dialexis-architecture | 160 | 17 KB / 3 f | 577 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-07 |  |
| `dialexis-ingestion` | global | D:\Luke\dev\ Dialexis/.claude/skills/dialexis-ingestion | 99 | 6 KB / 1 f | 695 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-07 |  |
| `dialexis-kairos` | global | D:\Luke\dev\ Dialexis/.claude/skills/dialexis-kairos | 141 | 8 KB / 1 f | 664 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-11 |  |
| `evaluation-independence` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/evaluation-independence | 222 | 14 KB / 1 f | 818 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-27 |  |
| `evidence-bound-papers` | global | D:\Luke\dev\ EvidenceBoundPapers | 248 | 3867 KB / 237 f | 1175 ch; NAME-ONLY in listing, >1024 | 0 / 0 | 2026-09-14 | desc 1175; 237 files/3.9 MB tree |
| `falsifiable-claims` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/falsifiable-claims | 185 | 11 KB / 1 f | 1002 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-03 |  |
| `git-efficiency` | global | D:\Luke\dev\ git_efficiency/git-efficiency | 322 | 18 KB / 1 f | 792 ch; desc shown | 111 / 6 | 2026-10-02 |  |
| `grader-validation` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/grader-validation | 192 | 12 KB / 1 f | 965 ch; NAME-ONLY in listing | 1 / 0 | 2026-09-27 |  |
| `handoff` | global | D:\Luke\dev\ Lodestar/docs/handoff | 219 | 13 KB / 1 f | 720 ch; desc shown | 71 / 0 | 2026-10-06 |  |
| `ideogram` | global | D:\Luke\dev\ Ideogram/.claude/skills/ideogram | 504 | 65 KB / 5 f | 1160 ch; NAME-ONLY in listing, >1024 | 0 / 0 | 2026-10-07 | 504 L; desc 1160 |
| `image_scaling` | global | D:\Luke\dev\ image-scaling | 132 | 8 KB / 2 f | 475 ch; NAME-ONLY in listing | 1 / 13 | 2026-10-04 |  |
| `incomplete-ground-truth` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/incomplete-ground-truth | 205 | 13 KB / 1 f | 1205 ch; NAME-ONLY in listing, >1024 | 0 / 0 | 2026-09-27 | desc 1205 |
| `knowledge-registry` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/knowledge-registry | 214 | 24 KB / 2 f | 1087 ch; NAME-ONLY in listing, >1024 | 0 / 0 | 2026-09-03 | desc 1087 |
| `measuring-large-artifacts` | global | D:\Luke\dev\ measuring-large-artifacts | 293 | 316 KB / 19 f | 700 ch; desc shown | 16 / 41 | 2026-09-27 |  |
| `meeting-transcripts` | global | D:\Luke\dev\ Lodestar/docs/meeting-transcripts | 46 | 3 KB / 1 f | 570 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-07 |  |
| `nemotron-delegate` | global | D:\Luke\dev\ Nemotron_Bridge/skills/nemotron-delegate | 214 | 10 KB / 1 f | 613 ch; NAME-ONLY in listing | 0 / 0 | 2026-08-26 | last edit 2026-08-26 |
| `nemotron-image` | global | D:\Luke\dev\ Nemotron_Bridge/skills/nemotron-image | 49 | 2 KB / 1 f | 656 ch; NAME-ONLY in listing | 0 / 0 | 2026-08-26 | last edit 2026-08-26 |
| `option-portfolio` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/option-portfolio | 178 | 15 KB / 2 f | 864 ch; desc shown | 4 / 0 | 2026-09-03 |  |
| `parallel-agent-worktrees` | global | D:\Luke\dev\ parallel-agent-worktrees | 153 | 11 KB / 2 f | 1083 ch; NAME-ONLY in listing, >1024 | 0 / 2 | 2026-10-02 | teaches worktrees; RimMandrake has worktrees OFF (owner 2026-10-02) — can trigger against policy here; desc 1083 chars |
| `placard` | global | D:\Luke\dev\ Placard | 182 | 744 KB / 71 f | 806 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-06 |  |
| `question-card` | global | D:\Luke\dev\ QuestionCard | 282 | 33 KB / 3 f | 486 ch; desc shown | 47 / 2 | 2026-09-29 |  |
| `relevant-transcripts` | global | D:\Luke\dev\ Relevant_Transcripts/.claude/skills/relevant-transcripts | 240 | 14 KB / 1 f | 968 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-07 |  |
| `resumable-batch-jobs` | global | D:\Luke\dev\ resumable-batch-jobs | 244 | 17 KB / 2 f | 547 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-06 |  |
| `review-sheets` | global | D:\Luke\dev\ review-sheets | 475 | 192 KB / 13 f | 658 ch; desc shown | 50 / 78 | 2026-09-23 | also wired into project .claude/skills (double-wired) |
| `scientific-visualization` | global | D:\Luke\dev\ MandrakeVisualize/skills/v0.1/scientific-visualization | 141 | 7 KB / 1 f | 374 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-08 |  |
| `search-when-words-differ` | global | D:\Luke\dev\ search-when-words-differ | 231 | 14 KB / 2 f | 490 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-29 |  |
| `validity-floors` | global | D:\Luke\dev\ MandrakeVisualize/skills/epistemic/validity-floors | 179 | 11 KB / 1 f | 933 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-03 |  |
| `verify-model-quotes` | global | D:\Luke\dev\ verify-model-quotes | 237 | 15 KB / 2 f | 685 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-29 |  |
| `visual-beautiful` | global | D:\Luke\dev\ MandrakeVisualize/skills/beautiful/visual-beautiful | 173 | 10 KB / 1 f | 647 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-08 |  |
| `visual-composition` | global | D:\Luke\dev\ MandrakeVisualize/skills/v0.1/visual-composition | 112 | 5 KB / 1 f | 304 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-08 |  |
| `visual-critic` | global | D:\Luke\dev\ MandrakeVisualize/skills/v0.1/visual-critic | 119 | 5 KB / 1 f | 341 ch; NAME-ONLY in listing | 0 / 0 | 2026-08-28 |  |
| `visual-encoding` | global | D:\Luke\dev\ MandrakeVisualize/skills/v0.1/visual-encoding | 111 | 5 KB / 1 f | 322 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-08 |  |
| `visual-intent` | global | D:\Luke\dev\ MandrakeVisualize/skills/v0.1/visual-intent | 122 | 6 KB / 1 f | 496 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-08 |  |
| `visual-portfolio` | global | D:\Luke\dev\ MandrakeVisualize/skills/v0.1/visual-portfolio | 237 | 14 KB / 1 f | 614 ch; NAME-ONLY in listing | 0 / 0 | 2026-09-03 |  |
| `visual-render-qa` | global | D:\Luke\dev\ MandrakeVisualize/skills/v0.1/visual-render-qa | 148 | 8 KB / 1 f | 364 ch; NAME-ONLY in listing | 0 / 0 | 2026-10-08 |  |
| `web-access` | global | D:\Luke\dev\ Fetcher/.claude/skills/web-access | 143 | 9 KB / 1 f | 882 ch; NAME-ONLY in listing | 15 / 0 | 2026-10-07 |  |


**Synced from claude.ai (not repo-controlled):**
- Bucket `ababdd57…` (13 skills) and bucket `bcd47911…` (21 skills) overlap on **13 identical skills** (docs, docx, pdf, pptx, xlsx, skill-creator, built-in-browser, chrome-browser, computer-use, deep-research, google-workspace, import-memory, morning).
- Bucket `bcd47911…` also carries **`rimworld-modding`**. That is a 2026-09-17 snapshot: 371 lines, references `traps.md`, `patch-operations.md`, `csharp-and-loading.md` and `validate_patch.py`. Its description is older than the project's: it lacks "ParentName or abstract def", and it still claims "ModsConfig/RimSort load order", which now belongs to `rimworld-start-prep`. It surfaces as `anthropic-skills:rimworld-modding` and competes with the live project skill on the same trigger.

**`skills/README.md` is stale in four places** (last commit 2026-10-10 `df5fbff2c`, roster regenerated; the prose was not):
1. **Lines 41–70** keep the **four-seat ownership table** (DECIDE/BUILD/CHECK/REP) and point to `infrastructure/agents/POLICY.md`. Both were superseded on 2026-08-27 by CHARTER and the BENCH/FOUNDRY windows. The table carries a "SUPERSEDED IN PART" banner, but the owner's rule is to delete wrong material, not label it.
2. **Line ~24**: "Verified 2026-08-23: 25 skills in this repo + 1 … = 26 symlinks". The measured count today is 34 dirs and 33 symlinks, with one project skill unwired.
3. **The "Three skills live OUTSIDE this repo" section** lists 3 skills. `~/.claude/skills` has 44.
4. **The closing section** says "Editing `skills/<name>/` is not shipping it. Claude Code installs from a `.skill` zip". That is false. The README's own opening section says discovery is the `.claude/skills/<name>` symlink, and MEMORY.md says "editing skills/<name> IS installing it". The `.skill` zip only feeds claude.ai uploads, which is how the stale synced copy of `rimworld-modding` got there.

## 2. SPLIT candidates

| skill | evidence | proposed split | risk if wrong |
|---|---|---|---|
| `rimbridge` (575 L, 222 KB with 10 refs) | `validate_skills` WARN >500. §0b "Claim the bridge" (lines 46–109, 64 L) duplicates `using-rimflow`'s bridge-lock section. §1 Connect is 134 L. | (a) **Move §0b** to `using-rimflow` and leave a 2-line pointer. (b) **Move §1 Connect** detail into `references/connect.md`; SKILL.md keeps the 10-line happy path. (c) §8 Speed and §6 Macros go to `references/`. Target is ≤350 L. No new skill name: the trigger stays the same. | Low. This is the top-used bridge skill (110 invocations, 270 opens), so the description must not change. |
| `rimworld-debug-testing` (497 L) | Covers two distinct procedures. **(i)** Running a quicktest and what it proves (§1–6). **(ii)** Writing a validation plan, its thresholds and closing bars (§7 validation plan, §8 advising, §9 threshold discipline), plus §4b and `references/long-proofs.md` on long live proofs. §4a "LOOK AT IT" overlaps `rimworld-live-review`. | New **`rimworld-live-proof-harness`**, proposed in §5: §4b, §7 and §9, `references/long-proofs.md`, and `rimworld-modding/references/validation-plan.md`, which is a third copy of the same theme. `rimworld-debug-testing` keeps §1–6 and §8. §4a shrinks to a pointer to `rimworld-live-review`. | Medium. The 80 invocations and 110 opens rely on the current trigger, so the description must keep "a long live proof on the full mod list keeps failing" until the new skill's trigger is proven. |
| `gravship-layout` (511 L) | WARN >500. Only 2 invocations and 8 opens in 30 days. Last edit 2026-09-04. | Do **not** split it into new skills. Move §"Validation plan" (424–501) and §"FOUR GATES" (357–423) into `references/`. | Low. It is rarely used, so splitting costs more than it saves. |
| `rimworld-xenotypes` (492 L) | Close to the limit. §10 "Moving species between mods" is a separate procedure (porting). | Move §10 into `references/moving-species.md`. No new skill. | Low. |
| `rimworld-modding` (452 L + 14 refs, 336 KB) | It is already split into references. Its §2 "restart is scarce" overlaps `rimworld-load-round`, and §6 "Deploying" overlaps `rimworld-deploy`. | Shrink §2 and §6 to pointers to the owning skills. Delete `references/validation-plan.md`, which moves to the proof-harness skill. | Low. |
| `rimworld-start-prep` (452 L) | One coherent procedure. | KEEP. | — |

## 3. PROMOTE / PULL-DOWN candidates

**Promote out of RimMandrake.** Each target is `~/dev/Machinist` or a dedicated `~/dev/<name>` repo, symlinked by absolute path the way `measuring-large-artifacts` is.

| skill | RimMandrake refs (MEASURED) | action | why | risk |
|---|---|---|---|---|
| `verify-before-you-escalate` | 0 refs, 1,521 words | PROMOTE, then MERGE into global `confident-wrong-numbers`, or keep standalone in Machinist | Fully generic. It has 0 invocations in 30 days because its trigger area is shadowed by `confident-wrong-numbers`. | Low. Only 13 opens, all by path, so update those docs. |
| `frozen-artifacts` | 5 refs | PROMOTE | Generic: protecting human-decision files from generators. `review-sheets` (global) already depends on the idea. | Low. |
| `calibrating-binary-formats` | 9 refs (examples) | PROMOTE, keep the RimWorld examples as one worked case | Generic method. 0 invocations here. | Low. |
| `deciding-and-superseding` | 1 ref | PROMOTE | Generic decision-propagation discipline. Lodestar-run projects need it too. | Low, but it is edited in this repo often (last commit today), so move it at a quiet moment. |
| `efficient-subagents` + `agent-fanout-research` | 2 refs / 1 ref | PROMOTE both, then MERGE (§4) | Generic subagent scoping. The owner's global CLAUDE.md already holds the fan-out policy these serve. | Medium. `efficient-subagents` has 29 invocations; keep the name. |
| `generating-images` + `editing-images` | 8 / 4 refs | PROMOTE | Driving Codex `$imagegen` is machine-level tooling. `generating-rimworld-sprites` stays in the project and wraps them. | Medium. The Codex staging path `D:\Luke\dev\_rmscratch\codex` is RimMandrake's, so parameterise it. |

**Pull down from global (RimMandrake specifics baked into a global skill):**
- `claude-remote-control` has 45 BENCH/FOUNDRY/RimMandrake refs. It is machine-specific by design and its README says so. KEEP.
- `parallel-agent-worktrees` is a global skill that teaches worktree dispatch, while RimMandrake has **worktrees OFF** (owner, 2026-10-02, by card), enforced by `block_worktrees.py`. It was opened 2 times in 30 days here.
  - Action: add a one-line "projects may ban worktrees; check the repo's CLAUDE.md" guard to its own repo. Alternatively, accept that the hook catches it.
  - Do not pull it down; it is generic.
- None of the others carries RimMandrake specifics: `git-efficiency` has 2 refs, `measuring-large-artifacts` 8 and `image_scaling` 7, all as examples.

**Installed but not wired (global):**
- `~/dev/ChatGPTConsult/SKILL.md` (`name: chatgpt-consult`, last commit 2026-10-10) exists but is **not in `~/.claude/skills`**. MEMORY.md still says "no skill by that name exists". The project's `gpt_consult.py` and 7 GPT/codex lessons cover the same ground. See §5.
- `~/dev/Lodestar/docs/bearing` and `jpl-weblore` have SKILL.md files and are not linked. They are outside RimMandrake scope; noted only.
- 🔴 **`~/.claude/CLAUDE.md` line 14 points at "the `wsl-windows-plumbing` skill", which does not exist.** I searched `~/.claude`, `~/dev/Machinist` and `~/dev/Lodestar` (depth 5): no hit. It is a dangling pointer in global rules, so either write the skill or delete the pointer (Q3).

## 4. MERGE / DELETE candidates

| target | action | why (evidence) | risk |
|---|---|---|---|
| `anthropic-skills:rimworld-modding` (claude.ai-synced, bucket `bcd47911…`, 2026-09-17) | DELETE from the claude.ai account, or re-upload the current version | A stale fork of a live project skill with the same trigger. Its description still claims load order, which now belongs to `rimworld-start-prep`. | Low. Only the owner's claude.ai account can remove it (Q2). |
| Duplicate synced buckets (13 skills in both `ababdd57…` and `bcd47911…`) | Owner decision | Two orgs or accounts sync the same Anthropic skills, so their descriptions take listing space twice. | UNMEASURED whether the harness dedupes them. |
| `agent-fanout-research` → into `efficient-subagents` | MERGE, as a `references/fanout-research.md` | 0 invocations and 3 opens in 30 days. Same domain: spawning agents, budgets, CONFIRMED-vs-UNCERTAIN. Two skills split the trigger. | Low. |
| `verify-before-you-escalate` → into `confident-wrong-numbers` (global) | MERGE, or promote standalone (§3) | 0 invocations. The "check a written claim before acting" trigger overlaps `confident-wrong-numbers` and `claim-provenance`. | Low. |
| `scaled-game-image-review` | KEEP, **WIRE NOW** (`ln -s ../../skills/scaled-game-image-review .claude/skills/`), then grow it (§5) | 46 opens by path, 0 invocations, because it is invisible. Lesson `20261008T174112Z-BENCH-enacting-ruled-art-sheet-one-command.md` records an owed curation edit pointing it at `art.py enact`. | None. The `warn_skill_unwired.py` hook should have caught this; I have not checked why it did not (UNMEASURED). |
| `rimworld-scenario-building` | KEEP, flag dormant | 0 uses, last edit 2026-08-15. Players receive a fixed savegame (CLAUDE.md), so scenario authoring is rare but not dead. | — |
| `rimworld-layout-layers`, `rimworld-scene-composition` | KEEP, flag dormant | 0 and 0–1 uses. Domain knowledge that is costly to rebuild. | — |
| `skills/README.md` four-seat table, "three outside skills" table, ".skill zip" closing section | DELETE those sections, replace them with 3 lines (wiring, curation-only edits, the generated roster) | Wrong as described in §1. The owner's rule is delete, not supersede. | Low. Keep the generated roster block. |
| `rimworld-debug-testing` line 34 and `generating-rimworld-sprites` line 353, both citing `infrastructure/agents/POLICY.md` | Re-point to `CHARTER.md` | POLICY.md was retired 2026-08-27. | Low. |
| `rimworld-ideoligion/references/validation.md` lines 18, 36, 67, 319 | Rewrite `/mnt/d/Luke/dev/RimMandrake` to repo-relative paths | The mirror has been read-only since 2026-10-02, and line 67 `cd`s into it to run a validator. | Low. |
| "~25 min" cold-load figure in rimbridge (2), load-round, modding, quests, world-editing, xenotypes | Correct to "~15 min (MEASURED 2026-09-07, 599 mods)" | CLAUDE.md supersedes it. | Low. Leave history notes alone. |
| Dead `jawa/` tool names (6, from `validate_skills.py`) | Fix them or delete the lines | The validator already says they are not real tools. | Low. |
| `generating-images/references/queue_worker_AGENTS.md` | Point at it from SKILL.md, or DELETE | Nothing references it (WARN). | Low. |

## 5. MISSING skills

Evidence base: newest 40 handoffs and all 299 lessons, keyword-classified by `topics.py` as file counts per topic. Counts below are "handoffs40 / lessons".

| proposed skill | trigger-form description | scope | contents | sources |
|---|---|---|---|---|
| **`landing-commits`** (git landing in seat clones) | "Use before any commit, push, `./publish` or `land.sh` in a RimMandrake seat clone, whenever `pull --rebase` refuses, a push is non-fast-forward, the clone reads ahead/behind with duplicates, selftests show phantom reds after landing elsewhere, or you are about to make a scratch clone." | project, with a generic half → `git-efficiency` | A decision tree: clean clone → `./publish`; dirty clone → `LAND_REPO=<clone> land.sh <sha> <paths>`. Then: proof by `merge-base --is-ancestor`; the `--autostash` strand trap; why pre-push ledger_lint judges local HEAD; stale-clone recovery when the reset hook refuses; scratch-clone cost (7–14 GB each, 18 strays = 276 GB) and `--reference`/`--filter`; deleting clones afterwards; the `land.sh` LAND_REPO default trap. Generic parts (temp-`GIT_INDEX_FILE` + `commit-tree` landing, autostash hazards) go upstream into `git-efficiency`. | 25/25 files. `design/RimMandrake/GIT_WORKFLOW.md` §"Landing when pull --rebase is refused" (an appended lesson list that belongs in a skill). `src/RimMandrake/Utils/land.sh`, `land_README.md`. Lessons `20261009T100707Z…land-sh-old…`, `20261010T164936Z…publish-runs…autostash`, `20261011T070420Z…land-sh-defaults…`, `20261010T235838Z…scratch-clone…`, `20261011T052223Z…seat-clone-recovery…`, `20261007T054859Z…never-git-clone…scratchpad`, `20261011T125553Z…pre-push…ledger-hook`. |
| **`rimworld-live-proof-harness`** | "Use when writing, running or reading a live proof of a mod: `proof_all.py`, a `northstar/` runner, `validation_core.py`, `modcheck` floors, `shows=` wiring, LogTap log budgets. Also use when two proof runs disagree, a proof goes stale, or a full-list log budget is blind." | project | The first-script contract from `debug_process.md`. Harness anatomy (`validation_core.py`, per-mod `northstar/`). Tier-labelled runs. Log budgets on 550+ mod lists. Staleness rules. Separating the harness's own failures from the mod's. What `modcheck` verbs mutate (`run` rewrites ModsConfig). Threshold and closing-bar discipline, moved from debug-testing. | 34/9 files. `design/RimMandrake/debug_process.md` (306 L). `src/RimMandrake/Utils/validation_core.py`. `src/RimMandrake/GimmeSomeSlack/northstar/proof_all.py`. `src/RimMandrake/FlowWorks/northstar/{proof_hose,validation_v2}.py`. `skills/rimworld-debug-testing/references/long-proofs.md`. Lessons `20261011T015018Z…proof-labelled-with-tier…`, `20261011T025641Z…log-budget-550…`, `20261011T142704Z…full-list-log-budgets…`, `20261005T155316Z…proof-run-goes-stale…`, `20261002T230900Z…northstar-driver…`. |
| **`review-sheet-lifecycle`** (grow `scaled-game-image-review` into it, or rename it) | "Use when serving, refreshing, remapping, enacting or retiring a RimMandrake review sheet: `serve_gated.py`, `refresh_sheets.py`, `remap_decisions.py`, `art.py enact`, a `.decisions.json`, a `*.serve.log`, or a sheet RimPulse does or does not list." | project, layered on global `review-sheets` | The lifecycle states (built → served → ruled → enacted → notes cleared → stopped). Serve-log rules: the LAST answering URL wins, and stdout must go to `<sheet>.serve.log` or RimPulse cannot see the sheet. `remap_decisions` when rows move. One-pass enact with `--hold`. Clearing followed notes. Never regenerate over a ruled sheet (pointer to `frozen-artifacts`). | 15/5 files. `src/RimMandrake/Utils/art/{serve_gated,refresh_sheets,remap_decisions}.py`. Lessons `20261011T064841Z…serve-log…several`, `20261011T060426Z…rimpulse-lists…`, `20261008T174112Z…enacting…one-command`, `20261009T054044Z…followed-sheet-notes…`. Memory `sheet-enactment-one-pass.md`, `followed-sheet-notes-must-be-cleared.md`. The ~30 `Transient/biome_ffar/*.serve.log` modified in git status show this churns daily. |
| **`night-shift-orchestration`** | "Use when the owner goes AFK or asleep and leaves a subagent count or cap, says 'thin orchestrator', 'belt', or 'keep N running', or when running a long autonomous queue with background agents." | global (Machinist), with a short RimMandrake overlay in BENCH.md or FOUNDRY.md | Recording the night's cap and expiry as data, not as a new memory file each night. The thin-orchestrator loop. Skeleton-first briefs (the 600 s silence watchdog). Foreground-only commands in helpers. Never `HANDOFF READY` from a subagent. Offline-only work while another window holds the bridge. Refilling slots. Handoff when dry. | 23/5 files. Eight dated memory files that are each one night's settings (`afk-night-2026-10-07…`, `…10-08…` ×2, `…10-10…` ×2, `…10-11…`, `thin-orchestrator-three-subagents…`, `two-subagents-keep-bridge-busy…`), a repeated procedure stored as eight memories. CLAUDE.md watchdog bullet. Lessons `20260929T164805Z…background-wait-deadlock…`, `20261011T125554Z…subagent-report-that-ends-handoff-ready`. |
| **`gpt-consult`**: wire the existing `~/dev/ChatGPTConsult` skill and reconcile it with project `gpt_consult.py` | Use the existing `chatgpt-consult` description. | global (already written) | Add the RimMandrake facts: `codex.exe` staging under `D:\Luke\dev\_rmscratch\codex`, high effort, `-m gpt-6.1-sol`, input truncation, inline inputs. | 0/7 lessons (`20261011T071444Z…gpt-consult-input-truncation`, `20261002T081258Z…codex-exe-needs-inline-inputs`, `20261002T230900Z…gpt-consult-with-no-live-process`). Memory `gpt-consult-via-codex-cli.md`, `gpt-consults-need-high-effort-and-sol.md`. |
| **`telemetry-time-series`** | Defer it. | — | Telemetry is **design-only**: `Transient/foundry_metrics_combined_20261010.md` says "Nothing is built or measured live." A skill now would encode guesses. Write it after option F's Windows-side observer exists, as part of building it. Then it covers schema rules (do not reset process counters, merge histograms rather than averaging p99s), and the blind spots: log cap, and heap delta ≠ allocation rate. | 4/1 files. |
| **disk watch** | Not a skill. | — | This is a timer or hook, not a procedure: one `df` threshold alarm in RimPulse. The one procedural part (clone cost, deleting clones) goes into `landing-commits`. | 0/1 files mention disk; the 276 GB event is recorded only in GIT_WORKFLOW.md. |
| `wsl-windows-plumbing` (named by global CLAUDE.md, absent) | "Use when a WSL process must reach Windows: `python.exe` vs `python3`, CRLF from `python.exe`, `/mnt/d` slowness and stale drvfs reads, loopback/NAT bridge reachability, opening pages with `powershell.exe Start-Process`, the WSL keepalive task." | global | Facts now scattered across CLAUDE.md "Instruments" bullets and memory files (`windows-python-misreads-wsl-absolute-paths`, `drvfs-stale-reads-mimic-revert`, `rimbridge_client` NAT). | Global CLAUDE.md line 14. RimMandrake CLAUDE.md CRLF/NAT bullets. MEMORY.md entries. |

## 6. skill-creator eval loop vs plain write

`skill-creator` is installed (`anthropic-skills:skill-creator` and `skill-creator:skill-creator`).

| proposed | method | why |
|---|---|---|
| `landing-commits` | **Full eval loop** | High frequency: 25 of 40 handoffs mention it. A wrong answer strands other agents' work (53 files in stash, 2026-10-10). It is also a trigger contest with `git-efficiency` (111 invocations), so the description must be tuned to win project landing questions without stealing generic git ones. |
| `rimworld-live-proof-harness` | **Full eval loop** | It is carved out of `rimworld-debug-testing` (80 invocations). The eval has to prove the split does not lose triggers either skill used to catch. |
| `review-sheet-lifecycle` | **Description-only eval** (skill-creator's trigger-optimisation step), body as a plain write | The body is a checklist of known facts. The risk is triggering against global `review-sheets` (50 invocations). |
| `night-shift-orchestration` | Plain write, then one eval round on trigger phrases ("AFK", "going to sleep", "belt", "keep N running") | The procedure is stable. The phrasings are the owner's and are known. |
| `gpt-consult` (wire existing) | Plain: `ln -s` plus a RimMandrake facts section | It already exists. |
| `wsl-windows-plumbing` | Plain write | A reference list of facts with no judgement. |
| All §2 splits | Plain moves into `references/`, with `validate_skills.py` before and after | Same names and descriptions, so no trigger change. |
| Listing-budget pass | **Description eval across all skills** | 51 of 77 skills were name-only in this session's listing. Shortening the 9 descriptions over 1,024 chars and trimming the rest is the highest-leverage trigger fix, and only an eval shows which skills regain visibility. |

## Top 10 actions, ranked by value

| # | target path | action | why | risk |
|---|---|---|---|---|
| 1 | `/home/mandrake/rm/bench/.claude/skills/scaled-game-image-review` | Create the symlink (WIRE) | The skill is used 46 times by path and is invisible to triggering. | None. |
| 2 | new `skills/landing-commits/`, plus `design/RimMandrake/GIT_WORKFLOW.md` §Landing | PROMOTE the lesson list to a skill and leave the doc with a pointer | Most-repeated pain: 25 git lessons, 25 of 40 handoffs, 276 GB of stray clones, stash strands. | Medium. Needs an eval against `git-efficiency`. |
| 3 | All skill descriptions; first the 9 over 1,024 chars (`consult-jev`, `rimworld-crew-and-nemesis-events`, `claim-provenance`, `incomplete-ground-truth`, `evidence-bound-papers`, `ideogram`, `defeat-recitation`, `knowledge-registry`, `parallel-agent-worktrees`) | Shorten | 51 of 77 skills showed name-only in the listing, so they cannot trigger on content. | Low per edit. The mechanism is UNMEASURED, so measure the listing again afterwards. |
| 4 | claude.ai account skill `rimworld-modding` (synced bucket `bcd47911…`) | DELETE or re-upload | A stale fork competing on the same trigger as the live skill. | Owner-only action (Q2). |
| 5 | new `skills/rimworld-live-proof-harness/`, carved from `rimworld-debug-testing` §4b, §7 and §9, plus `rimworld-modding/references/validation-plan.md` | SPLIT and MERGE | 34 of 40 handoffs touch proofs and northstar. Today it is spread across 3 skills and a 306-line design doc. | Medium. Needs an eval. |
| 6 | `skills/README.md` | DELETE the four-seat table, the "three outside skills" table and the `.skill`-zip claim; fix the counts | False statements read on every curation pass. | Low. |
| 7 | `~/.claude/CLAUDE.md` line 14 (`wsl-windows-plumbing`) | Write the skill or delete the pointer | A dangling pointer in the global rules. | Low. |
| 8 | `skills/rimbridge/SKILL.md` | SPLIT §0b into `using-rimflow` and §1, §6, §8 into `references/`; fix the 2 dead tool names and the 15-min figure | 575 lines, over the validator's limit. The most-opened skill (270 opens). | Low. Description unchanged. |
| 9 | `~/.claude/skills/chatgpt-consult` → `~/dev/ChatGPTConsult` | WIRE, and correct MEMORY.md's "no skill exists" | An existing skill not installed; 7 lessons rediscovered its facts. | Low. |
| 10 | `agent-fanout-research` → `efficient-subagents`; `verify-before-you-escalate` → `confident-wrong-numbers`; promote `frozen-artifacts`, `calibrating-binary-formats`, `deciding-and-superseding`, `generating-images`, `editing-images` to Machinist or their own repos | MERGE and PROMOTE | 0 to 3 invocations each. Generic skills taking project listing space. | Medium. Path references in docs must move with them. |

Also, small items: the POLICY.md cites at debug-testing line 34 and sprites line 353; the mirror paths in `rimworld-ideoligion/references/validation.md`; the 6 dead `jawa/` names from `validate_skills.py`; the "~25 min" figure in 6 skills.

## Questions only the owner can answer

1. **Where do promoted generic skills live?**
   (a) One repo, `~/dev/Machinist/skills/`.
   (b) One repo per skill under `~/dev/`, as `measuring-large-artifacts` already is.
   (c) Keep them in RimMandrake and only symlink them globally.
2. **The stale `rimworld-modding` copy on your claude.ai account (synced 2026-09-17):**
   (a) Delete it from claude.ai.
   (b) Re-upload the current version and keep it synced.
   (c) Leave it.
3. **`wsl-windows-plumbing`, named in your global CLAUDE.md but nonexistent:**
   (a) Write it now from the scattered CRLF/NAT/drvfs facts.
   (b) Delete the pointer.
4. **Night-run settings (subagent cap, offline-only, until when) are stored as a new memory file every night (8 so far):**
   (a) Make a `night-shift-orchestration` skill and record each night's numbers as one line in a state file.
   (b) Keep a memory file per night.
5. **Two claude.ai skill buckets sync the same 13 Anthropic skills onto this machine:**
   (a) Unsync one account or org.
   (b) Leave both.
6. **`landing-commits` scope:**
   (a) A project skill only.
   (b) A project skill, with the generic temp-index landing and autostash traps pushed up into global `git-efficiency`.
