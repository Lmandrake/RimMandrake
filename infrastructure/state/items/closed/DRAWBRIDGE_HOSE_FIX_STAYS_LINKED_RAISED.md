## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FA_core_sim_1.3, FB_hose_gss_1.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MAJOR. Not fixed: this item only records the defect.

### verification (FA_core_sim_1.3)
Verdict: CONFIRMED MAJOR. HoseEnds.Read returns Kind=None/Port=null when RM_Drawbridges.HoseCut (HoseEnds.cs:46); RM_HoseLinks.Ends treats Port==null as free end and builds a port at r.far for Intake/Outflow roles (LiquidNet.cs:1039-1044)

### GPT finding (verbatim)
### FA_core_sim_1.3 — Raised drawbridges do not disconnect hoses with Intake or Outflow roles
- severity: MAJOR
- where: `src/RimMandrake/FlowWorks/Source/Machinery/RM_LiquidNet.cs`:1032–1045 (`RM_HoseLinks.Ends`)
- evidence:
  ```csharp
  else if (e.Port == null)
  ```
  ```csharp
  far = new RM_NetPort { Reel = r, Cell = r.far, Role = role };
  ```
- failure scenario: Lay an Intake or Outflow hose across a drawbridge and raise its leaf. The hose-end reader correctly returns `Kind=None` and an invalid cell, but this fallback treats its null `Port` as an ordinary free end and recreates a hydraulic port at `r.far`. Pumping, dumping, or levelling can continue while the inspect line reports disconnection. Outside this part, I opened `Source/Hose/HoseEnds.cs`, `Source/Hose/RM_MapComponent_Hoses.cs`, and `Source/Pits/Drawbridge/RM_Drawbridges.cs`; raising the leaf invalidates end caches, and `HoseEnds.Read` returns the disconnected result.
- confidence: high

### verification (FB_hose_gss_1.4)
Verdict: CONFIRMED MAJOR. MERGE with FA_core_sim_1.3: RM_LiquidNet hose link takes comp.FeedsInto(r) relay (RM_LiquidNet.cs:1027) before any HoseCut check, only HoseEnds.Read checks it (HoseEnds.cs:46) -> raised leaf still relays

### GPT finding (verbatim)
### FB_hose_gss_1.4 — Raised drawbridges do not reliably disconnect hydraulic hose links
- severity: MAJOR
- where: src/RimMandrake/FlowWorks/Source/Hose/HoseEnds.cs:41–50 (`Read`); src/RimMandrake/FlowWorks/Source/Hose/RM_MapComponent_Hoses.cs:445–449 (`FeedsInto`)
- evidence:
  ```csharp
  if (Pits.RM_Drawbridges.HoseCut(r)) return e;
  return i < 0 || idx.OnLoop(i) ? null : At(idx.Next(i));
  ```
- failure scenario: Raise a leaf crossed by a hose feeding another reel. `HoseEnds.Read` reports no end, but `FeedsInto` still returns the relay, so the network can keep transferring across the raised bridge. For an Intake/Outflow hose, the empty end result can instead be reconstructed as an active free-end port. Confirmed in `Source/Machinery/RM_LiquidNet.cs:981–1050`—outside this part, opened—that eligibility does not check `HoseCut`, relay resolution precedes the free-end read, and a null port becomes a role-based endpoint without checking `Kind`. Thus invalidating the end cache does not ensure immediate hydraulic disconnection.
- confidence: high
