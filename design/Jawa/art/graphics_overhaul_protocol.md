# graphics_overhaul_protocol.md — overhauling race art ourselves

_Written 2026-08-11. Grounded in: the live def dump (2026-08-11T16:25Z), a texture
audit of every active Star Wars / alien-race mod, the render-tree and framework
layer as it actually exists in this stack, and the existing Gamorrean art brief at
`design/Jawa/art/graphic.md` — which is already the right method and is generalised
here._

Companion: `src/Jawa/README.md` (deployment), `CLAUDE.md` (operating rules),
`skills/rimworld-modding/` (patch authoring).

---

## 0. The lesson that has to come first

The Gamorrean work nearly produced commissioned art for a problem that was partly
a **def** problem. `PigEars` existed in Biotech and simply wasn't on the xenotype;
the head was rolling from a pool of 206 head types that declare no `requiredGenes`.
Some of "the art is bad" was "the wrong art is being selected."

So the protocol opens with a gate, not a brief:

> **Exhaust the def layer before you draw a single pixel.**
> Art is the most expensive and least reversible input in this pipeline. Every hour
> spent confirming that no existing texture, gene, or head type solves the problem
> is an hour that pays for itself several times over.

This is the same rule as the tier ladder in the modding skill — bake what must be
TRUE before you build something new — applied to pixels.

---

## 1. The two layers, and why art alone is never enough

A race's appearance is **texture files plus the defs that decide which textures get
drawn**. Both must be right; either alone fails silently.

### 1.1 What actually draws a pawn (verified counts from the live dump)

| Def type | Count | Role |
|---|---|---|
| `PawnRenderTreeDef` | 39 | The node graph that draws a pawn. One per distinct silhouette. |
| `PawnRenderNodeTagDef` | 5 | Attachment points: `Root`, `Head`, `Body`, `ApparelHead`, `ApparelBody`. |
| `HeadTypeDef` | 459 | One per named head shape. Core ships 14; the rest are mods. |
| `BodyTypeDef` | 9 | `Male, Female, Thin, Hulk, Fat, Baby, Child` + 2 modded. Nobody adds more — races reuse these names and supply their own art under them. |
| `GeneDef` | 4,615 | **615 carry `renderNodeProperties`** — i.e. a gene attaches its own graphic. |
| `XenotypeDef` | 250 | Gene lists + an icon. **No graphic fields of its own** — appearance is entirely the union of its genes. |
| `BodyDef` | 391 | Internal anatomy; what render-tree `linkedBodyPartsGroup` references point into. |

The standard humanlike tree is `Root → Body / Head → ApparelBody / ApparelHead`.
Other mods' code *checks for that tag shape*, which matters in §1.3.

### 1.2 The three ways art attaches

**(a) Humanoid Alien Races** (`erdelf.HumanoidAlienRaces`, active) — a
`ThingDef Class="AlienRace.ThingDef_AlienRace"` with `graphicPaths` pointing at
folders. Note that **vanilla `Human` is itself a `ThingDef_AlienRace` in 1.6**, so
this is the mainstream path, not an exotic one.

```xml
<alienRace>
  <graphicPaths>
    <body><path>Things/Pawn/Humanlike/Bodies/</path></body>
    <head><path>Things/Pawn/Humanlike/Heads/</path></head>
  </graphicPaths>
  <generalSettings><alienPartGenerator>
    <headTypes><li>...</li></headTypes>
    <bodyTypes><li>Male</li><li>Female</li>...</bodyTypes>
  </alienPartGenerator></generalSettings>
</alienRace>
```

**(b) Genes carrying graphics** — the Biotech path, and **the one this project
already uses**. A gene declares `forcedHeadTypes`; a matching `HeadTypeDef`
declares `requiredGenes` so it can only ever be picked for pawns carrying that
gene. Real example from Big and Small:

```xml
<GeneDef ParentName="GeneJawBase">
  <defName>BS_DevourerHead</defName>
  <forcedHeadTypes><li>BS_DevourerHead_Normal</li></forcedHeadTypes>
</GeneDef>

<HeadTypeDef ParentName="AverageBase">
  <defName>BS_DevourerHead_Normal</defName>
  <graphicPath>BS_Heads/Devourer/average</graphicPath>
  <requiredGenes><li>BS_DevourerHead</li></requiredGenes>
</HeadTypeDef>
```

**The `requiredGenes` gate is load-bearing.** Without it a head type joins the
open pool — which is exactly the measured problem behind `JawaHead.xml`: 318 head
types loaded, 206 with no `requiredGenes`, so a pawn with no head gene rolls from a
pool that is two-thirds modded alien skulls.

**(c) Custom render trees** — for genuinely non-humanoid silhouettes. Beldon (Star
Wars Animal Collection) is the worked example: `Root → Body` with three
`PawnRenderNodeProperties_BulbfreakTentacle` children, each bound to its own
`BodyPartGroupDef`. Powerful, and it has a cost — see next.

### 1.3 Two constraints that will bite

**Facial Animation removes the vanilla head draw call.** FA's
`PostfixParallelPreDraw` deletes the `PawnRenderNode_Head` request and paints its
own eyes/brows/mouth layers. Consequence, already discovered the hard way in
`HeadSetForFA_Revive.xml`: **`forcedHeadTypes` can never render on a pawn FA is
drawing.** So for any race we give custom head art, we must either exclude it from
FA (as was done for Gand) or author FA-compatible "blank" heads with no baked
features. Decide this per race, up front — it changes what the artist draws.

**A novel render tree is invisible to code that expects the standard tags.**
Beldon's tree has no `Head` node, so Big and Small's sapient-animal feature logs
*"unhandled render tree … Defaulting to BS_HumanlikeAnimal"* and substitutes a
bare body-only tree. Not a crash, but it means apparel-fitting and
sapient-animal mods can't reason about that pawn. Custom trees are for creatures,
not for colonists you want to dress.

---

## 2. Candidates — who actually needs it

From a texture audit of every active Star Wars / alien race mod: file counts, real
pixel dimensions, direction coverage, gender variants.

| Race | Mod | Evidence | Verdict |
|---|---|---|---|
| **Wookiee** | Star Wars Xenotypes (2915192253) | **128×128** head vs **512×512** for every other species in the same pack. ~~No body art.~~ | **RESOLVED 2026-08-11 — was a def problem. See §2.1** |
| **Falleen ridged-spine** | Star Wars Xenotypes | 10 files: 5 body variants × east/north. **No `_south` for any variant** — the attachment doesn't render facing the camera. | **NEEDS WORK** |
| Droid Depot droids · Galactic Diversity xenotypes | Outer Rim (neronix17.*) | **MEASURED 2026-08-13 — 804 textures read straight out of the bundles.** Droid Depot 250 (200×256², 48×512²); Galactic Diversity 554 (547×512²). Direction sets complete on 103/104 stems. | **GOOD — no in-game look needed** |
| Sith Pureblood | Rimwars: Pureblood (sov.sith) | 512×512, full S/N/E, M/F present — but **one head style only**, so every Pureblood is identical. No custom body. | ACCEPTABLE |
| JDS Separatist droids | m3.continued…tsda | 65 files, uniform 256×256 (some 320–512), complete directions | ACCEPTABLE/GOOD |
| KotOR droids | guy762.kotordroids | 512–1024px, complete direction sets, some explicit west | GOOD |
| Rodian, Hutt, Gungan, Trandoshan, Duros, MonCal, Ithorian, Quarren, Kubaz, Geonosian, Selkath, Taung, Anzellan, Twi'lek | Star Wars Xenotypes | 512×512, full S/N/E, `Male_`/`Female_` pairs throughout | GOOD |

### 2.1 The Wookiee — worked example of Phase A paying for itself

The Wookiee looked like the clearest art commission in the stack. It was a
one-gene patch. **Two complete, correctly-gated head chains already exist:**

| Gene | → HeadTypeDef | → graphicPath | Measured |
|---|---|---|---|
| `OuterRim_WookieeHead` | `OuterRim_Wookiee` | `Things/Pawn/Humanlike/Heads/Wookiee/Wookiee` | **512×512** S/N/E |
| `guy762_Head_wookiee` | `Wookiee_Average1/2/3` | `Pawn/HeadType/wookiee/wookiee1‑3` | **128×128** S/N/E |

Neither is buggy — both carry proper `requiredGenes`. The 512 art was invisible
to the first audit because it lives in an **AssetBundle** (§2.2).

**Why the bad one wins:** `RimMandrakeWookiee`, from *[BTD] Xenotype REMIX: Star Wars* —
the mod adopted specifically to dedupe the SW-Xenotypes / Outer Rim overlap —
carries `guy762_Head_wookiee`. Its own `XenotypeEquivalencies.xml` lists all
three Wookiee xenotypes in one `EquivalentGroup`, so it knew both existed and
chose the lower-resolution one. A judgement call by its author, not a defect —
which is why the remedy is a local patch, not a bug report.

**Remedy shipped:** `Jawa_Patches/Patches/WookieeHead_Upgrade.xml`, nested
conditionals so it no-ops if Outer Rim is ever disabled. Trade-off accepted:
three head variants become one, in exchange for 4× linear resolution.

**Two corrections to the original audit, both worth internalising:**

- **"No body art" was wrong.** `Furskin` is a Biotech gene whose
  `renderNodeProperties` attach a `PawnRenderNode_Fur` to the `Body` tag. The
  fur *is* the body treatment. The audit searched for a `BodyType/wookiee`
  folder and read absence as absence of art — but since 1.6 graphics reach a
  pawn by at least three routes (race `graphicPaths`, `HeadTypeDef.graphicPath`,
  gene `renderNodeProperties`) and a folder search only sees two.
- **The generalisable lesson.** This is the *second* time "the art is bad" has
  meant "the wrong art is selected" — the Gamorrean was the first. Presence of
  an asset says nothing about selection of it.

**Falleen is the cheapest possible win** — one missing view. Whether that's an art
job or a def job depends on whether the south sprite is *missing* or merely
*mis-pathed*; check the def before drawing.

**Resolve the AssetBundle mods before planning around them.** Two Outer Rim mods
hold their art in compiled bundles, so a file audit can't see it. That's ~44
xenotypes of unknown quality. One in-game look with dev-mode pawn spawning settles
it, and it should ride along with an already-planned load.

**On the "droids have no female art" claim:** confirmed but *intentional*. Every
droid race audited sets `hasGenders: false`. Not an art gap. The real droid bug was
different and is already fixed — `DroidFemaleTexture_Fix.xml` sets
`<fixedGender>Male</fixedGender>` on pawnkinds whose mod ships only `Naked_Male_*`
bodies, which were otherwise rendering magenta.

---

### 2.2 AssetBundles — readable, and overridable

Four mods ship art compiled into Unity AssetBundles rather than loose PNGs, which
made them invisible to the first audit. Both halves of that worry were wrong.

**Reading them:** tooling is committed as `src/RimMandrake/Utils/extract_bundle.py`.

⚠️ **A plain `pip install UnityPy` still does NOT work, and the failure looks
like the bundle being unreadable rather than a missing package.** The system
Python is **PEP 668 externally-managed**, so system and `--user` installs are
both refused — re-measured 2026-08-13 *after* the owner installed Python in WSL,
because that install fixed `pip` being absent but not this. The script then exits
with only `UnityPy is required: pip install UnityPy Pillow`, which reads as
"install this" — and following that instruction literally fails again.

**The working route — a venv, touching nothing system-wide:**

```bash
python3 -m venv ~/.venvs/rimworld                      # persistent: survives reboots, unlike /tmp
~/.venvs/rimworld/bin/pip install UnityPy Pillow
~/.venvs/rimworld/bin/python src/RimMandrake/Utils/extract_bundle.py <bundle> --list --find eopie
```

_Was a five-line bootstrap: `--without-pip`, then fetching `get-pip.py` and
running it, because `ensurepip` was missing too. The owner's 2026-08-13 install
supplied `ensurepip`, so `venv` now creates a venv with `pip` already in it and
those three lines are gone. **Verified end to end after the change** — the venv
built, UnityPy 1.25.3 and Pillow 12.3.0 installed, and `extract_bundle.py` listed
Bantha textures out of the bundle._

⚠️ **The interpreter is PER-SCRIPT. There is no single right answer, and that is
the trap.**

⚠️ **The premise below changed on 2026-08-13 and the conclusion did not.** The
owner installed Python in WSL, so `python` and `python3` both exist (3.14.4) and
`pip` is present. The original reason for this warning — *"a bare `python` is not
on PATH"* — **is now false.**

**Do not read that as this section being stale.** Which interpreter a script
needs was never about `python` being absent; it is about what each script can
reach. Test the old premise, find `python` works, conclude the section has
expired, and you make **exactly the swap it exists to prevent**. Caught by
a retired seat the hour the premise changed.

What still holds, measured after the install: **the interpreter is per-script,
and the obvious repair — swap in `python3` — is wrong for this script**, in a way
that looks like a different bug:

| script | interpreter | what the wrong one does |
|---|---|---|
| **`extract_bundle.py`** | **the venv `python`** | system `python3` exits `UnityPy is required: pip install UnityPy Pillow`, which reads as "install a package", not "wrong interpreter" |
| `deploy_custom_mods.py` | `python3` or `python.exe` | — |
| `refresh.py` | **`python.exe` only** | `python3` fails `cannot read ModsConfig`, which reads as "the config is gone" (it hardcodes `C:\Users\…`; closed, `29c89f0`) |

⚠️ **Every one of those wrong-interpreter failures names something else as the
cause.** That is what makes a blanket fix expensive: it sends the next person
hunting a problem that does not exist.

So for this script, keep using the venv from the recipe above:

```bash
~/.venvs/rimworld/bin/python src/RimMandrake/Utils/extract_bundle.py <mod>/AssetBundles/<bundle> --list --find wookiee
~/.venvs/rimworld/bin/python src/RimMandrake/Utils/extract_bundle.py <mod>/AssetBundles/<bundle> --extract out/ --keep-paths
```

_This block previously said `python3` on both lines — a mechanical `python` →
`python3` swap made while fixing the `command not found`, sitting directly below
a correct venv invocation. Caught by a retired seat, 2026-08-13._

⭐ **This reopened a blind spot recorded as closed-by-game-load above, and the
row is now CLOSED offline — no cold load was spent.** Flagged by a retired seat, who
verified the route by extracting 28 Eopie and 4 Massiff textures from Star Wars
Animal Collection and reproducing a day-old decision to within 0.01 of subject
aspect. Another retired seat then ran the audit itself, 2026-08-13:

| bundle | Texture2D | sizes | direction sets |
|---|---|---|---|
| `neronix17_outerrim_droiddepot` | **250** | 200×256², 48×512², 1×212×256, 1×64² | 21/22 complete |
| `neronix17_outerrim_galacticdiversity` | **554** | 547×512², 6×64², 1×500×40 | **82/82 complete** |

**Verdict GOOD.** Uniform resolutions, no undersized art, and the single
incomplete stem is `mse` (east+south, no north) — the already-known MSE-6 bug,
already fixed by the loose-PNG override in `mandrake.missingartfixes`.

⚠️ **20 fully-empty textures were found and NONE of them is a bug.** Recording
the triage, because the raw count is alarming and re-finding it would cost
another pass:

| what | count | why it is not a defect |
|---|---|---|
| `droid/blank/head/head_*` | 6 | folder is literally named **`blank`**, all six directions empty, **0 healthy siblings** — a self-labelled placeholder |
| `building/droidbay/droidassembly_*_south` | 11 | **systematic across all 11 assembly variants** against 37 healthy siblings in the same folder — a convention, not an omission |
| `genes/eyes/eyes_{male,female}_north` | 2 | eyes are not drawn from behind; the known idiom |
| `hairs/cerean/cereanmane_south` | 1 | **the one real bug** — already found and already fixed |

**Method note: an absolute "alpha max 0" test would have reported 20 bugs here.**
What separates them is the sibling comparison — *how many healthy files share
this folder, and is the emptiness systematic across a whole family?* Systematic
emptiness across every member of a family is a convention; a single empty file
among healthy siblings is a defect. That discriminator is the whole test.

It reports dimensions and resolves the internal path back to a RimWorld texture
path. Assets are stored at `assets/data/<packageid>/textures/<ordinary path>`, so
stripping the prefix recovers exactly what a def's `graphicPath` uses.
`--keep-paths` writes the tree in the layout an override mod needs.

Verified on Galactic Diversity's bundle: 554 `Texture2D` objects read cleanly.

**Overriding them — the important part.** RimWorld resolves a texture request in
this order:

1. a **loose file** at that path, in **any** active mod
2. the base game's built-in resources
3. **bundles**

Bundles are checked **last**, so a loose PNG at the same path wins *regardless of
load order*. Overriding a bundle mod is genuinely easier than overriding a
loose-file mod, where you would have to win the load-order fight. The corollary
constrains us only as authors: **a bundle can never override a base-game
texture**, so anything we ship that must override should be loose files.
Source: [RimWorld wiki — Asset Bundles](https://rimworldwiki.com/wiki/Modding_Tutorials/Asset_Bundles)

**Still unaudited:** Droid Depot and Galactic Diversity hold ~44 xenotypes'
worth of art we have now proven we *can* read but have not yet swept. That is
cheap offline work and should happen before any further art decisions.

---

## 3. The Hutt as the strange-shape study

The right instinct. The Hutt `FatHead` is the best donor in the stack for
non-human anatomy, and the existing brief already leans on it.

Looking at the actual art: it is **wider than tall, low sloping cranium, massive
jowls, sour downturned mouth** — and drawn with roughly a 10 px black contour at
512, a near-white lit band, one mid-grey shadow band, and almost nothing in
between. The face is two dots and a line.

That last point is the transferable lesson, and it is counter-intuitive:

> **RimWorld faces carry species through silhouette, not detail.** A colonist head
> occupies ~186×206 px of the 512 canvas; the Hutt occupies ~284×213 — about 50%
> wider. That width *is* the species read. At the 40–128 px the player actually
> sees, interior detail vanishes and only the outline survives.

So the discipline for any strange body or face shape is: **push the outline hard,
keep the interior nearly empty.** The `D_style_range_aliens` sheet proves the
ceiling — Mon Calamari eye stalks, Quarren face tentacles, Geonosian mandibles all
live comfortably in this style. You are not limited to a human head with bits
added. You are limited to three values and a heavy line.

---

## 4. The protocol

### Phase A — establish what the problem actually is (no art)

1. **Dump the race's current def state.** Which genes, which head type, which body
   type, which textures resolve. The live dump answers all of this offline.
2. **Ask whether an existing asset solves it.** Is there a Biotech gene (`PigEars`,
   `HeadBone`, snouts) or another mod's head type that gets you there? The
   Gamorrean's ears were sitting unused in the base game.
3. **Check for selection bugs.** Missing `requiredGenes`, an unguarded head pool, a
   mis-pathed texture, a missing `_south`. These look exactly like bad art.
4. **Decide the FA question now** (§1.3). Exclude the race from Facial Animation,
   or author blank heads. This changes the brief.
5. **Only if all four fail, commission art.**

### Phase B — build the seed pack

This is the part `design/Jawa/art/` already does well, and it generalises cleanly.
Every future request gets the same six folders:

| Folder | Contents | Why it matters |
|---|---|---|
| `00_contact_sheets/` | everything below, composited on a grey checkerboard | transparent PNGs are invisible otherwise; the model needs one glance |
| `01_donor_<species>/` | the closest existing head, all six views | style and geometry anchor; also fixes male→female dimorphism |
| `02_colonist_baseline/` | ordinary human head, three facings | defines "normal" so deviation can be judged |
| `03_vanilla_parts/` | the engine's own vocabulary for this trait | keeps drawn features in-style rather than grafted on |
| `04_style_range/` | 8 other alien heads from the same mod | proves the ceiling; licenses pushing anatomy |
| `05_current_<species>/` | the inadequate art being replaced | shows intended placement and line weight |
| `06_body_context/` | the body types the head will sit on | stops a dainty head on a Hulk body |

Two sheets in the existing pack are doing unusually heavy lifting and should be
mandatory in every future one: **`B_colonist_vs_donor_same_scale`** (relative bulk)
and **`F_true_ingame_scale`** (512 px source next to real 40–128 px display size).
The second is what stops an artist spending effort on detail nobody will ever see.

A third is worth adding as standard: the existing **`G_current_..._full_pawn`**,
showing the head with apparel layered on. The Gamorrean brief notes the hood crops
the cranium, so *"the snout, tusks, jowls and ears carry the entire species read."*
That kind of observation only comes from looking at the dressed pawn, and it should
be made before the brief is written, not after.

### Phase C — write the brief

`design/Jawa/art/graphic.md` is the template. Its structure works and the ordering is
deliberate — the technical constraint comes before the creative direction, because
a beautiful image in the wrong colour space is worthless.

Non-negotiable sections, in order:

1. **The greyscale-mask fact, stated before anything else.** *"These textures are
   greyscale masks. RimWorld multiplies a skin colour over them at runtime."* The
   art looks like a white ghost and that is correct. Colour baked into the texture
   cannot be undone.
2. **Hard constraints** — 512×512 PNG, true alpha, zero saturated pixels, the
   measured value distribution (~30% pure black line, ~30% in the 192–223 band,
   ~40% in 224–255, ~2% everything else), ~10 px outline, top lighting, framing
   box, head only, and a magenta-background fallback if the pipeline can't emit
   alpha.
3. **What "better" means, in one sentence.** The Gamorrean brief's is exemplary:
   *"recognisable as a Gamorrean from the silhouette alone, at 40 px, from any of
   the three facings."* Testable, and it disciplines everything else.
4. **The design**, feature by feature, each tied to a silhouette consequence.
5. **Canon references** — Wookieepedia and StarWars.com links.
6. **Delivery: one image per message at maximum resolution**, never a contact sheet
   (which starves each view of pixels), and **stop after image 1 for approval**
   before spending five more on the wrong style.

The "state your plan in one or two sentences before drawing" instruction at the end
is the highest-leverage line in the whole document — it costs nothing and catches a
misread before it becomes six images.

### Phase D — integrate and verify

1. Drop PNGs into the mod's `Textures/` tree under the path the def expects.
2. Author or patch `HeadTypeDef` + gene with `requiredGenes` gating.
3. `python src/RimMandrake/Utils/deploy_custom_mods.py` (plan) then `--apply` — **writing the file
   is not deploying it**; that cost a whole test cycle on 2026-08-11.
4. Dev-mode throwaway world, spawn the pawn, check **all three facings, dressed and
   undressed, at real zoom**, and grep `Player.log` for
   `Failed to find any textures at`.
5. Verify at 40 px, not at 512. That is the actual product.

### Phase E — batch it

Per `CLAUDE.md`, a game load is ~23–30 minutes. Never test one race per load.
Prepare every candidate's art and defs, deploy together, then spend one load
checking all of them. Art changes are low-attribution-risk — a wrong sprite is
obvious and names itself — so they batch freely, unlike C# assemblies.

---

## 5. What ChatGPT image generation is and isn't good for here

Honest assessment against what this style needs:

**Good fits:** the style is *simple* — flat greyscale, heavy line, three values,
minimal interior. That is far more achievable than photoreal, and consistency is
enforceable by giving the donor as a reference.

**Known weak points to design around:**

- **Exact alpha.** Hence the brief's magenta fallback, which is lossless here
  precisely because the art is greyscale.
- **Colour creeping in.** "Greyscale" needs stating more than once and needs
  checking on receipt — a saturation histogram is a two-line script and should be
  part of intake.
- **Framing drift.** The brief's approach is right: give the target box, then
  *"get close and I will do the final pixel alignment myself."* Don't ask the
  generator for pixel-exact placement; do it in post.
- **Cross-view consistency.** This is the real risk. Approving image 1 and
  demanding rigorous consistency afterwards is the correct mitigation, and the
  south/north identical-silhouette requirement is a hard check we can verify
  programmatically (opaque pixel counts should match).

**Also worth knowing before commissioning anything:** we can now read *any*
installed mod's art, bundled or loose (§2.2). So the donor search for a seed pack
is no longer limited to mods that ship loose PNGs — extract first, then choose the
best donor in the whole stack rather than the best visible one.

**Worth building: an intake validator.** A small `check_sprite.py` that asserts
512×512, a real alpha channel, zero saturated pixels, the value distribution within
tolerance, the silhouette bounding box within the target range, and south/north
silhouette parity. Every one of those is objectively checkable, and catching a bad
sprite at intake is far cheaper than after it is in the mod. This is the art
equivalent of `validate_patch.py`, and it pays back on the second race.

---

## 6. Phase 2 — the "broken infrastructure" mod

Same discipline, and the gate applies with equal force: **find out what already
exists before authoring anything.** RimWorld ships damaged/ancient structures, and
several installed mods (Ancient Urban Ruins, VQE Ancients, Rimsential Spaceports)
carry broken-building concepts. The first task is a survey, not a design.

The concept — a gravship arriving full of *broken* workbenches, turrets and engines
that must be repaired through tech progression — is strong for this campaign
specifically, because it converts the ship from a container into a **tech tree with
a floor plan**. It also fits the anti-exponential pillar: repair is gated by
research and materials, so the ship's capability curve is authored rather than
looted.

Likely shape, to be validated against what the survey finds:

- A `ThingDef` per broken variant, deliberately **non-functional** — no work
  giver, no power, reduced beauty — so it reads as scenery until fixed.
- A repair path as either a research-gated **recipe** or a construction
  `ThingDef` whose `costList` includes the broken one, so repairing consumes it.
- Damaged **graphics**, which can reuse this same art pipeline — and are far easier
  than pawn art, since buildings have no directional facings or gender variants.
- Placement via the map/scenario authoring already in `src/RimMandrake/Utils/`.

The gameplay effect is real: it turns "here is your ship" into "here is what your
ship *could* be", and every repair is a legible milestone. Worth doing properly —
but after the race art, and after the survey.

---

## 7. Recommended first move

**Wookiee, full pipeline, as the pilot.** It is the clearest need, the method is
already proven on the Gamorrean, and it exercises everything — head *and* body art,
the FA decision, gene gating, and the intake validator.

Concretely, and in this order:

1. Phase A on the Wookiee — confirm the 128 px head and absent body art are genuine
   gaps, not selection bugs. Offline, costs nothing.
2. Build the seed pack using the Gamorrean folder structure, with the Hutt or
   Trandoshan as donor.
3. Write `check_sprite.py` **before** commissioning, so intake is automatic from the
   first image.
4. Run the brief.
5. Batch the result with the Falleen south sprite and an in-game look at the two
   AssetBundle mods — one load, three answers.
