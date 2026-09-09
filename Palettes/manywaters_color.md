# manywaters_color — coloured water and slime

**Fluid-tint palette, v1.** Five colours, each authored as a matched pair — one
`RM_Water_<Colour>` (tints vanilla's `WaterShallowRamp`) and one `RM_Slime_<Colour>`
(tints Alpha Biomes' `AB_SlimeRamp`, gated `MayRequire="sarg.alphabiomes"`) — plus a
tinted `RM_Fleck_Steam_<Colour>` for the slime's ambient bubble effect and, where
Dubs Bad Hygiene's Thirst add-on is active, a matching `RM_WaterBottle_<Colour>`
drinkable item. All defs live in `src/RimMandrake/ManyWaters/Defs/`.

## The one thing that makes this palette different

🔴 **These RGB values are FRESHLY AUTHORED, not read from any mod's XML or
calibrated off a screen.** Unlike `sandscoured.md`'s structure colours, there was
nothing existing to source a "rust water" or "violet slime" tint from — these are
this item's own invention. Treat them as a first draft the owner can retint on
sight once he has looked at the quicktest grid; nothing here is load-bearing lore.

Colour still MULTIPLIES the texture (same law as every other palette here) — a
pale tint like Chalk reads close to the untinted ramp, a saturated one like Violet
reads strongly, because the base water/slime ramps are themselves fairly light.

```palette
# --------------------------------------------------------------- colours
color RM_Rust        168,92,58   @mod=ManyWaters (local) | iron oxide — old blood, mine runoff
color RM_Verdigris    70,168,140 @mod=ManyWaters (local) | copper salts — patinated bronze
color RM_Amber       198,150,60  @mod=ManyWaters (local) | resin or spice residue
color RM_Violet      120,80,168  @mod=ManyWaters (local) | something living in it, or used to
color RM_Chalk       200,196,178 @mod=ManyWaters (local) | dissolved limestone, milky

# ----------------------------------------------------------------- roles
role  WATER_RUST       RM_Water_Rust        @mod=ManyWaters (local) | tinted WaterShallowRamp
role  WATER_VERDIGRIS  RM_Water_Verdigris   @mod=ManyWaters (local) | tinted WaterShallowRamp
role  WATER_AMBER      RM_Water_Amber       @mod=ManyWaters (local) | tinted WaterShallowRamp
role  WATER_VIOLET     RM_Water_Violet      @mod=ManyWaters (local) | tinted WaterShallowRamp
role  WATER_CHALK      RM_Water_Chalk       @mod=ManyWaters (local) | tinted WaterShallowRamp
role  SLIME_RUST       RM_Slime_Rust        @mod=ManyWaters (local) | tinted AB_SlimeRamp, needs Alpha Biomes
role  SLIME_VERDIGRIS  RM_Slime_Verdigris   @mod=ManyWaters (local) | tinted AB_SlimeRamp, needs Alpha Biomes
role  SLIME_AMBER      RM_Slime_Amber       @mod=ManyWaters (local) | tinted AB_SlimeRamp, needs Alpha Biomes
role  SLIME_VIOLET     RM_Slime_Violet      @mod=ManyWaters (local) | tinted AB_SlimeRamp, needs Alpha Biomes
role  SLIME_CHALK      RM_Slime_Chalk       @mod=ManyWaters (local) | tinted AB_SlimeRamp, needs Alpha Biomes

# -------------------------------------------------------------------- rules
rule Colour MULTIPLIES here too — see sandscoured.md's law. A saturated colour reads strongly against these particular (light) base ramps; do not expect the same result against a darker terrain texture.
rule Slime defs and the tinted flecks are both MayRequire="sarg.alphabiomes" / built from AB's `AB_SlimeRamp` asset — Alpha Biomes absent means these rows do not load, not that they render wrong.
rule The bottled-water variants (`RM_WaterBottle_<Colour>`) only exist behind Dubs Bad Hygiene's Thirst add-on (`Dubwise.DubsBadHygiene.Thirst` active) — the item itself is defined in Lite (`Dubwise.DubsBadHygiene.Lite`, `DBH_WaterBottle`), which is the actual MayRequire gate used.
rule Do not add the `temporary=true` canal-flood siblings or FluidDefs here — MANYWATERS_COLOR_SUPPORT_1 deferred those until the owner picks which colours stay.

# -------------------------------------------------------------------- used
used MANYWATERS_COLOR_SUPPORT_1 v1 (2026-09-09): all five colours authored for both water and slime, painted on a quicktest grid for the owner to pick from. None ruled yet.
```

## Owed

Which colours stay, and whether any want per-fluid divergence (a colour that reads
right on water but wrong on slime, or vice versa) — the design allowed for that but
v1 paired them 1:1 for the simplest possible grid. Ratios/frequency are out of
scope; this is a look-and-pick palette, not a spawn table.
