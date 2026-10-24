// ATMOSPHERIC_BASE_BUILD_PROGRAM_1 T3 part (c) -- the Nine aboard the Utinni, read off the campaign tier's XML
// (src/RimUtinni/UtinniPatches/Defs/AtmosphericBase/RUT_NineSignatures.xml) into the REAL RM_AtmosphericSchemeDef and
// RM_SignatureDef classes, field by field, as the game's loader does -- but strictly: an element no field carries, an enum
// name the enum lacks, a bool that is not true/false, a number that does not parse, or a defName nothing defines is a
// FormatException, so a typo in the file reddens this test instead of loading as a default (the game would only log it).
// Per god: the readings load and resolve, validate clean in the kernel (reserved white, L8 black, approach fits...), sit
// on one palette, keep Gentle's floor and play Full as authored, show only aboard a Utinni gravship, and hold the design's
// territory. Then the canon pairings, the settings' silence about gods, and negative controls proving the parse can see.
// NOT covered: the game's own loader (MayRequire, cross-references) -- the live proof's business.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Reflection;
using System.Xml;
using RimMandrake.AtmosphericBase;
using Verse;

internal static class NineTests
{
    private static void Check(string name, bool ok, string detail = "") => Program.Check(name, ok, detail);

    internal const string Package = "mandrake.rm.atmosphericbase";
    private const string SchemeType = "RimMandrake.AtmosphericBase.RM_AtmosphericSchemeDef";
    private const string SignatureType = "RimMandrake.AtmosphericBase.RM_SignatureDef";

    /// <summary>The Nine, by the defName stem the file uses, with the design's territory (§2.10) and darkness.</summary>
    private struct God { public string key; public RM_ShapeKind shape; public RM_Anchor anchor; public bool dark; }
    private static readonly God[] Nine =
    {
        new God { key = "Ishko", shape = RM_ShapeKind.Tide, anchor = RM_Anchor.Core, dark = true },
        new God { key = "Ohm", shape = RM_ShapeKind.Circuit, anchor = RM_Anchor.Power },
        new God { key = "Oomo", shape = RM_ShapeKind.Tide, anchor = RM_Anchor.Medoid },
        new God { key = "MobUnloo", shape = RM_ShapeKind.Wedge, anchor = RM_Anchor.Core },
        new God { key = "Rekko", shape = RM_ShapeKind.Tide, anchor = RM_Anchor.Shrine },
        new God { key = "TaBaa", shape = RM_ShapeKind.Tide, anchor = RM_Anchor.Threshold },
        new God { key = "Zizzik", shape = RM_ShapeKind.Tide, anchor = RM_Anchor.Medoid, dark = true },
        new God { key = "Shkaar", shape = RM_ShapeKind.Tide, anchor = RM_Anchor.Open },
        new God { key = "Ozzik", shape = RM_ShapeKind.Tide, anchor = RM_Anchor.Grandest },
    };

    // ------------------------------------------------------------------ the strict loader

    internal sealed class Loaded
    {
        public readonly Dictionary<string, RM_AtmosphericSchemeDef> schemes = new Dictionary<string, RM_AtmosphericSchemeDef>();
        public readonly Dictionary<string, RM_SignatureDef> sigs = new Dictionary<string, RM_SignatureDef>();
        public readonly List<string> mayRequire = new List<string>();   // one per top-level def, "" when absent
    }

    private struct Pending { public object owner; public FieldInfo field; public string name; }

    internal static Loaded Load(string xmlText)
    {
        var doc = new XmlDocument();
        doc.LoadXml(xmlText);
        var outp = new Loaded();
        var pend = new List<Pending>();
        foreach (XmlNode n in doc.DocumentElement.ChildNodes)
        {
            if (n.NodeType != XmlNodeType.Element) continue;
            Type t = n.Name == SchemeType ? typeof(RM_AtmosphericSchemeDef) : n.Name == SignatureType ? typeof(RM_SignatureDef) : null;
            if (t == null) throw new FormatException("unknown def type <" + n.Name + ">");
            var def = (Def)Activator.CreateInstance(t);
            Fill(def, n, pend);
            if (string.IsNullOrEmpty(def.defName)) throw new FormatException("a <" + t.Name + "> has no defName");
            if (outp.schemes.ContainsKey(def.defName) || outp.sigs.ContainsKey(def.defName)) throw new FormatException("defName repeated: " + def.defName);
            if (def is RM_AtmosphericSchemeDef sd) outp.schemes[def.defName] = sd; else outp.sigs[def.defName] = (RM_SignatureDef)def;
            outp.mayRequire.Add(n.Attributes?["MayRequire"]?.Value ?? "");
        }
        foreach (Pending p in pend)
        {
            object target = null;
            if (p.field.FieldType == typeof(RM_AtmosphericSchemeDef) && outp.schemes.TryGetValue(p.name, out RM_AtmosphericSchemeDef s)) target = s;
            else if (p.field.FieldType == typeof(RM_SignatureDef) && outp.sigs.TryGetValue(p.name, out RM_SignatureDef g)) target = g;
            if (target == null) throw new FormatException("<" + p.field.Name + "> names " + p.name + ", which no " + p.field.FieldType.Name + " in the file defines");
            p.field.SetValue(p.owner, target);
        }
        return outp;
    }

    private static void Fill(object o, XmlNode node, List<Pending> pend)
    {
        foreach (XmlNode f in node.ChildNodes)
        {
            if (f.NodeType != XmlNodeType.Element) continue;
            FieldInfo fi = o.GetType().GetField(f.Name, BindingFlags.Public | BindingFlags.Instance);
            if (fi == null) throw new FormatException(o.GetType().Name + " has no field <" + f.Name + ">");
            if (typeof(Def).IsAssignableFrom(fi.FieldType)) { pend.Add(new Pending { owner = o, field = fi, name = f.InnerText.Trim() }); continue; }
            fi.SetValue(o, Value(fi.FieldType, f, pend));
        }
    }

    private static object Value(Type t, XmlNode f, List<Pending> pend)
    {
        string s = f.InnerText.Trim();
        if (t.IsEnum)
        {
            if (!Enum.IsDefined(t, s)) throw new FormatException(t.Name + " has no member '" + s + "' (<" + f.Name + ">)");
            return Enum.Parse(t, s);
        }
        if (t == typeof(float)) return float.Parse(s, NumberStyles.Float, CultureInfo.InvariantCulture);
        if (t == typeof(int)) return int.Parse(s, NumberStyles.Integer, CultureInfo.InvariantCulture);
        if (t == typeof(bool))
        {
            if (s == "true") return true;
            if (s == "false") return false;
            throw new FormatException("<" + f.Name + "> is not a bool: '" + s + "'");
        }
        if (t == typeof(string)) return s;
        if (t == typeof(ColorInt))
        {
            // the "(r,g,b,a)" integer form; ParseHelper is not callable off Mono (see Program.ShippedSchemes)
            string[] p = s.TrimStart('(').TrimEnd(')').Split(',');
            if (p.Length != 4 || !s.StartsWith("(") || !s.EndsWith(")")) throw new FormatException("not an (r,g,b,a) colour: " + s);
            int[] c = new int[4];
            for (int i = 0; i < 4; i++)
            {
                c[i] = int.Parse(p[i].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture);
                if (c[i] < 0 || c[i] > 255) throw new FormatException("colour channel out of 0-255: " + s);
            }
            return new ColorInt(c[0], c[1], c[2], c[3]);
        }
        if (t.IsGenericType && t.GetGenericTypeDefinition() == typeof(List<>))
        {
            Type it = t.GetGenericArguments()[0];
            if (typeof(Def).IsAssignableFrom(it)) throw new NotSupportedException("a list of def references");
            var list = (System.Collections.IList)Activator.CreateInstance(t);
            foreach (XmlNode li in f.ChildNodes)
            {
                if (li.NodeType != XmlNodeType.Element) continue;
                if (li.Name != "li") throw new FormatException("<" + f.Name + "> holds <" + li.Name + ">, not <li>");
                list.Add(Value(it, li, pend));
            }
            return list;
        }
        if (t.IsClass || (t.IsValueType && !t.IsPrimitive))
        {
            object inst = Activator.CreateInstance(t);
            Fill(inst, f, pend);
            return inst;
        }
        throw new NotSupportedException("field type " + t.Name);
    }

    // ------------------------------------------------------------------ colour judgements

    private static int Max(RM_SchemeData s, int i) => Math.Max(s.r[i], Math.Max(s.g[i], s.b[i]));
    private static double Dist(int r, int g, int b, int r2, int g2, int b2) => Math.Sqrt((r - r2) * (r - r2) + (g - g2) * (g - g2) + (b - b2) * (b - b2));

    /// <summary>§9.13 Sh'kaar "visibly gold, distinct from the Narrator's white": every entry at least 130 from
    /// (255,255,255) -- well past the reserved 100 -- and blue at most half of red.</summary>
    internal static bool Gold(int r, int g, int b) => Dist(r, g, b, 255, 255, 255) >= 130 && b * 2 <= r && r >= g;

    /// <summary>§9.13 Rekko "leans bronze": red over green over blue, blue at most 0.4 of red, and at least 50 from the
    /// vanilla lamp amber (214,148,94) the design said his top entry sat beside.</summary>
    internal static bool Bronze(int r, int g, int b) => r > g && g > b && b * 10 <= r * 4 && Dist(r, g, b, 214, 148, 94) >= 50;

    // ------------------------------------------------------------------ the run

    internal static void Run()
    {
        string path = Program.FindUp(System.IO.Path.Combine("src", "RimUtinni", "UtinniPatches", "Defs", "AtmosphericBase", "RUT_NineSignatures.xml"));
        Check("Nine: the campaign tier's signature file is found from the selftest exe", path != null);
        if (path == null) return;
        string text = System.IO.File.ReadAllText(path);
        Loaded L;
        try { L = Load(text); }
        catch (Exception e) { Check("Nine: the signature file parses strictly", false, e.GetType().Name + ": " + e.Message); return; }
        Check("Nine: the signature file parses strictly (every field known, every enum and reference resolved)", true);
        Check("Nine: nine signatures and 27 readings, nothing else", L.sigs.Count == 9 && L.schemes.Count == 27, L.sigs.Count + " signatures, " + L.schemes.Count + " schemes");
        Check("Nine: every def loads only with AtmosphericBase (MayRequire " + Package + ")",
              L.mayRequire.TrueForAll(m => m == Package), string.Join(",", L.mayRequire));

        // every scheme is the reading of exactly one signature
        var owner = new Dictionary<RM_AtmosphericSchemeDef, int>();
        foreach (RM_SignatureDef sig in L.sigs.Values) foreach (RM_AtmosphericSchemeDef r in sig.readings.All()) owner[r] = (owner.TryGetValue(r, out int k) ? k : 0) + 1;
        var orphan = new List<string>();
        foreach (var p in L.schemes) if (!owner.TryGetValue(p.Value, out int k) || k != 1) orphan.Add(p.Key);
        Check("Nine: every reading belongs to exactly one god", orphan.Count == 0, string.Join(", ", orphan));

        foreach (God god in Nine) RunGod(god, L, owner);

        // ---- §9.13 the two moved palettes, and controls proving the judgements can fail
        Check("Nine control: the design's proposed Blaze (255,236,150) is NOT gold (the judgement can fail)", !Gold(255, 236, 150));
        Check("Nine control: the design's proposed Burnish (200,146,74) is NOT bronze enough (26 from the vanilla lamp)", !Bronze(200, 146, 74));

        // ---- §9.15 canon pairings, by the loaded defs (as RM_SignatureDef.Rules builds them)
        var rules = new List<RM_PairingRule>();
        foreach (RM_SignatureDef d in L.sigs.Values)
            foreach (RM_SignaturePairing p in d.pairings)
                rules.Add(new RM_PairingRule { a = d.defName, b = p.with.defName, anchorA = p.myAnchor, anchorB = p.theirAnchor, aHunts = p.hunts, label = p.label });
        Check("pairing: exactly the two canon pairings are authored", rules.Count == 2, rules.Count + " rules");
        string I = "RUT_Signature_Ishko", T = "RUT_Signature_TaBaa", S = "RUT_Signature_Shkaar";
        Func<string, RM_TerritoryShape> shapeOf = n => L.sigs[n].territory.Shape;
        RM_TerritoryPlan it = RM_TerritoryShapes.Plan(I, shapeOf(I), T, rules), ti = RM_TerritoryShapes.Plan(T, shapeOf(T), I, rules);
        Check("pairing: Ishko and Ta'Baa meet at the threshold (Ishko from the core, Ta'Baa from the threshold), either louder",
              it.kind == RM_PlanKind.PairedTide && it.leadAnchor == RM_Anchor.Core && it.otherAnchor == RM_Anchor.Threshold && it.hunter == -1
              && ti.kind == RM_PlanKind.PairedTide && ti.leadAnchor == RM_Anchor.Threshold && ti.otherAnchor == RM_Anchor.Core, it + " | " + ti);
        RM_TerritoryPlan si = RM_TerritoryShapes.Plan(S, shapeOf(S), I, rules), is_ = RM_TerritoryShapes.Plan(I, shapeOf(I), S, rules);
        Check("pairing: the authored Sh'kaar rule hunts Ishko whichever of them is louder", si.kind == RM_PlanKind.PairedTide && si.hunter == 0 && is_.hunter == 1
              && si.leadAnchor == RM_Anchor.Open && is_.otherAnchor == RM_Anchor.Open, si + " | " + is_);
        var wrong = new List<string>();
        foreach (string a in L.sigs.Keys)
            foreach (string b in L.sigs.Keys)
            {
                if (a == b) continue;
                bool canon = (a == I && b == T) || (a == T && b == I) || (a == S && b == I) || (a == I && b == S);
                if (canon) continue;
                RM_TerritoryPlan pl = RM_TerritoryShapes.Plan(a, shapeOf(a), b, rules), own = RM_TerritoryShapes.Plan(a, shapeOf(a), null, rules);
                if (pl.kind != own.kind || pl.leadAnchor != own.leadAnchor || pl.rule != null) wrong.Add(a + "/" + b + "=" + pl);
            }
        Check("pairing: every other pair plays the leader's own shape", wrong.Count == 0, string.Join("; ", wrong));

        // ---- §9.12 off the Utinni the settings never name a god
        var named = new List<string>();
        foreach (string n in RM_PatternChoice.NeutralSchemes) if (L.schemes.ContainsKey(n) || n.StartsWith("RUT_")) named.Add(n);
        Check("settings: the neutral set names no god's reading", named.Count == 0, string.Join(", ", named));
        string abDefs = Program.FindUp(System.IO.Path.Combine("src", "RimMandrake", "AtmosphericBase", "Defs", "RM_AtmosphericSchemes.xml"));
        string abText = abDefs != null ? System.IO.File.ReadAllText(abDefs) : null;
        Check("settings: AtmosphericBase's own scheme file ships no god (no signature, no RUT_ reading)",
              abText != null && !abText.Contains("RM_SignatureDef") && !abText.Contains("RUT_"), abDefs ?? "file not found");
        Check("gate: a neutral scheme shows anywhere", RM_GodGate.MayShow(false, false, false) && RM_GodGate.MayShow(false, true, false));

        // ---- negative controls: a typo fails loudly. Each mutation must change the text, or the control is blind.
        Mutant("a field-name typo (<dwel>)", text, "<dwell>14</dwell>", "<dwel>14</dwel>");
        Mutant("an enum typo (Treshold)", text, "<anchor>Threshold</anchor>", "<anchor>Treshold</anchor>");
        Mutant("a primitive typo (Proccession)", text, "<primitive>Procession</primitive>", "<primitive>Proccession</primitive>");
        Mutant("a reading reference typo", text, "<resting>RUT_Scheme_Ohm_Resting</resting>", "<resting>RUT_Scheme_Ohm_Restin</resting>");
        Mutant("a pairing reference typo", text, "<with>RUT_Signature_TaBaa</with>", "<with>RUT_Signature_Tabaa</with>");
        Mutant("a non-bool bool (yes)", text, "<scarKeeps>true</scarKeeps>", "<scarKeeps>yes</scarKeeps>");
        Mutant("a def type typo", text, "<RimMandrake.AtmosphericBase.RM_SignatureDef MayRequire=\"mandrake.rm.atmosphericbase\">\n    <defName>RUT_Signature_Ozzik",
               "<RimMandrake.AtmosphericBase.RM_SignatureDefs MayRequire=\"mandrake.rm.atmosphericbase\">\n    <defName>RUT_Signature_Ozzik", "</RimMandrake.AtmosphericBase.RM_SignatureDef>\n\n</Defs>", "</RimMandrake.AtmosphericBase.RM_SignatureDefs>\n\n</Defs>");
        // a value that parses but breaks a rule: the kernel, not the parser, must refuse it
        string white = text.Replace("<li>(255,218,104,0)</li>  <!-- Blaze (moved) -->", "<li>(250,250,240,0)</li>");
        bool whiteRefused = false;
        if (white != text)
        {
            try { whiteRefused = RM_SchemeKernel.Errors(Load(white).schemes["RUT_Scheme_Shkaar_Resting"].Data).Exists(e => e.Contains("L11")); }
            catch (Exception) { whiteRefused = false; }
        }
        Check("Nine control: a near-white entry slipped into Sh'kaar is refused by the reserved-white guard (L11)", whiteRefused);
    }

    private static void Mutant(string what, string text, params string[] pairs)
    {
        string m = text;
        for (int i = 0; i + 1 < pairs.Length; i += 2)
        {
            string n = m.Replace(pairs[i], pairs[i + 1]);
            if (n == m) { Check("Nine control: " + what + " fails the parse", false, "BLIND: '" + pairs[i] + "' is not in the file"); return; }
            m = n;
        }
        string err = null;
        try { Load(m); }
        catch (Exception e) { err = e.GetType().Name + ": " + e.Message; }
        Check("Nine control: " + what + " fails the parse loudly", err != null, "the mutant loaded clean");
    }

    private static void RunGod(God god, Loaded L, Dictionary<RM_AtmosphericSchemeDef, int> owner)
    {
        string g = "Nine/" + god.key + ": ";
        L.sigs.TryGetValue("RUT_Signature_" + god.key, out RM_SignatureDef sig);
        var rd = new RM_AtmosphericSchemeDef[3];
        string[] kinds = { "Resting", "Pleased", "Angry" };
        bool loads = sig != null && sig.readings.resting != null && sig.readings.pleased != null && sig.readings.angry != null;
        if (loads)
        {
            rd[0] = sig.readings.resting; rd[1] = sig.readings.pleased; rd[2] = sig.readings.angry;
            for (int i = 0; i < 3; i++) loads &= rd[i].defName == "RUT_Scheme_" + god.key + "_" + kinds[i];
        }
        Check(g + "the signature loads with its resting, pleased and angry readings, each named for it", loads,
              sig == null ? "no RUT_Signature_" + god.key : "a reading is missing or misnamed");
        if (!loads) return;
        Check(g + "the signature has a label and a tell", !string.IsNullOrEmpty(sig.label) && !string.IsNullOrEmpty(sig.tell));

        // the kernel's own validation (reserved white L11, black needs mayGoDark L8, layer ranges, approach fits...)
        var errs = new List<string>();
        foreach (RM_AtmosphericSchemeDef r in rd) foreach (string e in RM_SchemeKernel.Errors(r.Data)) errs.Add(r.defName + ": " + e);
        Check(g + "all three readings validate clean in the scheme kernel", errs.Count == 0, string.Join("; ", errs));
        var near = new List<string>();
        foreach (RM_AtmosphericSchemeDef r in rd)
            for (int i = 0; i < r.Data.Count; i++)
                if (RM_SchemeKernel.NearNarratorWhite(r.Data.r[i], r.Data.g[i], r.Data.b[i])) near.Add(r.defName + "[" + i + "]");
        Check(g + "no entry sits within the Narrator's reserved white", near.Count == 0, string.Join(", ", near));
        bool onePalette = true;
        for (int k = 1; k < 3; k++)
        {
            RM_SchemeData a = rd[0].Data, b = rd[k].Data;
            if (a.Count != b.Count) { onePalette = false; continue; }
            for (int i = 0; i < a.Count; i++) onePalette &= a.r[i] == b.r[i] && a.g[i] == b.g[i] && a.b[i] == b.b[i];
        }
        Check(g + "the three readings share one palette (identity rides hue)", onePalette);
        bool hasBlack = false, maySet = false;
        foreach (RM_AtmosphericSchemeDef r in rd) { maySet |= r.mayGoDark; for (int i = 0; i < r.Data.Count; i++) hasBlack |= Max(r.Data, i) == 0; }
        Check(g + (god.dark ? "a dark god: true black in the palette, mayGoDark set" : "never dark: no black entry, mayGoDark unset"),
              god.dark ? hasBlack && maySet : !hasBlack && !maySet);

        // §9.14 Full is Full; Gentle keeps a floor. Indices sampled off the real evaluator (no graph: graph primitives Pass).
        bool fullSame = true, gentleFloor = true, inRange = true, fullBlack = false, gentleBlack = false;
        string why = "";
        foreach (RM_AtmosphericSchemeDef r in rd)
        {
            RM_SchemeData d = r.Data;
            gentleFloor &= RM_GodGate.GentleKeepsFloor(d);
            for (int i = 0; i < d.Count; i++) fullSame &= RM_GodGate.Apply(d, i, (int)RM_Intensity.Full) == i;
            try
            {
                for (int e = 0; e < 40; e++)
                    for (int s = 0; s < 60; s++)
                    {
                        int idx = RM_SchemeKernel.PaletteIndex(d, 1000 + e, e % 7, s * 7.3 + e * 0.37, false);
                        if (idx < 0 || idx >= d.Count) { inRange = false; why = r.defName + " gave " + idx; continue; }
                        if (Max(d, idx) == 0) fullBlack = true;
                        int gi = RM_GodGate.Apply(d, idx, (int)RM_Intensity.Gentle);
                        if (Max(d, gi) == 0) gentleBlack = true;
                        if (Max(d, gi) < RM_GodGate.GodFloor) gentleFloor = false;
                    }
            }
            catch (Exception ex) { inRange = false; why = r.defName + " threw " + ex.GetType().Name + ": " + ex.Message; }
        }
        Check(g + "2,400 samples per reading are valid palette indices", inRange, why);
        Check(g + "Full plays every entry as authored", fullSame);
        Check(g + "Gentle never shows an entry under the god floor (max channel " + RM_GodGate.GodFloor + ")", gentleFloor && !gentleBlack);
        if (god.dark) Check(g + "Full reaches true black (a dark god is not floored at Full)", fullBlack);

        // §9.12 the gate: these are signature readings, shown only aboard a Utinni gravship
        bool gated = true;
        foreach (RM_AtmosphericSchemeDef r in rd)
        {
            bool isSig = owner.ContainsKey(r);
            gated &= isSig && RM_GodGate.MayShow(isSig, true, true) && !RM_GodGate.MayShow(isSig, true, false)
                     && !RM_GodGate.MayShow(isSig, false, true) && !RM_GodGate.MayShow(isSig, false, false);
        }
        Check(g + "shows only on a Utinni map with a grav engine; inert anywhere else", gated);

        // the design's territory (§2.10)
        RM_SignatureTerritory t = sig.territory;
        bool terr = t.shape == god.shape && (god.shape == RM_ShapeKind.Wedge || t.anchor == god.anchor);
        Check(g + "territory is the design's " + god.shape + (god.shape == RM_ShapeKind.Wedge ? "" : "(" + god.anchor + ")"), terr, t.shape + "(" + t.anchor + ")");

        // §9.13 the two palettes the owner ruled on
        if (god.key == "Shkaar")
        {
            RM_SchemeData d = rd[0].Data; var bad = new List<string>();
            for (int i = 0; i < d.Count; i++) if (!Gold(d.r[i], d.g[i], d.b[i])) bad.Add("(" + d.r[i] + "," + d.g[i] + "," + d.b[i] + ")");
            Check(g + "visibly gold at every entry, well clear of the Narrator's white", bad.Count == 0, string.Join(" ", bad));
            Check(g + "a fighting rank share of at least 0.4 (design §2.8)", Math.Abs(t.minShare - 0.4f) < 1e-4);
        }
        if (god.key == "Rekko")
        {
            RM_SchemeData d = rd[0].Data; var bad = new List<string>();
            for (int i = 1; i < d.Count; i++) if (!Bronze(d.r[i], d.g[i], d.b[i])) bad.Add("(" + d.r[i] + "," + d.g[i] + "," + d.b[i] + ")");
            Check(g + "leans bronze above his patina floor, clear of the vanilla lamp", bad.Count == 0 && d.r[0] > d.g[0] && d.g[0] > d.b[0], string.Join(" ", bad));
            bool scar = true;
            foreach (RM_AtmosphericSchemeDef r in rd) scar &= r.scarLinger > RM_Scar.MaxLinger && r.scarKeeps;
            Check(g + "M3 SCAR is his: every reading keeps what was, past the 30 s linger", scar);
        }
    }
}
