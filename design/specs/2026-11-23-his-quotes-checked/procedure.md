# Procedure: check the owner's quoted words for imprecise language

A later run follows this brief. Promises: `boundary.md`. Never edit a character of a quote. Work in the rule line
beside it.

1. **List.** `python3 design/specs/2026-11-23-his-quotes-checked/extract_quotes.py --json <files>`. First plant one
   quote of each shape (ITALIC, PLAIN, CARD), one bold lead that starts with a quote mark, and one `"***` close. See
   them listed correctly. PLAIN and CARD rows are candidates: mark the ones that are not his NOT HIS.
2. **Source.** Find each quote in `owner_rulings.py --last 0 --grep <words>`, in `card_capture.py show <ITEM>`, or in
   `conversations/`. Read his WHOLE message, and the question or report that he answered. A quote in no record is
   "source not found", never "false". Text that names him as "he" is ours: look for what he really said.
3. **Later words.** Run `owner_rulings.py --since <the quote's date> --grep <subject>`. A later ruling on the subject
   replaces the quote, or narrows it. This is the commonest fault.
4. **Kind.** Order ("Do X"), opinion ("I think"), invitation ("Perhaps?") or question. Only an order, or his yes to a
   stated text, is a ruling. A card's label and its "Why:" text are ours; his pick is his.
5. **Words.** For each noun, pronoun, number in brackets and time word, name what it points at. Use the text that always
   travels with the quote, then the source.
6. **Readings.** Write each reading that stays plausible, and the act that it leads to. Same act: one reading.
7. **Verdict.**
   - CLEAR: one reading, and the rule line beside the quote is right.
   - ONE READING, LOOSE WORDS: the source settles the reading. Write it as the rule line, and name the source.
   - TWO READINGS: the readings lead to different acts, and no source settles them. Write the question. Do not pick.
   - RULE LINE DISAGREES: the rule line says more, less or other; or it is replaced; or it makes an opinion a ruling.
     Correct the rule line, and name the source or the later ruling.
8. **Repair.** Check that no live rewrite run holds the file. Edit. Compare every ITALIC quote with the base, character
   for character. Run the selftests that read the file.
9. **Stop** after one pass. A loose style that no reader could act on wrongly is CLEAR. Keep the questions few.
