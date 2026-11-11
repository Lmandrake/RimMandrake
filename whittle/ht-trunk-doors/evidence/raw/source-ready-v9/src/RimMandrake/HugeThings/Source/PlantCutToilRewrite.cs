using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;

namespace RimMandrake.HugeThings
{
    /// <summary>Pure IL transformation shared by production and the mutation harness. Returns original instructions
    /// unchanged unless exactly the two measured contact calls and their operands match.</summary>
    public static class PlantCutToilRewrite
    {
        private static bool Constant(CodeInstruction code, int value)
        {
            if (code.opcode == OpCodes.Ldc_I4 || code.opcode == OpCodes.Ldc_I4_S) return Convert.ToInt32(code.operand) == value;
            OpCode[] small = { OpCodes.Ldc_I4_0, OpCodes.Ldc_I4_1, OpCodes.Ldc_I4_2, OpCodes.Ldc_I4_3, OpCodes.Ldc_I4_4,
                OpCodes.Ldc_I4_5, OpCodes.Ldc_I4_6, OpCodes.Ldc_I4_7, OpCodes.Ldc_I4_8 };
            return value >= 0 && value < small.Length && code.opcode == small[value];
        }

        public static List<CodeInstruction> Rewrite(List<CodeInstruction> code, FieldInfo driver, MethodInfo go, MethodInfo touch,
            MethodInfo goWrapper, MethodInfo touchWrapper, int target, int mode, out bool accepted)
        {
            accepted = false;
            if (driver == null || go == null || touch == null || goWrapper == null || touchWrapper == null) return code;
            var gotos = new List<int>(); var contacts = new List<int>();
            for (int i = 0; i < code.Count; i++)
            {
                if (Equals(code[i].operand, go)) gotos.Add(i);
                if (Equals(code[i].operand, touch)) contacts.Add(i);
            }
            if (gotos.Count != 1 || contacts.Count != 1) return code;
            int g = gotos[0], c = contacts[0];
            if (code[g].blocks.Count != 0 || code[c].blocks.Count != 0) return code;
            if (g < 3 || c < 2 || !Constant(code[g-3], target) || !Constant(code[g-2], mode) || !Constant(code[g-1], 0) ||
                !Constant(code[c-2], target) || !Constant(code[c-1], mode)) return code;
            var replacements = new Dictionary<int, MethodInfo> { [g] = goWrapper, [c] = touchWrapper };
            var result = new List<CodeInstruction>();
            for (int i = 0; i < code.Count; i++)
            {
                if (!replacements.TryGetValue(i, out MethodInfo wrapper)) { result.Add(code[i]); continue; }
                var load = new CodeInstruction(OpCodes.Ldarg_0);
                load.labels.AddRange(code[i].labels);
                load.blocks.AddRange(code[i].blocks);
                result.Add(load);
                result.Add(new CodeInstruction(OpCodes.Ldfld, driver));
                result.Add(new CodeInstruction(OpCodes.Call, wrapper));
            }
            accepted = true;
            return result;
        }
    }
}
