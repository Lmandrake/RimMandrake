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
| 1 | **One permanent enemy or two?** Design pillar 5 promises the Directorate alone; the Junkers are also `Permanent enemy: Yes` and hostile to everyone. Either the pillar describes two, or the Junkers become negotiable. | A design pillar, not a value. Changing it changes what the mid-game's "wedge" is. | The Directorate antagonist work (it currently reads `hostile=false`, and a second empire outranks it). `v1`-adjacent. | `infrastructure/state/queue/VISION.md` V6, V7 |
| 3 | **Who owns `validate_patch.py`?** It reads `Patches/` only, never `Defs/`, and does not say so. | Genuinely ambiguous — **OPS** by fail-toward-success family, **CREATE** by it being a patch-authoring tool. Guessing is how work falls out of every queue. | The fix, and the docs that describe the tool's scope. | `infrastructure/state/queue/PROJECT.md` |
| 4 | **Did the completed load already consume O5?** O5 is "write the three expected-failure signatures before the next load"; a shutdown/load cycle has since completed. | Only the owner knows which load was which. | OPS either writes the signatures or drops the item; it cannot tell which. | `infrastructure/state/queue/OPS.md` O5 |
| 5 | **Where does `TODO.md` §12's doctrine and §7's closed record go** — `agents_def.md`, a traps file, or nowhere? | The lessons are worth keeping and the queue entries are not; which destination is a judgement about what gets read. | Retiring `TODO.md` (848 lines holding ~14 live items). | `infrastructure/state/queue/PROJECT.md` P3 |
| 6 | **Space Tower — confirm VISION gates CREATE**, i.e. the design call comes before the technical due diligence, not the reverse. | It is a dependency direction between two seats; neither should set it for the other. | Both halves are stopped: CREATE is told not to start until VISION rules. `[v2]` | `infrastructure/state/queue/VISION.md` V11, `infrastructure/state/queue/CREATE.md` C2 |
| 7 | **Rule on the 9 keep-or-delete questions in `output\STALE_FILE_AUDIT.md` §E** (~3,480 lines, ~6.6 MB): the pitch deck, the idea backlog, the map-image catalogue, `Map_improver.py`, and 5 more. | Deletion is the owner's call by standing rule; the audit deliberately deleted nothing. | ~85 MB and 7.4% of the repo's prose. Buckets A and B are already cleared for action; §E is the remainder. | `output\STALE_FILE_AUDIT.md` §E |
| 8 | **Dinosaurs: full cut, or the ~20-name partial cut?** | Taste call on how the fauna roster reads. The seat leans partial and will not pick for you. | The fauna roster's §3–§4 animal work. `[v2]` | `design/Jawa/worldbuilding/biome_and_fauna_roster.md` §7 |
| 9 | **The xenotype keep/reflavor set** — how "pure SW" versus "populated galaxy" should the roster feel? | Pure taste; there is no technical answer to find. | The Cherry Picker §2 deletions. `[v2]` | `design/Jawa/mods/cherry_picker_killlist.md` |
| 10 | **Name the gravship pursuer.** "Imperial Droid Army" contradicts the ratified roster, which rules the Directorate droid-averse; the same mechanic ships as **Imperial purge units / security ordnance**. | The roster is ratified, so overriding it is not a seat's call. | The pursuer build, and the linked question of whether its units can be downed and captured. `[v2]` | `design/Jawa/worldbuilding/gravship_pursuer_mechanism.md` |

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
