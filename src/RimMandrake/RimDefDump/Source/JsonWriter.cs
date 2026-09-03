using System;
using System.Globalization;
using System.IO;

namespace RimMandrake.RimDefDump
{
    /// <summary>
    /// Minimal streaming JSON writer. Hand-rolled on purpose: RimWorld does not
    /// reliably ship a JSON library, and the project rule is no new dependencies.
    /// Streams straight to a TextWriter so a full def dump never has to be held
    /// in memory as one giant string.
    ///
    /// Usage is positional: Name("x") then any value/StartObject/StartArray call.
    /// The writer tracks comma placement itself; callers never write punctuation.
    /// </summary>
    public sealed class JsonWriter
    {
        private readonly TextWriter writer;
        private readonly bool indent;
        private int depth;

        // True until the first member of the current object/array is written, so
        // we know whether a separating comma is needed.
        private bool atContainerStart = true;

        // Set by Name(): the value that follows belongs to that member and must
        // not emit its own comma or line break.
        private bool suppressSeparator;

        // Cleared once anything has been written, so the document does not open
        // with a stray blank line before the root token.
        private bool atDocumentStart = true;

        public JsonWriter(TextWriter writer, bool indent = true)
        {
            this.writer = writer;
            this.indent = indent;
        }

        private void NewlineIndent()
        {
            if (!indent) return;
            if (atDocumentStart) return;
            writer.Write('\n');
            for (int i = 0; i < depth; i++) writer.Write("  ");
        }

        private void Separate()
        {
            if (suppressSeparator)
            {
                suppressSeparator = false;
                atContainerStart = false;
                atDocumentStart = false;
                return;
            }
            if (!atContainerStart) writer.Write(',');
            NewlineIndent();
            atContainerStart = false;
            atDocumentStart = false;
        }

        public void Name(string name)
        {
            Separate();
            WriteString(name);
            writer.Write(':');
            if (indent) writer.Write(' ');
            suppressSeparator = true;
        }

        public void StartObject() { Separate(); writer.Write('{'); depth++; atContainerStart = true; }
        public void EndObject() { depth--; if (!atContainerStart) NewlineIndent(); writer.Write('}'); atContainerStart = false; }
        public void StartArray() { Separate(); writer.Write('['); depth++; atContainerStart = true; }
        public void EndArray() { depth--; if (!atContainerStart) NewlineIndent(); writer.Write(']'); atContainerStart = false; }

        public void Null() { Separate(); writer.Write("null"); }
        public void Bool(bool v) { Separate(); writer.Write(v ? "true" : "false"); }

        public void Number(double v)
        {
            Separate();
            if (double.IsNaN(v) || double.IsInfinity(v)) { writer.Write("null"); return; }
            writer.Write(v.ToString("R", CultureInfo.InvariantCulture));
        }

        // A `float` routed through Number(double) gets widened to double BEFORE
        // round-trip formatting, and that widening is where the noise comes
        // from: 0.1f is not exactly representable in either width, but the two
        // roundings differ, so "R" on the widened value prints every digit of
        // that difference (0.1f -> "0.10000000149011612" instead of "0.1").
        // Formatting the float directly, at its own precision, is what makes
        // "R" round-trip losslessly the way it's supposed to.
        public void Number(float v)
        {
            Separate();
            if (float.IsNaN(v) || float.IsInfinity(v)) { writer.Write("null"); return; }
            writer.Write(v.ToString("R", CultureInfo.InvariantCulture));
        }

        public void Number(long v)
        {
            Separate();
            writer.Write(v.ToString(CultureInfo.InvariantCulture));
        }

        public void Str(string v)
        {
            Separate();
            if (v == null) { writer.Write("null"); return; }
            WriteString(v);
        }

        // --- convenience: name + value in one call -------------------------
        public void Prop(string name, string v) { Name(name); Str(v); }
        public void Prop(string name, bool v) { Name(name); Bool(v); }
        public void Prop(string name, long v) { Name(name); Number(v); }
        public void Prop(string name, double v) { Name(name); Number(v); }

        private void WriteString(string s)
        {
            writer.Write('"');
            for (int i = 0; i < s.Length; i++)
            {
                char c = s[i];
                switch (c)
                {
                    case '"': writer.Write("\\\""); break;
                    case '\\': writer.Write("\\\\"); break;
                    case '\n': writer.Write("\\n"); break;
                    case '\r': writer.Write("\\r"); break;
                    case '\t': writer.Write("\\t"); break;
                    case '\b': writer.Write("\\b"); break;
                    case '\f': writer.Write("\\f"); break;
                    default:
                        // Escape control chars and lone surrogates; mod text and
                        // translation keys are full of surprises, and one bad
                        // char would break the whole dump for the Python side.
                        if (c < 0x20 || c == 0x7f || (c >= 0xd800 && c <= 0xdfff))
                        {
                            writer.Write("\\u");
                            writer.Write(((int)c).ToString("x4", CultureInfo.InvariantCulture));
                        }
                        else writer.Write(c);
                        break;
                }
            }
            writer.Write('"');
        }

        /// <summary>
        /// Write an already-boxed primitive/string/enum. Returns false if the
        /// value is not a simple type, so the reflector can recurse instead.
        /// </summary>
        public bool TryWriteSimple(object v)
        {
            if (v == null) { Null(); return true; }
            Type t = v.GetType();
            if (t.IsEnum) { Str(v.ToString()); return true; }
            switch (Type.GetTypeCode(t))
            {
                case TypeCode.Boolean: Bool((bool)v); return true;
                case TypeCode.String: Str((string)v); return true;
                case TypeCode.Char: Str(v.ToString()); return true;
                case TypeCode.SByte:
                case TypeCode.Byte:
                case TypeCode.Int16:
                case TypeCode.UInt16:
                case TypeCode.Int32:
                case TypeCode.UInt32:
                case TypeCode.Int64:
                    Number(Convert.ToInt64(v, CultureInfo.InvariantCulture)); return true;
                case TypeCode.UInt64:
                    Number((double)Convert.ToUInt64(v, CultureInfo.InvariantCulture)); return true;
                case TypeCode.Single:
                    Number((float)v); return true;
                case TypeCode.Double:
                case TypeCode.Decimal:
                    Number(Convert.ToDouble(v, CultureInfo.InvariantCulture)); return true;
            }
            return false;
        }
    }
}
