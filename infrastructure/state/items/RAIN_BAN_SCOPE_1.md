## spec
🔴 **One question for the owner. Everything else about the rain ban is decided and specced
(`items/D-V2-RAIN.md`).**

His 2026-08-19 ruling was *"Ban rainfall: v1 (but might still happen on highly mountainous
terrain!)"*. Applying it as ruled means `rain_mm = 0` on every tile below `hilliness` 4.

**That dries 433 tiles that are currently wet and are not mountains** — median elevation
696 m. 235 of them are in **The Dune Sea**. It also dries 31 tiles of
`AB_PyroclasticConflagration` and 23 of `Volcano`, which currently sit at **1668 mm**, the
same rainfall as a tropical rainforest.

⚠️ **The map has already been accepted for v1**, which is why this is not mine to do.
✅ **It repaints nothing he can see** — `rain_mm` is not rendered on the world map. The only
thing that changes is whether water falls out of the sky.

| | option | what the planet becomes |
|---|---|---|
| **(a)** | ⭐ **apply as ruled** — 0 below `hilliness` 4 | rain exists only on the 504 mountain tiles. The Dune Sea, the volcano and the badlands go dry. Most faithful to *"ban rainfall"*, and to *does it read as a photograph of a real planet* |
| **(b)** | apply everywhere except `AB_FeraliskInfestedJungle` | the 271 river-jungle tiles keep 1668 mm and still rain. The design already says the jungles are fed by **rivers, not sky**, so they do not need it — but it is the least disruptive edit |
| **(c)** | ratify what is there | 3.1% of the planet keeps tropical rainfall, including a volcano and a sand sea |

**DECIDE recommends (a).**

## verify
the owner picks a, b or c, and `D-V2-RAIN` is unblocked with the answer written into it.

## criteria
—
