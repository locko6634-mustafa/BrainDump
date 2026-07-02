# -*- coding: utf-8 -*-
"""
Özel Modern Diyalog Bileşenleri
Çerçevesiz, gölgeli, projenin temasına uygun ve QSS uyumlu özel QDialog sınıfları.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QFrame, QGraphicsDropShadowEffect,
    QTextEdit, QTextBrowser, QComboBox
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor
import qtawesome as qta
from core.utils import CATEGORIES, format_date_tr


class BaseModernDialog(QDialog):
    """Modern diyaloglar için çerçevesiz, gölgeli temel sınıf."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Sürükleme pozisyonu
        self.drag_position = QPoint()

        # Dış düzen (gölgenin sığabilmesi için kenar boşluğu veriyoruz)
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(12, 12, 12, 12)

        # Ana içerik çerçevesi
        self.container = QFrame()
        self.container.setObjectName("dialog_container")
        self.outer_layout.addWidget(self.container)

        # Yumuşak gölge efekti
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(16)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.container.setGraphicsEffect(self.shadow)

        # İçerik düzeni
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(20, 16, 20, 20)
        self.layout.setSpacing(16)

        # Üst Başlık Barı (Tüm modern diyaloglarda standart)
        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(8)
        
        self.title_icon = QLabel()
        self.header_layout.addWidget(self.title_icon)

        self.title_label = QLabel()
        self.title_label.setObjectName("dialog_title")
        self.header_layout.addWidget(self.title_label, stretch=1)

        # Kapatma (X) Butonu
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("close_btn")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.setIcon(qta.icon("mdi6.close", color="#a0a0b8"))
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 4px; }"
            "QPushButton:hover { background: rgba(255, 82, 82, 0.2); }"
        )
        self.close_btn.clicked.connect(self.reject)
        self.header_layout.addWidget(self.close_btn)

        self.layout.addLayout(self.header_layout)

    # --- Pencere Sürükleme Davranışı ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class ModernInputDialog(BaseModernDialog):
    """Metin girişi almak için tasarlanmış modern diyalog kutusu."""
    def __init__(self, title: str, label_text: str, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.title_label.setText(title)
        self.title_icon.setPixmap(qta.icon("mdi6.target", color="#10B981").pixmap(18, 18))
        self.setMinimumWidth(320)

        # Açıklama etiketi
        self.info_label = QLabel(label_text)
        self.info_label.setObjectName("dialog_info_label")
        self.info_label.setWordWrap(True)
        self.layout.addWidget(self.info_label)

        # Metin girdi kutusu
        self.input_field = QLineEdit()
        self.input_field.setObjectName("dialog_input")
        self.input_field.setPlaceholderText(placeholder)
        self.input_field.setMinimumHeight(38)
        self.input_field.returnPressed.connect(self.accept)
        self.layout.addWidget(self.input_field)

        # Butonlar satırı
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        # İptal butonu
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setMinimumHeight(34)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        # Onayla/Ekle butonu
        self.ok_btn = QPushButton("Ekle")
        self.ok_btn.setObjectName("save_btn")
        self.ok_btn.setMinimumHeight(34)
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.layout.addLayout(btn_layout)
        self.input_field.setFocus()

    def get_text(self) -> str:
        return self.input_field.text().strip()

    @staticmethod
    def getText(parent, title: str, label_text: str, placeholder: str = "") -> tuple[str, bool]:
        dialog = ModernInputDialog(title, label_text, placeholder, parent)
        result = dialog.exec()
        return dialog.get_text(), (result == QDialog.DialogCode.Accepted)


class ModernConfirmDialog(BaseModernDialog):
    """Evet/Hayır şeklinde onay almak için tasarlanmış modern diyalog kutusu."""
    def __init__(self, title: str, message: str, is_danger: bool = False, parent=None):
        super().__init__(parent)
        self.title_label.setText(title)
        self.setMinimumWidth(340)

        # İşlem türüne göre başlık ikonu belirleme
        if is_danger:
            self.title_icon.setPixmap(qta.icon("mdi6.alert-circle", color="#FF5252").pixmap(18, 18))
        else:
            self.title_icon.setPixmap(qta.icon("mdi6.help-circle", color="#10B981").pixmap(18, 18))

        # Orta Kısım: İkon + Mesaj satırı
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 8, 0, 8)

        # Büyük durum ikonu
        self.status_icon = QLabel()
        if is_danger:
            icon_img = qta.icon("mdi6.alert-outline", color="#FF5252").pixmap(32, 32)
        else:
            icon_img = qta.icon("mdi6.help-circle-outline", color="#10B981").pixmap(32, 32)
        self.status_icon.setPixmap(icon_img)
        self.status_icon.setAlignment(Qt.AlignmentFlag.AlignTop)
        content_layout.addWidget(self.status_icon)

        # Mesaj metni
        self.msg_label = QLabel(message)
        self.msg_label.setObjectName("dialog_info_label")
        self.msg_label.setWordWrap(True)
        content_layout.addWidget(self.msg_label, stretch=1)

        self.layout.addLayout(content_layout)

        # Butonlar satırı
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        # Hayır / İptal butonu
        self.no_btn = QPushButton("Hayır")
        self.no_btn.setObjectName("cancel_btn")
        self.no_btn.setMinimumHeight(34)
        self.no_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.no_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.no_btn)

        # Evet / Onayla butonu
        self.yes_btn = QPushButton("Evet")
        self.yes_btn.setMinimumHeight(34)
        self.yes_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Eğer tehlikeli bir işlemse onay butonunu danger_btn, değilse save_btn yapıyoruz
        if is_danger:
            self.yes_btn.setObjectName("danger_btn")
        else:
            self.yes_btn.setObjectName("save_btn")

        self.yes_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.yes_btn)

        self.layout.addLayout(btn_layout)

    @staticmethod
    def confirm(parent, title: str, message: str, is_danger: bool = False) -> bool:
        dialog = ModernConfirmDialog(title, message, is_danger, parent)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted


class NoteDetailDialog(BaseModernDialog):
    """Not ayrıntılarını gösteren ve düzenleme/Markdown önizleme desteği sunan diyalog kutusu."""
    
    def __init__(self, note_data: dict, parent=None):
        super().__init__(parent)
        self.db = parent.db if parent and hasattr(parent, 'db') else None
        if not self.db:
            from core.json_manager import JSONManager
            self.db = JSONManager()
            
        self.note_data = note_data
        self.is_edit_mode = False
        self.is_preview_markdown = True

        self.title_label.setText("Not Detayı")
        self.title_icon.setPixmap(qta.icon("mdi6.note-text-outline", color="#10B981").pixmap(18, 18))
        self.setMinimumSize(600, 500)

        # Üst kısımdaki butonlar (Düzenleme / Önizleme Toggle)
        self.top_buttons_layout = QHBoxLayout()
        
        # Markdown Önizleme / Düzenleme Toggle Butonu
        self.preview_toggle_btn = QPushButton("Önizleme Modu")
        self.preview_toggle_btn.setObjectName("secondary_btn")
        self.preview_toggle_btn.setFixedSize(120, 28)
        self.preview_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.preview_toggle_btn.clicked.connect(self._toggle_preview_mode)
        self.preview_toggle_btn.setVisible(False) # Sadece edit modundayken aktif olacak
        self.top_buttons_layout.addWidget(self.preview_toggle_btn)
        
        self.top_buttons_layout.addStretch()
        
        # Düzenle / Kaydet Butonu
        self.edit_save_btn = QPushButton("Düzenle")
        self.edit_save_btn.setObjectName("secondary_btn")
        self.edit_save_btn.setFixedSize(100, 28)
        self.edit_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.edit_save_btn.clicked.connect(self._on_edit_save_clicked)
        self.top_buttons_layout.addWidget(self.edit_save_btn)
        
        self.layout.addLayout(self.top_buttons_layout)

        # --- Görünüm Paneli (Detay Gösterimi) ---
        self.view_panel = QFrame()
        self.view_layout = QVBoxLayout(self.view_panel)
        self.view_layout.setContentsMargins(0, 0, 0, 0)
        self.view_layout.setSpacing(10)

        # Not Başlığı (Görünüm)
        self.lbl_title = QLabel(note_data.get("title", ""))
        self.lbl_title.setObjectName("page_title")
        self.lbl_title.setWordWrap(True)
        self.view_layout.addWidget(self.lbl_title)

        # Kategori & Tarih & Etiketler
        self.lbl_meta = QLabel()
        self.lbl_meta.setObjectName("page_subtitle")
        self._update_meta_label()
        self.view_layout.addWidget(self.lbl_meta)

        # Not İçeriği (Markdown Rendered/Düz Metin)
        self.txt_browser = QTextBrowser()
        self.txt_browser.setObjectName("txt_browser")
        # Markdown olarak ayarla
        self.txt_browser.setMarkdown(note_data.get("content", ""))
        self.view_layout.addWidget(self.txt_browser)

        self.layout.addWidget(self.view_panel, stretch=1)

        # --- Düzenleme Paneli (Gizli) ---
        self.edit_panel = QFrame()
        self.edit_layout = QVBoxLayout(self.edit_panel)
        self.edit_layout.setContentsMargins(0, 0, 0, 0)
        self.edit_layout.setSpacing(12)

        # Başlık Edit
        self.input_title = QLineEdit(note_data.get("title", ""))
        self.input_title.setObjectName("note_title_input")
        self.input_title.setPlaceholderText("Not başlığı...")
        self.input_title.setMinimumHeight(38)
        self.edit_layout.addWidget(self.input_title)

        # Kategori & Etiketler Yan Yana
        cat_tags_layout = QHBoxLayout()
        cat_tags_layout.setSpacing(10)

        # Kategori Seçici
        self.combo_category = QComboBox()
        self.combo_category.setObjectName("category_combo")
        self.combo_category.addItems(CATEGORIES)
        self.combo_category.setCurrentText(note_data.get("category", "Genel"))
        self.combo_category.setMinimumHeight(38)
        cat_tags_layout.addWidget(self.combo_category)

        # Etiket Girişi
        self.input_tags = QLineEdit(", ".join(note_data.get("tags", [])))
        self.input_tags.setObjectName("note_tags_input")
        self.input_tags.setPlaceholderText("Etiketler (virgülle ayırın: proje, fikir...)")
        self.input_tags.setMinimumHeight(38)
        cat_tags_layout.addWidget(self.input_tags, stretch=1)
        self.edit_layout.addLayout(cat_tags_layout)

        # Editör (QTextEdit)
        self.editor = QTextEdit()
        self.editor.setObjectName("note_editor")
        self.editor.setPlainText(note_data.get("content", ""))
        self.editor.setMinimumHeight(240)
        self.edit_layout.addWidget(self.editor)

        self.layout.addWidget(self.edit_panel, stretch=1)
        self.edit_panel.setVisible(False)

        # Geri Dönüş / Kapat Butonu (Alt Butonlar)
        self.bottom_buttons = QHBoxLayout()
        self.bottom_buttons.addStretch()
        
        self.close_dialog_btn = QPushButton("Kapat")
        self.close_dialog_btn.setObjectName("cancel_btn")
        self.close_dialog_btn.setMinimumHeight(36)
        self.close_dialog_btn.setMinimumWidth(100)
        self.close_dialog_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_dialog_btn.clicked.connect(self.accept)
        self.bottom_buttons.addWidget(self.close_dialog_btn)
        
        self.layout.addLayout(self.bottom_buttons)

    def _update_meta_label(self):
        """Kategori, Tarih ve Etiketleri içeren meta etiketini günceller."""
        cat = self.note_data.get("category", "Genel")
        date = self.note_data.get("date", "")
        tags = self.note_data.get("tags", [])
        
        formatted_date = format_date_tr(date)
        meta_text = f"📂 {cat}   •   📅 {formatted_date}"
        if tags:
            meta_text += f"   •   🏷️ {', '.join(tags)}"
        self.lbl_meta.setText(meta_text)

    def _toggle_preview_mode(self):
        """Editör modundayken Markdown önizlemesi ve kod görünümü arasında geçiş yapar."""
        if self.is_preview_markdown:
            # Düzenleme moduna geç (ham metin / markdown kodları)
            self.editor.setVisible(True)
            self.txt_browser.setVisible(False)
            self.preview_toggle_btn.setText("Önizleme Modu")
            self.is_preview_markdown = False
        else:
            # Önizleme moduna geç (render edilmiş Markdown)
            markdown_content = self.editor.toPlainText()
            self.txt_browser.setMarkdown(markdown_content)
            self.editor.setVisible(False)
            self.txt_browser.setVisible(True)
            self.preview_toggle_btn.setText("Düzenleme Modu")
            self.is_preview_markdown = True

    def _on_edit_save_clicked(self):
        """Düzenle/Kaydet butonu eylemini yönetir."""
        if not self.is_edit_mode:
            # Düzenleme Moduna Giriş
            self.is_edit_mode = True
            self.edit_save_btn.setText("Kaydet")
            self.edit_save_btn.setObjectName("save_btn")
            self.edit_save_btn.style().unpolish(self.edit_save_btn)
            self.edit_save_btn.style().polish(self.edit_save_btn)
            
            # Panelleri değiştir
            self.view_panel.setVisible(False)
            self.edit_panel.setVisible(True)
            self.preview_toggle_btn.setVisible(True)
            self.preview_toggle_btn.setText("Önizleme Modu")
            
            # Form alanlarını güncelle
            self.input_title.setText(self.note_data.get("title", ""))
            self.combo_category.setCurrentText(self.note_data.get("category", "Genel"))
            self.input_tags.setText(", ".join(self.note_data.get("tags", [])))
            self.editor.setPlainText(self.note_data.get("content", ""))
            
            self.is_preview_markdown = False
            self.editor.setVisible(True)
            self.txt_browser.setVisible(False)
            self.close_dialog_btn.setText("İptal")
        else:
            # Değişiklikleri Kaydetme
            title = self.input_title.text().strip()
            content = self.editor.toPlainText().strip()
            category = self.combo_category.currentText()
            tags_raw = self.input_tags.text().strip()
            
            if not title or not content:
                # Başlık veya içerik boş olamaz
                return

            # Etiket listesini işle
            tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]

            # Veritabanında güncelle
            note_id = self.note_data["id"]
            if self.db.update_note(note_id, title, content, category, tags):
                # Başarılı güncelleme sonrası nesne verisini yenile
                self.note_data["title"] = title
                self.note_data["content"] = content
                self.note_data["category"] = category
                self.note_data["tags"] = tags
                
                # Arayüzü güncelle
                self.lbl_title.setText(title)
                self.txt_browser.setMarkdown(content)
                self._update_meta_label()
                from ui.toast import ToastManager
                ToastManager.show(self, "Başarılı", "Notunuz başarıyla güncellendi.", "success")
            else:
                from ui.toast import ToastManager
                ToastManager.show(self, "Hata", "Not güncellenirken bir sorun oluştu.", "error")

            # Görünüm Moduna Geri Dönüş
            self.is_edit_mode = False
            self.edit_save_btn.setText("Düzenle")
            self.edit_save_btn.setObjectName("secondary_btn")
            self.edit_save_btn.style().unpolish(self.edit_save_btn)
            self.edit_save_btn.style().polish(self.edit_save_btn)
            
            self.view_panel.setVisible(True)
            self.edit_panel.setVisible(False)
            self.preview_toggle_btn.setVisible(False)
            self.close_dialog_btn.setText("Kapat")
