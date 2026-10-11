# 09: Review-sheet skill trade study (2026-10-11)

This is a design document only. Nothing in it has been built or edited. Every number below was measured in this session by a python script over the bench clone and transcripts. None comes from the audit reports. The 03 and 07 audits were used as leads and then re-checked.

## 0. The owner's ask (typed, 2026-10-11)

> "For the review sheet, I had separated it originally because it would revert to a traditional review sheet (and not include scaled image comparisons properly) often, so I would invoke one BY NAME sometimes that forced it to include scaled images. If you can make it smarter to always include scaling comparisons next to images that have real in-game scaling, but that's specific vs. the external repo skill of review sheets I use for all sorts of things. See what I mean? Do a design trade study here and come up with better ways to handle this, then we'll follow the advice of what you find after another question card."

The requirement has three parts:
1. An image with a real in-game size always gets its scaled comparison, with no need to name the right skill.
2. The external `review-sheets` skill stays general.
3. The names are clear.

## 1. Inventory: every review-sheet skill and tool

### Skills

**`review-sheets`**
- Where it lives: `D:\Luke\dev\review-sheets\SKILL.md`. It is its own repo, `git@github.com:Lmandrake/review-sheet.git`, and is symlinked as `~/.claude/skills/review-sheets`. The project also symlinks it as `.claude/skills/review-sheets`, so it is double-wired.
- Visibility: its description is shown in the listing, and it is generic and cross-project.
- Usage: 474 lines. The template and tools are in `assets/`: `sheet_template.html`, `check_sheet.py`, `serve_sheet.py`, `merge_artifact_db.py` and `review_status.py`. Over 30 days it had 50 invocations and 78 opens (03 audit).
- Scale content: one bullet in §1 says a scale panel is a measurement, so print its source. It never tells an author to add a scale comparison.

**`scaled-game-image-review`**
- Where it lives: `D:\Luke\dev\RimMandrake\skills\scaled-game-image-review\SKILL.md`.
- 🔴 It is NOT WIRED. There is no `.claude/skills/scaled-game-image-review`, which I confirmed with `ls`, and it does not appear in this session's skill listing at all.
- Usage: 131 lines, 14 owner rulings, 0 invocations and 46 path opens (03 audit).
- What it is: the owner commissioned it on 2026-10-05 as "a subset of the review sheet skill… for reviewing in game art".

**`image_scaling`**
- Where it lives: `D:\Luke\dev\image-scaling\SKILL.md`. It is global and listed name-only.
- What it is: the viewing model and legibility laws. It feeds `scale_panel.py`, but it is not a sheet skill.

**`rimworld-live-review`**
- Where it lives: `D:\Luke\dev\RimMandrake\skills\rimworld-live-review`. It is wired.
- What it is: in-game staging and screenshots. It is not a sheet skill, though it is adjacent.

### Project machinery

All of this is under `D:\Luke\dev\RimMandrake\src\RimMandrake\Utils\`.

| tool | what it does | scope today |
|---|---|---|
| `art\art_sheet.py --biome RM_X` | Builds a biome flora/fauna art sheet from the art ledger. It builds to `.gate.tmp`, runs the gate, and only a pass is stamped and moved into place. | **biome sheets only.** No mode exists for buildings, items, junk, gear, or a set of artpipe renders. |
| `art\scale_panel.py` | Measures the size in cells and shows the source. Renders the true-scale panel at 128–256 px/cell beside a vanilla human on the biome's ground colour. | **animals and plants only.** Buildings and items (`graphicData.drawSize` on a non-plant ThingDef) have no resolver. |
| `art\scaled_review_gate.py` | Runs the 14 requirements, writes the stamp, and has `check` and `all`. | `all` globs `Transient\biome_ffar\*_sheet_*.html` only. |
| `art\serve_gated.py` | The only launcher allowed in this repo. It refuses an unstamped sheet (exit 4) unless the sheet declares `sheet-kind: non-art`. | Served sheets only. |
| `art\nonart_sheet.py` | The checked route for non-art sheets. The author declares `<meta name="sheet-kind" content="non-art">`. | Self-declared. |
| `art\refresh_sheets.py` | Rebuilds sheets whose candidates changed. URLs stay stable. | biome sheets only. |
| `art\remap_decisions.py` | Re-maps column letters to the same pictures after a rebuild. | biome sheets only. |
| `art\art.py enact` / `ingest` | Turns rulings into ledger events. `--redo-jobs` requires the owner's note verbatim. | biome sheets. |
| `sheet_to_artifact.py` | Turns a sheet into a claude.ai artifact so it can be reviewed by phone. | **No gate check.** |
| `.claude\hooks\block_hand_edited_sheet.py` | Refuses Write/Edit/Bash writes to `biome_ffar\*_sheet_*.html`, and refuses a bare `serve_sheet.py`. | `biome_ffar` path only. |
| `.claude\hooks\warn_skill_unwired.py` | Warns when a SKILL.md has no symlink. | Exits 1, so it **warns on the owner's screen only and is invisible to the agent**. That is why it did not catch the unwired skill. |

## 2. How a sheet ends up "traditional" (no scaled comparison)

The census below was measured over every `Transient\**\*sheet*.html` and `*review*.html`. It counts `.png` references and `scale_` images per file.

- **Every gated sheet has scale panels: 27 of 27** `biome_ffar` sheets are stamped and carry `scale_` images.
- **Every art sheet built outside the gated tool lacks them.** Since 2026-10-03 there are 7 image sheets outside `biome_ffar`, and all 7 have **0** scale panels:

| sheet | images | scale panels | subjects have a real in-game size? |
|---|---|---|---|
| `Transient\desert_art_review_2026-10-03.html` | 359 png | 0 | yes (desert flora/fauna) |
| `Transient\junk_reskin_review_2026-10-04\sheet.html` | 171 | 0 | yes (junk items) |
| `Transient\junk_reskin_review_2026-10-09\sheet.html` | 346 | 0 | yes |
| `Transient\donor_code_creatures_sheet_2026-10-09.html` | 40 | 0 | yes (creatures) |
| `Transient\sluice_panning_warden_sheet_20261010.html` | 20 | 0 | yes (1×2 sluice box, a building, a creature) |
| `Transient\icon_outline_batch4_sheet_20261010.html` | 72 | 0 | mostly no (UI icons), but it includes the "Warden Mother aged" creature |
| `Transient\sheet_conflicts_review_2026-10-09.html` | 311 | 0 | it shows art pictures, yet it **declares itself `non-art`** |

There are four causes, in the order they bite.

1. **Skill selection loses.** The general `review-sheets` is listed with its description. The scaled one is not listed at all because it is unwired. Even if it were wired, 51 of 77 skills showed name-only in the listing (03 audit, observed), so description-based triggering is unreliable here. An agent asked for "a review sheet" gets the general skill, and the general skill never asks for a scale comparison.
2. **There is no gated generator for non-biome art.** `art_sheet.py` only takes `--biome`, and `scale_panel.py` only sizes animals and plants. An agent reviewing a sluice box, a junk reskin or a batch of artpipe renders has nothing to run, so it writes a one-off generator. Examples are `Transient\sluice_panning_warden_sheet_20261010.py` and `Transient\junk_reskin_review_2026-10-09\build_sheet.py`, both copied from the general template. Even an agent that read the scaled skill could not have complied without hand-rolling the panel.
3. **Every gate is keyed by path or by self-declaration, not by content.**
   - The hook and `gate all` look only at `biome_ffar`.
   - A static HTML file written by `python3 x.py` and opened or committed directly never passes through `serve_gated.py`.
   - `nonart_sheet.py declare` lets any sheet opt out. `sheet_conflicts_review` shows 311 art pictures and is declared non-art.
   - `sheet_to_artifact.py` (the phone route) checks nothing.
4. **The generator once whitelisted itself out.** A `SCALE_BIOMES` whitelist silently left 21 sheets with no scale panel (`infrastructure\state\handoffs\BENCH_REBOOT_HANDOFF_202610060555.md` line 38). That was fixed when the gate landed. It shows that even the gated tool needs the gate to check every row, not just the opted-in ones.

**No gate today refuses a scaled-art sheet that lacks the comparison unless it is a biome sheet.** The 14-requirement gate is strong, but it guards a single doorway.

## 3. Evidence from transcripts, lessons, handoffs

I scanned the typed user messages in 366 main-session transcripts under `~/.claude/projects/{-home-mandrake-rm-bench,-home-mandrake-rm-foundry,-mnt-d-Luke-dev-RimMandrake,…}`. Times are PDT.

- 2026-10-04 16:03: *"Hate to do this to you, but I also need to know the cell size for each of these flora and fauna too, with a realistic game human for scale. It's the only way I can judge the art quality/resolution. You know how to show this to me from past comparisons."*
- 2026-10-04 16:04: *"There are skills about scaled images"*. He had to point the agent at the skill.
- 2026-10-05 18:39: *"You also did not include the scaled portrayal on that sheet. I want you to make a subset of the review sheet skill right now that's for reviewing in game art. … Scaled game image review?"* This created the skill.
- 2026-10-05 19:00: *"Add hooks to the scaled image review sheet so it MUSt pass its requirements to be generated"*. This created the gate and the hook, scoped to `biome_ffar`.
- 2026-10-05 20:18: *"On The Slime yet again you have failed to include scaling imagery"*. This was one hour after the skill existed.
- Handoff `BENCH_REBOOT_HANDOFF_202610060555.md` records "scale panel on every row (skill `scaled-game-image-review`)" as an owner-said rule. It also notes that def `<color>` tints are visible only in the scale panel, so the panel catches defects the raw columns hide.
- I found no typed by-name invocation after 2026-10-05 in these projects. That is consistent with what the owner describes, though he may have done it from another project or from the phone. Either way, the 7 non-biome sheets since then show the failure is still live wherever the gate does not reach.

**The lesson:** a skill alone failed within an hour, and the gate fixed it completely where it applies (27 of 27). Enforcement, not triggering, is what works.

## 4. Options and scored trade study

The scores run from 1 (bad) to 5 (good). Weights reflect the owner's ask: never miss scale (×3), don't depend on skill triggering (×2), keep the external skill general (×2). The other criteria are ×1.

| criterion (weight) | A. overlay skill only | B. gate + generator | C. one project skill replaces both | D. hooks only | E. data-driven scale field in the general template | **H. B + E + a thin A** |
|---|---|---|---|---|---|---|
| Never misses scale on in-game art (×3) | 2 | 4 | 2 | 3 | 3 | **5** |
| Independent of skill triggering (×2) | 1 | 5 | 2 | 5 | 3 | **5** |
| External skill stays general (×2) | 5 | 5 | 1 | 5 | 4 | **4** |
| Covers non-biome art: buildings, items, renders (×1) | 2 | 4 | 3 | 2 | 4 | **5** |
| Build cost, inverted (×1) | 5 | 2 | 3 | 3 | 3 | **2** |
| Drift / maintenance (×1) | 4 | 4 | 1 | 3 | 5 | **4** |
| False-positive burden on icon / non-art sheets (×1) | 5 | 3 | 4 | 2 | 4 | **4** |
| Clarity to owner and agents (×1) | 4 | 3 | 4 | 2 | 4 | **5** |
| **weighted total (max 60)** | 38 | 48 | 27 | 41 | 43 | **53** |

What each option is, and its decisive weakness:

- **A. Overlay skill only.** Wire `scaled-game-image-review`, rename it, and sharpen its description. This is the status quo plus a symlink. Its weakness is shown in the evidence: the skill existed and the agent still did not include scale an hour later. With 51 of 77 skills name-only, triggering is a coin flip, and it still gives no tool for non-biome art.
- **B. The generator and gate enforce it.** This means a general-subject mode in `art_sheet.py`, `scale_panel.py` extended to buildings and items, and a gate classified by content and checked at every delivery chokepoint. Skill choice stops mattering. Its weakness is cost, and a page that never reaches a chokepoint is still possible.
- **C. One project skill replaces both.** It forks the 474-line general skill into the project, which breaks the owner's "I use it for all sorts of things". The two copies would drift. It also still depends on triggering.
- **D. Hooks only.** A PreToolUse or Stop hook scans any written sheet HTML for game images. A sheet written by `python3 gen.py` is invisible to PreToolUse, so only Stop or commit catches it, and only after the fact. It detects the gap but cannot produce the panel for a building, which `scale_panel` cannot size yet. Its heuristics carry a false-positive risk.
- **E. Data-driven.** The general template gains an optional per-row `scale` field (size, reference figure, background, px/unit) and renders a true-scale panel whenever the field exists. `check_sheet.py` fails a sheet whose `CONFIG.trueScale` is `required` when any image row lacks it. This is generic: maps, printed parts and UI mockups have real sizes too. But an author who never fills the field still gets a traditional sheet, unless something project-side makes it required.
- **H. Hybrid (recommended).** Use E for the general mechanism, B for project enforcement and coverage, and a thin, wired, clearly named overlay skill for the lifecycle knowledge. Its weakness is build cost, about one focused session.

## 5. Recommendation: H

### Names

- **`review-sheets`** keeps its name. It is the general, external skill, in its own repo, with 50 invocations.
- **`rimworld-review-sheets`** is the project overlay. It replaces `scaled-game-image-review`, whose contents move in. The name is deliberately parallel. With 51 of 77 skills shown name-only, **the name is the trigger surface**, and "rimworld-review-sheets" next to "review-sheets" reads unambiguously as "the RimWorld version of that one" with no description needed.
  - The alternative is `rimworld-art-review-sheets`, if he wants "art" in the name. The cost is that it then does not obviously own the non-art lifecycle (serve, enact, remap, notes) that audits 03 and 07 both say needs one home.
  - "Scaled" goes into the description and the first rule rather than the name, because under H scaling is enforced by code and no longer needs the name to summon it.

### What each SKILL.md contains

**`review-sheets`** (external; the edits are small and stay generic):
- A new short section, "Things with a real size". When the items have a physical or rendered size (game sprites, map tiles, printed parts), show each at true scale beside a known reference figure on its real background, print the size and its source, and never only at thumbnail size.
- It documents the template's new optional `scale` row field and the `CONFIG.trueScale: "required" | "optional"` switch, which `check_sheet.py` enforces.
- A one-paragraph "Overlays" section. A project may layer a `<domain>-review-sheets` skill on top, and its rules win where they are stricter. The section must not name RimWorld.

**`rimworld-review-sheets`** (project; it is a lean SKILL.md and the details go in `references/`):
- **Rule 1, in the first screen.** Any image with a real in-game size gets the true-scale comparison. The code enforces this, and the skill says which tool to run, not how to hand-build it.
- **The one decision tree for building a sheet:**

  | sheet | tool |
  |---|---|
  | biome sheet | `art_sheet.py --biome` |
  | any other game art | `art_sheet.py --subjects`, which is new |
  | not art | `nonart_sheet.py` |

  ⛔ There is no hand-rolled generator for art.
- **The lifecycle:** build → gate → `serve_gated` → owner → `refresh_sheets` / `remap_decisions` → `art.py enact` (preview, then `--apply`, with `--hold`) → fresh audit → followed notes cleared. This brings in the six sheet lessons from audit 07 §2 row 6 as a traps section in `references/traps.md`.
- The 14 owner rulings move verbatim from `scaled-game-image-review` into `references/art_requirements.md`.
- **Description**, under 600 characters and trigger-form: "Use before building, serving, refreshing, enacting or retiring any RimMandrake review sheet, and before showing the owner any game art (sprites, renders, buildings, items, creatures, plants) to judge. RimWorld layer over `review-sheets`: true in-game scale beside every picture that has one, gated build and serve, ruled-art enact."
- **Wiring:** `ln -s ../../skills/rimworld-review-sheets .claude/skills/`. Delete `skills/scaled-game-image-review/` once its content has moved. The owner's rule is delete, not supersede. Fix every inbound reference in the same change: the gate's docstring, the hook's REASON, `art_ledger_design_2026-10-04.md` and the handoffs-to-come.

### Enforcement code changes (B and E)

Each change below carries a selftest whose fixture is a real past failure.

1. **`scale_panel.py` gains a `thing` resolver.** It reads `graphicData.drawSize` for buildings and items, honouring `size` and rotation, and uses the same human and ground composition.
   - A subject with **no world size** resolves to `kind: none`, with the reason measured. Examples are a `uiIconPath` icon, a designator or research icon, and a menu icon.
   - **The exemption comes from the resolver, never from the author.** This closes the "declare non-art" loophole.
   - Fixtures: the sluice box (1×2) must size; an icon-batch icon must resolve `none`.
2. **`art_sheet.py --subjects <defName…> | --jobs <artpipe ids…> --sheet-id X`.** This is the gated path for any non-biome art. An uninstalled render is sized through its job's `install_to` / `target_texpath` and from there to its def. It uses the same gate and stamp, and `serve_gated` / `refresh` / `remap` / `enact` must accept the new sheet kind.
3. **`scaled_review_gate.py classify <html>`** decides "game art" from the content, not from the path.
   - It reads every row image's provenance (a texture under a mod's `Textures\`, an artpipe `_artsrc` / `done` job, or a texPath) and requires a scale panel on every such row unless the resolver says `none`.
   - `gate all` widens from `biome_ffar` to every `Transient\**\*.html` carrying the template's `<script id="ITEMS">`.
   - `nonart_sheet.py check` fails any sheet that `classify` finds to contain game art.
   - Fixtures: the `sheet_conflicts_review` case, and the `SCALE_BIOMES` whitelist case (one row without a panel fails the sheet).
4. **Gate every delivery chokepoint, not just the path.**
   - `serve_gated.py` already gates served sheets.
   - **Add the commit chokepoint:** the existing pre-commit / PreToolUse git hook runs `classify` on any staged `Transient\**\*.html` and refuses an unstamped game-art sheet. In this repo the owner reads sheets through the origin/main mirror, so a commit is how a static sheet reaches him.
   - **Add the phone chokepoint:** `sheet_to_artifact.py` refuses an unstamped game-art sheet.
   - Widen `block_hand_edited_sheet.py`'s Write/Edit match from `biome_ffar` to any HTML with the template markers.
5. **`review-sheets` template and `check_sheet.py`** (in the external repo, generic):
   - Add the optional `scale` row field, a default renderer, and `CONFIG.trueScale`. `check_sheet` fails a row missing `scale` when the setting is `required`.
   - `art_sheet.py` sets `required`, so the external gate and the project gate agree.
   - Add one fixture to `test_check_sheet.py`.
6. **Make "unwired skill" visible to the agent.** `skills/validate_skills.py` should ERROR on a project skill with no `.claude/skills` symlink, and `warn_skill_unwired.py` should exit 2 on a SKILL.md write with no symlink. The current exit 1 is invisible to the agent, and that is how `scaled-game-image-review` stayed unwired for 6 days.

What H does not cover:
- A sheet that is never served, committed or published, opened only from a local file. That route has no chokepoint, so the skill's first rule is the only guard there.
- Pawn apparel and heads. Their scale comes from the pawn render tree, so they stay `FALLBACK` until a resolver exists, and they are shown and badged, not hidden.

## 6. Question card options

The owner picks one. This is written for a card, so it is plain language with the trade on each option.

1. **Recommended: make the tools enforce it, and give the project skill a clear name.**
   - The sheet builder learns to size buildings, items and new renders, not just biome creatures and plants. Any art sheet without the human-for-scale panel is refused before you can see it, wherever it was made.
   - The general review-sheets skill gains a small, general "show things at true size" option, with no RimWorld in it.
   - The project skill becomes `rimworld-review-sheets` and holds the whole sheet lifecycle.
   - The trade: about one build session, and the most code to keep up.
2. **Enforce only, rename nothing.**
   - Same refusal and the same new sizing, but the skills stay as they are: `scaled-game-image-review` gets wired and its name kept.
   - The trade: cheaper, and you keep the name you chose. The sheet lifecycle (serve, enact, notes) stays scattered across three places, and the name keeps fighting `review-sheets` for attention.
3. **Skills only, no new code.**
   - Wire and rename the project skill, sharpen its description, and point the general skill at it.
   - The trade: an hour of work. The record shows this alone failed within an hour on 2026-10-05, and it gives no way to size a building or item, so non-biome sheets would likely keep coming out without scale.
