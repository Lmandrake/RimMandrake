// RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START: the guard every built texture path goes through (Core/TexPath.cs, SafeTex.cs).
using System;
using System.IO;
using System.Linq;
using RimMandrake.GimmeSomeSlack.Core;

namespace RimMandrake.GimmeSomeSlack.SelfTest
{
    internal static class TexPathChecks
    {
        private static void Check(bool ok, string msg) => Program.Check(ok, "texture paths: " + msg);

        public static void Run()
        {
            Check(TexPath.BadAt("RimMandrake/GimmeSomeSlack/Styles/ExtCord/Blue/Junction_X_p12") == -1, "a real texture path passes");
            Check(TexPath.BadAt("RimMandrake/GimmeSomeSlack/Styles/Modern|Blue/PowerSwitch") == "RimMandrake/GimmeSomeSlack/Styles/Modern|Blue/PowerSwitch".IndexOf('|'), "planted: a bar in a look's name is refused at its place");
            Check(TexPath.BadAt("RimMandrake/GimmeSomeSlack/Strand\0Taped".Replace("\\0", "\0")) >= 0, "planted: a NUL is refused");
            Check(TexPath.BadAt("a\tb") == 1 && TexPath.BadAt("a\"b") == 1 && TexPath.BadAt("a<b") == 1 && TexPath.BadAt("a>b") == 1, "planted: a tab, a quote and angle brackets are refused");
            Check(TexPath.BadAt(null) == -2 && TexPath.BadAt("") == -2, "no path at all is refused");
            Check(TexPath.Shown("a\0b|c") == "a\\u0000b|c", "a refused path is shown with its unprintable characters spelled out (" + TexPath.Shown("a\0b|c") + ")");
            // every character the platform's own Path.Combine refuses is refused here first
            Check(Path.GetInvalidPathChars().All(c => TexPath.BadAt("x" + c + "y") == 1), "every character Path.Combine refuses on this platform is refused");
            // (that no call in the mod reaches ContentFinder with a built path but through the guard is read off the repo's own files:
            // northstar/selftest_gss_texpath.py; the staged copy this runs from can hold files the mod no longer has)
        }
    }
}
