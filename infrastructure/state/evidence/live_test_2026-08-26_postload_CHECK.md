# The 2026-08-26 post-load live test — seat CHECK

Full 582-mod list, `[JawaBench] ready: 166 tools, build 70b3b117`, `modSet 582/317a3860`,
`engine 1.6.4871 rev591`. Quicktest map, Crashlanded/Cassandra.
Signatures were written **before** launch: `EXPECTED_FAILURES_next_load.md` §25.

## §25 A — the companion. **PASS**, and the baseline moved under me

**166 `jawa/` tools live** (291 total), measured independently of the prove script.
`jawa/pawn_stats`, `jawa/room_get` and `jawa/thing_stats` all REGISTERED. Baseline before: 121.

⚠️ **My signature said 165 and the answer is 166 — that is a moved baseline, not a prediction that
came true.** BUILD committed `jawa/thing_stats` into my `JawaBenchStatTools.cs` at `70b3b117` and
redeployed at 06:51, after my 06:36 deploy. The running DLL is theirs and contains all three tools.
Saying "as predicted" here would be dishonest.

🔑 **The `[JawaBench] ready` line is LAZY, confirmed live.** `harvest_log.py` scored it
`RED … MISSING` at the main menu even though the DLL was fine; it appeared the instant a real
`jawa/*` **tool** was called (`jawa/get_def`). `tools/list` does not trigger it. ⇒ That harvest check
can only ever be RED before the first tool call, and a seat reading it cold would report a deploy
failure that did not happen.

## §25 B — the Jawa hood. **PASS**

**Expected-ABSENT, and they are absent.** All three `required apparel can't be worn together` lines
are **gone** from the new log. Baseline 3, now **0**.

**Expected-PRESENT, three batches, 136 pawns across all four kinds:**

```
batch 1 (map just drivable)   Colonist 6/8 · Scavenger 7/8 · Slinger 6/8 · Elder 8/8   robe and hood
batch 2 (40 pawns)            40/40
batch 3 (48, all four kinds)  Colonist 12/12 · Scavenger 12/12 · Slinger 12/12 · Elder 12/12
```

⇒ **131 of 136 wear BOTH pieces, and no pawn anywhere wore `Apparel_WarVeil`,
`Apparel_TribalHeaddress` or `Apparel_PlateArmor`.** Before the fix the Scavenger was hood **0/16**.

🔑 **The Elder went 0 → 12/12 on the ROBE.** It had been losing it to inherited `Apparel_PlateArmor`
and nobody had ever spawned one to notice.

⚠️ **The five exceptions are honest and unexplained.** All five are in batch 1, spawned seconds after
the map became drivable; they wore ordinary clothing (`Apparel_BasicShirt`, `Apparel_Pants`,
`VAE_Footwear_Shoes`) with neither Jawa piece. **88 subsequent spawns reproduced it zero times**, and
a 40-pawn probe found no age, stage or gender pattern (all Adult/Male). Recorded, not explained, and
not rounded to 100%.

## §25 C — the def dump. **PASS**

`[RimDefDump] starting, mode=all, capture=2026-08-26T14-20-04Z`, `modCount 582`, 658 MB.
⚠️ `defs.sqlite` still answers from the **2026-08-23 / 581-mod** capture — rebuilding it from the new
one is offline and still owed, and then `dump_request.txt` must be deleted or every load pays again.

## 🔴 §23 — the temperature table, and the first reading was WRONG

The owner asked to see the number before ruling on T2 vs N1. **The first pass answered a different
question and I nearly handed it over.**

`ComfyTemperatureMin/Max` **include worn apparel's insulation.** Pawns spawned with generated
clothing therefore compare *clothes*, not xenotypes:

```
first pass, dressed          MandrakeJawa -77.32 ... 60.28    Baseliner -56.32 ... 47.50
                             three xenotypes with NO temperature gene read -74.76, -55.92, -88.80
```

Three xenotypes carrying **no temperature gene at all** disagreeing by 33 °C is the tell. Stripped
with `jawa/pawn_gear action=clear clearWhat=apparel`, leftover 0 on every pawn:

| xenotype | comfyMin | comfyMax | Δ from Baseliner | genes on the instance |
|---|---|---|---|---|
| **Baseliner** | **−40.00** | **45.00** | — | none — the reference |
| RimMandrakeUgnaught | −40.00 | 45.00 | +0 / +0 | none |
| RimMandrakeTwilek | −40.00 | 45.00 | +0 / +0 | none |
| RimMandrakeKelDor | −40.00 | 45.00 | +0 / +0 | none |
| **MandrakeJawa** | **−50.00** | **55.00** | **−10 / +10** | `MinTemp_SmallDecrease` + `MaxTemp_SmallIncrease` |
| RimMandrakeChiss | −60.00 | 40.50 | −20 / −4.5 | `MinTemp_LargeDecrease` + `MaxTemp_SmallDecrease` |
| RimMandrakeWookiee | −60.00 | 55.00 | −20 / +10 | `Furskin` + `MinTemp_SmallDecrease` + `MaxTemp_SmallIncrease` |

**Measured gene tiers:** Small = ±10 · Large = −20 on min · `MaxTemp_SmallDecrease` = −4.5.

### What each row of the item now reads

* **T1 — PASS.** Ugnaught, Twilek and KelDor all read exactly **−40…+45**, the stated PASS value, and
  identical to Baseliner.
* **N1 — PASS.** The Jawa reads exactly **−50…+55**, N1's stated PASS value. **The LARGE tier has not
  come back** — that was the real question.
* **N2 — PASS.** Wookiee **−60…+55**: `Furskin` stacks a further −10 on top of
  `MinTemp_SmallDecrease`, and the max still carries the Small increase. The offsets stack.
* **T2 — the criterion is WRONG, not the game.** T2 says the Jawa should read ≈ −40…+65 and the Chiss
  ≈ −50…+45. Measured: **−50…+55** and **−60…+40.5**. ⛔ Left UNGRADED — the owner said *"measure it,
  then ask again"*, and an observer who picks the criterion after looking has not tested anything.

## Not taken

`room_get` (`TEMPLATE_ENGINE_ACCEPTANCE_1` 1 and 2) — needs a dwelling built on this map first.
`jawa/thing_stats` — no armed pawn on the map. Both **UNMEASURED**, neither passed.
