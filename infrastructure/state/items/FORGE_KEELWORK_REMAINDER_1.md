# FORGE_KEELWORK_REMAINDER_1 — keelwork: the launch ring, the art, and "payload"

Split from `FORGE_GPT_ENRICHMENT_1` §1.

## built in the parent

`RM_FloatstoneKeelBrace` (TheForge `Defs/ThingDefs_Buildings/`) is a vanilla gravship facility with
`fuelSavingsPercent` 0.05, up to four per ship (TUNED). `Patches/RM_TheForge_KeelBraceLink.xml` links it to the
grav engine. MEASURED (RimSage 1.6): Odyssey gravships have no mass or payload. Launch cost is fuel, and
`Building_GravEngine.FuelSavingsPercent` is the only lever, so no Harmony hook was needed. `RM_CompKeelBrace`
shows the saving. The brace is researched by `RM_SpunstoneBonding`.

## owed

1. **Glassy ring at launch.** No launch hook exists yet. Find the launch entry point in RimSage (the gravship
   launch path in `GravshipUtility` / the gravship controller) and play a glass one-shot per linked brace.
2. **Art.** The placeholder is the floatstone block's item texture. A 1x1 pearl-white spun-sugar brace is owed.
   Check artpipe `done/`, `_artsrc/` and `registry.jsonl` first (none existed on 2026-10-01).

## open question (owner)

The spec says braces "reduce launch cost **or raise effective payload**". Vanilla has no payload. The nearest
vanilla quantity is the `SubstructureSupport` stat offset that grav field extenders carry (how much substructure a
ship can hold). Should a brace also add substructure support, and if so how much?
