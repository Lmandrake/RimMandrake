# Property — validation walk
subject: src/RimMandrake/Property  (packageId mandrake.rm.property)
deps: none (modDependencies: Ludeon.RimWorld only)
list: minimal
status-hint: decaying-claim ownership fabric — (claimant, strength, basis, timestamp) records per Thing, computed virtually by default, recorded only for the exception list (stolen/purchased/claim-fee-paid/gifted/inherited/looted); no Harmony hooks auto-fire it, pure C# API for other mods to call.

## must be true
- `PropertyEngine.Fire(TakingEvent)` runs act → claim resolution → authorization check → witness/perception roll → lazy faction-record propagation without throwing (`Property/Source/PropertyEngine.cs:20`).
- `PropertyEngine.RecordTransfer`/`RecordLoot`/`RecordGift`/`RecordInheritance` each write the correct `ClaimBasis` — `Purchased`(3)/`Looted`(7)/`Gifted`(5)/`Inherited`(6) — never `Territorial`(0)/`Situational`(1), which are virtual-only and never stored (`Property/Source/ClaimBasis.cs`).
- `ClaimDecay`'s lifetime curve stays within `PropertyTuning.MinClaimLifetimeDays`(3) / `MaxClaimLifetimeDays`(3650) (`Property/Source/PropertyTuning.cs`).
- A claim recorded on a stackable `Thing` logs `Log.Warning` rather than silently corrupting the ledger (`Property/Source/GameComponent_PropertyLedger.cs:78`).
- `ClaimRecord` loaded with `Basis=Situational` (a virtual basis that should never persist) logs `Log.Error` (`Property/Source/ClaimRecord.cs:62`) — proof the exception-list/virtual boundary is enforced on load, not just on write.
- The mod ships zero Defs (no `Defs/` folder on disk) and adds no Harmony patches (About.xml: "No Harmony hooks auto-fire TakingEvents from vanilla actions").

## the walk
1. [L] Player.log after load contains no "Config error in mandrake.rm.property" and no XML error naming Property's About.xml   # load-time; mod ships no Defs so this should be trivially clean
2. [L] `python3 src/RimMandrake/Utils/selftest_property_fabric.py` exits 0 — covers `ClaimDecay.LifetimeTicks()`/`EffectiveStrength()` (pure math), `ClaimantRef.Equals()`/`GetHashCode()`/`OfPawn()`/`OfCommons()`/`IsUnclaimed` (null-safe reference identity), and a byte-for-byte transcription of `ClaimEngine.ResolveClaim`'s private winner-picking sort (strength desc, then specificity desc, then timestamp desc) — see `Property/Source/SelfTest/Program.cs` header for exactly what is and isn't reachable offline
3. [D] a live RimDefDump capture (`DefDump/captures/<id>/manifest.json`) lists zero defs with `modName` "RimMandrake: Property" — confirms the mod stays defs-free as About.xml claims; any hit is a regression
4. [B] `jawa/spawn_thing {defName: "Steel", count: 25}` → success, then `jawa/list_things` confirms the spawned Thing exists on the map — establishes there's a live Thing available for a future bridge-level PropertyEngine exercise once one is wired (none exists yet; PropertyEngine itself has no bridge tool, only SalvageClaim's and TheftHauler's float-menu callers do — see their own walks)
X. [S] (human pass) none — pure back-end ledger with no rendered UI of its own
