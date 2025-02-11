# *************************************************************************************
# | Install the scripts for use by the user without having to specify the full        |
# | path to them.                                                                     |
# |                                                                                   |
# | This script will:                                                                 |
# | 1. Check if the bin directory already exists in the user's home directory         |
# | 2. If it doesn't exist, create it                                                 |
# | 3. Add the bin directory to the user's PATH (permanently)                         |
# | 4. Install the scripts to the bin directory                                       |
# |                                                                                   |
# | Usage:                                                                            |
# | 1. Open a PowerShell terminal                                                     |
# | 2. Run the script `.\install.ps1`                                                 |
# | 3. Use the `create-helm-chart` command to create a chart in the current directory |
# |                                                                                   |
# | --------------------------------------------------------------------------------- |
# | Author: [Bridgeman Accessible](https://bridgemanaccessible.ca)                    |
# | Date: 2025-02-11                                                                  |
# | Version: 1.0.0                                                                    |
# | --------------------------------------------------------------------------------- |
# | MIT License                                                                       |
# |                                                                                   |
# | Copyright (c) 2025 Bridgeman Accessible / Alan Bridgeman                          |
# |                                                                                   |
# | Permission is hereby granted, free of charge, to any person obtaining a copy      |
# | of this software and associated documentation files (the "Software"), to deal     |
# | in the Software without restriction, including without limitation the rights      |
# | to use, copy, modify, merge, publish, distribute, sublicense, and/or sell         |
# | copies of the Software, and to permit persons to whom the Software is             |
# | furnished to do so, subject to the following conditions:                          |
# |                                                                                   |
# | The above copyright notice and this permission notice shall be included in all    |
# | copies or substantial portions of the Software.                                   |
# |                                                                                   |
# | THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR        |
# | IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,          |
# | FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE       |
# | AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER            |
# | LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,     |
# | OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE     |
# | SOFTWARE.                                                                         |
# *************************************************************************************

Write-Host "Installing automated-helm-generator to $($env:USERPROFILE)\bin ..."

# Check if the bin directory already exists in the user's home directory
# If it doesn't exist, create it
# This is so that we can have a predictable location to install scripts to
if (-not (Test-Path $env:USERPROFILE\bin)) {
    Write-Host "Creating %USERPROFILE%\bin"
    mkdir $env:USERPROFILE\bin
}
else {
    Write-Host "$($env:USERPROFILE)\bin already exists"
}

# Because we want the scripts to be usable without having to specify the full path to them we need to add the scripts folder to the user's PATH
# Check if the bin directory is already on the user's PATH
if (-not [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User).Contains("%USERPROFILE%\bin")) {
    Write-Host "Adding $($env:USERPROFILE)\bin (%USERPROFILE%\bin) to the user's PATH"

    # Add the bin directory to the user's PATH permanently
    [Environment]::SetEnvironmentVariable(
        "Path", 
        [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User) + ";%USERPROFILE%\bin",
        [EnvironmentVariableTarget]::User)
    
    Write-Host "You will likely need to restart PowerShell for the changes to take effect"
}
else {
    Write-Host "$($env:USERPROFILE)\bin (%USERPROFILE%\bin) is already on the user's PATH"
}

mkdir $env:USERPROFILE\bin\automated-helm-generator

# Install the script to the bin directory
Copy-Item -Recurse .\src $env:USERPROFILE\bin\automated-helm-generator\src
Copy-Item .\create-helm-chart.py $env:USERPROFILE\bin\automated-helm-generator\create-helm-chart.py
Copy-Item .\create-helm-chart.ps1 $env:USERPROFILE\bin\create-helm-chart.ps1

Write-Host "Installed successfully to $($env:USERPROFILE)\bin"