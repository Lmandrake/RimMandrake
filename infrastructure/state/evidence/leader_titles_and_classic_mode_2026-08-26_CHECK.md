# LEADER_TITLES_ON_THE_IDEO_1 — FAIL, and the cause is bigger than the titles

2026-08-26, seat CHECK, live Ash'karr, full 582-mod list.

## The reading

`jawa/faction_leader_get`, all 16 non-hidden factions:

```
Jawa_IndigenousTribes  effectiveTitle "leader"  ideoTitle "leader"  defTitle "Prime Trader"
Jawa_Junkers           effectiveTitle "leader"  ideoTitle "leader"  defTitle "Scraplord"
Jawa_HuttCartel        effectiveTitle "leader"  ideoTitle "leader"  defTitle "Lord"
…  ideoOverrodeDef: true on every row
```

⛔ **Criterion not met: none of the twelve reports its intended title.** ⚠️ And the item's own
table — `Awoken Cheese`, `Ethical Thug`, `High Stellarch` — is **stale**. It was measured
2026-08-22 on a world that no longer exists; today every faction reads the single word `leader`.

## 🔴 The cause: Ash'karr is in Ideology CLASSIC MODE, and the twelve ideoligions are not in it

`jawa/ideo_of` on the live game: **`ideosTotal: 1`.** One ideoligion, named **`Astropolitan`**,
carrying `Classic_DanceParty` / `Classic_DrumParty` precepts — vanilla's classic-mode ideo.
`ideologyActive: true`, 152 pawns scanned, 95 non-player believers, all in that one ideo.

**Not just this session.** A literal-string read of the saves on disk:

```
ASHKARR_WITHER_2026-08-26      <classicMode>True</classicMode>  <name>Astropolitan</name>  <leaderTitleMale>leader</leaderTitleMale>
ASHKARR_ALLPASSES_2026-08-26   <classicMode>True</classicMode>  <name>Astropolitan</name>  <leaderTitleMale>leader</leaderTitleMale>
ASHKARR_DRAFT_2026-08-24       <classicMode>True</classicMode>  <name>Astropolitan</name>  <leaderTitleMale>leader</leaderTitleMale>
```

⇒ Every Ash'karr save back to 2026-08-24 is classic mode.

## Why that hard-sets the title — the mechanism, read not guessed

`RimWorld/IdeoFoundation.cs:695`:

```csharp
public virtual void GenerateLeaderTitle() {
    if (ideo.classicMode) {
        ideo.leaderTitleMale = PreceptDefOf.IdeoRole_Leader.label;   // "leader"
        ideo.leaderTitleFemale = ideo.leaderTitleMale;
        return;                                                       // <- short-circuits
    }
    if (ideo.culture.leaderTitleMaker == null) { … null … }
    …
    ideo.leaderTitleMale = NameGenerator.GenerateName(request, null, false, "r_leaderTitle");
}
```

and `RimWorld/Faction.cs:146` falls back to `def.leaderTitle` **only when the ideo's title is
empty** — `"leader"` is not empty, so the def never wins.

## 🔑 The mechanism the item asked me to find is ALREADY BUILT — and it cannot fire

Route 1 (a def route) is real and done. `src/Jawa/Jawa_Patches/Defs/CultureDefs/JawaLeaderTitles.xml`
ships **twelve `CultureDef`s, each with its own `leaderTitleMaker` RulePackDef**
(`Jawa_Culture_TradeMoot` → `Jawa_LeaderTitle_TradeMoot`, `Jawa_Culture_Junkers` →
`Jawa_LeaderTitle_Junkers`, …). The file's own header quotes the same `IdeoFoundation` line and
explains why a whole CultureDef per faction was needed. All twelve FactionDefs carry
`<fixedIdeo>true</fixedIdeo>`, `<requiredPreceptsOnly>true</requiredPreceptsOnly>` and an
`<ideoName>` — *the Weight*, *the Balance*, *Meckgin*, *the Ascendant Genome*, *the Continuity
Protocol*, and the rest.

⇒ **Nothing is missing from the content. The world simply never used it.**

Route 2 (a bridge pass) is **shut**: across all 246 live tools the only ideo tools are
`jawa/ideo_of` (read-only) and `jawa/set_pawn_ideo` (pawn-level). There is no ideo writer, and
`GenerateLeaderTitle` would re-derive from `classicMode` anyway.

## What this means beyond this item

🔴 CLAUDE.md: *"a faction, ideoligion or setting absent when he builds it is absent from every
player's game forever."* **Twelve authored ideoligions — names, descriptions, memes, precepts,
leader-title cultures — are absent from every Ash'karr save.** This is not a leader-title defect
with a workaround; it is a world-creation setting, and the world is the deliverable.

⚠️ **I am not proposing the fix.** Whether Ash'karr is re-created with Ideology in full mode — and
what that costs against the authored planet, which took many sessions — is a scope and schedule
call. Filed as `ASHKARR_IS_CLASSIC_IDEOLOGY_1`.
