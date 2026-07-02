# -*- coding: utf-8 -*-
"""
Ayarlar Sayfası Widget'ı
Uygulama ayarları: tema, dil, not tercihleri ve hakkında bilgisi.
QSettings ile kalıcı olarak ayarları saklar.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QCheckBox, QFrame, QScrollArea,
    QPushButton, QFileDialog, QApplication, QMessageBox,
    QLineEdit
)
from PyQt6.QtCore import (
    Qt, QSettings
)
import qtawesome as qta
from core.json_manager import JSONManager
from core.utils import CATEGORIES


class SettingsGroup(QFrame):
    """Ayar grubu çerçevesi — başlık ve ayar satırlarını barındırır."""

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_group")

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(14)

        # Grup başlığı
        title_label = QLabel(title)
        title_label.setObjectName("group_title")
        self._layout.addWidget(title_label)

    def add_row(self, label_text: str, control_widget: QWidget):
        """Gruba etiket + kontrol satırı ekler."""
        row = QHBoxLayout()
        row.setSpacing(16)

        label = QLabel(label_text)
        label.setObjectName("setting_label_text")
        row.addWidget(label)

        row.addStretch()
        row.addWidget(control_widget)

        self._layout.addLayout(row)

    def add_info_row(self, label_text: str, value_text: str):
        """Gruba salt okunur bilgi satırı ekler."""
        row = QHBoxLayout()
        row.setSpacing(16)

        label = QLabel(label_text)
        label.setObjectName("setting_label_text")
        row.addWidget(label)

        row.addStretch()

        value = QLabel(value_text)
        value.setObjectName("setting_value_text")
        value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row.addWidget(value)

        self._layout.addLayout(row)


class SettingsPage(QWidget):
    """Ayarlar sayfası — uygulama tercihleri ve hakkında bilgisi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_page")
        self.db = JSONManager()
        
        # QSettings nesnesi
        self.settings = QSettings("BrainDump", "BrainDump")

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
        title_row.addWidget(page_title)
        title_row.addStretch()
        layout.addLayout(title_row)

        # ============================================
        # GRUP 1: Genel
        # ============================================
        general_group = SettingsGroup("Genel")

        # Tema seçici
        self.theme_combo = QComboBox()
        self.theme_combo.setObjectName("theme_combo")
        self.theme_combo.addItems(["Koyu Tema", "Açık Tema"])
        general_group.add_row("Tema", self.theme_combo)

        # Dil seçici
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("language_combo")
        self.language_combo.addItems(["Türkçe", "English"])
        general_group.add_row("Dil", self.language_combo)

        layout.addWidget(general_group)

        # ============================================
        # GRUP 2: Not Ayarları
        # ============================================
        notes_group = SettingsGroup("Not Ayarları")

        # Varsayılan kategori
        self.default_category_combo = QComboBox()
        self.default_category_combo.setObjectName("default_category_combo")
        self.default_category_combo.addItems(CATEGORIES)
        notes_group.add_row("Varsayılan Kategori", self.default_category_combo)

        # Otomatik kaydetme
        self.auto_save_check = QCheckBox()
        self.auto_save_check.setObjectName("auto_save_check")
        notes_group.add_row("Otomatik Kaydetme", self.auto_save_check)

        layout.addWidget(notes_group)

        # ============================================
        # GRUP 2.5: Kategori Yönetimi (Faz 3)
        # ============================================
        category_group = SettingsGroup("Kategori Yönetimi")

        # Mevcut Kategoriler ve Sil butonu
        self.settings_categories_combo = QComboBox()
        self.settings_categories_combo.setObjectName("settings_categories_combo")
        self.settings_categories_combo.addItems(CATEGORIES)

        self.btn_delete_category = QPushButton("Seçileni Sil")
        self.btn_delete_category.setObjectName("danger_btn")
        self.btn_delete_category.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_delete_category.setMinimumHeight(32)
        self.btn_delete_category.clicked.connect(self._on_delete_category)

        delete_row_widget = QWidget()
        delete_layout = QHBoxLayout(delete_row_widget)
        delete_layout.setContentsMargins(0, 0, 0, 0)
        delete_layout.addWidget(self.settings_categories_combo, stretch=1)
        delete_layout.addWidget(self.btn_delete_category)
        category_group.add_row("Mevcut Kategoriler", delete_row_widget)

        # Yeni Kategori ve Ekle butonu
        self.input_new_category = QLineEdit()
        self.input_new_category.setObjectName("dialog_input")
        self.input_new_category.setPlaceholderText("Yeni kategori adı...")
        self.input_new_category.setMinimumHeight(32)

        self.btn_add_category = QPushButton("Kategori Ekle")
        self.btn_add_category.setObjectName("save_btn")
        self.btn_add_category.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_category.setMinimumHeight(32)
        self.btn_add_category.clicked.connect(self._on_add_category)

        add_row_widget = QWidget()
        add_layout = QHBoxLayout(add_row_widget)
        add_layout.setContentsMargins(0, 0, 0, 0)
        add_layout.addWidget(self.input_new_category, stretch=1)
        add_layout.addWidget(self.btn_add_category)
        category_group.add_row("Yeni Kategori Ekle", add_row_widget)

        layout.addWidget(category_group)

        # ============================================
        # GRUP 3: Hakkında
        # ============================================
        about_group = SettingsGroup("Hakkında")
        about_group.add_info_row("Uygulama", "BrainDump v0.1.0")
        about_group.add_info_row("Geliştirici", "Mustafa")

        # Açıklama satırı (uzun metin)
        desc_row = QHBoxLayout()
        desc_label = QLabel("Açıklama")
        desc_label.setObjectName("setting_label_text")
        desc_row.addWidget(desc_label, alignment=Qt.AlignmentFlag.AlignTop)

        desc_row.addStretch()

        desc_value = QLabel("Kişisel kullanım için masaüstü\nnot ve hedef takip uygulaması.")
        desc_value.setObjectName("setting_value_text")
        desc_value.setWordWrap(True)
        desc_value.setMaximumWidth(300)
        desc_row.addWidget(desc_value)

        about_group._layout.addLayout(desc_row)

        layout.addWidget(about_group)

        # ============================================
        # GRUP 4: Veri Yönetimi
        # ============================================
        data_group = SettingsGroup("Veri Yönetimi")

        self.btn_export = QPushButton("Verileri Yedekle (JSON)")
        self.btn_export.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export.clicked.connect(self._on_export_backup)
        data_group.add_row("Dışa Aktar", self.btn_export)

        self.btn_import = QPushButton("Yedekten Geri Yükle")
        self.btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_import.clicked.connect(self._on_import_backup)
        data_group.add_row("İçe Aktar", self.btn_import)

        layout.addWidget(data_group)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)
        
        # QSettings verilerini arayüze yükleme
        self._load_saved_settings()

        # Değişiklik tetikleyicilerini bağlama
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.default_category_combo.currentIndexChanged.connect(self._on_default_category_changed)
        self.auto_save_check.stateChanged.connect(self._on_auto_save_changed)

    def _load_saved_settings(self):
        """Kaydedilmiş ayarları QSettings'ten yükler."""
        # 1. Tema
        saved_theme = self.settings.value("theme", "Koyu Tema")
        self.theme_combo.setCurrentText(saved_theme)
        
        # 2. Dil
        saved_lang = self.settings.value("language", "Türkçe")
        self.language_combo.setCurrentText(saved_lang)
        
        # 3. Varsayılan Kategori
        saved_cat = self.settings.value("default_category", "Genel")
        self.default_category_combo.setCurrentText(saved_cat)
        
        # 4. Otomatik Kaydetme
        saved_auto_save = self.settings.value("auto_save", True, type=bool)
        self.auto_save_check.setChecked(saved_auto_save)

    def _on_theme_changed(self, index):
        """Seçilen temayı kaydeder ve dinamik olarak uygular."""
        theme_name = self.theme_combo.currentText()
        self.settings.setValue("theme", theme_name)
        
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

    def _on_language_changed(self, index):
        """Seçilen dili kaydeder."""
        lang_name = self.language_combo.currentText()
        self.settings.setValue("language", lang_name)

    def _on_default_category_changed(self, index):
        """Seçilen varsayılan kategoriyi kaydeder."""
        cat_name = self.default_category_combo.currentText()
        self.settings.setValue("default_category", cat_name)

    def _on_auto_save_changed(self, state):
        """Otomatik kaydetme durumunu kaydeder."""
        is_checked = self.auto_save_check.isChecked()
        self.settings.setValue("auto_save", is_checked)

    def _on_add_category(self):
        """Yeni kategori ekler ve kaydeder."""
        cat_name = self.input_new_category.text().strip()
        if not cat_name:
            return
            
        from core.utils import get_categories
        current_cats = get_categories()
        
        if cat_name in current_cats:
            from ui.toast import ToastManager
            ToastManager.show(self, "Hata", "Bu kategori zaten mevcut.", "error")
            return
            
        current_cats.append(cat_name)
        self.settings.setValue("custom_categories", current_cats)
        self.input_new_category.clear()
        
        self._reload_category_combos()
        from ui.toast import ToastManager
        ToastManager.show(self, "Başarılı", f"'{cat_name}' kategorisi başarıyla eklendi.", "success")

    def _on_delete_category(self):
        """Seçilen kategoriyi siler."""
        cat_to_delete = self.settings_categories_combo.currentText()
        if not cat_to_delete:
            return
            
        from core.utils import get_categories
        current_cats = get_categories()
        
        if len(current_cats) <= 1:
            from ui.toast import ToastManager
            ToastManager.show(self, "Hata", "En az bir kategori bulunmalıdır.", "error")
            return
            
        from ui.widgets.dialogs import ModernConfirmDialog
        ok = ModernConfirmDialog.confirm(
            self,
            "Kategoriyi Sil",
            f"'{cat_to_delete}' kategorisini kalıcı olarak silmek istediğinizden emin misiniz?",
            is_danger=True
        )
        if ok:
            current_cats.remove(cat_to_delete)
            self.settings.setValue("custom_categories", current_cats)
            
            # Eğer varsayılan kategori olarak seçiliyse, ilkini seç
            if self.default_category_combo.currentText() == cat_to_delete:
                self.default_category_combo.setCurrentIndex(0)
                self.settings.setValue("default_category", self.default_category_combo.currentText())
                
            self._reload_category_combos()
            from ui.toast import ToastManager
            ToastManager.show(self, "Başarılı", f"'{cat_to_delete}' kategorisi silindi.", "success")

    def _reload_category_combos(self):
        """Sayfadaki tüm kategori seçim kutularını yeniler."""
        from core.utils import CATEGORIES
        self.settings_categories_combo.clear()
        self.settings_categories_combo.addItems(CATEGORIES)
        
        current_default = self.default_category_combo.currentText()
        self.default_category_combo.clear()
        self.default_category_combo.addItems(CATEGORIES)
        
        if current_default in CATEGORIES:
            self.default_category_combo.setCurrentText(current_default)

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
                from ui.toast import ToastManager
                ToastManager.show(self, "Başarılı", "Tüm verileriniz başarıyla yedeklendi!", "success")
            else:
                from ui.toast import ToastManager
                ToastManager.show(self, "Hata", "Yedek aktarılırken bir hata oluştu.", "error")

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
                    from ui.toast import ToastManager
                    ToastManager.show(self, "Başarılı", "Yedek veriler başarıyla geri yüklendi!", "success")
                else:
                    from ui.toast import ToastManager
                    ToastManager.show(self, "Hata", "Yedek yüklenirken bir hata oluştu.", "error")
