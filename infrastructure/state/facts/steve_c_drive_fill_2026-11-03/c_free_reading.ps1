$d = Get-PSDrive C
"{0} free_bytes={1} size_bytes={2}" -f (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"), $d.Free, ($d.Free + $d.Used)
