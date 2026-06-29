# -*- coding: utf-8 -*-
"""
Ayarlar Sayfası Widget'ı
Uygulama ayarları: tema, dil, not tercihleri ve hakkında bilgisi.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QCheckBox, QFrame, QScrollArea,
    QGraphicsOpacityEffect, QPushButton, QFileDialog,
    QApplication, QMessageBox
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve
)
import qtawesome as qta
from core.json_manager import JSONManager


class SettingsGroup(QFrame):
    """Ayar grubu çerçevesi — başlık ve ayar satırlarını barındırır."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_group")
        self.setStyleSheet(
            "QFrame#settings_group { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 12px; }"
        )

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(14)

        # Grup başlığı
        title_label = QLabel(title)
        title_label.setObjectName("group_title")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: 700; color: #f4f4f5;"
            " padding-bottom: 4px; border-bottom: 1px solid #27272a;"
        )
        self._layout.addWidget(title_label)

    def add_row(self, label_text: str, control_widget: QWidget):
        """Gruba etiket + kontrol satırı ekler."""
        row = QHBoxLayout()
        row.setSpacing(16)

        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; color: #a0a0b8;")
        row.addWidget(label)

        row.addStretch()
        row.addWidget(control_widget)

        self._layout.addLayout(row)

    def add_info_row(self, label_text: str, value_text: str):
        """Gruba salt okunur bilgi satırı ekler."""
        row = QHBoxLayout()
        row.setSpacing(16)

        label = QLabel(label_text)
        label.setStyleSheet("font-size: 14px; color: #a0a0b8;")
        row.addWidget(label)

        row.addStretch()

        value = QLabel(value_text)
        value.setStyleSheet("font-size: 14px; color: #e8e8e8;")
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row.addWidget(value)

        self._layout.addLayout(row)


class SettingsPage(QWidget):
    """Ayarlar sayfası — uygulama tercihleri ve hakkında bilgisi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_page")

        # Ortak ComboBox stili
        combo_style = (
            "QComboBox { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 8px; padding: 6px 12px; color: #f4f4f5;"
            " font-size: 13px; min-width: 160px; }"
            "QComboBox:focus { border-color: #10B981; }"
            "QComboBox:disabled { color: #71717a; }"
            "QComboBox::drop-down { border: none; width: 28px; }"
            "QComboBox QAbstractItemView { background: #18181b; color: #f4f4f5;"
            " selection-background-color: #10B981; border: 1px solid #27272a; }"
        )

        # --- Ana düzen ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setObjectName("settings_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll içeriği
        content = QWidget()
        content.setObjectName("settings_content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # --- Sayfa başlığı ---
        title_row = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(
            qta.icon("mdi6.cog-outline", color="#10B981").pixmap(28, 28)
        )
        title_row.addWidget(title_icon)

        page_title = QLabel("Ayarlar")
        page_title.setObjectName("page_title")
        page_title.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #e8e8e8;"
        )
        title_row.addWidget(page_title)
        title_row.addStretch()
        layout.addLayout(title_row)

        self.db = JSONManager()

        # ============================================
        # GRUP 1: Genel
        # ============================================
        general_group = SettingsGroup("Genel")

        # Tema seçici
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        self.theme_combo.addItems(["Koyu Tema", "Açık Tema"])
        self.theme_combo.setEnabled(True)
        self.theme_combo.setStyleSheet(combo_style)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        general_group.add_row("Tema", self.theme_combo)

        # Dil seçici
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.addItems(["Türkçe", "English"])
        self.language_combo.setEnabled(True)
        self.language_combo.setStyleSheet(combo_style)
        general_group.add_row("Dil", self.language_combo)

        layout.addWidget(general_group)

        # ============================================
        # GRUP 2: Not Ayarları
        # ============================================
        notes_group = SettingsGroup("Not Ayarları")

        # Varsayılan kategori
        self.default_category_combo = QComboBox()
        self.default_category_combo.setObjectName("default_category_combo")
        self.default_category_combo.addItems(["Genel", "İş", "Kişisel"])
        self.default_category_combo.setStyleSheet(combo_style)
        notes_group.add_row("Varsayılan Kategori", self.default_category_combo)

        # Otomatik kaydetme
        self.auto_save_check = QCheckBox()
        self.auto_save_check.setObjectName("auto_save_check")
        self.auto_save_check.setChecked(True)
        self.auto_save_check.setStyleSheet(
            "QCheckBox::indicator { width: 20px; height: 20px;"
            " border: 2px solid #27272a; border-radius: 4px;"
            " background: transparent; }"
            "QCheckBox::indicator:checked { background: #10B981;"
            " border-color: #10B981; }"
            "QCheckBox::indicator:hover { border-color: #34d399; }"
        )
        notes_group.add_row("Otomatik Kaydetme", self.auto_save_check)

        layout.addWidget(notes_group)

        # ============================================
        # GRUP 3: Hakkında
        # ============================================
        about_group = SettingsGroup("Hakkında")
        about_group.add_info_row("Uygulama", "BrainDump v0.1.0")
        about_group.add_info_row("Geliştirici", "Mustafa")

        # Açıklama satırı (uzun metin)
        desc_row = QHBoxLayout()
        desc_label = QLabel("Açıklama")
        desc_label.setStyleSheet("font-size: 14px; color: #a0a0b8;")
        desc_row.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignTop)

        desc_row.addStretch()

        desc_value = QLabel("Kişisel kullanım için masaüstü\nnot ve hedef takip uygulaması.")
        desc_value.setStyleSheet("font-size: 14px; color: #e8e8e8;")
        desc_value.setWordWrap(True)
        desc_value.setMaximumWidth(300)
        desc_row.addWidget(desc_value)

        about_group._layout.addLayout(desc_row)

        layout.addWidget(about_group)

        # ============================================
        # GRUP 4: Veri Yönetimi
        # ============================================
        data_group = SettingsGroup("Veri Yönetimi")
        
        btn_style = (
            "QPushButton { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 8px; color: #f4f4f5; padding: 8px 16px; font-weight: 600; font-size: 13px; }"
            "QPushButton:hover { border-color: #10B981; color: #ffffff; }"
        )

        self.btn_export = QPushButton("Verileri Yedekle (JSON)")
        self.btn_export.setStyleSheet(btn_style)
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self._on_export_backup)
        data_group.add_row("Dışa Aktar", self.btn_export)

        self.btn_import = QPushButton("Yedekten Geri Yükle")
        self.btn_import.setStyleSheet(btn_style)
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.clicked.connect(self._on_import_backup)
        data_group.add_row("İçe Aktar", self.btn_import)

        layout.addWidget(data_group)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

    def _on_theme_changed(self, index):
        """Seçilen temayı dinamik olarak uygular."""
        theme_name = self.theme_combo.currentText()
        app = QApplication.instance()
        
        import os
        import sys
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        if theme_name == "Açık Tema":
            qss_file = os.path.join(base_path, "assets", "light_styles.qss")
        else:
            qss_file = os.path.join(base_path, "assets", "styles.qss")
            
        try:
            with open(qss_file, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
        except Exception as e:
            print(f"[HATA] Tema QSS yüklenemedi {qss_file}: {e}")

    def _on_export_backup(self):
        """Verileri JSON dosyası olarak dışa aktarır."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Yedeği Kaydet",
            "",
            "JSON Dosyaları (*.json)"
        )
        if file_path:
            if self.db.export_backup(file_path):
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Tüm verileriniz başarıyla JSON dosyası olarak yedeklendi!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Hata",
                    "Yedek aktarılırken bir hata oluştu."
                )

    def _on_import_backup(self):
        """Yedek JSON dosyasını içeri aktarır."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Yedek Dosyası Seç",
            "",
            "JSON Dosyaları (*.json)"
        )
        if file_path:
            from ui.widgets.dialogs import ModernConfirmDialog
            ok = ModernConfirmDialog.confirm(
                self,
                "Yedeği Geri Yükle",
                "Yedeği geri yüklemek mevcut tüm not ve hedeflerinizi silecektir. Devam etmek istiyor musunuz?",
                is_danger=True
            )
            if ok:
                if self.db.import_backup(file_path):
                    QMessageBox.information(
                        self,
                        "Başarılı",
                        "Yedek veriler başarıyla geri yüklendi! Değişikliklerin yansıması için lütfen sayfaları yenileyin."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Hata",
                        "Yedek yüklenirken bir hata oluştu. Lütfen dosya formatının doğru olduğundan emin olun."
                    )
