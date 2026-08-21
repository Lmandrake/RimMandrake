<!-- status: live -->
# repurposed_graphics.md — turned off, but the ART may still be worth having

DECIDE owns this. **Append-only.** Nothing here is scheduled and nothing here is
a commitment.

**Why this file exists.** The cherrypick turns content off for *fiction* reasons
— a mechanic we will not use, a gun that looks wrong. That says nothing about
whether the **texture** is good. A crashed mechanitor ship is bad game content
for this campaign and excellent scenery for a scavenger world, and once it is
switched off nobody remembers it existed.

**How to use it.** When a `[v2]` job needs art — a prop, a building, a piece of
salvage — read this before commissioning anything. Reusing a shipped texture is
free; generating one is not.

✅ **Licensing is SETTLED and is not a consideration — owner, 2026-08-15.** This is
a **private playthrough**; nothing is published. **Do not weight licences in any
reuse decision, and do not spend effort reading licence files.** Reuse another
mod's textures, def values or whole defs freely, and choose between "reference
their mod" and "author our own" on engineering grounds only — dependency risk,
control over names and values, and how much cherrypick work the unwanted
remainder costs.

⚠️ The single carve-out, and it is not a licence question: **if this ever ships
publicly, that decision revisits everything reused here.** Recorded so a future
reader knows the reasoning was "private", not "permitted".

---

## From the mechanitor cut, 2026-08-15

The player mechanitor system is off — no mechlinks, no gestators, no band nodes,
no rechargers. **33 defs cut.** What the art could still be:

| what | why it is worth keeping in mind |
|---|---|
| **`MechGestator` · `LargeMechGestator`** | Big industrial vats with a forming-mech animation. Reads as a droid-manufacturing tank — which is *exactly* the Geonosian Foundry Hive's fiction, and the prize in the droid-theft arc |
| **`BandNode` · `AM_BeamcasterBandNode` · `AM_GreaterBandNode`** | Antenna and relay props. A scavenger clan's comms mast, or Imperial orbital infrastructure |
| **`MechBooster` · `BurnoutMechlinkBooster`** | Tower-shaped tech props |
| **`BasicRecharger` · `StandardRecharger` · the WallStuff chargers** | Charging cradles. Obvious fit for a droid bay aboard the gravship |
| **`Mechlink` · `ControlSublink` · `RemoteRepairer` · `RemoteShielder`** | Small implant/device icons. Restraining-bolt art is unbuilt and these are the right shape and scale |
| **21 `MechGestator*` motes** | Forming/complete animation frames. Reusable for any vat, tank or fabricator effect |

## Deliberately NOT cut, because the art is the point

Recorded so nobody "finishes the job" and removes them later:

- **`AncientBandNode` · `AncientBasicRecharger` · `AncientStandardRecharger` ·
  `AncientMechGestator` · `AncientMechGestatorTank` · `AncientLargeMechGestator`**
  (Core and Biotech) — these are *ruins* props, not player tech. Ancient mech
  wreckage half-buried on a desert world is the campaign's whole aesthetic.
- **`ShuttleCrashed_Exitable_Mechanitor`** — a crashed ship you can enter. On a
  scavenger world that is a gift, not a leftover.
- **The 11 `VFEPD_*` mech props** (Vanilla Furniture Expanded — Props and Decor)
  — decorative by construction. They were never functional mechanitor gear.
- 🪤 **`KOTOR_ShieldBank`** — matched the search on the word "recharger" and is
  **not** mechanitor content at all. It is a Star Wars shield recharger. Do not
  cut it.

## From the firearms cut, 2026-08-15

74 conventional guns are off. **Most of their art is worthless to us** — the
reason they were cut is that they look like real-world rifles. Two exceptions:

- **`Vanilla Weapons Expanded` makeshift-adjacent frames** — crude pipe-and-tape
  silhouettes read as scavenger-built regardless of the original name. (The
  Makeshift weapons are themselves deprecated for v1, so this art is available
  too — reskin fodder for a salvage-built *blaster*, not for another pipe gun.)
- **Ancient urban ruins' weapon icons** — genuinely modern, genuinely wrong.
  Recorded only so nobody re-proposes them.

## AssetBundle art IS reachable — the earlier note here was wrong

`[AB] Xenotype: Yautja` ships 2 loose PNGs and a 33.7 MB AssetBundle holding
**2,732 textures**. An earlier entry called that unreachable. It is not:
`src/RimMandrake/Utils/extract_bundle_textures.py` pulls every `Texture2D` out
with UnityPy, and 23,095 textures across 67 sources now sit in
`observed/inventory/bundle_textures/`.

⇒ **Bundled art is a graphics source like any other.** That includes vanilla —
Core's art is not even in a bundle, it is in `RimWorldWin64_Data\resources.assets`,
and the extractor reads that too.

## From the Vanilla Animals Expanded removal, 2026-08-15

The mod is gone, so this art is no longer loadable — it is recorded because the
subjects are desert-correct and we may want the *creature*, drawn our own way.

| what | why it is worth remembering |
|---|---|
| **`AEXP_GilaMonster`** | The one animal that survived review, cut only because it was the last tenant of a whole mod. A venomous desert lizard is squarely on-world; if we ever want a small dayside predator, this is the reference |
| **`AEXP_Camel`** | Cut in review, but a desert world without a pack animal is worth a second thought. Recorded so the question can be re-asked deliberately rather than by accident |
| **`AEXP_BeaverDam`** | A buildable animal structure. The mechanic — a creature that alters terrain — has no equivalent left in the stack |

## Giant Snake — cut stands, but the STAT BLOCK is the asset, 2026-08-15

**Owner's ruling: leave it cut.** The art is flat clip-art — thick black outline,
primary green and yellow, cartoon fangs — and it would read as pasted in from
another game.

Recorded because the *creature* is not the problem. `zal.giantsnake` shipped two
of the most lethal animals measured in the whole stack:

| | body | health | combat power | best DPS |
|---|---|---|---|---|
| giant snake · white viper | 4.0 | 6.5 · 7.5 | 150 | **21.2** |
| thrumbo, for scale | 4.0 | 8.0 | 500 | 11.5 |

Elephant-sized, tougher than a rhino, roughly twice a thrumbo's damage per second
off a 35-power toxic bite, `manhunterOnDamageChance` 100, and it already listed
`Desert` and `AridShrubland` among its biomes.

⇒ **If v1 ever wants a massive dayside ambush predator, build it on a surviving
body rather than restoring this mod** — the design (huge, venomous, always turns
manhunter, hunts prey up to body size 4.3) is the part worth copying.

🔴 **And do not copy its `combatPower` of 150.** A thrumbo costs 500 at half the
damage output. Anything that builds manhunter packs by points would price these
like muffalo and send a swarm.
