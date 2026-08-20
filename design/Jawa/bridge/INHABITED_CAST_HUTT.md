# `Inhabited` — cast 01: the Hutt Cartel

_Authored 2026-08-19. **Rewritten 2026-08-20 after the owner rejected the first pass.**_

## 🔴 What this is, and what the first attempt got wrong

**We are not writing memorable STORIES. The story is what the player makes across repeat
encounters — we cannot write it and should stop trying.** What we write is people who are
**MEMORABLE THEMSELVES**: standout, unique, immediately striking. The thing that makes
someone go *"whoa"* and recognise them again six months later.

⛔ **The first pass wrote quiet, understated, literary people** — unremarked tragedies,
withheld detail, restraint. That was a wrong inference from the research finding *"we can
only invite attachment"*. **Inviting attachment means being VIVID, not subtle.** Nobody
remembers the man who said nothing; they remember the one who is *impossibly stupid,
dangerously so.*

**The owner's own examples, which are the target register:**
> *"A gimpy walk and a voice like a razor, she drinks herself into a stupor if left alone."*
> *"He's fast, he's lean, and he's impossibly stupid. I mean just... dim. Dangerously so."*

⏱️ **This is a STOP-GAP.** Once in-game LLM support exists these are generated on the fly.
So: do a good job, do not gold-plate, move on.

## The format — it is a PAWN, not a portrait

```
Name  ·  race  ·  gender  ·  age
traits:     real TraitDefs, and the hook must MATCH them
childhood:  one line
adult:      one line
hook:       1-2 sentences. Physical + manner + the flaw that will cause trouble.
```

🔑 **The hook and the traits must agree.** *"Drinks herself into a stupor"* is only worth
writing if the pawn actually carries `DrugDesire: ChemicalFascination`. A hook the mechanics
do not back is a lie the player will catch.

⚠️ **Verified TraitDefs** (RimSage, 2026-08-20): `AnnoyingVoice` · `CreepyBreathing` ·
`Abrasive` · `Psychopath` · `Cannibal` · `Masochist` · `Jealous` · `Ascetic` · `Gourmand` ·
`TooSmart` · `SlowLearner` · `FastLearner` · `GreatMemory` · `Brawler` · `TorturedArtist` ·
`Transhumanist` · `BodyMastery` · `VoidFascination` · `Delicate` · `NaturalMood` ·
`ShootingAccuracy` · `Beauty`. ⛔ **Never `Pyromaniac`** — measured: it appears in players'
disaster anecdotes and never in their affection ones. ⚠️ **Alcoholism is not a trait** — it
is `DrugDesire` plus an addiction hediff.

---

## KESSEK REFINERY

**Bruk Oleen** · Ugnaught · m · 101
`traits: Abrasive, GreatMemory, Ascetic`
childhood: won the right to his trade at twenty, tusks against his own cousin.
adult: eighty-one years on the same cracking tower.
> Four feet of grievance in a leather apron. He remembers every mistake you have ever made
> on his floor and will recite them in order, and he is never once wrong, which is worse.

**Ferrin Oleen** · Ugnaught · m · 99
`traits: DrugDesire(ChemicalFascination), Gourmand, AnnoyingVoice`
childhood: lost the duel. Kept the job. Never got over either.
adult: clears the settling sump, badly drunk, extremely well.
> He'll tell you about the breath-hold record inside four minutes of meeting you, in a voice
> like a hinge, and he'll tell you again tomorrow. Leave a bottle where he can see it and
> you lose him for two days.

**Tenno Vurr** · Chagrian · m · 44
`traits: Ascetic, Abrasive, GreatMemory`
childhood: saltwater took his sense of taste before he was ten, as it takes every Chagrian's.
adult: runs a refinery mess by smell alone and is better at it than anyone has explained.
> Tongue out, flick, adjust — he tastes your dinner with his nose and hands it over without
> looking. He eats nutrient capsules standing up in nine seconds. He has never once sat down
> to a meal in his life and finds the idea faintly obscene.

**Poul Adden-Adden** · Ortolan · m · 23
`traits: SlowLearner, Gourmand, NaturalMood(Sanguine)`
childhood: pushed out of the family unit at seven and traded to a household that wanted a
musician.
adult: junior stockman, convinced he is management-track.
> He's blue, he's round, he introduces himself with both names every single time, and he is
> under the immovable impression that he is being observed for promotion. He took this job
> for the meals. He would take a worse one for better meals and will tell you so proudly.

**Margrave Sarrick** · Togorian · m · 38
`traits: Brawler, Ascetic, Beauty(Beautiful)`
childhood: nomad. Rode a flying reptile before he could read.
adult: eleven years offworld on a gate, reading every manifest that passes, looking for one
name.
> Seven feet of silent cat in a doorway, and he has never drawn on anyone here. He made the
> scimitar on his back himself and has twice refused a year's passage for it. Ask him why
> he's on this rock and he will simply stop talking to you.

**Jat Hessik** · Rodian · m · 31
`traits: NaturalMood(Depressive), FastLearner, Delicate`
childhood: fled a clan feud and will not say which clan.
adult: best pipe-fitter on the tower. Works nights. Cold-blooded.
> Wrapped in three stolen thermal layers and shaking by the fourth hour, because he is
> cold-blooded and they gave him the night gang as a joke six years ago. He is better than
> all of them. He has never asked to be moved.

**Ossuk Rell** · Muun · m · 52
`traits: Abrasive, TooSmart, Jealous`
childhood: failed the third examination at nineteen. Will not say which one.
adult: keeps a perfect book on a tower beneath him, and runs the little oil shop at the gate.
> Two metres of pale disapproval with three hearts, two of which he consciously runs hot to
> keep his hands warm, and he is mortified to be seen doing it. He is visibly appalled by
> everyone here. He is also the only one who shows up when Ferrin is bad.

---

## DOCK NINE

**Adda Wesh** · human · f · 41
`traits: Abrasive, GreatMemory, DrugDesire(ChemicalInterest)`
childhood: dock brat. Learned manifests before letters.
adult: the only loadmaster permitted to tell a Hutt factor he is wrong.
> A gimpy walk from a crate that came down in '48 and a voice like a rasp on tin. She drinks
> the night gang under the table twice a season and reminds them of it for the other
> fifty-one weeks. Two promotions lost to her mouth and she'd lose a third tomorrow.

**Gand** · Gand · m · 60ish
`traits: Ascetic, GreatMemory, CreepyBreathing`
childhood: earned a surname young. Witnessed, entered, real.
adult: gave it back after one consignment went to the wrong world.
> He has no name. He speaks of himself in the third person and signs every docket "Gand",
> and when you ask him to write it properly he writes it the same. He sleeps two hours in
> six days. He does not breathe like anything you have met.

**Buba Nokk** · Herglic · m · 35
`traits: NaturalMood(Sanguine), Gourmand, SlowLearner`
childhood: hauled freight for an uncle who bet the family's stake and lost it.
adult: does the same, on his own wages, every payday, at the same table.
> Two and a half metres of apologetic whale who cannot fit through the personnel door and
> must be let in through the freight hatch, every shift, by someone. He clears his blowhole
> before saying anything important — a great wet *hauum* that silences the shed — and then
> says something like "the small crates go on top."

**Sen Ilva** · Selkath · f · 29
`traits: Kind, TooSmart, Delicate`
childhood: raised on kolto rigs her people no longer own.
adult: dock medic, in a suit that hisses.
> You hear her before you see her: the misting vents cycle every eleven seconds and she has
> never fixed them. She will not approach you unless you signal her first — approaching the
> unwilling is a rudeness she physically cannot commit — so half the injuries here reach her
> late and she knows it and cannot stop.

**Orrin Kwaad** · human · m · 47
`traits: Psychopath, NaturalMood(Sanguine), GreatMemory`
childhood: unremarkable, by every account including his own.
adult: gate scanner. Takes forty credits to look at a manifest for slightly less time.
> Forty. Not four hundred — forty, for six years, never once raised, which unsettles people
> more than the theft does. He remembers your children's names and asks after them by name
> and feels precisely nothing while doing it.

**Tikka Vosh** · Rodian · f · 34
`traits: GreatMemory, Ascetic, NaturalMood(Pessimist)`
childhood: born to a house that is owed a debt by another house.
adult: sorter, day gang, wears a scent-damper and says it is for headaches.
> It is not for headaches. She has known exactly who the night-shift fitter is since her
> third week and has said nothing for two years. She eats alone, in sight of the gate road,
> at the hour the night gang walk up.

---

## THE LEDGER HOUSE

**Factor Ummu Sekk** · human · f · 60
`traits: Psychopath, TooSmart, Ascetic`
childhood: nothing on record and nothing volunteered.
adult: holds the paper on most of this list.
> She is small, she is sixty, and she speaks so quietly that everyone leans in. She has never
> raised her voice inside this building and has twice had someone carried out of it. *"Pay,
> and you are family. Do not pay, and you are inventory. There is no third column."*

**Denno Fash** · Ithorian · m · 71
`traits: Kind, Ascetic, SlowLearner`
childhood: raised under a law that says plant two for every one taken.
adult: assessor. Will not put a value on anything that came out of a killing.
> A translator collar that mistimes by half a second, so every price he gives arrives after
> his mouth has stopped. He keeps a seedling tray in a back office on a world where nothing
> grows, and starts a new one every season, and has never once got one to transplant.

**Tobb the Ledger's Boy** · Jawa · m · ~14
`traits: GreatMemory, NaturalMood(Sanguine), Nimble`
childhood: four hems, two of which he let down himself, badly.
adult: runs paper between three houses and overcharges on a sliding scale of his own
invention.
> Two glowing eyes and a smell that arrives first. He is a thief, is known to be a thief,
> and considers this an excellent professional reputation. He will explain at length, to
> people who did not ask, that the insects living in his hood are correct and that you are
> the one doing it wrong.

**Iss the Quiet** · Anzati · m · unknown
`traits: Ascetic, GreatMemory, CreepyBreathing`
childhood: given no name, so he could take one that matched wherever he ended up.
adult: house factotum. Second-best pair of hands in the building at every task and best at
none.
> Payroll has him at four years. The old man on the door has sat there nineteen and is
> fairly sure it is longer. He is agreeable, unremarkable, and instantly forgettable in a
> way that survives being pointed out to you. He has no pulse.

**Yesh Adden** · Ortolan · m · 40
`traits: Gourmand, Kind, Delicate`
childhood: traded to a kitchen at seven, like all of them.
adult: fourth kitchen he has run; first where anyone thanked him.
> He cooks with his hands buried in the food because his fingertips do the tasting, which
> the human staff have privately agreed never to mention. The pump gallery below hurts him —
> his ears hear into the subsonic — and he has worked above it for eleven years and told
> nobody.

**Old Nabb** · human · m · 68
`traits: SlowLearner, NaturalMood(Sanguine), AnnoyingVoice`
childhood: not worth recounting, and he will recount it.
adult: sits on a stool by the door. Nineteen years.
> He is not a guard and would be no use as one. His entire function is that people arriving
> to beg for time see a bored old man first instead of Ummu, and it takes something out of
> them. He knows this. He has one story, about grain, and it is not a good story.

---

## Notes

- **Every hook is backed by a trait.** Ferrin's bottle is `DrugDesire(ChemicalFascination)`;
  Adda's rasp is `AnnoyingVoice` territory; Orrin's warmth over nothing is `Psychopath`;
  Buba's *hauum* is species, and his payday is why he has none.
- **The physical comes first**, per the craft rule that tics are built from discomfort, not
  personality: the hissing suit, the shaking Rodian, the whale who cannot fit through a door.
- ⛔ **No Pyromaniacs.**
- 🔑 **The relationships are still there but they are no longer the point** — Bruk and
  Ferrin, Jat and Tikka, Iss and Nabb. They are what the player discovers on the SECOND
  meeting. The hook is what makes them look twice in the first place.
