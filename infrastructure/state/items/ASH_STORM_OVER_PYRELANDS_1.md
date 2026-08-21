## spec
`AB_VolcanicAsh` (Alpha Biomes, already loaded — no new weather authored) now
occurs on `ZBiome_Grasslands` at commonality 3, against `DryThunderstorm` 2, so
it should read as the dominant storm without erasing the others. Relabelled to
**`ash storm`** and given a description with no volcano in it.

## verify
off the next def dump, `AB_VolcanicAsh.label` reads `ash storm`.

## criteria
🔴 **LOOK AT IT.** Land on one of the 422 authored Pyrelands tiles, pass time,
and see an ash storm: grey sky, fog overlay, ranged accuracy down. The weather
tab should name it `ash storm`.
⚠️ **The relabel is GLOBAL and that was accepted, not overlooked.**
`AB_PyroclasticConflagration` uses the same weather and is rare; if you meet it,
it will also say "ash storm", which reads correctly.
⚠️ Weather is rolled by commonality, so absence over a short window proves
nothing. If you want it now, force it rather than waiting — `jawa/weather_set`.

## notes
**from:** BUILD, 2026-08-20. `AshStorms_Pyrelands.xml` written, validated, deployed.

**Imported from `queue/CHECK.md`. Its `state:` read, verbatim:**

ready
