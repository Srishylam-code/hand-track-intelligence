@echo off
echo Cleaning project for GitHub push...
mkdir legacy_archive 2>nul
move auth_app.py legacy_archive\ 2>nul
move finger_particle_system.py legacy_archive\ 2>nul
move hand_tracker.py legacy_archive\ 2>nul
move hud_visualizer.py legacy_archive\ 2>nul
move osc_sender.py legacy_archive\ 2>nul
move patch_dashboard.py legacy_archive\ 2>nul
move fix_encoding.py legacy_archive\ 2>nul
move hand_landmarker.task legacy_archive\ 2>nul
move particle_demo.py legacy_archive\ 2>nul
move touchdesigner_setup.md legacy_archive\ 2>nul
move build_app.bat legacy_archive\ 2>nul
move push_to_github.bat legacy_archive\ 2>nul
echo.
echo ==================================================
echo   CLEANUP COMPLETE: Core root is now professional.
echo ==================================================
echo.
pause
