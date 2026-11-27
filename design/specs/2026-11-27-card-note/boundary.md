# Boundary: a note by card in one command (`src/RimMandrake/rimflow/card_note.py`)

Item RIMMANDRAKE_BUILD_CARD_NOTE_48_CARD_NOTES_BY_HAND (script candidate 5 of
`design/specs/2026-11-26-script-candidates/one_page.md`). In 7 days: 48 `--by-card` commands and 142 ledger writes
within 15 minutes of an answer, each typed by hand. The model now gives the item and the consequence sentence. The tool
finds the card and the real `cli.py note` stamps it.

Code: `src/RimMandrake/rimflow/card_note.py` (all of it). It calls `src/RimMandrake/rimflow/cli.py` (`note --by-card`)
and `src/RimMandrake/rimflow/card_capture.py` (`store_path`, `norm`, `WINDOW_S`).

## ACCEPTS

- **the-call.** `card_note.py <ITEM> "<consequence sentence>" [--card <key or words>] [--seat S] [--publish] [--dry-run]`.
  `--dry-run` prints the `cli.py note` argument list and writes nothing.
- **the-card-store.** The file that `card_capture.store_path()` names (`RM_CARDS_STORE` overrides it). Each line is one
  answered card. The hook `capture_card_answer.py` writes it.
- **a-card-key-or-words.** `--card` is a card key (exact, or a prefix of 6 or more characters), or words that all occur
  in the card's key, questions, headers or picked answers. No `--card`: the card with the newest `answered` time.

## DOES NOT SURVIVE

- **a-card-older-than-the-window.** `cli.py` reads cards answered in the last `card_capture.WINDOW_S` (7 days). An older
  card is refused by name: the note would not carry the whole card.
- **a-wrong-consequence.** The tool does not read the sentence. The model owns what it says.

## PROMISES

- **note-carries-the-whole-card.** One call writes ONE `note` event on the item. The event is seat OWNER, has
  `byCard` and a `card` field with every question of the card, the picked option and its description. It has no
  `ownerSaid`.
- **bare-call-takes-the-card-answered-last.** With no `--card`, the card with the newest `answered` time is used, wherever
  it sits in the file.
- **no-card-in-the-store-is-refused-by-name.** An empty store, a `--card` that fits no card, and a store that cannot be
  read each exit non-zero, write nothing and name the store path. The empty store says what was looked for. The
  unreadable store says `could not read`. A `--card` that fits several cards is refused, and the keys are listed.
- **the-consequence-sentence-is-the-note-text.** The `text` of the event is the sentence, as given. An empty sentence
  is refused.
- **a-card-is-named-by-key-or-words-and-two-fits-are-refused.** Words that fit one question of a many-question card
  stamp that question only. A key is exact. Words that fit two cards are refused.
- **a-cli-past-its-deadline-reads-unmeasured.** A `cli.py note` that runs longer than `NOTE_DEADLINE_S` is stopped.
  The tool exits 5 and says UNMEASURED, because the note may stand written and not landed. The line names
  `rimflow show <ITEM>`. `NOTE_DEADLINE_S` is a hang guard of at least 10 times a published ledger write (over 120 s
  measured 2026-11-27).

## LIFE CYCLES

- **a model, after a question card is answered:** `card_note.py <ITEM> "<sentence>"` → `read_store` → `choose` →
  `cli.py note --by-card` → `card_capture.find` stamps the card on the event.
- **the host's card hook:** writes the store before the call. This tool never writes the store.

Later lists beside this page: `polish.md` (none yet).
