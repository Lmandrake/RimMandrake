## Verdict: ready for parent inspection, with limits listed below

**Scope.** I checked that the fix targets the reported defect: the missing depth check in `HosePorts.RawFind`. It does not touch the relay intake path via `comp.IsFed` (`RM_LiquidNet.cs:1166`). That path still bypasses `Port()` and stays an explicit, disclosed limit. `RawFindAt` (free ends) is unchanged apart from line shifts. `EndReaches` still requires equal bands, and no ramp/ladder endpoint permission was added (design P5).

### Bullet 1: depth at actual contact — met
- **Clamp, all sides:** `HosePorts.cs:132-134` pairs each outside perimeter cell with the reel's touching edge cell. `PerimeterInto` (`HoseMath.cs:2833`) never yields corner cells, so this is exactly `contact - side` on every side.
- **Multiple contacts and fallback:** passing the reachable set into `Pick` (`HoseMath.cs:2918`) filters contacts before ranking. A later valid cell of the same neighbour can still win, and an invalid preferred pipe falls back to the next candidate. Kind/side/edge/id ranking is otherwise unchanged, and callers without the set behave as before.
- **Pumps:** `HosePorts.cs:145-157` limits a pump candidate to the pump cell behind its designated port (`PortCell(...) - d`, using the real `Position`). It keeps the overlap rejection, and `Find`'s `PumpSideTakes` id gate is untouched. A competing reel's body is now depth-checked too, which is the correct consequence.
- **Live (deployed DLL):** a 2x2 reel and tank couple at (40,36). The same tank moves to its other contact (40,37) when the first cell is dug, and is refused when both are dug. Turning the rules off restores the legacy coupling. Fallback goes to the west pipe. `Find` equals forced `Port` in all six rows (`live_attempt1.json:7651-7790`).

### Bullet 2: checks, suite and build — met, with one significant limit
- **Original reproduces:** the staged originals (`HosePorts` bb8a…, `HoseMath` dd6e…) contain no reachable filter. `fast_original_expanded` fails 17/43, exactly the depth/contact/fallback/pump cases.
- **Final and mutant:** final passes 47/47. The mutant differs only at the `Pick` call (`fast_unfiltered_mutant/inputs/.../HosePorts.cs:163`) and fails exactly the later-valid-contact case.
- **Real code:** the probe compiles the actual production files. The stubs (`AdapterStubs.cs`) only stand in for the engine boundary.
- **Replaced fixture:** the retired pump fixture placed two reel bodies on overlapping cells, which can't exist in a real game. With overlapping bodies the shared cell had depth 8 for both reels, so the old expectation relied on the now-forbidden other-lane coupling. Replacing it with free-end reservation cases (laid / unlaid / wrong lane) is legitimate.
- **Suite:** PASS 1/1. Main 1244/1244, plus the 4 new `ReelBodyInlet_*` cases, hose 188/188 checks and 457/457 assertions. Source hashes match between before, after and the suite receipt (`HosePorts` 75544c…, `HoseMath` ed5978…).
- **Build:** 0 warnings / 0 errors; 352 stamped compile inputs match.
- **Significant limit:** the permanent selftest (`HoseBodyInletChecks.cs`) only tests `Pick`'s filtering. The depth check inside `RawFind` and the pump port-lane limit are guarded only by the evidence-retained adapter (`fast_probe.py`), not by a registered suite entry. Reverting `RawFind` would still pass the normal suite. The file header discloses this, but the parent should weigh it against "reject its return".

### Bullet 3: live acceptance and GSS — met
- **DLL identity:** sha bb4849… is the same in the build, publication (88b81f3…), the deployed copy and the identity the game reported live.
- **Scene and restore:** ran on a disposable save of the calm test site with real dry depth-4 digs, no failed or displaced operations. The driver's `finally` reloaded the begin save; the rectangle fingerprint matches before and after (275a5b…) and the rules setting is restored to True.
- **Canonical saves:** both hashes match before and after (`live_inputs_before.json` vs `final_checks.json` `canonical_unchanged`).
- **Final state:** `game_final.txt` DOWN / NOT RUNNING; `bridge_final.txt` bridge FREE and driver lock FREE.
- **GSS:** preserved by 502 unchanged file hashes plus the GSS DLL match; there is no new art claim.

### Other limits (no blocker found)
1. **Contact moves for some valid pump couplings.** For a same-band reel beside a multi-cell pump whose port lane isn't the lowest edge lane (e.g. a station with `Position`=(minX+1, minZ+1)), the reported contact, and so the drawn feed coupling, moves to the designated port lane. That follows the owner's one-port rule but strictly goes beyond "ranking fixed except unreachable contacts". It isn't verified live and isn't called out as a visible change in FINDINGS.
2. **Live coverage gaps:** no pump/machine case and no case with both reel and neighbour on a nonzero band; those are adapter-only.
3. **Disclosed qualifications:**
   - Forced `Port` reads only: no 60-tick cache convergence or fluid transfer.
   - The `IsFed` relay path is untouched.
   - The settings-screen selftest that arrived during publication was not retested.
   - The cache refused admission.
   - The HugeThings dependency catch-up makes no acceptance claim.

would show: yes