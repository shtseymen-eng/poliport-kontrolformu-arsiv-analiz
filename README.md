# SEYMEN Kontrol Formu Arşiv Analizi

Bu uygulama, daha önce indirilen kontrol formu Excel dosyalarını analiz eder.
Mevcut indirme uygulamasına, ReportServer'a veya Chrome'a bağlanmaz.

## Beklenen klasör düzeni

```text
Ana Klasör
└── 2026
    └── EYLÜL
        └── 25
            └── AGENA LOJ.
                └── Kontrol Formları
                    └── 34ABC123_....xlsx
```

## Çalıştırma

Windows'ta `KUR_VE_CALISTIR.bat` dosyasına çift tıklayın.

Uygulamada ana arşiv klasörünü seçin; yıl, ay, gün ve nakliyeci filtrelerini
belirleyin. `Analizi Listele` çekicileri tek satır mantığıyla tarar. Her tarihli
evrak ekranda görünür; geçmiş tarihler kırmızı, 20 gün ve altı turuncudur.

`Excel'e Aktar` aşağıdaki sayfaları oluşturur: Özet, Çekiciler, Dorseler,
ISO Tanklar, Sürücüler, Kritik Evraklar ve Okunamayan Dosyalar.

## EXE oluşturma

Windows bilgisayarda `EXE_OLUSTUR.bat` dosyasına çift tıklayın. Oluşan program
`dist\\SEYMEN_Kontrol_Formu_Arsiv_Analizi` klasöründe yer alır.

GitHub'a proje yüklendikten sonra **Actions → Windows EXE Build → Run workflow**
ile de Windows EXE paketi üretilebilir.
