# TIBANNA_EMBARGO_PLOT_1 — the Empire's tibanna monopoly as a campaign clock

Source of intent: `design/Jawa/worldbuilding/biomes/the_forge.md` §8 (ratified) —
the garrisoned gas operation metering the herds, the dwindling ammunition, the
resolution the owner ruled must come.

## spec

`design/Jawa/tibanna_embargo_plot_spec.md` (drafted 2026-09-11). Shape: metered vs
unmetered gas as the legality line; enforcement rides the existing pursuit spine;
Heat/Hutt-Interest wiring mirrors `design/Jawa/kyber_trade_plot_spec.md` (same GM
blackboard, same fixer NPC, calibrated register table in §4); an Embargo Clock
scalar carries the "ammunition running out" register through faction texture and
prices, never a UI gauge; seven beats (§6), all text/menu, game whole without the
Oracle; resolution shape is CARD T2, unruled. Harvest mechanics stay with
FORGE_MECHANICS_1; this item owns only the legality layer. Tibanna ≠ propane
(spec §0). Verified defNames: `OuterRim_Tibanna` (read in outerrim.core 1.6 XML),
`RUT_Jawa_HuttCartel`; beldons have no def yet — roster pass owed, do not guess.

## verify

- Shadow-mode blackboard test: black-market purchase moves Heat + Interest per the
  §4 table; metered purchase moves neither; crafting consumption moves nothing.
- Clock advances on calendar, accelerates on player unmetered traffic, fires
  exactly one resolution chain at threshold.
- After every beat: no Rebellion presence on-world, no Force grant, no worldgen
  call, no non-beldon tibanna source, every quest completes with the Oracle absent.
- CARD T1 resolved before any build: the live extractor/mineable tibanna routes
  (outerrim.core siphons/extractors; LK MineablesOR + Mines-2.0 patches) either
  cut, gated, or the ban relaxed — the spec assumes cut.

## criteria

- Spec registered in `design/INDEX.md`; the_forge.md §8's `TIBANNA_EMBARGO_PLOT_1`
  pointer now lands on a real spec.
- Both cards (T1 extractor-route contradiction, T2 resolution shape) reach the
  owner; no build work starts on unruled card material.
- No duplication of kyber-spec machinery: heat detection, fixer ladder, and site
  quest patterns are cited, not restated.

## cards

- **T1** — live mod stack ships non-beldon tibanna routes; the_forge.md §6 ban 5
  forbids them. Cut / gate / relax — owner's call. (Spec, Cards section.)
- **T2** — the ruled "must resolve" needs a shape: break the meter / bleed the
  meter / Empire wins the clock. Spec recommends (a)+(c) as one clock's two ends.
