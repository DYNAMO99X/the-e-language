@echo off
REM Uninstall the E interpreter.
REM Reverses everything install_win64.bat did:
REM   - Removes the .e file association
REM   - Removes the install directory from the user's PATH
REM   - Optionally deletes the installed e.exe
REM
REM No administrator rights are required.

setlocal EnableExtensions EnableDelayedExpansion

echo.
echo ============================================
echo   E Language Uninstaller
echo ============================================
echo.

set "REG_PATH=HKCU\Environment"

REM ----- 1. Ask where E was installed -----
set "DEFAULT_DIR=%~dp0"
set "DEFAULT_DIR=%DEFAULT_DIR:~0,-1%"

set /p "INSTALL_DIR=Where is e.exe installed? [press Enter for: %DEFAULT_DIR%]: "
if "%INSTALL_DIR%"=="" set "INSTALL_DIR=%DEFAULT_DIR%"
if "%INSTALL_DIR:~-1%"=="\" set "INSTALL_DIR=%INSTALL_DIR:~0,-1%"

echo.
echo Uninstalling from: "%INSTALL_DIR%"
echo.

REM ----- 2. Remove the .e file association -----
reg delete "HKCU\Software\Classes\.e" /f >nul 2>&1
if errorlevel 1 (
    echo [skip] .e file extension was not registered
) else (
    echo [OK] Removed .e file extension registration
)

reg delete "HKCU\Software\Classes\EE.Lang" /f >nul 2>&1
if errorlevel 1 (
    rem silently skip
) else (
    echo [OK] Removed EE.Lang file association
)

REM ----- 3. Remove the install directory from the user's PATH -----
for /f "tokens=2*" %%A in ('reg query "%REG_PATH%" /v Path 2^>nul') do set "USER_PATH=%%B"

if defined USER_PATH (
    echo !USER_PATH! | findstr /I /C:"%INSTALL_DIR%" >nul
    if not errorlevel 1 (
        REM Build a new PATH without the install directory
        set "NEW_PATH=!USER_PATH:;%INSTALL_DIR%;=;!"
        set "NEW_PATH=!NEW_PATH:%INSTALL_DIR%;=!"
        set "NEW_PATH=!NEW_PATH:;%INSTALL_DIR%=!"
        set "NEW_PATH=!NEW_PATH:%INSTALL_DIR%=!"
        reg add "%REG_PATH%" /v Path /t REG_EXPAND_SZ /d "!NEW_PATH!" /f >nul
        if errorlevel 1 (
            echo WARNING: Could not update PATH in registry.
        ) else (
            echo [OK] Removed "%INSTALL_DIR%" from user PATH
            echo      (restart any open terminals for PATH changes to take effect)
        )
    ) else (
        echo [skip] "%INSTALL_DIR%" was not on the user PATH
    )
) else (
    echo [skip] User PATH is empty
)

REM ----- 4. Optionally delete e.exe -----
if exist "%INSTALL_DIR%\e.exe" (
    set /p "DELETE_EXE=Delete %INSTALL_DIR%\e.exe ? (y/N): "
    if /i "!DELETE_EXE!"=="y" (
        del /F /Q "%INSTALL_DIR%\e.exe" >nul 2>&1
        if errorlevel 1 (
            echo WARNING: Could not delete e.exe
        ) else (
            echo [OK] Deleted e.exe
        )
    ) else (
        echo [skip] Kept e.exe
    )
) else (
    echo [skip] e.exe was not found at "%INSTALL_DIR%\e.exe"
)

REM ----- 5. Refresh Explorer -----
ie4uinit.exe -show 2>nul
powershell -NoProfile -Command "[Win32.Shell32]::SHChangeNotify(0x08000000, 0, 0, 0)" >nul 2>&1

echo.
echo ============================================
echo   Uninstallation complete.
echo ============================================
echo.
pause
endlocal
