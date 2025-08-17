@echo off
setlocal
pushd %~dp0

REM Build EXE with PyInstaller if needed
if not exist ..\MiniFileBot\dist\MiniFileBot.exe (
  echo Building EXE via PyInstaller...
  where py >NUL 2>NUL && set PY_CMD=py
  if "%PY_CMD%"=="" where python >NUL 2>NUL && set PY_CMD=python
  if "%PY_CMD%"=="" (
    echo [!] Python not found. Install Python 3.11 (64-bit) and re-run.
    pause
    exit /b 1
  )
  %PY_CMD% -m venv ..\.venv
  call ..\.venv\Scripts\activate
  python -m pip install --upgrade pip
  pip install -r ..\MiniFileBot\requirements.txt pyinstaller
  cd ..\MiniFileBot
  pyinstaller --noconfirm --clean --windowed --onefile app_gui.py --name MiniFileBot --collect-all PySide6 --collect-submodules guessit
  cd ..\installer
)

REM Install WiX if missing
where candle.exe >NUL 2>NUL || where light.exe >NUL 2>NUL
if errorlevel 1 (
  echo Installing WiX Toolset via Chocolatey...
  where choco >NUL 2>NUL || (echo [!] Chocolatey not found. Install WiX manually from https://wixtoolset.org/ and ensure candle.exe/light.exe are in PATH.& pause & exit /b 1)
  choco install wixtoolset --yes
)

set BUILDOUT=%CD%\..\MiniFileBot\dist
set WXS=MiniFileBot.wxs

REM Compile WXS -> .wixobj
candle.exe -dBuildOutput="%BUILDOUT%" "%WXS%"
if errorlevel 1 ( echo [!] candle failed.& pause & exit /b 1 )

REM Link .wixobj -> .msi
for %%f in (*.wixobj) do set WIXOBJ=%%f
light.exe "%WIXOBJ%" -ext WixUIExtension -o ..\dist\MiniFileBot-Installer.msi
if errorlevel 1 ( echo [!] light failed.& pause & exit /b 1 )

echo MSI created at: %CD%\..\dist\MiniFileBot-Installer.msi
pause
popd
