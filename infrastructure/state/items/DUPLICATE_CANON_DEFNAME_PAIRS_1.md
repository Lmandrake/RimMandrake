# DUPLICATE_CANON_DEFNAME_PAIRS_1 — one canon animal, two defNames, both cast

## what was measured — 2026-09-22

Found while adjudicating `BIOME_SPECIFIC_FAUNA_LAW_1`. Four canon Star Wars animals exist in the
shipped content **twice**: once under the bare donor defName and once under our own `RSW_` port.
Both copies are wired into `<wildAnimals>`, in *different* biomes.

| animal | donor defName is in | our `RSW_` port is in | distinct places |
|---|---|---|---|
| gizka | Greentide, `RUT_AridShrubland` | Greentide, Pyrelands, `RUT_Desert`, `RUT_ExtremeDesert` | **5** |
| kreetle | `RUT_AridShrubland`, `RUT_Miasma`, `RUT_Webwork` | `RUT_Desert`, `RUT_ExtremeDesert` | **5** |
| nuna | Greentide, `RUT_AridShrubland`, `RUT_FeverWood` | Greentide, Pyrelands, `RUT_Desert` | **5** |
| worrt | Greentide, `RUT_AridShrubland` | Greentide, `RUT_Desert` | **3** |

⚠️ `Shiro` / `RSW_ShiroTrap` is **not** confirmed as such a pair — a trap-form may be a
deliberately different creature. Establish that before touching it.

## why it matters more than the multi-homing it was found inside

1. 🔴 **`selftest_no_duplicate_defs.py` cannot catch this.** That guard (built 2026-09-20 for
   `STONEBACK_DEFNAME_COLLISION_1`) finds two *defs sharing one defName*. This is the inverse —
   **one animal under two different defNames** — so every name is unique and the guard passes.
2. **It makes `BIOME_SPECIFIC_FAUNA_LAW_1` unenforceable as written.** That law is applied per
   defName, so `RSW_Kreetle` can be reduced to one home and be fully compliant while the *animal*
   kreetle still appears in five biomes under the donor name. A player meeting "kreetle" in the
   Webwork and in the Desert is meeting two unrelated ThingDefs.
3. **Stats, art and body may silently differ** between the two copies, so the same animal can read
   as two creatures. UNMEASURED — the donor defs are not under `src/` and are unreadable from the
   Mac laptop.

## ✅ Desktop step 1 done — donor vs `RSW_` port compared per animal (MEASURED 2026-09-23)

Report: `Transient/duplicate_canon_pairs_desktop_2026-09-23.md` (side-by-side tables, path:line).

- **gizka, kreetle, worrt: SAME CREATURE.** The donor ThingDef/PawnKindDef (Mlie's `Races_Animal_SW.xml`,
  workshop 3497316713) and our `RSW_` port are byte-identical apart from renamed cross-refs (leather/meat/egg/sound);
  the `texPath` strings are literally identical, so both defNames render the same sprite.
- **nuna: SAME CREATURE by content; the standing ruling's premise is false.** `STARWARS_DONOR_SUNSET_1` (closed) kept
  both on the ground that *"Mlie's becomes distinct alongside vanilla Core's Nuna"*. MEASURED on the Desktop: a
  full-text search of Core + all five DLC `Defs/` trees finds **zero** occurrences of "Nuna" — there is no vanilla
  Nuna. ⇒ Owner call: the keep-both ruling was made on a wrong fact, so the nuna pair is a merge candidate like
  the other three. Not resolved here.
- Donor mod `mlie.starwarsanimalcollection` is **ACTIVE** in the live list (623 active, parsed).
- Wiring today, file-read: donor bare names sit on `RUT_AridShrubland`/`RUT_Greentide`/`RUT_Miasma`/`RUT_Webwork`/
  `RUT_FeverWood`; the `RSW_` ports sit on `RUT_Desert`/`RUT_ExtremeDesert` and, via the Utinni patches, on
  `RM_Greentide`/`RM_Pyrelands`. ⚠️ Corrections to this item's own table: `RUT_Pyrelands` is not a file (the
  Pyrelands twin is the donor `ZBiome_Grasslands` + `RM_Pyrelands`), and `RM_Pyrelands` already carries **only** the
  `RSW_` forms of gizka/nuna. The live tile-holder `RUT_Greentide` carries only donor-bare names while its `RSW_`
  counterparts sit on the not-yet-painted `RM_Greentide` — so today's live double-cast is smaller than the 5/5/5/3
  counts suggest once same-named `RUT_`/`RM_` twins are counted once.
- `Shiro`/`RSW_ShiroTrap` untouched — not an established pair.

**✅ RULED — decision taken by question card, 2026-09-23: MERGE ALL FOUR ONTO THE `RSW_` PORT.** Gizka, kreetle,
nuna and worrt each keep exactly one defName in our content, the `RSW_` one. The earlier keep-both ruling for nuna
(`STARWARS_DONOR_SUNSET_1`, closed) is superseded — its premise, a vanilla Core nuna, does not exist.

**NEXT (FOUNDRY, offline):** in every def and patch of ours that names the donor bare defName (`Gizka`, `Kreetle`,
`Nuna`, `Worrt` — the wiring table above and the report list the files: `RUT_AridShrubland`, `RUT_Greentide`,
`RUT_Miasma`, `RUT_Webwork`, `RUT_FeverWood`, plus any `WildAnimals_*.xml`/doctrine patch), replace the row with the
`RSW_` defName at the same commonality — under a `MayRequire="mandrake.rsw.swbestiary"` guard where the file is
RimMandrake-tier per arch §7 Q11. Mlie's mod stays installed; its defs simply stop being cast by us. Do not touch
`Shiro`/`RSW_ShiroTrap`. Then each biome's own sitting applies the one-home law to the single defName.

## spec

1. **Confirm the pairing per animal** — that the donor def and the `RSW_` port really are the same
   canon creature and not a deliberate variant. `Shiro`/`RSW_ShiroTrap` is the case to be careful
   with. Use `design/RimStarWars/canon_references/` where an entry exists (gizka, kreetle, nuna
   all have one); ⛔ absence from that library is not evidence of anything (137 entries by design).
2. **Decide which defName survives per animal.** The `RSW_` port is the presumptive keeper — it is
   ours, it is in-tier per `NAMING_SCHEME_PLAN.md`, and it does not depend on a donor mod staying
   active. But check whether the donor def is still load-bearing for donor art or cross-refs
   first, as the `AA_JOE_DESERT_PORT_BATCH_1` precedent did.
3. **Repoint every roster and patch** from the losing defName to the survivor, merging the two
   home sets — and only THEN apply the one-home law to the merged set, not before.
4. **Extend the guard.** A selftest that flags two defs whose `label` matches while their
   `defName` differs would have caught all four. That is the missing check, and it is cheap.

## verify

No canon animal is reachable under two defNames in any `<wildAnimals>` block. A label-collision
selftest exists and fails when a pair is reintroduced (prove it by reintroducing one, the way
`selftest_no_duplicate_defs.py` was proven).

## criteria

A player never meets the same creature twice as two different animals.

## Watch out

- 🔴 **Do not apply the one-home law to these four until they are merged.** Reducing `RSW_Gizka`
  to one home while the donor `Gizka` keeps two produces a *compliant-looking* roster set that
  still has the animal in three places. Merge first, then adjudicate once.
- ⚠️ Roster counts are inflated wherever a pair is double-cast, so any "this roster is thin"
  judgement that touches these biomes is suspect until the merge lands. `RUT_AridShrubland`
  carries all four donor copies.
