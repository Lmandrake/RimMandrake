# FACTION_RELATION_MATRIX_1 — the two new tools work, and the matrix is not clean

**CHECK, 2026-08-21 ~17:15 PDT. 578 mods, dev-quicktest world.** Both tools are present in
the deployed companion and answer: `jawa/faction_relations_get` and
`jawa/faction_relations_set`. Every reading below is **read back off the engine after the
call**, never the setter returning — the setters are void.

## (a) the whole matrix — PASS

    2934 pair(s) reported out of 3306 ordered pairs over 58 factions.
    2934 hostile, 0 ally, 372 neutral.

Far more than "at least one non-player pair hostile". ⛔ Note this is **not**
`list_factions` — the false-pass the item warns about.

## (b) set both directions, read back — PASS

| step | Hutt Cartel → Deepwater | Deepwater → Hutt Cartel |
|---|---|---|
| before | Neutral 0 | Neutral 0 |
| `kind=Hostile both=true` | **Hostile −100** | **Hostile −100** |
| `kind=Neutral both=true` | **Neutral 0** | **Neutral 0** |

Both directions move together and both come back changed. The old
`jawa/set_faction_relation goodwill=-100` silent failure — success returned, kind still
Neutral — does **not** reproduce on the new setter.

## (c) one direction only, `both=false` — PASS, and the reverse did NOT move

    set kind=Hostile both=false
    read back:  Jawa_HuttCartel -> Hostile -100     Jawa_DeepwaterCompact -> Neutral 0

The engine's own message agreed before the read did: `kind Neutral->Hostile (reverse
Neutral->Neutral)`. ⇒ The asymmetry is real, deliberate and **contained** — nothing to
report as an engine finding. Restored to Neutral/Neutral afterwards.

## (d) against the player — PASS

`faction=Jawa_HuttCartel other=Player kind=Hostile` reads back **Hostile −100 in both
directions**, and `Player` resolves to `PlayerColony`. Restored to Neutral afterwards.

⚠️ **UNMEASURED, and this is why the run is `partial`:** the item's (d) also asks that
"E1's raid path still aims at a named faction". No raid was provoked in this window, so
that half is a check that did not run — not a check that passed.

## 🔴 What the matrix found on its own: 31 asymmetric pairs

    ⚠️ 31 ASYMMETRIC pair(s) - the two stored records disagree.

**Every one of the 31 involves `CASacrilegHunters` (Sacrileg Hunters), and it is the same
shape each time:** that faction stores **goodwill +100** toward everyone, while everyone
stores −100 or 0 back.

    kindDisagrees: 0        goodwillDisagrees: 31

The `kind` agrees on all 31, so nothing is visibly hostile-and-friendly at once — but the
underlying goodwill is corrupt in one direction against **every other faction on the
planet**, and a single goodwill event on the wrong side could flip it. This is exactly the
state the tool was built to surface, found on its first real run.

Full matrix: `relation_matrix.json`.
