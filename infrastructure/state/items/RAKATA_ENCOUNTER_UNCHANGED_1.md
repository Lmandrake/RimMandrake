## spec

**The half of `RAKATA_SLEEPERS_LOOK_RIGHT_1` a pawn spawn cannot answer.** Its appearance
clauses all passed on 2026-08-23 — six ancient kinds carry `RimMandrakeRakata 1.0`, a
spawned `AncientSoldier` renders with the `RimMandrake_Rakatan` skull, the inspect pane
reads **"Forsaken soldier"** and the xenotype reads **"Rakata"**, exonym and endonym both
right and correctly different.

🔴 **What is NOT proven is that the ENCOUNTER plays exactly as before.** That item is
explicit: *"same spawn count, same gear, same difficulty. This is an appearance change and
nothing else; report any behavioural difference as a defect."*

⚠️ **A direct `jawa/spawn_pawn` cannot test it.** Forcing one pawn into existence bypasses
the ancient-complex generation that decides how many arrive, with what, and at what
threat. What has to be observed is a real cryptosleep casket cracked in a real ancient
structure.

### The Avaloi clause, carried over intact

`det.avaloi` injects `DV_Avaloi` into the `Ancients` and `AncientsHostile` faction sets at
**0.15 / 0.10**, so roughly one sleeper in ten used to come out Avaloi rather than human.
🔑 With the six kinds now forcing `RimMandrakeRakata` at **1.0** and `useFactionXenotypes
false`, that injection should be overridden — **but nobody has watched a casket to see
which wins.** If an Avaloi still appears, the forcing is not absolute and the appearance
change is incomplete.

## verify

- An ancient complex is entered and a casket cracked: the sleeper is Rakatan, not human
  and not Avaloi.
- Spawn count, gear and threat read the same as the pre-change baseline — or the
  difference is named.
- Across ~10 sleepers, zero Avaloi.

## criteria

Nobody can say the Rakata change altered how the ancients FIGHT, and the Avaloi question
has an answer instead of a caveat.
