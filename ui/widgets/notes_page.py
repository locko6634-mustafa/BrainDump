# -*- coding: utf-8 -*-
"""
Notlarım Sayfası Widget'ı
Tüm notları grid düzeninde gösteren sayfa: arama, filtreleme ve not kartları.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QGridLayout,
    QScrollArea, QMenu, QComboBox
)
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal
)
from PyQt6.QtGui import QResizeEvent
import qtawesome as qta
from core.json_manager import JSONManager
from core.utils import CATEGORIES, format_date_tr
from ui.animations import HoverCard, StaggerAnimationHelper


class NoteCard(HoverCard):
    """Tek bir not kartı bileşeni."""
    delete_clicked = pyqtSignal(str)
    pin_clicked = pyqtSignal(str, bool)
    clicked = pyqtSignal(str)

    def __init__(self, note_id: str, title: str, preview: str, date: str, category: str, is_pinned: bool = False, parent=None):
        super().__init__(parent)
        self.note_id = note_id
        self.is_pinned = is_pinned
        self.setObjectName("hover_card")
        self.setMinimumHeight(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        # Başlık ve butonlar satırı
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        # Not başlığı
        title_label = QLabel(title)
        title_label.setObjectName("note_card_title")
        title_row.addWidget(title_label, stretch=1)

        # Sabitleme (Pin) butonu
        self.pin_btn = QPushButton()
        self.pin_btn.setObjectName("pin_btn")
        self.pin_btn.setFixedSize(24, 24)
        self.pin_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pin_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
        self.pin_btn.clicked.connect(self._on_pin_clicked)
        self.update_pin_icon()
        title_row.addWidget(self.pin_btn)

        # Sil butonu
        self.delete_btn = QPushButton()
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.setIcon(qta.icon("mdi6.trash-can-outline", color="#FF5252"))
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet("QPushButton { background: transparent; border: none; }")
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
        layout.addWidget(preview_label)

        layout.addStretch()

        # Alt kısım: tarih + kategori etiketi
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        date_label = QLabel(date)
        date_label.setObjectName("note_card_date")
        bottom_row.addWidget(date_label)

        bottom_row.addStretch()

        # Kategori etiketi
        category_tag = QLabel(category)
        category_tag.setObjectName("category_tag")
        bottom_row.addWidget(category_tag)

        layout.addLayout(bottom_row)

    def update_pin_icon(self):
        """Pin ikonunu durumuna göre günceller."""
        if self.is_pinned:
            self.pin_btn.setIcon(qta.icon("mdi6.pin", color="#10B981"))
        else:
            self.pin_btn.setIcon(qta.icon("mdi6.pin-outline", color="#71717a"))

    def _on_pin_clicked(self):
        """Sabitleme butonu tıklandığında durumu tersine çevirip sinyal yayar."""
        self.is_pinned = not self.is_pinned
        self.update_pin_icon()
        self.pin_clicked.emit(self.note_id, self.is_pinned)

    def _on_delete_clicked(self):
        """Silme butonuna tıklandığında silme sinyalini tetikler."""
        self.delete_clicked.emit(self.note_id)

    def mousePressEvent(self, event):
        """Kart tıklandığında, butonlara tıklanmadıysa clicked sinyalini yayar."""
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            # Silme veya Pin butonuna tıklanmadıysa detay aç
            if not self.delete_btn.geometry().contains(pos) and not self.pin_btn.geometry().contains(pos):
                self.clicked.emit(self.note_id)
        super().mousePressEvent(event)


class NotesPage(QWidget):
    """Notlarım sayfası — tüm notları grid görünümde listeler."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("notes_page")
        self.db = JSONManager()
        self.selected_category = "Hepsi"
        self.current_cols = 3 # Varsayılan sütun sayısı

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
        title_row.addWidget(page_title)
        title_row.addStretch()
        self.content_layout.addLayout(title_row)

        # --- Üst bar: Arama + Sıralama + Filtre ---
        search_bar = QHBoxLayout()
        search_bar.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setObjectName("search_input")
        self.search_input.setPlaceholderText("Notlarda ara...")
        self.search_input.setMinimumHeight(40)
        search_bar.addWidget(self.search_input, stretch=1)

        # Sıralama Kutusu (Faz 3)
        self.sort_combo = QComboBox()
        self.sort_combo.setObjectName("sort_combo")
        self.sort_combo.addItems(["En Yeni", "En Eski", "A-Z Başlık", "Z-A Başlık", "Kategori"])
        self.sort_combo.setMinimumHeight(40)
        self.sort_combo.setMinimumWidth(110)
        self.sort_combo.currentIndexChanged.connect(self.load_notes)
        search_bar.addWidget(self.sort_combo)

        # Filtre butonu
        filter_btn = QPushButton()
        filter_btn.setObjectName("filter_btn")
        filter_btn.setIcon(qta.icon("mdi6.filter-variant", color="#a0a0b8"))
        filter_btn.setMinimumSize(40, 40)
        filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Filtre menüsü
        self.filter_menu = QMenu(self)
        self.reload_categories()
        
        filter_btn.setMenu(self.filter_menu)
        search_bar.addWidget(filter_btn)

        self.content_layout.addLayout(search_bar)

        # --- Not kartları grid'i ---
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(16)
        self.content_layout.addLayout(self.grid_layout)

        # --- Bilgi satırı ---
        self.info_label = QLabel("0 not bulundu")
        self.info_label.setObjectName("notes_count")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(self.info_label)

        self.content_layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # Arama kutusu değiştiğinde tetikleme
        self.search_input.textChanged.connect(self.load_notes)

        # Notları ilk defa yükle
        self.load_notes()

    def reload_categories(self):
        """Kategori filtre menüsünü ve mevcut seçim durumunu günceller."""
        self.filter_menu.clear()
        categories = ["Hepsi"] + CATEGORIES
        for cat in categories:
            action = self.filter_menu.addAction(cat)
            action.triggered.connect(lambda checked, c=cat: self._on_filter_changed(c))
        
        # Seçili kategori silindiyse "Hepsi"ye sıfırla
        if self.selected_category != "Hepsi" and self.selected_category not in CATEGORIES:
            self.selected_category = "Hepsi"
            self.load_notes()

    def _clear_grid(self):
        """Grid'deki tüm kartları ve düzen elemanlarını temizler."""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_notes(self):
        """Notları JSON dosyasından yükler, arama, filtre ve sıralamaya göre listeler."""
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
                tags_match = any(search_text in tag.lower() for tag in note.get("tags", []))
                if not (title_match or content_match or category_match or tags_match):
                    continue
            
            filtered_notes.append(note)

        # --- Sıralama Mantığı (Faz 3) ---
        sort_choice = self.sort_combo.currentText()
        
        def sort_key(note):
            note_date = note.get("date", "")
            note_title = note.get("title", "").lower()
            note_category = note.get("category", "").lower()
            
            if sort_choice in ["En Yeni", "En Eski"]:
                return note_date
            elif sort_choice in ["A-Z Başlık", "Z-A Başlık"]:
                return note_title
            elif sort_choice == "Kategori":
                return note_category
            return note_date

        reverse_sort = (sort_choice == "En Yeni" or sort_choice == "Z-A Başlık")
        filtered_notes.sort(key=sort_key, reverse=reverse_sort)
        
        # Sabitlenen (Pinned) notları stabil olarak en tepeye uçur
        filtered_notes.sort(key=lambda x: not x.get("is_pinned", False))

        # Kartları oluştur ve grid'e ekle
        cards = []
        for i, note in enumerate(filtered_notes):
            card = NoteCard(
                note_id=note["id"],
                title=note["title"],
                preview=note["content"],
                date=format_date_tr(note["date"]),
                category=note["category"],
                is_pinned=note.get("is_pinned", False)
            )
            card.delete_clicked.connect(self._on_delete_note)
            card.pin_clicked.connect(self._on_pin_clicked)
            card.clicked.connect(self._on_note_clicked)
            
            row = i // self.current_cols
            col = i % self.current_cols
            self.grid_layout.addWidget(card, row, col)
            cards.append(card)

        # Bilgi satırını güncelle
        self.info_label.setText(f"{len(filtered_notes)} not bulundu")

        # Staggered entry animasyonunu tetikle
        if cards:
            QTimer.singleShot(30, lambda: StaggerAnimationHelper.stagger_widgets(cards))

    def _on_pin_clicked(self, note_id, is_pinned):
        """Notun pinlenme durumu değiştiğinde kaydeder ve yeniden yükler."""
        if self.db.update_note_pin(note_id, is_pinned):
            self.load_notes()
            from ui.toast import ToastManager
            msg = "Not en üste sabitlendi." if is_pinned else "Notun sabitlemesi kaldırıldı."
            ToastManager.show(self, "Başarılı", msg, "success")

    def resizeEvent(self, event: QResizeEvent):
        """Pencere yeniden boyutlandırıldığında responsive grid yapısını ayarlar."""
        super().resizeEvent(event)
        width = self.width()
        
        # Genişliğe göre sütun sayısını hesapla
        if width < 550:
            new_cols = 1
        elif width < 850:
            new_cols = 2
        elif width < 1150:
            new_cols = 3
        else:
            new_cols = 4
            
        if self.current_cols != new_cols:
            self.current_cols = new_cols
            self.rearrange_grid()

    def rearrange_grid(self):
        """Mevcut kartları yenilemeden grid üzerinde yeniden dağıtır (Performanslı Reflow)."""
        widgets = []
        for i in range(self.grid_layout.count()):
            item = self.grid_layout.itemAt(i)
            if item and item.widget():
                widgets.append(item.widget())
                
        # Widget'ları grid'den sök
        for w in widgets:
            self.grid_layout.removeWidget(w)
            
        # Yeni sütun yapısıyla tekrar yerleştir
        for idx, w in enumerate(widgets):
            row = idx // self.current_cols
            col = idx % self.current_cols
            self.grid_layout.addWidget(w, row, col)

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
                from ui.toast import ToastManager
                ToastManager.show(self, "Başarılı", "Not başarıyla silindi.", "success")

    def _on_note_clicked(self, note_id):
        """Bir not kartına tıklandığında detay diyalogunu açar."""
        notes = self.db.get_all_notes()
        note = next((n for n in notes if n["id"] == note_id), None)
        if note:
            from ui.widgets.dialogs import NoteDetailDialog
            dialog = NoteDetailDialog(note, self)
            dialog.exec()
            self.load_notes()  # Değişiklik yapılmış olabileceği için listeyi yenile
