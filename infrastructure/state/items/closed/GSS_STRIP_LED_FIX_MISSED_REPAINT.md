## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_3.1). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_3.1)
Verdict: CONFIRMED MINOR. Section Sig (RM_MapComponent_CordGraph.cs:322-326) holds geometry/seed/material but no live/dark-strip state; a rebuild that consumes a power change (LiveNow 328-332) need not repaint the LEDs

### GPT finding (verbatim)
### FB_hose_gss_3.1 — Rebuilding can consume a power-state change without repainting strip LEDs
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/RM_MapComponent_CordGraph.cs:322–335` (`Sig`, `LiveNow`)
- evidence:
  ```csharp
  liveEnds[c] = v;
                  ? string.Join("\n", l.Select(p => p.Key + "@" + p.GeometryHash() + "#" + (seeds.TryGetValue(p, out int v) ? v : 0) +
                                                    "%" + (mats.TryGetValue(p, out int g) ? g : -1)))
  ```
- failure scenario: An already printed Modern tangle loses power. Before the next 250-tick poll, construction elsewhere triggers a rebuild. Building the new tangle updates `liveEnds` and creates dark-strip decals, but its signature contains no decal state, so its owning section need not repaint. The subsequent poll sees the already updated live value and detects no flip. The player can therefore keep seeing lit strips on a dead net until another event dirties that section. Outside this part, opened `Source/Core/CordBuilder.cs`: `TanglePiece` uses a fixed key, reads `isLive`, and changes connector decals; `GeometryHash` hashes only strand coordinates.
- confidence: high
