@echo off
rem Windows build. Output: dist\music-downloader-vX.Y.Z-windows-x64.zip
setlocal
cd /d "%~dp0"

if not exist .venv-build python -m venv .venv-build || goto :fail
call .venv-build\Scripts\activate.bat
python -m pip install -q --upgrade pip || goto :fail
python -m pip install -q -r requirements.txt -r requirements-build.txt || goto :fail
python packaging\make_ico.py || goto :fail

for /f %%v in ('python packaging\info.py version') do set VERSION=%%v
for /f %%v in ('python packaging\info.py slug') do set SLUG=%%v
set NAME=%SLUG%-v%VERSION%-windows-x64

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
pyinstaller --noconfirm --clean music-downloader.spec || goto :fail

powershell -NoProfile -Command "Compress-Archive -Path 'dist\%SLUG%' -DestinationPath 'dist\%NAME%.zip' -Force" || goto :fail
echo.
echo built: dist\%NAME%.zip
echo run now: dist\%SLUG%\%SLUG%.exe
exit /b 0

:fail
echo BUILD FAILED
exit /b 1
