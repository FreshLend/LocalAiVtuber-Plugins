@echo off
chcp 65001
cd /D "%~dp0"
set PATH=%PATH%;%SystemRoot%\system32

if not exist "downloads" mkdir "downloads"
if not exist "downloads\plugins" mkdir "downloads\plugins"
if not exist "downloads\fixes" mkdir "downloads\fixes"

:: GitHub Settings
set GITHUB_REPO=FreshLend/LocalAiVtuber-Plugins
set GITHUB_BRANCH=main
set PLUGINS_URL=https://api.github.com/repos/%GITHUB_REPO%/contents/LocalAiVtuber/plugins?ref=%GITHUB_BRANCH%
set FIXES_URL=https://api.github.com/repos/%GITHUB_REPO%/contents/LocalAiVtuber/fixes?ref=%GITHUB_BRANCH%

:: Main Menu
:menu
cls
color b
echo.
echo ##################################
echo # Local Ai Vtuber - Control Menu #
echo ##################################
echo.
echo ==================================
echo = 1 - Full installation          =
echo = 2 - Install plugins / fixes    =
echo = 3 - Run without installation   =
echo = ------------------------------ =
echo = 0 - Exit                       =
echo ==================================
echo.
set /p choice="Select action [1-0]: "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto download_menu
if "%choice%"=="3" goto start
if "%choice%"=="0" exit /b
goto menu

:: Download Menu
:download_menu
cls
echo.
echo ##################################
echo #   Install Plugins and Fixes    #
echo ##################################
echo.
echo ==================================
echo = 1 - Install plugins            =
echo = 2 - Install fixes              =
echo = ------------------------------ =
echo = 3 - Back to main menu          =
echo ==================================
echo.
set /p choice="Select action [1-3]: "

if "%choice%"=="1" goto list_plugins
if "%choice%"=="2" goto list_fixes
if "%choice%"=="3" goto menu
goto download_menu

:: Plugins List
:list_plugins
echo Getting plugins list...
powershell -command "$ErrorActionPreference = 'Stop'; try { $response = Invoke-RestMethod -Uri '%PLUGINS_URL%' -Headers @{'Accept'='application/vnd.github.v3+json'}; for($i=1; $i -le $response.Count; $i++) { Write-Host (('{0} - {1}' -f $i, $response[$i-1].name)) }; } catch { Write-Host 'Error getting plugins list: ' $_.Exception.Message; exit 1 }"
if errorlevel 1 (
    pause
    goto download_menu
)

echo.
set /p plugin_num="Select plugin number to install (or 0 to cancel): "
if "%plugin_num%"=="0" goto download_menu

echo Installing plugin #%plugin_num%...
powershell -command "$ErrorActionPreference = 'Stop'; try { $response = Invoke-RestMethod -Uri '%PLUGINS_URL%' -Headers @{'Accept'='application/vnd.github.v3+json'}; $selected = $response[%plugin_num%-1]; $download_url = $selected.download_url; $plugin_name = $selected.name -replace '\.zip$',''; $temp_zip = Join-Path $env:TEMP ('plugin_' + (Get-Date -Format 'yyyyMMddHHmmss') + '.zip'); $temp_dir = Join-Path $env:TEMP ('plugin_' + (Get-Date -Format 'yyyyMMddHHmmss')); Write-Host 'Downloading plugin ' $plugin_name '...'; Invoke-WebRequest -Uri $download_url -OutFile $temp_zip; $dest_path = Join-Path '%cd%' 'downloads\plugins'; if(!(Test-Path $dest_path)) { New-Item -ItemType Directory -Path $dest_path | Out-Null }; Write-Host 'Extracting plugin...'; New-Item -ItemType Directory -Path $temp_dir -Force | Out-Null; Expand-Archive -Path $temp_zip -DestinationPath $temp_dir -Force; $extractedFiles = Get-ChildItem -Path $temp_dir; if ($extractedFiles.Count -eq 1 -and $extractedFiles[0].PSIsContainer) { $sourcePath = $extractedFiles[0].FullName; } else { $sourcePath = $temp_dir; }; $finalPath = Join-Path $dest_path $plugin_name; if (Test-Path $finalPath) { Remove-Item $finalPath -Recurse -Force }; Move-Item -Path $sourcePath -Destination $finalPath -Force; Remove-Item $temp_zip -Force; Remove-Item $temp_dir -Recurse -Force; Write-Host 'Plugin successfully installed to ' $finalPath; } catch { Write-Host 'Error installing plugin: ' $_.Exception.Message; if (Test-Path $temp_zip) { Remove-Item $temp_zip -Force }; if (Test-Path $temp_dir) { Remove-Item $temp_dir -Recurse -Force }; exit 1 }"
if errorlevel 1 (
    echo Error installing plugin
)
pause
goto download_menu

:: Fixes List
:list_fixes
echo Getting fixes list...
powershell -command "$ErrorActionPreference = 'Stop'; try { $response = Invoke-RestMethod -Uri '%FIXES_URL%' -Headers @{'Accept'='application/vnd.github.v3+json'}; for($i=1; $i -le $response.Count; $i++) { Write-Host (('{0} - {1}' -f $i, $response[$i-1].name)) }; } catch { Write-Host 'Error getting fixes list: ' $_.Exception.Message; exit 1 }"
if errorlevel 1 (
    pause
    goto download_menu
)

echo.
set /p fix_num="Select fix number to install (or 0 to cancel): "
if "%fix_num%"=="0" goto download_menu

echo Installing fix #%fix_num%...
powershell -command "$ErrorActionPreference = 'Stop'; try { $response = Invoke-RestMethod -Uri '%FIXES_URL%' -Headers @{'Accept'='application/vnd.github.v3+json'}; $selected = $response[%fix_num%-1]; $download_url = $selected.download_url; $fix_name = $selected.name; $temp_file = Join-Path $env:TEMP ([System.IO.Path]::GetRandomFileName()); Write-Host 'Downloading fix ' $fix_name '...'; Invoke-WebRequest -Uri $download_url -OutFile $temp_file; $dest_path = Join-Path '%cd%' 'downloads\fixes'; if(!(Test-Path $dest_path)) { New-Item -ItemType Directory -Path $dest_path | Out-Null }; $final_path = Join-Path $dest_path $fix_name; Move-Item -Path $temp_file -Destination $final_path -Force; Write-Host 'Fix successfully installed to ' $final_path; } catch { Write-Host 'Error installing fix: ' $_.Exception.Message; if (Test-Path $temp_file) { Remove-Item $temp_file -Force }; exit 1 }"
if errorlevel 1 (
    echo Error installing fix
)
pause
goto download_menu

:: Full Installation
:install
echo "%CD%"| findstr /C:" " >nul && (
    echo This script uses Miniconda which cannot be installed in a path with spaces.
    pause
    goto menu
)

@rem Check for special characters in path
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{|}~]" >nul && (
    echo.
    echo WARNING: Special characters detected in installation path!
    echo          This may cause installation errors!
    echo.
    pause
)

@rem Path configuration
set INSTALL_DIR=%cd%\installer_files
set CONDA_ROOT_PREFIX=%cd%\installer_files\conda
set INSTALL_ENV_DIR=%cd%\installer_files\env
set MINICONDA_DOWNLOAD_URL=http://127.0.0.1:43034/download/miniconda_installer.exe
set conda_exists=F

@rem Check for Conda
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" set conda_exists=T

@rem Install Miniconda
if "%conda_exists%" == "F" (
    echo Downloading Miniconda from %MINICONDA_DOWNLOAD_URL%
    mkdir "%INSTALL_DIR%" 2>nul
    curl -Lk "%MINICONDA_DOWNLOAD_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || (
        echo Miniconda download failed
        pause
        goto menu
    )
    
    echo Installing Miniconda to %CONDA_ROOT_PREFIX%
    start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%
    
    call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || (
        echo Miniconda installation failed
        pause
        goto menu
    )
)

@rem Create virtual environment
if not exist "%INSTALL_ENV_DIR%" (
    echo Creating virtual environment...
    call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.10 || (
        echo Environment creation failed
        pause
        goto menu
    )
)

if not exist "%INSTALL_ENV_DIR%\python.exe" (
    echo Error: Environment not created
    pause
    goto menu
)

@rem Environment setup
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem Activate environment
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || (
    echo Environment activation failed
    pause
    goto menu
)

@rem Install C++ Build Tools
set VSBUILDTOOLS_DIR=%cd%\BuildTools
if not exist "%VSBUILDTOOLS_DIR%\VC\Auxiliary\Build\vcvars64.bat" (
    echo Installing C++ Build Tools...
    "%cd%\vs_buildtools.exe" --quiet --wait --norestart --nocache ^
        --installPath "%VSBUILDTOOLS_DIR%" ^
        --add Microsoft.VisualStudio.Workload.VCTools ^
        --includeRecommended || (
        echo C++ Build Tools installation failed
        pause
        goto menu
    )
)

@rem Enable long paths
reg query "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "LongPathsEnabled" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    net session >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo Administrator privileges required to enable long paths...
        powershell -Command "Start-Process '%~f0' -Verb RunAs"
        exit /b
    )
    reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "LongPathsEnabled" /t REG_DWORD /d 1 /f
)

@rem Install dependencies
echo Installing dependencies...
CALL python -m pip install pip==24.0
CALL python -m pip install -r requirements.txt
CALL python -m pip install llama-cpp-python
CALL python -m pip install torch==2.5 torchaudio

@rem Create required directories
set "conda_path_bin=%INSTALL_ENV_DIR%\bin"
if not exist "%conda_path_bin%" mkdir "%conda_path_bin%"

goto start

:: Run without installation
:start
echo Checking for virtual environment...

set CONDA_ROOT_PREFIX=%cd%\installer_files\conda
set INSTALL_ENV_DIR=%cd%\installer_files\env
echo.
echo Verifying paths...
echo CONDA_ROOT_PREFIX: %CONDA_ROOT_PREFIX% 
echo INSTALL_ENV_DIR: %INSTALL_ENV_DIR%
echo.

if not exist "%INSTALL_ENV_DIR%\python.exe" (
    echo Virtual environment not found! Please run installation first.
    pause
    goto menu
)

:: Check if conda is available
if not exist "%CONDA_ROOT_PREFIX%\_conda.exe" (
    echo Conda not found! Please run installation first.
    pause
    goto menu
)

:: Activate environment
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || (
    echo Failed to activate virtual environment
    pause
    goto menu
)

echo Starting main.py...
python main.py

pause
goto menu
