## spec
🔴 **OWNER'S BRIEF, 2026-08-22 13:33 — the fauna pass is v1 and it is NOW.** Verbatim:
*"move the animal assignment task to v1 and right now… This is exciting! The biomes are
pretty much frozen right now as are the animals, so it's a good time for this."*

⭐ **Worked WITH the owner, not for him.** He asked for these as items *"to work through with
me now"*. Bring him decisions to react to, never a questionnaire.

### The measured starting state (578-mod dump, 2026-08-22)
| | |
|---|---|
| animal `ThingDef`s installed (intelligence `Animal`) | **2,042** |
| that can spawn anywhere on Ash'karr | **377** |
| 🔴 reach **no biome at all** | **1,665 — 82% of what we ship** |
| animals with no explicit `ComfyTemperatureMin` | **1,015 of 2,042** |

🔑 **The mechanism, so nobody invents one.** Every `BiomeDef.wildAnimals` **already lists all
1,024 candidates** as `BiomeAnimalRecord`s; assignment is the `commonality` number and most
sit at **0** (never). ⇒ This is **re-weighting an existing table in XML**, not new content.
⚠️ **Never count `wildAnimals` entries** — every biome returns 1,024 and the number is
meaningless. Count `commonality > 0`.

## the job — the final pass, and a flag list only
**Owner, 2026-08-22:** *"Then we do a final pass and optionally flag some for art review in
particularly egregious cases."*

⛔ **Blocked on the six passes before it.** This is the look-at-the-result step.

🔴 **FLAG ONLY — DO NOT FIX ANY ART.** Standing owner directive: art *fixing* is stopped until
the owner personally verifies art is broken. **This item produces a LIST for him**, and
nothing else. ⛔ Do not generate a sprite, do not edit a texture, do not "improve" anything.
✅ Observation is explicitly welcome; that is what this is.

⚠️ **Prove art is missing before flagging it as missing** — magenta first, and note the
`Graphic_Multi` blind spot where magenta never fires. A creature that renders fine in game and
badly in a contact sheet is a contact-sheet defect.
🔑 **Shrinking is the cheap remedy and it is already available** (`CREATURE_SIZES_ADJUSTED_1`).
**Prefer "flag to shrink" over "flag to redraw"** — one is free and reversible.

## verify
A ranked list of egregious cases, each with the sprite shown, and a recommended remedy
(shrink / replace with a different creature / redraw) — for the owner to rule on.

## criteria
A flag list the owner can act on. Zero art files modified by this item.
