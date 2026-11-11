@echo off
setlocal
cd /d "%~dp0"
set ASTRO_TELEMETRY_DISABLED=1
set "CRITTER_NODE=%LOCALAPPDATA%\Programs\nodejs\node.exe"
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" (
  set "CRITTER_NODE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
)
if not exist "%CRITTER_NODE%" set "CRITTER_NODE=node"
if not exist "node_modules\astro\bin\astro.mjs" (
  echo Dependencies are missing. Follow README.md to install them first.
  pause
  exit /b 1
)
echo.
echo Critter Creek local preview
echo Website:       http://127.0.0.1:4321/
echo Staff editor:  http://127.0.0.1:4321/keystatic/
echo.
echo Keep this window open while reviewing. Press Ctrl+C to stop.
echo If that port is busy, use the Local address printed below.
echo.
"%CRITTER_NODE%" node_modules\astro\bin\astro.mjs dev --host 127.0.0.1
pause
