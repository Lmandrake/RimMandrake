# FACTION_LABELS_ONE_LOOK_1
Read every authored faction and world label off one generated world

Created by CHECK 2026-08-21. Four items each wanted a GLANCE at a generated world's
labels. None needs a raid, a spawn, or the bridge — they need the world on screen.

## spec

🔑 **This is the LABEL half only.** Whether a faction's raids arrive as the right PAWN
KIND is a different, more expensive question that needs raids provoked over the bridge —
that stays with `B40`, `B42` and
`seven-authored-factions-generate-and-field-their-own-kinds-5b90c7`. Splitting the cheap
half out is the point: it stops four label glances from being priced as four raid rounds.

**Absorbed, every clause carried:**

| absorbed | what must read correctly on screen |
|---|---|
| `B41` | Homestead Defense League shows its name and its **High Marshal** leader title |
| `B43` | Blackstar Company reads as named, under a **Captain** |
| `B52` | **Jawa Trade Moot** settlements are present on the generated planet |
| `B63` | the world is named **Ash'karr**, with the correct apostrophe; the Sundered scenario and AmbientHorror are in the save |

⚠️ **`B63`'s apostrophe is not a nicety.** The name is baked at world creation and the
world is frozen, so a wrong glyph ships forever with no regenerate behind it.

⛔ **`B41`'s `raidsForbidden` clause is explicitly NOT carried here.** "This faction never
raids" cannot be observed in any bounded check — an absence proves nothing over any finite
window. It was the unobservable half of `B41`, and dropping it is deliberate: read the
field off the def offline if it matters, and do not pretend a look settled it.

## verify

With a generated world on screen, read the four rows above and record what each actually
says — the observed string, not "correct".

## criteria

- ✅ **PASS** when all four rows are recorded with the exact text seen.
- ❌ **FAIL** on any mismatch; a mismatch on `B63`'s world name is a **stop**, because it
  is unretrofittable once the world is frozen.
- ⛔ **NOT in scope:** raid composition, and `raidsForbidden` as noted above.
