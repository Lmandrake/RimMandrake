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

---

## 🖼️ Three typo'd filenames, repaired by shipping the same bytes at the right name

_Added 2026-08-12 by WORLD._

Three textures in other people's mods are **misnamed**, so the engine looks for a
file that does not exist and the pawn/mech renders its **south** art while facing
north. None of this can ever appear in a log: `Failed to find any textures at`
fires only when **every** direction is missing, and here two of three are fine.

| shipped as | copied verbatim from | in |
|---|---|---|
| `Textures/Things/Pawns/Mechanoid/Astronaut/MechAncient_Astronaut_north.png` | `MechAncient_Astrronaut_north.png` (double R) | Vanilla Gravship Expanded – Ch.1 |
| `Textures/Things/Pawns/Mechanoid/Astronaut/Allegiance_Mech_Astronaut_north.png` | `Allegiance_Mech_Astrronaut_north.png` (double R) | same |
| `Textures/Pawn/CenterFrill/CenterFrill8_north.png` | `CenterFrill8_north-.png` (trailing hyphen) | Vanilla Races Expanded – Saurid |

**Verified, not assumed.** The Astronaut def asks for the *correct* spelling —
`<texPath>Things/Pawns/Mechanoid/Astronaut/MechAncient_Astronaut</texPath>` and
`<maskPath>…/Allegiance_Mech_Astronaut</maskPath>`, `graphicClass Graphic_Multi`,
in `3609835606/1.6/Mods/Biotech/Defs/ThingDefs_RacesMechanoids/Races_Astronaut.xml:79`
— while the file on disk carries the typo. The correctly-spelled `_east` and
`_south` sit in the same folder, which is what proves the intended stem. For the
Saurid frill, `CenterFrill7` has a complete north/east/south set and only `8` is
malformed.

⚠️ **Check `visibleFacing` before ever calling a missing direction a bug.** The
Falleen ridged-spine "bug" was the engine correctly not drawing a South texture
the gene never asked for. These three are different: the def asks, and the art
exists under a name one keystroke off.

**Why this is repair and not origination:** the bytes are copied verbatim, so not
one pixel changes. CREATE declined these for exactly that reason. Placed here
following the `jawaeyes_glow` precedent — this mod already ships a loose texture
override and loads last, so `ContentFinder` resolves each direction independently
and picks these up. **Trivially movable** if the owner would rather they lived in
a dedicated override mod; nothing references them by mod name.
