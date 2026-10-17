**The weir is the main failure. It reads as fishing equipment, and the composite reinforces that reading: water appears to pass around a basket rather than build up against a barrier.** The raw sprites have good material rendering; their function needs stronger large shapes.

**(a) First impressions, before the names**

1. **First:** A tapered fishing net or fish corral stretched between lashed stakes, with a reinforced collection basket at its broad end.
2. **Second:** A lit lantern mounted on a stout, rope-wrapped waterfront post.
3. **Third:** A short wooden barricade or retaining fence reinforced with scrap iron.
4. **Fourth:** A mooring bollard with a rope winch attached to its side.

**(b) Which functions fail**

- **Weir: fails strongly.** Its taper, mesh panels and tall projecting poles describe a trap. There is no continuous level crest, visible water-level difference or overflow. In the composite, the silhouette resembles a collapsed fishing platform projecting from shore.
- **Silt trap: fails without placement context.** It communicates “fence,” but nothing identifies which side catches sediment or whether water passes through it. More metal plates will not resolve that.
- **Ferry post: partially succeeds.** “Rope-handling waterfront equipment” is clear. “Ferry terminal” requires a taut rope continuing across the river, preferably toward another terminal. You already have the rope asset; that connection is more valuable than redrawing the post.
- **Bank stake lamp: succeeds.** The luminous lantern is unmistakable. The player does not need to decode its secondary role as a bank marker.

**(c) Exact weir redraw**

Use **128 × 64 native pixels** for a rotated 1×2-cell footprint. The **128 px axis crosses the current**; the 64 px axis follows it. For this specification, water flows **top to bottom**, with the bank at the right. Rotate the complete arrangement for other directions.

One constraint matters: **a two-cell structure cannot visually dam a wider river.** Either connect these modules across the channel or present it as a partial bank weir, with water visibly escaping around its exposed tip. Foam cannot disguise a missing span.

| Element | Native-pixel drawing specification | Where it belongs |
|---|---|---|
| **Overall silhouette** | Replace the triangular net with a low, blunt timber sill. Its main body occupies approximately **x=0–127, y=23–42**. Eliminate the pointed end, fan of poles and tall mesh panels. | Building sprite |
| **Crest line** | Draw one uninterrupted transverse beam at **y=23–28**. Use a **2 px light upper edge**, a darker broad timber face and a **2 px shadow underneath**. All modules must join at the same height. | Building sprite |
| **Structural supports** | Add **three or four squat, 5–7 px-wide supports**, mostly contained behind/below the crest. Keep their tops level; do not create another picket fence. Use a few large lashings, not a rope lattice. | Building sprite |
| **Spill face** | Immediately below the crest, draw a **10–14 px-deep blue-gray sheet**, approximately **y=29–42**, covering most of the span. Add several **1–2 px pale vertical streaks** and irregular dark slots where timber interrupts the flow. It must begin at the crest, with no dry gap. | Attached water overlay; bake into the sprite if only one texture can change |
| **Foam toe** | At **y=41–47**, draw a broken **3–5 px-wide pale band**. Use short connected scallops and a few dark gaps, not isolated white dots or a solid white outline. | Persistent attached overlay; minimum static version can be baked |
| **Upstream pool** | Across roughly **y=3–22**, apply a broad, low-contrast, slightly darker/cooler water tint. Suppress most fast streaks here. End the pool directly against the crest. Avoid an opaque rectangular patch. | Water surface overlay, clipped to water |
| **Downstream turbulence** | From approximately **y=47–63**, add **three to five irregular elongated eddies**, 3–8 px across, with dark centers and sparse pale rims. Let a few trails extend another 10–20 px downstream. | Water overlay; moving foam fragments may be motes |
| **Bank connection** | Embed the final **8–12 px** of the sill into shore. Add a short timber return running upstream/downstream at that end, plus a compact earth/stone wedge around it. There must be **no blue slit between beam and bank**. | Timber return in building; earth wedge in a shore overlay |
| **Exposed riverward end** | Finish with a squared cap. If it ends in open water, show a narrow curling bypass wake around that cap; if it joins another module, omit the end wake. | Cap in building; wake in water overlay |

The essential read is **quiet broad water → straight crest → falling sheet → narrow foam toe → broken wake**. Make those five bands readable before adding individual nails.

Do not make the upstream pool out of short-lived motes. It needs to remain visible continuously. Animation is optional; the hydraulic arrangement is not.

**(d) Top five changes by value per effort**

1. **Replace the weir’s tapered silhouette and add a static spill/foam toe.** Highest value, moderate effort. This changes what the object appears to do; polishing the existing net will not.
2. **Connect ferry posts with the existing taut rope asset.** Very high value, low effort. Have the rope visibly leave the drum toward the crossing. A loose rope around the base communicates storage.
3. **Give the silt trap an asymmetric sediment apron.** High value, low effort. Put a broad brown gravel/silt wedge against its upstream face, thinning away from it, with visible water passages between selected boards. Keep downstream water comparatively clear.
4. **Give the sluice a continuous wet path and an outlet.** Good value, low effort. A narrow water ribbon should connect the existing top splash through the riffles to a small discharge fan. Currently the lower section can read as a dry ladder.
5. **Improve the panning spot’s silhouette at actual game scale.** Moderate value, low effort. Simplify the pebble halo, strengthen the pan’s elliptical rim and consolidate the gold into two or three readable glints. The surrounding gravel currently competes with the useful object.

**Leave the lamp design alone.** It already communicates successfully. Across this set, more rust, rope and tiny hardware would mostly add effort without improving recognition.