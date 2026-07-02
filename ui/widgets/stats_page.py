# -*- coding: utf-8 -*-
"""
İstatistikler Sayfası Widget'ı
Özet kartları, grafik alanı ve aktivite özeti.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea
)
from PyQt6.QtCore import (
    Qt, QPointF
)
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient, QPainterPath
from datetime import datetime, timedelta
import qtawesome as qta
from core.json_manager import JSONManager
from core.utils import parse_turkish_date, format_date_tr


class DynamicLineChart(QWidget):
    """QPainter tabanlı, degradeli son 7 günün aktivite çizgi grafiği."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data_notes = [0] * 7
        self.data_goals = [0] * 7
        self.dates = [""] * 7
        self.setMinimumHeight(220)

    def set_data(self, dates, notes, goals):
        self.dates = dates
        self.data_notes = notes
        self.data_goals = goals
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        padding_left = 35
        padding_right = 20
        padding_top = 20
        padding_bottom = 25
        
        plot_width = width - padding_left - padding_right
        plot_height = height - padding_top - padding_bottom
        
        # Eksen çizgisi
        axis_pen = QPen(QColor("#27272a"), 1)
        painter.setPen(axis_pen)
        painter.drawLine(padding_left, height - padding_bottom, width - padding_right, height - padding_bottom)
        
        max_val = max(max(self.data_notes), max(self.data_goals), 5)
        
        # Grid ve Kılavuz yazıları
        grid_pen = QPen(QColor("#1f1f23"), 1, Qt.PenStyle.DashLine)
        text_pen = QPen(QColor("#71717a"), 1)
        
        for i in range(4):
            val = int(max_val * i / 3)
            y = height - padding_bottom - int(plot_height * i / 3)
            painter.setPen(grid_pen)
            painter.drawLine(padding_left, y, width - padding_right, y)
            
            painter.setPen(text_pen)
            painter.drawText(10, y + 4, str(val))
            
        # Gün isimleri
        for i in range(7):
            x = padding_left + int(plot_width * i / 6)
            painter.setPen(text_pen)
            date_str = self.dates[i] if i < len(self.dates) else ""
            painter.drawText(x - 18, height - 6, date_str)
            
        # Çizgi 1: Not Aktivitesi (Zümrüt Yeşili)
        self._draw_trend_line(painter, self.data_notes, QColor("#10B981"), max_val, padding_left, padding_bottom, plot_width, plot_height, height)
        # Çizgi 2: Hedef Aktivitesi (Mavi)
        self._draw_trend_line(painter, self.data_goals, QColor("#3B82F6"), max_val, padding_left, padding_bottom, plot_width, plot_height, height)

    def _draw_trend_line(self, painter, data, color, max_val, padding_left, padding_bottom, plot_width, plot_height, height):
        points = []
        for i in range(7):
            x = padding_left + int(plot_width * i / 6)
            y = height - padding_bottom - int(plot_height * data[i] / max_val)
            points.append(QPointF(x, y))
            
        path = QPainterPath()
        path.moveTo(points[0])
        for pt in points[1:]:
            path.lineTo(pt)
            
        line_pen = QPen(color, 2.5)
        painter.setPen(line_pen)
        painter.drawPath(path)
        
        fill_path = QPainterPath(path)
        fill_path.lineTo(points[-1].x(), height - padding_bottom)
        fill_path.lineTo(points[0].x(), height - padding_bottom)
        fill_path.closeSubpath()
        
        gradient = QLinearGradient(0, height - padding_bottom - plot_height, 0, height - padding_bottom)
        gradient.setColorAt(0.0, QColor(color.red(), color.green(), color.blue(), 60))
        gradient.setColorAt(1.0, QColor(color.red(), color.green(), color.blue(), 5))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(fill_path)
        
        point_brush = QBrush(QColor("#18181b"))
        point_pen = QPen(color, 2)
        for pt in points:
            painter.setPen(point_pen)
            painter.setBrush(point_brush)
            painter.drawEllipse(pt, 4, 4)


class StatCard(QFrame):
    """Tek bir istatistik özet kartı bileşeni."""

    def __init__(self, icon_name: str, value: str, label: str, parent=None):
        super().__init__(parent)
        self.setObjectName("stat_card")
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 20)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # İkon (32px)
        icon_label = QLabel()
        icon_label.setPixmap(
            qta.icon(icon_name, color="#10B981").pixmap(32, 32)
        )
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)

        # Değer (büyük font)
        self.value_label = QLabel(value)
        self.value_label.setObjectName("stat_value")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)

        # Etiket (küçük)
        label_widget = QLabel(label)
        label_widget.setObjectName("stat_label")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_widget)

    def update_value(self, new_value: str):
        """Kart üzerindeki değeri dinamik olarak günceller."""
        self.value_label.setText(new_value)


class StatsPage(QWidget):
    """İstatistikler sayfası — özet kartları ve grafik alanı."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("stats_page")
        self.db = JSONManager()

        # --- Ana düzen ---
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll alanı
        scroll = QScrollArea()
        scroll.setObjectName("stats_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Scroll içeriği
        content = QWidget()
        content.setObjectName("stats_content")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # --- Sayfa başlığı ---
        title_row = QHBoxLayout()
        title_icon = QLabel()
        title_icon.setPixmap(
            qta.icon("mdi6.chart-bar", color="#10B981").pixmap(28, 28)
        )
        title_row.addWidget(title_icon)

        page_title = QLabel("İstatistikler")
        page_title.setObjectName("page_title")
        title_row.addWidget(page_title)
        title_row.addStretch()
        layout.addLayout(title_row)

        # --- 4 adet özet kartı (yatay sıralı) ---
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        # İstatistik kartlarını sınıf değişkeni olarak saklıyoruz
        self.card_total_notes = StatCard("mdi6.notebook-outline", "0", "Toplam Not")
        self.card_weekly_notes = StatCard("mdi6.calendar-week", "0", "Bu Hafta")
        self.card_completed_goals = StatCard("mdi6.check-circle-outline", "0", "Tamamlanan Hedef")
        self.card_streak = StatCard("mdi6.fire", "0 Gün", "Seri")

        cards_layout.addWidget(self.card_total_notes, stretch=1)
        cards_layout.addWidget(self.card_weekly_notes, stretch=1)
        cards_layout.addWidget(self.card_completed_goals, stretch=1)
        cards_layout.addWidget(self.card_streak, stretch=1)

        layout.addLayout(cards_layout)

        # --- Grafik Kartı (Gerçek Grafik Alanı) ---
        chart_card = QFrame()
        chart_card.setObjectName("chart_card")
        chart_card.setMinimumHeight(280)

        chart_card_layout = QVBoxLayout(chart_card)
        chart_card_layout.setContentsMargins(20, 16, 20, 16)
        chart_card_layout.setSpacing(10)

        # Grafik Başlığı ve Legend Satırı
        chart_header = QHBoxLayout()
        chart_title = QLabel("Haftalık Aktivite Trendi")
        chart_title.setObjectName("section_title")
        chart_header.addWidget(chart_title)
        chart_header.addStretch()

        # Legend: Notlar (Emerald Yeşil)
        note_legend_icon = QLabel()
        note_legend_icon.setPixmap(qta.icon("mdi6.circle", color="#10B981").pixmap(10, 10))
        note_legend_lbl = QLabel("Not Yazma")
        note_legend_lbl.setObjectName("stat_label")
        chart_header.addWidget(note_legend_icon)
        chart_header.addWidget(note_legend_lbl)

        chart_header.addSpacing(10)

        # Legend: Hedefler (Mavi)
        goal_legend_icon = QLabel()
        goal_legend_icon.setPixmap(qta.icon("mdi6.circle", color="#3B82F6").pixmap(10, 10))
        goal_legend_lbl = QLabel("Tamamlanan Hedef")
        goal_legend_lbl.setObjectName("stat_label")
        chart_header.addWidget(goal_legend_icon)
        chart_header.addWidget(goal_legend_lbl)

        chart_card_layout.addLayout(chart_header)

        # QPainter Grafik Widget'ı
        self.chart = DynamicLineChart()
        chart_card_layout.addWidget(self.chart)

        layout.addWidget(chart_card)

        # --- Aktivite Özeti bölümü ---
        summary_frame = QFrame()
        summary_frame.setObjectName("activity_summary")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(20, 16, 20, 16)
        summary_layout.setSpacing(8)

        summary_title = QLabel("Aktivite Özeti")
        summary_title.setObjectName("section_title")
        summary_layout.addWidget(summary_title)

        self.summary_text = QLabel("Yükleniyor...")
        self.summary_text.setObjectName("stat_label")
        summary_layout.addWidget(self.summary_text)

        layout.addWidget(summary_frame)

        layout.addStretch()

        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        # İstatistikleri ilk kez yükle
        self.load_stats()

    def load_stats(self):
        """İstatistikleri JSON'dan okuyup dinamik olarak günceller."""
        notes = self.db.get_all_notes()
        goals = self.db.get_all_goals()

        # 1. Toplam Not
        total_notes = len(notes)
        self.card_total_notes.update_value(str(total_notes))

        # 2. Bu Hafta Eklenen Notlar (Son 7 Gün) - Gerçek Veri
        weekly_count = 0
        now = datetime.now()
        one_week_ago = now - timedelta(days=7)
        for note in notes:
            note_date = parse_turkish_date(note.get("date", ""))
            if note_date and one_week_ago <= note_date <= now:
                weekly_count += 1
            
        self.card_weekly_notes.update_value(str(weekly_count))

        # 3. Tamamlanan Hedef
        completed_goals = sum(1 for g in goals if g.get("completed", False))
        self.card_completed_goals.update_value(str(completed_goals))

        # 4. Seri (Streak) - Gerçek Ardışık Gün Tamamlama Verisi
        completed_dates = set()
        for g in goals:
            if g.get("completed", False) and g.get("completed_at"):
                try:
                    date_part = g["completed_at"].split("T")[0]
                    completed_dates.add(date_part)
                except Exception:
                    pass
                    
        streak = 0
        if completed_dates:
            today_date = now.date()
            yesterday_date = today_date - timedelta(days=1)
            
            today_str = today_date.isoformat()
            yesterday_str = yesterday_date.isoformat()
            
            current_check = None
            if today_str in completed_dates:
                current_check = today_date
            elif yesterday_str in completed_dates:
                current_check = yesterday_date
                
            if current_check:
                streak = 1
                while True:
                    prev_day = current_check - timedelta(days=streak)
                    if prev_day.isoformat() in completed_dates:
                        streak += 1
                    else:
                        break
                        
        self.card_streak.update_value(f"{streak} Gün")

        # Aktivite Özeti metnini güncelle
        total_goals = len(goals)
        self.summary_text.setText(
            f"Kişisel beyninizde şu an {total_notes} not bulunuyor. "
            f"Toplam {total_goals} hedeften {completed_goals} tanesini başarıyla tamamladınız."
        )

        # 5. Grafik Verilerini Hazırla (Son 7 Gün) - Gerçek Veriler
        dates_list = []
        notes_counts = []
        goals_counts = []
        
        turkish_months_short = ["", "Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]

        for i in range(6, -1, -1):
            day = now - timedelta(days=i)
            day_str = f"{day.day} {turkish_months_short[day.month]}"
            dates_list.append(day_str)
            
            # Not sayısını bul (ISO YYYY-MM-DD olarak karşılaştır)
            day_iso = day.date().isoformat()
            notes_on_day = sum(1 for n in notes if n.get("date") == day_iso)
            notes_counts.append(notes_on_day)
            
            # Hedef tamamlanma sayısını bul (completed_at'e göre)
            goals_on_day = sum(
                1 for g in goals 
                if g.get("completed", False) and g.get("completed_at") and g.get("completed_at").split("T")[0] == day_iso
            )
            goals_counts.append(goals_on_day)

        # Grafik widget'ına verileri yükle
        if hasattr(self, 'chart'):
            self.chart.set_data(dates_list, notes_counts, goals_counts)
