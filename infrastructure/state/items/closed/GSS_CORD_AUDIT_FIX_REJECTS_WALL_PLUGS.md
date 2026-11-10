## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_2.4). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_2.4)
Verdict: CONFIRMED MINOR. CordAudit requires plug head inside device footprint (CordAudit.cs:161-167) but IntoArt extends a HasHome cord into the wall cell (CordBuilder.cs:699-706) -> false PlugFaults on wall devices

### GPT finding (verbatim)
### FB_hose_gss_2.4 — Art-fit checks reject correctly routed wall-device plugs
- severity: MINOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/Core/CordAudit.cs:161–167` (`ArtFit`); `src/RimMandrake/GimmeSomeSlack/Source/Core/CordBuilder.cs:673,702` (`Home`, `IntoArt`)
- evidence:
  ```csharp
  V2 head = plug.Value.Pos + Dir(plug.Value.Angle) * (PlugFace * plug.Value.Scale);
  bool inside = head.X > m.X0 && head.X < m.X0 + m.W && head.Z > m.Z0 && head.Z < m.Z0 + m.H;
  ```
- failure scenario: A wall-mounted powered device has `HasHome` set to its supporting wall. `IntoArt` deliberately extends its cable and plug under that wall, outside the device’s own footprint. The audit nevertheless requires the plug head to lie inside the device footprint, producing `PlugFaults` for the intended geometry. Offline or live consumers of this audit can therefore fail a correctly drawn wall connection.
- confidence: high
