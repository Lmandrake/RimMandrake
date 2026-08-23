## spec
🔴 **OWNER, 2026-08-23:** *"The dinosaur review sheet is v1, and it folds into the fauna pass
rather than running twice."*

**Both halves are rulings, and the second is the one that saves work.** The dinosaur review is
**IN** v1 — it is not deferred. But it does **not** get its own sheet, its own generator or its
own sitting. It happens **inside the fauna pass**, on the same rows, in the same instrument.

## 🔑 Where it actually folds in — measured, not assumed

`design/Jawa/mods/CHERRYPICK_AGENDA.md:66` already says so:

| ☐ | 4 | **Creatures / beasts** | **2,387** | by mod and by theme | *"Fiction-visible on the map. **Your dinosaur review sits here**"* |

⇒ **A dinosaur is a creature.** It is judged by the same test as every other creature on
Ash'karr — does it read as belonging on this planet — and by the same eyes, in one pass over
row 4. ⛔ **Do not build `dinosaur_review.html`.** A second sheet over a subset of the same
2,387 rows means the same sprite is judged twice by different criteria, which is how two
registers of "kept" get created and then disagree.

## ✅ And the fold-in point is OPEN as of now

The owner's fauna order was **assign → resize → density → combat → diet/temperature → names →
art flags**. Measured 2026-08-23:

| stage | item | state |
|---|---|---|
| assign | `BIOME_CREATURE_CAST_1` | ✅ **closed** |
| resize | `CREATURE_SIZES_ADJUSTED_1` | ✅ closed |
| combat | `CREATURE_COMBAT_NORMALIZED_1` | ✅ closed |
| diet/temperature | `CREATURE_DIET_AND_TEMPERATURE_1` | ✅ closed |
| names | `CAST_MISSES_TWO_NAMED_BEASTS_1` | ✅ closed |
| **art flags** | `CREATURE_ART_REVIEW_FLAGS_1` | 🔴 was **BLOCKED behind the cast** — **unblocked 2026-08-23**, its blocker closed |

⇒ **`CREATURE_ART_REVIEW_FLAGS_1` IS the dinosaur review.** It was blocked *"until the cast list
is approved"*, and the cast closed — so it had been sitting behind a gate that was already open.
Unblocked as part of this item. **That is the whole deliverable: the dinosaurs get looked at
once, there, by the owner, with everything else that lives on the planet.**

⭐ **The instrument already exists and already shows sprites** —
`design/Jawa/fauna/creature_size_review.html`, built for the resize pass. Whatever the art pass
needs should extend that, not start a third sheet.

## verify
No file named `dinosaur*` exists under `design/`, and `CREATURE_ART_REVIEW_FLAGS_1` is not
blocked. Both true 2026-08-23.

## criteria
- [x] Ruled: dinosaurs are v1, reviewed inside the fauna pass, no separate sheet.
- [x] The fold-in point identified and **unblocked**.
- [ ] ⏳ The art pass actually run — carried by `CREATURE_ART_REVIEW_FLAGS_1`, which needs the
      owner's eyes and is his to schedule.

## Watch out
⛔ **If anyone proposes a dinosaur-specific sheet again, this is the ruling that refuses it.**
The failure it prevents is two keep/cut registers over one set of sprites.
⚠️ `CREATURE_ART_REVIEW_FLAGS_1`'s own brief is **flag, fix nothing** — it surfaces egregious art
for the owner and must not start regenerating sprites on its own.
