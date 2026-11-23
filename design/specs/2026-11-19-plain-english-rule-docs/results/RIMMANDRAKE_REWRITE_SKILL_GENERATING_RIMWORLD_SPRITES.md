# Result: `RIMMANDRAKE_REWRITE_SKILL_GENERATING_RIMWORLD_SPRITES`

One session of batch 17 of `batch_plan.md` (`RIMMANDRAKE_REWRITE_SKILLS_IN_CURATION_SESSIONS_ONE_SKILL_EACH`).
File: `skills/generating-rimworld-sprites/SKILL.md`. Run 2026-11-23.

Base: `0a5a223b67`
Also: skills/generating-rimworld-sprites/references/history.md

## Scores

| measure | before | after |
|---|---|---|
| bytes | 24,471 | 25,863 |
| words in linted prose | 3,025 | 3,300 |
| STE violations per 100 words | 5.29 | 1.97 |
| sentences over 20 words | 59 | 15 |
| flagged lines (mechanical) | 27 | 16 |
| lines that a cold reader cannot act on (hand count, by the writer) | 12 | 0 that this run could resolve; 5 listed under "Could not determine" |

The file grew by 6%. The worked example grew by 16%.

### The 15 long sentences that stay

| line | kind |
|---|---|
| 49, 335 | a quote (the owner's, and the invariants text for the prompt) |
| 16, 74, 89, 221, 225, 259, 284, 319, 323, 368, 376, 383, 404 | two short sentences that the lint joined at a bold lead |

The 16 flags that stay are all `shout`. They are the 🔴, ⛔, ✅ and ❌ marks, and the owner's two headings in capitals. The
🔴 and ⛔ marks stay because they mark a rule as binding. The ⭐, 🔑, ⚠️ and ⇒ marks in body text are gone.

## What stays byte for byte

The front matter (`description` included), every heading, every table and every fenced command are the same as at the base.
A `diff` of each group is empty. `traps.md` cites the section headings.

## The POLICY pointer

The deploy line cited `infrastructure/agents/POLICY.md`, a superseded file. The line now cites
`infrastructure/agents/CHARTER.md`. The old citation is evidence in `references/history.md`. `SKILL.md` §Reference names
that file once.

## The hand count

| old line | what a cold reader lacks | state after |
|---|---|---|
| "`$RM_IMAGE_SKILLS_ROOT` overrides" | overrides what | "overrides where it looks" (`image_skills.py`) |
| "including creatures we draw at 3.69 cells" | which set includes them | "The 256x256 set" (256 / 3.69 = 69, the figure in the line) |
| "for 300 animals it would be" | would be what | "it is a real cost" |
| "left the file no worse than it found it" | what "it" is | "no worse than before" |
| "Ludeon relies on it" | what "it" is | "relies on this", in its own bullet |
| "because the damage was mid-tone …" (look at it) | the cause sits at the end of a 33-word sentence | "The cause: …" |
| "It has already earned its place twice. It found …" | which "it" | "the selftest" |
| "it never re-asserts the file is present, only that IF checked, it's clean" | what the pin asserts | "The pin asserts only that the file is clean IF something checks it" |
| "→ facings, mirroring, …: the `rimworld-sprite-facings` skill" | what to do | "read the … skill" |
| "An owner-kind canon check" | what owner-kind means | gloss from the `canon_check.py` docstring |
| "Full rule: `CLAUDE.md > Check for existing …`" | `CLAUDE.md` has only a pointer now | adds `design/RimMandrake/standing_rulings.md` §Check for existing regenerated art before queuing more |
| "Deploying is a separate claim from writing" | which claims | "A claim that you deployed a file is separate from a claim that you wrote it" |

## Checks, with a planted loss first

| check | input | result |
|---|---|---|
| check 1 (`checkable.py compare`) | a copy without `RSW_Anooba`/`RSW_Dragonsnake`, `ZEER_EAST_TOP_CLIP_1` and "14% of body size" | 2 lost (the id, 14%), exit 1. Check 1 did not see the two def names. |
| check 2 (`rule_doc_lint.py keep`) | the same copy | 5 lost, failed |
| check 1 | the final rewrite, with `--also` | 72 items, 0 lost, exit 0 |
| check 2 | the final rewrite, with `--also` | 212 spans, 0 lost |
| `rule_doc_lint.py selftest`, `checkable.py selftest` | — | PASS, 19 of 19 |
| `selftest_validate_skills.py`, `selftest_skills_by_work.py`, `selftest_skills_registered_or_listed.py`, `selftest_retired_era_gone.py`, `selftest_game_names_prose.py`, `selftest_image_skills.py`, `selftest_artist_role.py` | new text | PASS |
| `scripts/selftest.py --reference …/RM_ZennaqFilament.png` (the count in the text) | current code | 12 of 12 cases |

Names: this run counted Ludeon, Odyssey, Alpha Animals, Vanilla Gravship Expanded, the Artist, BENCH, FOUNDRY (a retired name), Opus and
Sovereign in old and new. Each count is equal.

## What the meaning read found

One fresh Opus reader (rm-judge, model opus) read the old and the new text. It did not get the writer's reasoning. It found
9 lines and 3 glosses. The writer repaired the 9 lines and 2 of the glosses. The reader kept the third gloss (the 256x256 set).

| first draft | why it was wrong | repair |
|---|---|---|
| "Even our own shipped art that works … and the donor … fail it" | the donor file left the group "shipped, working art" | old grouping back |
| "This project's pilot earned these rules. Both rules …" | credits three rules to the pilot | "earned both rules" |
| "The damage was mid-tone …" | cause lost | "The cause: …" |
| "The conform step scales …" (hose) | cause lost | "The cause: …" |
| the colour wash as its own bullet | lost its tie to the atlas | joined: "But on that same source, …" |
| "So the wave did not have 81 to generate" | reads as a derived conclusion | "was not 81 to generate. The wave was actually 77 …" |
| "mirrored views" | narrower than "mirroring" | "mirroring" |
| "Vanilla small creatures ship at 128 px." as a sentence | reads as a size target | the parenthesis is back |
| "To deploy is a separate claim from to write" | ungrammatical | rewritten |
| owner-kind gloss | named only half of the owner note | adds the owner-attributed passage of the prompt |
| "Full rule: … Its full text is in …" | two claims of "full" | "Rule: … Full text: …" |

The same reader then read each repair and the later sentence splits: every line SAME. Its one polish note: a canon entry
with no "Must show" lines also becomes owner kind.

After that read, the writer split one more sentence: "Three features let vanilla read at 24-32 px. The features are …". No
reader read that split.

## Conflicts (listed, not decided)

1. **Creature size.** "Generate creature sprites at 256 px, not 512" and "`fill_queue.py` warns past it": against the table
   (3.7 cells → 512, 8.0 → 1024). `fill_queue.py` and `common.canvas_for_cells` size at drawSize × 128, floor 256, ceiling
   1024. A comment in `fill_queue.py` says that the 2026-09-13 finding was measured at vanilla zoom only, and that the owner
   is not convinced of it (`ART_PAINTERLY_RESTORATION_1`, 2026-09-14).
2. **256 px is not a legal size.** 256x256 is 65,536 px, under the 655,360 minimum of "The size trap". The line probably
   means the shipped texture, not the generated picture.
3. **The 16.0 row.** The table ships 2048. The owner's later ruling (2026-09-02) and `CANVAS_CEILING_PX` (1024) stop lower.
   The 4.3 row ships 512, and the formula rounds 557 up to 1024.
4. **"Pixel-identical" with "RMSE 5-7".** Pixel-identical pictures have an RMSE of 0.
5. **Keyline.** The legibility bullet says that thin or absent outlines turn to mud. `design/RimMandrake/art_judge_brief.md`
   B1a (no outlines, card 2026-10-04) says that a sprite without an outline is correct and a heavy keyline is STYLE_OFF.
6. **Legibility gate.** "The legibility gate gates the job": `artpiped.py` says that the gate is advisory and off by default
   since 2026-09-14 (`ART_PAINTERLY_RESTORATION_1`).
7. **Canon check.** "can fail a render forever", "passes 0/0 VACUOUSLY": `canon_check.py` says that the check is an advisor,
   never a gate (owner, 2026-10-15), and that 0/0 reads UNGRADED, never PASS.
8. **Owner note grading.** The heading says the check grades every sentence of `owner_note`. `canon_check.py` also grades a
   passage of the prompt when the field is empty.
9. **Canvas.** "Canvas: size differs from the reference" is a REJECT. `validate_sprite.py --drawsize` now judges a candidate
   at scale on its rule canvas. The skill does not name that flag.
10. **Selftest reference.** The command says `any_real_sprite.png`. A soft sprite fails the semi-transparent case
    (`Pyrinth_a.png` did in this run; `selftest_sprite_reference_crisp.py` guards this).
11. **Cold load.** "~23–30 minute" here; `infrastructure/agents/CHARTER.md` says ~15 min (measured 2026-09-07).
12. **Deploy.** "deploy only your own files" here; CHARTER says "Never deploy over the uncommitted files of another window."
13. **Both or three.** "Both rules are now non-negotiable" stands above three numbered rules and "Phrase all three".
14. **81, 77 and 24.** 77 and 24 add up to 101, not 81. The two groups can overlap. The text does not say.

## Could not determine

| line | question | who would know |
|---|---|---|
| "prompt + library images for inspiration only" | if "library" is the canon library (`canon_reference`) | the author of the 2026-09-13 lesson (BENCH) |
| "fails the Terran check" | which check that is; no other doc names it | the Artist; `references/traps.md` line 19 repeats it |
| "A dead-catch job" | which job id; probably the dead sea catches (`dead_catches`) | the Artist |
| "bleeds the cold grey out at the same luminance" | how a wash changes the hue and keeps the luminance of a multiply | the author of the colour section |
| "`PLAN.md`" of a creature | where that file sits for a creature outside SeaBeasts (`write_sea_plan.py`) | the Artist |

## What this run did not test

- No art run used the new text. No image was generated.
- No measurement shows that an agent makes better sprites with the new text.
- The trigger evals of the description were not run, because the description did not change.
- The other files of `references/` are not in scope. This run read only parts of them.
