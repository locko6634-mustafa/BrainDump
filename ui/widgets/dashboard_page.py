# -*- coding: utf-8 -*-
"""
Dashboard Sayfası Widget'ı
Ana sayfa: karşılama mesajı, hızlı eylem kartları ve son aktiviteler.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal
)
from PyQt6.QtGui import QColor
from datetime import datetime
import qtawesome as qta
from core.json_manager import JSONManager
from ui.animations import HoverCard, StaggerAnimationHelper


class ActionCard(HoverCard):
    """Hızlı eylem kartı bileşeni."""
    clicked = pyqtSignal()

    def __init__(self, icon_name: str, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("hover_card") # HoverCard'ın QSS eşleşmesi için

        # Kart düzeni
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 24, 20, 24)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # İkon
        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon(icon_name, color="#10B981").pixmap(40, 40)
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Başlık
        title_label = QLabel(title)
        title_label.setObjectName("card_title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 15px; font-weight: 600; color: #e8e8e8; background: transparent;")
        layout.addWidget(title_label)

        # Açıklama
        desc_label = QLabel(description)
        desc_label.setObjectName("card_description")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setStyleSheet("font-size: 12px; color: #a0a0b8; background: transparent;")
        layout.addWidget(desc_label)

    def mousePressEvent(self, event):
        """Kart tıklandığında sinyal yayar."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class DashboardPage(QWidget):
    """Ana panel sayfası — karşılama, hızlı eylemler ve son aktiviteler."""
    page_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dashboard_page")
        self.db = JSONManager()

        # --- Ana düzen ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)


        # Scroll alanı
        scroll = QScrollArea()
        scroll.setObjectName("dashboard_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll içeriği
        content = QWidget()
        content.setObjectName("dashboard_content")
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(32, 32, 32, 32)
        self._content_layout.setSpacing(24)

        # --- Karşılama bölümü ---
        self.welcome_title = QLabel("Merhaba! 👋")
        self.welcome_title.setObjectName("welcome_title")
        self.welcome_title.setStyleSheet(
            "font-size: 28px; font-weight: 700; color: #e8e8e8; margin-bottom: 0px;"
        )
        self._content_layout.addWidget(self.welcome_title)

        self.welcome_subtitle = QLabel("Bugün harika şeyler başarabilirsin.")
        self.welcome_subtitle.setObjectName("welcome_subtitle")
        self.welcome_subtitle.setStyleSheet(
            "font-size: 14px; color: #a0a0b8; margin-top: 0px; margin-bottom: 8px;"
        )
        self._content_layout.addWidget(self.welcome_subtitle)

        # --- Hızlı eylem kartları ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        # Kart verileri
        card_data = [
            ("mdi6.note-plus-outline", "Yeni Not Oluştur", "Hızlıca bir not al"),
            ("mdi6.target", "Bugünkü Hedefler", "Günlük hedeflerini belirle"),
            ("mdi6.chart-bar", "İstatistiklere Bak", "İlerlemeni takip et"),
        ]

        self._action_cards = []
        target_indices = [1, 3, 4] # Yeni Not (1), Bugünkü Hedefler (3), İstatistikler (4)
        for idx, (icon_name, title, desc) in enumerate(card_data):
            card = ActionCard(icon_name, title, desc)
            card.setMinimumHeight(140)
            card.clicked.connect(lambda t=target_indices[idx]: self.page_requested.emit(t))
            cards_layout.addWidget(card, stretch=1)
            self._action_cards.append(card)

        self._content_layout.addLayout(cards_layout)

        # --- Son Aktiviteler bölümü ---
        self.activity_section = QFrame()
        self.activity_section.setObjectName("activity_section")
        self.activity_section.setStyleSheet(
            "QFrame#activity_section { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 12px; padding: 8px; }"
        )
        activity_layout = QVBoxLayout(self.activity_section)
        activity_layout.setContentsMargins(20, 16, 20, 16)
        activity_layout.setSpacing(12)

        activity_title = QLabel("Son Aktiviteler")
        activity_title.setObjectName("section_title")
        activity_title.setStyleSheet(
            "font-size: 16px; font-weight: 600; color: #e8e8e8;"
        )
        activity_layout.addWidget(activity_title)

        # Aktivitelerin listeleneceği layout
        self.activity_list_layout = QVBoxLayout()
        self.activity_list_layout.setSpacing(8)
        self.activity_list_layout.setContentsMargins(0, 0, 0, 0)
        activity_layout.addLayout(self.activity_list_layout)

        self._content_layout.addWidget(self.activity_section)
        self._content_layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # Aktivite verilerini ilk kez yükle
        self.load_dashboard()

    def load_dashboard(self):
        """Dashboard panelindeki dinamik verileri yeniler."""
        self.load_activities()

    def _parse_date(self, date_str):
        """Türkçe ay içeren not tarihlerini datetime nesnesine dönüştürür."""
        turkish_months = {
            "Oca": "Jan", "Şub": "Feb", "Mar": "Mar", "Nis": "Apr",
            "May": "May", "Haz": "Jun", "Tem": "Jul", "Ağu": "Aug",
            "Eyl": "Sep", "Eki": "Oct", "Kas": "Nov", "Ara": "Dec"
        }
        try:
            for tr, eng in turkish_months.items():
                date_str = date_str.replace(tr, eng)
            return datetime.strptime(date_str, "%d %b %Y")
        except Exception:
            return None

    def load_activities(self):
        """Not ve hedef verilerinden karma son aktiviteler listesi oluşturup yükler."""
        # Eski widget'ları temizle
        while self.activity_list_layout.count():
            item = self.activity_list_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        notes = self.db.get_all_notes()
        goals = self.db.get_all_goals()

        raw_activities = []

        # 1. Notlar (Eklenen Notlar)
        for note in notes:
            note_date = self._parse_date(note.get("date", ""))
            raw_activities.append({
                "text": f"📝  Yeni not eklendi: {note['title']}",
                "info": note.get("date", "Bilinmeyen Tarih"),
                "timestamp": note_date or datetime.min
            })

        # 2. Tamamlanan Hedefler
        for goal in goals:
            if goal.get("completed", False):
                raw_activities.append({
                    "text": f"✅  '{goal['text']}' hedefi tamamlandı",
                    "info": "Bugün",
                    "timestamp": datetime.now()
                })

        # Zaman damgasına göre sırala (en yeni en üstte)
        sorted_activities = sorted(raw_activities, key=lambda x: x["timestamp"], reverse=True)

        # En fazla 4 aktivite göster
        display_activities = sorted_activities[:4]

        if not display_activities:
            empty_row = QLabel("Henüz bir aktivite gerçekleşmedi.")
            empty_row.setObjectName("activity_row_empty")
            empty_row.setStyleSheet("font-size: 13px; color: #6a6a8a; padding: 6px 0px; font-style: italic;")
            self.activity_list_layout.addWidget(empty_row)
        else:
            for act in display_activities:
                row = QLabel(f"{act['text']} — {act['info']}")
                row.setObjectName("activity_row")
                row.setStyleSheet(
                    "font-size: 13px; color: #a0a0b8; padding: 6px 0px;"
                    " border-bottom: 1px solid #2a2a4a;"
                )
                self.activity_list_layout.addWidget(row)

    def showEvent(self, event):
        """Dashboard sayfası gösterildiğinde staggered entry animasyonunu çalıştırır."""
        super().showEvent(event)
        widgets = [
            self.welcome_title,
            self.welcome_subtitle,
        ] + self._action_cards + [self.activity_section]
        QTimer.singleShot(50, lambda: StaggerAnimationHelper.stagger_widgets(widgets))

