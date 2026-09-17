# Canon appearance dossier — 13 species, before any appearance fix

**Written 2026-09-17, Mac laptop. No definition file was changed. No `## north star` section was touched.**

This exists because you said the downloaded canon has errors in it and you want to verify by
search before authorising an appearance change. So every entry below tells you **three separate
things** and keeps them apart:

- what the def on disk actually says (file + line, read this session — **CONFIRMED**);
- what our canon entry says, **quoted**, plus the source *the entry itself names*;
- whether that source is one you can actually check.

**Where our library is the only authority for a claim, it says so.** Three of the audit's claims
did not survive contact with the library and are marked ⛔ **AUDIT WRONG**.

🔴 **Read the top five, then stop if you want.** They are the ones with a named work per colour
value. Everything below #8 is progressively weaker evidence, and #13 (Umbaran) rests on our own
reading of a picture.

---

## The table

| # | Species | What ships (measured) | What canon says | Source strength | Defect class |
|---|---|---|---|---|---|
| 1 | **Ithorian** | `Skin_PaleRed`, `Outland_Skin_DeepSage`, `Outland_Skin_DeepAzure`, `Outland_Skin_DeepBrown`, `Outland_Skin_Brown` (xml:916–920) | infobox skin **brown / green / light brown / orange**, one named work each | `SOURCED` | **data fix** (drop blue+pale-red, add orange) **+ engine limit** (face untintable) **+ RIG LIMIT** (neck) |
| 2 | **Bith** | `Skin_Melanin3` — sole skin gene (xml:162) | infobox **"cream, green, orange, pink, or white"**; Legends "pale pink, red, yellow, or (rarely) green" | `SOURCED` | **data fix** (body) **+ engine limit** (2,194 baked-red px at the mouth, face untintable) |
| 3 | **Zygerrian** | `Skin_DeepRed`, `Outland_Skin_Red`, + brown/grey ×5 (xml:2261–2267); head is `RSW_CatharHead` (xml:2259) | infobox skin **"Light"** — a single entry, in **both** canon and Legends | `SOURCED` | **engine limit** — Cathar head is `useSkinShader:false`, so no skin gene reaches the face at all |
| 4 | **Chadra-Fan** | **no skin gene**; `Furskin` (xml:286) | infobox skin **gray** / **light** / **tan**, one named work each | `SOURCED` | **data fix** |
| 5 | **Abednedo** | ⛔ **eight** skin genes: `Skin_Orange`, `Outland_Skin_PaleOrange`, `Skin_Melanin5/1/3`, `Outland_Skin_PalePink`, `Outland_Skin_Brown`, `Outland_Skin_PaleBrown` (xml:33–40) | infobox **brown, cream, gray, orange, pink, tan**, one named work each | `SOURCED` | ⛔ **AUDIT WRONG** — not missing; missing only *grey/cream*. And it is an **engine limit**: face untintable |
| 6 | **Ewok** | **no skin gene**; `Furskin` + 9 hair genes, darkest `Hair_DarkBrown` (xml:542–554) | infobox skin **brown**, hair **black**; body "brown and black as the most common colors" | `SOURCED` | ⛔ **AUDIT MIS-FRAMED** — the gap is a black **hair/fur** gene, not skin. **data fix** |
| 7 | **Lasat** | `RSW_CatharHead` (xml:1153); `RSW_Skin_Lavender`, `RSW_Skin_SlateBlue` | infobox skin **light brown, gray, purple**; *"NO TWO LASAT HAD THE SAME STRIPING"* | `SOURCED` | **engine limit** (striping; Cathar face untintable) **+ RIG LIMIT** (digitigrade legs) |
| 8 | **Ortolan** | `RSW_Head_kubaz` (xml:1462); `Skin_Blue` + `Outland_Skin_PaleAzure` | infobox skin **blue** (*Return of the Jedi*) | `SOURCED` | **skin already correct.** Head = **new art** (Kubaz mask *is* tintable) |
| 9 | **Mimbanese** | `RSW_Head_Devolved` → **Tusken Raider art** (xml:1187); `Skin_DeepRed` | *"lurid, red skin"*; sourced red / brown / grey | `SOURCED` | **skin already correct.** Head = **new art** (Tusken mask *is* tintable) |
| 10 | **Ugnaught** | **no skin gene** (xml:2049–2071) | infobox **"varying shades of pink"** — 🔴 **but the canon infobox IMAGE is dun grey-brown** | `UNCHECKABLE` (pink is second-hand via an unfetched Databank page) | **data fix** — but *which* colour is genuinely contested |
| 11 | **Chagrian** | `Outland_Skin_DeepOrange`, `Skin_Orange`, `Skin_Blue`, `Outland_Skin_DeepAzure` (xml:314–317) | infobox skin **blue only**; blue is evolved radiation resistance under an unstable sun | `SOURCED` but **single-source** (*Lead by Example*), article flagged incomplete by the wiki | **data fix** (drop the two oranges) |
| 12 | **Nelvaanian** | `RSW_BothanHead` (xml:1407); `RSW_Skin_SlateBlue` | **canon article is a stub with an EMPTY infobox.** Skin "blue" is **Legends-only** | `UNCHECKABLE` in canon; Legends-sourced | **engine limit** (Bothan face untintable) + head = **new art** |
| 13 | **Umbaran** | `Skin_LightGray` (xml:2091), `Head_Gaunt` (vanilla) | infobox **"Pale and bluish"**. The **lavender-violet** target is 🔴 **our own reading of an image** | `SOURCED` for "pale and bluish"; `UNSOURCED` for lavender | **data fix** |

`xml:` = `src/RimStarWars/StarWarsRaces/Defs/XenotypeDefs/RimMandrakeXenotypes.xml`

---

## The one measurement that changes what "fixing this" means

🔴 **36 of 138 `HeadTypeDef` blocks in
`src/RimStarWars/StarWarsRaces/Defs/HeadTypeDefs/SW_HeadTypes.xml` carry
`<useSkinShader>false</useSkinShader>`.** MEASURED this session by parsing the file, not grepped.
Among them are **every borrowed or racial head used by six of your thirteen**:

| Head | line | worn by |
|---|---|---|
| `RSW_Abednedo_Normal` | 16 | Abednedo |
| `RSW_Bith_Normal` | 57 | Bith |
| `RSW_Bothan_MaleNormal` / `FemaleNormal` | 84 / 71 | **Nelvaanian** |
| `RSW_Cathar_MaleNormal` / `FemaleNormal` | 111 / 97 | **Lasat**, **Zygerrian** |
| `RSW_Ithorian_Normal` | 461 | Ithorian |

And I measured the mask files themselves (PIL, opaque pixels only):

| texture | size | mean chroma | max chroma | verdict |
|---|---|---|---|---|
| `Heads/Abednedo/Normal_south.png` | 512² | 0.0 | **0** | pure greyscale |
| `HeadType/ithorian/Male_Ithorian_south.png` | 512² | 0.0 | 2 | pure greyscale |
| `Heads/Cathar/Male_Head_south.png` | 512² | 0.0 | **0** | pure greyscale |
| `Heads/Bothan/Male_Bothan_south.png` | 512² | 0.0 | **0** | pure greyscale |
| `Heads/Bith/Normal_south.png` | 512² | 3.4 | **94** | **2,194 coloured pixels** |
| `HeadType/kubaz/Male_Kubaz_south.png` | 512² | 0.3 | 3 | greyscale — **and NOT in the false-shader list** |
| `HeadType/Sov_tusken/HeadSandM_south.png` | 512² | 0.5 | 2 | greyscale — **and NOT in the false-shader list** |

**What this means, if `useSkinShader:false` does what the library says it does:** for Abednedo,
Bith, Ithorian, Lasat, Nelvaanian and Zygerrian, **editing the skin gene changes the body and
leaves the face grey.** Those are not data fixes. They are engine limits.

⚠️ **Honest limit on that conclusion.** The *flag's presence* is CONFIRMED — file, line, and
byte. What the flag *does at render time* is a claim about the `TabulaRasa` /
`neronix17.toolbox` mod's code, which is **not in this repo**, and RimSage does not connect on
this laptop. `AGENT_BRIEF.md` itself writes "⚠️ **Needs in-game confirmation of what actually
renders.**" So: **UNCERTAIN**, and one quicktest settles it. I am not going to launder it into a
fact.

🔴 **`AGENT_BRIEF.md`'s own engine-limits list is wrong by omission.** It says the false-shader
problem is "Known on Bothan, Gungan, Duros and Twi'lek heads" — four. The measured figure is
**36**, including Cathar, Bith, Abednedo, Ithorian, Cerean, Iktotchi, Kaminoan, Herglic, Nikto,
Pyke, Quarren, Selkath, Trandoshan, Wookiee, Geonosian, Mon Calamari, Aqualish and four abstract
bases. That understatement is why four of the entries below say "Engine limits: none known" when
they should not.

---

# 1. Ithorian — `SOURCED`, and the strongest citation set in the batch

**1. What ships.** `RSW_RimMandrakeIthorian`, xml:898.
Skin genes at xml:916–920: `Skin_PaleRed`, `Outland_Skin_DeepSage`, `Outland_Skin_DeepAzure`,
`Outland_Skin_DeepBrown`, `Outland_Skin_Brown`. Head gene `RSW_IthorianHead` (xml:913) →
`RSW_Ithorian_Normal` (SW_Genes.xml:2743 → SW_HeadTypes.xml:461).
Also measured, not in the audit: **`nameMaker` is `RSW_KoTOR_NamerSullustan`** (xml:905) —
Ithorians are drawing Sullustan names.

**2. What canon says.** `design/RimStarWars/canon_references/ithorian/description.md`, quoted
verbatim:

> "Infobox: skin **brown** (Databank "byph"), **green** (*Rebels: Recon Missions*), **light
> brown** (*Star Wars Lightsabers*), **orange** (*Rebels*, "The Future of the Force")"

and the finding, verbatim:

> "🔴 **`Outland_Skin_DeepAzure` (blue) is unsourced**, and **orange — which IS sourced**
> (*Rebels*, "The Future of the Force") — has no gene. `Skin_PaleRed` is also unsourced. The
> sourced palette is brown / light brown / green / orange, i.e. entirely earth tones"

and, from the visual brief:

> "**Palette varies across individuals and all of it is in the earth range**… **Nothing is
> blue.**"

**3. Does it carry a source? YES — the best in the batch.** Four colour values, four *named
works*, one per value. Search terms for you: the Wookieepedia **Ithorian** article's infobox;
`starwars.com/databank/ithorians`; *Star Wars Rebels* "The Future of the Force" for the orange.
The entry states its own retrieval honestly: wikitext via
`api.php?action=parse&page=Ithorian&format=json&prop=wikitext`, **38,530 chars, 2026-09-15**, and
records that the Databank page was **NOT fetched** — so "brown" reaches us second-hand through
Wookieepedia's citation of it.

**4. What it should become, and confidence.** Drop `Outland_Skin_DeepAzure` and `Skin_PaleRed`;
add an orange. Keep DeepSage / DeepBrown / Brown. **HIGH confidence** on the palette. **LOW
confidence that this visibly fixes the pawn**, for the reason in #5.

**5. Defect class — all three at once, and this is the case that shows why they must be kept
apart.**
- **data fix**: the skin gene list. Cheap, and it does fix the *body*.
- **engine limit**: `RSW_Ithorian_Normal` (SW_HeadTypes.xml:461) carries `useSkinShader:false`
  and the mask is pure greyscale (max chroma **2**). The face will not take the new colour.
  ⚠️ **The Ithorian entry does not record this.**
- 🔴 **RIG LIMIT**: the forward-curving neck. `CLAUDE.md` names Ithorian as a known rig limit.
  ⚠️ **But the entry files it under `## Engine limits`** —

  > "- A RimWorld head sprite cannot carry the forward-curving neck… the defining structure is
  >   undisplayable in a head-only slot as things stand."

  The substance is right; the **heading is the wrong class**. An "engine limit" invites new art
  or more mask channels. A rig limit means **no art at any price**. Filed in the wrong drawer,
  this is exactly the mistake that gets a sprite commissioned for nothing.

---

# 2. Bith — `SOURCED`, and I can measure the defect in pixels

**1. What ships.** `RSW_RimMandrakeBith`, xml:148. **`Skin_Melanin3` is the only skin gene**
(xml:162). Head `RSW_BithHead` (xml:160; SW_Genes.xml:323) → `RSW_Bith_Normal`
(SW_HeadTypes.xml:57).

⚠️ The exact RGB of `Skin_Melanin3` is **UNMEASURED**. It is a vanilla Biotech gene, and no
vanilla gene def and no def dump exists on this laptop (the frozen `official` dump lives under
the Windows path). What I can confirm is the gene *name* in the list and that it is the only one.

**2. What canon says.** `.../bith/description.md`, quoted:

> "Canon infobox: subspecies **Y'bith**; **skin colour cream, green, orange, pink, or white**"

> "Skin **pale pink, red, yellow, or (rarely) green**." *(Legends infobox)*

> "🔴 **`Skin_Melanin3` is a mid-brown human tone, and no Bith is brown.**… A single mid-melanin
> human skin gene produces a colour that appears nowhere in either continuity"

> "**Skin is pale**: cream, bone, pale pink, or a warm pale tan across the four images. Never
> dark, never brown, never saturated."

**3. Does it carry a source? YES.** Two infoboxes, both quoted, both on pages you can open:
Wookieepedia **Bith** and **Bith/Legends**. Retrieval recorded: 26,387 chars and 36,330 chars,
both 2026-09-15. ⚠️ The entry flags that the canon article carries an `{{Expand|all sections}}`
banner and that the print sources (*Fully Operational*, *Alien Archive*) were **not independently
verified**. So the *infobox colour list* is checkable in one search; the books behind it are not.

**4. What it should become.** Replace `Skin_Melanin3` with a pale palette — cream / bone / pale
pink / pale tan. **HIGH confidence.** Five of the six canon values plus all four references agree,
and this is the least ambiguous colour call in the batch.

**5. Defect class — data fix for the body, engine limit for the face.**
The entry says **`## Engine limits: none known`**. 🔴 **That is measurably wrong.** I measured
`Heads/Bith/Normal_south.png`: **2,194 opaque pixels with chroma > 40**, bounding box
x203–308 / y301–346 in a 512² image — **centroid 64% down the head, i.e. the mouth** — mean RGB
**(171,105,105)**, most saturated pixel **(220,126,126)**. That is baked red at the mouth, and it
is exactly what the entry's own prose describes ("a dark red gash filled with jagged black
spikes… baked-in red, not a tintable grey"). The entry *found* it and then wrote "none known" in
the field that was supposed to carry it. Combined with `useSkinShader:false` on line 57, **no
skin gene can override that mouth.** New art, not a value.

---

# 3. Zygerrian — `SOURCED`, and the audit under-reported it

**1. What ships.** `RSW_RimMandrakeZygerrian`, xml:2240. **Seven** skin genes (xml:2261–2267):
`Skin_DeepRed`, `Outland_Skin_Red`, `Outland_Skin_Brown`, `Outland_Skin_PaleBrown`,
`RSW_Skin_MidGray`, `Skin_SlateGray`, `Skin_LightGray`.

⚠️ **"Ships red" is a simplification.** Red is first in the list, but five of the seven are
browns and greys, and the canon entry says those five **map correctly**. Only the two reds are
outliers. `RSW_Skin_MidGray` = `(162, 162, 162)` (SW_Genes.xml:3274) — measured.

🔴 **Two things the audit did not mention, both measured:** the head gene is **`RSW_CatharHead`**
(xml:2259) — so Zygerrian is a **fifth** borrowed head, not a skin-only case — and the
`<iconPath>` is **`…/XenotypeIcons/Xenotype_Cathar`** (xml:2243).

**2. What canon says.** `.../zygerrian/description.md`, quoted:

> "Canon infobox: class **feline**; 🔑 **skin colour "Light" — a SINGLE entry**"

> "**Legends** … **skin colour Light**"

> "*Other individuals displayed a certain amount of **bare skin on their faces, which was light
> in tone**.*"

> "They generally had **sallow complexions**"

> "🔴 **The def gives Zygerrians RED skin. Canon gives exactly one skin colour — "Light" — and
> not one of the four references shows red skin. This is the loudest error in this batch.**"

And the nuance that makes the def defensible in part:

> "**Red** appears in canon as a **hair/FUR colour**, not skin — so a red *fur* option is
> defensible, but red as the species' primary skin is not"

**3. Does it carry a source? YES, and it is unusually clean** — the same single value, "Light", in
**two independent infoboxes** (canon and Legends), plus a body-text sentence. One search settles
it. Retrieval recorded: canon 26,951 chars, 2026-09-15.
⚠️ **Two honest caveats the entry itself raises.** The canon article **has no "Biology and
appearance" section at all** — the biology is on `/Legends`. And the Legends pull **hit the
50,000-char cap and is TRUNCATED**; the entry states the infobox and Biology section are *within*
the retrieved portion and that everything below is "UNREAD, not absent." Believe that
distinction; it is the correct one.

**4. What it should become.** Drop `Skin_DeepRed` and `Outland_Skin_Red` from *skin*; consider red
as a *fur/hair* option instead. **HIGH confidence** on canon. **Confidence that it changes the
pawn's face: LOW** — see #5.

**5. Defect class — `engine limit`, not the data fix the audit implies.**
The entry writes **`## Engine limits: none known — every finding recorded here (red rather than
"Light" skin…) is attributed to specific gene/def choices, not to a rendering-pipeline
constraint.`** 🔴 **Measurably wrong.** `RSW_Cathar_MaleNormal` (SW_HeadTypes.xml:111) and
`RSW_Cathar_FemaleNormal` (:97) both carry `<useSkinShader>false</useSkinShader>`, and the mask
`Heads/Cathar/Male_Head_south.png` is **pure greyscale (max chroma 0)**. So editing the skin gene
moves the body and leaves the face untinted. The entry drew the opposite conclusion in the exact
field meant to catch it.

---

# 4. Chadra-Fan — `SOURCED`, audit CONFIRMED, but the fix may be a no-op

**1. What ships.** `RSW_RimMandrakeChadraFan`, xml:257. **CONFIRMED: no skin-colour gene of any
kind** in xml:266–293. `Furskin` at xml:286. No head-type gene either — the species is
`RSW_Nose_SmallPig` + `Outland_Ears_Fleef` on `Body_Standard`.

**2. What canon says.** `.../chadra_fan/description.md`, quoted:

> "Skin color: **gray** (*Darth Vader* (2017) 18), **light** (*Trail of Shadows* 4), **tan**
> (*Star Wars: Card Trader*)."

> "🔴 **No skin-colour gene at all**, so the sourced **gray / tan / light** span is
> unrepresented; `Furskin` is doing all the work. Grey is what the on-screen Shortpaw actually
> is."

> "🔴 **The two individuals are completely different colours: warm mid-brown fur (scout) versus
> cool ash-grey (Shortpaw).** Both are sourced. Do not settle on one."

**3. Does it carry a source? YES** — three colour values, three named works with issue numbers
(*Darth Vader* (2017) **18**; *Trail of Shadows* **4**). That is as checkable as this gets.
Retrieval: 17,080 chars, 2026-09-15. ⚠️ The 1-metre height comes from
`starwars.com/databank/chadra-fan`, **NOT fetched** — second-hand.

**4. What it should become.** Add grey and tan. **MEDIUM confidence — and this is a genuine
open question, not a hedge.** The species is `Furskin`, and the canon colour being described is
**fur**, not skin. Whether a `Skin_*` gene visibly recolours a Furskin pawn is an
engine-behaviour question, and on this laptop it is **UNMEASURABLE** — no RimSage, no decompiler,
no def dump. Do not let anyone tell you the answer without a quicktest.

**5. Defect class — `data fix`**, and unlike Zygerrian/Bith this one is clean: there is no
Chadra-Fan HeadTypeDef at all, so no `useSkinShader:false` stands in the way.
⚠️ **Separately, the entry records a fabricated number worth your attention**: "🔴
**`RSW_lifespan_half` is unsourced.** The infobox lifespan field is **empty**… this is invented
and it is exactly the kind of number this library exists to stop." Not appearance — but it is in
the def (xml:269).

---

# 5. Abednedo — ⛔ **THE AUDIT IS WRONG**

**1. What ships.** `RSW_RimMandrakeAbednedo`, xml:19. The audit says Abednedo is "missing a skin
colour entirely." **It is not.** xml:33–40 carries **eight** skin genes:

```
33  <li>Skin_Orange</li>
34  <li>Outland_Skin_PaleOrange</li>
35  <li>Skin_Melanin5</li>
36  <li>Skin_Melanin1</li>
37  <li>Skin_Melanin3</li>
38  <li>Outland_Skin_PalePink</li>
39  <li>Outland_Skin_Brown</li>
40  <li>Outland_Skin_PaleBrown</li>
```

**2. What canon says.** `.../abednedo/description.md`, quoted — and note the finding is a
*narrower* one:

> "Skin color is a wide individual menu: **brown** (*The Force Awakens*), **cream** (*Star Wars:
> Uprising*), **gray** (*TFA Visual Dictionary*), **orange** (*IDW Adventures* 5), **pink** and
> **tan** (*Visual Dictionary*)."

> "🔴 **No grey or cream skin gene.** The list carries `Skin_Orange`, `Outland_Skin_PaleOrange`,
> `Outland_Skin_PalePink`, `Outland_Skin_Brown`, `Outland_Skin_PaleBrown`, `Skin_Melanin1/3/5` —
> i.e. the whole orange-to-brown band, and **not** the grey-cream that the on-screen Abednedo
> actually is."

> "🔴 **The palette on screen is grey-cream, NOT orange.**… Orange is a sourced *possible* color
> from a single comic, and treating it as the default is the failure mode here."

**3. Does it carry a source? YES — six values, six named works.** The strongest citation density
in the batch alongside Ithorian. Retrieval: 30,172 chars, 2026-09-15.

**4. What it should become.** Add a grey and a cream; demote orange from first-in-list.
**MEDIUM-HIGH confidence.** The claim is not "orange is wrong" — orange *is* canon, from *IDW
Adventures* 5. The claim is "orange is one comic's value and the on-screen character isn't it."
That is a judgement about weighting, not a canon violation, so it is yours to make rather than
the library's.

**5. Defect class — `data fix` PLUS an unrecorded `engine limit`.** `RSW_Abednedo_Normal`
(SW_HeadTypes.xml:16) carries `useSkinShader:false`, and I measured
`Heads/Abednedo/Normal_south.png` as **exactly greyscale — max chroma 0**. The entry writes
`## Engine limits: none known`. 🔴 Wrong. Adding a cream gene will cream the *body* and leave the
face flat grey.

---

# 6. Ewok — ⛔ **THE AUDIT IS MIS-FRAMED** (but there IS a real defect underneath)

**1. What ships.** `RSW_RimMandrakeEwok`, xml:516. **CONFIRMED: no skin-colour gene.** `Furskin`
at xml:554. Nine **hair** genes at xml:542–550: `Hair_SnowWhite`, `Hair_Blonde`,
`Hair_SandyBlonde`, `Hair_LightOrange`, `Hair_ReddishBrown`, `Hair_DarkBrown`,
`Hair_DarkReddish`, `RSW_Hair_SlateBlue`, `RSW_Hair_SlateRed`. Darkest available:
`Hair_DarkBrown`. Also `Hair_BaldOnly` at xml:537.

**2. What canon says.** `.../ewok/description.md`. The audit's "reportedly black, and reportedly
the centre figure of its own reference image" is **CONFIRMED** — but the entry files it against
**hair/fur**, not skin:

> "🔴 **There is no black fur gene, and black is one of the two colours canon names as most
> common.**… The darkest available is `Hair_DarkBrown`. Canon: "**brown and black as the most
> common colors**," the infobox cites hair colour **black**, and **the black Ewok is the centre
> figure of the infobox image.** A player will never roll the most iconic variant."

> "2. **Solid deep black**, with a contrasting **pale grey-tan muzzle**." *(centre of three
> figures in the infobox image)*

> "🔴 **`RSW_Hair_SlateBlue` and `RSW_Hair_SlateRed` are attested nowhere.**… The palette has
> room for two invented colours while missing the canonical one."

**3. Does it carry a source? YES.** Infobox skin **brown**, hair **black**, height **1 m**, mass
**30 kg** — the entry notes this is "the only species in this batch with BOTH height and mass
sourced." Retrieval: 45,397 chars, 2026-09-15. ⚠️ Caveats it raises itself: the article carries a
`{{MultipleIssues|expand|image}}` banner, and `starwars.com/databank/ewok` — the source of the
1-metre height — was **NOT fetched**.

**4. What it should become.** Add a black fur/hair gene; consider removing the two invented slate
colours. **HIGH confidence** — one infobox field and the wiki's own infobox picture. Do **not**
add a "skin colour" here; that is the audit's framing, not the evidence's.

**5. Defect class — `data fix`.** No Ewok HeadTypeDef exists, so no shader flag interferes.
⚠️ The entry also flags that the *art* gap is separate and larger: the repo's entire Ewok
inventory is a round-ears mask, with "**no muzzle patch, no eye-ring, no fur body, no juvenile
variant**" — that part is **new art**.

---

# 7. Lasat — `SOURCED`; audit CONFIRMED; and it collides with a rig limit

**1. What ships.** `RSW_RimMandrakeLasat`, xml:1131. **CONFIRMED: `RSW_CatharHead` at xml:1153.**
Skin: `RSW_Skin_Lavender` (xml:1159) = **`(160,145,200)`** and `RSW_Skin_SlateBlue` (xml:1160) =
**`(165,180,190)`** — both measured from SW_Genes.xml:3254 and :3354.
Also measured: **`<description>` is the single character `e`** (xml:1133).

**2. What canon says.** `.../lasat/description.md`, quoted:

> "Infobox: class **humanoid**; **skin colour light brown, gray, purple**"

> "🔑 **The fur patterns of a Lasat varied from individual to individual, and could change as
> they aged. NO TWO LASAT HAD THE SAME STRIPING.**"

> "🔴 **`RSW_CatharHead`.** The Lasat borrows the Cathar head. Cathar are a *feline* species;
> canon Lasat are classed only as `humanoid` and read as a deep-muzzled ursine/simian design with
> bat-like ears. A cat face is the wrong head, and it is the most visible error in the def."

> "🔴 **No striping anywhere in the gene list.** `RSW_Skin_Lavender` and `RSW_Skin_SlateBlue` are
> flat single-tone skins. The canonical Lasat is *banded*, and the wiki says so explicitly. This
> is the highest-value fix."

**3. Does it carry a source? YES.** Canon infobox (three colours) plus a quoted body-text
sentence. Retrieval: canon 29,008 chars, Legends 4,938 chars, both 2026-09-15. ⚠️ The
"impressive height, prehensile feet, strength and agility" distinctions line traces to
`starwars.com/databank/lasat`, **not fetched** — second-hand. The entry also does something I
want to praise loudly: it keeps `wookieepedia_lasat_legends_ae.jpg` as a **labelled negative
reference**, because Legends Lasat is a visibly different creature. If a sprite ever comes back
gaunt and goggle-eyed, that is the tell.

**4. What it should become.** Give it its own head. **HIGH confidence** that the Cathar head is
wrong; **LOW confidence** that any cheap fix exists, for two independent reasons in #5.

**5. Defect class — all three, and one of them is unfixable.**
- 🔴 **RIG LIMIT.** `CLAUDE.md` names Lasat. The entry agrees: "**Digitigrade legs with
  prehensile toes are a body-plan feature a human-skeleton RimWorld pawn rig cannot express as
  things stand.**" **No art fixes this at any price.** Retarget to best-achievable silhouette;
  do not commission legs.
- **engine limit (striping).** "**Striping cannot be expressed by a single-channel tint mask.**"
  Correctly filed.
- **engine limit (face tint) — MISSING from the entry.** `RSW_Cathar_*` carries
  `useSkinShader:false` (SW_HeadTypes.xml:97, :111) and the mask is greyscale (max chroma 0). The
  entry calls striping "the highest-value fix" without recording that the face cannot be tinted
  at all. Same miss as Zygerrian, same cause: they share the head.
- **new art** for the head itself: there is **no Lasat HeadTypeDef and no Lasat head gene**
  anywhere in `SW_HeadTypes.xml` or `SW_Genes.xml` — measured. So "point it at the right head"
  is not available. Something must be drawn.

---

# 8. Ortolan — `SOURCED`, and the skin is already RIGHT

**1. What ships.** `RSW_RimMandrakeOrtolan`, xml:1453. **CONFIRMED: `RSW_Head_kubaz` at
xml:1462** (SW_Genes.xml:2333 → `RSW_Male_Kubaz` / `RSW_Female_Kubaz`, SW_HeadTypes.xml:565 /
:292 → `HeadType/kubaz/Male_Kubaz`). Skin: `Skin_Blue` (xml:1469), `Outland_Skin_PaleAzure`
(xml:1470).

**2. What canon says.** `.../ortolan/description.md`, quoted:

> "**Skin colour: blue** (*Return of the Jedi*). **Eye colour: black.**"

> "🔴 **`RSW_Head_kubaz` is the wrong species' head.** An Ortolan is a broad dome, a thick
> drooping trunk and two huge black eyes; the Kubaz head is a narrow skull with a thin bristled
> snout and small slitted eyes. This is the biggest defect in the def."

> "🔴 **`donor_current_sprite.png` is not Ortolan art. There is NO Ortolan texture anywhere in
> `src/`** (a repo-wide search for `ortolan` returns nothing at all)."

**3. Does it carry a source? YES for the colour** — skin blue, cited to *Return of the Jedi*, and
the reference of record is a **live-action screencap** from *The Book of Boba Fett*
(`File:MaxRebo-BoBFCh2.png`), which the entry rightly calls "Practical creature effect rather
than an artist's interpretation, so this is the strongest possible evidence."
⚠️ **One citation in this entry is weak and you should know it**: the class "**elephantine**" is
cited to "**Leland Chee, Holocron-keeper Instagram, 2024-08-03**." That is a real sourcing
practice on Wookieepedia, but an Instagram post is a harder thing to verify than a film. It
affects only the *class*, not the colour.

**4. What it should become.** **Leave the skin alone — it is correct.** The head needs Ortolan
art. **HIGH confidence** on both halves.

**5. Defect class — `new art`, and this one is NOT blocked by the shader.** I verified both ends:
`RimMandrake_KubazJawBase` (SW_HeadTypes.xml:499) and its two children carry **no
`useSkinShader:false`** — they are absent from the 36 — and `HeadType/kubaz/Male_Kubaz_south.png`
measures greyscale (max chroma 3). So the entry's claim is **exactly right**: "the Kubaz head
base carries no `useSkinShader: false`, so the blue skin genes *will* tint it — the shape is
wrong, not the colour." A well-made entry; its `## Engine limits: none known` is the correct
answer here.

---

# 9. Mimbanese — `SOURCED`, skin already RIGHT, head confirmed as Tusken

**1. What ships.** `RSW_RimMandrakeMimbanese`, xml:1168. **CONFIRMED and traced end to end:**
`RSW_Head_Devolved` (xml:1187) → SW_Genes.xml:2206, label "**Devolved head**", forcing
`RSW_Male_DevolvedNormal` / `RSW_Female_DevolvedNormal` → SW_HeadTypes.xml:507 / :234, whose
`graphicPath` is **`RimMandrakeSW/SWX/Pawn/HeadType/Sov_tusken/HeadSandM` / `HeadSandF`** — Tusken
Raider art. Skin: `Skin_DeepRed` (xml:1189). `<description>` is the single character `e`
(xml:1170).

⚠️ **Note the trap in the audit's own wording.** The gene is not called "Tusken" anywhere. It is
called `RSW_Head_Devolved`. If you go looking for a Tusken reference in the Mimbanese def you
will not find one; the borrowing is two hops away, in the `graphicPath`.

**2. What canon says.** `.../mimbanese/description.md`, quoted:

> "Skin colour is sourced three ways — **red** (*Solo*), **brown** (*Bounty Hunters* 15), **grey**
> (*The Acolyte: The Visual Guide*)."

> "🔑 **The bright red colour of the Mimbanese came from their keratin scutes, although they
> could fade in colour**"

> "🔴 **`RSW_Head_Devolved` renders a Mimbanese with TUSKEN RAIDER head art.**… **a broad blank
> rounded head with two plain black dots for eyes, no nose, no mouth, no horns.** A Mimbanese
> therefore ships with a Tusken's featureless wrapped head and **none** of its own three
> identifying features."

> "✅ … `Skin_DeepRed` matches the sourced lurid red and the images."

**3. Does it carry a source? YES** — three values, three named works with issue numbers.
Retrieval: 8,170 chars, 2026-09-15. ⚠️ The article carries `{{Species-stub}}`, and the entry is
explicit that **no Legends article exists**, so height, mass and lifespan "remain **UNSOURCED**
and must not be invented." Good discipline. This entry also **cites its own repo line numbers**
for the head trace — the only one in the batch that does. It is the best-audited entry here.

**4. What it should become.** **Leave the skin alone.** Draw a Mimbanese head: lidless pale-blue
eyes, two rows of short brow horns, broad flattened snout. **HIGH confidence.**

**5. Defect class — `new art`.** Not shader-blocked: `RimMandrake_DevolvedHeadBase`
(SW_HeadTypes.xml:201) carries **no** `useSkinShader:false` — absent from the 36 — and
`Sov_tusken/HeadSandM_south.png` measures greyscale (max chroma 2). So the red *does* reach the
face today; the face is simply the wrong face.
⚠️ **One more thing worth your eye, non-appearance**: the entry flags
`AptitudePoor_Intellectual` + `RSW_GS_Primitive` against a canon text that calls the species
"**both highly aggressive and highly intelligent**" — and the gene's own player-facing label,
"**Devolved head**", editorialises against canon in the gene UI.

---

# 10. Ugnaught — `UNCHECKABLE`, and **our canon material contradicts itself**

**1. What ships.** `RSW_RimMandrakeUgnaught`, xml:2041. **CONFIRMED: no skin-colour gene** in
xml:2049–2071. Also measured: `<description>` is a single period `.` (xml:2043); `nameMaker` is
`RSW_KoTOR_NamerDevaronian` (xml:2048) — Ugnaughts draw Devaronian names.

**2. What canon says — and this is where it gets interesting.** `.../ugnaught/description.md`:

> "Infobox: class **porcine humanoids**; **skin colour "varying shades of pink"**"

> "**"Ugnaughts were diminutive, porcine humanoids who had pink skin, upturned noses, white hair,
> and thick layers of jowls."**"

But the same entry's visual brief says the opposite:

> "⚠️ **The infobox's "pink skin" is Legends colour asserted over canon art, and the live-action
> canon Ugnaught is not pink.**"

> "His skin is a **weathered grey-tan / dun brown**… There is a reddish undertone, but calling it
> "pink" produces the wrong colour."

> "`wookieepedia_negas_legends.jpg` — the Legends plate, and **this one IS pink**… So the two
> continuities genuinely differ, and the infobox is quoting the Legends value while illustrating
> with the canon figure."

And its `## Must show` picks the image over the text:

> "- [ ] Skin is a weathered grey-tan/dun brown (the canon live-action Kuiil), not pink — pink is
> the Legends-only value"

**3. Does it carry a source? `UNCHECKABLE` for the pink, and the entry says so itself:**

> "NOT fetched this pass: https://www.starwars.com/databank/ugnaught. The canon article cites it
> for the pink-skin / upturned-nose / white-hair / thick-jowls sentence… so those reach here
> **second-hand through Wookieepedia's citation.** ⚠️ That matters more than usual here, because
> the "pink" the Databank is cited for is the value the live-action image contradicts."

🔴 **This is exactly the failure mode you were worried about, and the library caught it rather
than laundering it.** The infobox says pink; the infobox's own picture is dun. One of the two is
wrong and our library cannot tell you which — it can only tell you the conflict is real. **If you
search one thing on this species, search `starwars.com/databank/ugnaught` and see whether it
actually says pink.**

**4. What it should become.** **This is the one where I want your call, not mine.** Options are
dun grey-brown (live-action *The Mandalorian* Kuiil) or pink (infobox text + Legends plate).
**Confidence LOW on which**, HIGH that *some* skin gene is owed — the entry notes that with none
at all, "Ugnaughts render in baseline human skin tones… neither is a human tone. This is the gap
most responsible for how they read in game."

**5. Defect class — `data fix`.** No Ugnaught HeadTypeDef exists (measured: nothing matching
Ugnaught in `SW_HeadTypes.xml`), so nothing shader-blocks it. ⚠️ The entry also records that
**the repo has no Ugnaught art of any kind** — "no head, no body, no hair, and not even a
xenotype icon" — so the snout/jowl/ear silhouette is **new art**, separately.

---

# 11. Chagrian — `SOURCED` but resting on a **single** book

**1. What ships.** `RSW_RimMandrakeChagrian`, xml:296. Four skin genes (xml:314–317):
`Outland_Skin_DeepOrange`, `Skin_Orange`, `Skin_Blue`, `Outland_Skin_DeepAzure`.

⚠️ **"Ships orange" is a simplification** — it ships two oranges *and* two blues. The two blues
are correct; the audit's phrasing implies orange is all there is.

**2. What canon says.** `.../chagrian/description.md`, quoted:

> "Infobox skin color is **blue only**; eye color **blue only**"

> "**Radiation resistance.** Chagrian skin ranges **light blue → cerulean → indigo** as a direct
> result of the species evolving under an **unstable sun**; the skin developed **an innate
> resistance to harmful radiation**, which became a **dominant trait of the species**. This is
> the one hard mechanical trait canon gives them."

> "🔴 **The xenotype carries orange skin, and canon Chagrian skin has no orange in it.**… Canon
> is **light blue → cerulean → indigo, and the blue is causally load-bearing** — it is the
> visible result of evolved radiation resistance under an unstable sun. An orange Chagrian is not
> a colour variant, it contradicts the species' stated biology."

**So the audit's "canon blue is load-bearing, an evolved radiation resistance" is CONFIRMED**
as the entry's claim, word for word.

**3. Does it carry a source? Yes, but thinly — and the entry flags it:**

> "⚠️ The article carries an `{{Expand|all sections}}` banner, so it is flagged incomplete by the
> wiki's own editors. **Nearly all of the biology and society detail above is cited to a single
> source, *Lead by Example* (`LBE`).**"

One book carrying the whole radiation-resistance argument is a real dependency. Retrieval: 26,516
chars, 2026-09-15. ⚠️ **A second thing to know**: the entry itself records that the infobox and
the images disagree on eye colour —

> "The infobox cites **blue only** (*The Phantom Menace*). The close-up plainly shows
> **orange/amber irises**… Trusting images on appearance: **orange is attested**, and the repo's
> `Outland_Eye_Orange` gene is therefore defensible rather than an error."

So there *is* legitimate orange on a Chagrian — in the **eyes**, not the skin. That is very likely
where the def's orange came from, and it is worth naming so nobody "fixes" the eye gene too.

**4. What it should become.** Drop `Outland_Skin_DeepOrange` and `Skin_Orange`; keep both blues;
the entry's visual brief argues the real target is "pale blue-grey to lavender/purple, heavily
mottled with pale cream-yellow patches — not a flat blue." **MEDIUM-HIGH confidence** — high that
orange skin is wrong, medium on the exact blue, because mottling is a texture claim.

**5. Defect class — `data fix`.** Clean. No Chagrian HeadTypeDef; the horn attachment
`RSW_ChagrianHorns` (SW_Genes.xml:683) declares `<colorType>Skin</colorType>`, so it tracks the
skin gene. The mottling, if you want it, is **new art**.

---

# 12. Nelvaanian — canon article is a **STUB**; everything comes from Legends

**1. What ships.** `RSW_RimMandrakeNelvaanian`, xml:1390. **CONFIRMED: `RSW_BothanHead` at
xml:1407.** Skin: `RSW_Skin_SlateBlue` (xml:1409) = `(165,180,190)`.

**2. What canon says.** `.../nelvaanian/description.md` — and the honesty is the point:

> "⚠️ **The canon (Disney-era) article is a stub with a completely empty infobox** — no height,
> mass, skin colour, eye colour, lifespan or distinctions. Every physical number and colour below
> comes from **`Nelvaanian/Legends`**, whose infobox is fully populated and sourced to *The Clone
> Wars Campaign Guide*."

> "**Skin colour: blue.** **Hair colour: blue-green with a black headcrest.** **Eye colour:
> black.**" *(Legends infobox)*

> "🔴 **"Blue-furred" badly misdescribes what the images show. A Nelvaanian is predominantly BARE
> BLUE-GREY SKIN with fur only in patches**"

> "🔴 **`RSW_BothanHead` is the wrong species' head.** A Nelvaanian's diagnostic features are a
> **long lupine snout** and **large upright pointed ears**; the Bothan head sprite has neither.
> This is the single biggest defect."

**3. Does it carry a source? Canon: NO. Legends: yes.** The retrieval numbers make the asymmetry
plain — canon article **3,045 bytes** (a stub), Legends **6,292 bytes**. Everything visual is
Legends, sourced to *The Clone Wars Campaign Guide*, which the entry states it **did not consult
directly** — "only Wookieepedia's transcription of it." ⚠️ Also: the species' entire screen life
is four episodes of the 2003–05 micro-series, so there is no live-action or CGI reference at all;
all three images are painted RPG plates.

🔴 **And the entry catches a fabrication in our own def**: "the claim in the repo def's own
`<description>` — 'a keen sense of smell and acute hearing that is purported to be able to detect
a creature's movement from a mile away' — **does not appear in either the canon or the Legends
article wikitext**." That sentence is shipping to players today (xml:1392) and traces to nothing.

**4. What it should become.** New head with a lupine snout and upright ears; keep
`RSW_Skin_SlateBlue`. **MEDIUM confidence** — the head being wrong is certain, the target colour
is Legends-only.

**5. Defect class — `engine limit` + `new art`. This is the entry that got the class RIGHT**, and
I verified it byte for byte:

> "the xenotype's `RSW_BothanHead` carries `useSkinShader: false` over its greyscale mask
> (`Defs/HeadTypeDefs/SW_HeadTypes.xml`), so no skin-colour gene reaches the face — a Nelvaanian
> pawn renders a blue body with a grey-white, untinted face."

**CONFIRMED**: `RSW_Bothan_MaleNormal` (SW_HeadTypes.xml:84) and `RSW_Bothan_FemaleNormal` (:71)
both carry `<useSkinShader>false</useSkinShader>`, and `Heads/Bothan/Male_Bothan_south.png`
measures **exactly greyscale, max chroma 0**. This is the entry that found the limit the Bith,
Abednedo, Ithorian, Zygerrian and Lasat entries all missed.

---

# 13. Umbaran — 🔴 **our own library is the only authority for the colour it recommends**

**1. What ships.** `RSW_RimMandrakeUmbaran`, xml:2074. `Skin_LightGray` (xml:2091) — **CONFIRMED,
and it is the only skin gene.** Head is vanilla `Head_Gaunt` (xml:2090). No Umbaran head type or
head gene exists in the repo.

**2. What canon says.** `.../umbaran/description.md`:

> "Infobox: class near-human; **skin colour "Pale and bluish"**"

> "a **slender** near-human species with **pale, bluish skin**"

Now the recommendation, and read the verb carefully:

> "**The well-lit illustration is the colour reference of record.** `wookieepedia_senator_infobox.jpg`
> (the canon infobox, a painted full-figure with even lighting) **shows the true value: a very
> pale desaturated skin with a distinct LAVENDER/lilac-violet cast** — pink-violet rather than
> blue, and definitely not grey and not green."

> "**`Skin_LightGray` is the wrong direction.** Canon says "pale and bluish"; the evenly-lit
> reference art reads **pale lavender-violet**. Grey is the one value that makes them look merely
> sickly rather than alien, and it is not supported by any source."

**3. Does it carry a source? SPLIT, and this is the field that matters most on this species.**
- **"Pale and bluish"** — `SOURCED`. Canon infobox, one search away (Wookieepedia **Umbaran**).
  Retrieval: 17,673 chars, 2026-09-15.
- 🔴 **"Lavender-violet"** — **UNSOURCED. No text anywhere says lavender.** It is *our agent's
  eyeball read of one painted illustration*, arrived at by deliberately discarding two
  screencaps as badly lit. The reasoning is good and it is stated openly ("This is the species
  where lighting has to be subtracted"), and trusting images over prose is the library's own
  stated rule from `AGENT_BRIEF.md`. But **if you search for "Umbaran lavender skin" you will
  find nothing**, because the claim is ours.
- The entry also notes the canon article's own pale-blue / white-eye / white-hair values come via
  `starwars.com/databank/umbaran`, **not fetched** — second-hand.

**4. What it should become.** Replace `Skin_LightGray` with a pale **blue-violet**.
**MEDIUM confidence, and I would frame it to you as "pale and bluish" — the sourced words — with
lavender offered as our interpretation of the picture, clearly labelled as ours.** Grey is
defensible as "pale" and indefensible as "bluish", so *something* is owed either way; the
argument for lavender specifically is a judgement, not a citation.
⚠️ Two further findings in the same entry, both sourced: `Hair_BaldOnly` contradicts the flat
canon sentence "**Although Umbarans did have hair, some of them either were bald or shaved their
heads**", and `Outland_Eye_White` "overshoots 'colorless'" — no image shows a blank white eye and
the infobox itself lists grey and pale blue.

**5. Defect class — `data fix`, cleanly.** The entry gets this right: "🔑 **There is no
Umbaran-specific head, body or hair texture in the repo at all** — the def builds the species
entirely from generic genes… so every correction below lands on a *gene choice*, not on new art."
Verified: nothing matching Umbaran in `SW_HeadTypes.xml`, and `Head_Gaunt` is vanilla, so no
`useSkinShader` flag is in play.

---

## Errors found in our own canon material — you asked for these

1. 🔴 **Four entries write `## Engine limits: none known` when they carry a measurable one.**
   Bith (SW_HeadTypes.xml:57), Abednedo (:16), Zygerrian and Lasat (Cathar, :97/:111) — all
   `useSkinShader:false` over greyscale masks. Zygerrian's is the most explicit: it *asserts* the
   red-skin problem is "not… a rendering-pipeline constraint," which is the opposite of what the
   file says. Only the **Nelvaanian** entry found this class of defect.
2. 🔴 **`AGENT_BRIEF.md` names four false-shader heads; the measured count is 36 of 138.**
   That understatement is the likely root cause of #1.
3. 🔴 **The Ithorian entry files a RIG limit under `## Engine limits`.** Right substance, wrong
   drawer. `CLAUDE.md` and `AGENT_BRIEF.md` both classify the Ithorian neck as a rig limit, and
   the distinction is the difference between "commission art" and "never commission art."
4. ⚠️ **The Ugnaught entry contains a real canon contradiction and handles it correctly** — the
   infobox says "varying shades of pink" while the infobox's own live-action image is dun
   grey-brown, and the pink traces to an unfetched Databank page. Flagging it rather than picking
   one is the right call, but it means the fix is not decidable from the library alone.
5. ⚠️ **The Chagrian entry rests almost entirely on one book** (*Lead by Example*) on an article
   the wiki itself flags `{{Expand|all sections}}`.
6. ⚠️ **The Zygerrian Legends pull is truncated at Fetcher's 50,000-char cap.** The entry says so
   and marks the remainder "UNREAD, not absent" — the honest wording — but it is a gap.
7. ⚠️ **The Nelvaanian canon article is a stub with an empty infobox**; every colour and number
   in that entry is Legends. And our own def ships an invented sentence ("a mile away") that
   appears in neither article.
8. ⚠️ **The Ortolan entry's "elephantine" class cites a Holocron-keeper Instagram post
   (2024-08-03)** — harder to verify than the rest, though it does not affect the colour.

## Non-appearance defects measured in passing — not for this decision, but recorded

- `nameMaker` wrong species: **Ithorian → Sullustan** (xml:905), **Ugnaught → Devaronian**
  (xml:2048). **Ortolan has no `nameMaker` at all.**
- `<description>` placeholders shipping to players: **Lasat `e`** (xml:1133), **Mimbanese `e`**
  (xml:1170), **Ugnaught `.`** (xml:2043).
- **Zygerrian's `<iconPath>` is `Xenotype_Cathar`** (xml:2243) — a second borrowed Cathar asset.

## What I could not measure on this machine

- **Exact RGB of every vanilla `Skin_*` and every `Outland_Skin_*` gene: `UNMEASURED.`** Those
  defs are not in this repo, and the frozen `official` def dump lives under the Windows path.
  Only the nine `RSW_Skin_*` genes are readable here (SW_Genes.xml:3196–3395); I quoted the three
  that matter.
- **What `useSkinShader:false` actually does at render time: `UNCERTAIN`.** It is a
  `TabulaRasa.DefModExt_HeadTypeStuff` field from `neronix17.toolbox`, whose source is not in this
  repo, and RimSage has never connected on this laptop. The flag's presence is confirmed; its
  effect needs one quicktest.
- **Whether a `Skin_*` gene visibly recolours a `Furskin` pawn: `UNMEASURABLE` here.** Bears on
  Chadra-Fan and Ewok directly.
