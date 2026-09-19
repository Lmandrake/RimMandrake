# MLIE_ARTOVERRIDE_COLLISION_CHECK_1 — pre-flight collision map for 6 queued species + Insectomorph/Dewback verdict

Investigation pass, offline. Mirrors the pattern already fixed twice this
session: `mandrake.rsw.swbestiary` loads AFTER every `*ArtOverride` mod in the
live `ModsConfig.xml` (index-driven, NOT via `About.xml` `loadAfter` — none of
these override mods declare `loadAfter` against SWBestiary, only against
`mlie.starwarsanimalcollection`) — so when SWBestiary's Wave C port extracts
donor art at the same relative `texPath` an override mod already ships custom
art at, SWBestiary's copy silently wins and reverts verified-live art with no
error. Already happened once for real (Anooba, `5a8fc8c1c`) and caught before
commit once (Dragonsnake, `8dc279c64`).

## Part 1 — 6 species still queued (Mynock, Kreetle, Horax, Fambaa, Zakkeg, Ronto)

Each override mod covers **south/east/north facings only**, at
`swanimals/<Species>/<Species>_<facing>.png`, `loadAfter` declares only
`mlie.starwarsanimalcollection` — none declare `loadAfter` against
`mandrake.rsw.swbestiary`. Live `ModsConfig.xml` (593 active mods) has
`mandrake.rsw.swbestiary` at index **560**, after all six:

| Species | Override packageId | idx | Colliding texPath (must NOT be re-shipped by the port) | Donor-only facings safe to extract |
|---|---|---|---|---|
| Mynock | mandrake.rsw.mynockartoverride | 305 | `swanimals/Mynock/Mynock_{east,north,south}.png` | flying-animation frames, `Mynock_Dessicated` |
| Kreetle | mandrake.rsw.kreetleartoverride | 306 | `swanimals/Kreetle/Kreetle_{east,north,south}.png` (adult only) | juvenile "maggot" stage, `Kreetle_Dessicated` |
| Horax | mandrake.rsw.horaxartoverride | 308 | `swanimals/Horax/Horax_{east,north,south}.png` | `Horax_Dessicated` only |
| Fambaa | mandrake.rsw.fambaaartoverride | 309 | `swanimals/Fambaa/Fambaa_{east,north,south}.png` (adult only) | juvenile stage, swimming graphic, `Fambaa_Dessicated` |
| Zakkeg | mandrake.rsw.zakkegartoverride | 311 | `swanimals/Zakkeg/Zakkeg_{east,north,south}.png` | `Zakkeg_Dessicated` only |
| Ronto | mandrake.rsw.rontoartoverride | 313 | `swanimals/Ronto/Ronto_{east,north,south}.png` (covers BOTH calf and adult stages) | `Ronto_Dessicated` only |

**What the future port must do for each**: extract/ship donor art for every
facing/life-stage EXCEPT the 3 named `_{east,north,south}` files above — skip
those exact files during the extraction/re-pathing step (this is what the
Anooba/Dragonsnake fixes did after the fact; doing it up front is cheaper).
Adding `loadAfter: mandrake.rsw.<x>artoverride` to SWBestiary's own `About.xml`
would NOT be sufficient by itself — load order here is driven by
`ModsConfig.xml` index, not by these `loadAfter` declarations (confirmed:
SWBestiary already loads after all six today and still collides on any
matching file it ships).

## Part 2 — Insectomorph / Dewback verdict

### Insectomorph: NOT broken — and not actually ported yet

The task's framing ("already-ported... reportedly also having an override
mod") is incorrect for Insectomorph. Verified:
- `grep -r RSW_Insectomorph src/RimStarWars/SWBestiary/Defs/` → 0 hits.
- The only "Insectomorph" hit inside SWBestiary is
  `Patches/BeastNorm/BeastNorm_Law3.xml`, which patches the bare **donor**
  defName `Insectomorph` in place — not a replacement `ThingDef`.
- Only the 4 `SoundDef`s were absorbed (2026-09-02 blanket 589-sound pass:
  `RSW_Pawn_Insectomorph_{Angry,Call,Death,Wounded}` in
  `infrastructure/state/facts/mlie_sound_defname_map.json`).
- No `swanimals/Insectomorph/` texture folder exists anywhere under
  SWBestiary — repo (`find src/RimStarWars/SWBestiary -ipath '*insectomorph*'`
  → only the 4 `.ogg` files) or live-deployed
  (`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/SWBestiary`
  → same, only the 4 `.ogg` files).
- `InsectomorphArtOverride` (idx 312, `loadAfter mlie.starwarsanimalcollection`
  only) is therefore the only loose PNG at
  `swanimals/Insectomorph/Insectomorph_{east,north,south}.png` and is live and
  correct today. Still queued for Wave C — flag it the same way as the 6
  above when it's actually ported.

### Dewback: CONFIRMED LIVE REGRESSION (same bug as pre-fix Anooba)

`RSW_Dewback.xml` is fully ported (`src/RimStarWars/SWBestiary/Defs/ThingDefs_Races/RSW_Dewback.xml`,
`texPath swanimals/Dewback/Dewback` for its live graphic). SWBestiary also
shipped its own donor-extracted `Dewback_east/north/south.png` at the
**exact** relative path `DewbackArtOverride`'s `About.xml` claims. Live
`ModsConfig.xml` (direct XML parse): `mandrake.rsw.dewbackartoverride` idx
**315**, `mandrake.rsw.swbestiary` idx **560** — SWBestiary loads after and
wins the same-path resolution, silently reverting the verified-live custom
Dewback art back to donor art, exactly as Anooba was before `5a8fc8c1c`.

**Evidence — md5sum, repo AND live-deployed copies (both matched each other,
so this is not a repo-only discrepancy, the game was actually showing it)**:

| facing | override (repo=live) | SWBestiary (repo=live) | same? | sizes (override / SWBestiary) |
|---|---|---|---|---|
| east | `0d692ea3cfa5d3adbd6dfd5aab01f942` | `9239fcfc0cbdf06989b14513203e1faa` | NO | 193997B / 19961B |
| north | `57e0be47fc55dc1f5e67b5ed17146666` | `ebb80ee2ae736fecbd1894d67bcd9b5e` | NO | 252179B / 15700B |
| south | `ac803dc2737d83a32f6e4c757f2da282` | `c9b6997c586dfeb90da7976448f4a5b0` | NO | 299561B / 16398B |

Live-deployed paths compared:
`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/DewbackArtOverride/Textures/swanimals/Dewback/Dewback_{east,north,south}.png`
vs
`/mnt/c/Program Files (x86)/Steam/steamapps/common/RimWorld/Mods/SWBestiary/Textures/swanimals/Dewback/Dewback_{east,north,south}.png`
— hashes matched their repo counterparts exactly, confirming the live game
is (was) reading the reverted donor art.

**Fix applied this pass (repo only — NOT deployed, NOT live-tested, NOT
committed/pushed)**, matching the exact Anooba/Dragonsnake pattern (delete the
colliding SWBestiary PNGs so the override's loose PNG becomes the sole file
at that path — no def edit needed since `texPath` is relative text resolved
across the whole loaded mod set, not owned by a specific mod folder):

- Deleted `src/RimStarWars/SWBestiary/Textures/swanimals/Dewback/Dewback_east.png`
- Deleted `src/RimStarWars/SWBestiary/Textures/swanimals/Dewback/Dewback_north.png`
- Deleted `src/RimStarWars/SWBestiary/Textures/swanimals/Dewback/Dewback_south.png`

Left untouched (correctly still SWBestiary's, outside the override's declared
scope): `Dewback_Dessicated.png` and all `DewbackW_*`/`*m.png` recolor-mount
variants.

**Still owed before this is fully closed**: `deploy_custom_mods.py --apply`
to push the deletion live, a bridge/quicktest spawn + screenshot to confirm
the override's Dewback art actually renders now, then `git commit`/`push`
the deletion together with this note. Left in `doing`, not closed, on
purpose — do not rimflow-close until deploy + live verification + commit
have happened.
