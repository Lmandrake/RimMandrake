# Belt review 2026-10-09

(skeleton; findings appended per area)

## Greentide - RM_CompShoalHide.cs, RM_GreentideMod.cs: no findings (comp hook order correct, Scribe symmetric, in csproj L60). Marked clean.
## LeaningScrub - RM_VenomvineFourForms.cs
- FIXED :212 and :254 `foreach (Pawn p in RadialDistinctThingsAround(...))` casts every Thing; the sleeper plant is on the centre cell, so InvalidCastException on first sweep/wake (60b611dea).
- FIXED RM_CompStrangler.CompTickLong: adjacency test used target.Position, so multi-cell targets retargeted every tick and reset wrap to 0; now Thing-overload and reset only on target change.
