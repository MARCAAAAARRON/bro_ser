@echo off
echo ========================================================
echo        Bro-ser Production Executable Compiler
echo ========================================================
echo.

:: Detect virtual environment
set VENV_DIR=.venv
if exist %VENV_DIR%\Scripts\activate.bat (
    echo [INFO] Activating virtual environment located at %VENV_DIR%...
    call %VENV_DIR%\Scripts\activate.bat
) else (
    echo [WARNING] No virtual environment detected in %VENV_DIR%. Utilizing system python...
)

echo.
echo [INFO] Installing required dependencies from requirements.txt...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo [INFO] Running PyInstaller package compiler with bro-ser.spec...
pyinstaller --clean --noconfirm bro-ser.spec

echo.
echo ========================================================
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Compilation completed successfully!
    echo [SUCCESS] The standalone app is located at: dist\Bro-ser\
    echo [SUCCESS] You can run and distribute the folder or compress it.
) else (
    echo [ERROR] Compilation failed. Please inspect build logs above.
)
echo ========================================================
echo.
pause
