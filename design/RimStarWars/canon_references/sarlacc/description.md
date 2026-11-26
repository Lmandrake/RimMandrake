# Sarlacc

**defName**: `RSW_SarlaccSwimmer` (label "sarlacc swimmer"; `src/RimStarWars/Sarlacc/Defs/ThingDefs_SarlaccSwimmer.xml`,
the Sarlacc mod). It is our mobile sub-sand stage of the sarlacc family. Canon has no "sarlacc swimmer"; the nearest
canon forms are the **infant sarlaccs** (mobile) and the **adult sarlacc** (a buried pit mouth). No other in-game def
is a sarlacc.

## Sourced text (Wookieepedia)

Canon page `Sarlacc` (wikitext pulled through the API on 2026-11-26):

- Infobox: designation sentient (per *From a Certain Point of View: Return of the Jedi*, "My Mouth Never Closes");
  **3 meters wide** (the mouth; *Ultimate Star Wars*); **length 100 meters** (StarWars.com Encyclopedia, *Ultimate Star
  Wars*); skin colour **tan (of tentacles)**; distinctions **tentacles** and a **beak**; diet carnivorous.
- Range: Felucia, I'vorcia Prime, Pasaana, Tatooine, Vodran. Shares common ancestry with the **rathtar, blixus and
  vixus**: "all possessed a large maw, tentacles, and a voracious appetite"; the sarlacc became "the largest and least
  mobile of its relatives".
- Life cycle: a sarlacc **begins life as a spore** that travels great distances. A smaller male feeds parasitically on
  a female, grows to her original size, then bursts and releases millions of spores. Maturity comes after 30,000 years;
  then it **burrows nearly 100 meters below the surface**.
- Body: "its entire body was buried in sand, save its great, round mouth with a **beak** inside". It has **two
  mouths** (the second inside the body), **several appendages** branching off the buried body, and **many stomachs**.
  The mouth holds "rows of hundreds of **spear-like teeth**" that keep a victim from climbing out. Prey is overcome by
  toxic gas, then acid; digestion is said to take a thousand years (Jabba), though the acid scarred Boba Fett in hours.
- Predator: the **krayt dragon** eats sarlaccs alive and lairs in the cavity left behind.
- Xenobiologists debated whether it is an animal or a carnivorous plant.
- Image captions on the page: "Han Solo fleeing a pair of **infant sarlaccs** on I'vorcia Prime" (*Galaxy's Edge* 1);
  "The full body of a grown sarlacc" (*Star Wars Bestiary*); "The sarlacc's tongue" (*Return of the Jedi*).

Legends page `Sarlacc/Legends` (read for contrast; Legends only, never for the canon creature): an omnivorous
invertebrate; the "beak" is its tongue, with a stubby tentacle inside it; **no eyes or ears**, it senses through roots;
most of the body covered in **rigid plates**; **eight appendages** below ground and **three roots** at the end of the
body; it lures prey with scents.

## Visual brief

Four images, and they agree on the family look:

- `wookieepedia_pit_mouth_infobox.jpg` (canon infobox, *Book of Boba Fett* databank): a sand pit with a round,
  fleshy, pink-tan maw at the bottom; long, pale, **ridged tan tentacles** rise out of it like stalks; a dark **beak**
  sits in the throat. No eyes are visible.
- `wookieepedia_beak_tongue.jpg` (*Return of the Jedi*): close view of the beak/tongue, a ridged, horn-like,
  tan-and-purple structure inside a wet red throat lined with fleshy folds and tentacles.
- `wookieepedia_full_body_bestiary.jpg` (*Star Wars Bestiary* painting): the buried whole body. A segmented,
  arthropod-like trunk, tan-grey, hangs below a crown of short tentacles round the mouth (a ring of small eye-like
  knobs at the crown), with **many jointed, branching limbs** down its length and root-like tips at the bottom.
- `wookieepedia_infant_sarlaccs.jpg` (*Galaxy's Edge* 1, comic): two **infant sarlaccs** in the air chasing Han Solo.
  Each is a **segmented, plated, tan-brown grub body** about a person's size, with a **round mouth disc ringed with
  teeth** at the front and **whip-like tentacles** streaming from the mouth rim. These are the only canon picture of a
  sarlacc that moves, and they are the best target for our mobile swimmer.

What our creature should read as: a sarlacc-family hunter that moves under the sand. The infant body plan (segmented
plated tan body, round toothed mouth disc at the front, whip tentacles from the rim) plus the adult's beak in the
throat. Never a legged quadruped, never a worm with eyes.

Today's art is a **placeholder**: the def reuses the vanilla (Anomaly DLC) Devourer textures
(`Things/Pawn/Devourer/Devourer`, swimming and desiccated variants) by reference, so no repo file exists to copy as
`donor_current_sprite.png`. The def's own comment names the swimmer's real silhouette as still owed.

## Source URLs

- https://starwars.fandom.com/wiki/Sarlacc (canon; wikitext via
  `https://starwars.fandom.com/api.php?action=parse&page=Sarlacc&format=json&prop=wikitext`, 2026-11-26)
- https://starwars.fandom.com/wiki/Sarlacc/Legends (Legends; same API, 2026-11-26)

## Candidate images

- `wookieepedia_pit_mouth_infobox.jpg` — File:Sarlacc-BTM-DB.png (canon, infobox)
- `wookieepedia_beak_tongue.jpg` — File:SarlaccBeak-ROTJ.png (canon, film still)
- `wookieepedia_full_body_bestiary.jpg` — File:FullSarlacc-Bestiary.png (canon, *Star Wars Bestiary*)
- `wookieepedia_infant_sarlaccs.jpg` — File:HanFleesBabySarlaccs-GalaxysEdge1.png (canon, comic)

Each is a copy downscaled to at most 1024 px.

## Must show
- [ ] BODY PLAN (mobile stage): a segmented, plated grub-like body, no legs, as the infant sarlaccs have
- [ ] A round mouth disc at the front, ringed with inward spear-like teeth
- [ ] Whip-like tentacles streaming from the mouth rim
- [ ] COLOUR: tan to tan-brown body and tentacles (infobox: tan tentacles), with a pink-red wet interior to the mouth
- [ ] NOT: no visible eyes on the head, no legged quadruped stance

## Engine limits

- The adult's defining look is a **pit in the ground**, and a pawn cannot draw itself as terrain. Our creature is the
  mobile stage, so this limit does not block the swimmer; it would block an "adult sarlacc in a pit" pawn.
- The buried 100 m body is never seen; nothing to draw.

## ruling

(empty: the owner has not reviewed this entry. The ruling is his.)
