# PYRELANDS_LIGHTNING_BREAKER_BUILD_1

Spec: `design/Jawa/worldbuilding/biomes/pyrelands_bedazzle_review_2026-10-01.md` §5. Owner, typed: *"The Lightning breakers is a neat idea. They should be made of metal and sand in a recipe in the forge. Only learnable here because of the frequent lightning and sandy soil. Desert sand works just fine too once you know how"*. Free `RM_` tier.

1. **Building:** a lightning breaker on a power line. When a short circuit strikes the grid, the breaker trips, isolating the fault so the rest of the grid stays live; tripping spends it (or a charge). Visible tripped state, a crack sound, a message naming the protected and lost sections. **UNMEASURED:** the vanilla short-circuit entry point; read it in RimSage before writing the patch.
2. **Recipe:** metal and sand at the smithy (the forge). Sand is `RM_GlassSand` (Stillsand mod, same unified biomes mod): add it as the clear/shovel yield of the Pyrelands' `RM_FE_Ground_Sand` terrain; desert drift sand is the same item.
3. **Learning gate:** a research project learnable only on a Pyrelands map (e.g. unlocked by studying `RM_FE_Fulgurite` where it fell, or a techprint dropped only there). Once known, the breaker is buildable on every map and desert sand works.
4. **Mod Settings:** on/off; the Pyrelands-only gate (default on); recipe cost; trip cost.

Powerful by design (owner: powerful tech is good); balanced by cost and the gate, never by narrowing it. Art: the breaker building (art list job `RM_LightningBreaker`); lightning glass already has art.

🔴 **North-star re-measure:** `PYRELANDS_NORTHSTAR_TRIAL_1` must re-measure after row 0 (the animal move) lands: it changes the cast the trial's census reads. Sequence with `PYRELANDS_SHIP_READINESS_1`.

## verify
- Research cannot start off-Pyrelands until learned there; afterwards the recipe works anywhere with desert sand.
- Forced short circuit on a two-section grid: the breaker trips, the protected section stays powered, the sign is readable.
