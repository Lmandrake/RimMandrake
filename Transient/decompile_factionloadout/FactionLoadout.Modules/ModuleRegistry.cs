using System.Collections.Generic;
using System.Linq;

namespace FactionLoadout.Modules;

public static class ModuleRegistry
{
	public static readonly List<ITotalControlModule> modules = new List<ITotalControlModule>();

	public static bool initialized;

	public static IReadOnlyList<ITotalControlModule> Modules => modules;

	public static void Register(ITotalControlModule module)
	{
		if (module == null)
		{
			ModCore.Warn("Attempted to register a null module.");
		}
		else if (string.IsNullOrEmpty(module.ModuleKey))
		{
			ModCore.Warn("Module '" + module.ModuleName + "' has a null or empty ModuleKey. Skipping registration.");
		}
		else if (modules.Any((ITotalControlModule m) => m.ModuleKey == module.ModuleKey))
		{
			ModCore.Warn("Duplicate module key '" + module.ModuleKey + "' from '" + module.ModuleName + "'. A module with this key is already registered. Skipping.");
		}
		else
		{
			modules.Add(module);
			ModCore.Log($"Registered module: '{module.ModuleName}' (key: {module.ModuleKey}, active: {module.IsActive})");
			if (initialized)
			{
				ModCore.Warn("Module '" + module.ModuleName + "' registered after InitializeAll() was called. Data from already-loaded presets will not include this module's data.");
				module.Initialize();
			}
		}
	}

	public static void InitializeAll()
	{
		initialized = true;
		ModCore.Log($"Initializing {modules.Count} registered module(s)...");
		foreach (ITotalControlModule module in modules)
		{
			ModCore.Debug("Initializing module: '" + module.ModuleName + "' (key: " + module.ModuleKey + ")");
			module.Initialize();
		}
	}

	public static ITotalControlModule GetModule(string moduleKey)
	{
		return modules.FirstOrDefault((ITotalControlModule m) => m.ModuleKey == moduleKey);
	}
}
