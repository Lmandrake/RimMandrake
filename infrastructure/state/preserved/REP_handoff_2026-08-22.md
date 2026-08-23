# REP handoff — 2026-08-22 21:53

All committed and pushed; `origin/main..HEAD` empty. REP owns no open items.
MODE is back to `interactive` — the owner returned to launch the game.

## 🔴 THE GAME IS LOADING RIGHT NOW

Stamped `LOADING` at 21:52 on the owner's words. The new `Player.log` started
**21:52:17**.

**THE FIRST READING DECIDES EVERYTHING ELSE:**

> **`[Inhabited] ready:` must read 294, NOT 193.**

193 means the cast fix did not reach the game — **stop**, and no number measured
after it is worth keeping, because a baseline against 193 of 294 people has to be
thrown away. Also watch for
`Could not resolve cross-reference: No RimWorld.SkillDef named li` — the exact
signature of the bug that was fixed.

⚠️ **I had a Monitor armed on those strings. It dies with this session** — re-arm
it or read the log.

⭐ **The previous `Player.log` is saved** at
`infrastructure/state/logs/Player_2026-08-22_08-40.log` (149 MB, gitignored). It is
the only evidence for everything done before this launch and would otherwise have
been overwritten at 21:52.

## Pre-launch was verified clean — do not redo it

| check | reading |
|---|---|
| mod list | `LIVE 578 = FULL 578` by md5 |
| custom mods | in sync, 0 pending (14 held on purpose) |
| JawaBench companion | byte-identical to HEAD |
| 69 `Patches/*.xml` | 0 errors against the real load set |
| def dump | current and **FROZEN** at `49b83562b10df31c`, matches the live 578 |

⛔ **Do not arm a new def dump.** Nothing needs it.

**57 items ride this load — 37 `bridge`, 14 `game-up`, 6 `harvest`.** Recounted
21:52 off the queue files, not trusted from the doc.

## 🔴 The board was rebuilt today and the doctrine changed

Owner: *"It's never showing what the agents are really doing… all the agent
status' are wrong."* **He was right about every tile**, and the cause was one
thing: the board printed what seats SAY, and no seat says anything.

- `status/<SEAT>.json` had **no writer at all** (`board.py say` is long gone) and
  the four files were 1–7 days old. **They are deleted.**
- *"CHECK holds the Bridge"* was a lease nobody releases.
- *"STALE 6m"* was the **ledger's** age, not the page's.

⭐ **Now:** `measured()` in `status_server.py` reads `ps` for the window, the
append-only ledger for activity, a **TCP probe on :5174** for the bridge, and git
for durability — and every tile prints the instrument that produced it.

🔑 It rides on **both** `/data` and `/board`. **DECK is the default view and polls
`/board` only**, so fixing the legacy view alone fixed nothing the owner could see —
that mistake cost a round trip. Stale-while-revalidate, warmed at startup, because
a cold reading took 20 s under load and the board answered `000`.

⛔ **Do not re-introduce a tile a seat has to remember to update.** Full rule in
`infrastructure/agents/REP.md`.

## ⭐ Node 22 is now installed

User-local, `~/.local/bin/node`, no sudo. **Lint every board view with
`node --check` before serving it.** REP shipped the board twice in one session
saying "no JS engine here" when installing one took 40 seconds.

## Closed this session

- **`VALIDATOR_READS_LANGUAGE_FILES_1`** (`6494c698`) — the pre-load gate read
  `Languages/*.xml` as patch files and reported `FAIL` on a clean mod. Now
  `OK TOTAL — 0 errors`.
- **`TEXTURE_RESOLVER_MISSES_TWO_FORMS_1`** (`776be62f`) — four missing rungs, not
  two. Misses **70 → 0** on the 190-plant fixture, and `Plant_Berry_Leafless`
  correctly stays unresolved. Evidence in `infrastructure/state/evidence/`.

Two runnable checks now live in the repo: `test_resolve_texture.py` (instant) and
`verify_resolve_texture_live.py` (~4 min). ⚠️ The fast one caught a bug the slow
fixture had **masked**.

## Owner rulings routed today

1. **The weapons floor is bows and knives, for anyone** — and a bare-handed pawn is
   fixed by **cheapening a weapon, never by raising `weaponMoney`**. That reverses
   standing advice in three open items. `WEAPON_FLOOR_BOWS_KNIVES_1`.
2. **HorrorWastes goes in the frozen band just PAST the terminator**, roughly
   arc 100–130 — **not** the deep nightside. `arc >= 140` is superseded.
3. **The coldest ground carries only the most alien life.** That is a **casting**
   constraint on `BIOME_CREATURE_CAST_1`, and it means `AB_RockyCrags` cannot be
   cast as one list — two casts at its two ends.

## Open, and not REP's

- **The fauna question** — 560 animals no mod ever made wild. Recommendation on
  file: cast from the 462, reach into the 560 only for a biome's missing
  super-huge. ⛔ The owner said *"DECIDE is working on the animals"* — do not chase it.
- **`FOUR_CULTURES_NO_FACTION_1`**, filed for DECIDE. 12 Jawa cultures, 8 factions ⇒
  Blackstar, DeepDesert, Empire and Homestead have **no FactionDef**, and their 16
  pawnkinds have nothing to field them. 🔑 The world is hand-made once and frozen,
  so this must be fixed **before** he builds it.
