@echo off
mkdir "C:\Users\CLAUDIA\Downloads\Photos_20250710_100139"
xcopy "C:\Users\CLAUDIA\Downloads\TempPhotos\*" "C:\Users\CLAUDIA\Downloads\Photos_20250710_100139" /Q /Y /C /E
echo Download complete!