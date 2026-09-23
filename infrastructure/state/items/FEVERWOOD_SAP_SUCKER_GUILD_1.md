# FEVERWOOD_SAP_SUCKER_GUILD_1 — three sap-suckers, three defences

## spec

Authority: `design/Jawa/worldbuilding/biomes/fever_wood_deep_and_mud_2026-09-23.md` §6.

**Owner's brief:** *"Perhaps more creatures that sit and drink sugary sap and resist being
bothered via various defenses?"* — then, ruling the set: *"There should be three kinds of
these sap-suckers, each with a different kind of defense above"*, selecting exactly three.

Every member shares one behaviour — **clamped to bark, drinks sap, does not flee** — and
differs only in **how it refuses to be bothered**.

| # | refusal | yields |
|---|---|---|
| 1 | **seals itself in hardened sap** — must be cracked open | a usable **lacquer** material |
| 2 | **screams for help** — sets the chorus off, pulling the crown's predators toward the disturbance | nothing directly; its value is that the biome fights for it |
| 3 | **swells so it cannot be pulled off** | burst it for a large **one-time** payout that destroys a renewable source |

⛔ **"Drops into the pool" was offered and NOT chosen** — declined, not deferred. It was the
idea that would have explained *why anything lives down there*; that question is now open
and must **not** be answered by quietly reviving this mechanism.

## the fourth member, and a flag

⚠️ The **thornbug** already exists (`the_fever_wood.md` §4) with its own refusal — the
nectar contract, protected by **hard ban 6** (*never yields under fear*). Reading taken:
the guild is **thornbug + these three**, since all three chosen defences differ from the
contract. ⚠️ **Flag to the owner if he meant three *including* the thornbug.**

## dependencies

- 🔴 **They have nothing to eat until the flora roster lands.** `RM_Ossagrel`
  (`FEVERWOOD_FLORA_ROSTER_1`, row 5) is the host cane they clamp to and drink from — it
  was authored specifically to feed this guild.
- ✅ **The yield gate is already built.** `RM_CompGatherableCalmGated`
  (`FEVER_WOOD_MECHANICS_1` F8) gates `Active`, not `Gathered()` — the spec's original plan
  did not compile, because `CompHasGatherableBodyResource.Gathered(Pawn)` is
  `public void`, non-virtual. `Active` is the real and only seam both vanilla callers use.
  ⛔ Do not re-derive this; it is a settled correction.
- ⚠️ F8 shipped as a **compiling skeleton with no `ThingDef`/`PawnKindDef` attached**, and
  there was **zero repo precedent for `CompProperties_HasGatherableBodyResource`** when it
  was written. This item owns creating that precedent.

## why defence #2 matters more than it looks

🔑 **The ants steal these creatures ALIVE** (sheet §4 — theft, not slaughter). So a
well-defended species is one the ants **cannot take**, which makes species placement a real
perimeter decision. Defence #2 is the one that converts a theft raid into a fight the crown
joins on the player's side.

⚠️ **Defence #2 competes with a ruling.** The chorus goes silent **only for the water**
(§4). A screamer that triggers the chorus must therefore be a *rise* in noise, never a
silence — ⛔ do not implement it as a hush, or it collides with the deep thing's exclusive
tell and destroys the biome's clearest signal.

## Watch out

Names are unset — all three need `RM_` tier invented names, and none may collide with the
Greentide's 22 or with this biome's 18 plants.
