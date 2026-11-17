using RimMandrake.GimmeSomeSlack.Core;
using UnityEngine;
using Verse;

namespace RimMandrake.GimmeSomeSlack
{
    /// <summary>The one door to ContentFinder for a path this mod builds (Core/TexPath.cs): a path no file system takes is logged once
    /// with its text and its caller and answered null, as a missing texture is.</summary>
    internal static class SafeTex
    {
        public static Texture2D Get(string path, bool reportFailure = false, [System.Runtime.CompilerServices.CallerMemberName] string caller = null,
                                    [System.Runtime.CompilerServices.CallerFilePath] string file = null)
        {
            int bad = TexPath.BadAt(path);
            if (bad != -1)
            {
                Log.ErrorOnce("[GimmeSomeSlack] a texture was asked for by a path no file system takes (" + (bad == -2 ? "empty" : "character " + bad)
                              + "): \"" + TexPath.Shown(path) + "\", from " + caller + " in " + System.IO.Path.GetFileName(file ?? "?")
                              + " (RIMMANDRAKE_TRACE_GSS_ILLEGAL_PATH_ONLY_ON_FIRST_START)", ("gss-texpath:" + path + caller).GetHashCode());
                return null;
            }
            return ContentFinder<Texture2D>.Get(path, reportFailure);
        }
    }
}
