# Jawa Patches (local) — `mandrake.jawa.patches`

Campaign patch mod for the Jawa gravship playthrough. Loads **last**, so it can
patch defs every other mod has already contributed.

---

## ❄️ FROZEN 2026-08-11 — the Jawa eye glow is settled, do not retune casually

Four in-game iterations to get here. The final values are the answer to specific
observed failures, so changing one in isolation will probably reintroduce one of
them.

| setting | value | why this and not something else |
|---|---|---|
| texture | `Textures/JawaEyes/jawaeyes_glow.png`, 168×168 | the donor art is flat `(255,255,0)` across the whole ellipse, so a `<color>` tint could only ever read as paint |
| eye radius | 38 × 29 px | larger merged with the neighbouring eye into one orange bar |
| halo | 1.10× radius | at 1.75× the bloom was 43% of the texture and the pair read as "a mass of broad orange light, not eyes" |
| rim | solid opaque black, full width | a soft rim let adjacent eyes bleed together; the hard rim is what makes them read as two |
| `drawSize` | **0.16** | judged "50% too large" at 0.24. Apparent size is now 37% *smaller* than the donor |
| shader | **`MoteGlow`** on all three genes | see below |

**Why `MoteGlow` and nothing else.** A night screenshot at Dark 0% split the
pawns 9 glowing / 6 black, matching the save exactly: 7 `MoteGlowPulse` +
2 `MoteGlow` visible, 6 `MoteGlowPulseLow` invisible. **`MoteGlowPulseLow` does
not render usefully on a pawn render node.** `MoteGlowPulse` renders but its
pulse was reported as imperceptible — it is driven by global time, so every pawn
pulses in phase, and there is no XML knob for a per-pawn offset or a floor under
the trough. Doing pulse or blink properly needs a C# `PawnRenderNodeWorker`; it
is not a shader swap. Steady is also the canon read: two unblinking lights under
a hood.

⚠️ **`shaderTypeDef` is real but invisible to a def dump.** It exists on
`Verse.PawnRenderNodeProperties` (confirmed in IL) and is simply null by default,
so a live dump omits it. Do not conclude from a dump that gene render nodes
cannot take a shader — that nearly cost this feature.

**All of this only works because Jawa are excluded from Facial Animation.** FA
deletes the vanilla head draw call and paints its own face. The LFS eyes mod
proves the consequence: its FA-compat patch does `PatchOperationRemove` on
`renderNodeProperties` for every one of its own eye genes. A gene can only draw
its own eyes on a pawn FA is not drawing.
