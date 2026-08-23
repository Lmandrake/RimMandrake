## spec

🔴 **Every Jawa pawnkind requires the robe and hood, and not one Jawa wears them.**
Measured live 2026-08-23 02:0x, six `Jawa_Tribal_Scavenger` spawned into
`Jawa_IndigenousTribes` on a dev map and read back with `jawa/pawn_get`:

| wanted | what actually spawned |
|---|---|
| `guy762_Robes_jawa` + `guy762_JawaHood` | `VFET_Apparel_TribalHeavy`, `VAE_Apparel_TribalPoncho`, `VAE_Apparel_TribalKilt`, `VFET_Apparel_TribalLight`, `Apparel_WarVeil` |

**Zero of five wore either piece.** (The sixth did not appear in the list.)

### The def is right, and it is deployed

`apparelRequired = guy762_Robes_jawa, guy762_JawaHood` is present on **all four** Jawa
kinds — `Jawa_Colonist`, `Jawa_Tribal_Scavenger`, `Jawa_Tribal_Slinger`,
`Jawa_Tribal_Elder` — and the repo copy and the game copy are identical:

```
src\Jawa\Jawa_Patches\Defs\PawnKindDefs\JawaColonistPawnKinds.xml
C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\Jawa_Patches\Defs\PawnKindDefs\JawaColonistPawnKinds.xml
```

⇒ **This is not a deploy problem and not a typo.** `apparelRequired` is applied
directly to the pawn rather than through `apparelTags`, which is the whole reason that
channel was chosen — so it should be unmissable.

### The suspect was named before the test, in our own docs

`Jawa_Patches\About.xml` records the reasoning behind `SpeciesStartingGear_Tuning.xml`
and predicts this failure verbatim: *"Something in the stack is bypassing pawnkind
apparel generation wholesale; twelve active assemblies reference `PawnApparelGenerator`
and **Faction Loadout** is the standout suspect, NOT confirmed."* It also says the fix
needs **both** halves — `apparelRequired` **and** `apparelMoney 0`, because
*"apparelRequired alone still lets the random pass add"* extra clothing.

🔑 **And that second half is missing here.** Only `Jawa_Colonist` carries an
`apparelMoney` (350~600). The three TRIBAL kinds carry none at all, so the generator
keeps a default budget and dresses them. **That is the first thing to test — it is a
one-line change and it is inside our own file**, before anyone goes after Faction
Loadout.

⚠️ **But do not assume it is sufficient.** `apparelMoney 0` explains the *extra* tribal
gear; it does not by itself explain the *required* robe being absent. If setting it to
0 leaves a naked Jawa rather than a robed one, the required-apparel channel is being
bypassed too and the fix moves out of XML — which is exactly what About.xml says.

## verify

- Six `Jawa_Tribal_Scavenger` spawned through `jawa/spawn_pawn`, read with
  `jawa/pawn_get`: every one wears `guy762_Robes_jawa` and `guy762_JawaHood`.
- The same for `Jawa_Colonist`, `Jawa_Tribal_Slinger` and `Jawa_Tribal_Elder`.
- No surgical mask and no modern civilian clothing on any of them — the original
  symptom `SpeciesStartingGear_Tuning.xml` was written against.

## criteria

A Jawa looks like a Jawa on sight, without anyone checking a def to find out why not.
