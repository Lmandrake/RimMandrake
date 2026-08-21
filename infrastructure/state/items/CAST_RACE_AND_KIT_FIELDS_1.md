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

## ruling
**DECIDE, 2026-08-21. Done. Twelve cast files, 294 characters.**

⭐ **The race half was already satisfied and nobody had checked.** Every one of the 294
header lines already carries a race in the `**Name** · race · sex · age` slot, and
`cast_to_xml.py` already parses it. ⇒ **no edit was needed for `race` at all.** The item's
framing — *"none of the 269 carries any of them"* — was true of the other three fields and
false of this one.

**The kit pass is the whole deliverable, and it is now written.** Method: one subagent per
cast file, each required to quote the sentence behind every field it proposed; then a
revision pass by DECIDE over all twelve returns.

| | |
|---|---|
| characters carrying anything | **123 of 294** (42%) |
| carrying nothing, correctly | **171** (58%) |
| `weapon:` lines | 18 |
| `apparel:` lines | 15 |
| `item:` lines | 27 |
| `skills:` lines | 101 |

**Format documented at `INHABITED_DESIGN.md` §5.7a**, with the tracing test, the
sparse-is-the-spec rule and the worked examples.

### What the revision pass actually changed

🔴 **Nine proposed defNames did not exist.** Every one was checked against
`observed/2026-08-13/dumps/defnames.live.2026-08-15.json` (73,760 defNames, 585 mods)
before anything was written.
- ✅ **Four had real substitutes and are better for it:** a Tusken gaffi stick →
  **`GS_Gaffi`** · a Tusken cycler → **`OuterRim_CyclerRifle`** · a scent-vial bandolier →
  **`Apparel_Bandolier`** · a Togorian scimitar → **`DV_MeleeWeapon_SerratedScimitar`**.
  Also `guy762_KelDorMask` and `guy762_Headband_rebreathermask` in place of a generic gas
  mask, and `guy762_TuskenMask` for a damaged Tusken mask.
- ⛔ **Five were dropped:** strapped stilts, a bent spanner, a translator collar, a Whiphid
  cooling shroud, a patched reactor suit. Nothing in 73,760 defs covers them and inventing
  one is not this item's job. **The characters keep their skills; only the prop is gone.**
- `SniperRifle` → `Gun_SniperRifle`; an Arcona salt narcotic → `Flake`.

⚠️ **Six skill-20s were proposed and three were trimmed.** 20 is the ceiling of what a
person can be, and two 20s in one cast file cheapens both. Kept: the proof-drone that has
been correct for three years, the sniper with nineteen contracts and nineteen rounds fired,
the droid that has never missed. Trimmed: a second sniper in the same file who is
*"frequently still working when it arrives"* → 17, and a second Plants 20 in the same file
→ 18.

⭐ **One agent's own flag was honoured:** it marked a `Melee` value as weakly traced and
offered to drop it. Dropped.

✅ **The low numbers are the best output in the pass** and are listed in §5.7a: `Medicine 5`
on a beloved bad nurse, `Shooting 0` on a man who carried the ramp for twenty-nine years,
`Intellectual 0` on a hunter who cannot read.

⏸️ **`xenotype` and `pawnKind` remain openly unanswered**, exactly as this item required.
⛔ Nothing here inferred a xenotype from a race string.

⇒ The parser extension is `CAST_PARSER_KIT_FIELDS_1` for BUILD.
