#!/usr/bin/env python3
"""Mutation proof for the RimDefDump fuzz: plants each defect in the JSON writer (JsonWriter.cs) and the kernel (RM_DumpKernel.cs), demands the
fuzz FAILS, restores each file byte-identical. Exit 0 only if every mutation was caught.

    python3 src/RimMandrake/Utils/mutate_rimdefdump_fuzz.py [name-substring]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutate_explosivegrowth_fuzz import run_mutations  # noqa: E402

KERNEL = "src/RimMandrake/RimDefDump/Source/Kernel/RM_DumpKernel.cs"
WRITER = "src/RimMandrake/RimDefDump/Source/JsonWriter.cs"
KERNEL_MUTATIONS = [
    ("capture id length 19", "public const int CaptureIdLength = 20;", "public const int CaptureIdLength = 19;"),
    ("capture id accepts a colon", "if (i == 4 || i == 7 || i == 13 || i == 16) { if (c != '-') return false; }", "if (i == 4 || i == 7 || i == 13 || i == 16) { if (c != '-' && c != ':') return false; }"),
    ("capture id accepts lowercase t", "else if (i == 10) { if (c != 'T') return false; }", "else if (i == 10) { if (c != 'T' && c != 't') return false; }"),
    ("capture id ignores the Z", "else if (i == 19) { if (c != 'Z') return false; }", "else if (i == 19) { }"),
    ("capture id accepts letters in digits", "else if (c < '0' || c > '9') return false;", "else if (c < '0' || c > 'z') return false;"),
    ("retention counts frozen captures", "if (d.Value) continue;", ""),
    ("retention deletes frozen captures", "if (d.Value) continue;", "if (!d.Value) { }"),
    ("retention takes junk names", "if (!IsCaptureId(d.Key)) continue;", ""),
    ("retention sorts case-insensitively", "ids.Sort(StringComparer.Ordinal);", "ids.Sort(StringComparer.OrdinalIgnoreCase);"),
    ("retention keeps the oldest", "for (int i = 0; i < drop; i++) victims.Add(ids[i]);", "for (int i = 0; i < drop; i++) victims.Add(ids[ids.Count - 1 - i]);"),
    ("retention keeps one too few", "int drop = ids.Count - keepNewest;", "int drop = ids.Count - keepNewest + 1;"),
    ("retention keeps one too many", "int drop = ids.Count - keepNewest;", "int drop = ids.Count - keepNewest - 1;"),
    ("retention keeps two", "public const int KeepNewest = 3;", "public const int KeepNewest = 2;"),
    ("safe name keeps a plus", "c == '.' || c == '_' || c == '-' ? c : '_'", "c == '.' || c == '_' || c == '-' || c == '+' ? c : '_'"),
    ("safe name drops digits", "char.IsLetterOrDigit(c) ||", "char.IsLetter(c) ||"),
    ("safe name drops dashes", "c == '.' || c == '_' || c == '-' ?", "c == '.' || c == '_' ?"),
    ("stem clash overwrites", "if (assigned.Add(stem)) return stem;\n            clashed = true;", "if (assigned.Add(stem)) return stem;\n            clashed = true; return stem;"),
    ("stem clash not flagged", "            clashed = true;\n            string asm", "            string asm"),
    ("stem second clash reuses the first suffix", "for (int i = 2; !assigned.Add(candidate); i++) candidate = stem + \"__\" + asm + \"_\" + i;", "if (!assigned.Add(candidate)) return candidate;"),
    ("stem suffix skips the assembly", "string candidate = stem + \"__\" + asm;", "string candidate = stem + \"__\";"),
    ("stem set is case-sensitive in effect", "if (assigned.Add(stem)) return stem;", "if (assigned.Add(stem) || assigned.Contains(stem.ToLowerInvariant()) == false && false) return stem;"),
]
WRITER_MUTATIONS = [
    ("quote not escaped", "case '\"': writer.Write(\"\\\\\\\"\"); break;", ""),
    ("backslash not escaped", "case '\\\\': writer.Write(\"\\\\\\\\\"); break;", ""),
    ("newline not escaped", "case '\\n': writer.Write(\"\\\\n\"); break;", ""),
    ("control limit 0x1f", "if (c < 0x20 || c == 0x7f ||", "if (c < 0x1f || c == 0x7f ||"),
    ("surrogates written raw", "(c >= 0xd800 && c <= 0xdfff))", "false)"),
    ("high surrogate range short", "(c >= 0xd800 && c <= 0xdfff)", "(c >= 0xd800 && c <= 0xdbff)"),
    ("unicode escape uppercase width 3", "((int)c).ToString(\"x4\", CultureInfo.InvariantCulture)", "((int)c).ToString(\"x\", CultureInfo.InvariantCulture)"),
    ("float widened to double", "if (float.IsNaN(v) || float.IsInfinity(v)) { writer.Write(\"null\"); return; }\n            writer.Write(v.ToString(\"R\", CultureInfo.InvariantCulture));", "if (float.IsNaN(v) || float.IsInfinity(v)) { writer.Write(\"null\"); return; }\n            writer.Write(((double)v).ToString(\"R\", CultureInfo.InvariantCulture));"),
    ("double precision lost", "writer.Write(v.ToString(\"R\", CultureInfo.InvariantCulture));\n        }\n\n        // A `float`", "writer.Write(v.ToString(\"G6\", CultureInfo.InvariantCulture));\n        }\n\n        // A `float`"),
    ("NaN written raw", "if (double.IsNaN(v) || double.IsInfinity(v)) { writer.Write(\"null\"); return; }", ""),
    ("infinity written", "if (float.IsNaN(v) || float.IsInfinity(v)) { writer.Write(\"null\"); return; }", "if (float.IsNaN(v)) { writer.Write(\"null\"); return; }"),
    ("ulong through double", "writer.Write(v.ToString(CultureInfo.InvariantCulture));\n        }\n\n        public void Str", "writer.Write(((double)v).ToString(\"R\", CultureInfo.InvariantCulture));\n        }\n\n        public void Str"),
    ("simple ulong narrowed", "Number(Convert.ToUInt64(v, CultureInfo.InvariantCulture)); return true;", "Number(Convert.ToInt64(v, CultureInfo.InvariantCulture)); return true;"),
    ("simple float widened", "Number((float)v); return true;", "Number(Convert.ToDouble(v, CultureInfo.InvariantCulture)); return true;"),
    ("prop float widened", "public void Prop(string name, float v) { Name(name); Number(v); }", "public void Prop(string name, float v) { Name(name); Number((double)v); }"),
    ("comma between members dropped", "if (!atContainerStart) writer.Write(',');", ""),
    ("comma before the first member", "if (!atContainerStart) writer.Write(',');", "writer.Write(',');"),
    ("name separator dropped", "writer.Write(':');", ""),
    ("end object leaves the container open for commas", "writer.Write('}'); atContainerStart = false; }", "writer.Write('}'); atContainerStart = true; }"),
    ("end array leaves the container open for commas", "writer.Write(']'); atContainerStart = false; }", "writer.Write(']'); atContainerStart = true; }"),
    ("indent depth never returns", "public void EndObject() { depth--;", "public void EndObject() {"),
    ("null string written as empty", "if (v == null) { writer.Write(\"null\"); return; }\n            WriteString(v);", "if (v == null) { WriteString(\"\"); return; }\n            WriteString(v);"),
    ("bool inverted", "writer.Write(v ? \"true\" : \"false\");", "writer.Write(v ? \"false\" : \"true\");"),
    ("enum written as number", "if (t.IsEnum) { Str(v.ToString()); return true; }", "if (t.IsEnum) { Number(Convert.ToInt64(v, CultureInfo.InvariantCulture)); return true; }"),
    ("char dropped", "case TypeCode.Char: Str(v.ToString()); return true;", ""),
]

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    rc = run_mutations(KERNEL, "selftest_rimdefdump_fuzz.py", KERNEL_MUTATIONS, only)
    rc2 = run_mutations(WRITER, "selftest_rimdefdump_fuzz.py", WRITER_MUTATIONS, only)
    sys.exit(rc or rc2)
