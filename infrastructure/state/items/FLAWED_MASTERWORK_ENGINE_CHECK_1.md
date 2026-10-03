# FLAWED_MASTERWORK_ENGINE_CHECK_1 — can Ninefold damp Ozzik's knock-on for one call?

The Flawed Masterwork (`design/Jawa/biome_rites_pass_2026-10-01.md` §6.2, ruled-kept by card 2026-10-01) raises Ozzik while drawing less of Sh'kaar's and Zizzik's attention. Question: can `mandrake.rm.ninefold` (`design/Jawa/divine_satiation_engine.md`) apply an Ozzik delta with the cross-god amplifier damped for that one call?

Finding at filing (grep of `src/RimMandrake/Ninefold` on origin/main): no damp, intercession or per-call amplifier hook exists. Only `MoodAmplitude` (per-god random-walk amplitude) and `EventMagnitude` (per-event size) appear, both untuned first-pass encodings. Fallback already named in the pass: a separate small Sh'kaar settlement call.

Done when: either `ApplyDelta` gains a per-call factor (or the fallback is chosen), recorded here.

## resolution (FOUNDRY, 2026-10-03, read of `GameComponent_Ninefold.ApplyDelta` and every `Patch_*.cs`)
`ApplyDelta(god, amount, reason)` moves ONE god's satiation and has no cross-god coupling, so a per-call damp factor has nothing to damp. The "draws Sh'kaar and Zizzik" knock-on in `divine_satiation_engine.md` §3 9(c) is Ozzik's EXALTED BAND acting as a standing bias on their event rolls (§8); no code reads that bias yet (`SatiationBand` only classifies). Chosen: the FALLBACK, with no engine change. The rite calls `ApplyDelta(God.Ozzik, +X)` and a small separate `ApplyDelta(God.Shkaar, -y, "flaw scratched, the crown never quite fits")` settlement call; when the band-bias lands, the rite needs no new hook. Do not add a `damp` parameter to `ApplyDelta`.
