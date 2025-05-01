@echo off
echo Pushing Smart Attendance System to GitHub...

REM Check if git is installed
where git >nul 2>&1
if %errorLevel% neq 0 (
    echo Git is not installed or not in PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Initialize git repository if not already initialized
if not exist .git (
    echo Initializing git repository...
    git init
)

REM Add all files
echo Adding files to git...
git add .

REM Commit changes
echo Committing changes...
git commit -m "Initial commit of Smart Attendance System"

REM Ask for GitHub repository URL
set /p REPO_URL=Enter your GitHub repository URL (e.g., https://github.com/username/smart-attendance-system.git): 

REM Add remote and push
echo Adding remote repository...
git remote add origin %REPO_URL% 2>nul
if %errorLevel% neq 0 (
    echo Remote already exists, updating...
    git remote set-url origin %REPO_URL%
)

echo Pushing to GitHub...
git push -u origin master

if %errorLevel% equ 0 (
    echo Successfully pushed to GitHub!
    echo Your repository is now available at %REPO_URL%
) else (
    echo Failed to push to GitHub.
    echo Please make sure you have created the repository on GitHub first.
    echo You can create a repository at https://github.com/new
)

pause 