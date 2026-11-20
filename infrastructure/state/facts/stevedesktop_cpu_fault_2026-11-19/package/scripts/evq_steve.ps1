$s=[datetime]'2026-10-20'
$q=@(
 @{LogName='System';ProviderName='Microsoft-Windows-WHEA-Logger';StartTime=$s},
 @{LogName='System';Id=41;ProviderName='Microsoft-Windows-Kernel-Power';StartTime=$s},
 @{LogName='System';Id=1001;StartTime=$s},
 @{LogName='System';Id=6008;StartTime=$s},
 @{LogName='System';Id=6005,6006,6009,12,13;StartTime=$s},
 @{LogName='Application';Id=1000,1001,1002,1026;StartTime=$s}
)
$all=foreach($h in $q){ try{ Get-WinEvent -FilterHashtable $h -EA Stop }catch{} }
$all | Sort-Object TimeCreated | ForEach-Object { [pscustomobject]@{utc=$_.TimeCreated.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ');log=$_.LogName;provider=$_.ProviderName;id=$_.Id;level=$_.LevelDisplayName;msg=(($_.Message -replace '\s+',' '))} } | ConvertTo-Csv -NoTypeInformation
