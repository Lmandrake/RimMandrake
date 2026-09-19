## spec
Discovered during DISTRICT_TEMPLATE_LIBRARY_1's live-verify pass (2026-09-01):
nothing in the codebase binds a `SettlementManifestDef` instance to a
`WorldObject_InhabitedSettlement` instance. The `manifest` field
(`src/RimMandrake/Inhabited/Source/WorldObject_InhabitedSettlement.cs`) is a
bare runtime field, assigned nowhere — not at `PostMake`, not by matching
`settlementName`/tile against `DefDatabase<SettlementManifestDef>`, nowhere.

Consequence: even once the world-authoring pipeline places the real Junkers
"The Claim Jump" `Inhabited_Settlement` WorldObject on the frozen Ash'karr map
(via whatever mechanism `jawa/world_settlements_import`-style authoring uses,
or a future dedicated importer), it will NOT automatically pick up
`Inhabited_Manifest_TheClaimJump` — `GenStep_ComposeSettlementDistrict` will
silently fall back to the placeholder-stub path forever, because
`settlement.manifest` stays null.

Scope: bind a manifest to a settlement WorldObject at the point it is
created for a named settlement — most likely: match
`SettlementManifestDef.settlementName` against the WorldObject's own label/
name at `PostMake` (or lazily on first `Generate()` call, matching however
`WorldObject_Inhabited`'s existing place-lookup already resolves its own
place data — read that pattern first, don't invent a second lookup idiom).
Cover: The Claim Jump (the only manifest that exists today) and the general
case for future settlements/manifests.

## verify
- A `WorldObject_InhabitedSettlement` created and named "The Claim Jump"
  resolves `manifest == Inhabited_Manifest_TheClaimJump` without any bridge
  call setting it directly.
- A settlement named anything with no matching manifest stays `manifest ==
  null` and falls back to the existing stub path — no exception, no crash.

## criteria
The binding is automatic and data-driven (matching by name, not a hardcoded
if/else), and the existing SETTLEMENT_VISIT_LOOP_1/DISTRICT_TEMPLATE_LIBRARY_1
compose paths need no changes — they already read `settlement.manifest`
correctly, they just never receive one today.
