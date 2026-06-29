# BrainDump — Kişisel "Second Brain" Masaüstü Uygulaması

Kişisel kullanım için Python + PyQt6 ile geliştirilmiş modern bir "Brain Dump" masaüstü uygulaması.

## Özellikler (v0.1.0 — Sadece UI)

- 🎨 Koyu tema (Mor/Eflatun aksan renk paleti)
- 📋 Daraltılabilir sidebar navigasyonu
- ✨ Zengin animasyonlar (slide, fade, hover efektleri)
- 📄 6 sayfa: Dashboard, Yeni Not, Notlar, Günlük Hedefler, İstatistikler, Ayarlar

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python main.py
```

## Teknolojiler

- Python 3.12+
- PyQt6
- qtawesome (Material Design ikonları)

## Proje Yapısı

```
BrainDump/
├── main.py
├── ui/
│   ├── main_window.py
│   ├── sidebar.py
│   └── widgets/
│       ├── dashboard_page.py
│       ├── new_note_page.py
│       ├── notes_page.py
│       ├── goals_page.py
│       ├── stats_page.py
│       └── settings_page.py
├── assets/
│   ├── styles.qss
│   └── fonts/
├── requirements.txt
└── README.md
```

## Sürüm Kontrolü

Proje sürüm kontrolü Git ve GitHub Desktop entegrasyonu ile aktif olarak sağlanmaktadır.

## Lisans

Kişisel kullanım.
