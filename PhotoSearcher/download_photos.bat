@echo off
mkdir "C:\Users\CLAUDIA\Downloads\Photos_20250620_090339"
xcopy "C:\Users\CLAUDIA\Downloads\TempPhotos\*" "C:\Users\CLAUDIA\Downloads\Photos_20250620_090339" /Q /Y /C /E
echo Download complete!