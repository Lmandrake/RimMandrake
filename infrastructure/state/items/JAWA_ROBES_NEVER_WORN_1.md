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

---

## 🔴 UNPROVEN 2026-08-23 by BUILD — the live test could not have seen the fix

    robes + hoods committed and deployed   2026-08-23 01:48:31   (e479d8ae)
    the game under test LOADED             2026-08-23 00:12
    the live test ran                      2026-08-23 02:0x

**The running process started 96 minutes before the def existed.** Defs are parsed at
startup only, so that game never held `apparelRequired` on any Jawa kind — it could not
have, whatever the disk said.

⚠️ **The item's own "the def is right, and it is deployed" check is the trap, not the
proof.** It compared the repo copy against the GAME COPY ON DISK and found them identical.
Both were correct. Neither was what the running game had in memory. **A byte-identical
deploy check does not close that gap** — it is the same mistake that produced
`EMPIRE_GRUNT_SPAWNS_BARE_1` the same morning.

⇒ **This item proves nothing about whether Jawa wear robes.** Re-test after the next load,
against a game that started at or after 01:48.

## ✅ What IS settled, from the source rather than a re-test
`PawnApparelGenerator.GenerateWorkingPossibleApparelSetFor` (`:884-923`) adds
`kindDef.apparelRequired` **before** the money loop and independently of it, so the robe and
hood land whatever `apparelMoney` says. The file's comment is right.

🔑 **Three ways it can still silently fail, and a re-test should distinguish them:**
1. the def is not in `allApparelPairs` — it is filtered by `pa.thing == reqApparel[i]`, so a
   piece that never became a generatable pair is skipped with no error;
2. `CanUseStuff(pawn, pa)` finds no valid stuff;
3. `workingSet.PairOverlapsAnything(pa)` — the robe and hood must not claim the same slot.

⛔ **The About.xml claim that the fix needs `apparelMoney 0` as well is WRONG** as stated —
required apparel is not gated on money. What `apparelMoney 0` would change is the pass
*after* it: the random loop that added the ponchos, kilts and war veil observed in the test.

## ⚠️ ONE QUESTION FOR THE OWNER, deliberately not answered here
His ruling was *"Jawa wear robes+hoods ONLY"*. This file's own comment documents the
opposite as deliberate — *"`IndustrialBasic` only dresses whatever slots they leave open"* —
with `apparelMoney 350~600` on `Jawa_Colonist`.

Both readings are defensible and they produce different Jawa:
- **ONLY** ⇒ `apparelMoney 0` on all four kinds. A Jawa wears a robe and a hood and nothing
  else, ever.
- **robe and hood ALWAYS, plus whatever else fits** ⇒ leave as is. The silhouette is
  guaranteed; the remaining slots vary.

🔑 **BUILD did not change it.** Reinterpreting a one-word ruling against a file that
documents the contrary choice, while the owner is away, is not a call to make silently.
