"""Acceptance test for RIMMANDRAKE_FIX_PYRE_HAWK_LETTER_BLANKS_FOUR_NAMED_SLOTS (python3, offline).

RimWorld's GrammarResolverSimple reads `{NAME_sub}` as argument NAME with sub-symbol `sub` (as in {PAWN_pronoun}).
So a C# `.Named("A_B")` can never fill `{A_B}`: the resolver looks for an argument "A" and asks it for "B", and the
slot comes out blank. This scans Pyrelands' C# for .Named("...") labels holding '_' that a Keyed string uses as {...}.
Exit 0 = none; 1 = at least one (each printed)."""
import glob, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 7))
MOD = os.path.join(ROOT, "src", "RimMandrake", "Pyrelands")
named = set()
for f in glob.glob(os.path.join(MOD, "Source", "**", "*.cs"), recursive=True):
    named |= set(re.findall(r'\.Named\(\s*"([A-Za-z0-9]+_[A-Za-z0-9_]+)"\s*\)', open(f, encoding="utf-8", errors="replace").read()))
used = {}
for f in glob.glob(os.path.join(MOD, "Languages", "**", "*.xml"), recursive=True):
    for tag in re.findall(r"\{([A-Za-z0-9_]+)\}", open(f, encoding="utf-8", errors="replace").read()):
        used.setdefault(tag, os.path.relpath(f, ROOT))
bad = sorted(n for n in named if n in used)
print("%d named argument(s) with '_' that a Keyed string uses as a whole symbol" % len(bad))
for n in bad:
    print("  {%s} in %s" % (n, used[n]))
sys.exit(1 if bad else 0)
