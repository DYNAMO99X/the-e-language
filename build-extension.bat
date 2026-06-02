@echo off
REM Build the VSCode extension (.vsix) for the E language.
REM Output: vscode-e\e-lang-0.1.0.vsix

setlocal

cd /d "%~dp0vscode-e"

echo === Installing dependencies ===
call npm install
if errorlevel 1 (
    echo npm install failed.
    exit /b 1
)

echo === Building TypeScript ===
call npm run build
if errorlevel 1 (
    echo TypeScript build failed.
    exit /b 1
)

echo === Packaging .vsix ===
call npx vsce package
if errorlevel 1 (
    echo vsce package failed.
    exit /b 1
)

echo.
echo === Done ===
echo The extension is at: vscode-e\e-lang-0.1.0.vsix
echo To install it, run:
echo     code --install-extension vscode-e\e-lang-0.1.0.vsix

endlocal
