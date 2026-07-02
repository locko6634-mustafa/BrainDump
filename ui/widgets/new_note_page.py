# -*- coding: utf-8 -*-
"""
Yeni Not Sayfası Widget'ı
Not oluşturma formu: başlık, kategori, içerik editörü ve eylem butonları.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QFrame, QScrollArea
)
from PyQt6.QtCore import (
    Qt, pyqtSignal
)
import qtawesome as qta
from core.json_manager import JSONManager
from core.utils import CATEGORIES


class NewNotePage(QWidget):
    """Yeni not oluşturma sayfası."""
    note_saved = pyqtSignal()
    cancel_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("new_note_page")
        self.db = JSONManager()

        # --- Ana düzen ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setObjectName("new_note_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll içeriği
        content = QWidget()
        content.setObjectName("new_note_content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # --- Sayfa başlığı ---
        title_row = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(
            qta.icon("mdi6.note-plus-outline", color="#10B981").pixmap(28, 28)
        )
        title_row.addWidget(title_icon)

        page_title = QLabel("Yeni Not")
        page_title.setObjectName("page_title")
        title_row.addWidget(page_title)
        title_row.addStretch()
        layout.addLayout(title_row)

        # --- Form alanı (QFrame ile sarılmış) ---
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(16)

        # Başlık giriş alanı
        title_label = QLabel("Başlık")
        title_label.setObjectName("form_label")
        form_layout.addWidget(title_label)

        self.note_title_input = QLineEdit()
        self.note_title_input.setObjectName("note_title_input")
        self.note_title_input.setPlaceholderText("Not başlığı...")
        self.note_title_input.setMinimumHeight(40)
        form_layout.addWidget(self.note_title_input)

        # Kategori seçici
        category_label = QLabel("Kategori")
        category_label.setObjectName("form_label")
        form_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.setObjectName("category_combo")
        self.category_combo.addItems(CATEGORIES)
        self.category_combo.setMinimumHeight(40)
        form_layout.addWidget(self.category_combo)

        # Etiketler Giriş Alanı
        tags_label = QLabel("Etiketler")
        tags_label.setObjectName("form_label")
        form_layout.addWidget(tags_label)

        self.note_tags_input = QLineEdit()
        self.note_tags_input.setObjectName("note_tags_input")
        self.note_tags_input.setPlaceholderText("Etiketler (virgülle ayırın: proje, kişisel, fikir)...")
        self.note_tags_input.setMinimumHeight(40)
        form_layout.addWidget(self.note_tags_input)

        # Büyük metin alanı
        editor_label = QLabel("İçerik")
        editor_label.setObjectName("form_label")
        form_layout.addWidget(editor_label)

        self.note_editor = QTextEdit()
        self.note_editor.setObjectName("note_editor")
        self.note_editor.setPlaceholderText("Notunuzu buraya yazın (Markdown desteği mevcuttur)...")
        self.note_editor.setMinimumHeight(250)
        form_layout.addWidget(self.note_editor)

        layout.addWidget(form_frame)

        # --- Alt butonlar ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.addStretch()

        # İptal butonu
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setMinimumWidth(120)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self.cancel_btn)

        # Kaydet butonu (başlangıçta devre dışı)
        self.save_btn = QPushButton("Kaydet")
        self.save_btn.setObjectName("save_btn")
        self.save_btn.setEnabled(False)
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setMinimumWidth(120)
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_layout.addWidget(self.save_btn)

        layout.addLayout(btn_layout)

        # --- İpucu metni ---
        hint_label = QLabel("💡 İpucu: Notunuzu kaydettikten sonra, üzerine tıklayarak Markdown Önizleme modunda görüntüleyebilirsiniz.")
        hint_label.setObjectName("hint_label")
        layout.addWidget(hint_label)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # Girdi kontrolleri ve eylemleri bağlama
        self.note_title_input.textChanged.connect(self._validate_inputs)
        self.note_editor.textChanged.connect(self._validate_inputs)
        self.save_btn.clicked.connect(self._save_note)
        self.cancel_btn.clicked.connect(self._cancel_note)

        # Ctrl+S Kısayolu (Faz 2)
        from PyQt6.QtGui import QShortcut, QKeySequence
        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(self._on_ctrl_s_pressed)

    def _on_ctrl_s_pressed(self):
        """Ctrl+S basıldığında buton aktifse kaydeder."""
        if self.save_btn.isEnabled():
            self._save_note()

    def _validate_inputs(self):
        """Başlık ve içerik doluluğuna göre Kaydet butonunu aktif/deaktif eder."""
        title = self.note_title_input.text().strip()
        content = self.note_editor.toPlainText().strip()
        self.save_btn.setEnabled(len(title) > 0 and len(content) > 0)

    def _save_note(self):
        """Notu JSON veritabanına kaydeder ve kaydetme sinyali yayar."""
        title = self.note_title_input.text().strip()
        category = self.category_combo.currentText()
        content = self.note_editor.toPlainText().strip()
        tags_raw = self.note_tags_input.text().strip()

        if title and content:
            # Virgülle ayrılmış etiketleri ayıkla ve listeye çevir
            tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]
            if self.db.add_note(title, content, category, tags):
                self._clear_inputs()
                self.note_saved.emit()
                from ui.toast import ToastManager
                ToastManager.show(self, "Başarılı", "Notunuz başarıyla kaydedildi.", "success")
            else:
                from ui.toast import ToastManager
                ToastManager.show(self, "Hata", "Not kaydedilirken bir sorun oluştu.", "error")

    def _on_cancel_clicked(self):
        """Girdileri temizler ve iptal sinyali yayar."""
        self._clear_inputs()
        self.cancel_clicked.emit()

    def _cancel_note(self):
        """Girdileri temizler ve iptal sinyali yayar."""
        self._clear_inputs()
        self.cancel_clicked.emit()

    def _clear_inputs(self):
        """Form girdilerini sıfırlar."""
        self.note_title_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.note_tags_input.clear()
        self.note_editor.clear()
        self.save_btn.setEnabled(False)
