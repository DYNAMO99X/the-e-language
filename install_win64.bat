@echo off
REM Install the E interpreter (e.exe) on this machine.
REM
REM Full Package install:
REM   - Copies e.exe to the chosen directory
REM   - Adds that directory to the user's PATH (HKCU, no admin needed)
REM   - Registers the .e file extension so double-clicking a .e file
REM     runs it with the installed e.exe
REM
REM No administrator rights are required.

setlocal EnableExtensions EnableDelayedExpansion

echo.
echo ============================================
echo   E Language Installer
echo ============================================
echo.

REM ----- 1. Find the e.exe we just built -----
set "EXE=%~dp0dist\e.exe"
if not exist "%EXE%" (
    echo ERROR: Could not find "%EXE%".
    echo Please run build.bat first.
    pause
    exit /b 1
)

REM ----- 2. Ask the user where to install -----
set "DEFAULT_DIR=%~dp0"
set "DEFAULT_DIR=%DEFAULT_DIR:~0,-1%"

set /p "INSTALL_DIR=Install E to which directory? [press Enter for: %DEFAULT_DIR%]: "
if "%INSTALL_DIR%"=="" set "INSTALL_DIR=%DEFAULT_DIR%"

REM Strip any trailing backslash
if "%INSTALL_DIR:~-1%"=="\" set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

echo.
echo Installing to: "%INSTALL_DIR%"
echo.

REM ----- 3. Create the directory if it does not exist -----
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%" >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Could not create "%INSTALL_DIR%".
        pause
        exit /b 1
    )
)

REM ----- 4. Copy e.exe -----
copy /Y "%EXE%" "%INSTALL_DIR%\e.exe" >nul
if errorlevel 1 (
    echo ERROR: Failed to copy e.exe.
    pause
    exit /b 1
)
echo [OK] Copied e.exe to "%INSTALL_DIR%"

REM ----- 5. Add the directory to the user's PATH (HKCU) -----
set "REG_PATH=HKCU\Environment"
for /f "tokens=2*" %%A in ('reg query "%REG_PATH%" /v Path 2^>nul') do set "USER_PATH=%%B"

REM Check if the directory is already on the PATH
echo !USER_PATH! | findstr /I /C:"%INSTALL_DIR%" >nul
if errorlevel 1 (
    if defined USER_PATH (
        set "NEW_PATH=!USER_PATH!;%INSTALL_DIR%"
    ) else (
        set "NEW_PATH=%INSTALL_DIR%"
    )
    reg add "%REG_PATH%" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
    if errorlevel 1 (
        echo WARNING: Could not update PATH in registry.
    ) else (
        echo [OK] Added "%INSTALL_DIR%" to user PATH
        echo      (restart any open terminals for PATH changes to take effect)
    )
) else (
    echo [OK] "%INSTALL_DIR%" is already on the user PATH
)

REM ----- 6. Register the .e file extension -----
set "EXT_KEY=HKCU\Software\Classes\.e"
set "PROG_KEY=HKCU\Software\Classes\EE.Lang\shell\open\command"

reg add "%EXT_KEY%" /ve /d "EE.Lang" /f >nul
if errorlevel 1 (
    echo WARNING: Could not register the .e extension.
) else (
    echo [OK] Registered .e file extension
)

reg add "HKCU\Software\Classes\EE.Lang" /ve /d "E Language Source File" /f >nul
reg add "%PROG_KEY%" /ve /d "\"%INSTALL_DIR%\e.exe\" \"%%1\"" /f >nul
if errorlevel 1 (
    echo WARNING: Could not register the file association command.
) else (
    echo [OK] Double-clicking a .e file will run it with e.exe
)

REM ----- 7. Notify Explorer to pick up changes -----
ie4uinit.exe -show 2>nul
powershell -NoProfile -Command "[Win32.Shell32]::SHChangeNotify(0x08000000, 0, 0, 0)" >nul 2>&1

echo.
echo ============================================
echo   Installation complete!
echo ============================================
echo.
echo Try it out:
echo   %INSTALL_DIR%\e.exe examples\hello.e
echo.
echo Or, after restarting your terminal:
echo   e examples\hello.e
echo.
echo Double-click any .e file in Explorer to run it.
echo.
echo To uninstall, run uninstall_e.bat
echo.
pause
endlocal
