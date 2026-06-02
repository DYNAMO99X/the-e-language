@echo off
REM Build the E interpreter into a single Windows executable.
REM Output: dist\e.exe
REM
REM Prerequisites: Python 3.9+ with PyInstaller installed.
REM   pip install pyinstaller
REM
REM No external libraries are required to *run* E programs; the .exe
REM bundles a small Python runtime plus the src/ package.

setlocal

echo ============================================
echo   Building E interpreter
echo ============================================

where pyinstaller >nul 2>&1
if errorlevel 1 (
    set "PYI=python -m PyInstaller"
) else (
    set "PYI=pyinstaller"
)

pushd "%~dp0"

%PYI% e.spec --clean --noconfirm
if errorlevel 1 (
    echo.
    echo Build FAILED.
    popd
    exit /b 1
)

if not exist "dist\e.exe" (
    echo.
    echo Build did not produce dist\e.exe
    popd
    exit /b 1
)

echo.
echo ============================================
echo   Build succeeded.
echo   dist\e.exe
echo ============================================
echo.
echo You can now test it:
echo   dist\e.exe examples\hello.e
echo.
echo To install system-wide (registers .e files and adds to PATH):
echo   install_win64.bat
echo.

popd
endlocal
