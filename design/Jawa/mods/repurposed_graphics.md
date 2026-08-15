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

⚠️ **Licensing is unresolved and matters here.** Reusing another mod's texture in
our own def is redistribution. Fine while we never publish; check the donor's
licence before anything ships publicly. Several mods in this stack carry no
licence file at all, which defaults to all-rights-reserved.

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
