@echo off
setlocal
cd /d "%~dp0"
title Build The Benefactor

echo Building "The Benefactor.exe" ...
echo.

if not exist launder_app.pyw (
  echo Can't find launder_app.pyw. Put this file in the same folder as it.
  goto :fail
)
if not exist launder.py (
  echo Can't find launder.py. It needs to be in this folder too.
  goto :fail
)
if not exist logo.ico (
  echo Can't find logo.ico. Run make_shortcut.py once first - it creates logo.ico.
  goto :fail
)

python --version >nul 2>&1
if errorlevel 1 (
  echo Python wasn't found. Install Python from python.org and tick "Add python.exe to PATH".
  goto :fail
)

echo Checking the app files being packaged:
findstr /C:"APP_VERSION =" launder_app.pyw
findstr /C:"def default_profiles_file" launder.py >nul
if errorlevel 1 (
  echo.
  echo launder.py is the OLD version - clients would not be saved properly.
  echo Replace it with the newest launder.py and run this again.
  goto :fail
)
echo.

rem Remove the old build first, so we can tell for sure that a new one was made.
if exist "The Benefactor.exe" del /F /Q "The Benefactor.exe" >nul 2>&1
if exist "The Benefactor.exe" (
  echo Can't replace "The Benefactor.exe" - it is still open.
  echo Close the app completely ^(check the taskbar^), then run this again.
  goto :fail
)
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1
del /F /Q "The Benefactor.spec" >nul 2>&1

echo Step 1 of 2: installing PyInstaller ...
python -m pip install --upgrade pyinstaller
if errorlevel 1 goto :fail

echo.
echo Step 2 of 2: building the app (this takes a minute or two) ...
copy /Y launder_app.pyw benefactor_main.py >nul
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "The Benefactor" --icon "logo.ico" benefactor_main.py
set RESULT=%errorlevel%
del benefactor_main.py >nul 2>&1
if not "%RESULT%"=="0" goto :fail

copy /Y "dist\The Benefactor.exe" "The Benefactor.exe" >nul
if not exist "The Benefactor.exe" (
  echo The build finished but the new .exe couldn't be copied here. Antivirus may have blocked it.
  echo Look for it in the "dist" folder.
  goto :fail
)
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1
del "The Benefactor.spec" >nul 2>&1

echo.
echo Done! New build made:
for %%F in ("The Benefactor.exe") do echo   %%~fF   ^(%%~tF^)
echo.
echo Open it and check the title bar says the version shown above, and that the
echo bottom right says where your clients are saved.
echo.
pause
exit /b 0

:fail
echo.
echo The build didn't finish. Scroll up for the error message.
echo.
pause
exit /b 1
