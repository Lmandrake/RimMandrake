// Vector runner for JawaBenchCondCore.cs (the PRODUCTION file): reads Utils/conds_vectors.json on stdin and prints
// JawaBenchCondCore.RunVectorsText - one "name<TAB>canonical result" line per vector, "\n" endings, UTF-8 without BOM.
// Driven by src/RimMandrake/Utils/selftest_conds_vectors.py, which requires it byte-identical to conds.py's output.
using System;
using System.IO;
using System.Text;

namespace JawaBench.BridgeTools
{
    internal static class Program
    {
        static int Main()
        {
            string text;
            using (var r = new StreamReader(Console.OpenStandardInput(), new UTF8Encoding(false)))
                text = r.ReadToEnd();
            string outText = JawaBenchCondCore.RunVectorsText(text);
            var bytes = new UTF8Encoding(false).GetBytes(outText);
            using (var o = Console.OpenStandardOutput())
                o.Write(bytes, 0, bytes.Length);
            return 0;
        }
    }
}
