using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Reflection.Emit;
using HarmonyLib;
using RimMandrake.HugeThings;
class Program
{
    public object driver = null;
    static void Go(int target,int mode,bool parent) { }
    static void Touch(object toil,int target,int mode) { }
    static void GoWrap(int target,int mode,bool parent,object driver) { }
    static void TouchWrap(object toil,int target,int mode,object driver) { }
    static int checks;
    static void Check(bool value,string why) { checks++;if(!value) throw new Exception(why); }
    static MethodInfo Method(string name)=>typeof(Program).GetMethod(name,BindingFlags.Static|BindingFlags.NonPublic);
    static List<CodeInstruction> Original()=>new List<CodeInstruction> {
        new CodeInstruction(OpCodes.Ldc_I4_1),new CodeInstruction(OpCodes.Ldc_I4_2),new CodeInstruction(OpCodes.Ldc_I4_0),
        new CodeInstruction(OpCodes.Call,Method(nameof(Go))),new CodeInstruction(OpCodes.Ldnull),
        new CodeInstruction(OpCodes.Ldc_I4_1),new CodeInstruction(OpCodes.Ldc_I4_2),new CodeInstruction(OpCodes.Call,Method(nameof(Touch)))};
    static List<CodeInstruction> Rewrite(List<CodeInstruction> code,out bool accepted, bool field=true)
        =>PlantCutToilRewrite.Rewrite(code,field?typeof(Program).GetField(nameof(driver)):null,
            Method(nameof(Go)),Method(nameof(Touch)),Method(nameof(GoWrap)),Method(nameof(TouchWrap)),1,2,out accepted);
    static int Main()
    {
        try
        {
            var original=Original();var output=Rewrite(original,out bool accepted);
            Check(accepted && output.Count==original.Count+4,"valid contact shape not rewritten exactly twice");
            Check(output.Count(c=>Equals(c.operand,Method(nameof(GoWrap))))==1 && output.Count(c=>Equals(c.operand,Method(nameof(TouchWrap))))==1,"wrapper cardinality");
            Check(output.Count(c=>c.opcode==OpCodes.Ldfld)==2,"driver context not injected into both wrappers");
            Check(original.Count==8 && Equals(original[3].operand,Method(nameof(Go))),"rewriter mutated original input");
            foreach(var mutate in new Action<List<CodeInstruction>>[] {
                c=>c.RemoveAt(3), c=>c.Add(new CodeInstruction(OpCodes.Call,Method(nameof(Go)))),
                c=>c.Add(new CodeInstruction(OpCodes.Call,Method(nameof(Touch)))),
                c=>c[0]=new CodeInstruction(OpCodes.Ldc_I4_2),c=>c[1]=new CodeInstruction(OpCodes.Ldc_I4_3),
                c=>c[2]=new CodeInstruction(OpCodes.Ldc_I4_1),c=>c[5]=new CodeInstruction(OpCodes.Ldc_I4_2),
                c=>c[6]=new CodeInstruction(OpCodes.Ldc_I4_3),c=>c[3]=new CodeInstruction(OpCodes.Call,Method(nameof(GoWrap))) })
            {
                var bad=Original();mutate(bad);var snapshot=bad.ToArray();var result=Rewrite(bad,out accepted);
                Check(!accepted && ReferenceEquals(result,bad) && result.SequenceEqual(snapshot),"IL mismatch partially patched vanilla");
            }
            var noField=Original();Check(ReferenceEquals(Rewrite(noField,out accepted,false),noField) && !accepted,"missing driver field accepted");
            var labels=Original();var dm=new DynamicMethod("label",typeof(void),Type.EmptyTypes);var label=dm.GetILGenerator().DefineLabel();
            labels[3].labels.Add(label);output=Rewrite(labels,out accepted);
            Check(accepted && output[3].opcode==OpCodes.Ldarg_0 && output[3].labels.Contains(label),"branch skipped injected driver context");
            Check(labels[3].labels.Contains(label),"input branch labels mutated");
            var region=Original();region[3].blocks.Add(new ExceptionBlock(ExceptionBlockType.EndExceptionBlock));
            Check(ReferenceEquals(Rewrite(region,out accepted),region) && !accepted,"exception boundary moved across driver injection");
            Console.WriteLine("PASS trunk contact IL: "+checks+" checks including nine mismatch mutants");return 0;
        }
        catch(Exception e) { Console.WriteLine("FAIL trunk contact IL: "+e);return 1; }
    }
}
