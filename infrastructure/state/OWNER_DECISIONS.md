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
| 5 | **Where does `TODO.md` §12's doctrine and §7's closed record go** — `agents_def.md`, a traps file, or nowhere? | The lessons are worth keeping and the queue entries are not; which destination is a judgement about what gets read. | Retiring `TODO.md` (848 lines holding ~14 live items). | `infrastructure/state/queue/PROJECT.md` P3 |
| 7 | **Rule on the keep-or-delete set** — the pitch deck, the idea backlog, the map-image catalogue, `Map_improver.py` and ~5 more. ⚠️ **The audit that listed them is now stale** (every path predates the restructure) and was disposed; PROJECT must RE-RUN it against the new tree first. Owner will review interactively. | Deletion is the owner's call by standing rule. | ~85 MB and a chunk of the repo's prose. | re-run needed |
| 8 | **Dinosaurs — owner wants to REVIEW THEM NEXT TO THEIR IMAGES** and pick "the wildest and weirdest". Not a keep/cut ruling: a request for a new deliverable, an image-backed review sheet of the roster. | Taste, and it cannot be exercised from defNames alone. | The fauna roster §3–§4. `[v2]`, but the deliverable is now specified. | `design/Jawa/mods/biome_and_fauna_roster.md` §7 |
| 9 | **The xenotype keep/reflavor set** — how "pure SW" versus "populated galaxy" should the roster feel? | Pure taste; there is no technical answer to find. | The Cherry Picker §2 deletions. `[v2]` | `design/Jawa/mods/cherry_picker_killlist.md` |

---

## Checked and NOT listed — so nobody re-adds them

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
