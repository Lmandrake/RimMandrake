# CAST_RACE_AND_KIT_FIELDS_1 — race for all 269, kit and skills only where the prose earns it

## spec

🔴 **OWNER, 2026-08-21, verbatim:** *"Yes, please add Race for sure to the Inhabited
character specs and any special equipment and skills each one might carry to be more
interesting (e.g. if the description mentions good at combat, give them a good weapon, and
ensure they have high weapon skills). You don't have to spec out items weapons and armor
for everyone, nor all their skills. Just if they have an unusually high or low skill in
something for narrative reasons, or if they have a special weapon, armor, or unusual
item."*

This answers question 1 of `INHABITED_OPEN_QUESTIONS_1` — *the four missing character
fields* — and it answers it **differently from how that item framed it.** The item
proposed a `review-sheets` build pre-filling all four fields for all 269 people. The owner
has instead split the four:

| field | ruling |
|---|---|
| **race** | 🔴 **REQUIRED, all 269.** Every character gets one. The prose already carries race as a string; this makes it a field the parser can bind |
| **weapon · armour · unusual item** | ✅ **OPTIONAL, and deliberately sparse.** Only where the prose says something. A cast of 269 identically-kitted people is worse than one where twelve stand out |
| **skills** | ✅ **OPTIONAL, and only the OUTLIERS.** An unusually HIGH or unusually LOW skill, for a narrative reason. Not a full 12-skill block per person |
| **xenotype · pawnKind** | ⏸️ **NOT ruled here.** Still open in `INHABITED_OPEN_QUESTIONS_1`. ⛔ Do not infer a xenotype from the race string and do not let this item quietly settle it — a guessed xenotype ships a wrong-looking person into a frozen world |

🔑 **The worked example the owner gave is the acceptance test.** *"If the description
mentions good at combat, give them a good weapon, and ensure they have high weapon
skills."* ⇒ The kit must AGREE with the prose in both directions: a character described as
a fighter gets both the weapon and the Shooting/Melee to use it, and a character with no
such line gets neither. **A conflict between a hook and a kit is the defect this item is
judged on.**

⚠️ **Sparse is the specification, not a shortcut.** Do not backfill the optional fields to
look complete. An empty `weapon` on a moisture farmer is correct output.

⛔ **`Apparel_Duster` and `Apparel_Headwrap` are the only two apparel defs proven safe
against a mod removal** — both vanilla Core; that is why `Jawa_Homestead_DesertRanger`
names them. Anything modded that a character carries must be checked to exist in the
578-mod dump before it is written, or the frozen world ships a dead reference.

**Scale:** eleven `INHABITED_CAST_*.md` files, 269 characters. The twelfth faction, the
Deepwater Compact, has no cast at all — that is `DEEPWATER_CAST_ROSTER_1`, separate, and
its ~25 characters get these same fields when they are written.

## verify

- All 269 characters carry a `race`. Count it; a partial pass is a fail.
- Every `weapon`/`armour`/`item`/`skill` written traces to a specific sentence of that
  character's prose. Spot-check 10 at random against their hooks.
- No character has a kit that contradicts its prose (no unarmed "veteran gunhand", no
  master surgeon at Medicine 2).
- Every def named — weapon, apparel, item — resolves in the 578-mod def dump.
- `CAST_ROSTER_MACHINE_READABLE_1`'s parser binds the new fields with no schema change
  beyond making them optional, and `CAST_ROSTER_269_LOAD_1` still loads 269.

## criteria

269 people with a race, and a minority who are interesting because the prose said they
were — with xenotype and pawnKind still openly unanswered rather than quietly guessed.
