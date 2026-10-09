
<!-- Split from the 2026-09-12 build decomposition; standing constraints: arc spec section 'The law' (knowledge gate, bans 1/2/3/6, rationed patience, Oracle laws, no Force, no worldgen) bind this item. -->


## spec
Arc §3 "Mechanoid pass" (RULED, owner verbatim quoted there). Scope RULED
(owner card, 2026-09-13, via CATHEDRAL_ARC_OPEN_CARDS_1): the NARROWEST
reading — faction-13 Sentinels + Cathedral-controlled machines, Cathedral
ground only; other mechanoid factions are NOT covered, and the pass does
nothing off Cathedral maps. No longer an assumption. Two verbs:
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

### Exact checks 2026-10-09 (acceptance sitting)
- A1 CHECK: `jawa/get_defs defs="HediffDef/RUT_CathedralPass;BiomeDef/RM_RustCathedral;BiomeDef/RUT_RustCathedral" fields="defName"`. Patch armed: `jawa/harmony_patches typeName="GenHostility" methodName="HostileTo"` lists a postfix whose owner is `mandrake.rut.cathedralpass` (Patch_CathedralPassHostility.cs; applied by PatchApplier tag `RimMandrake.Utinni.CathedralPass`). Setting: `jawa/mod_settings_field typeName="RimMandrake.Utinni.CathedralPass.CathedralPassSettings" action=get field="cathedralPassEnabled"`. Log: `[RimMandrake.Utinni.CathedralPass] Harmony: patched N, missing 0`. PASS: success=true, foundCount=3, notFound empty; harmony_patches shows the postfix; census line with missing 0; cathedralPassEnabled reads true. FAIL: success=false (UNMEASURED, not absent), notFound non-empty, or foundCount short, no postfix on HostileTo (silent non-arm), or the census line shows missing>=1 or `Harmony patch failed`.

## criteria
Both verbs callable from the GM layer; Harmony scope reviewed (mark-clean
path); no behavior off Cathedral maps.

**Depends on:** item 1 (stage + verbs), item 4 (offer lane, soft), item 7
(Helix-REVOKE trigger only — GRANT ships without it). **Waited on by:**
nothing. **Seat/needs:** FOUNDRY; C# + Harmony + quicktest (game-up, minimal
list). Row-3 hard — model per `infrastructure/agents/Agent_Policy.md` ladder.

## build 2026-10-06 (FOUNDRY, offline, uncommitted at time of writing)
GRANT flag + scoped hostility exception built as a new mod, `src/RimUtinni/CathedralPass/`
(`mandrake.rut.cathedralpass`): `RUT_CathedralPass` HediffDef; `CathedralPass.Grant/Revoke/GrantToClan/RevokeFromAll`
(the API the GM verbs will call); one Harmony postfix on `GenHostility.HostileTo(Thing, Thing)` — faction-13
(`Faction.OfMechanoids`) vs a player pawn holding the flag, both on an `RM_RustCathedral`/`RUT_RustCathedral` map,
forced-hostile mental states still win; one Mod Settings kill switch; dev-mode debug actions standing in for the verbs.
Built clean via winbuild. NOT built: the GM-layer GRANT/REVOKE verbs and the Helix REVOKE (blocked on
CATHEDRAL_REGARD_BLACKBOARD_1 / item 7). NOT proven: the whole `## verify` bar (live quicktest).
