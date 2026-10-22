## spec
Child 1 of `CANAL_COVER_DESIGN_WET_FOXHOLE`. Trench cover, AI use and readout; design
`design/RimMandrake/canal_cover_design_2026-10-17.md` §3, §4, §7-§10 (steps 1-3, 5-8). LAW 2 replaced (owner
2026-10-18): depth affects movement, liquid **and cover**.
- Any dug hole with a wall, wet or dry (Q2). Cover from each neighbour whose ground is higher than the pawn's floor, read
  like vanilla sandbags (8 neighbours, angle and distance falloff). Natural water reads 0; a pit cover reads ground; a
  suspension deck does not make a wall (the floor runs on beneath it).
- `block = 0.75 × clamp(h/H, 0, 1) × strength`: waist-deep a bit under sandbags, chest-deep a bit over (Q3).
- `RM_TrenchCoverMath.cs` (pure, selftested); postfix on `CoverUtility.CalculateOverallBlockChance`; the
  `ShotReport.HitReportFor` fold that avoids the null-cover-Thing trap (§2); "trench wall: blocks N%" readout line.
- No blast cover (Q7): explosions unchanged.
- Raiders use it (Q5) with the cage check: `CastPositionPreference` scores 0 for a square in a pocket the caster could
  not climb out of.
- Settings `trenchCoverEnabled`, `trenchCoverStrength`, `trenchCoverCap`, `trenchAiAvoidsCages` (§9).
- **C# comments/text still stating the old LAW 2 — fix in this item (agents must not hand-edit them elsewhere):**
  `src/RimMandrake/FlowWorks/Source/RM_ExcavationDepth.cs:15-23` (docstring "never affects sight, cover or projectile
  arcs"); `RimMandrakeFlowWorksMod.cs:1601` (setting tooltip "nothing here changes accuracy, cover or sight. Off: depth
  never affects shooting"); `Superdeep/RM_PitLipOcclusion.cs:20` and `Superdeep/RM_PitDepthDraw.cs:9` ("LAW 2 (depth
  never touches sight, shooting or cover)"). Re-grep `LAW 2` in `src/RimMandrake/FlowWorks` at build.
- Functional script `src/RimMandrake/FlowWorks/northstar/trench_cover_proof.py`; walk row in
  `design/validation_walks/RimMandrake/FlowWorks.md`.
Dependencies: V5 `PIT_RULES_REWIRE_RELATIVE_NOT_ABSOLUTE` (done); reads metres once P4 `LIQUID_DEPTH_REWIRE_FIVE_IS_DEAD`
lands (notches × 0.5 m until then); the cage guard trusts the pocket grid that `PIT_CLIMB_PROVE_RAIDERS_VS_SHEER_TRENCH`
proves. Check `HitReportFor` field names with RimSage and run modcheck for combat-overhaul mods before building. Art:
none. ESTIMATE 2 to 2.5 agent-days + 0.5 day live.

## verify
- L1: math selftests: the §4 table (0.22 / 0.44 / 0.66 for a 1.7 m person at 0.5 / 1 / 1.5 m), enfilade 0, lip shooter
  ×0.333, pit cover reads 0, natural water reads 0.
- L2: dry 1 m trench, pawn in it, shooter 10 cells off square-on: `ShotReport` hit chance lower than the same shot at
  the pawn on open ground by about 0.44 × base; shooter along the trench axis: no difference; same with 0.5 m water: same
  as dry.
- L2: a raid against a colony with a 1 m canal line facing it: at least one raider's cast square is a canal square;
  no raider casts from a 1.5 m sheer canal it cannot leave.
- L2: a frag grenade on a pawn in the trench: damage equals the open-ground control (no blast cover).
- L2: CastPositionFinder timing on a 500-dug-square map, on vs off, recorded.
- L1: `grep "LAW 2"` in `src/RimMandrake/FlowWorks` finds no text saying depth never affects cover or shooting.
