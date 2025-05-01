@echo off
echo Configuring Windows Firewall for Flask Web Server...

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo This script requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Get Python path
for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i

REM Create firewall rule
echo Creating firewall rule...
netsh advfirewall firewall add rule name="Flask Web Server" dir=in action=allow program="%PYTHON_PATH%" protocol=TCP localport=5000

if %errorLevel% == 0 (
    echo Firewall rule created successfully!
) else (
    echo Failed to create firewall rule.
)

pause 