
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §3 "Mechanoid pass" (RULED, owner verbatim quoted there). Two verbs:
- **GRANT** — at VOUCHED+, the Cathedral may extend the Helix-style pass to
  the clan: its machines read pass-holders as non-hostile. Priced like any
  boon against Imperial Heat (offer rides item 4's lane); revocable when the
  relationship cools (stage demotion) or goes dark. Implementation: NEW
  (flag) `RUT_CathedralPass` hediff/flag on clan pawns + a targeting/hostility
  exception for faction-13 Sentinels and Cathedral-controlled mechs toward
  pass-holders — likely one scoped Harmony patch on the hostility check;
  scope it to faction 13 + Cathedral maps, never global.
- **REVOKE (Helix)** — the Helix's own pass is the Cathedral's silent
  tolerance; the reveal (item 7's flag) is what enables stripping it — a
  legible consequence, not a new mechanism: a GM-layer relation flip keyed on
  the reveal flag. Build against the flag name; dormant until item 7 lands.
- **Never**: the pass opens nothing at the antipode war lab — command codes
  sit on the Spire's isolated system (`worldbuilding/ashfall_research_base.md`
  §6). Assert in tests, not just prose.

## verify
Quicktest with hostile faction 13: pass-holder pawns untargeted, non-holders
targeted (spawn many — one pawn is RNG, per memory); REVOKE returns targeting
within the vanilla hysteresis bounds, no manhunt/raid behavior introduced
(arc §8 seed 4); war-lab access unchanged with pass held; grant/revoke driven
purely by blackboard verbs over the bridge.

## criteria
Both verbs callable from the GM layer; Harmony scope reviewed (mark-clean
path); no behavior off Cathedral maps.

**Depends on:** item 1 (stage + verbs), item 4 (offer lane, soft), item 7
(Helix-REVOKE trigger only — GRANT ships without it). **Waited on by:**
nothing. **Seat/needs:** FOUNDRY; C# + Harmony + quicktest (game-up, minimal
list). Row-3 hard — model per `infrastructure/agents/Agent_Policy.md` ladder.
