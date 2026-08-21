## spec
Ruling and reasoning: `items/TWO_JOKE_LABELS_ON_SLEEPERS_1.md` `## ruling`.

`src/Jawa/Jawa_Patches/Patches/AncientsAreRakata.xml` already patches these two defs'
`xenotypeSet` and leaves their labels alone. Add the label ops beside them:

| defName | label today | ⇒ new label |
|---|---|---|
| `AncientMallGuards` | `"Fashion guy"` | `Forsaken sentinel` |
| `AncientSlaughter` | `slaughter` | `Forsaken executioner` |

✅ **Both defs DO carry a `<label>` node — verified 2026-08-21** in
`.../294100/3316062206/1.6/Defs/PawnKindDefs/PawnKinds_Boss.xml`, which is a folder that
mod's `<v1.6>` block actually loads (`/ · 1.6 · CE · Vanilla`). ⇒ a plain
`PatchOperationReplace` on `.../label` is correct and matches 1 node.
⚠️ The file's header says urban-ruins labels use **Remove + Add** because *"presence not
verifiable offline"*. That caveat is now discharged for these two — but **use whichever form
the surrounding ops already use**; consistency inside the file is worth more than saving an
op, and Remove+Add is not wrong.

⛔ **Do not touch the four already renamed** — `Forsaken soldier`, `Forsaken captain`, and
the two `Forsaken special unit`.
⛔ **Do not change either `defName`.** `AncientMallGuards` and `AncientSlaughter` are
third-party defs; renaming them breaks every reference in their own mod.
⛔ **Do not touch their `xenotypeSet` ops** — those already ship and are correct.

## verify
- `validate_patch.py --defs` stays at **0 errors**, and each new op reports **1** hit, not 0
- `grep -c "Fashion guy" src/` returns 0 outside comments
- the six ancient kinds read: soldier · captain · special unit ×2 · sentinel · executioner

## criteria
No pawn thawed out of an ancient casket is called `"Fashion guy"`.
