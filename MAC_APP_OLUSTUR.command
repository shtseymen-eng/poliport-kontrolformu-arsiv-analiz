#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "SEYMEN Kontrol Formu Arşiv Analizi macOS uygulaması oluşturuluyor..."
python3 -m pip install -r requirements.txt
python3 -m PyInstaller --noconfirm --clean --windowed --name "SEYMEN_Kontrol_Formu_Arsiv_Analizi" app.py

echo
echo "Uygulama hazır: dist/SEYMEN_Kontrol_Formu_Arsiv_Analizi.app"
