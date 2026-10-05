# belt bridge2 20261005

- started: 3 fails RestrainingBolts enabled_flips, formula_caps_by_bolted_count_and_floors; GravshipLanding reveal_gate_armed
- root causes: static_call args='' binds 0-param (ProofCap/ProofReveal take 1 string) => stale call in validation (fixed args='go'); FDE-absent check stale (UtinniPatches now loaded) => relaxed. enabled_flips and reveal_gate_armed PASS in latest 20261005k summary.
- rerun a: GravshipLanding 10/10 PASS. RB: FDE check read 'error' not 'message' (fixed); bland setup now calls reset() before assert (pawn-gen scars). rerun b launched
- rerun b: RB 9P/1U(FDE absent, legit), GL 10P, bland 5/5. bridge released.
