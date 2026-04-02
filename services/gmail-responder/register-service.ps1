$rootPath = "c:\Users\admin\Downloads\NEXUS\nexus-main\printivo"
$pythonPath = "C:\Users\admin\AppData\Local\Programs\Python\Python312\python.exe"
$scriptPath = Join-Path $rootPath "services\gmail-responder\service.py"
$taskName = "NEXUS_Gmail_Responder"

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "-u `"$scriptPath`"" -WorkingDirectory $rootPath
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

try {
    # Check if exists and remove old
    Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue | Unregister-ScheduledTask -Confirm:$false
    
    # Register new task
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description "NEXUS: Persistent Gmail Responder"
    
    # Start it immediately
    Start-ScheduledTask -TaskName $taskName
    
    Write-Host "SUCCESS: NEXUS Responder registered and started for current user."
}
catch {
    Write-Host "ERROR: Could not register task. Permission check required."
}
