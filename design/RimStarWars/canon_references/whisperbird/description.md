# Whisperbird

**defName**: `Whisperbird` (third-party, mlie.starwarsanimalcollection, not
vendored — the mod's 1.6 release packs creature art inside Unity
AssetBundles rather than loose PNGs; see "donor art" note below)

## Sourced text (Wookieepedia)
Two separate Wookieepedia articles share almost the same name, and only one
of them is an actual describable animal — this is the key finding for this
creature:

- **`Whisperbird`** (current canon, one word, sourced to the *Thrawn
  Ascendancy* trilogy): a "creature known to the Chiss Ascendancy" with
  unspecified biology; it has no usable physical description. It is
  represented as a piece in the Chiss strategy board game *Tactica*, and is
  the namesake of a Chiss light cruiser (Ar'alani's *Whisperbird*) and a
  figure of speech: in *Lesser Evil* Thrawn explains that Ba'kif sacrificed
  his "nightdragon" (Thrawn) to the Syndicure to keep his "whisperbirds",
  those who served under the senior captain. The article gives **zero
  physical description** — no size, color, body plan, or habitat. Wookieepedia
  files it under "Creatures of unspecified biology." The wiki notes only that
  it shares a name with the Yavin 4 whisper bird; their identity is not
  established. https://starwars.fandom.com/wiki/Whisperbird
- **`Whisper bird`** (current canon, two words, sourced to *Ultimate Star
  Wars*, *Star Wars: Alien Archive*, *Star Wars Bestiary Vol. 1*, and
  others): a real, describable species — a **golden-colored** bird native
  to the rainforests of the moon **Yavin 4** (also found on Coruscant and
  Null). Non-sentient. Diet of fish and weeds. Distinct low-pitched call;
  named "whisper bird" for its ability to fly silently, which it uses while
  hunting. Roosts in massassi trees in flocks; preyed on by packs of
  stintaril rodents while roosting. A cartographer's shuttle was nicknamed
  *Whisper Bird* for its long bronze wings and perched landing stance.
  Also found on Coruscant and Null; travels silently in flocks (*Before the
  Awakening*). First named in the 1995 Legends novel *Young Jedi Knights: Heirs
  of the Force*; confirmed canon by *Ultimate Star Wars* (2015). First canon
  appearance: *Star Wars Battlefront II*. https://starwars.fandom.com/wiki/Whisper_bird

Given a third-party **animal collection** mod would be adding an actual
creature (not a lore-only board-game-piece reference with no body plan),
**`Whisper bird` is treated as the intended source creature** (an editorial inference, not proof of the donor's intent) for this
folder, and this file researches and illustrates that species. The
one-word/two-word naming collision is flagged here so a future pass does not
mistake the lore-only Chiss reference for a design target.

## Visual brief
**Owner ruling 2026-10-08 (verbatim): "That's realistic, not these cartoon versions you keep using. Replace the canon with something more realistic. The web is full of them."**

The hatched *Alien Archive* illustration (`wookieepedia_alienarchive.jpg`) was deleted 2026-10-08. The target is now
**`wookieepedia_bf2_render.png`**, the photoreal *Star Wars Battlefront II* (canon, video game) model of the bird in
flight. `wookieepedia_woswfg_legends.jpg` is a naturalistic Legends painting from *The Wildlife of Star Wars* and
disagrees on wing type (below).

From the Battlefront II render (realistic):
- **Plumage**: warm golden-tan to honey-brown feathers over the body and long broad wings, with soft darker brown
  shading along the feather tracts and paler tips; the coat is fairly even — **no strong black barring** is visible.
- **Head and neck**: a bald, blue-grey, vulture-like head and a long thin bare blue-grey neck, held stretched forward
  in flight; a long slim pale orange-tan beak.
- **Tail**: a very long, thin, trailing tail streamer of golden feathers, longer than the body.
- **Silhouette**: a lean, long-necked, long-winged soaring bird, closer to a heron or crane than a stocky raptor.
- **Disagreement (loud)**: the deleted *Alien Archive* drawing showed heavy dark banding under the wings, a dark belly
  patch, a hooked red-tipped beak and big blue-grey talons; the realistic render shows none of that banding, a
  slimmer straighter beak and the legs tucked out of sight. Follow the render.
- **Legends painting** (`woswfg_legends`): same bald blue-grey head and long neck, but **pterosaur-like membrane
  wings** in bright orange-yellow and an open toothed beak. It is Legends; use it for head and neck only, never the
  wings.

## Must show
- [ ] Warm golden-tan to honey-brown feathered body and long broad wings, without heavy black barring
- [ ] Bald blue-grey vulture-like head on a long, thin, bare blue-grey neck stretched forward
- [ ] Long, slim, pale orange-tan beak
- [ ] A very long, thin, trailing golden tail streamer, longer than the body
- [ ] Lean, long-necked soaring silhouette (heron/crane-like), not a stocky raptor
- [ ] Realistic rendering: natural feather texture and soft natural lighting, no outlines, no ink hatching or cartoon shading

## Engine limits
none known — no donor sprite could be obtained at all (creature art ships packed in Unity AssetBundles, not loose files), so there is nothing on disk to test against a rendering-pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Whisperbird (current canon, one-word
  title — the lore-only Chiss board-game/naming reference; wikitext pulled
  2026-09-13)
- https://starwars.fandom.com/wiki/Whisper_bird (current canon, two-word
  title — the actual golden bird species; wikitext pulled 2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/7/75/WhisperBird-BFII.png
- https://static.wikia.nocookie.net/starwars/images/0/08/WhisperBird-woswfg.jpg
- Donor mod `mlie.starwarsanimalcollection` — `About.xml` confirms
  packageId `Mlie.StarWarsAnimalCollection`, GitHub mirror
  `github.com/emipa606/StarWarsAnimalCollection`; its `Textures/` folder
  contains only an empty `UpdateInfo` subfolder (creature art ships packed
  in AssetBundles, not loose files) — same finding as the `pekopeko` and
  `wyyyschokk` passes. No workshop preview screenshot specifically labeled
  Whisperbird was located this pass.

## Candidate images
- `wookieepedia_bf2_render.png` — canon page `Whisper bird`; *Star Wars Battlefront II* photoreal video-game model in flight. **Primary reference.** File `WhisperBird-BFII.png` — https://static.wikia.nocookie.net/starwars/images/7/75/WhisperBird-BFII.png/revision/latest?cb=20260920153411
- `wookieepedia_woswfg_legends.jpg` — Legends; *The Wildlife of Star Wars: A Field Guide* naturalistic painting, two birds in flight and a head study. Head/neck only; its membrane wings disagree with canon. File `WhisperBird-woswfg.jpg` — https://static.wikia.nocookie.net/starwars/images/0/08/WhisperBird-woswfg.jpg/revision/latest?cb=20070124223418
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — creature art ships packed in AssetBundles.

## ruling
(empty — owner has not reviewed this creature yet)
