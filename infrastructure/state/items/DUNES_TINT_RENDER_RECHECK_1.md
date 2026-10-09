NEW mechanism never observed: the Map/Transparent tint fallback in SectionLayer_DuneSand has never rendered.

Re-check of DUNES_TINT_GATE_PROOF_1.A1 after the fix. The A1 failure stands: MatBases.Sand (Misc/Sand, Custom/Snow) has no _Color, so the shipped MaterialColor tint painted nothing. Fix: SectionLayer_DuneSand now, for a non-white tint on a shader without _Color, draws a Map/Transparent clone of the sand texture carrying the tint (src/RimMandrake/MovingDunes/Source/SectionLayer_DuneSand.cs MaterialFor, tintFallback). White tint keeps the vanilla material and pollution mask.

## criteria
- [ ] A1: With a dune material tint of (0.6,0.4,0.3) and tintMode MaterialColor on a skinned map, SectionLayer_DuneSand uses a material whose shader is Map/Transparent and whose colour equals the tint (a state read), and sand cells draw tinted rather than vanilla.
- [ ] A2: With tint (1,1,1) the layer still uses the vanilla Misc/Sand clone (no behaviour change).

## verify
Needs the bridge and a quicktest map with Odyssey. Add a read-only probe to RM_DunesProof (e.g. ProofTintLayer: build MaterialFor with a temp tint def and report shader name + colour) via the rimbridge-companion pattern, `jawa/static_call` it; A2 by calling with white. A screenshot of tinted sand is optional corroboration only. UNMEASURED: no map with Odyssey active, or the probe not yet written.
