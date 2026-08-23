## spec
`./game` reported **"bridge silent"** on every call this session while the bridge was up
the whole time. The verdict was conservative and fine; the **wording** was a lie, and the
wording is what every seat reads.

`src/RimMandrake/rimflow/probe.py` — `_bridge_answers()` returns three values:

    True   something accepted a connection on the bridge port
    False  nothing accepted            <- a real negative
    None   GABP_SERVER_PORT is unset   <- THE PROBE NEVER LOOKED

`measure()` collapsed `False` and `None` into one `else` branch and printed
`"%s running, bridge silent"` for both. ⇒ **"I looked and got nothing" and "I never
looked" were spelled identically.** In a plain shell `GABP_SERVER_PORT` is simply not set,
so the None path is the COMMON one — the message almost always meant the thing it did not
say.

⚠️ The function's own docstring said a None *"is harmless: the coarse answer stays
LOADING, which is the conservative one."* True of the **verdict** and false of the
**message**, and it is the message that reaches a person.

## fix
Three branches, three wordings. `None` now names the cause and says the verdict is a
default rather than a reading:

    bridge answers    -> UP       "RimWorldWin64 running, bridge answers"
    bridge refused    -> LOADING  "RimWorldWin64 running, bridge did not answer"
    never probed      -> LOADING  "RimWorldWin64 running; BRIDGE NOT PROBED —
                                   GABP_SERVER_PORT is unset, so LOADING here is a
                                   DEFAULT, not a reading."

## verify
    PYTHONPATH=src/RimMandrake python3 -m rimflow.selftest_probe     -> 14/14
All three branches exercised directly by stubbing `_process_alive` and `_bridge_answers`;
each renders distinct text. Verdicts unchanged — this only stops the instrument spelling
ignorance like a finding.

## criteria
- [x] `None` and `False` produce different text.
- [x] The `None` message names `GABP_SERVER_PORT` as the cause and the remedy.
- [x] No verdict changed; `selftest_probe` still passes 14/14.

## Watch out
🔑 **The verdict was never wrong — only the evidence string was.** Anyone re-deriving this
from the verdict alone will conclude there was no bug. The defect was that a reader could
not tell a measurement from a default, which is the same class as
`measure`'s rule that `0` must mean measured-zero and ignorance must answer `UNMEASURED`.
⛔ Do not "simplify" this back into one branch.
