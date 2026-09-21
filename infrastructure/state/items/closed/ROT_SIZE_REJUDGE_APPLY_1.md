# ROT_SIZE_REJUDGE_APPLY_1

## why this exists

The first Rot review sheet **understated 11 AlphaBiomes flora rows by up to 6×**. The
generator parsed donor `<ThingDef>` blocks as TEXT, and AlphaBiomes puts a nested
`<descriptionHyperlinks><ThingDef>…</ThingDef></descriptionHyperlinks>` early in the
def, so the closing tag fired inside the hyperlink list and truncated before
`<plant>`. `visualSizeRange` read as absent and the vanilla `0.3~1.00` fallback was
recorded AS a measurement. Proof: the only two AB rows without `descriptionHyperlinks`
before `<plant>` are exactly the two that came out right. Verified 13/13 against the
raw XML.

The owner re-judged against corrected numbers on 2026-09-19 and froze the result:
`Transient/rot_size_rejudge_2026-09-19.decisions.json` (36 writes, `savedBy:
review-sheet-sidecar`). 🔴 That file is FROZEN owner data — read it, never rewrite it.

## spec — apply these 11 rulings, verbatim

| defName | his ruling |
|---|---|
| `AB_AgaricusDomeCap` | 2 |
| `AB_ArbuscularMycorrhiza` | 8 |
| `AB_DribblingCap` | 9 |
| `AB_GiantAgarilux` | 6 still, **but keep the sparkling luminous violet spots** |
| `AB_WitchesOyster` | 3 |
| `RUT_BleedingTooth` | 1.5 |
| `RUT_CrimsonCap` | .9 |
| `RUT_FlakespireFungus` | 2 |
| `RUT_Shinecap` | 3 |
| `RUT_VioletWimple` | 1 |
| `AA_MycoidColossus` | **Size 12** — plus an art defect, tracked at `MYCOID_COLOSSUS_ART_MISROUTE_1` |

Numbers are **mature size in cells**. For flora that is `drawSize.x × visualSizeRange.max`
and `drawSize` is a constant 1.0 across all 40 rows, so the knob is `visualSizeRange`.
Engine rule confirmed from source: `Plant.Print` → `drawSize.x *
visualSizeRange.LerpThroughRange(growth)`.

⚠️ **The mycoid colossus is a CREATURE, not a plant** — its size is
`bodyGraphicData.drawSize` on the adult life stage of its **PawnKindDef**, not
anything on the ThingDef.

🔴 **The adult value was 15, not 4.** MEASURED 2026-09-19 against the live def dump
(`mods=621/fedd946a33bb7137`, captured 16:54Z): `AA_MycoidColossus`'s PawnKindDef
carries drawSize **4 / 5 / 15** across baby / juvenile / adult. The **4 is the BABY
stage** — reading life stage `[0]` instead of the adult is how it was mistaken for
the live size. And the 15 is *ours*: `RotSpecies_NamesAndSizes.xml` already patched
`lifeStages/li[3]/bodyGraphicData/drawSize` to 15 in `df261b2bc`, so it is exactly
what the running game carries. His 12 was therefore applied against 15.

## 5 rows he left UNDECIDED on purpose

`AB_Agarilux` · `AB_GlowingAgarilux` · `AB_Glowstool` · `AB_LilacBeacon` ·
`AB_SlimyPholiota`

Posture is blacklist, so undecided = **size unchanged**. ⛔ Do not invent numbers for
these; they were the rows where the sheet had lied to him and he chose not to rule.

## verify

`validate_patch.py` with BOTH `--defs` and `--live`, then confirm from a post-load def
dump — not from the patch file. A `PatchOperationConditional` returns true on no match,
so a clean log does not prove a size landed.

## state (2026-09-21, FOUNDRY) — already applied, deployed, now closing

The 11 rulings were already applied and committed at `dab0bba2b` (2026-09-19) — checked
source directly: all 10 flora targets' `visualSizeRange` max and the colossus PawnKindDef's
adult `drawSize` already match every ruling in the table above byte-for-byte, and the 5
undecided rows are byte-unchanged. That commit's own message flagged two things still
owed: **deploy**, and a **post-load def dump check** (a `PatchOperationConditional` returns
true on no match, so a clean source diff alone doesn't prove it landed live).

**Deploy**: `deploy_custom_mods.py --mod RotSporeKit` / `--mod UtinniPatches` both already
report "in sync" — the fix has been in the live Mods folder for some time, nothing to push.

**Post-load verification**: read `ThingDef.json` from the most recent def dump
(`captures/2026-09-21T08-56-31Z`, mods=post-rename). The dump does not carry the nested
`<plant>` block at all (a known blind-spot of this capture format — no `visualSizeRange`
on ANY ThingDef in it, donor or ours), so the exact numeric field is UNMEASURABLE by this
instrument. What IS measurable: the **label** field, set by a sibling operation inside the
same `PatchOperationSequence`/outer `PatchOperationConditional` as the `visualSizeRange`
replace. All 5 AB_ donor labels read live as their campaign renames (`skarrow dome`,
`turrok shelf`, `vokkun pillar`, `bollusk trunk`, `ruvvak weeper`) — proof the same gated
operation block actually fired against the live defs, not silently no-op'd for a missing
donor mod. Combined with the original commit's own `validate_patch.py --live --defs: 0
errors` and the source match, this is as much confirmation as the available instruments
give; the `<plant>` field itself was never independently re-measured live and is not
claimed as MEASURED.

Closing.
