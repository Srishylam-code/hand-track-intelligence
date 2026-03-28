@echo off
echo.
echo [🖐️ HandTrack Intelligence] Starting GitHub Push...
echo --------------------------------------------------

:: 1. Initialize Git
echo [1/4] Initializing local repository...
git init

:: 2. Stage and Commit
echo [2/4] Staging files and creating initial commit...
git add .
git commit -m "Initial commit: AI Hand Tracking & Vision Engine"

:: 3. Setup Remote (Handles both new and existing remotes)
echo [3/4] Linking to https://github.com/Srishylam-code/hand-track-intelligence.git...
git branch -M main
git remote add origin https://github.com/Srishylam-code/hand-track-intelligence.git 2>nul
git remote set-url origin https://github.com/Srishylam-code/hand-track-intelligence.git

:: 4. Push to Main
echo [4/4] Pushing to GitHub...
echo.
git push -u origin main

echo.
echo --------------------------------------------------
echo ✅ Done! Your code is now live on GitHub.
echo.
pause
