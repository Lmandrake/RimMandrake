# FEVERWOOD_DIANOGA_GIANT_MAP_1 — in the campaign, the dianoga goes over the whole sekkulaath, not just the tank

Caused by `FEVERWOOD_SCORING_SITTING_1` (turn 1). Campaign tier, `mandrake.rsw.swbestiary`
(`src/RimStarWars/SWBestiary/Patches/`). Design: `feverwood_bedazzle_review_2026-10-02.md` §1 ("The dianoga
is only half mapped"; the reverse slip), §4 row 0, §8. Rulings: owner 2026-09-23, *"Map it to the Dianoga
when Utinni is active"* and *"It belongs only in tank prisons and the Fever Wood"*; **build first: land the
decided work plus the giant's story** (decision taken by question card 2026-10-02 11:12 PDT), whose option
text reads *"take the Star Wars lines out of the free tentacles and put the dianoga over the whole monster in
the campaign"*. Tier law: `biome_mod_architecture.md` §7 Q11/Q11a (canon names live only in the campaign
layer).

## spec

1. **The free text is `BIOME_TIER_CLEANUP_1` (b)'s** (the snare, lash, sentinel and spleen-chemical lines);
   this item does not duplicate it. It depends on it, because the canon facts those lines drop come back here.
2. **A campaign patch** `RSW_Sekkulaath_DianogaGiant.xml` (beside `RSW_SekkulaathTank_DianogaSwap.xml`)
   replaces, on all six limb ThingDefs (`RM_Sekkulaath_Feeler/Snare/Lash/Porter/Sentinel/Bloom`), the
   `label` and `description` with dianoga wording: the giant dianoga's limbs, carrying the canon facts the free
   text drops (suckered tentacles, the giant form's barbed tentacles, excellent hearing; the eye-stalk on the
   bloom). Sourced from `design/RimStarWars/canon_references/` if an entry exists, else Wookieepedia's
   `action=parse` API; never from a donor defName.
3. **Every other player-facing string naming the sekkulaath** in a loaded def (letters, the escape and
   establish messages in `RM_CompEscapedCaptive`/`RM_CompCapturedSpecimen` if they are keyed strings, the
   juvenile's description, the products' descriptions, the suppressant's job report, Mod Settings labels are
   exempt) is mapped to *dianoga* by the same patch or by a campaign `Keyed`/`DefInjected` language file.
   Strings hardcoded in C# are listed first; any that cannot be patched move into `Keyed` in the free mod
   (free wording) so the campaign can override them.
4. **Guards:** `PatchOperationFindMod` / `PatchOperationConditional` on each operation, **never**
   `<Operation MayRequire=…>` (inert in 1.6, `PATCH_MAYREQUIRE_GUARD_INERT_1`). Fix the same on the two
   operations of `RSW_SekkulaathTank_DianogaSwap.xml` while there.
5. The free mod keeps the sekkulaath and stays free of any `RSW_`/canon reference.

Depends on: `BIOME_TIER_CLEANUP_1` (b), Fever Wood part.

## criteria

- Offline parse of the free mod (`src/RimMandrake/FeverWood/`, all XML): no `dianoga` and no `canon` in any
  `label`/`description`/`text` node; no `RSW_` reference.
- With the campaign layer loaded: `jawa/get_defs` on `ThingDef/RM_Sekkulaath_<X>` for all six (reading
  `success`/`foundCount` = 6): each loaded `label` or `description` contains `dianoga`.
- With only the free mod loaded: the same six reads contain `sekkulaath` and not `dianoga`.
- Offline parse of both campaign patch files: no `<Operation>` node carries a `MayRequire` attribute.
