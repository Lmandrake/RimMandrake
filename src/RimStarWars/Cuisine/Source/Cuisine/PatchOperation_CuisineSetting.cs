using System.Reflection;
using System.Xml;
using Verse;

namespace RimMandrake.StarWars.Cuisine
{
    /// <summary>
    /// COLD_STORAGE_CUISINE_BUILD_PRESERVE_DISHES: run <see cref="match"/> only while the named public static bool of
    /// <see cref="RSW_CuisineSettings"/> is on, else <see cref="nomatch"/> (if any). A switched-off patch succeeds, so
    /// it logs nothing. Settings are read in RSW_CuisineMod's constructor, which runs before patches apply, so the
    /// value here is the player's saved one; a change takes effect at the next start.
    /// </summary>
    public class PatchOperation_CuisineSetting : PatchOperation
    {
        public string setting;
        public PatchOperation match;
        public PatchOperation nomatch;

        protected override bool ApplyWorker(XmlDocument xml)
        {
            FieldInfo f = setting.NullOrEmpty()
                ? null
                : typeof(RSW_CuisineSettings).GetField(setting, BindingFlags.Public | BindingFlags.Static);
            if (f == null || f.FieldType != typeof(bool))
            {
                Log.Error("[RimStarWars.Cuisine] PatchOperation_CuisineSetting: no bool setting named " + setting);
                return false;
            }
            PatchOperation op = (bool)f.GetValue(null) ? match : nomatch;
            return op == null || op.Apply(xml);
        }
    }
}
