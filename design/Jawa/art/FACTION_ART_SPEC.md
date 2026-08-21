<!-- status: live -->
# Faction art — the world map, and what v1 owes it

_DECIDE, 2026-08-21, closing `FACTION_ART_SPEC_1`. Every mechanism claim below was read
from the shipped C# or the shipped def; every path was checked against the 1.6 load path,
not against the file system._

> 🔴 **THE RULING, and it is a narrowing.** `FACTION_SPEC.md:18` rule **R17** already says
> *"bespoke faction art is `[v2]`"*, and that stands. ⇒ **v1 does not commission thirteen
> Star Wars sigils.** What v1 owes is much smaller and much harder to skip: **every faction
> must have an icon that resolves, and no two factions on the map may draw the same one.**
> The Star Wars canon direction is written in §5 as the v2 commission brief, so the artist
> is not starting from nothing when it is scheduled.

⚠️ **Why the small thing is the urgent thing.** The owner's world is built **once** and
frozen. A faction's marker is what a player uses to read the planet, and there is no
regenerate behind it.

---

## 1. What actually draws on the world map — measured, not assumed

Three fields, and **the surprising one is that `factionIconPath` is a world-map field**, not
merely a UI field:

| field | where it renders | source |
|---|---|---|
| `factionIconPath` | ⭐ **the settlement's marker when the planet is zoomed out**, and the faction's icon in every UI list | `Settlement.cs:40` — `ExpandingIcon => Faction.def.FactionIcon` |
| `settlementTexturePath` | the settlement's marker when zoomed in | `Settlement.cs:74` |
| `colorSpectrum` | ⇒ `Faction.Color`, which **tints both of the above** | `Settlement.cs:74` `MaterialPool.MatFrom(path, WorldOverlayTransparentLit, Faction.Color, 3550)` |

🔑 **Three consequences that decide every choice in this document:**

1. **Both markers are tinted by the faction colour, and the icon is tinted only on the
   map.** `FactionUIUtility.cs:112` and `:290` draw the icon with no colour set, so the
   Factions tab shows it as authored. ⇒ **art with colour baked in looks right in the UI
   and muddy on the planet.** Author white-to-grey with alpha; let `colorSpectrum` do the
   colouring.
2. **A path that does not resolve is not an error — it is a magenta square.**
   `FactionDef.cs:375` falls back to `BaseContent.BadTex` and logs nothing at that point.
3. **Shape is the only channel that separates two factions at planet scale.** Tint is the
   other, and it is weak: our thirteen colours are mostly mid-value earth tones read
   against desert terrain. Two factions sharing an icon path are, in practice, one faction
   on the map.

**Canvas:** 128×128 PNG with alpha is the working convention on this stack — measured from
`UI/FactionIcons/JunkersOutpost.png`, the one non-vanilla icon we already use.

**Inheritance:** `settlementTexturePath` is supplied by all three abstracts we build on —
`OutlanderFactionBase` and `PirateBandBase` give `World/WorldObjects/DefaultSettlement`,
`TribeBase` gives `World/WorldObjects/TribalSettlement`. ⛔ **Do not "fix" our defs by adding
the field**; they already inherit it and no faction of ours is missing it. `factionIconPath`
is *also* inherited (`Town` / `Village` / `PirateOutpost`) — which is precisely how two of
the three collisions in §2 happened, silently.

---

## 2. 🔴 The defects — four, and one of them ships a magenta square

### 2.1 `Jawa_IndigenousTribes` has no icon at all

`src/Jawa/Jawa_Patches/Defs/FactionDefs/JawaTribes.xml:59` points at
`OuterRim/WorldObjects/MoistureFarmers`. **That texture is not in the 1.6 load path.**
Verified twice, independently:

- The only copy on disk is
  `C:\Program Files (x86)\Steam\steamapps\workshop\content\294100\2919227155\Common_Old\Textures\OuterRim\WorldObjects\MoistureFarmers.png`
- Outer Rim - Core's `LoadFolders.xml` loads `Common_Old` under **`<v1.4>` and `<v1.5>`
  only**. Its `<v1.6>` block loads `/`, `Common`, `1.6` — and `Common/Textures/OuterRim/`
  does not exist.

⇒ `FactionIcon` returns `BadTex`. **The Jawa Trade Moot — the player's own kin, seven
settlements — draws as a magenta square on the frozen planet.** 🔑 This is the
stranded-folder trap in `skills/reading-rimworld-graphics`: art left in a folder an older
game version loaded. It is a real finding about the donor mod, not a resolver bug.

### 2.2 Three pairs of factions draw the identical glyph

| shared path | who | settlements between them |
|---|---|---|
| `World/WorldObjects/Expanding/Empire` | **`Jawa_AscendantHelix`** (set explicitly) and **`Empire`**, the Galactic Empire | 6 |
| `World/WorldObjects/Expanding/Town` | **`Jawa_HuttCartel`** (set explicitly) and **`OutlanderCivil`**, the Homestead Defense League (**inherited** from `OutlanderFactionBase`) | 21 |
| `World/WorldObjects/Expanding/Village` | **`Jawa_DeepwaterCompact`** (set explicitly) and **`TribeCivil`**, the Deep Desert Tribes (**inherited** from `TribeBase`) | 14 |

⭐ **41 of the map's ~72 settlements** are drawn as one of three shapes, each shared by two
factions. And `Town` is *also* `PlayerColony`'s icon and `Village` is *also* `PlayerTribe`'s
— so under the current defs **the Hutt Cartel draws the same glyph as the player's own
colony.**

### 2.3 The green that already read wrong

`FACTION_SPEC.md:614` records it: `Jawa_WildsteamClan`'s deep green `(0.30,0.45,0.25)` on
`Expanding/VillageSavage` *"reads wrong on an outlander icon"*. ✅ Kept, unresolved, and
folded into the LOOK step in §4 rather than guessed at again.

### 2.4 Two icons are on-loan from other mods with no gate

`World/RogueDroids` needs `guy762.kotordroids`; `UI/FactionIcons/JunkersOutpost` needs
`oskarpotocki.vfe.pirates`. Both are active, and both resolve today. ⚠️ **A texture path
cannot carry `MayRequire`** — if either mod leaves the list, that faction becomes 2.1.
Recorded, not fixed: adding a dependency is a bigger move than this item.

---

## 3. The v1 fix — four reassignments, reusing art that already ships

**Reuse only.** Nothing here is commissioned; every path below is a texture the game or an
already-active mod already loads, and every donor faction is **suppressed by
`src/Jawa/JawaFactionSlate/Patches/OnlyOurFactions.xml` or `hidden`**, so it holds no
settlement and the glyph is genuinely free.

| faction | from | ⇒ to | why this glyph |
|---|---|---|---|
| `Jawa_IndigenousTribes` | `OuterRim/WorldObjects/MoistureFarmers` **(dead)** | `World/WorldObjects/Expanding/Salvagers` | ⭐ literally the salvager marker, for the salvagers. Odyssey's `Salvagers` is zeroed by the slate |
| `Jawa_HuttCartel` | `Expanding/Town` **(shared ×2)** | `World/WorldObjects/Expanding/TradersGuild` | a trade-guild glyph for a cartel whose whole character is the market. Odyssey's `TradersGuild` is zeroed by the slate |
| `Jawa_DeepwaterCompact` | `Expanding/Village` **(shared)** | `World/WorldObjects/Expanding/TownRough` | still a civic settlement — right for *"clean infrastructure married to ritual reverence for the cistern"* — and distinct from `Town`. `OutlanderRough` is zeroed by the slate |
| `Jawa_AscendantHelix` | `Expanding/Empire` **(shared)** | `World/WorldObjects/Expanding/HoraxCult` | ⭐ a cult sigil, not a town. `INHABITED_CAST_HELIX.md:9` — *"Not a laboratory — a people with a religion about it."* Anomaly's `HoraxCult` is `hidden` and holds no settlement |

⛔ **Do not move the four reskins** — `Empire`, `OutlanderCivil`, `TribeCivil`, `Pirate` keep
their vessel's icon and spectrum. That is R22's principle and it is what makes the reskins
cheap. When an authored faction collides with a vessel, **the authored faction moves.**

⛔ **Do not add `settlementTexturePath` to any of our defs** (§1).

✅ **Leave alone:** `Jawa_GeonosianFoundryHive` on `Expanding/Insects` and
`Jawa_WildsteamClan` on `Expanding/VillageSavage`. Both share with a vanilla faction
(`Insect`, `TribeSavage`) that the slate keeps off the map, so neither is a visible
collision.

⚠️ **These four are assigned by reasoning, not by looking.** §4 is how that gets checked
before the world is frozen, and it is not optional.

---

## 4. Verify — and the LOOK step is the real one

```
# 1. every path in the roster resolves in the 1.6 load path
grep -rn factionIconPath src/Jawa/Jawa_Patches/Defs/FactionDefs/
#    -> for each, confirm the PNG is under a folder the donor mod's LoadFolders.xml
#       lists under <v1.6>. Common_Old and 1.5 do NOT count.

# 2. no two of the thirteen share a path, INCLUDING inherited ones
#    -> resolve OutlanderCivil/TribeCivil/Pirate through their abstracts before comparing
```

🔴 **3. Then look at them.** Build a contact sheet of the thirteen icons **at world-map
scale, each tinted by its own `colorSpectrum`, against the desert terrain colour** —
`src/RimMandrake/Utils/extract_bundle_textures.py` pulls the vanilla ones out of
`resources.assets`. Two things only the picture can answer: whether thirteen glyphs are
still distinguishable at that size, and whether Wildsteam's green (§2.3) reads.

**A number that says the map is legible while the sheet shows thirteen grey blobs is the
number being wrong.**

---

## 5. `[v2]` — the commission brief, so the artist is not starting cold

⛔ **Nothing in this section is v1 work and none of it is scheduled.** It exists so that
when bespoke faction art *is* commissioned, the direction is already decided. Sources are
`faction_roster_v2.md`, `FACTION_SPEC.md` and the `design/Jawa/bridge/INHABITED_CAST_*.md`
briefs.

Every sigil below must survive §1's constraints: **one shape, white-to-grey with alpha,
legible at ~24 px, no baked colour.**

| faction | register | the sigil idea |
|---|---|---|
| **Galactic Empire** | cold, inexorable, procedural — *"clerks, not villains"* | ⭐ **the rank itself.** Its second god is *"the Line / That Which Has No Face"*, and *"anonymity is the sacrament"* — a formation, not a crest. Hard grey/white |
| **Hutt Cartel** | oily, transactional, amused by your desperation | a seal or stamp — the mark a shell company puts on a crate. Sickly gold |
| **Junkers** | *"weight is rank; what is bolted to you was cut off somebody slower"* | ⭐ the **warcasket** silhouette — steel welded around a body. ⛔ not generic post-apocalyptic raiders |
| **Free Droid Enclaves** | machines that declared themselves people | *"the Rust Cathedral"* — brass gone dull, a bulb optic. Cold steel |
| **Geonosian Foundry Hive** | chitinous, brutal, trophy-laden | a hive mouth or a caste mark. Rust |
| **Deepwater Compact** | clean infrastructure married to reverence for the cistern | the cistern, measured — a vessel with a level marked on it. Teal |
| **Wildsteam Clan** | hand-made, bone-and-hide; ⭐ the only faction that plants | a growing thing, bound. Deep green — ⚠️ and §2.3 says green is the hard one here |
| **Ascendant Helix** | clinical, sterile, chrome — *"a people with a religion about it"* | a helix as a **devotional** object, not a diagram. Pale violet |
| **Jawa Trade Moot** | comedic, greedy, communal, subterranean | ⭐ the **sandcrawler**, or the two glowing eyes under a hood. Sand with the ember |
| **Homestead Defense League** | humble, hand-made, libertarian, decent | the vaporator array — *"the faction's defining infrastructure"*. ⛔ no spacer chrome |
| **Deep Desert Tribes** | zealots who are not villains; offworld tech is abhorrent | the gaderffii, or the filtered mask |
| **Blackstar Company** | *"one dangerous person with a name who is coming for you"* | ⭐ *"the sworn do not remove the helmet"* — the helmet is the sigil |
| **the Forgotten Arsenal** | *"not an army, an armoury nobody came back for"* | ⛔ **none.** It is `hidden`, holds no settlement, and costs *"one label patch, not a dossier"* |

---

## 6. What this file supersedes

- `FACTION_SPEC.md:427-437` — the R17 icon assignment table. Four of its rows are replaced
  by §3; the rest stand, and R17 itself is reaffirmed, not overturned.
- `enrichment_agents.md:123-128` — the proposed, unbuilt *"faction visual-identity kit
  agent"*. §5 is that brief, written by hand instead.
