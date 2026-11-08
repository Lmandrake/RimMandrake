# FlowWorks pits: questions for the owner (Artisan pass 2, 2026-11-07)

## 1. A raid's rescue ladder in a hole that also holds your prisoners (decision)
Built this pass, not yet seen in game: raiders lower a ladder into the pit to fetch a trapped comrade (his story), and a
person the hole traps can be captured from the lip with no bed (his card, "Drained moat is a prison"). The prisoner is
held only because the hole traps him. Ladders need no keys (ladderNoKeys, on by default), so ANY lowered ladder in his
part of the hole lets him climb out: a raid's rescue ladder lowered for one of its own in the same hole frees your
prisoners too.
- A: keep it. Raiders who get a ladder into your prison break it open, and you can shoot the ladder (40 HP) or the rescuer.
  It is a fair, readable story beat.
- B: the rescue refuses a hole that holds colony prisoners; trapped raiders sharing a hole with your prisoners are left
  behind.
My recommendation: A, with one message when a rescue ladder goes into a hole holding your prisoners, so the player sees
the break coming and can act. Until you say otherwise the code does A, silently.

## 2. The aspect split
Nothing seen so far says the split is wrong. One thing to know: the bed-less pit prison (his moat's "prisoners in a
prisoner pit") and wardens working from the lip were built in this aspect, because his pit-trap story ends in "a tidy
prison". The moat's swim and drain stay in aspect 2.
