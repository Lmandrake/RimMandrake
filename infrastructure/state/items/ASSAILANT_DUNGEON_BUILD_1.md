## spec
Full spec: `design/Jawa/worldbuilding/dungeons_arc_spec.md` §2. Summary:

The Assailant's **first-impact point** — where its landing struck, unknown and
undetected until far too late (canon.yml `assailant_reveal_arc`). Fixed site,
deep-nightside, in region **The Umbra** (arc > 152°, an existing named region —
`ASHKARR_WORLD_DEFINITION.md`), adjacent to tile **20853** (held for
`VAULT_DUNGEON_BUILD_1`'s V6, the frozen-Rakata vault) — "the frozen Rakata and
their frozen killer sleep near each other, one pilgrimage, two revelations."

**Thaw-gate** (owner ruling verbatim, `ASSAILANT_FLESH_DUNGEON_1` history
2026-08-30): the complex is inert/frozen on arrival; delivering an "old power
core" item to a hidden socket flips it to hostile/active — guardian spawns
come online, sealed passages open, the reveal beat becomes reachable. One-way
state change, drafted as a quest signal/map trigger (confirm at build time
whether existing `rimworld-quests` vocabulary suffices or a custom C# node is
needed — not proven this pass).

**Content palette**: all 70 rows of `assailant_flesh_sheet.decisions.json`
(`blanket: keep-for-dungeon`), three of them (`DeadColumnMod`, `Trispike`,
`Metalhorror`) site-only exceptions to their campaign-wide cut. Guardian
register: Anomaly fleshmass/entity toolbox (the one v1 exception to
zero-Anomaly, canon.yml `anomaly_content`) as the body-horror core, plus ONE
sickly-pale reskin of the Geonosian living turrets for Assailant emplacements
(new art, not yet drawn). `AA_BlackDefiler` is already canon-assigned "The
Assailant's flesh" on the turret register.

**Layout concept**: three bands — frozen approach (dormant fabric, the
power-core socket at the threshold) → interior digested-works galleries
(`VFEI2_InfestedShip{Chunk,Module,Part}` set-pieces — direct match for "a
Rakatan structure being DIGESTED") → core (embedded witness +
`FleshmassHeart`/`FleshmassNucleus`, ship memory-fragment loot).

**Learning chain / endgame** (RULED, canon.yml `assailant_reveal_arc`): droid
trust → Cathedral trust → Cathedral reveals the location → thaw-gate strike →
Cathedral wants the Cradle as its pyrrhic strike against the Assailant →
releasing that knowledge to the Hutts needs a deal protecting the droids.

**Held for the owner** (creative lock-in, per `FUTURE_VECTORS.md`'s own
"with the owner" instruction — this item stays `doing`, not closed): the
actual KCSG structure authoring for all three bands; the thaw-trigger's
concrete implementation; the power-core item's exact defName; the
pale-Geonosian-turret reskin art; all reveal-beat/Hutt-deal dialogue and
letters; the bridge write that sites the complex on the world.

## verify
- [ ] Owner reviews `dungeons_arc_spec.md` §2 and rules any open calls
  (thaw-trigger mechanism, power-core defName, exact tile).
- [ ] Three-band layout authored as KCSG `StructureLayoutDef`(s) and proven on
  a quicktest by LOOKING (`take_screenshot`, read the image — see the vault
  item's quicktest-proven bar, `dungeons_arc_spec.md` §3.7, same standard
  applies here).
- [ ] Thaw-gate playable end to end on a quicktest: complex spawns dormant,
  delivering the power core flips it hostile, the reveal beat fires.
- [ ] Site committed to the real world (`world_commit`, one bridge driver at a
  time) on tile adjacent to 20853, deep Umbra.
- [ ] Reveal-beat letters/dialogue authored and fire correctly on
  entering/looting the core.

## criteria
- [ ] Complex reads as frozen/inert until the power core is delivered — no
  guardian spawns before the trigger.
- [ ] Assailant register guard holds: no ambient tyranny content pre-reveal;
  the Assailant is never named, never sympathetic.
- [ ] All three site-only-exception defs (`DeadColumnMod`, `Trispike`,
  `Metalhorror`) appear ONLY in this dungeon, nowhere else in the campaign.
- [ ] Pale-Geonosian-turret reskin reads as visually distinct from ordinary
  Hive turrets on sight.
- [ ] `AA_BlackDefiler` present per its existing "Assailant's flesh" turret
  assignment.

## Watch out
🔶 **This item is a build SPEC, not creative lock-in.** `FUTURE_VECTORS.md`
names this arc explicitly as "with the owner" — do not close this item on a
solo authoring pass. Leave `doing` until the owner has ruled the open calls in
`dungeons_arc_spec.md` §2.7.

⛔ **Do not weld this to the forsaken crags.** `03_deep_history.md`: "the crags
read as chemistry that was always here; two alien facts are richer than one
explained one."

🔑 **The 70-row content palette is not a menu to re-curate.** It was ruled
2026-08-30, `blanket: keep-for-dungeon`, `decidedCount: 70` — use it as-is;
the three site-only exceptions are the only asterisks.
