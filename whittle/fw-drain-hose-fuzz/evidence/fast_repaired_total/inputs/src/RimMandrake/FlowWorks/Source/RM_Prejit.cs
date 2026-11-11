using System;
using System.Collections.Generic;
using System.Reflection;

namespace RimMandrake.FlowWorks
{
	/// <summary>
	/// LEVELLING_TICK_DIAGNOSE_DRY_GC_SPIKE: compile a hot path's methods before the first tick that runs them. Mono compiles a
	/// method on its first call, so the first levelling cycle after a cold launch paid for compiling the whole walk / link /
	/// move call graph inside one tick (28.8 ms live, against 2.4 ms for the same cycle on a reload in a warm process).
	/// <see cref="RuntimeMethodHandle.GetFunctionPointer"/> makes the runtime compile the method and return its code address
	/// without running it. It CAN run type initialisers (Mono initialises a class while compiling or inlining code that needs
	/// it), so call this only where running those initialisers is already safe: on the main thread, after the defs load
	/// (a [StaticConstructorOnStartup] constructor), for types whose initialisers would run on the first tick anyway.
	/// Roots must be non-generic types (a closed generic root's nested closures come back open and are skipped).
	/// Verse-free: selftested by LevelPrejitChecks.
	/// </summary>
	public static class RM_Prejit
	{
		public struct Result
		{
			/// <summary>Methods compiled, methods that threw while compiling, methods skipped (abstract, open generic, no IL body).</summary>
			public int Compiled, Failed, Skipped, Types;
			public double Ms;
			/// <summary>The first failure's text (type.method: exception), "" when none.</summary>
			public string FirstFailure;
		}

		private const BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static
			| BindingFlags.DeclaredOnly;

		/// <summary>Compile every concrete method and constructor declared by <paramref name="roots"/> and their nested types (the
		/// compiler's closure and iterator classes included), then each of <paramref name="extra"/> (closed generic instantiations
		/// a type walk cannot see). Never throws.</summary>
		public static Result Run(IEnumerable<Type> roots, IEnumerable<MethodBase> extra = null)
		{
			var r = new Result { FirstFailure = "" };
			long t0 = System.Diagnostics.Stopwatch.GetTimestamp();
			var seen = new HashSet<Type>();
			var stack = new Stack<Type>();
			var more = new List<MethodBase>();
			try
			{
				foreach (Type t in roots ?? Array.Empty<Type>())
				{
					if (t != null)
					{
						stack.Push(t);
					}
				}
				foreach (MethodBase m in extra ?? Array.Empty<MethodBase>())
				{
					if (m != null)
					{
						more.Add(m);
					}
				}
			}
			catch (Exception e)
			{
				Fail(ref r, "inputs: " + e.GetType().Name);
			}
			while (stack.Count > 0)
			{
				Type t = stack.Pop();
				if (!seen.Add(t))
				{
					continue;
				}
				r.Types++;
				Type[] nested;
				MethodBase[] members;
				try
				{
					nested = t.GetNestedTypes(All);
					var list = new List<MethodBase>(t.GetMethods(All));
					list.AddRange(t.GetConstructors(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.DeclaredOnly));
					members = list.ToArray();
				}
				catch (Exception e)
				{
					Fail(ref r, t.FullName + ": " + e.GetType().Name);
					continue;
				}
				foreach (Type n in nested)
				{
					stack.Push(n);
				}
				if (t.ContainsGenericParameters)
				{
					r.Skipped += members.Length;
					continue;
				}
				foreach (MethodBase m in members)
				{
					Compile(m, ref r);
				}
			}
			foreach (MethodBase m in more)
			{
				Compile(m, ref r);
			}
			r.Ms = (System.Diagnostics.Stopwatch.GetTimestamp() - t0) * 1000.0 / System.Diagnostics.Stopwatch.Frequency;
			return r;
		}

		/// <summary>True when a method has IL the runtime would compile: not abstract, not an open generic, not extern/runtime,
		/// and it has an IL body. May throw on unreadable metadata (Compile catches it).</summary>
		public static bool Compilable(MethodBase m)
		{
			if (m == null || m.IsAbstract || m.ContainsGenericParameters)
			{
				return false;
			}
			MethodImplAttributes impl = m.GetMethodImplementationFlags();
			if ((impl & (MethodImplAttributes.InternalCall | MethodImplAttributes.Runtime | MethodImplAttributes.Native)) != 0)
			{
				return false;
			}
			return (m.Attributes & MethodAttributes.PinvokeImpl) == 0 && m.GetMethodBody() != null;
		}

		private static void Compile(MethodBase m, ref Result r)
		{
			try
			{
				if (!Compilable(m))
				{
					r.Skipped++;
					return;
				}
				System.Runtime.CompilerServices.RuntimeHelpers.PrepareMethod(m.MethodHandle);
				m.MethodHandle.GetFunctionPointer();
				r.Compiled++;
			}
			catch (Exception e)
			{
				Fail(ref r, (m.DeclaringType?.FullName ?? "?") + "." + m.Name + ": " + e.GetType().Name);
			}
		}

		private static void Fail(ref Result r, string what)
		{
			r.Failed++;
			if (r.FirstFailure.Length == 0)
			{
				r.FirstFailure = what;
			}
		}
	}
}
