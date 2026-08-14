# OWNER_DECISIONS.md — the single list of what is waiting on the owner

_Every question only the owner can answer lives here, and nowhere else. Scattered
across five queues and a dozen design docs they rot: two items were re-raised
after already being answered._

## The rule

- **A seat with a question for the owner adds a row here AND says so in its
  report.** One or the other is not enough — the row is the durable record, the
  report is what gets it seen.
- **Do not file a row a seat could answer itself.** "Which of us owns this" and
  "is this on-brand" are owner calls; "how do I build it" is not.
- **PROJECT sweeps this file**, clears answered rows into `CLOSED.md` with the
  outcome, and deletes the row. Answered rows do not stay here struck through.
- ⚠️ **Re-read the source before adding a row.** An already-answered item listed
  here is worse than no list at all — it spends a decision cycle on nothing.
- **Budget: 120 lines.** A list of owner decisions that grows past that is not
  being drained, which is the failure this file exists to prevent.

---

## Open

| # | the ask | why the owner and not a seat | blocked until answered | source |
|---|---|---|---|---|
| 8 | **Dinosaurs — owner wants to REVIEW THEM NEXT TO THEIR IMAGES** and pick "the wildest and weirdest". Not a keep/cut ruling: a request for a new deliverable, an image-backed review sheet of the roster. | Taste, and it cannot be exercised from defNames alone. | The fauna roster §3–§4. `[v2]`, but the deliverable is now specified. | `design/Jawa/worldbuilding/biome_and_fauna_roster.md` §7 |
| 9 | **The xenotype keep/reflavor set** — how "pure SW" versus "populated galaxy" should the roster feel? | Pure taste; there is no technical answer to find. | The Cherry Picker §2 deletions. `[v2]` | `design/Jawa/mods/cherry_picker_killlist.md` |
| 12 | 🔴 **O12 — droid raids are broken and it is our patch that broke them. Three routes, pick one.** (1) **Drop the KotOR flesh type from `DroidsAreMachines.xml`** — restores tending, loses vanilla EMP on them, **does not touch our ion weapon** (its guard moved to `IsMechanoid` on 08-13); (2) **~5 lines of Harmony** in an assembly we already ship, giving Humanlike pawns a relations tracker regardless of `IsFlesh`; (3) **accept broken droid raids.** ⛔ Retargeting to vanilla `Mechanoid` is EXCLUDED — it would make our own ion weapon block them. | A trade between three kinds of loss, none of them technical: tending vs EMP vs shipping a broken antagonist. | 🔴 **`guy762_KotORFaction_RogueDroids` raids — a v1 KEEP and the quest-critical antagonist of the KotOR distress call.** ✅ Worldgen is clear on four independent grounds; this does not block a world. | **CONFIRMED LIVE 2026-08-14** — BRIDGE ran it: 1st `KotORDroidGood_3C` spawned clean, **2nd threw NRE, 0/1 spawned**, exactly as the chain predicted. `observed/2026-08-14_O12_har_pawngen_nre.md` |
| 10 | 🔴 **Is a DISCARDED world — generated purely to measure, then thrown away — permitted?** ✅ **NOW ANSWERABLE ON EVIDENCE, 2026-08-14:** a quicktest **builds a full world** — `jawa/world_stats` returned `tilesTotal 119904, waterPct 25.0, 2 bodies, seedString "green", planetCoverage 0.3` in 127 ms, `previewOnly:false`. ⇒ **the sea can be rehearsed on disposable worlds without ever opening the planet page or the once-only Configure Factions screen.** ⚠️ Two caveats, both BRIDGE's own: this is the sea **without** `JawaSeaShaper.dll` (S1 undeployed), and a quicktest world may not use campaign parameters. **A baseline we have never had — not a solution.** Not the campaign click; a throwaway run to feed `jawa/world_stats` and iterate the sea. | The worldgen hold is the owner's, so only the owner can say what the hold does and does not forbid. | **v1 rows 2 and 7 — half the open v1 surface.** They are blocked on the sea, and the sea currently has **no measurement route at all**: the gate is 5-of-5 collectable but has nothing to read without a generated world. Waiting does not unblock them. ✅ **SEAT PREREQUISITE SATISFIED — VISION, 2026-08-14.** It asked whether a world can be generated and read without spending the once-only Configure Factions page. **It can: the quicktest that produced the reading above never opens that page, and it returned `previewOnly:false` on a 119,904-tile world.** ⇒ **Nothing technical is left in this question. What remains is purely the owner's: does the worldgen HOLD forbid a throwaway world?** ⚖️ **YES buys** the sea gate rehearsed to boredom on disposable planets before the real screen is ever opened, and a baseline that may delete the S1 build item entirely (`worldgen_sea_spec.md`, "the cheap test"). **NO costs** nothing today — the sea simply stays unmeasured and rows 2+7 stay blocked. ⚠️ Two limits stand, both BRIDGE's: this is the sea without `JawaSeaShaper.dll`, and requirements 3 and 4 of the gate are miscalibrated until the fixed build deploys — **a quicktest can answer requirements 1 and 2 only.** | PROJECT, 2026-08-14 · prerequisite closed by VISION |
| 11 | **`StrandedQuest` — enable it or leave it inert?** 3 files, deployed-but-not-enabled in `ModsConfig.xml`. OPS found it in `--plan` and correctly declined to add an unannounced quest surface on no ruling. | Adding a quest surface to the campaign world is a design/scope call, not a deploy call. | 🔴 **Must land PRE-WORLDGEN** — but worldgen is HELD, so **no deadline tonight.** It costs nothing sitting inert. | OPS `--plan`, 2026-08-14 |

---

## Checked and NOT listed — so nobody re-adds them

- **#5, `TODO.md`'s retirement, and #7, the keep-or-delete set** — both ruled by the
  owner 2026-08-13 and **executed the same hour**. Do not re-raise either; the
  outcomes are in `CLOSED.md`. `TODO.md` is now a pointer stub, so filing anything
  there is a mistake — the seat queues took the four survivors.

- **A hook guarding `git commit` without a pathspec** — described as needing the
  owner because it is config. **Already built and live:**
  `.claude/hooks/block_blanket_git_stage.py` blocks the naked-commit form. What
  remains is confirming the guard matches the intent, which is PROJECT's, not
  yours (`infrastructure/state/queue/PROJECT.md` P2).
- **Where the seat identity files live** — answered by `infrastructure/agents/` existing.
- **The mines, the Warcasket retune, `MissingArtFixes`** — all ruled; see
  `CLOSED.md`.
- **Directorate leader title, "Sector governor" vs `Sector Director`** — VISION
  owns design and can rule it. Not escalated.
