# -*- coding: utf-8 -*-
"""
Günlük Hedefler Sayfası Widget'ı
Hedef takibi: ilerleme çubuğu, checkbox'lu hedefler ve motivasyon metni.
"""

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QProgressBar, QPushButton, QFrame,
    QScrollArea, QGraphicsOpacityEffect, QComboBox,
    QSpinBox, QButtonGroup, QLineEdit
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QTimer
)
import qtawesome as qta
from core.json_manager import JSONManager
from ui.animations import StaggerAnimationHelper, TactileButton
from ui.widgets.dialogs import BaseModernDialog


class GoalItem(QFrame):
    """Tek bir hedef satırı bileşeni."""
    status_changed = pyqtSignal(str, bool)
    progress_changed = pyqtSignal(str, int, bool)
    delete_clicked = pyqtSignal(str)

    def __init__(self, goal_id: str, text: str, is_completed: bool = False, period: str = "daily", progress: int = 0, total_progress: int = 1, parent=None):
        super().__init__(parent)
        self.goal_id = goal_id
        self.period = period
        self.progress = progress
        self.total_progress = total_progress
        self.is_completed = is_completed
        
        self.setObjectName("goal_item")
        self.setMinimumHeight(52)
        self.setStyleSheet(
            "QFrame#goal_item { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 10px; }"
        )

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(16, 8, 16, 8)
        self.main_layout.setSpacing(12)

        # 1. Onay/İlerleme Tetikleyicileri
        if self.total_progress > 1:
            # Sayaçlı Hedef Arayüzü
            self.counter_widget = QWidget()
            counter_layout = QHBoxLayout(self.counter_widget)
            counter_layout.setContentsMargins(0, 0, 0, 0)
            counter_layout.setSpacing(6)

            self.minus_btn = QPushButton()
            self.minus_btn.setIcon(qta.icon("mdi6.minus", color="#a0a0b8"))
            self.minus_btn.setFixedSize(24, 24)
            self.minus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.minus_btn.setStyleSheet(
                "QPushButton { background: #27272a; border: none; border-radius: 4px; }"
                "QPushButton:hover { background: rgba(16, 185, 129, 0.15); }"
            )
            self.minus_btn.clicked.connect(self._decrement_progress)
            counter_layout.addWidget(self.minus_btn)

            self.plus_btn = QPushButton()
            self.plus_btn.setIcon(qta.icon("mdi6.plus", color="#10B981"))
            self.plus_btn.setFixedSize(24, 24)
            self.plus_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.plus_btn.setStyleSheet(
                "QPushButton { background: #27272a; border: none; border-radius: 4px; }"
                "QPushButton:hover { background: rgba(16, 185, 129, 0.25); }"
            )
            self.plus_btn.clicked.connect(self._increment_progress)
            counter_layout.addWidget(self.plus_btn)

            self.main_layout.addWidget(self.counter_widget)
        else:
            # Standart Checkbox Arayüzü
            self.checkbox = QCheckBox()
            self.checkbox.setChecked(is_completed)
            self.checkbox.setStyleSheet(
                "QCheckBox::indicator { width: 20px; height: 20px;"
                " border: 2px solid #27272a; border-radius: 4px;"
                " background: transparent; }"
                "QCheckBox::indicator:checked { background: #10B981;"
                " border-color: #10B981; }"
                "QCheckBox::indicator:hover { border-color: #34d399; }"
            )
            self.checkbox.stateChanged.connect(self._on_state_changed)
            self.main_layout.addWidget(self.checkbox)

        # 2. Hedef Metni ve Sayaç Bilgisi
        self.label_layout = QVBoxLayout()
        self.label_layout.setSpacing(2)
        
        self.label = QLabel(text)
        self.label.setStyleSheet("font-size: 14px; color: #e8e8e8;")
        self.label_layout.addWidget(self.label)

        if self.total_progress > 1:
            self.lbl_progress = QLabel(f"İlerleme: {self.progress} / {self.total_progress}")
            self.lbl_progress.setStyleSheet("font-size: 11px; color: #a0a0b8;")
            self.label_layout.addWidget(self.lbl_progress)
            
        self.main_layout.addLayout(self.label_layout, stretch=1)

        # 3. Tamamlandı İkonu
        self.check_icon = QLabel()
        self.check_icon.setPixmap(
            qta.icon("mdi6.check-circle", color="#69F0AE").pixmap(20, 20)
        )
        self.main_layout.addWidget(self.check_icon)

        # 4. Sil Butonu
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
        self.main_layout.addWidget(self.delete_btn)

        # Başlangıç stili
        self.update_style(self.is_completed)

    def _on_state_changed(self, state):
        is_completed = self.checkbox.isChecked()
        self.is_completed = is_completed
        self.update_style(is_completed)
        self.status_changed.emit(self.goal_id, is_completed)
        self._notify_parent()

    def _increment_progress(self):
        if self.progress < self.total_progress:
            self.progress += 1
            self.is_completed = (self.progress == self.total_progress)
            self.lbl_progress.setText(f"İlerleme: {self.progress} / {self.total_progress}")
            self.update_style(self.is_completed)
            self.progress_changed.emit(self.goal_id, self.progress, self.is_completed)
            self._notify_parent()

    def _decrement_progress(self):
        if self.progress > 0:
            self.progress -= 1
            self.is_completed = (self.progress == self.total_progress)
            self.lbl_progress.setText(f"İlerleme: {self.progress} / {self.total_progress}")
            self.update_style(self.is_completed)
            self.progress_changed.emit(self.goal_id, self.progress, self.is_completed)
            self._notify_parent()

    def _notify_parent(self):
        p = self.parentWidget()
        while p is not None:
            if hasattr(p, "update_progress"):
                p.update_progress()
                break
            p = p.parentWidget()

    def _on_delete_clicked(self):
        self.delete_clicked.emit(self.goal_id)

    def update_style(self, is_completed: bool):
        self.is_completed = is_completed
        self.label.setStyleSheet(
            f"font-size: 14px; color: {'#6a6a8a' if is_completed else '#e8e8e8'};"
            f" {'text-decoration: line-through;' if is_completed else ''}"
        )
        if self.total_progress > 1:
            self.lbl_progress.setStyleSheet(
                f"font-size: 11px; color: {'#52526b' if is_completed else '#a0a0b8'};"
            )
        self.check_icon.setVisible(is_completed)



class AddGoalDialog(BaseModernDialog):
    """Yeni hedef eklemek için detaylı modern diyalog kutusu (Periyot ve Sayaç desteği ile)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title_label.setText("Yeni Hedef Ekle")
        self.title_icon.setPixmap(qta.icon("mdi6.target", color="#10B981").pixmap(18, 18))
        self.setMinimumWidth(380)

        # 1. Hedef Açıklaması
        self.layout.addWidget(QLabel("Hedef Açıklaması:"))
        self.input_text = QLineEdit()
        self.input_text.setPlaceholderText("Örn: Kitap oku, spor yap...")
        self.input_text.setMinimumHeight(38)
        self.input_text.setStyleSheet(
            "QLineEdit { background: #18181b; border: 1px solid #27272a; border-radius: 8px;"
            " padding: 6px 12px; color: #f4f4f5; font-size: 13px; }"
            "QLineEdit:focus { border-color: #10B981; }"
        )
        self.input_text.returnPressed.connect(self.accept)
        self.layout.addWidget(self.input_text)

        # 2. Periyot Seçimi
        self.layout.addWidget(QLabel("Zaman Dilimi (Periyot):"))
        self.combo_period = QComboBox()
        self.combo_period.addItems(["Günlük", "Haftalık", "Aylık"])
        self.combo_period.setMinimumHeight(38)
        self.combo_period.setStyleSheet(
            "QComboBox { background: #18181b; border: 1px solid #27272a; border-radius: 8px;"
            " padding: 6px 12px; color: #f4f4f5; font-size: 13px; }"
            "QComboBox:focus { border-color: #10B981; }"
            "QComboBox QAbstractItemView { background: #18181b; color: #f4f4f5;"
            " selection-background-color: #10B981; border: 1px solid #27272a; }"
        )
        self.layout.addWidget(self.combo_period)

        # 3. Sayaçlı İlerleme Seçeneği
        self.check_is_counter = QCheckBox("Sayaçlı İlerleme Desteği (Örn: 20 sayfa okuma)")
        self.check_is_counter.setStyleSheet(
            "QCheckBox::indicator { width: 18px; height: 18px; border: 2px solid #27272a; border-radius: 4px; }"
            "QCheckBox::indicator:checked { background: #10B981; border-color: #10B981; }"
        )
        self.check_is_counter.stateChanged.connect(self._on_counter_changed)
        self.layout.addWidget(self.check_is_counter)

        # 4. İlerleme Hedef Değeri Girişi
        self.counter_widget = QWidget()
        counter_layout = QHBoxLayout(self.counter_widget)
        counter_layout.setContentsMargins(0, 0, 0, 0)
        
        lbl_total = QLabel("Hedef Sayı / Sınır:")
        lbl_total.setStyleSheet("font-size: 12px; color: #a0a0b8;")
        counter_layout.addWidget(lbl_total)
        
        self.spin_total = QSpinBox()
        self.spin_total.setRange(2, 9999)
        self.spin_total.setValue(5)
        self.spin_total.setMinimumHeight(38)
        self.spin_total.setStyleSheet(
            "QSpinBox { background: #18181b; border: 1px solid #27272a; border-radius: 8px;"
            " padding: 6px 12px; color: #f4f4f5; font-size: 13px; }"
        )
        counter_layout.addWidget(self.spin_total, stretch=1)
        
        self.layout.addWidget(self.counter_widget)
        self.counter_widget.setVisible(False)

        # Alt Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        btn_layout.addStretch()

        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.setMinimumHeight(36)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setStyleSheet(
            "QPushButton { background: #18181b; border: 1px solid #27272a; border-radius: 6px;"
            " color: #a1a1aa; padding: 0 16px; font-weight: 600; }"
            "QPushButton:hover { border-color: #ef4444; color: #ef4444; }"
        )
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        self.ok_btn = QPushButton("Ekle")
        self.ok_btn.setMinimumHeight(36)
        self.ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.ok_btn.setStyleSheet(
            "QPushButton { background: #10B981; border: none; border-radius: 6px;"
            " color: #09090b; padding: 0 20px; font-weight: 600; }"
            "QPushButton:hover { background: #34d399; }"
        )
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)

        self.layout.addLayout(btn_layout)

    def _on_counter_changed(self, state):
        self.counter_widget.setVisible(self.check_is_counter.isChecked())

    def get_data(self):
        period_map = {"Günlük": "daily", "Haftalık": "weekly", "Aylık": "monthly"}
        is_counter = self.check_is_counter.isChecked()
        return {
            "text": self.input_text.text().strip(),
            "period": period_map.get(self.combo_period.currentText(), "daily"),
            "completed": False,
            "progress": 0,
            "total_progress": self.spin_total.value() if is_counter else 1
        }


class GoalsPage(QWidget):
    """Gelişmiş hedefler sayfası — günlük/haftalık/aylık hedeflerin ve sayaçların takibi."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("goals_page")
        self.db = JSONManager()
        self._goal_items = []
        self.selected_period = "daily"  # Varsayılan: Günlük hedefler

        # --- Ana düzen ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setObjectName("goals_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll içeriği
        content = QWidget()
        content.setObjectName("goals_content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # --- Sayfa başlığı ---
        title_row = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(
            qta.icon("mdi6.target", color="#10B981").pixmap(28, 28)
        )
        title_row.addWidget(title_icon)

        page_title = QLabel("Hedeflerim")
        page_title.setObjectName("page_title")
        page_title.setStyleSheet(
            "font-size: 24px; font-weight: 700; color: #e8e8e8;"
        )
        title_row.addWidget(page_title)
        title_row.addStretch()
        layout.addLayout(title_row)

        # --- Tarih göstergesi ---
        ay_isimleri = [
            "", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
            "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
        ]
        bugun = datetime.now()
        tarih_str = f"Bugün — {bugun.day} {ay_isimleri[bugun.month]} {bugun.year}"

        date_label = QLabel(tarih_str)
        date_label.setObjectName("date_indicator")
        date_label.setStyleSheet(
            "font-size: 14px; color: #a0a0b8; margin-bottom: 4px;"
        )
        layout.addWidget(date_label)

        # --- Zaman Periyodu Sekme Butonları ---
        period_layout = QHBoxLayout()
        period_layout.setSpacing(8)
        
        self.btn_group = QButtonGroup(self)
        
        # Ortak Buton Stili (Seçili butona 'active="true"' set edeceğiz)
        btn_style = (
            "QPushButton { background: #18181b; border: 1px solid #27272a; border-radius: 8px;"
            " color: #a1a1aa; padding: 10px 16px; font-weight: 600; font-size: 13px; }"
            "QPushButton:hover { border-color: #10B981; color: #ffffff; }"
            "QPushButton[active=\"true\"] { background: rgba(16, 185, 129, 0.12); border-color: #10B981; color: #10B981; }"
        )

        self.btn_daily = QPushButton("Günlük Hedefler")
        self.btn_daily.setStyleSheet(btn_style)
        self.btn_daily.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_daily.setProperty("active", "true")
        self.btn_daily.clicked.connect(lambda: self._on_period_changed("daily"))
        period_layout.addWidget(self.btn_daily)

        self.btn_weekly = QPushButton("Haftalık Hedefler")
        self.btn_weekly.setStyleSheet(btn_style)
        self.btn_weekly.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_weekly.setProperty("active", "false")
        self.btn_weekly.clicked.connect(lambda: self._on_period_changed("weekly"))
        period_layout.addWidget(self.btn_weekly)

        self.btn_monthly = QPushButton("Aylık Hedefler")
        self.btn_monthly.setStyleSheet(btn_style)
        self.btn_monthly.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_monthly.setProperty("active", "false")
        self.btn_monthly.clicked.connect(lambda: self._on_period_changed("monthly"))
        period_layout.addWidget(self.btn_monthly)
        
        period_layout.addStretch()
        layout.addLayout(period_layout)

        # --- İlerleme çubuğu ---
        progress_frame = QFrame()
        progress_frame.setStyleSheet(
            "QFrame { background: #18181b; border: 1px solid #27272a;"
            " border-radius: 12px; }"
        )
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setContentsMargins(20, 16, 20, 16)
        progress_layout.setSpacing(8)

        progress_header = QHBoxLayout()
        self.progress_title = QLabel("Günlük İlerleme")
        self.progress_title.setStyleSheet("font-size: 14px; font-weight: 600; color: #e8e8e8;")
        progress_header.addWidget(self.progress_title)

        self.progress_value = QLabel("0/0 hedef")
        self.progress_value.setStyleSheet("font-size: 12px; color: #a0a0b8;")
        progress_header.addStretch()
        progress_header.addWidget(self.progress_value)
        progress_layout.addLayout(progress_header)

        self.goals_progress = QProgressBar()
        self.goals_progress.setObjectName("goals_progress")
        self.goals_progress.setValue(0)
        self.goals_progress.setFormat("%p% tamamlandı")
        self.goals_progress.setMinimumHeight(24)
        progress_layout.addWidget(self.goals_progress)
        layout.addWidget(progress_frame)

        # --- Hedef listesi layout'u ---
        self.goals_layout = QVBoxLayout()
        self.goals_layout.setSpacing(10)
        layout.addLayout(self.goals_layout)

        # --- Yeni Hedef Ekle butonu ---
        self.add_goal_btn = TactileButton("  Yeni Hedef Ekle")
        self.add_goal_btn.setObjectName("secondary_btn")
        self.add_goal_btn.setIcon(qta.icon("mdi6.plus-circle-outline", color="#10B981"))
        self.add_goal_btn.setMinimumHeight(44)
        self.add_goal_btn.clicked.connect(self._on_add_goal_clicked)
        layout.addWidget(self.add_goal_btn)

        # --- Motivasyon quote ---
        quote_label = QLabel('"Büyük hedefler küçük adımlarla başlar."')
        quote_label.setObjectName("motivation_quote")
        quote_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        quote_label.setStyleSheet(
            "font-size: 13px; color: #10B981; font-style: italic;"
            " margin-top: 24px; padding: 16px;"
        )
        layout.addWidget(quote_label)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # Hedefleri yükle
        self.load_goals()

    def _on_period_changed(self, period):
        """Seçilen periyodu değiştirir ve listeyi günceller."""
        if self.selected_period == period:
            return
        
        self.selected_period = period
        
        # Butonların aktiflik durumunu güncelle
        self.btn_daily.setProperty("active", "true" if period == "daily" else "false")
        self.btn_weekly.setProperty("active", "true" if period == "weekly" else "false")
        self.btn_monthly.setProperty("active", "true" if period == "monthly" else "false")
        
        # Stilleri yenile
        self.btn_daily.style().unpolish(self.btn_daily)
        self.btn_daily.style().polish(self.btn_daily)
        self.btn_weekly.style().unpolish(self.btn_weekly)
        self.btn_weekly.style().polish(self.btn_weekly)
        self.btn_monthly.style().unpolish(self.btn_monthly)
        self.btn_monthly.style().polish(self.btn_monthly)

        # İlerleme başlığını güncelle
        period_titles = {"daily": "Günlük İlerleme", "weekly": "Haftalık İlerleme", "monthly": "Aylık İlerleme"}
        self.progress_title.setText(period_titles.get(period, "İlerleme"))

        self.load_goals()

    def _clear_goals_layout(self):
        """Hedef listesi arayüz elemanlarını temizler."""
        while self.goals_layout.count():
            item = self.goals_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._goal_items.clear()

    def load_goals(self):
        """Hedefleri JSON'dan yükleyip listeler."""
        self._clear_goals_layout()
        goals = self.db.get_all_goals()
        
        for goal in goals:
            # Sadece mevcut periyoda ait hedefleri göster
            if goal.get("period", "daily") != self.selected_period:
                continue

            item = GoalItem(
                goal_id=goal["id"],
                text=goal["text"],
                is_completed=goal["completed"],
                period=goal.get("period", "daily"),
                progress=goal.get("progress", 0),
                total_progress=goal.get("total_progress", 1)
            )
            item.status_changed.connect(self._on_goal_status_changed)
            item.progress_changed.connect(self._on_goal_progress_changed)
            item.delete_clicked.connect(self._on_delete_goal)
            
            self.goals_layout.addWidget(item)
            self._goal_items.append(item)

        self.update_progress()

        # Staggered entry animasyonunu tetikle
        if self._goal_items:
            QTimer.singleShot(30, lambda: StaggerAnimationHelper.stagger_widgets(self._goal_items))

    def update_progress(self):
        """Günlük/Haftalık/Aylık ilerleme göstergelerini dinamik olarak günceller."""
        total_goals = len(self._goal_items)
        if total_goals == 0:
            self.goals_progress.setValue(0)
            self.progress_value.setText("0/0 hedef")
            return

        completed_goals = sum(1 for item in self._goal_items if item.is_completed)
        percentage = int((completed_goals / total_goals) * 100)

        self.goals_progress.setValue(percentage)
        self.progress_value.setText(f"{completed_goals}/{total_goals} hedef")

    def _on_goal_status_changed(self, goal_id, completed):
        """Hedef tamamlanma durumu değiştiğinde JSON dosyasını günceller."""
        self.db.update_goal_status(goal_id, completed)

    def _on_goal_progress_changed(self, goal_id, progress, is_completed):
        """Sayaçlı hedef ilerlemesi değiştiğinde JSON dosyasını günceller."""
        self.db.update_goal(goal_id, progress=progress, completed=is_completed)

    def _on_add_goal_clicked(self):
        """Kullanıcıdan yeni hedef alıp veritabanına ekler."""
        dialog = AddGoalDialog(self)
        if dialog.exec() == BaseModernDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["text"]:
                self.db.add_goal(
                    text=data["text"],
                    completed=data["completed"],
                    period=data["period"],
                    progress=data["progress"],
                    total_progress=data["total_progress"]
                )
                self.load_goals()

    def _on_delete_goal(self, goal_id):
        """Hedefi siler ve listeyi günceller."""
        if self.db.delete_goal(goal_id):
            self.load_goals()



