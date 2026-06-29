"""
BrainDump — Kişisel "Second Brain" Masaüstü Uygulaması
Giriş noktası: Font yükleme, tema uygulama, ana pencere başlatma.
"""

import sys
import os
import traceback

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from PyQt6.QtCore import Qt, qInstallMessageHandler, QtMsgType

from ui.main_window import MainWindow


def qt_message_handler(msg_type, context, message):
    """
    Qt dahili uyarılarını filtreler.
    Zararsız olan setPointSize ve grafik efekti painter uyarılarının
    konsolu kirletmesini engeller.
    """
    harmless_warnings = [
        "setPointSize",
        "Painter not active",
        "A paint device can only be painted by one painter",
        "Unbalanced save/restore",
        "QWidgetEffectSourcePrivate::pixmap",
        "worldTransform"
    ]
    if any(warn in message for warn in harmless_warnings):
        return
        
    # Diğer önemli Qt mesajlarını yazdır
    sys.stderr.write(f"[Qt LOG] {message}\n")


def get_asset_path(relative_path: str) -> str:
    """Asset dosyasının mutlak yolunu döndürür (PyInstaller uyumlu)."""
    if getattr(sys, 'frozen', False):
        # PyInstaller ile paketlenmiş
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def load_font():
    """Inter fontunu yükler. Dosya yoksa fallback kullanılır."""
    font_path = get_asset_path(os.path.join("assets", "fonts", "Inter-Variable.ttf"))
    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id >= 0:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                return families[0]
    # Fallback: Segoe UI (Windows varsayılanı)
    return "Segoe UI"


def load_stylesheet() -> str:
    """QSS tema dosyasını okur ve döndürür."""
    qss_path = get_asset_path(os.path.join("assets", "styles.qss"))
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"[UYARI] Stil dosyası bulunamadı: {qss_path}")
        return ""


def main():
    """Uygulamayı başlatır."""
    qInstallMessageHandler(qt_message_handler)
    # Yüksek DPI desteği
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    app = QApplication(sys.argv)

    # Uygulama meta bilgileri
    app.setApplicationName("BrainDump")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("BrainDump")
    app.setWindowIcon(QIcon(get_asset_path(os.path.join("assets", "icon.ico"))))

    # Font yükle
    font_family = load_font()
    app_font = QFont(font_family, 10)
    app.setFont(app_font)

    # Tema (QSS) uygula
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # Ana pencereyi oluştur ve göster
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
