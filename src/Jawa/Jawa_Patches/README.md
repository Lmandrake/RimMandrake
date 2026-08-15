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
| texture | `RimMandrake_StarWarsRaces/Textures/RimMandrakeSW/Jawa/jawaeyes_glow.png`, 168×168 | the donor art is flat `(255,255,0)` across the whole ellipse, so a `<color>` tint could only ever read as paint |
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

---

## 🖼️ MOVED OUT 2026-08-13 — the three typo'd-filename repairs no longer live here

_Added 2026-08-12 by WORLD, removed 2026-08-13 by CREATE._

This mod used to ship three loose texture overrides repairing misnamed files in
other people's mods. They are **gone from here** and now ship in their own
per-donor fix mods, by the owner's ruling that an art fix belongs in one
independently uploadable mod per donor:

| the file | now shipped by | donor |
|---|---|---|
| `Textures/Things/Pawns/Mechanoid/Astronaut/MechAncient_Astronaut_north.png` | `mandrake.gravshipastronautfix` | Vanilla Gravship Expanded – Ch.1 |
| `Textures/Things/Pawns/Mechanoid/Astronaut/Allegiance_Mech_Astronaut_north.png` | same | same |
| `Textures/Pawn/CenterFrill/CenterFrill8_north.png` | `mandrake.sauridfrillfix` | Vanilla Races Expanded – Saurid |

🔴 **Do not re-add them.** Both mods were enabled in `ModsConfig.xml` while this
mod still carried its own copies, and **`mandrake.jawa.patches` sits below both**
in the load order — so this mod's copy was winning, and the fix mods were
inert. Two loose files at one texture path are resolved by **load order, not by
intent**, and a texture that loses to another texture produces **no log line at
all**. The README's old closing line said these were "trivially movable if the
owner would rather they lived in a dedicated override mod". The owner did.

The reasoning that justified the repair is unchanged and now lives in each fix
mod's own `About.xml`: the def asks for the correct spelling, the correctly
spelled `_east` and `_south` sit beside the typo'd `_north`, and the bytes are
copied verbatim so not one pixel changes.

⚠️ **The surviving lesson, which is not about these files:** check `visibleFacing`
before ever calling a missing direction a bug. The Falleen ridged-spine "bug" was
the engine correctly declining to draw a South texture the gene never asked for.
