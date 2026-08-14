# Droid chassis — what we have, what one subscribe buys, what needs art

_VISION, 2026-08-13. Measured against the owner's canon-lineage brief. **The
headline is that coverage is far better than it looked, and the reason it looked
worse is a search method.**_

---

## ⭐ The method trap, first, because it changed three answers

**Two research passes reported "Retail Caucus droid: NOT FOUND — needs a
from-scratch sprite." It is installed and active right now.** So is the aqua
droid. So is the buzz droid.

They are invisible to a title search because JDS names its defs by model number
and **the canon name appears only in the `<description>`**:

| the owner asked for | what already provides it | where the canon name lives |
|---|---|---|
| **Retail Caucus barrel droid** | `JDSCIS_LR-57_Combat_Droid` | description: *"Retail Caucus droid, retail droid, or mine droid…"* |
| **Aqua droid** | `JDSCIS_AQ_Battle_Droid` | description: *"Aqua droids, were an amphibious model…"* |
| **Buzz droid** | `JDSCIS_Pistoeka_Sotage_Droid` | Pistoeka *sabotage* droid **is** the buzz droid |

🔴 **The honest coverage question is "what do the descriptions say", not "what is
the mod called."** Acting on the title search would have commissioned three
sprite jobs for droids already on disk.

## The scoreboard

> **7 already have · 5 one subscribe away · 4 genuinely need art.**

| silhouette | verdict |
|---|---|
| **Crab droid — LM-432 Muckraker** | ✅ **have** — `OuterRim_MuckrakerDroid`, active. *(Six-legged variant does not exist)* |
| **Dwarf spider droid** | ✅ **have** — `JDSCIS_DSD1`, active |
| **Retail Caucus barrel droid** | ✅ **have** ⭐ |
| **Aqua droid** | ✅ **have** ⭐ |
| **Buzz droid** | ✅ **have** — silhouette right, job wrong (JDS makes it a miner) |
| **Sniper droid** | ✅ **have, partial** — a sniper droideka, not the standalone canon model |
| **Imperial sentry** | ✅ **have, partial** — DT Sentry + KX Security, active |
| **Tank droid — NR-N99** | 🟡 one subscribe |
| **Homing spider droid — OG-9** | 🟡 one subscribe |
| **Octuptarra tripod** | 🟡 one subscribe |
| **Hailfire — IG-227** | 🟡 one subscribe |
| **Scorpenek annihilator** | 🟡 one subscribe |
| **Rocket battle droid** | ❌ needs art *(closest: `B2-RP`, in the same mod)* |
| **Vulture droid** | ❌ does not exist in any RimWorld version |
| **Hyena bomber** | 🟠 exists only as an **SRTS transport** — a fly-to-another-tile widget, not a map unit. Needs a framework we do not have, and the page says **not Odyssey compatible** |
| **B'omarr brain-walker** | ❌ needs art. Best donor: `Mech Theraphosidae` |
| **IT-O interrogation droid** | ❌ needs art |
| **Imperial Viper probe droid** | ❌ canon version is 1.3-only — but **MIT-licensed art exists** at `github.com/emipa606/StarWarsSupportDroids`. KotOR's hovering probes are the working analog today |

## ⭐ The one recommendation: `[KR] Star Wars: Droids`

**Workshop `3248936254`.** 1.6-tagged, **Biotech only — no framework, no HAR, no
JecsTools**, and Biotech is already active. Not installed. Its droids are
**pawns**, built in the mechanical gestator.

**It supplies five of the six real gaps in one subscribe** — NR-N99 tank droid,
OG-9 homing spider, Octuptarra tripod, IG-227 Hailfire, Scorpenek annihilator.
**There is no second source for any of the five.**

⚠️ Author's own warning: it *"disrupts the game's original balance."* Expect a
tuning pass, not a drop-in.

### 🔴 Take the chassis. Refuse the faction wrappers.

**The same author ships `[KR] Star Wars Separatist Army` and `[KR] Star Wars
Mechanoid its Droid`, which turn these chassis into factions and into vanilla
mech replacements. We do not want either.**

`what_the_machines_are.md` already ruled there is **no thirteenth faction** — the
roster holds twelve and four of them are already about machines. **These are
visual variety for factions that exist**, not new polities.

⇒ **Adopt for SILHOUETTES, not for count.** The Geonosian Foundry Hive is a droid
*manufacturer* with nothing distinctive to manufacture; the Separatist roster is
sixteen humanoids and one walker. **Five heavy, unmistakable shapes is exactly
what those two need**, and it is the difference between "more droids" and "that
faction looks like something".

## Also worth knowing

- **Vehicle Framework and Vanilla Vehicles Expanded are already installed and
  ACTIVE.** *"Requires a vehicle framework"* has been used as a disqualifier in
  past evaluations and **should be retired as one** — it costs nothing here.
  `[KR] Star Wars Tanks` (`3413994103`) becomes a cheap second option on that
  basis, though it is Republic/Imperial only and adds no droid walkers.
- **`Outer Rim – Separatists`** (`3097604003`) adds **no chassis** — but both its
  dependencies are installed, and it is the cheapest way to make the CIS droids
  we already own actually appear on a map.
- ⚠️ **Droid Depot's own probe-droid research is commented out** — lines 131–139
  of `Research__GeneralDroids.xml`. It never reaches the tree, so that content is
  inert today.

## Traps to carry forward

1. **Search def descriptions, not mod titles.** Cost three false "needs art"
   verdicts on this pass alone.
2. **Confirm appid 294100.** Several strong-looking hits were Ravenfield, Garry's
   Mod and Space Engineers. Reference art only.
3. **Steam's logged-out "removed for violating guidelines" banner is
   boilerplate.** It falsely condemned three live mods here. Check the API's
   `banned` field.
