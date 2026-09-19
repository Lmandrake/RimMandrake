
## Findings (BENCH recon, 2026-09-14)

**Technique (both BioReactor and vanilla Biotech growth vats):** composite the LIVE pawn, not a portrait — re-enter the pawn's own renderer at an offset draw location, then draw the glass/liquid layer above it by altitude:
- Vanilla `RimWorld.Building_GrowthVat`: `DynamicDrawPhaseAt(...)` calls `selectedPawn.Drawer.renderer.DynamicDrawPhaseAt(phase, drawLoc + PawnDrawOffset, null, neverAimWeapon: true)`; the lid/glass `TopGraphic.Draw(...)` renders at `DrawPos + Altitudes.AltIncVect * 2f`.
- BioReactor `Building_BioReactor.drawInnerThing`: forces `pawn.Rotation = Rot4.South`, calls `pawn.Drawer.renderer.RenderPawnAt(rootLoc, Rot4.South)` (floating, facing camera); `LiquidDraw(Color, fillPct)` tints toward cyan `Color32(123,255,233,75)`; reusable `CompSecondLayer : ThingComp` draws the glass/status overlay.

**Sources:**
| mod | id/repo | license | 1.6 |
|---|---|---|---|
| BioReactor (Continued) | github.com/emipa606/BioReactor (Steam 3307031939) | MIT | yes, updated 2025-08 |
| BioReactor (original, NukaFrog) | Steam 1564657272 | no repo found — treat all-rights-reserved | 1.0–1.4 only |
| Vanilla growth vat | Building_GrowthVat (Biotech) | Ludeon proprietary (write own by observed behavior) | native |

**Recommendation:** vanilla growth-vat pattern written fresh (low effort, high fidelity, no license risk); or copy `CompSecondLayer.cs` + `LiquidDraw` from the MIT Continued fork for the liquid-fill system. Avoid portrait/RenderTexture compositing (static-icon look). VNPE renders no pawns (irrelevant). UNKNOWN: whether Alpha Genes ships its own vat renderer.
