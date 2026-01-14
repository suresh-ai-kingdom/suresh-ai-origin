# Windows Task Scheduler Setup for Automation Services
# Run these commands in PowerShell as Administrator

# 1. Nightly backup (runs at 2 AM daily)
$action1 = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\sures\Suresh ai origin\scripts\nightly_backup.py" -WorkingDirectory "C:\Users\sures\Suresh ai origin"
$trigger1 = New-ScheduledTaskTrigger -Daily -At 2am
$settings1 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "SURESH_AI_NightlyBackup" -Action $action1 -Trigger $trigger1 -Settings $settings1 -Description "Automated nightly backup with integrity check"

# 2. Daily automations (runs at 3 AM daily - workflows: churn, payment retry, campaigns, etc.)
$action2 = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\sures\Suresh ai origin\scripts\run_daily_automations.py" -WorkingDirectory "C:\Users\sures\Suresh ai origin"
$trigger2 = New-ScheduledTaskTrigger -Daily -At 3am
$settings2 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "SURESH_AI_DailyAutomations" -Action $action2 -Trigger $trigger2 -Settings $settings2 -Description "Run all daily automation workflows"

# 3. Continuous monitor (starts at system startup and runs in background)
$action3 = New-ScheduledTaskAction -Execute "python" -Argument "C:\Users\sures\Suresh ai origin\scripts\monitor_service.py" -WorkingDirectory "C:\Users\sures\Suresh ai origin"
$trigger3 = New-ScheduledTaskTrigger -AtStartup
$settings3 = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 0)
Register-ScheduledTask -TaskName "SURESH_AI_MonitorService" -Action $action3 -Trigger $trigger3 -Settings $settings3 -Description "Continuous production health monitoring"

# Verify tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "SURESH_AI_*"} | Format-Table TaskName, State, LastRunTime, NextRunTime

Write-Host "`n✅ Scheduled tasks created successfully!" -ForegroundColor Green
Write-Host "`nTo start monitor service immediately:" -ForegroundColor Yellow
Write-Host "Start-ScheduledTask -TaskName 'SURESH_AI_MonitorService'" -ForegroundColor Cyan
Write-Host "`nTo view logs:" -ForegroundColor Yellow
Write-Host "Get-ScheduledTask -TaskName 'SURESH_AI_*' | Get-ScheduledTaskInfo" -ForegroundColor Cyan
