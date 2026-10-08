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
Only one candidate image was found (`wookieepedia_alienarchive.jpg`, credited
to *Star Wars: Alien Archive*) — a stylized game-guide illustration in
flight, wings fully spread:

- **Body/plumage**: warm **golden/tan-brown** feathers overall, matching the
  "golden-colored" text exactly, with **dark brown-to-black barred/banded
  markings** across the underside of both wings and a dark patch across the
  chest/belly.
- **Head**: a **bald, blue-gray, vulture-like head and upper neck** (no
  feathers) with a hooked, reddish-tipped beak shown open — this reads much
  more vulture/condor-like than songbird-like, despite the "whisper" naming
  suggesting something delicate.
- **Legs/feet**: blue-gray legs and talons matching the head color, four
  sharp curved claws per foot, visible and prominent in the flight pose.
  Long, thin feathered tail trailing behind.
- **Silhouette**: broad swept wings, lean raptor-proportioned body — reads
  as a bird of prey silhouette; the wiki text says it hunts and eats fish and weeds
  and does not describe it as a scavenger, despite the vulture-like head.

**Net read**: golden-tan plumage with dark wing banding, bald blue-gray
vulture-style head and legs, red beak tip — a raptor/vulture-shaped bird,
not a songbird. Single-source image, but it agrees closely with the sourced
text's "golden-colored" description, so treat it as reliable.

## Must show
- [ ] Golden/tan-brown body plumage overall
- [ ] Dark brown-to-black barred/banded markings across the underside of both wings and a dark chest/belly patch
- [ ] Bald, blue-gray, vulture-like head and upper neck (no feathers on the head), with a hooked beak carrying a reddish tip
- [ ] Blue-gray legs and talons, with four sharp curved claws per foot
- [ ] Broad swept wings on a lean, raptor-proportioned body — a bird-of-prey/vulture silhouette, not a songbird

## Engine limits
none known — only one candidate image exists for this species and no donor sprite could be obtained at all (creature art ships packed in Unity AssetBundles, not loose files), so there is nothing on disk to test against a rendering-pipeline constraint.

## Source URLs
- https://starwars.fandom.com/wiki/Whisperbird (current canon, one-word
  title — the lore-only Chiss board-game/naming reference; wikitext pulled
  2026-09-13)
- https://starwars.fandom.com/wiki/Whisper_bird (current canon, two-word
  title — the actual golden bird species; wikitext pulled 2026-09-13)
- https://static.wikia.nocookie.net/starwars/images/1/19/Whisper_Bird-Alien_Archive.jpg
- Donor mod `mlie.starwarsanimalcollection` — `About.xml` confirms
  packageId `Mlie.StarWarsAnimalCollection`, GitHub mirror
  `github.com/emipa606/StarWarsAnimalCollection`; its `Textures/` folder
  contains only an empty `UpdateInfo` subfolder (creature art ships packed
  in AssetBundles, not loose files) — same finding as the `pekopeko` and
  `wyyyschokk` passes. No workshop preview screenshot specifically labeled
  Whisperbird was located this pass.

## Candidate images
- `wookieepedia_alienarchive.jpg` — flying whisper bird, golden-tan
  plumage with dark banded wing markings, bald blue-gray vulture-like head
  with red beak tip, blue-gray taloned legs. **Only candidate found; best
  and only color/body-plan reference.**
- **No donor-mod (`mlie.starwarsanimalcollection`) sprite included** — same
  AssetBundle-packaging finding as prior waves; revisit if the mod is ever
  installed locally or a labeled preview surfaces.
- No additional candidate images found this pass beyond the one above —
  searches for the current-canon `Whisperbird` (Chiss board-game piece) also
  turned up no illustrations, consistent with that article having no
  physical description to illustrate.

## ruling
(empty — owner has not reviewed this creature yet)
