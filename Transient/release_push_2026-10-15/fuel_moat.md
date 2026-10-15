# Fuel moat — CHEMFUEL_MOAT_WIRE_MISSING_CHANNEL (BENCH, 2026-10-15)

Owner, by card 2026-10-15: "Connect it today and make it tremendous. ... a moat of gasoline ... Then there's
astrofuel. That should simply be a massive explosion ... In Utinni such a thing should instantly summon raids ..."

| step | state | sha | notes |
|---|---|---|---|
| 1 chemfuel/astrofuel fill channels (canalFluid) | done | (this commit) | registry row via generator; astrofuel adoption patch. Tank->pump/hose->channel was already generic (Building_LiquidPump, RM_LiquidSpill read canalFluid). Propane has no canal FluidDef: out of scope. |
| 2 chemfuel inferno (fast front, big flames, heat, ignite radius, fast burn-down, settings) | todo | | |
| 3 astrofuel chained detonation (budgeted per tick, all consumed, settings) | todo | | |
| 4 Utinni hook (raid on blast; heat only if a heat system exists) | todo | | |
| review-map stations + functional script rows | todo | | |
| DLL build + selftests + reviews | todo | | |

## Perf numbers

(pending)

## Live proof commands

(pending)

## Filed

(pending)
