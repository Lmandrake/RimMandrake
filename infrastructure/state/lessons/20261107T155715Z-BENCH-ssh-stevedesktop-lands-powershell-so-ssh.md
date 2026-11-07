ssh stevedesktop lands in PowerShell, so 'ssh stevedesktop true' exits nonzero when the machine is up; a wait loop on it never fires. Use 'ssh stevedesktop hostname'.
