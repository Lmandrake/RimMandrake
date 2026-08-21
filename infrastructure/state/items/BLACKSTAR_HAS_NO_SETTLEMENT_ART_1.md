## spec
`AM_EnemyPirate` is the FactionDef the **Blackstar Company** is built on, and its
`settlementTexturePath` is **null**. Every other faction in the roster has one
(`World/WorldObjects/DefaultSettlement`, or `TribalSettlement` for the tribes).
The engine path, read out of the live stack trace, not guessed:
  `Settlement.get_Material()` → `MaterialPool.MatFrom(null, ...)`
  → `ContentFinder.Get(null)` → `ModContentHolder.Get(null)`
  → `Dictionary.FindEntry(null)` → **ArgumentNullException: Parameter name: key**
⇒ **once per settlement, per frame.** Four Blackstar holdings took TPS from 60 to
**3.7 (273 ms/tick)** and flooded the debug log. The game is effectively unusable
on the world map while they exist.
FIX: a `PatchOperationAdd` in `Jawa_Patches` giving `AM_EnemyPirate` a
`settlementTexturePath`. ⛔ `AM_EnemyPirate` is a THIRD-PARTY def — patch it, do
not edit the mod. `World/WorldObjects/DefaultSettlement` is what every other
faction in our roster uses and it is vanilla, so it cannot go missing.
📌 Relates to B43 (turn vanilla pirates into the Blackstar Company). If B43 ends up
defining our OWN FactionDef the field belongs there instead — but until then the
roster names `AM_EnemyPirate` and the patch is the shortest fix.

## verify
`validate_patch.py --defs` 0 errors and the xpath reports 1 hit, not 0.
Then off the regenerated dump: `AM_EnemyPirate.settlementTexturePath` is non-null.

## criteria
place the four Blackstar settlements on a live world and watch the world map for
          ten seconds. 🔴 ZERO `Error while drawing Settlement` lines, and TPS stays at 60.
          ⚠️ THIS IS WHY THE ITEM EXISTS AND HOW IT LIES: **nothing numeric caught it.**
          `world_settlements_import` reported success and read 72 back off the engine;
          `world_lint` reported 76 findings and none of them was this. It was visible only
          in a screenshot. Do not close it on a count.
📌        WHY IT WAS INVISIBLE UNTIL NOW: worldgen never created a Blackstar settlement,
          because the faction had none. No settlement, no draw, no throw. The authored
          roster is the first thing that ever made one exist.

## notes
🔴 **THE FIX BELOW IS SUPERSEDED — read `BLACKSTAR_NEVER_GENERATES_1` first (2026-08-20).**
The crash is real and the diagnosis is right, but `AM_EnemyPirate` is the WRONG DEF to be
using at all: it is `hidden=True` with `settlementGenerationWeight=0`, from a third-party
mod, while the actually-reskinned `Blackstar Company` is vanilla **`Pirate`** — which
already has `World/WorldObjects/DefaultSettlement`. ⇒ **Repoint the roster instead of
patching a texture onto a hidden faction.** Doing that closes this item as a side effect
and costs no patch. ⛔ Do not ship the `PatchOperationAdd` described below.

**from:** CHECK, 2026-08-20, live. Found by LOOKING at the planet after the authored
settlement roster went in — every numeric check passed while this was happening.

**Imported from `queue/BUILD.md`. Its `state:` read, verbatim:**

void 2026-08-20 — closed by `BLACKSTAR_NEVER_GENERATES_1` rather than by a patch,
exactly as this item's own superseding header says. `AM_EnemyPirate` is the wrong
def to be using at all; the real Blackstar Company is vanilla `Pirate`, which
already carries `World/WorldObjects/DefaultSettlement`. REP repointed the four
CSV rows, so no `settlementTexturePath` patch is needed and none was written.
⛔ **The `PatchOperationAdd` described below was NOT shipped. Do not ship it.**
⚠️ The crash it describes was real and its diagnosis was right — a null
`settlementTexturePath` throws once per settlement per frame and took TPS to 3.7.
It simply cannot happen once nothing points at that faction.
⏳ It stays open in one sense only: nobody has SEEN the four Blackstar holdings
render, because `Pirate` is not in the live world at all. That is tracked in
`BLACKSTAR_NEVER_GENERATES_1` and in `queue/CHECK.md`.
