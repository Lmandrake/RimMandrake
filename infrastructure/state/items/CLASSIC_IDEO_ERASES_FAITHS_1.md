## spec
🔴 **Measured live 2026-08-21 on the painted world. `jawa/ideo_of` reports
`ideologyActive: true` and `ideosTotal: 2`.** Not eleven.

    id 18  Astropolitan    memes 0   structureMeme null   precepts 54   initialPlayerIdeo true
    id 19  the Contract    memes 5   Structure_Ideological precepts 114  initialPlayerIdeo false

**Every one of the sixteen factions returns a null ideo name, zero memes, zero deities.**
`Astropolitan` — zero memes, no structure meme, `initialPlayerIdeo` — is the signature of
the **Classic ideoligion** option on the world-creation page.

✅ **The defs are not at fault.** All twelve `ideoName` values are present in the deployed
FactionDefs: `Meckgin`, `The Rising Order`, `The Salvation`, `the Ascendant Genome`,
`the Balance`, `the Continuity Protocol`, `the Contract`, `the Covenant of Free Wells`,
`the Green Oath`, `the Reckoning of Debts`, `the Sun-Debt`, `the Weight`.
`B54`'s offline half had already validated 8/8 FactionDefs and 4/4 patches.

🔑 **An Ideo is generated once at world creation and cannot be retrofitted**, so the
ideoligion mode chosen on that page is the difference between eleven faiths and none,
**forever**. `WORLDGEN_RUN.md` did not say so and now does, at the top.

⚠️ **ONE THING HERE IS INFERRED AND NOT MEASURED.** The single NPC ideo is `the Contract`,
which is Blackstar Company's faith, and Blackstar is the one faction created by hand with
`jawa/faction_create` *after* worldgen — so it LOOKS like `faction_create` applies the
FactionDef ideo block. **I never counted ideos before that call**, so I cannot separate a
faith the tool made from one worldgen had already made. ⛔ Do not build a repair route on it
until §verify settles it.

## verify
Two separate things, and do not conflate them.

**1. The count, on the next world generated.** `jawa/ideo_of` with no arguments →
`ideosTotal` and the per-faction rows. Eleven authored faiths present, or not.

**2. The mechanism, one line, on any world:**

    read ideosTotal  ->  jawa/faction_create a faction whose def carries an ideoName  ->  read ideosTotal

A rise of exactly one, named for that def, proves `faction_create` applies the ideo block.
No rise means the ideo already existed and my explanation above is wrong.

## criteria
- 🔴 on the world that becomes v1, `jawa/ideo_of` reads **eleven** faiths back, and their
  names match `faction_religions_spec.md`
- the ideoligion mode that produces that is recorded in `WORLDGEN_RUN.md` as a click, not a
  hope, because it is irreversible
- and the `faction_create` mechanism is either proven or struck out — not left as a maybe
  that someone later reads as a plan

## notes
Filed by CHECK 2026-08-21 from `B54`'s failing run. ⚠️ Two known text defects ride along and
are NOT this item: the Hutt Cartel's `ideoDescription` in the def is not the paragraph in
`faction_religions_spec.md` entry 2 despite a comment claiming verbatim, and a **twelfth**
faith exists that the spec never authorised — the Jawa Trade Moot carries `The Salvation`.
Both were already filed to DECIDE from `B54`'s offline half.
