## spec
🔴 **`9078a15` rewrote the `modlist_sha` of an ALREADY-FROZEN registry entry, in place.**
`OFFICIAL-2026-08-21` went from `e0f11692cf69e516` to `5ef6eec3daf6c325` with its
`capturedUtc` unchanged.

**The stated reason is not correct.** The commit body and `refresh.py:417`'s docstring both
say the old value *"reproduces from NOTHING on this machine — not the dump's own mod set
(`5ef6eec3daf6c325`), not the live load set (`49b83562b10df31c`)"*.

⚠️ **It reproduced.** DECIDE recomputed `e0f11692cf69e516` from the then-current
`manifest.json` at 13:0x on 2026-08-21 — sha256 over the sorted, lowercased
`mods[].packageid` set, first 16 hex — and it matched the recorded value exactly. Two
independent routes to one number. That measurement is recorded in `c330690`.
🔑 **So "I could not reproduce it" was reported as "it reproduces from nothing."** That is
the same error class already in `BUILDABLE.md` — a tool that cannot find something reporting
absence as fact. Whoever first froze the entry evidently used that algorithm; checking two
other algorithms cannot rule it out.

⛔ **The defect is the in-place rewrite, and it stands regardless of which algorithm is
better.** `dump_fingerprint`'s value may well be the better fingerprint — it is now what
canon points at, deliberately. But **a freeze whose recorded fingerprint can be edited is not
a freeze.** After this change, anyone recomputing the old way gets `e0f1…`, reads a mismatch
against `5ef6…`, and concludes the *capture* changed when only the *algorithm* did. That is
strictly worse than either number alone.
⚠️ **And it is now unfalsifiable from disk:** the 08:20 capture has been replaced by the
22:44 one, so the original manifest no longer exists to recompute either value against.

**Do, in this order:**
1. **Never rewrite a frozen entry's recorded values.** If an algorithm changes, append a new
   field (`modlist_sha_v2`, with the tool and version that produced it) or a new entry, and
   leave the original readable. Enforce it: `refresh.py` should refuse to modify an existing
   `frozen: true` line at all.
2. **Correct `refresh.py:417`'s docstring**, which teaches the false claim to every future
   reader.
3. Record the superseded value in the entry rather than deleting it, the way `canon.yml`
   records `superseded:`.

## verify
`selftest_frozen_dumps.py` gains a case: any write path that would alter an existing
`frozen: true` entry raises instead. Grep of `refresh.py` finds no remaining assertion that
`e0f11692cf69e516` reproduces from nothing.

## criteria
Offline; no game needed.

## notes
⚠️ **Not an accusation of carelessness, and it should not be worked as one.** Folding two
freeze commands into one was right, and demanding that every frozen number be reproducible is
right — that instinct is what canon now depends on. The error is narrow: an unreproduced value
was called unreproducible, and a frozen record was edited on that basis.
🔑 DECIDE's own canon entry carried the same `e0f1…` claim and has been corrected in the same
pass — canon now names the TOOL rather than any hand recipe, so no third algorithm can appear.
