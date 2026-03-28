@echo off
echo ========================================================
echo   Building Luxury Hand Tracker into a Standalone App
echo ========================================================
echo.
echo Installing PyInstaller...
pip install pyinstaller

echo.
echo Compiling Python to EXE... (This will take a few minutes!)
pyinstaller --noconfirm --onedir --console --add-data "templates;templates" --collect-all mediapipe main.py

echo.
echo ========================================================
echo   DONE!
echo   1. Go into the new "dist" folder in your project.
echo   2. You will see a folder named "main" inside it.
echo   3. Right-click the "main" folder and ZIP it.
echo   4. Send that ZIP file to your friend!
echo   5. They just unzip it and double-click "main.exe". No Python required!
echo ========================================================
pause
