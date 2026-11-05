// HOSE_REPLAY_WIRE_MONO_TIMING_LANE: embed the game's Mono and run one assembly in it.
//   MonoHost <RimWorld dir> <assembly.exe> [args...]
// Loads <RimWorld>\MonoBleedingEdge\EmbedRuntime\mono-2.0-bdwgc.dll, points it at the game's own class libraries
// (<RimWorld>\RimWorldWin64_Data\Managed, the corlib RimWorld runs on) and config (MonoBleedingEdge\etc), and returns the
// assembly's exit code. Prints one "MONOHOST dll=<path> corlib=<dir>" line to stderr so a report names its runtime.
using System;
using System.IO;
using System.Runtime.InteropServices;

internal static unsafe class MonoHost
{
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void SetDirs(IntPtr lib, IntPtr etc);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void SetPath(IntPtr path);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate void ConfigParse(IntPtr file);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate IntPtr JitInit(IntPtr name, IntPtr version);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate IntPtr AsmOpen(IntPtr domain, IntPtr path);
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)] private delegate int JitExec(IntPtr domain, IntPtr asm, int argc, IntPtr* argv);

    private static T Fn<T>(IntPtr lib, string name) where T : Delegate
        => Marshal.GetDelegateForFunctionPointer<T>(NativeLibrary.GetExport(lib, name));

    private static IntPtr U8(string s) => Marshal.StringToCoTaskMemUTF8(s);

    private static int Main(string[] args)
    {
        if (args.Length < 2) { Console.Error.WriteLine("usage: MonoHost <RimWorld dir> <assembly.exe> [args...]"); return 2; }
        string game = args[0], asmPath = Path.GetFullPath(args[1]);
        string dll = Path.Combine(game, "MonoBleedingEdge", "EmbedRuntime", "mono-2.0-bdwgc.dll");
        string managed = Path.Combine(game, "RimWorldWin64_Data", "Managed");
        string etc = Path.Combine(game, "MonoBleedingEdge", "etc");
        foreach (string p in new[] { dll, managed, etc, asmPath })
            if (!File.Exists(p) && !Directory.Exists(p)) { Console.Error.WriteLine("MonoHost: missing " + p); return 2; }

        IntPtr lib = NativeLibrary.Load(dll);
        Fn<SetDirs>(lib, "mono_set_dirs")(U8(managed), U8(etc));
        Fn<SetPath>(lib, "mono_set_assemblies_path")(U8(managed));
        Fn<ConfigParse>(lib, "mono_config_parse")(IntPtr.Zero);
        IntPtr domain = Fn<JitInit>(lib, "mono_jit_init_version")(U8("hose_replay_mono"), U8("v4.0.30319"));
        if (domain == IntPtr.Zero) { Console.Error.WriteLine("MonoHost: mono_jit_init_version returned null"); return 3; }
        IntPtr asm = Fn<AsmOpen>(lib, "mono_domain_assembly_open")(domain, U8(asmPath));
        if (asm == IntPtr.Zero) { Console.Error.WriteLine("MonoHost: cannot open " + asmPath); return 3; }
        Console.Error.WriteLine("MONOHOST dll=" + dll + " corlib=" + managed);
        Console.Error.Flush();

        int argc = args.Length - 1;   // argv[0] is the assembly itself, as mono.exe passes it
        IntPtr* argv = stackalloc IntPtr[argc];
        argv[0] = U8(asmPath);
        for (int i = 2; i < args.Length; i++) argv[i - 1] = U8(args[i]);
        int rc = Fn<JitExec>(lib, "mono_jit_exec")(domain, asm, argc, argv);
        Console.Out.Flush();
        // no mono_jit_cleanup: a second runtime's shutdown inside this process buys nothing; exit with the replay's code
        Environment.Exit(rc);
        return rc;
    }
}
