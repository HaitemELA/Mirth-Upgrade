# Define variables
$nugetUrl = "https://aka.ms/nugetclidl"
$nugetExecutable = "nuget.exe"
$pythonInstallDir = "$PSScriptRoot\python"   # Python installation directory
$requirementsFile = ".\requirements.txt"     # Path to requirements file
$pythonScript = ".\Debug.py"           # Path to your Python script

# Record the start time
$startTime = Get-Date

# Helper function to print step titles
function Print-Step {
    param (
        [string]$stepName
    )
    Write-Output "`n--------------------------------------------------------------------"
    Write-Output "                             $stepName"
    Write-Output "--------------------------------------------------------------------`n"
}

# Step 1: Download nuget.exe if it does not exist
Print-Step "Downloading nuget.exe (if needed)"
if (!(Test-Path $nugetExecutable)) {
    Write-Output "Downloading nuget.exe..."
    Invoke-WebRequest -Uri $nugetUrl -OutFile $nugetExecutable
} else {
    Write-Output "nuget.exe already exists. Skipping download."
}

# Step 2: Use nuget to install Python silently
Print-Step "Installing Python using nuget"
& .\$nugetExecutable install python -ExcludeVersion -OutputDirectory $pythonInstallDir

# Define path to the Python executable
$pythonPath = Join-Path -Path $pythonInstallDir -ChildPath "python\tools\python.exe"

# Step 3: Install the latest versions of Python libraries from requirements.txt
Print-Step "Installing Python libraries"
if (Test-Path $requirementsFile) {
    & $pythonPath -m pip install --upgrade -r $requirementsFile
} else {
    Write-Output "requirements.txt not found. Skipping library installation."
}

# Step 4: Run your Python script
Print-Step "Running Mirth Upgrade script"
& $pythonPath $pythonScript

# Step 5: Clean up and remove the Python installation
Print-Step "Removing Python installation"
Remove-Item -Recurse -Force $pythonInstallDir

# Cleanup downloaded nuget.exe
Write-Output "`nCleaning up nuget.exe..."
Remove-Item -Force $nugetExecutable

# Record the end time
$endTime = Get-Date

# Calculate and display the total execution time
$executionTime = $endTime - $startTime
Write-Output "`n--------------------------------------------------------------------"
Write-Output "Python installation, execution, and cleanup completed."
Write-Output "Total Execution Time: $($executionTime.Hours) hours, $($executionTime.Minutes) minutes, $($executionTime.Seconds) seconds."
Write-Output "--------------------------------------------------------------------`n"
