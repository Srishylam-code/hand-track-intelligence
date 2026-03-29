@echo off
echo ==================================================
echo   GITHub SYNC: Mission Control Dashboard v3.0
echo ==================================================
echo.

:: Stage all moves, deletions, and updates
git add -A

:: Commit with a professional message
git commit -m "feat: complete Mission Control UI, 15+ advanced gestures, and project architecture cleanup"

:: Push to your remote repository
:: (Assumes the remote and branch are already set up)
echo.
echo Pushing to GitHub...
git push origin HEAD

echo.
echo ==================================================
echo   SYNC COMPLETE: Your repository is now updated!
echo ==================================================
echo.
pause
