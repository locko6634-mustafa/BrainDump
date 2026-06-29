"""
BrainDump — Daraltılabilir Sidebar Widget
Tam metin ↔ ikon modu (~60px ↔ ~220px) geçişi destekler.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel,
    QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    pyqtSignal, pyqtProperty, QSize
)
from PyQt6.QtGui import QFont
import qtawesome as qta


class SidebarButton(QPushButton):
    """Sidebar menü öğesi butonu — ikon + metin gösterir."""

    def __init__(self, icon_name: str, text: str, parent=None):
        super().__init__(parent)
        self._icon_name = icon_name
        self._text = text
        self._is_expanded = True

        self.setObjectName("sidebar_btn")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(False)

        # İkon ve metin ayarla
        self._update_display()

    def _update_display(self):
        """Butonun ikon ve metin görünümünü günceller."""
        icon = qta.icon(self._icon_name, color="#a0a0b8")
        self.setIcon(icon)
        self.setIconSize(QSize(22, 22))

        if self._is_expanded:
            self.setText(f"  {self._text}")
        else:
            self.setText("")

    def set_expanded(self, expanded: bool):
        """Sidebar genişletme/daraltma durumunu ayarlar."""
        self._is_expanded = expanded
        self._update_display()

    def set_active(self, active: bool):
        """Aktif menü öğesi stilini uygular."""
        self.setProperty("active", active)
        # Aktif ikon rengi: yeşil aksan
        color = "#10B981" if active else "#a0a0b8"
        icon = qta.icon(self._icon_name, color=color)
        self.setIcon(icon)
        # Stili yeniden uygula
        self.style().unpolish(self)
        self.style().polish(self)


class Sidebar(QWidget):
    """
    Daraltılabilir (collapsible) sidebar navigasyon widget'ı.
    Genişletilmiş (~220px) ve daraltılmış (~60px) modları destekler.
    """

    # Sayfa değişikliği sinyali (index gönderir)
    page_changed = pyqtSignal(int)

    EXPANDED_WIDTH = 220
    COLLAPSED_WIDTH = 60
    ANIMATION_DURATION = 300

    # Menü öğeleri: (ikon_adı, metin)
    MENU_ITEMS = [
        ("mdi6.view-dashboard", "Dashboard"),
        ("mdi6.note-plus-outline", "Yeni Not"),
        ("mdi6.notebook-outline", "Notlar"),
        ("mdi6.target", "Günlük Hedefler"),
        ("mdi6.chart-bar", "İstatistikler"),
        ("mdi6.cog-outline", "Ayarlar"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self._is_expanded = True
        self._current_index = 0
        self._buttons: list[SidebarButton] = []

        # Sabit genişlik ayarı
        self.setFixedWidth(self.EXPANDED_WIDTH)
        self.setMinimumHeight(400)

        # Genişlik animasyonu
        self._width_anim = QPropertyAnimation(self, b"fixedWidth")
        self._width_anim.setDuration(self.ANIMATION_DURATION)
        self._width_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self._setup_ui()

    def _setup_ui(self):
        """Sidebar arayüzünü oluşturur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 12, 8, 16)
        layout.setSpacing(2)

        # --- Üst Kısım: Toggle Butonu + Brand ---
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)

        # Toggle butonu
        self._toggle_btn = QPushButton()
        self._toggle_btn.setObjectName("sidebar_toggle_btn")
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setIcon(qta.icon("mdi6.menu", color="#a0a0b8"))
        self._toggle_btn.setIconSize(QSize(24, 24))
        self._toggle_btn.setFixedHeight(44)
        self._toggle_btn.clicked.connect(self.toggle)
        header_layout.addWidget(self._toggle_btn)

        # Brand Label
        self._brand_label = QLabel("BrainDump")
        self._brand_label.setObjectName("sidebar_brand")
        self._brand_label.setFont(QFont("Inter", 16, QFont.Weight.Bold))
        header_layout.addWidget(self._brand_label)

        layout.addLayout(header_layout)
        layout.addSpacing(16)

        # --- Menü Öğeleri ---
        for index, (icon_name, text) in enumerate(self.MENU_ITEMS):
            btn = SidebarButton(icon_name, text, self)
            btn.clicked.connect(lambda checked, idx=index: self._on_menu_click(idx))
            self._buttons.append(btn)
            layout.addWidget(btn)

        # Boşluk (alt kısmı aşağı iter)
        layout.addItem(QSpacerItem(
            20, 40,
            QSizePolicy.Policy.Minimum,
            QSizePolicy.Policy.Expanding
        ))

        # İlk butonu aktif yap
        self._update_active_button(0)

    def _on_menu_click(self, index: int):
        """Menü öğesine tıklandığında çağrılır."""
        if index != self._current_index:
            self._current_index = index
            self._update_active_button(index)
            self.page_changed.emit(index)

    def _update_active_button(self, active_index: int):
        """Aktif menü öğesini günceller."""
        for i, btn in enumerate(self._buttons):
            btn.set_active(i == active_index)

    def toggle(self):
        """Sidebar'ı daralt veya genişlet."""
        if self._is_expanded:
            self._collapse()
        else:
            self._expand()

    def _collapse(self):
        """Sidebar'ı daralt (ikon modu)."""
        self._is_expanded = False
        self._width_anim.setStartValue(self.EXPANDED_WIDTH)
        self._width_anim.setEndValue(self.COLLAPSED_WIDTH)
        self._width_anim.start()

        # Metinleri gizle
        self._brand_label.hide()
        for btn in self._buttons:
            btn.set_expanded(False)

        # Toggle ikon değiştir
        self._toggle_btn.setIcon(qta.icon("mdi6.menu-open", color="#a0a0b8"))

    def _expand(self):
        """Sidebar'ı genişlet (tam metin modu)."""
        self._is_expanded = True
        self._width_anim.setStartValue(self.COLLAPSED_WIDTH)
        self._width_anim.setEndValue(self.EXPANDED_WIDTH)
        self._width_anim.start()

        # Metinleri göster
        self._brand_label.show()
        for btn in self._buttons:
            btn.set_expanded(True)

        # Toggle ikon değiştir
        self._toggle_btn.setIcon(qta.icon("mdi6.menu", color="#a0a0b8"))

    # --- fixedWidth property (QPropertyAnimation için) ---
    def get_fixed_width(self):
        return self.width()

    def set_fixed_width(self, width: int):
        self.setFixedWidth(width)

    fixedWidth = pyqtProperty(int, get_fixed_width, set_fixed_width)

    def set_current_index(self, index: int):
        """Dışarıdan aktif menü öğesini ve indeksini günceller."""
        if 0 <= index < len(self._buttons):
            self._current_index = index
            self._update_active_button(index)
