A guard written max(1.0, x/1e9) floors the RATIO's denominator at 1 G, not at 1 token: every variant spending under 1G/week had its per-G efficiency understated (Ralph A read 122 sound closes per G instead of 191). Put the floor on the raw quantity (max(1.0, x)/1e9) and give every derived ratio a selftest with a sub-unit denominator.
home: src/RimMandrake/Utils/sim (sim conventions)
