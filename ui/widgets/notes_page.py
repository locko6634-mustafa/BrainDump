# -*- coding: utf-8 -*-
"""
Notlarım Sayfası Widget'ı
Tüm notları grid düzeninde gösteren sayfa: arama, filtreleme ve not kartları.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGridLayout,
    QScrollArea, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QMenu
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
)
from PyQt6.QtGui import QColor
import qtawesome as qta
from core.json_manager import JSONManager
from ui.animations import HoverCard, StaggerAnimationHelper, TactileButton


class NoteCard(HoverCard):
    """Tek bir not kartı bileşeni."""
    delete_clicked = pyqtSignal(str)
    clicked = pyqtSignal(str)

    def __init__(self, note_id: str, title: str, preview: str, date: str, category: str, parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self.setObjectName("hover_card")
        self.setMinimumHeight(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Başlık ve sil butonu satırı
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        # Not başlığı
        title_label = QLabel(title)
        title_label.setObjectName("note_card_title")
        title_label.setStyleSheet(
            "font-size: 15px; font-weight: 700; color: #e8e8e8; background: transparent;"
        )
        title_row.addWidget(title_label, stretch=1)

        # Sil butonu
        self.delete_btn = QPushButton()
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.setIcon(qta.icon("mdi6.trash-can-outline", color="#FF5252"))
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; border-radius: 4px; }"
            "QPushButton:hover { background: rgba(255, 82, 82, 0.15); }"
        )
        self.delete_btn.clicked.connect(self._on_delete_clicked)
        title_row.addWidget(self.delete_btn)

        layout.addLayout(title_row)

        # Önizleme metni (uzunsa kırpıp 3 nokta koyalım)
        max_preview_len = 75
        if len(preview) > max_preview_len:
            preview = preview[:max_preview_len] + "..."
        preview_label = QLabel(preview)
        preview_label.setObjectName("note_card_preview")
        preview_label.setWordWrap(True)
        preview_label.setStyleSheet("font-size: 12px; color: #a0a0b8; background: transparent;")
        layout.addWidget(preview_label)

        layout.addStretch()

        # Alt kısım: tarih + kategori etiketi
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        date_label = QLabel(date)
        date_label.setStyleSheet("font-size: 11px; color: #6a6a8a; background: transparent;")
        bottom_row.addWidget(date_label)

        bottom_row.addStretch()

        # Kategori etiketi
        category_tag = QLabel(category)
        category_tag.setObjectName("category_tag")
        category_tag.setStyleSheet(
            "font-size: 10px; color: #10B981; background: rgba(16,185,129,0.12);"
            " border-radius: 4px; padding: 2px 8px; font-weight: 600;"
        )
        bottom_row.addWidget(category_tag)

        layout.addLayout(bottom_row)

    def _on_delete_clicked(self):
        """Silme butonuna tıklandığında silme sinyalini tetikler."""
        self.delete_clicked.emit(self.note_id)

    def mousePressEvent(self, event):
        """Kart tıklandığında, silme butonuna tıklanmadıysa clicked sinyalini yayar."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Fare silme butonunun üzerinde değilse tıklamayı kabul et
            pos = event.position().toPoint()
            if not self.delete_btn.geometry().contains(pos):
                self.clicked.emit(self.note_id)
        super().mousePressEvent(event)


class NotesPage(QWidget):
    """Notlarım sayfası — tüm notları grid görünümde listeler."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("notes_page")
        self.db = JSONManager()
        self.selected_category = "Hepsi"

        # --- Ana düzen ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setObjectName("notes_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll içeriği
        content = QWidget()
        content.setObjectName("notes_content")
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(32, 32, 32, 32)
        self.content_layout.setSpacing(20)

        # --- Sayfa başlığı ---
        title_row = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(
            qta.icon("mdi6.notebook-multiple", color="#10B981").pixmap(28, 28)
        )
        title_row.addWidget(title_icon)

        page_title = QLabel("Notlarım")
        page_title.setObjectName("page_title")
        page_title.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #e8e8e8;"
        )
        title_row.addWidget(page_title)
        title_row.addStretch()
        self.content_layout.addLayout(title_row)

        # --- Üst bar: Arama + Filtre ---
        search_bar = QHBoxLayout()
        search_bar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Notlarda ara...")
        self.search_input.setMinimumHeight(40)
        self.search_input.setStyleSheet(
            "QLineEdit { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 8px; padding: 8px 12px; color: #f4f4f5;"
            " font-size: 14px; }"
            "QLineEdit:focus { border-color: #10B981; }"
        )
        search_bar.addWidget(self.search_input, stretch=1)

        # Filtre butonu
        filter_btn = QPushButton()
        filter_btn.setObjectName("filter_btn")
        filter_btn.setIcon(qta.icon("mdi6.filter-variant", color="#a0a0b8"))
        filter_btn.setMinimumSize(40, 40)
        filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        filter_btn.setStyleSheet(
            "QPushButton { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 8px; }"
            "QPushButton:hover { border-color: #10B981; }"
        )
        
        # Filtre menüsü
        self.filter_menu = QMenu(self)
        categories = ["Hepsi", "Genel", "İş", "Kişisel", "Proje", "Fikir"]
        for cat in categories:
            action = self.filter_menu.addAction(cat)
            action.triggered.connect(lambda checked, c=cat: self._on_filter_changed(c))
        
        filter_btn.setMenu(self.filter_menu)
        search_bar.addWidget(filter_btn)

        self.content_layout.addLayout(search_bar)

        # --- Not kartları grid'i (3 sütun) ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)
        self.content_layout.addLayout(self.grid_layout)

        # --- Bilgi satırı ---
        self.info_label = QLabel("0 not bulundu")
        self.info_label.setObjectName("notes_count")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(
            "font-size: 12px; color: #6a6a8a; margin-top: 16px;"
        )
        self.content_layout.addWidget(self.info_label)

        self.content_layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # Arama kutusu değiştiğinde tetikleme
        self.search_input.textChanged.connect(self.load_notes)

        # Notları ilk defa yükle
        self.load_notes()

    def _clear_grid(self):
        """Grid'deki tüm kartları ve düzen elemanlarını temizler."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_notes(self):
        """Notları JSON dosyasından yükler, arama ve filtreye göre süzüp listeler."""
        self._clear_grid()
        notes = self.db.get_all_notes()
        
        search_text = self.search_input.text().strip().lower()
        
        filtered_notes = []
        for note in notes:
            # Kategori Filtresi
            if self.selected_category != "Hepsi" and note.get("category") != self.selected_category:
                continue
            
            # Arama Filtresi
            if search_text:
                title_match = search_text in note.get("title", "").lower()
                content_match = search_text in note.get("content", "").lower()
                category_match = search_text in note.get("category", "").lower()
                # Etiket araması
                tags_match = any(search_text in tag.lower() for tag in note.get("tags", []))
                if not (title_match or content_match or category_match or tags_match):
                    continue
            
            filtered_notes.append(note)

        # Kartları oluştur ve grid'e ekle (3 sütun)
        cards = []
        for i, note in enumerate(filtered_notes):
            card = NoteCard(
                note_id=note["id"],
                title=note["title"],
                preview=note["content"],
                date=note["date"],
                category=note["category"]
            )
            card.delete_clicked.connect(self._on_delete_note)
            card.clicked.connect(self._on_note_clicked)
            
            row = i // 3
            col = i % 3
            self.grid_layout.addWidget(card, row, col)
            cards.append(card)

        # Bilgi satırını güncelle
        self.info_label.setText(f"{len(filtered_notes)} not bulundu")

        # Staggered entry animasyonunu tetikle
        if cards:
            QTimer.singleShot(30, lambda: StaggerAnimationHelper.stagger_widgets(cards))

    def _on_filter_changed(self, category):
        """Filtre değiştiğinde listeyi günceller."""
        self.selected_category = category
        self.load_notes()

    def _on_delete_note(self, note_id):
        """Bir not silinmek istendiğinde kullanıcıdan onay alır ve siler."""
        from ui.widgets.dialogs import ModernConfirmDialog
        ok = ModernConfirmDialog.confirm(
            self,
            "Notu Sil",
            "Bu notu kalıcı olarak silmek istediğinizden emin misiniz?",
            is_danger=True
        )

        if ok:
            if self.db.delete_note(note_id):
                self.load_notes()

    def _on_note_clicked(self, note_id):
        """Bir not kartına tıklandığında detay diyalogunu açar."""
        notes = self.db.get_all_notes()
        note = next((n for n in notes if n["id"] == note_id), None)
        if note:
            from ui.widgets.dialogs import NoteDetailDialog
            dialog = NoteDetailDialog(note, self)
            dialog.exec()
            self.load_notes()  # Değişiklik yapılmış olabileceği için listeyi yenile

