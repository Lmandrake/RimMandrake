# FlowWorks live proof 2026-10-02

Started Fri Oct  2 07:01:39 PDT 2026

## Steps
- steps 1-2: preflight offline P-O4/5/6 FAIL (pits in FULL.LATEST diff, no golden save sidecar, no backup at that time); backup written deployed/config/ns_flowworks_backup.20261002T070221.json; flowworks tier applied (9 mods)
- step 3: launched via steam, Bridge token at +36s
- step 4: prove_flowworks_pulse: all PASS except 'P2 something moved in 3 pulses' (script design: strip has no water SOURCE cell, F=1 D=1 uniform -> fixed point; tools themselves PASS P1,P3,P4,P5). Step 5: building water-body + 4-direction channel script
- step 5: wrote Transient/flowworks_live_dirs_20261002.py/.out. E,W (len3,6) MATCH oracle; N,S (len3,6) MISMATCH (stall after first unit). investigating
- diag: N/S stall in runs 1-2 = sink band at map edge (columns x=2,4,8; sinkTransferredTotal 94) = harness placement flaw, not engine. Rerunning N/S at x>=20 on fresh body
- step 5 RESULT (clean run, Transient/flowworks_live_dirs3_20261002.out + run1 for W): 4 dirs x len 3,6 all MATCH PulseOracle(fixed): len3 [0,0,1]->[0,1,1]->[1,1,1]; len6 fills in exactly 6 pulses; vectors IDENTICAL across E,N,S (run3) and W (run1, W3/W6 matched). Earlier N/S stalls were sink-band placement (x<10) not engine.
- step 6: see final reply. Game left UP.
