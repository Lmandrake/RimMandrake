# CHRONICLE_NINEFOLD_DECOUPLE_1

## Spec
Decouple Aftermath from Ninefold per design/CHRONICLE_EVENT_SPINE.md
(the three violations listed on CHRONICLE_EVENT_SPINE_1).

## State — IMPLEMENTED 2026-09-09 (BENCH-orchestrated opus agent, 35e0756c)
ChronicleEvents spine in Aftermath (static event + reflection-friendly
Subscribe); Ninefold subscribes via AccessTools.TypeByName, zero
compile-time refs either direction; godTie God?→string (AftermathRites
XML unchanged, parses identically); builds 0W/0E, selftest 11/11; NOT
deployed (next shutdown window).

## Still owed before close
1. One live quicktest battle: reflection bind + StaticConstructorOnStartup
   ordering + the Sh'kaar delta actually applying.
2. Owner nod on the added spine kind `chronicle.rule.queued` (consumer:
   Ninefold — fires at rule-queue time; godTie-as-string forced it).
3. The Chronicle RENAME row (gated on this) must keep Subscribe/Raise/
   ChronicleEvent field names byte-identical — string-bound, breaks with
   no compile error; ChronicleSubscriber already probes the new name first.
4. Law-1 sweep candidates found: Inhabited hard-depends on
   mandrake.rm.injections; SacredGraffiti on mandrake.rm.graffiti.

## Owner nod RULED — question card, 2026-09-09

**Approved** — the added spine kind `chronicle.rule.queued` stands as
implemented. Owner noted he feels he may have already ruled on this before;
no such ruling was found on file, so this card is the ruling of record now.
Still owed before close: the live quicktest battle (item #1 above) and the
Chronicle RENAME row's byte-identical-name requirement (item #3).
