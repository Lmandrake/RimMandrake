# GRAVSHIP_SHRINE_FOLLOWUPS_1 — held decisions and remaining passes from the 2026-08-28 shrine round

BENCH + owner built these live on 2026-08-28 (session start ~00:00 local; save
`gravship_scratch` predates all of it). Everything below is EITHER a held owner
decision (needs `owner`) or a bridge pass any seat can run once the bridge frees.

## What already exists (context, verified by read-back and screenshot)

- Engine room: 23×23 octagon x116–138 / z139–161, door S at (127,139), corridor
  N gap x126–128 at z161. Shrine: 6 Brazier (aisle x125/x129 at z141/144/147),
  6 AncientLamp ring, 2 AncientSystemRack (122/132,158),
  2 AncientTerminal (124/130,159). Substructure verified under all 422 cells.
- Computer-core vault x119–125 / z168–174 ON substructure (flies with the ship),
  AncientBlastDoor at (125,171): AncientCommsConsole, 2 AncientTerminal,
  2 AncientSystemRack, AncientHermeticCrate, AncientCryptosleepCasket (empty).
- Dead engine sockets at (104,166) and (152,132); machinery cluster ~(158–166,166–175).
- 6 mismatched hull patches (Steel / KOTOR_AlloyBronzium) at (114,92-93),
  (125,174-175), (162-163,176), (133,97-98), (156,122-123), (138,148-149) —
  conduit + astrofuel pipe re-laid under every one.
- Pad grime on both Spaceports_ShuttleLandingPad (115,65)/(136,65); sentry
  stains at (124-130,136-137).

## Held owner decisions (needs: owner)

1. **Vault roof** — currently open sky so the interior is visible. One word
   ("roof it") → `jawa/set_roof_batch` RoofConstructed over x120–124 / z169–173.
2. **Stele inscription** — ⛔ DEAD. The owner REMOVED the stele (2026-09-02);
   measured absent from the map and from `gravship_scratch_b.rws`. There is nothing
   to inscribe. The drafts are kept only in case a later stele wants them:
   - "IT SLEEPS. FEED IT NOTHING. ASK IT NOTHING."
   - "The Engine remembers every hand that touched it. Touch it politely."
   - "HOME is the noise it makes when it is not angry."
3. **Casket contents** — the vault's AncientCryptosleepCasket is empty. Occupant?
4. **Factory live/dead-twin pass** — owner must point at the semi-working
   factory bay (no workbenches found in ring scan x88–188 / z85–215); then build
   two dead-twin bays flanking it: same layout, unpowered, rusted, broken-down.

## Remaining bridge passes (needs: bridge, no owner input required)

- Toll shack near the landing pads (small MegaBone room + Aurebesh sign).
- Droid-sentry corpses at posts: NO husk prop def exists in the stack (checked
  offline dump + live probes); route would be spawn droid pawn factionless →
  kill via jawa/damage → corpse. Beware SPAWN_PAWN_SUBSTITUTES_VANILLA_KIND_1.

## Traps met this session (already in LESSONS_INBOX)

substructure `set` silently skips under-terrain cells; wall demolition drops
full-material leavings (wealth injection); `jawa/clear_ui` does not close
`MainTabWindow_Menu` — check `get_ui_layout` surfaces and `rimworld/close_window` it.

---

# CLOSED 2026-08-28 by BENCH on the owner's word ("Close the shrine follow-ups please")

The held decisions are settled by the close, in the direction the map already is:
vault stays unroofed · stele stays uninscribed · casket stays empty · no factory
twins, toll shack, or droid sentries. The shrine round ships as built. Anything
here is re-raisable as a fresh item if he ever wants it.
