@echo off
chcp 65001
cd /D "%~dp0"
set PATH=%PATH%;%SystemRoot%\system32

:: Создание структуры папок
if not exist "downloads" mkdir "downloads"
if not exist "downloads\plugins" mkdir "downloads\plugins"
if not exist "downloads\fixes" mkdir "downloads\fixes"

:: GitHub Settings
set GITHUB_REPO=FreshLend/LocalAiVtuber-Plugins
set GITHUB_BRANCH=main
set PLUGINS_URL=https://api.github.com/repos/%GITHUB_REPO%/contents/LocalAiVtuber2/plugins?ref=%GITHUB_BRANCH%
set FIXES_URL=https://api.github.com/repos/%GITHUB_REPO%/contents/LocalAiVtuber2/fixes?ref=%GITHUB_BRANCH%

:: Main Menu
:menu
cls
color b
echo.
echo ####################################
echo # Local Ai Vtuber 2 - Control Menu #
echo ####################################
echo.
echo ====================================
echo = 1 - Full installation            =
echo = 2 - Install plugins / fixes      =
echo = 3 - Run without installation     =
echo = -------------------------------- =
echo = 0 - Exit                         =
echo ====================================
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
echo #############################
echo # Install Plugins and Fixes #
echo #############################
echo.
echo =============================
echo = 1 - Install plugins       =
echo = 2 - Install fixes         =
echo = ------------------------- =
echo = 3 - Back to main menu     =
echo =============================
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
cls
echo Starting automatic installation...
echo This may take several minutes depending on your internet connection...
echo.

echo Checking for Python 3.10...
python --version 2>nul | findstr /R /C:"Python 3\.10\." >nul
IF %ERRORLEVEL% NEQ 0 (
    color c
    echo.
    echo ##################################################################
    echo #         ERROR: Python 3.10 is required but not found!          #
    echo ##################################################################
    echo =                                                                =
    echo = Please install Python 3.10 first and run installation again    =
    echo = Download from:                                                 =
    echo = https://www.python.org/downloads/release/python-3100/          =
    echo =                                                                =
    echo = Make sure to check "Add Python to PATH" during installation!   =
    echo ==================================================================
    echo.
    pause
    goto menu
)

echo Checking for CUDA 12.4...
where nvcc >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    nvcc --version | findstr /C:"release 12.4" >nul
    if %ERRORLEVEL% NEQ 0 (
        SET cuda_warning=1
    )
) else (
    SET cuda_warning=1
)

if defined cuda_warning (
    if %cuda_warning% EQU 1 (
        color 6
        echo.
        echo ##################################################################
        echo #  [WARNING] CUDA 12.4 not detected - The project may not start  #
        echo ##################################################################
        echo =                                                                =
        echo = Please install CUDA 12.4 for optimal performance               =
        echo = before running this application.                               =
        echo = -------------------------------------------------------------- =
        echo = You can download CUDA 12.4 from:                               =
        echo = https://developer.nvidia.com/cuda-12-4-0-download-archive      =
        echo =                                                                =
        echo = The application will continue to run,                          =
        echo = but may use CPU instead of GPU, or it may not start at all.    =
        echo ==================================================================
        echo.
        timeout /t 3 >nul
        cls
        color 7
    )
)

echo Starting installation process...
cd backend

:: Проверка и создание venv
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo Error creating virtual environment
        pause
        cd ..
        goto menu
    )
) else (
    echo Virtual environment already exists, skipping creation...
)

echo Activating virtual environment...
call venv\Scripts\activate
if %ERRORLEVEL% NEQ 0 (
    echo Error activating virtual environment
    pause
    cd ..
    goto menu
)

echo Updating pip...
pip install --upgrade pip
if %ERRORLEVEL% NEQ 0 (
    echo Error updating pip
    pause
    cd ..
    goto menu
)

echo Installing llama-cpp-python...
pip install llama-cpp-python==0.2.90 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124
if %ERRORLEVEL% NEQ 0 (
    echo Error installing llama-cpp-python
    pause
    cd ..
    goto menu
)

echo Installing PyTorch with CUDA 12.4...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
if %ERRORLEVEL% NEQ 0 (
    echo Error installing PyTorch
    pause
    cd ..
    goto menu
)

echo Installing main dependencies...
pip install fastapi uvicorn qdrant-client[fastembed] pyautogui sounddevice silero-vad easyocr==1.7.2 mss numpy==1.23.4 pytchat
if %ERRORLEVEL% NEQ 0 (
    echo Error installing main dependencies
    pause
    cd ..
    goto menu
)

echo Installing TTS requirements...
pip install -r services\TTS\GPTsovits\requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error installing TTS requirements
    pause
    cd ..
    goto menu
)

color a
echo.
echo ##################################################################
echo #          Installation completed successfully!                  #
echo ##################################################################
echo =                                                                =
echo = You can now run the application from the main menu             =
echo =                                                                =
echo ==================================================================
echo.
timeout /t 3 >nul
cls
call venv\Scripts\activate
python server.py
pause
goto menu

:: Run without installation
:start
cls
echo Starting server.py...
cd backend

SET has_error=0
SET cuda_warning=0

echo Checking for Python 3.10...
python --version 2>nul | findstr /R /C:"Python 3\.10\." >nul
IF %ERRORLEVEL% NEQ 0 (
    color c
    echo.
    echo ##################################################################
    echo #         ERROR: Python 3.10 is required but not found!          #
    echo ##################################################################
    echo =                                                                =
    echo = Please install Python 3.10 and make sure it's added to PATH    =
    echo = before running this application.                               =
    echo = -------------------------------------------------------------- =
    echo = You can download Python 3.10 from:                             =
    echo = https://www.python.org/downloads/release/python-3100/          =
    echo =                                                                =
    echo = Make sure to check "Add Python to PATH" during installation!   =
    echo ==================================================================
    echo.
    SET has_error=1
    goto error_display
)

echo Checking for CUDA 12.4...
where nvcc >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    nvcc --version | findstr /C:"release 12.4" >nul
    if %ERRORLEVEL% NEQ 0 (
        SET cuda_warning=1
    )
) else (
    SET cuda_warning=1
)

if defined cuda_warning (
    if %cuda_warning% EQU 1 (
        color 6
        echo.
        echo ##################################################################
        echo #  [WARNING] CUDA 12.4 not detected - The project may not start  #
        echo ##################################################################
        echo =                                                                =
        echo = Please install CUDA 12.4 for optimal performance               =
        echo = before running this application.                               =
        echo = -------------------------------------------------------------- =
        echo = You can download CUDA 12.4 from:                               =
        echo = https://developer.nvidia.com/cuda-12-4-0-download-archive      =
        echo =                                                                =
        echo = The application will continue to run,                          =
        echo = but may use CPU instead of GPU, or it may not start at all.    =
        echo ==================================================================
        echo.
        timeout /t 10 >nul
        cls
        color 7
    )
)

:: Проверка и активация venv
if exist "venv\" (
    echo Activating virtual environment...
    call venv\Scripts\activate
    if %ERRORLEVEL% NEQ 0 (
        echo Warning: Failed to activate virtual environment
        SET has_error=1
    )
) else (
    echo Warning: Virtual environment not found
    SET has_error=1
)

python server.py
IF %ERRORLEVEL% NEQ 0 (
    SET has_error=1
)

:error_display
IF %has_error% EQU 1 (
    color c
    echo.
    echo ##################################################################
    echo #                        PLEASE READ THIS                        #
    echo ##################################################################
    echo =                                                                =
    echo = Requirements:                                                  =
    echo = - Python 3.10 must be installed and available in PATH          =
    echo = - Virtual environment should be properly set up                =
    echo = - CUDA 12.4 recommended for GPU acceleration                   =
    echo =                                                                =
    echo = Please follow the installation instructions in the readme      =
    echo = to set up the environment properly before running this script. =
    echo =                                                                =
    echo = This script is only for starting the program after             =
    echo = the environment has been properly set up.                      =
    echo =                                                                =
    echo = If you can't get it to work after following the instructions,  =
    echo = please see if others have already had the same issue,          =
    echo = and file an issue if not:                                      =
    echo = https://github.com/0Xiaohei0/LocalAIVtuber2/issues             =
    echo =                                                                =
    echo ==================================================================
    echo.
    cd ../
)

pause
goto menu
