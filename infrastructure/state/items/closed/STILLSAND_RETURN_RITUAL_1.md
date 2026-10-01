# STILLSAND_RETURN_RITUAL_1 — the Return: the Sun-Debt ritual and the water ledger

From `STILLSAND_BEDAZZLE_SITTING_1` (closed 2026-09-30). Design source:
`design/Jawa/worldbuilding/biomes/stillsand_turn3_development_2026-09-30.md` §2.3, with the turn-4
rulings in `stillsand_bedazzle_cast_2026-09-30.md` §0. Owner, typed: *"I like your religious
implication of a ritual here."* Builds on the built Sun-Debt ideoligion (DeepDesertTribes).

## spec

1. **The Debt (Utinni tier).** A colony counter of water drawn on Stillsand maps: every still litre,
   canteen egg drunk, duumma sac and wringing (`STILLSAND_GLASS_LENS_CHAIN_1`). Sun-Debt believers
   get a mood line that worsens as the debt rises (*"We have taken too much"*), and the Deep Desert
   Tribes' goodwill follows it.
2. **The sand collects:** unpaid debt raises the weight of the krayt attack and the muurrok
   (`STILLSAND_EVENT_CREATURES_1`) and the sand-buster eruption. The ritual is a pressure valve on
   the biome's danger, not a buff.
3. **The Return (Ideology `RitualDef` on the Sun-Debt):** at a **debt stone** (`RM_DebtStone`,
   built on open sand in full sun, never in shade), believers pour a real quantity of water into the
   sand in a line toward the star. Opens on events, never by clock (no circadian ban): after a dune
   gale, after a krayt kill, or when the debt passes a threshold. Outcomes by quality: an hourbloom
   ring at the stone (shipped `RM_IncidentWorker_BloomBurst`); debt reduced; on a great outcome the
   sand gives back one buried cache near the stone (dunes engine reveal); on a bad one the pour wakes
   a siidda bloom, read as a debt refused. Letters may speak in the sarlacc's Sun-Debt stage labels
   (Seeker / Debtor / Collector / Paid).
4. **The sign that stays:** the pour leaves a darker "Return line" stain on the sand until the next
   gale; old tribal debt stones in caves (`STILLSAND_PRECIOUS_CAVES_1`, debt cave) have lines worn in.
5. **RM tier, no theology:** water poured on Stillsand sand blooms (the physics stands alone), and
   wet sand draws swimmers for a while (the rumble comes to the pour). No debt meter in the RM tier.
6. **Mod Settings:** toggle the Debt, its incident weighting, and bloom-on-pour.

## criteria

- A Sun-Debt colony on a Stillsand quicktest accrues debt from a still and can run the Return after
  a dev-fired gale; a good outcome lowers the debt and blooms the ring.
- Without the Utinni layer, pouring water on Stillsand sand still blooms and no debt UI appears.
