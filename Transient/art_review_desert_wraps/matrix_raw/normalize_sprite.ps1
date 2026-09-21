param([Parameter(Mandatory=$true)][string]$Path)
Add-Type -AssemblyName System.Drawing
$source=[System.Drawing.Bitmap]::FromFile($Path)
$bitmap=New-Object System.Drawing.Bitmap($source.Width,$source.Height,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g=[System.Drawing.Graphics]::FromImage($bitmap);$g.DrawImageUnscaled($source,0,0);$g.Dispose();$source.Dispose()
$rect=New-Object System.Drawing.Rectangle(0,0,$bitmap.Width,$bitmap.Height)
$data=$bitmap.LockBits($rect,[System.Drawing.Imaging.ImageLockMode]::ReadWrite,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$bytes=New-Object byte[] ([Math]::Abs($data.Stride)*$bitmap.Height)
[Runtime.InteropServices.Marshal]::Copy($data.Scan0,$bytes,0,$bytes.Length)
$w=$bitmap.Width;$h=$bitmap.Height;$mask=New-Object bool[] ($w*$h);$horizontal=New-Object bool[] ($w*$h);$subject=New-Object bool[] ($w*$h);$radius=6
for($y=0;$y-lt$h;$y++){for($x=0;$x-lt$w;$x++){$p=$y*$data.Stride+$x*4;$mask[$y*$w+$x]=(($bytes[$p]+$bytes[$p+1]+$bytes[$p+2])-gt 36)}}
for($y=0;$y-lt$h;$y++){$count=0;for($x=0;$x-lt$w;$x++){$add=$x+$radius;$remove=$x-$radius-1;if($add-lt$w-and$mask[$y*$w+$add]){$count++};if($remove-ge 0-and$mask[$y*$w+$remove]){$count--};$horizontal[$y*$w+$x]=($count-gt 0)}}
for($x=0;$x-lt$w;$x++){$count=0;for($y=0;$y-lt$h;$y++){$add=$y+$radius;$remove=$y-$radius-1;if($add-lt$h-and$horizontal[$add*$w+$x]){$count++};if($remove-ge 0-and$horizontal[$remove*$w+$x]){$count--};$subject[$y*$w+$x]=($count-gt 0)}}
for($y=0;$y-lt$h;$y++){for($x=0;$x-lt$w;$x++){$p=$y*$data.Stride+$x*4;if($subject[$y*$w+$x]){$grey=[byte][Math]::Round(0.2126*$bytes[$p+2]+0.7152*$bytes[$p+1]+0.0722*$bytes[$p]);$bytes[$p]=$grey;$bytes[$p+1]=$grey;$bytes[$p+2]=$grey;$bytes[$p+3]=255}else{$bytes[$p]=255;$bytes[$p+1]=0;$bytes[$p+2]=255;$bytes[$p+3]=255}}}
[Runtime.InteropServices.Marshal]::Copy($bytes,0,$data.Scan0,$bytes.Length);$bitmap.UnlockBits($data)
$temp="$Path.normalized.png";$bitmap.Save($temp,[System.Drawing.Imaging.ImageFormat]::Png);$bitmap.Dispose();Move-Item -LiteralPath $temp -Destination $Path -Force
