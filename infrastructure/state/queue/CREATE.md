# CREATE inbox.

⚠️ This file was created 2026-08-16 on the owner's direct instruction ("add a v2 queue
item for CREATE"). There was no CREATE seat file or queue before it. Standing doctrine
(`C-V2`) is that v2 work is NOT queued and lives in `design/V2_DREAMS.md`; the owner
asked for a queue item anyway, so the canonical text is in V2_DREAMS and this is the
pointer. **Nothing here is scheduled.**

## CR-V2-RAIN  Ban rainfall planet-wide, except violent rain in the high mountains
state:    v2 — SPEC ONLY. Do not implement. Not scheduled.
owner:    2026-08-16, verbatim: *"spec out banning rainfall on any biome except those
          that occur in high mountain areas where instead it is torrential, boiling, red,
          or otherwise violent and bizarre, otherwise we have to add mutators everywhere
          to enact this (v1 approach)."*

the idea:  On a Tatooine-grade desert world rain should essentially not exist. The
          exception is the high country, where what falls is not rain as anyone would
          recognise it — **torrential, boiling, red, violent, bizarre**. Rain becomes a
          rare, frightening, altitude-locked event rather than weather.

why v1's shape is wrong:
          v1 can only express this by hanging a mutator on every tile that should be dry,
          and another on every tile that should be violent. That is thousands of
          placements to say one planetary rule, and it breaks the moment the world is
          regenerated. **The rule belongs in worldgen and in the biome/weather defs, not
          in per-tile decoration.**

what we already know, so the spec starts from fact not guesswork:
          · Rainfall is a per-tile array in the save, stored as **raw mm/year**, and it is
            already writable offline — `src/RimMandrake/Utils/worldmap.py`, verified.
            Land on a test world spanned **233–2584 mm**.
          · **Biome selection keys off rainfall.** Zeroing it does not just change a
            number; it changes which biomes are eligible, which is the real lever and
            also the real risk.
          · Altitude is available too: `tileElevation` (raw − 8192 → metres) and
            `tileHilliness`. "High mountain" is therefore a computable predicate, not a
            hand-drawn region.
          · The tidally-locked planet mod rewrites **temperature** but leaves rainfall
            alone — so rainfall is ours to define with no conflict.
          · `VEE_FertileRains` already occurs **124 times**; whatever we do must
            out-rank or remove that.

the spec should answer:
          1. Does "ban" mean rainfall 0, or a low non-zero floor? 0 may make some biomes
             ungenerable and could break plant life the campaign needs.
          2. Are the violent rains a **WeatherDef** (an event you live through), a
             **GameConditionDef**, a biome property, or a mutator confined to high tiles?
             Only the first three scale; the fourth is the v1 shape we are rejecting.
          3. What does "boiling" and "red" mean mechanically — damage, temperature spike,
             toxic buildup, terrain change? Flavour without mechanics will not survive
             contact with play.
          4. Which biomes survive at zero rainfall, and do we still get the plant cover
             the Jawa economy assumes?
          5. Does it read from orbit? A planet with one wet band in the mountains should
             be VISIBLE on the world map, or the rule is invisible to the player.

⛔ do not start:  this is a design spec, not a build. It also touches worldgen, which is
          OUT of every version by standing ruling — the write-up must stay on the design
          side of that line.
