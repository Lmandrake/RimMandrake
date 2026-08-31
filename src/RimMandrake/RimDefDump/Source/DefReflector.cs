using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using RimWorld;
using Verse;

namespace RimMandrake.RimDefDump
{
    /// <summary>
    /// Reflects a Def (or any object hanging off one) into JSON.
    ///
    /// The whole point of this tool is post-resolution truth, so the reflector
    /// deliberately reads the LIVE object graph rather than re-parsing XML. That
    /// graph is hostile in three specific ways, and each has a rule here:
    ///
    ///  1. It is cyclic. Def A references Def B references Def A, forever.
    ///     Rule: a Def encountered below the root is written as its defName
    ///     string, never expanded. The root Def is the only one expanded.
    ///  2. It reaches into Unity. Textures, Materials and Graphics are huge,
    ///     useless to us, and touching some of them before load completes can
    ///     throw.
    ///     Rule: anything in the UnityEngine namespace is skipped by type.
    ///  3. Individual field reads can throw for mod-specific reasons.
    ///     Rule: every read is wrapped; a failure records the exception rather
    ///     than losing the whole def.
    /// </summary>
    public static class DefReflector
    {
        /// <summary>Depth cap for nested non-Def objects hanging off a def.</summary>
        public const int DefaultMaxDepth = 6;

        /// <summary>Guard against a runaway lazy sequence hanging the game load.</summary>
        private const int MaxSequenceItems = 4096;

        /// <summary>
        /// Fields the engine GENERATES at load rather than reading from XML.
        /// They are derived data, so they tell us nothing about what a mod
        /// author wrote — and they are enormous.
        ///
        /// Measured on the first full run (562 mods, 2026-08-10):
        /// race.lifeStageWorkSettings is a (workType x lifeStage) cross-product
        /// that reached 2,212 entries and 185 KB on a single def — about 94% of
        /// that record. Across the dump it was most of 729 MB of animals.json.
        /// It never tripped the MaxSequenceItems guard because 2,212 is a
        /// perfectly ordinary list length; the problem is the number of records
        /// carrying one, not any single list.
        ///
        /// Matched by field NAME, so keep entries specific enough not to
        /// collide with an unrelated field on another type.
        /// </summary>
        private static readonly HashSet<string> SkippedFieldNames = new HashSet<string>
        {
            "lifeStageWorkSettings",
        };

        // Reflection is the dominant cost when dumping tens of thousands of
        // defs, so field lists are resolved once per type and cached.
        private static readonly Dictionary<Type, FieldInfo[]> fieldCache = new Dictionary<Type, FieldInfo[]>();

        private static FieldInfo[] FieldsOf(Type t)
        {
            FieldInfo[] cached;
            if (fieldCache.TryGetValue(t, out cached)) return cached;

            var keep = new List<FieldInfo>();
            // DeclaredOnly plus a manual base walk, so we get fields from every
            // level of the hierarchy without duplicates where a subclass hides a
            // base field with `new`.
            for (Type cur = t; cur != null && cur != typeof(object); cur = cur.BaseType)
            {
                FieldInfo[] fields = cur.GetFields(BindingFlags.Public | BindingFlags.NonPublic
                                                   | BindingFlags.Instance | BindingFlags.DeclaredOnly);
                for (int i = 0; i < fields.Length; i++)
                {
                    FieldInfo f = fields[i];
                    if (f.IsStatic) continue;
                    // Compiler-generated backing fields and closures add noise
                    // without adding information.
                    if (f.Name.IndexOf('<') >= 0) continue;
                    if (SkippedFieldNames.Contains(f.Name)) continue;
                    if (IsSkippedType(f.FieldType)) continue;
                    keep.Add(f);
                }
            }
            FieldInfo[] arr = keep.ToArray();
            fieldCache[t] = arr;
            return arr;
        }

        private static bool IsSkippedType(Type t)
        {
            if (t == null) return true;
            if (typeof(Delegate).IsAssignableFrom(t)) return true;

            string ns = t.Namespace ?? "";
            if (ns.StartsWith("UnityEngine", StringComparison.Ordinal)) return true;
            if (ns.StartsWith("System.Reflection", StringComparison.Ordinal)) return true;
            if (ns.StartsWith("System.Threading", StringComparison.Ordinal)) return true;
            if (ns.StartsWith("System.IO", StringComparison.Ordinal)) return true;
            return false;
        }

        /// <summary>Write one Def as a full JSON object, expanded.</summary>
        public static void WriteDef(JsonWriter w, Def def, int maxDepth = DefaultMaxDepth)
        {
            w.StartObject();

            // Identity block first, so the file is readable and greppable even
            // before anything parses it.
            w.Prop("defName", def.defName);
            w.Prop("defType", def.GetType().Name);
            w.Prop("defTypeFull", def.GetType().FullName);
            w.Prop("label", SafeString(def.label));

            // THE reason this tool exists, part 1: the true shortHash, resolved
            // by the game across the whole loaded set with collisions bumped.
            // Utils/animal_inventory.py can only ever produce a candidate.
            w.Prop("shortHash", (long)def.shortHash);

            // THE reason this tool exists, part 2: live provenance. Which mod
            // actually won the def after load order and overrides settled.
            ModContentPack pack = null;
            try { pack = def.modContentPack; }
            catch { }

            if (pack != null)
            {
                w.Prop("modName", SafeString(pack.Name));
                w.Prop("packageId", pack.PackageId);
            }
            else
            {
                w.Name("modName"); w.Null();
                w.Name("packageId"); w.Null();
            }

            WriteClassification(w, def);

            w.Name("fields");
            WriteObjectBody(w, def, 0, maxDepth, new List<object>());

            w.EndObject();
        }

        /// <summary>
        /// THE reason this tool exists, part 3: authoritative category flags.
        ///
        /// "Is this a weapon?" is a COMPUTED property in C# (ThingDef.IsWeapon),
        /// not an XML field. An offline scan can only approximate it from shape
        /// — does the def have weaponTags, does it have an apparel node — and
        /// those approximations will disagree with the game at the margins.
        ///
        /// Emitting the real answers turns that disagreement from an invisible
        /// source of false diffs into something measurable: the offline
        /// classifier can be calibrated against this, and any residual
        /// mismatch is reported as its own category rather than being mistaken
        /// for a content change.
        /// </summary>
        private static void WriteClassification(JsonWriter w, Def def)
        {
            // TerrainDef gets one flag: can the FLOOR take the vanilla paint
            // system (TerrainDef.isPaintable). Added 2026-08-28 for offline
            // template generation - the general reflector drops this field, and
            // paintability inherits through ParentName chains, so only the
            // post-inheritance dump can answer it.
            var terr = def as TerrainDef;
            if (terr != null)
            {
                w.Name("is");
                w.StartObject();
                Flag(w, "paintable", delegate { return terr.isPaintable; });
                w.EndObject();
                return;
            }

            var td = def as ThingDef;
            if (td == null) return;

            w.Name("is");
            w.StartObject();
            Flag(w, "weapon", delegate { return td.IsWeapon; });
            Flag(w, "meleeWeapon", delegate { return td.IsMeleeWeapon; });
            Flag(w, "rangedWeapon", delegate { return td.IsRangedWeapon; });
            Flag(w, "apparel", delegate { return td.IsApparel; });
            Flag(w, "medicine", delegate { return td.IsMedicine; });
            Flag(w, "drug", delegate { return td.IsDrug; });
            Flag(w, "stuff", delegate { return td.IsStuff; });
            Flag(w, "ingestible", delegate { return td.IsIngestible; });
            Flag(w, "corpse", delegate { return td.IsCorpse; });
            Flag(w, "buildingArtificial", delegate { return td.IsBuildingArtificial; });
            // Vanilla paint (Building.ChangePaint): def.building.paintable, which
            // inherits - GravshipHull is paintable only via Wall's ParentName, so
            // raw XML scans answer this WRONG. Added 2026-08-28 for offline
            // template generation and rimplace's paint lint.
            Flag(w, "paintable", delegate { return td.building != null && td.building.paintable; });
            Flag(w, "plant", delegate { return td.IsPlant; });
            Flag(w, "frame", delegate { return td.IsFrame; });
            Flag(w, "blueprint", delegate { return td.IsBlueprint; });
            Flag(w, "minifiable", delegate { return td.Minifiable; });
            Flag(w, "everHaulable", delegate { return td.EverHaulable; });

            // Pawn-side flags. race is null for everything that is not a pawn,
            // so these also encode "is this a pawn at all".
            RaceProperties race = null;
            try { race = td.race; }
            catch { }
            if (race != null)
            {
                Flag(w, "pawn", delegate { return true; });
                Flag(w, "animal", delegate { return race.Animal; });
                Flag(w, "humanlike", delegate { return race.Humanlike; });
                Flag(w, "toolUser", delegate { return race.ToolUser; });
                Flag(w, "mechanoid", delegate { return race.IsMechanoid; });
                Flag(w, "flesh", delegate { return race.IsFlesh; });
            }

            // The coarse engine category (Item / Building / Pawn / Plant / ...).
            try { w.Prop("category", td.category.ToString()); }
            catch { }

            w.EndObject();
        }

        private delegate bool BoolGetter();

        /// <summary>
        /// These are computed properties, and a mod can make any of them throw.
        /// A classifier that dies on one bad def is worse than useless, so a
        /// failure is recorded rather than propagated.
        /// </summary>
        private static void Flag(JsonWriter w, string name, BoolGetter get)
        {
            try { w.Prop(name, get()); }
            catch (Exception ex) { w.Prop(name, "<failed:" + ex.GetType().Name + ">"); }
        }

        /// <summary>
        /// Write a non-Def object (e.g. a ThingDef's RaceProperties) as a
        /// nested JSON object, using the same rules as a full def dump.
        /// </summary>
        public static void WriteNested(JsonWriter w, object o, int maxDepth = DefaultMaxDepth)
        {
            if (o == null) { w.Null(); return; }
            WriteObjectBody(w, o, 0, maxDepth, new List<object>());
        }

        /// <summary>Write an arbitrary value at the given depth.</summary>
        private static void WriteValue(JsonWriter w, object v, int depth, int maxDepth, List<object> path)
        {
            if (v == null) { w.Null(); return; }
            if (w.TryWriteSimple(v)) return;

            Type t = v.GetType();

            // System.Type shows up constantly (thingClass, workerClass,
            // compClass). Expanding it would drag in the reflection graph.
            var asType = v as Type;
            if (asType != null) { w.Str(asType.FullName); return; }

            if (IsSkippedType(t)) { w.Str("<skipped:" + t.Name + ">"); return; }

            // Rule 1: nested Defs collapse to their defName. This is what keeps
            // the graph acyclic and the files a sane size.
            var asDef = v as Def;
            if (asDef != null) { w.Str(asDef.defName); return; }

            // ModContentPack is reachable from several defs and is enormous.
            var asPack = v as ModContentPack;
            if (asPack != null)
            {
                w.StartObject();
                w.Prop("name", SafeString(asPack.Name));
                w.Prop("packageId", asPack.PackageId);
                w.EndObject();
                return;
            }

            if (depth >= maxDepth) { w.Str("<maxdepth:" + t.Name + ">"); return; }

            // Dictionaries enumerate as KeyValuePair, whose Key/Value are
            // PROPERTIES, not fields, so the generic field walk would emit {}.
            // race.wildBiomes is exactly this shape, so it matters.
            var asDict = v as IDictionary;
            if (asDict != null)
            {
                w.StartArray();
                foreach (DictionaryEntry e in asDict)
                {
                    w.StartObject();
                    w.Name("key"); WriteValue(w, e.Key, depth + 1, maxDepth, path);
                    w.Name("value"); WriteValue(w, e.Value, depth + 1, maxDepth, path);
                    w.EndObject();
                }
                w.EndArray();
                return;
            }

            var asEnum = v as IEnumerable;
            if (asEnum != null)
            {
                w.StartArray();
                try
                {
                    int n = 0;
                    foreach (object item in asEnum)
                    {
                        if (n++ >= MaxSequenceItems) { w.Str("<truncated>"); break; }
                        WriteValue(w, item, depth + 1, maxDepth, path);
                    }
                }
                catch (Exception ex) { w.Str("<enumerate-failed:" + ex.GetType().Name + ">"); }
                w.EndArray();
                return;
            }

            // Reference cycle guard for plain objects. Reference equality only:
            // invoking a mod's Equals override here would be asking for trouble.
            if (!t.IsValueType)
            {
                for (int i = 0; i < path.Count; i++)
                {
                    if (ReferenceEquals(path[i], v)) { w.Str("<cycle:" + t.Name + ">"); return; }
                }
            }

            WriteObjectBody(w, v, depth, maxDepth, path);
        }

        private static void WriteObjectBody(JsonWriter w, object obj, int depth, int maxDepth, List<object> path)
        {
            Type t = obj.GetType();
            bool tracked = !t.IsValueType;
            if (tracked) path.Add(obj);

            w.StartObject();

            // Record the concrete type, because it is often the entire content
            // of an entry: knowing a comps element is CompProperties_Milkable is
            // exactly what the animal inventory wants to know.
            w.Prop("$type", t.Name);

            FieldInfo[] fields = FieldsOf(t);
            for (int i = 0; i < fields.Length; i++)
            {
                FieldInfo f = fields[i];
                object val;
                try { val = f.GetValue(obj); }
                catch (Exception ex)
                {
                    w.Name(f.Name);
                    w.Str("<read-failed:" + ex.GetType().Name + ">");
                    continue;
                }
                if (val == null) continue; // omit nulls; these files are big enough

                w.Name(f.Name);
                try { WriteValue(w, val, depth + 1, maxDepth, path); }
                catch (Exception ex) { w.Str("<write-failed:" + ex.GetType().Name + ">"); }
            }

            w.EndObject();

            if (tracked) path.RemoveAt(path.Count - 1);
        }

        /// <summary>
        /// Labels and descriptions are free text from hundreds of authors. The
        /// JSON writer already escapes correctly, so this only flattens hard
        /// line breaks to keep one def on one logical line for grep.
        /// </summary>
        public static string SafeString(string s)
        {
            if (string.IsNullOrEmpty(s)) return s;
            char[] buf = s.ToCharArray();
            for (int i = 0; i < buf.Length; i++)
            {
                // Compared numerically to keep this file free of escape
                // sequences that tooling likes to mangle.
                if (buf[i] == (char)10 || buf[i] == (char)13) buf[i] = (char)32;
            }
            return new string(buf);
        }
    }
}
