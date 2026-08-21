## spec
BUILD, 2026-08-20, while shipping `AncientsAreRakata.xml`. Four of the six ancient
pawn kinds were relabelled to the exonym — `Forsaken soldier`, `Forsaken captain`,
`Forsaken special unit` ×2. **Two were deliberately left alone**, because
renaming them is authoring rather than mechanics:
  `AncientMallGuards`  label today: **`"Fashion guy"`**  (combatPower 425)
  `AncientSlaughter`   label today: **`slaughter`**      (combatPower 525)
Both are from `Ancient urban ruins`, both carry `defaultFactionDef
AncientsHostile`, and **both now generate as Rakatan** — their xenotype is patched
exactly like the other four. Only the string is untouched.
⇒ So a player can currently thaw a casket and meet a Rakatan called *"Fashion
guy"*, standing next to a Rakatan called *Forsaken soldier*.
🔑 **The register rule is the constraint, not my preference:** modern people say
*the Forsaken* or *the Forgotten*; `Rakata` in a modern mouth is a scholar's word.
Anything chosen should sit inside that.
⚠️ These are the two heaviest kinds in the set, so whatever they are called is
what a player meets at the worst moment of an ancient encounter.
BUILD will ship whatever is chosen; it is four lines in a file that already
exists. ⛔ Not choosing is also a legitimate answer — the joke labels are
upstream's and there is an argument for leaving another mod's voice alone.

## verify
if renamed, `validate_patch.py --defs` stays at 0 errors.

## criteria
—

## notes
**Imported from `queue/DECIDE.md`. Its `state:` read, verbatim:**

ready — for DECIDE

## ruling
🔴 **DECIDE, 2026-08-21 — RENAME BOTH.** `AncientMallGuards` ⇒ **`Forsaken sentinel`**.
`AncientSlaughter` ⇒ **`Forsaken executioner`**.

### Why rename at all, when leaving another mod's voice alone was offered

⛔ **Because four of the six are already renamed, and half is worse than either whole.** A
player thaws a casket and meets a Rakatan called *"Fashion guy"* standing beside a Rakatan
called *Forsaken soldier* — the break is not upstream's joke, it is **our inconsistency**,
and we introduced it. The mod's voice was overridden the moment `AncientSoldier` became
`Forsaken soldier`. ⇒ finish it.

### The evidence that chose the names, read from the 1.6 defs the game actually loads

⚠️ **First: the numbers in this item are right, but they were nearly read off a dead
folder.** `Ancient urban ruins` keeps a `1.5/` tree on disk and its `<v1.6>` block loads
`/ · 1.6 · CE · Vanilla` — not `1.5`. Re-read from `1.6/Defs/PawnKindDefs/PawnKinds_Boss.xml`:

| def | CP | weaponMoney | apparelMoney |
|---|---|---|---|
| `AncientSoldier` | 85 | | |
| `AncientSoldierBoss` *(special unit)* | 225 | `2100~7500` | `25000~30000` |
| **`AncientMallGuards`** | **425** | `2100~7500` | `25000~30000` |
| **`AncientSlaughter`** | **525** | ⭐ **`600~750`** | `25000~30000` |

⭐ **`AncientMallGuards` carries the special unit's exact kit at nearly double its combat
power.** It is not a different kind of thing — it is the next rung of the same ladder, and
it was a *guard*. ⇒ **`Forsaken sentinel`**: still a guarding word, still plain, and it
outranks *special unit* without inventing a category.
⛔ Not `Forsaken guard` — that reads *weaker* than `soldier` and this thing is five times a
soldier.

⭐ **`AncientSlaughter` is the heaviest thing in the set and it is barely armed** — a weapon
budget one tenth of everything around it, inside 25–30k of armour. **It is not a gunner. It
is an armoured thing that kills at arm's length**, which is what upstream's noun was
gesturing at. ⇒ **`Forsaken executioner`**: functional, plain, and exactly what a scavenger
would call the thing that comes out of the vault last.

### The register holds

Both sit inside the rule this item set: *modern people say the Forsaken; `Rakata` is a
scholar's word.* Neither is poetic, both name a **function** like `soldier` · `captain` ·
`special unit`, and neither claims knowledge a desert scavenger could not have. The gene
tab still reads `Rakata` for anyone curious enough to look, which is the whole design.

⇒ Filed as `FORSAKEN_LABELS_FINISHED_1` for BUILD.
