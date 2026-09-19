## spec
Filed 2026-08-29T01:18Z claiming `jawa/incident_schedule` sits OUTSIDE
`#if JAWA_GM_TOOLS` in `JawaBenchSimTools.cs`, contradicting the file's own
doctrine ("everything that WRITES to the live colony sits behind
`#if JAWA_GM_TOOLS`") — found while fixing the gate guard's false positive.
Asked to audit the rest of SimTools' storyteller section for other un-gated
actors and wrap them.

## finding — already fixed, audit confirms doctrine holds
Read the file fresh (not grepped blind): exactly one `#if JAWA_GM_TOOLS` /
`#endif` pair, lines 222-839. `IncidentSchedule` (`jawa/incident_schedule`,
line 384-395) is INSIDE it. This matches
`f35ab2bb "Companion deployed (--gm, game down); gate guard false positive
fixed"`, a concurrent BENCH commit landed in this same shared checkout between
this item being filed and being picked up here — the fix this item asked for
already happened.

Full audit of the rest of the file's `[Tool(` entries (12 total): only two sit
outside the gate, `jawa/cell_temperature` (line 90) and
`jawa/incident_parms_preview` (line 149) — both read `MainThread.InvokeAsync`
bodies checked line-by-line, and both are genuine pure reads
(`GenTemperature.TryGetTemperatureForCell`, `StorytellerUtility.DefaultParmsNow`
/ `DefaultThreatPointsNow`) that fire, queue or write nothing. No `[Tool(`
entries exist after the `#endif` at line 839. The doctrine the file's own
header states ("Only the two pure reads... are always compiled in") is
currently TRUE of the file as it stands, verified rather than assumed.

## verify
    grep -n '^#if\|^#endif' JawaBenchSimTools.cs        -> 222, 839 (one pair)
    grep -n '\[Tool(' JawaBenchSimTools.cs               -> 12 tools, only
                                                             lines 90 and 149 outside
                                                             222-839, both confirmed
                                                             pure reads by reading their bodies

## criteria
- [x] `jawa/incident_schedule` confirmed inside the gate (already fixed elsewhere).
- [x] Every other SimTools storyteller-section tool audited; no un-gated writer found.
- [x] Nothing further to wrap — closing as already-resolved-and-verified, not re-fixing
      what a concurrent commit already fixed.
