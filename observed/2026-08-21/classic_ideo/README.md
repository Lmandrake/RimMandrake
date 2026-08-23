# CLASSIC_IDEO_ERASES_FAITHS_1 — both halves answered

**CHECK, 2026-08-21 ~17:00 PDT, 578 mods, two dev-quicktest worlds.**

## 1. The count, on a newly generated world — the defs are fine

`jawa/ideo_of` on two independently rolled quicktest worlds: **`ideosTotal: 45`**, and
**all twelve authored faiths present**, each attached to the right faction. Not two.

⇒ The painted world's `ideosTotal: 2` with a zero-meme `Astropolitan` marked
`initialPlayerIdeo` was **the Classic ideoligion option on the world-creation page**,
exactly as this item inferred. It is a choice made at the click, not a def defect.
🔴 **That page's ideoligion mode is the difference between twelve faiths and none,
forever.**

Detail and per-faith rows: `../B54_faction_faiths/`.

## 2. The mechanism — `faction_create` DOES apply the FactionDef ideo block

The item flagged this as inferred and forbade building a repair route on it. It is now
measured, by the exact line the item specified:

| step | reading |
|---|---|
| `jawa/ideo_of` before | `ideosTotal: 45` |
| `jawa/faction_create defName=CannibalPirate dryRun=false` | `created: true`, factions 57 → 58 |
| `jawa/ideo_of` after | **`ideosTotal: 46`** |

The new ideo is **id 45, `the Contract`** — the `ideoName` on `CannibalPirate`'s def —
with `primaryFactions: ['Blackstar Company']`. A rise of exactly one, named for the def.

⇒ **A faction created after worldgen gets its FactionDef's authored faith.** The repair
route the item would not let anyone build is now permitted.

⚠️ Two things worth carrying forward from the same call:
- the tool's own reply says **"SAVE the game or this is lost"**
- `CannibalPirate` arrived wearing `fixedName: Blackstar Company`, making it the
  **fifth** faction of that name on this planet — see `BLACKSTAR_IS_EVERY_PIRATE_1`
- its ideo came out with **6** memes against 5 forced: the same append leak
