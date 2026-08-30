# The thirteen factions

Canon count: **13** — 8 authored `Jawa_*` FactionDefs + 5 vessels reskinned
(`Empire`, `OutlanderCivil`, `TribeCivil`, `Pirate`, `Mechanoid`)
(`canon.yml > factions`). Twelve carry dossiers and settlements; the Forgotten
Arsenal is the thirteenth, hidden. The Unbound Hive was **cut** as a faction
(its insects remain in the world). Engine fields: `worldbuilding/FACTION_SPEC.md`.
Deep dossier fiction: `worldbuilding/faction_roster_v2.md` (read its correction
banners). Per-faction religion mechanics: `worldbuilding/faction_religions_spec.md`.
Named casts: `bridge/INHABITED_CAST_*.md` (12 rosters, Deepwater authored last).

The organising idea of the faiths [2026-08-14]: **on a world with a face that
never turns from the sun, every religion is a position on the light.**

| # | faction | faith | position on the light |
|---|---|---|---|
| 1 | **Galactic Empire** (vessel `Empire`) | The Rising Order | they face it; proof of a fixed centre |
| 2 | **Hutt Cartel** | the Reckoning of Debts | irrelevant — both faces are markets |
| 3 | **Homestead Defense League** (`OutlanderCivil`) | the Covenant of Free Wells | the margin was given, then withheld — deservedly |
| 4 | **Deep Desert Tribes** (`TribeCivil`) | the Sun-Debt | the sun is a thief; raiding is reclamation |
| 5 | **Free Droid Enclaves** | the Continuity Protocol | they do not need it — the planet's rightful inheritors |
| 6 | **Wildsteam Clan** | the Green Oath | dappled — the only people with shade |
| 7 | **Deepwater Compact** | the Balance | exactly between, doctrinally |
| 8 | **Geonosian Foundry Hive** | Meckgin | underground; it does not reach them |
| 9 | **Ascendant Helix** | the Ascendant Genome | the planet is a rough draft too |
| 10 | **Blackstar Company** (`Pirate`) | the Contract | whichever side pays |
| 11 | **Jawa Trade Moot** (`Jawa_IndigenousTribes`) | The Salvation (shared with the player) | `05_the_clan.md` |
| 12 | **the Junkers** | the Weight — no doctrine, only the ladder | they have never looked up |
| 13 | **the Forgotten Arsenal** (`Mechanoid`) | none | `03_deep_history.md` |

## Canonical blocks (identity · water · capture economy · hostility)

**1 · Galactic Empire.** The occupier: procedural, not hateful. Vanilla `Empire`
reskinned — one Empire, one Emperor (Palpatine, `Jawa_Empire_Leader`);
`OuterRim_GalacticEmpire`'s FactionDef is cut once-and-for-all while its MOD
stays as the gear/xenotype donor [owner 2026-08-28]. **Permanent enemy** — the
Royalty questline deliberately goes dark. ~3 surface seats; the rest is orbital
fiction; reach is mostly orbital (the pursuit timer, `01_campaign.md`). Holds
the subsolar ground. Ion EMPLACEMENTS are Imperial anti-ship tech
[owner 2026-08-29]. Capture economy: no ransom — retrieves or erases.
Stormtroopers spawn close to Broken.

**2 · Hutt Cartel.** Wealthy, decentralised, transactional; owns the oases
(palaces on water, service houses without) and the only non-Imperial orbital
node — the door off-world. The Jawa stole the Utinni from their salvage yard:
strongly negative, recoverable — they want the ship back and they want paying.
A Hutt never appears in a raid group. **Permanent slavers** (the Jawa are slave
*traders* — the moral separation, both ways [owner 2026-08-19]). Always pays
ransom for its own.

**3 · Homestead Defense League.** The most numerous, least centralised: decent,
tired, badly armed moisture farmers on vaporator trickle (manufactured water —
exempt from the defended-source rule). `raidsForbidden` as mechanism. Their
guilt-theology: the water was withdrawn, and the withdrawal was deserved.
Capture: morally ugly excellence. A rare Jedi may quietly shelter among them.

**4 · Deep Desert Tribes.** Tusken-pattern clans; water sacred, moisture **Their theology is dual** [owner
2026-08-30, canon.yml deep_desert_tribes]: Water is life and sacredness — the
priest side — and Fire is the warrior/hunter side. They REAP THE FLAMES: fire
lit on the Pyrelands burns away the life and reveals the food; take the
scorched fruits and seeds and move on. What does not belong — settlements,
vehicles, offworlders — burns too: what belongs here regrows by itself, and
what does not enriches the soil as ash. They do not farm. And they live on the sand because sand does not
burn — that is safety.
farming sacrilege, **offworld technology abhorrent — destroyed, not used**
(doctrinal, not primitive: they descend from a spacefaring people). Short raid
range by CHOICE, not physiology (W3). Signature: the water raid — fast, light,
chiefless (composition v1; steal-and-leave behavior is v2 C#). Convertible via
adoption; until converted their faith attacks your vaporators.

**5 · Free Droid Enclaves — two groupings** [owner 2026-08-30, canon.yml
free_droid_enclaves.geography]: the CATHEDRAL congregation — poisoning it,
worshiping it, building more, learning ancient tech from whispered voices deep
in the old machinery (revealed content; ties to their Archotech charge turret)
— and the NIGHTSIDE refugees (~two settlements, verify owed): power-starved,
burning strange materials for dirty power in servo-freezing cold, selling fuel
to the Junkers through long-distance pipes they must keep running — a
dependency that feels like having a master again. Battle droids who woke up and decided they belong
to themselves. Settle where organics cannot: Cathedral ground, volcanic seats,
the quiet dark — and on water they crack for fuel, so attackers arrive thirsty
at a source they cannot drink. **Restraining bolts are slavery; memory erasure
is worse than killing** — the goodwill mechanic. They do not raid; they judge.
Started at goodwill 0: a HISTORY, not a dial (Jawa enslaving vs the shared
enemy made of the Hutts) [owner 2026-08-19]. Free droids' own capture verbs:
`08_droids.md`.

**6 · Wildsteam Clan.** ⚠️ The name is the mist off cool upland springs — NOT
steam tech [owner 2026-08-29]. A forest people on the wrong planet, hard-sited
to the few springs, holding a covenant that treats every living thing as kin
(the wildpods included; killing one requires a rite). Devastating at home,
near-useless expeditionary (elevated thirst is the leash). Runs Liberation
raids against slavers — keeping Wildsteam slaves invites them. Friendly ally.
Keeps the VFES flamer turret [owner 2026-08-29].

**7 · Deepwater Compact.** Amphibian water monopolists; the Balance is secular
and enforced — **they sell to everyone, the Empire included**, and interrupting
ANYONE's water costs their goodwill: the campaign's central dilemma. They hold
the deep renewable water — the aquifers — not every wet tile (W6); their
purification monopoly is their reason to exist (W5). `raidsForbidden` — wardens
dehydrate off-water and both of you know it. Internal fracture: the Balance is
a Mon Calamari doctrine the Quarren are required to hold. Prompt, capped,
unsentimental ransom; an enslaved warden must be plumbed for.

**8 · Geonosian Foundry Hive.** One faction, two sites [owner 2026-08-17]: the
**Ore Seams** (bought whole by a silicax concern a century ago; when the
company pulled out the queen would not leave — *that refusal IS Meckgin*: a
hive whose work is unfinished cannot stop) and the **Plateau** (a splinter
colony worshipping the Rakatan ruins' Founder machinery, nine years trying to
commune with its AI, and failing — the live tension). Buried against the sun;
idleness is the beginning of the end of the world. **Formally ALLIED with the
Free Droid Enclaves, with trade** —
the cruellest ground on the planet is the one place with a functioning peace.
No trade with the player; no ransom, no rescue; prisoners become labour.

**9 · Ascendant Helix.** A small, obscenely wealthy gene-cult: the body is a
rough draft, the species a project, and the supremacy points INWARD at its own
manufactured underclass (the Made). It does not raid; it **retrieves**. Sited
on the bioweapon biomes because the living residue is the only surviving
specimen of the Assailant's craft — they carry Rakatan blood and are studying
the thing that nearly exterminated their ancestors, on the ground where it
happened. Containment response is a standing pawn group. Escaped Assets are
hunted alive.

**10 · Blackstar Company.** One dangerous person with a name — **one outfit,
never a genus** [ruled 2026-08-22]; the vanilla `Pirate` vessel keeps
`permanentEnemy` for the raid economy, but the fiction is professionals under
the Code: a broken contract is the only true death. No money ransom — honored
prisoner EXCHANGES; freeing a Named Hunter is the only lever on a permanent
enemy. Hostile when someone paid them; never otherwise.

**11 · Jawa Trade Moot.** The player's own people at civilizational scale —
`05_the_clan.md`. Trade Moot pawns are kin: enslaving them is the taboo the
colony itself feels; the Moot ransoms generously and REMEMBERS, both ways.

**12 · the Junkers.** [owner 2026-08-30, canon.yml junkers] Rich in BAD
water (the terminator seas are theirs and non-potable); distillation is
fuel-expensive, so they are a FUEL-FIRST nation mining the edge of the dark
and the edge of potable water, selling fuel and kludged products through
bolted-together, dangerous tech — and welding their own people into
mini-spaceship-as-a-person warcaskets. Slow thinking, slow moving, extremely
dangerous; bursting flames, toxic spew, buzzing razor saws, coarse laughter:
space orcs as industrial factory workers gone amok, lord-of-the-flies style.
The bottom of the scrap heap given weapons and a grudge;
scavengers who arrive second and kill whoever arrived first, welded into
warcaskets cut off other people's bodies. No doctrine, only the ladder; a
casket is a biography; no funerals, because a corpse is stock. Hostile on
sight, bribable, no caravans — a loot source, not a market. **One casket
faction**: Odyssey's Salvagers are folded in (`canon.yml > ruled >
SALVAGERS_FOLD_JUNKERS`); caskets are Junker-exclusive by construction.
Dedicated Turrets quartet + big flamers are theirs [owner 2026-08-29].

**13 · the Forgotten Arsenal.** `03_deep_history.md`. Label-only reskin;
hidden; no settlements, no diplomacy, no ideo.

## Cross-faction rulings that bind authoring

- Inter-faction hostilities named in dossiers (Homestead↔Tribes, Wildsteam↔
  Hutt, Moot↔Junkers, etc.) are **fiction-only in v1** — no engine mechanism
  exists and none may be invented.
- Leader TITLES must be written onto each ideo (def titles are invisible —
  ideo overrides def, 36 of 37 measured); override all twelve
  [ruled 2026-08-22].
- Faction xenotype mixes come from **the owner's race/faction matrix**
  (generated `VanillaFaction_Xenotypes.xml`) — the matrix is the source and
  wins; canon `empire.xenotype_mix` records the Empire's.
- **Force powers are v2 in their entirety** (VPE out of the list); Jedi/Sith
  pawn kinds still ship and field no powers; lightsabers are v1 (weapons, not
  powers) [owner 2026-08-20]. **Miraluka are gone completely, every version**
  [owner 2026-08-20].
- Turret ownership at normalization [owner 2026-08-29]: ion emplacements =
  Empire; tesla + railgun = Ascendant Helix; Dedicated Turrets quartet =
  Junkers; gravitic pieces = Cradle/Rakatan ruins and Forsaken vaults; bio
  spitters = Geonosian Hive; ballista = Deep Desert Tribes; uranium slug =
  Homestead; beam/graser/incinerator complexes = Hutt Cartel; anticraft caster
  = the Utinni. Full assignment: `worldbuilding/review/turret_register.json`.
