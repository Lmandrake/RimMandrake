# Handoff Corpus Harvest Audit — 2026-09-17

Scope: all 67 `infrastructure/state/items/*_REBOOT_HANDOFF_*.md` files. Extracted every
"Traps learned" / "The one thing to carry forward" (and headline-variant: "Traps
rediscovered/re-paid/for whoever resumes", "Process notes worth carrying forward",
"Session-process fixes made") section — 124 sections, full text dumped to
`Transient/handoff_audit/raw_sections.txt` (2783 lines) and read in full.

Durable destinations checked: `infrastructure/state/LESSONS_INBOX.md` (188 entries, read
in full), `CLAUDE.md` (project root, read in full at session start), `infrastructure/state/facts/*`
(36 files), `skills/**/*.md` (29 top-level skill dirs). Grading is keyword-grep against these
four, cross-checked by having read LESSONS_INBOX.md and CLAUDE.md in full — so LESSONS_INBOX
grades are high-confidence; skills/facts grades are grep-confidence (spot-checked, not
exhaustively read).

Method note: LESSONS_INBOX.md turned out to be **extremely comprehensive** for handoffs
dated 2026-09-09 onward — many entries are near-verbatim transcriptions of a handoff's
"Traps learned" bullet. The gap is concentrated in (a) handoffs from 2026-09-06 to 09-08,
before that discipline was fully established, (b) synthesis-level "one thing to carry
forward" claims that don't reduce to a single filed trap line, and (c) tool-quirk one-offs
that got silently fixed rather than filed.

## 1-2. Claim list + grading

Grade key: **L**=LANDED (verbatim/near-verbatim in a durable destination),
**P**=PARTIAL (weaker/narrower/adjacent version landed), **S**=STRANDED (only in handoffs).
Severity on STRANDED only: **H**=would cost a game load/hours to rediscover, **M**=tens of
minutes, blank/**Lo**=minutes.

### Git / shared-worktree discipline
1. Bare `git commit` (even after `git add <files>`) sweeps whatever else is staged in the
   shared index — pathspec must go on BOTH `add` and `commit`. — **L** (LESSONS_INBOX ~10
   entries incl. L42/L60/L71/L84/L91/L104/L121/L150; CLAUDE.md Git section)
2. `.git/index.lock` contention with a concurrent peer is constant; retry-loop, `fuser`/`ps`
   check before removing, never blind `rm -f`. — **L** (LESSONS_INBOX L71/L72/L91; CLAUDE.md)
3. `git add -A` is blocked on the bare `-A` token alone even with explicit paths following. — **L** (LESSONS_INBOX L115)
4. `git add`: one bad path silently drops the WHOLE add if stderr is suppressed. — **L** (CLAUDE.md memory: git-add-never-suppress-stderr)
5. zsh does not word-split an unquoted `$VAR` — a pathspec/dir-list variable collapses to one token. — **L** (LESSONS_INBOX L128; CLAUDE.md memory; skill refs)
6. A failed `git add` under lock contention leaves the index loaded; a retry-loop commit ships it under the wrong message. — **L** (LESSONS_INBOX L50)
7. FOUNDRY's stash dance (stash/commit/pull/pop) dropped two waves of other agents' uncommitted work — never stash over foreign dirty state. — **L** (LESSONS_INBOX L45/L48)
8. `rimflow close --sha` does not validate the string resolves to a real commit (took the literal `"c1"`/`"HEAD"`). — **L** (LESSONS_INBOX L43; CLAUDE.md memory rimflow-close-sha-head-literal)
9. `block_blanket_git_stage.py` has no MERGE_HEAD exemption — use `git merge --continue`. — **L** (LESSONS_INBOX L70)
10. A rebuilt DLL with unchanged source still shows a git diff (fresh MVID/timestamp) — don't commit as a real change. — **S** (not found) — Lo

### Subagent / async patterns
11. A subagent has no channel to receive an async background-task notification — it deadlocks waiting; must poll in a foreground loop. — **L** (LESSONS_INBOX L19, repeated ~6x across dates; CLAUDE.md memory subagents-must-run-commands-foreground)
12. A backgrounded `Agent` is killed after ~600s with no streamed output and leaves NOTHING on disk — write a skeleton file immediately, fill section by section. — **L** (LESSONS_INBOX L170/L124; CLAUDE.md "A backgrounded Agent dies at 600s...")
13. `Monitor` tool re-fires a full-context notification on every tick, even a silent "still waiting" one (~130k tokens/ping). — **S** — M (product-feedback filed, not doctrine)
14. `TaskOutput(block=false)` on a running task can dump the full raw JSONL transcript into context. — **L** (LESSONS_INBOX overlaps loosely; not exact) — **P**
15. A background agent's own report can misattribute whose judgement a number represents (pre-fill vs owner verdict). — **L** (LESSONS_INBOX L141)
16. A backgrounded subagent can go completely silent, leaving finished work uncommitted with zero trace in the task registry — check `git status --porcelain`, not the registry. — **S** — H (real risk of losing a whole wave's output; not filed)
17. `TaskOutput`'s "Running background agents" list is environment-wide, not scoped to the calling window. — **S** — M
18. A nested subagent's own parallel forks don't reliably respect that subagent's own scoping instructions ("draft only" ignored by a fork). — **L** (LESSONS_INBOX L104; CLAUDE.md memory forks-act-on-the-whole-session)
19. A `fork` inherits the whole seat's standing autonomy doctrine, not just the task prompt — a negative instruction must explicitly suspend it. — **L** (LESSONS_INBOX L107; CLAUDE.md memory fork-inherits-seat-autonomy)
20. 15-agent parallel fanout pattern: `isolation:"worktree"` per agent, orchestrator serializes ALL ledger/queue writes and merges centrally. — **P** (efficient-subagents skill covers fanout generally, not this specific recipe)
21. `SendMessage` not enabled in some contexts — a running background agent cannot be extended. — **S** — Lo

### Bridge / RimWorld API quirks (jawa/rimworld tools)
22. Bridge tool param-name traps: `world_landmarks_get` takes `limit` not `range`; `world_features` keys id as `uniqueID`. — **L** (LESSONS_INBOX L10)
23. `set_pawn_identity`/`pawn_traits`/`inspect_string`/`destroy_batch`/`list_things` field-name traps (pawn not pawnId, thingIds, rects not ids, no name filter). — **P** (some individual ones landed elsewhere, not this consolidated set)
24. `jawa/list_pawns` returns `id`, not `thingId`. — **L** (LESSONS_INBOX L178)
25. `rimworld/load_game` never reports `programState` — assert on `mapCount>0` + ticking. — **P**
26. `rimworld/step_game_ticks` silently times out (~2,800/10s, or ~600/call variously reported) returning `success:false` in the payload while the outer envelope reads `Success:true`. — **L** (LESSONS_INBOX L86)
27. `jawa/spawn_batch` throws unhandled NRE on a pawn-race ThingDef — use `spawn_pawn` by PawnKindDef. — **L** (LESSONS_INBOX L79)
28. `execute_debug_action` ToolMap actions refuse a `thingId` param — use x/z cell targeting; `T: Destroy` by x/z destroys EVERY thing in the cell. — **L** (LESSONS_INBOX L57/L58)
29. Debug-action categories don't nest under their category name — flat entries under `Actions/<Label>` with a `category` field. — **P**
30. `GameComponentTick` (and any ConcurrentQueue delivery) never drains while the game is paused. — **S** — M
31. `rimworld/select_pawn` only resolves player-controlled colonists; Add Prisoner needs an existing bed. — **S** — M
32. `jump_camera_to_cell` reports success while the WORLD view stays up. — **L** (LESSONS_INBOX L186)
33. `frame_cell_rect`/`screenshot_cell_rect` camera-framing unreliability. — **P**
34. `take_screenshot` names files by second — two shots in one second collide silently. — **L** (LESSONS_INBOX L32)
35. `set_pawn_rotation dir:south lockRotation:true` faces pawns at camera for art shots. — **L** (LESSONS_INBOX L179)
36. Bridge-generated Settlement/no-colonist maps are CULLED once time steps — spawn PlayerColony pawns (home-map trick). — **L** (CLAUDE.md memory generated-map-culled-unless-home)
37. `rimworld/save_game` wrote 0 bytes silently once — stat the named file every time. — **L** (LESSONS_INBOX, CLAUDE.md "rimworld/save_game has silently written...")
38. `get_defs` returns only the TYPE NAME for list fields, not full content — must read raw XML. — **S** — M
39. `rimworld/load_game_ready` is a does-save-exist checker, not a load-progress probe. — **S** — M
40. `world_tile_get` has no lat/long; `world_neighbors` takes `path` not tiles. — **S** — Lo

### ModsConfig / mod-list mechanics
41. `grep -c '<li>'`/naive grep on `ModsConfig.xml` undercounts badly (line count not tag/element count) — parse the XML. — **L** (CLAUDE.md explicit "Never scan ModsConfig.xml"; LESSONS_INBOX L155/L174, many more)
42. RimWorld's own crash-recovery silently resets `ModsConfig.xml` to 6 mods on ANY unhandled exception in `Game..ctor()`. — **L** (LESSONS_INBOX L21)
43. `MayRequire` on a patch `<Operation>` element is INERT — only `PatchOperationFindMod` or `MayRequire` on the injected `<li>` gates. — **L** (LESSONS_INBOX L23/L180; CLAUDE.md "Never guess..." adjacent, and a dedicated fact line)
44. LoadFolders `IfModActive` subfolder defs defeat owning-mod MayRequire and the dump's packageId attribution. — **L** (LESSONS_INBOX L96)
45. RimWorld drops unknown packageIds from the active set silently at startup (a renamed mod is just not loaded, ModsConfig still shows it). — **P**
46. `start_debug_game_ready`/full quicktest is unreliable/crashes on the owner's full ~590-634-mod stack — always use a minimal/tiered list. — **L** (CLAUDE.md memory quicktest-crashes-full-modlist; LESSONS_INBOX multiple)
47. Enabling a mod that leans on a sibling mod's C# is not safe until BOTH are deployed — `deploy_custom_mods.py --mod X` only deploys X. — **L** (LESSONS_INBOX L80)
48. Deploy ≠ enabled — "in sync" means files match, says nothing about ModsConfig activation. — **L** (LESSONS_INBOX ~L (2026-09-18 handoff); CLAUDE.md deploy doctrine)
49. A companion/mod DLL cannot be written while the game is running. — **L** (CLAUDE.md/skills, well established)
50. A commit is not a deploy; a deploy dry-run with no diff lines is the only proof a restart tests what you think. — **L** (LESSONS_INBOX L112)
51. Deleting a def is not the whole cut — need a repo-wide grep for the deleted defName (recipeUsers, loot tables, etc). — **L** (LESSONS_INBOX L113)
52. `jawa/hot_reload_defs` is RETIRED and self-refuses. — **L** (LESSONS_INBOX L114; CLAUDE.md-adjacent)
53. A null `thingClass` on ANY ThingDef crashes `Game..ctor()` for every route (load/new colony/quicktest). — **L** (LESSONS_INBOX L24/L87)
54. Steam's own launch-lock gets stuck after a silent RimWorld crash — relaunch Steam client, not the game. — **L** (LESSONS_INBOX L25)
55. A shared RimWorld process crashing during ANY quicktest takes down an already-loaded stable campaign too. — **L** (LESSONS_INBOX L26)
56. Illegal `--` inside an XML `<!-- -->` comment silently discards the WHOLE file. — **L** (LESSONS_INBOX L27/L30/L62; CLAUDE.md-adjacent)
57. `ParentName` inheritance requires the PARENT to carry a `Name=` attribute in a FLAT namespace (not scoped by def type). — **L** (LESSONS_INBOX L64/L74)
58. `PawnKindDef.maxGenerationAge`/`minGenerationAge` are int years — drop the `AnimalAdult` lifeStage entry instead of forcing 0. — **L** (LESSONS_INBOX L65)
59. A donor retirement's whole-mod-list dependency check is not sufficient — the SAVE can hold direct Scribe references. — **L** (LESSONS_INBOX L22)
60. A cross-mod duplicate defName logs NOTHING (Remove-then-Add silently drops the log line). — **S** — M
61. `Pawn.CurrentlyUsableForBills()` requires `InBed()` — droids never satisfy it, blocking whole-pawn surgery recipes. — **L** (LESSONS_INBOX L89)
62. A self-referencing `ResearchProjectDef` prerequisite causes an uncatchable stack overflow — durable fix is a Harmony prefix, not an XML removal. — **L** (LESSONS_INBOX L88)
63. Wildanimals dictionary VALUE naming a Cherry-Picker-cut creature crashes mapgen — a cut needs a cross-ref sweep. — **L** (LESSONS_INBOX L61)
64. Cherry Picker's FactionDef cuts do NOT remove the def (only a subset of def types supported). — **L** (LESSONS_INBOX)
65. `cherrypicker.py --is-cut` prints "present" meaning NOT CUT — easy to misread. — **S** — M
66. A species with its own dedicated ArtOverride mod is silently regressed by a later-loading fauna-absorption pipeline (texPath collision, zero errors). — **L** (LESSONS_INBOX L90)
67. `validate_patch.py` without `--defs <mods>` can't see a DIFFERENT mod's texPath coverage — false positive for ArtOverride-style mods. — **L** (LESSONS_INBOX L95)
68. Null-workerClass BiomeDef crashes ALL worldgen per-tile. — **L** (LESSONS_INBOX L177)
69. An inactive/undeployed mod's MayRequire-gated defs vanish with ZERO log lines — census the mod LIST, never the log. — **L** (LESSONS_INBOX L187; CLAUDE.md)
70. A startup mod silently caps `BiomeDef.plantDensity` at 1.0 and rescales regrow days. — **L** (LESSONS_INBOX L185)
71. `Build succeeded 0/0` is true of files LISTED not files WRITTEN — `EnableDefaultCompileItems=false` + missing `<Compile>` entries. — **L** (LESSONS_INBOX L184/L99[dup])
72. An abstract engine-extension base class (`Alert` via `AllLeafSubclasses`) with no concrete consumer crashes construction and permanently nulls `Find.MapUI`. — **L** (LESSONS_INBOX; a dedicated multi-paragraph entry)
73. `modset_builder.py --restore`'s safety check compared against CONFIG which already held the just-made test tier — fixed to compare against the real backup. — **S** — Lo

### World/biome/worldmap painting
74. The savegame IS the world; a CSV is an export, never a rival — divergent lineages go unnoticed for weeks. — **P** (L9 covers the narrower "biome column" case, not the general principle)
75. A 100% match against an artifact you just imported only proves the import worked, NOT that it was wanted — state which direction a live-vs-CSV validate is evidence for. — **S** — **H** (validation-methodology defect; recurred structurally in the north-star "GREEN proves nothing" family but never generalized/filed as this principle)
76. The canon CSV's `biome` column is PRE-REBAND; live biome needs the plan-JSON overlay chain — never trust the CSV column alone. — **L** (LESSONS_INBOX L9)
77. `world_links_import clearFirst:true` does NOT clear orphan links absent from the CSV. — **L** (skills/rimworld-world-editing/references/road-networks.md)
78. `riverEntries` staying identical across imports proves idempotency, not correctness. — **S** — M
79. Neighbour-majority biome fills must exclude water biomes. — **L** (skills/rimworld-world-editing/SKILL.md)
80. A biome painted with the same `texture` as its neighbour is invisible (texture is the only visual lever, no colour override). — **S** — M
81. `TileMutatorDef` has no visual fields; only `LandmarkDef` draws on the world map. — **P**
82. Painting a biome can bury a settlement — check `world_lint`'s settlements-on-water. — **P**
83. Measure the owner's sighting before believing OR dismissing it (3 of 4 "defects" this session were not what they appeared). — **S** — M (methodology insight, not filed as a reusable rule)
84. River direction lives in `tileRiverDistancesDeflate`, NOT elevation. — **L** (LESSONS_INBOX L54; skills/rimworld-world-editing/references/savegame-editing.md; CLAUDE.md memory)
85. `HillinessLabel` is cached on the Tile with no reset — invisible until world reload. — **L** (skills/rimbridge/references/silent-failures.md; rimbridge-companion; world-editing)
86. GL-emitted custom landform's `worldTileReq` keeps the shipped source's field unless explicitly overridden (`--topology`). — **S** — M
87. A GL custom landform swap is NOT picked up by menu+quicktest alone — needs a full process kill + relaunch. — **S** — M
88. `set_camera_zoom_extension(true)` does not persist across a process restart. — **S** — Lo
89. Gravship substructure fuses with any touching substructure — cut a 1-cell seam to disconnect. — **S** — M
90. `GenStep_Fog` only unfogs the flood from `PlayerStartSpot` — a start spot inside a walled complex reveals one room. — **S** — M
91. A bridge-generated Settlement map is culled by the abandon timer once time runs — save before unpausing. — **L** (LESSONS_INBOX-adjacent; CLAUDE.md memory generated-map-culled-unless-home)

### Instruments that lie with a number
92. `northstar.parse()` returns a DICT — `getattr(w,'must_show')` silently yields None → 0, an alarming-round wrong number. — **L** (LESSONS_INBOX L173; CLAUDE.md explicit)
93. `[ -e path ]` / `os.path.isdir` is not "a mod lives here" — test `path/About/About.xml`. — **L** (LESSONS_INBOX L165; CLAUDE.md explicit)
94. A checker keyed to a fixed line number lies quietly — use the first matching line. — **L** (LESSONS_INBOX L166; CLAUDE.md explicit)
95. A texture glob matching `*south*` non-deterministically reads the colour MASK, not the base art. — **L** (LESSONS_INBOX L164; CLAUDE.md explicit)
96. `shows=` marker appears in 0 of N `validation.py` files — the north-star system cannot GREEN anything; every validated mod's checklist is bound-and-uncovered. — **L** (LESSONS_INBOX L168; CLAUDE.md explicit, extensively)
97. `modcheck status` prints GREEN for a mod that does not exist because the summary reads a stored field while the detail re-derives (later partially fixed). — **L** (LESSONS_INBOX L168; CLAUDE.md, with the fix noted)
98. `modcheck run <Mod>` REWRITES the live `ModsConfig.xml` despite reading like a query verb. — **L** (LESSONS_INBOX L167; CLAUDE.md explicit)
99. `os.path.isfile` returning False means ignorance (EACCES/EIO/drvfs stale), not absence — `proven_gone` stat-errno discipline. — **S** — H (a real data-destruction near-miss on `prune`; not filed as a general rule)
100. `$?` after a pipe reads the pipe's LAST command's exit code, not the one you meant. — **S** — M
101. An alpha>0 bounding box lies on generated art (sub-visible export halo) — measure alpha>16 on the original, never a thumbnail. — **L** (LESSONS_INBOX L137)
102. `point(lambda) then .convert("1")` silently zeroes everything (thresholds at 128) — use 255. — **L** (LESSONS_INBOX L138)
103. Cropping each sprite to its own bbox then rescaling to a square erases scale — compare at native scale. — **L** (LESSONS_INBOX L139)
104. Comparing whole canvases matches on shared transparency — exclude the background from the metric. — **L** (LESSONS_INBOX L139, same entry)
105. `touchedBySheet` is DERIVED by `serve_sheet.py --status`, never written to disk — guard on `savedBy`/`writeCount`/`savedAt`. — **L** (LESSONS_INBOX L134)
106. The review-sheets template ships `<script id="RENDER">` INSIDE an HTML comment — inert, inject a live `<script>`. — **L** (LESSONS_INBOX L133/L140)
107. A geometric image check (`facing_symmetry`) can pass what the eye rejects — not a tuning problem. — **L** (LESSONS_INBOX L143)
108. A state assertion (`expect_pawn_despawned`) and the screen can both be right and disagree — validation only reads state. — **L** (LESSONS_INBOX L142; CLAUDE.md-adjacent via north-star)
109. A subagent reported a structural fix "done" when only half existed — verify by RUNNING the command, not reading the summary. — **L** (LESSONS_INBOX L175)
110. A checker can manufacture findings by over-strict comparison (13 false STATUS_DISAGREEMENTs, true count 1). — **S** — Lo (self-caught, not filed)
111. `handoff.py` cannot tell two BENCH windows apart — do not release the bridge to satisfy the gate, use `--force`. — **L** (LESSONS_INBOX L176; CLAUDE.md explicit)
112. `handoff.py`'s bridge-holder gate used a bare substring match — false-positives when one seat name is a substring of another (BENCH inside MACBENCH). — **S** — M (fixed same session; the general "substring-check is suspect" lesson not filed)
113. `handoff.py` silently defaults the seat to FOUNDRY when it cannot tell — fixed to refuse; "a fallback to a valid-looking value is worse than an error." — **S** — M
114. `RUT_HumLayers.xml`'s comment "no audio pipeline exists" is measured FALSE (1048 audio files exist) — a prior agent's search result written into a comment ages into a false fact. — **L** (LESSONS_INBOX L156)
115. A doc's "state"/"verified" column decays fastest in the direction that causes rebuilding — reading a checklist aloud audits the doc. — **L** (LESSONS_INBOX L159/L160)
116. A doc can block work on defects fixed before the doc was written (liquids_framework_design.md example). — **L** (LESSONS_INBOX L147; CLAUDE.md explicit)
117. A gate cited by name outlives the item it names (NAMING_SCHEME_EXECUTION_1 closed but 20 docs still deferred to it). — **L** (LESSONS_INBOX L148; CLAUDE.md explicit)
118. An item's own figures decay — a placeholder-description count was stale by 4/5 items. — **P** (general doctrine "queue items decay" is landed as a CLAUDE.md/memory principle; this specific figure isn't)
119. `PIT_SUPERDEEP_COLLAPSE_1`'s item (not the 1127-line spec) is the authority — spec predates 3 rounds of rulings. — **L** (CLAUDE.md, verbatim dedicated section)
120. `RimSage` does not work on the Mac laptop and never has (TCP dead, no cached tree). — **L** (CLAUDE.md, verbatim dedicated section)
121. `northstar` validated-hash covers the WHOLE section including prose — correcting a stale caveat reverts VALIDATED to DRAFT. — **L** (LESSONS_INBOX L149; CLAUDE.md, ruled explicitly)

### Art / codex / generation pipeline
122. `codex_image.py` raises on its 180s ceiling BEFORE harvesting — a wrapper timeout is never evidence of a failed image. — **S** — M
123. `xargs` on Workshop paths breaks on "Program Files (x86)" — use python `glob`. — **L** (general space-safety doctrine present widely in skills)
124. gemini-3-pro-image returns fixed 1024×1024 JPEG with no native alpha; budget is CUMULATIVE from `throughput.jsonl`, not per-run. — **L** (LESSONS_INBOX L51)
125. N concurrent rembg loads die in a bounded cgroup (multiprocessing resource_tracker) — flock-serialize. — **S** — Lo
126. Piping a live daemon through `head` SIGPIPE-kills it mid-job, orphaning a billing-intent record. — **L** (LESSONS_INBOX L51)
127. OpenAI strict output-schema needs every property in `required` and rejects min/max/maxLength. — **L** (LESSONS_INBOX L52)
128. Sprite/creature-cast audits must verify IDENTITY (distinct creatures → distinct files), not just coverage %. — **S** — M
129. The artpipe daemon does not hot-reload — a source edit needs a process restart to take effect. — **L** (LESSONS_INBOX L56)
130. Two `artpiped.py` daemons can run concurrently with no lock — check `pgrep -af artpipe` for >1 PID. — **L** (LESSONS_INBOX L97)
131. `reference=` on an artpipe job triggers reskin-validate (pixel-fidelity to the OLD sprite) — wrong for a deliberate restyle. — **L** (LESSONS_INBOX L111; CLAUDE.md memory artpipe-reference-triggers-reskin-validate)
132. Asking for "transparent background" in a codex edit prompt can produce a literal opaque checkerboard — ask for a flat chroma-key colour instead. — **L** (generating-images skill doctrine)
133. `codex_image.py`'s sandbox helper is fragile across a Codex app update — check `tasklist.exe` for stale processes. — **S** — M
134. A brand-new `--codex-home` triggers a Windows UAC dialog per new home unless seeded from a captured template. — **S** — M
135. Concurrent codex imagegen workers can collide on a shared harvest dir (one worker harvests another's render). — **L** (LESSONS_INBOX L123)
136. Generated art's defects are mostly free to fix (export halo, byte-identical "renders", independently-prompted facings) — cheaper than prompt tuning. — **P** (specific numeric case not filed generally)
137. Donor art obeys a facing convention that our regenerated overrides break (mirror-symmetry 0.96+ vs 0.2-0.5). — **S** — M

### Generators / tooling that silently corrupts its own output
138. Generators anchored on their own prior output (5 separate defects, same shape) silently churn/drop/oscillate values — use `--out DIR`, diff at the xpath-SET level, never regen in place. — **S** — **H** (the single largest un-landed item in the corpus: a whole class of silent data-corruption defect across 3+ generator scripts, never generalized into LESSONS_INBOX or a skill)
139. `strings`/ASCII scan cannot see .NET UTF-16LE string literals — a clean scan of a managed DLL is not evidence of absence. — **L** (CLAUDE.md memory strings-misses-dotnet-utf16-constants; not in project CLAUDE.md itself) — **P** (memory ≠ one of the 4 listed durable destinations)
140. A dump's `duplicateDefName`/`duplicateOwners` fields do not exist — `package_id` per defName is the empirical winner answer. — **S** — Lo
141. `DebugActionType.ToolMap` is not a separate menu — same `Actions` root with a `T: ` label prefix. — **P**
142. A public field (e.g. `lastLaunchTick`) is a better Harmony success-gate than replicating a private guard chain. — **S** — Lo
143. A fresh-context adversarial review of your OWN just-written fix catches what your own self-review missed. — **P** (general code-review doctrine landed; this specific framing not)
144. `RM_BaseGraffiti`'s `placementMask=Any` is backwards — a requirement on the TERRAIN not a permission on the filth; `Any` places nothing, ever. — **S** — H (shipped broken silently for a week; general "clean build + active mod ≠ mechanism fires" lesson not filed as a rule)
145. `rosters/*.json` (fauna/flora) is THE single source of truth — never hand-edit downstream; review-sheet row-ids are positional (rebuild after roster edits). — **S** — **H** (silent wrong-verdict risk on review sheets)
146. A per-biome fauna cast joins TWO sources (in-rows + resolved move-rows) — naive reading of the raw decisions file double-counts. — **L** (LESSONS_INBOX L55)
147. VEF quest chains self-schedule into the save silently — grep `futureQuests` before retiring a quest mod. — **L** (LESSONS_INBOX L53)
148. `EnableDefaultCompileItems=false` + a stale `<Compile Include>` list silently excludes real .cs files from the build with "0 errors". — **L** (LESSONS_INBOX L184; recurring, well landed)
149. `DEPLOY_HOLD.txt` paths are relative to `custom_patches/` — a full-repo-path entry never matches, and a malformed hold is a silent no-op. — **P** (DEPLOY_HOLD mechanism itself is documented in skills/rimworld-deploy and rimworld-modding; this specific "silent no-op on malformed path" trap is not)
150. A generator/tool regenerating output must be diffed against the previous artifact before trusting it (idempotence never asserted). — **P**

### Process / rimflow / ledger / MODE
151. `rimflow` ledger writes (claim/start/close) are LOCAL only — sync explicitly, don't let them pile up uncommitted. — **L** (LESSONS_INBOX L66; CLAUDE.md memory)
152. Ledger projections must use FILE ORDER, never ts-sort (same-second start+close pairs invert). — **L** (LESSONS_INBOX L105; CLAUDE.md explicit)
153. `--owner-said` refuses a quote containing a question — an owner question authorizes examination, not a state change. — **L** (LESSONS_INBOX L157)
154. `infrastructure/state/MODE` can be stuck on a stale `afk`, silently suppressing `rimflow why`/`next` offers even while the owner is live. — **L** (LESSONS_INBOX L103)
155. `rimflow close`'s ownership refusal is no longer absolute — the owner ruled "anyone can close an item found genuinely done," citable via `--owner-said`. — **P** (CHARTER.md not checked directly; not confirmed in the 4 named destinations)
156. A ledger merge conflict in the append-only `events.jsonl` resolves by UNION, not by picking a side; `queue/*.md` regenerates, never hand-merges. — **L** (LESSONS_INBOX, MACBENCH handoff entry lands directly)
157. A botched `git stash pop` can land raw conflict markers into `events.jsonl`, breaking rimflow for every seat — repaired via a dedicated recovery script. — **L** (LESSONS_INBOX explicit entry + new tool `repair_torn_ledger.py`)
158. The ledger (`events.jsonl`) is guarded against direct `Edit` by a PreToolUse hook — use `sed -i` via Bash for a legitimate conflict-marker strip. — **S** — Lo
159. A PreToolUse hook refuses a WHOLE compound Bash command touching the ledger, including everything before the flagged part. — **P** (general "hook refuses whole compound" doctrine is landed via the blind-scan case; this ledger-specific instance is not)
160. `rimflow file --needs game-up` prints a refusal-shaped warning but still files the item anyway. — **S** — Lo
161. An item filed alongside a finished analysis must cite the report path, or the next window re-runs it blind. — **L** (LESSONS_INBOX L102)

### Laptop / cross-machine / RimSage
162. RimSage does not work on the Mac laptop and never has (measured 5x, TCP dead). — **L** (CLAUDE.md, extensively)
163. Laptop-only friction: `measure` not on PATH, `./game` permission-denied, `RIMFLOW_SEAT` required with no profile, `MACBENCH` not a valid seat, no `timeout` (BSD), `rimflow file` needs `--title`/no `list` verb. — **P** (RimSage-unreachable part landed; the specific tool-friction list is not)
164. `python.exe` misreads a WSL absolute path — `cd` into the repo and pass a relative path. — **L** (CLAUDE.md memory windows-python-misreads-wsl-absolute-paths; LESSONS_INBOX multiple)
165. `handoff.py` defaults the seat to FOUNDRY when `RIMFLOW_SEAT` is unset, and env vars don't survive across fresh Bash calls — prefix inline. — **S** — Lo (partially covered by claim 113's "silent fallback is worse than an error" fix)

### Misc / owner-facing
166. AskUserQuestion: a `preview` on any option suppresses the free-text write-in line; a self-authored "Other" option submits a label, not real text. — **L** (LESSONS_INBOX L130)
167. AskUserQuestion is gated by a hook requiring `?`-ending questions, ≤12-char headers, options that state their cost. — **P** (general "cards state a trade" doctrine landed in CLAUDE.md/memory; this exact hook-shape is not)
168. Never restart a review sidecar after handing the owner its URL — the port is part of the browser origin, orphans his tab/localStorage verdicts. — **L** (LESSONS_INBOX L132)
169. Owner's screenshots land in Steam userdata via F10, never RimWorld's own folder. — **L** (LESSONS_INBOX; CLAUDE.md memory rimworld-screenshot-location)
170. A mod-inventory description must come from the mod's About.xml text, never its packageId/name. — **S** — Lo
171. `serve_sheet.py`'s `explorer.exe` fallback pops File Explorer at Documents on every launch. — **L** (LESSONS_INBOX L67/L69)

## 3. Harvest-process evidence

- `git log --oneline -- skills infrastructure/state/LESSONS_INBOX.md CLAUDE.md` → **545 commits** total (this repo touches these paths constantly; not a useful "harvest cadence" signal by itself).
- The one explicit **full drain pass** found: `91bf54cf5` "Curation pass: drain LESSONS_INBOX (79 lessons) into 15 skills; regenerate rosters", dated **2026-09-04**.
- No second full drain has happened since. LESSONS_INBOX.md's earliest visible entries in the current file are dated 2026-09-07 (i.e. the file was emptied/restarted at the 09-04 drain and has grown to **188 entries** by 2026-09-17 — 13 days, ~14 entries/day).
- Curation has continued **piecemeal** since 09-04 (not as a second full pass): commits like `0b1ad5a58` ("Skills: the five world-repaint lessons from the vanilla-water closeout"), `f64c4430b` ("Sprite skill never said what north and south MEAN"), `660827578` ("canon library gets an index... a skill that fires") show individual lessons landing in skills/ in the days since. 12 commits touched `skills/*/SKILL.md` or `skills/*/references/*.md` in the last 14 days.
- **Estimated backlog since the last full drain: ~188 LESSONS_INBOX entries**, of which the piecemeal commits above have visibly absorbed maybe 15-20 into skills — the rest sit un-promoted to skills/CLAUDE.md (though many are independently useful as LESSONS_INBOX entries, which this audit already counts as "landed" per the task's own definition of durable destination).

## 4. LESSONS_INBOX compliance ("also file these to LESSONS_INBOX.md")

Cross-checking the "Traps learned" sections against LESSONS_INBOX.md entries by date:
- Handoffs dated **2026-09-09 onward**: compliance is very high — the large majority of
  named traps have a matching or near-verbatim LESSONS_INBOX entry, often on the same date,
  and several handoffs explicitly state "All filed to LESSONS_INBOX.md" or "All N in
  LESSONS_INBOX.md" (confirmed true in spot checks).
- Handoffs dated **2026-09-06 to 2026-09-08** (the earliest ~15 files): compliance is
  markedly lower — several sessions' traps (donor-def-before-design, codex 180s ceiling,
  xargs/Program Files, riverEntries-stability-≠-correctness, world_mutators_get tight-loop)
  have no LESSONS_INBOX entry at all, and no handoff from this window claims "filed to
  LESSONS_INBOX."
- Rough compliance estimate: **~80-85%** of traps from 09-09 onward were filed at the time;
  **~30-40%** from the 09-06 to 09-08 window were. Blended across the whole corpus: **roughly
  70%** filed at the time it was learned.

## 5. UNKNOWN

- Whether skills/*/references content that grep-matched a claim's keywords actually
  **teaches the lesson correctly** (vs. an incidental keyword collision) was spot-checked
  for ~20 of the highest-value claims, not all 171.
- Whether `infrastructure/agents/CHARTER.md` (not one of the four named destinations, but
  cited by handoffs as carrying some rulings, e.g. claim 155) independently landed anything
  — CHARTER.md was not read in this audit.
- Exact per-claim compliance-at-filing-time for handoffs between 09-11 and 09-14 was
  sampled, not exhaustively dated against LESSONS_INBOX entries one-by-one.
