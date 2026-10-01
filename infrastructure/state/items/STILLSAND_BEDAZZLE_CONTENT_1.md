# STILLSAND_BEDAZZLE_CONTENT_1 — make the built Stillsand visible, and build its ruled cast

From the Stillsand bedazzle sitting (`STILLSAND_BEDAZZLE_SITTING_1`, closed 2026-09-30). Sources:
`design/Jawa/worldbuilding/biomes/stillsand_bedazzle_review_2026-09-29.md` §2 "Art status per
cast member", §5 "Ruled-but-unbuilt debt" and §7 "Art already generated"; the turn-3 development
doc `stillsand_turn3_development_2026-09-30.md` §5 rank 0; the cast bible
`stillsand_bedazzle_cast_2026-09-30.md`. Mod: `src/RimMandrake/Stillsand/` (`mandrake.rm.stillsand`,
shipped inside `RimMandrake.Biomes`). This is wiring and defs whose outcome an atlas proves.

## spec

1. **Wire the six finished-but-unwired render sets.** Each def's texPath resolves nowhere today:
   `rmmirrorgiant_v1` → `RM_Oommok`, `rmdusthusk_v1` → `RM_Siidda`, `rmshademite_v1`/`_v2` →
   `RM_ShadeMite`, `RM_Ruukka_*` → `RM_Ruukka`, `RM_Oorrik_*` → `RM_Oorrik`,
   `RM_SandBusterMound_south` → `RM_SandBusterMound` (off vanilla `Hive`).
2. **Build the nine ruled fill-out defs** (owner ruled the art sheet 2026-09-27; use the `_b` redo
   set where one exists): soorrak (`_b`), gaanok (`_b`), loomma (`_b`), kneel ollim (`_b`),
   liikka, duumma, veessa, hourbloom, glasscrust. Design rows:
   `design/Jawa/worldbuilding/biomes/stillsand_roster_fillout_2026-09-27.md`.
3. **Wire the new art this sitting commissioned** (cast bible §6, rows tagged CONTENT): `RM_Vozzik`,
   `RM_Vekka`, `RM_Drazzik`, `RM_Nizzek`, `RM_Guzzka`, `RM_Aurrok` (off Alpha Animals'
   `AA_SpinedGow` texture, so the free mod has no Alpha Animals dependency) and the `RM_Biosilica`
   icon.
4. **Copy the borrowed textures in.** `RM_LightPipeNub`, `RM_Ollim` and `RM_OllimWood` resolve via
   SWBestiary's `RSW_` texture paths; copy those PNGs into `Stillsand/Textures` so the free mod
   stands alone (Q11a).
5. **Small ruled rows with no carrier (review §5.4):**
   - **vaalok**, the free-tier pack giant (Q11), so the standalone mod generates traders. Its art
     is not commissioned yet; file the def on a placeholder and queue the art with `fill_queue.py`
     after a dedup check.
   - **qorrax**: move `RM_Qorrax` inline into the RM mod (Q1), off the Utinni patch route.
   - **eemmok / shade mite**: the shipped label is the English "shade mite"; the ruled shipping
     name is eemmok. Rename it (label and description; keep the defName unless a save depends on it).
   - **vozzik**: drop the SWBestiary comp it carries in the free tier.
6. **Tier move of the sand catches (Q11a):** `RSW_DuneCrawler` and `RSW_GlassPearl` are invented,
   so they become `RM_DuneCrawler` and `RM_GlassPearl` in the RM tier. `RSW_SandStalker` stays RSW
   until the owner rules otherwise. The fishing hookup itself is `STILLSAND_SAND_SWIM_KIT_1`'s job.
7. **The piinnok is NOT this item's.** It was admitted 2026-09-30 and is the first member of
   `WATCHER_CREATURES_MOD_1`, which owns its def, behaviour and art. This item adds its
   `RM_Stillsand` roster row only once that def exists.

## criteria

- A Stillsand quicktest atlas shows no magenta and no donor texture on any free-tier def, and the
  free mod loads with `sarg.alphaanimals` and SWBestiary both absent.
- The nine fill-out defs spawn on a Stillsand quicktest map.
- `RM_Qorrax`, `RM_DuneCrawler` and `RM_GlassPearl` resolve from the RM mod; no `RSW_`-prefixed
  def remains for an invented creature or catch.
