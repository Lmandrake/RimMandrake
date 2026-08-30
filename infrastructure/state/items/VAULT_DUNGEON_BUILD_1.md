## spec
Full spec: `design/Jawa/worldbuilding/dungeons_arc_spec.md` §3. Summary:

Six sites, the "breached vaults" `03_deep_history.md` already names as holding
the self-replicating flesh, plus the triad's other two members: **① mechanoid
garrison** (held), **② flesh weapon loose** (breached), **③ frozen Rakata**
(the rare scene). All six sites RULED and independently verified
settlement-free (`vault_siting_prep.md`):

| id | tile | region | type | landmark |
|---|---|---|---|---|
| V1 | 678 | Rust Cathedral core | ① | `AncientGarrison` |
| V2 | 4000 | Scorch (Cathedral halo) | ① outer works | `AncientLaunchSite` |
| V3 | 9167 | Fall Line | ① route-spread | `AncientGarrison` |
| V4 | 17461 | Deadstone | ② | `AncientWarehouse` |
| V5 | 37 | Slough (terminator) | ② | none — needs authoring |
| V6 | 20853 | Umbra (deep nightside) | ③, the one | `AncientWarehouse` |

**Structure** (RULED): one concentric grammar varied per type — outer ring
states the vault's condition at a glance (①=disciplined+powered,
②=torn-open, ③=dark frost-locked) → garrison ring (the fight, or near-silence
for ③) → core payoff. Partial raids viable; the core always costs.

**Payoff ladder** (RULED): ①=Forsaken matter/weapons (never chassis — Arsenal
tech is canonically incompatible with droid parts); ②=survival + the route to
③ knowledge; ③=**wake** (sleepers join, no gratitude, recognize the Utinni as
their colonizer vessel and challenge its possession — canon.yml
`rakata.woken_brutality` — opens a ship-claim thread) / **loot** (kills them,
plainly) / **leave** (the Narrator remembers).

**Technical route**: KCSG (`StructureLayoutDef`) is already vendored
(`VanillaExpandedFramework-main/Source/KCSG/`) and already wired into the
bridge (`jawa/kcsg_place` in `JawaBenchKcsgTools.cs`) — no new C# needed to
place a template. FOUNDRY builds three parameterized templates (type ①/②/③),
proves each on a quicktest, then hand-finishes each of the six real sites with
the owner.

**LARGE maps** (RULED, owner verbatim: "should be LARGE... in terms of X Y
size"): proposed floor 300×300 against the campaign's standard 250×250 —
exact number held for the owner.

**Territorial access**: V1/V2 sit on Cathedral-FDE ground, V3 on the Empire's
Ashgarrison chokepoint — conflict/negotiation for access. Owner flagged a
"territories mod that introduced custom raids in proportion to settlements"
to investigate; **not identified or assessed by this item** — a separate
research task if picked up.

## verify
- [ ] Owner reviews `dungeons_arc_spec.md` §3 and rules the open calls (exact
  LARGE dimensions, the pawn-spawn symbol question in §3.6, whether the
  territories-mod research gets its own item).
- [ ] Three parameterized `StructureLayoutDef` templates (type ①/②/③)
  authored, each including the concentric ring structure.
- [ ] **Quicktest-proven**, per `dungeons_arc_spec.md` §3.7: each template
  placed via `jawa/kcsg_place` on a throwaway quicktest map at the LARGE
  dimensions, judged by LOOKING (`take_screenshot`, read the image) against
  the `rimworld-layout-layers` bar — power/roof sane, no floating/unreachable
  guardians, the core reachable only through the ring, no path that skips the
  garrison ring entirely.
- [ ] Each of the six sites hand-finished with the owner and committed to the
  world (`world_commit`, one bridge driver at a time).
- [ ] Wake/loot/leave dialogue and letters authored for V6; the ship-claim
  thread from waking V6 authored and fires correctly.

## criteria
- [ ] All six vaults readable at a glance by their outer-ring state (a player
  can tell ①/②/③ apart before entering the garrison ring).
- [ ] Type-① core loot is materials/weapons only — no mechanoid chassis ever
  drops.
- [ ] V6's wake branch reads as plainly brutal in dialogue — no gratitude, no
  sympathy softening, the ship-ownership challenge line lands.
- [ ] Partial raids (outer ring only, no core) are genuinely viable on every
  site — the grammar must not force a full clear.
- [ ] Map dimensions measurably exceed the campaign's 250×250 standard
  (`mapSize` read off the game, never off a note).

## Watch out
🔶 **This item is a build SPEC, not creative lock-in.** `FUTURE_VECTORS.md`
names this arc explicitly as "with the owner." Leave `doing` until the owner
has ruled the open calls in `dungeons_arc_spec.md` §3.9.

⛔ **Vaults do NOT get the Assailant dungeon's Anomaly exception**
(canon.yml `anomaly_content` names only the Assailant dungeon and,
tentatively, the sarlacc). Type-② guardians come from the existing
bioweapon-class roster, not the Anomaly toolbox.

🔑 **"Territories mod" is unresolved.** Do not assume a name or assess one
without first identifying it — the owner's note names only its function
("custom raids in proportion to settlements"), not the mod.

⚠️ **V5 has no landmark yet.** Sites V1–V4 and V6 sit on pre-authored
`AncientGarrison`/`AncientLaunchSite`/`AncientWarehouse` landmarks; V5 needs
one authored before it reads as a place rather than bare terrain.
