# MIASMA_KARRATHIL_POLLINATION_GATE_1

## what

Gate the Miasma's flowering mangals' reproduction on `RUT_Karrathil` (the
fever-swarm) presence — the second half of
`design/Jawa/worldbuilding/biomes/the_miasma.md` §4's "disease vector and
the mangals' only pollinator, one and the same swarm. You cannot have the
trees without the fever," and `design/Jawa/worldbuilding/biomes/
miasma_fauna_roster_2026-09-23.md` §3's own row for `RM_Karrathil` (built
this pass as `RUT_Karrathil`, `COMMISSION_LEDGER_CLEANUP_1`, ledger slug
`the_miasma:karr-fever-swarm-vector-pollinator-one-swarm`).

## why

The roster's own §3 caution: *"whether a `Plant` can be gated on a nearby
animal at all is an engine question, UNMEASURABLE on the Mac... check it on
the Desktop before this row's mechanics are specified."* This item exists
so that check — and whatever mechanism it enables — has a home separate
from the creature build, rather than being guessed at inline.

`COMMISSION_LEDGER_CLEANUP_1`'s wave that built `RUT_Karrathil` (this
session) shipped the creature (flying insect swarm, `wildGroupSize` 12~30,
wired into `RUT_Miasma.xml`) and the VECTOR half needs no new mechanism —
`miasma_kit_spec.md` M4 already routes the biome's diseases through
vanilla's own `diseaseMtbDays`/`<diseases>` list, no bespoke bite/contact
comp. Only the POLLINATION half — a plant's reproduction failing without a
nearby animal — is new engine territory, and it is what this item covers.

Checked this session (not a Mac laptop; `mcp__rimsage__*` tools DID
connect and answer from this environment): a source search for
`pollinat`/`Plant` reproduction found **no existing engine hook** to gate
plant spread on nearby animal presence. This confirms the roster's
"UNMEASURABLE" flag is about genuine absence of a ready mechanism, not
merely about tool access — the Desktop check this item still needs is
about whether such a gate is *buildable at all* (does `Plant`'s spread/
growth path expose anything a comp could veto?), not about reaching a
tool.

## watch out

- ⚠️ **Do not add a second pollinator or make killing karrathil strictly
  good** — both are the "obvious balance fix" the roster explicitly warns
  against (§7): *"If killing karrathil is strictly good, the bargain
  collapses."* The gate has to be able to FAIL flowering, not just tax it.
- ⛔ Do not invent a plant-reproduction mechanism by guessing at engine
  behavior from a doc — CLAUDE.md's own standing rule on UNMEASURABLE
  engine facts. Verify on the Desktop (RimSage or a live dev-mode test)
  before writing any comp.
- Which flowering plant(s) this gates (the mangals — `AB_MangroveTree`/
  `AB_ParasiticMangrove`, `RUT_Miasma.xml` wildPlants) is a content
  decision for whoever picks this up; not pre-judged here.

## verify

- Confirm (Desktop) whether `Plant`'s growth/reproduction path can be
  vetoed or slowed by a comp reading nearby-pawn presence.
- If yes: build the gate, wire it to `RUT_Karrathil`, and re-verify the
  mangals still reproduce normally with karrathil present and measurably
  worse (not zero) without it.
- If no: record why here and close or retarget this item rather than
  leaving it open indefinitely.

## criteria

Closed when either (a) the pollination gate ships and is verified against
a live game, or (b) the Desktop check finds no buildable mechanism and
this item is closed/retargeted with that finding recorded.
