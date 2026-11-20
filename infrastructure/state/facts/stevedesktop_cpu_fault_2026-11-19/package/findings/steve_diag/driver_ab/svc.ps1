Get-CimInstance Win32_Service | ? { $_.Name -match 'Corsair|iCUE|Asus|Armoury|AsSys|LightingService|ROG|GLCK|ENE|CPUID|Hasleo|MSI|HWiNFO|AI Suite|Aura' -or $_.PathName -match 'Corsair|ASUS|Hasleo|CPUID|MSI' } | Select Name,State,StartMode,PathName | ft -auto | Out-String -Width 250
Get-CimInstance Win32_SystemDriver | ? { $_.Name -match 'cpuz|Corsair|AsIO|Asusgio|GLCKIO|EneTech|MSIO|Hasleo|hasl|WinRing|RTCore|inpout' } | Select Name,State,StartMode,PathName | ft -auto | Out-String -Width 250
Get-Process | ? { $_.Name -match 'Corsair|iCUE|Armoury|Asus|Lighting|ROG|Hasleo|cpuz|HWiNFO' } | Select Name,Id,Path | ft -auto | Out-String -Width 250
Get-CimInstance Win32_Product -Filter "Vendor like '%Hasleo%'" -ErrorAction SilentlyContinue | Select Name,Version
