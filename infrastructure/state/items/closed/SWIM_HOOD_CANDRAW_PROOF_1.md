# SWIM_HOOD_CANDRAW_PROOF_1

## spec

Add public static string ProofHood(string) in src/RimStarWars/JawaRules/Source/Patch_JawaHoodSwimming.cs: find the worn guy762_JawaHood render node on the first swimming hooded Jawa and return swimming=<B> canDraw=<B> (PawnRenderNodeWorker_Apparel_Head.CanDrawNow). JawaRules/validation.py component swim_hood_drawn_live says no tool exposes this. Unblocks JAWA_SWIM_HOOD_KEEP_1.A1.

Filed from the 2026-10-09 acceptance-check pass (Transient/belt_acceptance_checks_20261009.md).

## verify

A state read through `jawa/static_call` on a loaded quicktest map returns the named fields; the owning acceptance criterion records the result.
