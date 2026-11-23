An agent is in the middle of a task. It meets ONE sentence of a rule file. The agent must be able to point at what each
noun and each verb's object means IN ONE STEP. The agent will not search other documents.

The agent already knows, and you must never flag:
- ordinary English, in its ordinary sense at that line;
- words of programming, git, shell, Windows, Linux, Claude Code, Codex and GPT, PC hardware and RimWorld modding (a def,
  a tick, a pawn, a commit, a clone, a hook, a unit, a timer, a selftest, a ledger);
- every term in the GLOSSARY below;
- anything that the sentence explains, or that the SECTION shown with the sentence explains or introduces;
- anything that carries its own pointer: a path, a command, an item id (RIMMANDRAKE_...), a def name, a tool name in code
  marks, a section mark and its heading;
- anything inside quote marks: quoted words are never changed;
- "he", "him", "the owner" and "Mandrake": the owner of the project.

Flag a term ONLY when all three are true:
1. The term names something particular to this project: a coined label, a nickname, a code, a one-word name of a process,
   place, machine, part or event. Or the term is a verb with no object. Or the term is a second name for one thing.
2. Nothing in the sentence, its section or the glossary says what the term is.
3. Two careful readers could take the term for two different things, and would then ACT differently or could not act.

Kinds:
- "undefined": the term resolves to nothing. Example: "a trailing commit (the belt carries those)": which belt?
- "synonym": a second name for a thing that this same section already names differently, so a reader cannot tell that the
  two names are one thing. Put the first name in "why".
- "no-object": a verb whose object is not named. Example: "Revert if a clone strands work": revert what?

A sentence that reads plainly to a developer who is new to the project, with the section in view, is NOT a fault. Most
sentences have no fault. Do not flag style, length, a word that could be more exact, or a thing you would like to know
more about. When in doubt, do not flag.

GLOSSARY
{LEXICON}

FILE: {PATH}
Its opening lines:
{OPENING}

{BODY}

Answer with one JSON object and nothing else:
{"faults": [{"n": <sentence number>, "term": "<the exact words from the sentence>", "kind": "undefined|synonym|no-object", "why": "<the two readings, or what the reader cannot do, in under 25 words>", "define_at": "<where the definition goes: this sentence, or a line of this section quoted by its first words, or the glossary>"}]}
