Get-PnpDevice -PresentOnly | ? { $_.InstanceId -match 'VID_1B1C' } | Select FriendlyName,InstanceId | ft -auto | Out-String -Width 220
Get-CimInstance -Namespace root/wmi -ClassName MSAcpi_ThermalZoneTemperature -EA SilentlyContinue | % { "{0} {1:N1}C" -f $_.InstanceName, ($_.CurrentTemperature/10-273.15) }
