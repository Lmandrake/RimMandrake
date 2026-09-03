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
    ///     Rule: anything in the UnityEngine namespace is skipped by type,
    ///     except the small value structs in SafeUnityValueTypeNames
    ///     (Vector2/3/4, Color, Color32, Quaternion, Rect, Bounds) — those
    ///     carry no asset reference and are captured normally.
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

        /// <summary>
        /// Types whose field list could NOT be read in full, and why. Reading
        /// FieldInfo.FieldType resolves the field's type, which throws
        /// (TypeLoadException / FileNotFoundException) when that type lives in
        /// an assembly that never loaded — a soft mod dependency is exactly
        /// this shape, and the mod's own class loads fine because .NET resolves
        /// field types lazily. Type.GetFields can throw for the same reason.
        ///
        /// Unguarded that escapes FieldsOf -> WriteObjectBody -> WriteDef, and
        /// the caller in DefDumper deletes the whole def type's file: one bad
        /// field on one mod's class costs every def of that type. Guarded, the
        /// gap costs one field and is REPORTED as $fieldsError rather than
        /// leaving the record silently short.
        /// </summary>
        private static readonly Dictionary<Type, string> fieldErrors = new Dictionary<Type, string>();

        private static readonly FieldInfo[] NoFields = new FieldInfo[0];

        private static FieldInfo[] FieldsOf(Type t)
        {
            FieldInfo[] cached;
            if (fieldCache.TryGetValue(t, out cached)) return cached;

            var keep = new List<FieldInfo>();
            string error = null;
            // DeclaredOnly plus a manual base walk, so we get fields from every
            // level of the hierarchy without duplicates where a subclass hides a
            // base field with `new`. DeclaredOnly alone does NOT do this: it
            // returns each level's own declaration separately, so a `new`-hidden
            // field is seen once from the derived type and once from the base.
            // `claimed` is what actually removes the duplicate — a name already
            // taken by a more-derived level (walk order is derived -> base) is
            // skipped at every base level below it, so only the derived value
            // survives and no JSON object ends up with the same key written
            // twice (which would let the base value win on a last-key-wins
            // parser instead of the derived one that's actually in effect).
            var claimed = new HashSet<string>();
            for (Type cur = t; cur != null && cur != typeof(object); cur = cur.BaseType)
            {
                FieldInfo[] fields;
                try
                {
                    fields = cur.GetFields(BindingFlags.Public | BindingFlags.NonPublic
                                           | BindingFlags.Instance | BindingFlags.DeclaredOnly);
                }
                catch (Exception ex)
                {
                    error = Note(error, cur.Name + ".GetFields: " + ex.GetType().Name);
                    continue;
                }
                for (int i = 0; i < fields.Length; i++)
                {
                    FieldInfo f = fields[i];
                    if (f.IsStatic) continue;
                    // Compiler-generated backing fields and closures add noise
                    // without adding information.
                    if (f.Name.IndexOf('<') >= 0) continue;
                    if (SkippedFieldNames.Contains(f.Name)) continue;
                    // f.FieldType is a type RESOLUTION, not a lookup - see
                    // fieldErrors above for why it throws and what it costs.
                    bool skipped;
                    try { skipped = IsSkippedType(f.FieldType); }
                    catch (Exception ex)
                    {
                        error = Note(error, f.Name + ": " + ex.GetType().Name);
                        continue;
                    }
                    if (skipped) continue;
                    if (!claimed.Add(f.Name)) continue;
                    keep.Add(f);
                }
            }
            FieldInfo[] arr = keep.ToArray();
            fieldCache[t] = arr;
            if (error != null) fieldErrors[t] = error;
            return arr;
        }

        private static string Note(string soFar, string msg)
        {
            return soFar == null ? msg : soFar + "; " + msg;
        }

        /// <summary>
        /// Plain Unity VALUE structs — no asset backing, cannot throw touching
        /// them before load completes — that are safe and useful to capture
        /// despite living in the UnityEngine namespace.
        ///
        /// DUMP_DRAWSIZE_CAPTURE_1 (2026-08-30): the blanket "skip all of
        /// UnityEngine" rule below was written for Texture2D/Material/Mesh and
        /// friends, but it also ate every Vector2/Color/etc field on EVERY def
        /// in the dump — GraphicData.drawSize (Vector2), GraphicData.color and
        /// .colorTwo (Color), any Quaternion/Rect/Bounds anywhere in the graph.
        /// Verified against a live capture: GravEngine and
        /// GravshipShieldGenerator both set graphicData.drawSize=(3,3) in raw
        /// XML, and neither's captured graphicData JSON carried drawSize at
        /// all. Named by type NAME (not namespace) so it stays a narrow,
        /// explicit allowlist rather than reopening the whole namespace.
        /// </summary>
        private static readonly HashSet<string> SafeUnityValueTypeNames = new HashSet<string>
        {
            "Vector2", "Vector3", "Vector4",
            "Color", "Color32",
            "Quaternion", "Rect", "Bounds",
        };

        private static bool IsSkippedType(Type t)
        {
            if (t == null) return true;
            if (typeof(Delegate).IsAssignableFrom(t)) return true;

            string ns = t.Namespace ?? "";
            if (ns.StartsWith("UnityEngine", StringComparison.Ordinal))
            {
                // A handful of plain structs are safe (see
                // SafeUnityValueTypeNames above); everything else in
                // UnityEngine — Texture, Material, Mesh, GameObject,
                // Component, ... — stays skipped exactly as before.
                if (SafeUnityValueTypeNames.Contains(t.Name)) return false;
                return true;
            }
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
                // Same two guards as the sequence branch below, for the same
                // reasons: a mod dictionary can throw while enumerating (or
                // hand back an enumerator whose entries are not
                // DictionaryEntry), and an unbounded one would be written in
                // full. An unguarded throw here does not just lose this value -
                // it escapes with the array still open, and DefDumper answers
                // that by deleting the whole def type's file.
                try
                {
                    int n = 0;
                    foreach (DictionaryEntry e in asDict)
                    {
                        if (n++ >= MaxSequenceItems) { w.Str("<truncated>"); break; }
                        w.StartObject();
                        w.Name("key"); WriteValue(w, e.Key, depth + 1, maxDepth, path);
                        w.Name("value"); WriteValue(w, e.Value, depth + 1, maxDepth, path);
                        w.EndObject();
                    }
                }
                catch (Exception ex) { w.Str("<enumerate-failed:" + ex.GetType().Name + ">"); }
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
            // finally, not a trailing call: an exception escaping this body
            // would otherwise leave obj on the path forever, and every later
            // RemoveAt pops the wrong entry - the cycle guard then reports
            // <cycle:...> for objects that are not in one, silently dropping
            // real content from the rest of the dump.
            try
            {
                w.StartObject();

                // Record the concrete type, because it is often the entire content
                // of an entry: knowing a comps element is CompProperties_Milkable is
                // exactly what the animal inventory wants to know.
                w.Prop("$type", t.Name);

                FieldInfo[] fields;
                string fieldsError;
                try { fields = FieldsOf(t); fieldsError = FieldsErrorOf(t); }
                catch (Exception ex) { fields = NoFields; fieldsError = "FieldsOf: " + ex.GetType().Name; }
                // A short field list is never left silent.
                if (fieldsError != null) w.Prop("$fieldsError", fieldsError);

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
            }
            finally
            {
                if (tracked) path.RemoveAt(path.Count - 1);
            }
        }

        private static string FieldsErrorOf(Type t)
        {
            string err;
            if (fieldErrors.TryGetValue(t, out err)) return err;
            return null;
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
