# fleet_toast.ps1 — raise a Windows notification from WSL.
#
# WHY THIS EXISTS
# ===============
# A stalled seat is invisible if the only channel is a terminal pane the owner
# is not looking at. On 2026-08-14 BRIDGE sat stopped at the main menu waiting
# for the owner's word while the owner believed work was in flight; nothing
# left the terminal to say so. The fix in every comparable system is the same:
# push, do not wait to be polled.
#
# ⚠️ Called ONLY from board.py's watch loop, and only after a seat has been
# stopped past the dwell threshold, once per stall. A toast per permission
# prompt trains the owner to dismiss toasts, which is worse than having none.
#
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File <this> -Title T -Msg M
#
# The AppId must be a registered app or the toast is silently dropped; Windows
# Terminal's is used because it is guaranteed present on this machine.
param([string]$Title = "FLEET", [string]$Msg = "")
$ErrorActionPreference = "Stop"
try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] > $null
    $t = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $n = $t.GetElementsByTagName("text")
    $n.Item(0).AppendChild($t.CreateTextNode($Title)) > $null
    $n.Item(1).AppendChild($t.CreateTextNode($Msg)) > $null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($t)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Microsoft.WindowsTerminal_8wekyb3d8bbwe!App").Show($toast)
}
catch {
    # Never let a failed notification take down the board that called it.
    exit 0
}
