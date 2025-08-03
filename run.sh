#!/bin/bash

while true; do
    echo "Önce ESP32'yi sıfırlayın ardından aşağıdaki seçeneklerden birini seçin:"
    echo "1. İvmeölçer Kalibrasyonu"
    echo "2. Jiroskop Kalibrasyonu"
    echo "3. Magnetometre Kalibrasyonu"
    echo "4. Sensör Verilerini Oku"
    echo "5. Durum cayrosunu aç"
    echo "0. Çıkış"
    echo ""

    read -p "Seçiminiz (0-5): " choice

    case $choice in
        1)
            echo ""
            echo "Kalibrasyon Başlatılıyor..."
            python3 src/main.py --calibrate accel
            ;;
        2)
            echo ""
            echo "Kalibrasyon Başlatılıyor..."
            python3 src/main.py --calibrate gyro
            ;;
        3)
            echo ""
            echo "Kalibrasyon Başlatılıyor..."
            python3 src/main.py --calibrate magn
            ;;
        4)
            echo ""
            echo "Veriler:"
            python3 src/main.py
            ;;
        5)
            echo ""
            echo "Program başlatılıyor"
            python3 src/ai.py
            ;;
        0)
            echo ""
            echo "Program sonlandırılıyor..."
            exit 0
            ;;
        *)
            echo "Geçersiz seçim!"
            ;;
    esac
    
    echo ""
done
