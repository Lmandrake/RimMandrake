## spec
found-by: GPT review, verified (BENCH, 2026-10-23, FlowWorks + GSS high-depth review; gpt_consult default model, high effort).
Report: `Transient/flowworks_takeover_20261023/GPT_REVIEW.md` (finding ids FB_hose_gss_3.2). Raw GPT reply: `D:\ClaudeWork\rimmandrake\scratch\gpt_fw_review\raw\<part>.md`.
Severity: MINOR. Not fixed: this item only records the defect.

### verification (FB_hose_gss_3.2)
Verdict: CONFIRMED MINOR. Probe FreshPieces (GimmeSomeSlackProbe.cs:336-345) never sets opt.StraightPlugIds = TapIds(map) as production does (RM_MapComponent_CordGraph.cs:220) -> fresh-build oracle differs at tap clamps

### GPT finding (verbatim)
### FB_hose_gss_3.2 — The fresh-build oracle omits production’s tap-clamp exceptions
- severity: MAJOR
- where: `src/RimMandrake/GimmeSomeSlack/Source/GimmeSomeSlackProbe.cs:336–344` (`FreshPieces`)
- evidence:
  ```csharp
              Dictionary<Cell, Aerial.CellStyle> styled = Aerial.ConduitStylePicker.CellStyles(map);
              opt.PileAt = c => styled.TryGetValue(c, out Aerial.CellStyle cs) ? (cs.Look == "Modern" ? PileArt.Strips : PileArt.Junctions) : (PileArt?)null;
              return b.Build(w, opt, c => CordWorldAdapter.IsLive(map, c));
  ```
- failure scenario: With default `slideUnder=true`, build cords connected to a power-tap clamp and run `fresh`. Production sets `opt.StraightPlugIds = CordWorldAdapter.TapIds(map)`; this supposedly equivalent build leaves the set empty. The oracle slides the clamp connection diagonally while production keeps its square connector approach. Consequently, `fresh` can report missing/extra/different geometry on an unchanged, correct map. `sameframe` also uses this inconsistent reference build. Outside this part, opened `CordWorldAdapter.cs`, `Core/CordBuilder.cs`, and `Core/CordGraph.cs`, confirming that these IDs change plug placement and arrival geometry.
- confidence: high
