// Gimme Some Slack core: Verse-free (see CordMath.cs header).
using System;
using System.Collections;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Text;

namespace RimMandrake.GimmeSomeSlack.Core
{
    /// <summary>GPT pre-release B24: a text fingerprint of every public static field of a settings class (a list field by its
    /// elements, not its type name), so closing the settings window re-prints every map only when something changed.</summary>
    public static class SettingsPrint
    {
        public static string Of(Type settings)
        {
            var sb = new StringBuilder();
            foreach (FieldInfo f in settings.GetFields(BindingFlags.Public | BindingFlags.Static).OrderBy(f => f.Name, StringComparer.Ordinal))
            {
                if (f.IsLiteral || f.IsInitOnly && !(typeof(IEnumerable).IsAssignableFrom(f.FieldType) && f.FieldType != typeof(string))) continue;
                sb.Append(f.Name).Append('=');
                object v = f.GetValue(null);
                if (v is IEnumerable e && !(v is string))
                {
                    sb.Append('[');
                    foreach (object o in e) sb.Append(Convert.ToString(o, CultureInfo.InvariantCulture)).Append(',');
                    sb.Append(']');
                }
                else sb.Append(Convert.ToString(v, CultureInfo.InvariantCulture));
                sb.Append('|');
            }
            return sb.ToString();
        }
    }
}
