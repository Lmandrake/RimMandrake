# "The ikee is watching me" — BUILD, 2026-08-23

Owner: *"activate the V2 C# build item 'The Ikee's watching me' as a positive mood buff for
Jawa, Hutt, and other Star Wars aliens known to keep creepy pets, but every other xenotype
receives a creep factor."*

Promoted out of `V2_DREAMS.md` and built. **New mod: `mandrake.jawaikee`.**

    src/Jawa/JawaIkee/About/About.xml
    src/Jawa/JawaIkee/Source/ThoughtWorker_IkeeNearby.cs      68 lines
    src/Jawa/JawaIkee/Source/JawaIkee.csproj                  net472
    src/Jawa/JawaIkee/Assemblies/JawaIkee.dll                 BUILT, 0 warnings 0 errors
    src/Jawa/JawaIkee/Defs/ThoughtDefs/Thought_IkeeWatching.xml

Deployed (3 files, VERIFIED in sync) and registered in `ModsConfig.xml` at **position 569 of
579**, immediately after `mandrake.starwarsraces` and well after `sarg.alphaanimals` — it
names defs from both. Previous ModsConfig backed up to `infrastructure/state/modlists/`.

## how it works
`ThoughtWorker_IkeeNearby` is a situational thought worker — RimWorld treats any ThoughtDef
with a `workerClass` as situational and polls it. It scans `map.mapPawns.AllPawnsSpawned` for
a living pawn whose `def.defName` is `AA_Eyeling` within 12 cells, then branches on the
observer's xenotype:

    stage 0   "ikee underfoot"            +4 mood    tolerant xenotypes
    stage 1   "the ikee is watching me"   -5 mood    everyone else

## 🔑 the tolerant list is DATA, not code
It sits on the ThoughtDef as a `DefModExtension` (`IkeeToleranceExtension`), so the owner can
retune who finds an ikee comforting **without rebuilding the assembly**. Ten xenotypes, all
verified present in the live set before shipping:

    MandrakeJawa                              the clan itself
    RimMandrakeHutt · Gamorrean · Nikto ·     Hutt space keeps worse things in its palaces
    Klatoonian · Weequay
    RimMandrakeTrandoshan · Rodian ·          hunters and scavengers who keep live trophies
    Aqualish
    RimMandrakeGeonosianVariants              hive-minded: an extra eye is unremarkable

`radius` is on the same extension and is also tunable.

## three decisions worth knowing
1. **No compile-time dependency on Alpha Animals.** The ikee is matched by `defName` string
   rather than a hard def reference, so this assembly does not need Alpha Animals' DLL to
   build and cannot fail to load if that mod changes.
2. **Every `<li>` in the list carries `MayRequire="mandrake.starwarsraces"`.** Without it a
   mod-list change turns the def into a red error at load instead of a shorter list.
3. **Animals and unspawned pawns return Inactive early** — animals do not have opinions about
   other animals, and a caravan pawn has no map to search.

## ⚠️ build note for whoever touches this next
`map.mapPawns.AllPawnsSpawned` is `IReadOnlyList<Pawn>` in 1.6, **not** `List<Pawn>`. The
first build failed on exactly that (`CS0266`). It is noted in the source.

## ⛔ NOT proven — no log line can
The mood numbers (+4 / −5) and the 12-cell radius are first guesses. Whether an ikee following
a Jawa around actually reads as *comforting* rather than as noise in the mood tab is a play
question. And the whole thing is invisible until a restart: a new assembly needs a cold load.
