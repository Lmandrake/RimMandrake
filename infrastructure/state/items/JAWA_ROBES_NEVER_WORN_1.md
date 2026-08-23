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


---

## 🔴 CORRECTION — BUILD, 2026-08-23. The premise is false, and `apparelRequired` WORKED.

**This item concludes that `apparelRequired` is unreliable. It is not. It did exactly what it
was told — the running game was simply told something else.**

### the timeline, measured

    00:12   the running game finished loading (capture 2026-08-23T07-12-04Z written)
    01:48   e479d8ae  robe + hood set on all nine Jawa kinds, deployed
    02:0x   this item's live test

**RimWorld parses defs at STARTUP.** A change deployed at 01:48 cannot reach a game that
loaded at 00:12, however byte-identical the repo and the game folder are. The deploy check in
this item is correct and irrelevant — it compares two files on DISK, and the process is
holding neither.

### what the RUNNING game actually holds for the kind that was tested

    Jawa_Tribal_Scavenger   apparelRequired  ['Apparel_WarVeil']
                            apparelTags      ['Neolithic']

⇒ **`Apparel_WarVeil` is in the observed spawn list.** The pawns wore the veil *because the
live def requires the veil*, and drew `VFET_Apparel_TribalHeavy` / `VAE_Apparel_TribalPoncho`
/ `VAE_Apparel_TribalKilt` from `Neolithic`, *because the live def names `Neolithic`*.

🔑 **Every single observed item is explained by the live def. Nothing failed.** The result is
positive evidence that `apparelRequired` is honoured, which is the opposite of this item's
conclusion.

⛔ **Do not hunt for a mod that strips `apparelRequired`.** The suspect named below was never
needed. Re-run the same test after the next cold load and expect robes and hoods.

⚠️ **The general lesson, and it has now cost two items in one night:** a live test proves what
the RUNNING game holds, never what disk holds. Before filing a live observation as a defect,
read the def out of the newest capture — that is the running game's own copy — and check it
says what you think you deployed.
