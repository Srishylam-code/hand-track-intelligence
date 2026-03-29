@echo off
echo ==================================================
echo   FINISHING MISSION CONTROL: Permanent Cleanup
echo ==================================================
echo.

:: Deleting Unwanted/Legacy Files
echo Deleting legacy Python tracking scripts...
del auth_app.py finger_particle_system.py hand_tracker.py hud_visualizer.py osc_sender.py 2>nul
del patch_dashboard.py fix_encoding.py hand_landmarker.task particle_demo.py 2>nul
del touchdesigner_setup.md push_to_github.bat build_app.bat cleanup.bat users.xlsx 2>nul

echo Root directory purged. Only core files remain.
echo.

:: Step 2: GITHub SYNC
echo Stage all deletions and updates...
git add -A

echo Committing changes...
git commit -m "chore: permanent removal of legacy Python scripts and full root cleanup"

echo Pushing to GitHub...
git push origin HEAD

echo.
echo ==================================================
echo   PURGE & SYNC COMPLETE: Your repo is now perfect!
echo ==================================================
echo.
pause
