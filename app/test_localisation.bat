@echo off
REM Victoria 2 Localisation Test Script
REM Usage: Run this after launching and quitting the mod

set ERROR_LOG="D:\Steam\steamapps\common\Victoria 2\error.log"
set MOD_FOLDER="D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R"

echo ====================================================================
echo Victoria 2 Localisation Test
echo ====================================================================
echo.

echo Checking for error log...
if not exist %ERROR_LOG% (
    echo ERROR: error.log not found at %ERROR_LOG%
    echo Have you launched Victoria 2 yet?
    pause
    exit /b 1
)

echo.
echo Searching for localisation errors...
echo.
echo --------------------------------------------------------------------
echo Unknown Key Errors (if any):
echo --------------------------------------------------------------------
findstr /i "unknown" %ERROR_LOG%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [!] WARNING: Found unknown key errors! Check above for details.
    echo     Some localisation keys may be missing or misspelled.
) else (
    echo.
    echo [OK] No unknown key errors found!
)

echo.
echo --------------------------------------------------------------------
echo File Not Found Errors (if any):
echo --------------------------------------------------------------------
findstr /i "file not found" %ERROR_LOG%

echo.
echo ====================================================================
echo Test Complete
echo ====================================================================
echo.
echo If no errors shown above, the mod localisation is healthy.
echo You can safely delete: .deprecated files in localisation folder
echo.
pause
