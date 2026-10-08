using System.Collections.Generic;
using Verse;

namespace RimMandrake.LoreStages
{
    // One reveal ladder, as data.
    //
    // "Rules as data": no lore text lives in C#. A campaign ships one of these
    // per ladder from its OWN mod (content tier), naming its own defs; this
    // assembly is the engine and knows no ladder by name.
    //
    // Ladders advance INDEPENDENTLY. GameComponent_LoreStage scribes a
    // Dictionary<ladderId, int>, so the Scarlands ladder sitting at rung 3 says
    // nothing about the Contagion's.
    public class RM_LoreStageTableDef : Def
    {
        // The key this ladder's stage is stored under in the save. Stable
        // forever once a save exists: renaming it silently resets that ladder
        // to stage 0 on the next load. Defaults to defName when left blank.
        public string ladderId;

        // Highest meaningful rung, for ConfigErrors and for AdvanceStage's
        // clamp. 0 means "no clamp" (unbounded).
        public int maxStage;

        public List<LoreStageTarget> targets = new List<LoreStageTarget>();

        public string LadderId => RM_LoreStageKernel.LadderKey(ladderId, defName);

        public override IEnumerable<string> ConfigErrors()
        {
            foreach (string err in base.ConfigErrors())
            {
                yield return err;
            }

            if (targets == null || targets.Count == 0)
            {
                yield return "RM_LoreStageTableDef with no targets — it will load, apply nothing, and look like it works.";
                yield break;
            }

            for (int i = 0; i < targets.Count; i++)
            {
                LoreStageTarget t = targets[i];
                if (t == null)
                {
                    // <li IsNull="True"/> is legal RimWorld XML and produces a
                    // null list entry — without this guard every field access
                    // below throws an NRE out of ConfigErrors.
                    yield return $"target {i}: null entry";
                    continue;
                }

                if (t.defType.NullOrEmpty())
                {
                    yield return $"target {i}: no defType";
                }

                if (t.defName.NullOrEmpty())
                {
                    yield return $"target {i}: no defName";
                }

                if (t.field.NullOrEmpty())
                {
                    yield return $"target {i} ({t.defName}): no field";
                }

                if (t.stages == null || t.stages.Count == 0)
                {
                    yield return $"target {i} ({t.defName}.{t.field}): no stages — nothing would ever change";
                    continue;
                }

                // null entries (<li IsNull="True"/>) are reported once and carry no stage or text, so they stay out of the rung rules
                var rungStages = new List<int>(t.stages.Count);
                var rungHasText = new List<bool>(t.stages.Count);
                var rungs = new List<LoreStageText>(t.stages.Count);
                foreach (LoreStageText s in t.stages)
                {
                    if (s == null)
                    {
                        yield return $"target {i} ({t.defName}.{t.field}): null stage entry";
                        continue;
                    }

                    rungs.Add(s);
                    rungStages.Add(s.stage);
                    rungHasText.Add(s.text != null);
                }

                foreach (KeyValuePair<int, RungProblem> problem in RM_LoreStageKernel.RungProblems(rungStages, rungHasText, maxStage))
                {
                    LoreStageText s = rungs[problem.Key];
                    switch (problem.Value)
                    {
                        case RungProblem.Duplicate:
                            yield return $"target {i} ({t.defName}.{t.field}): duplicate stage {s.stage} — which one wins is load order, i.e. undefined";
                            break;
                        case RungProblem.Negative:
                            yield return $"target {i} ({t.defName}.{t.field}): negative stage {s.stage}";
                            break;
                        case RungProblem.AboveMax:
                            yield return $"target {i} ({t.defName}.{t.field}): stage {s.stage} is above maxStage {maxStage} and can never be reached";
                            break;
                        default:
                            yield return $"target {i} ({t.defName}.{t.field}): stage {s.stage} has no text";
                            break;
                    }
                }
            }
        }
    }
}
