@echo off
chcp 65001 >nul
echo SEYMEN Kontrol Formu Arşiv Analizi EXE oluşturuluyor...
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --windowed --name "SEYMEN_Kontrol_Formu_Arsiv_Analizi" app.py
echo.
echo EXE hazır: dist\SEYMEN_Kontrol_Formu_Arsiv_Analizi\SEYMEN_Kontrol_Formu_Arsiv_Analizi.exe
pause
