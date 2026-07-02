# -*- coding: utf-8 -*-
"""
BrainDump — Modern Toast/Snackbar Bildirim Sistemi
Ekranın sağ üst köşesinde pürüzsüzce açılan ve stack şeklinde üst üste binen bildirimler.
"""

from PyQt6.QtWidgets import QFrame, QLabel, QHBoxLayout, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor
from PyQt6 import sip
import qtawesome as qta


class ToastNotification(QFrame):
    """Tek bir Toast bildirim kartı."""
    
    # Aktif toast bildirimlerini tutan sınıf düzeyindeki liste
    _active_toasts = []

    def __init__(self, parent, title: str, message: str, toast_type: str = "success", duration: int = 3000):
        # Ebeveyn widget'ı doğrudan alıyoruz ki onun içinde pozisyon alabilelim.
        super().__init__(parent)
        self.setObjectName("toast_widget")
        self.setFixedSize(300, 70)
        
        self.duration = duration
        self.toast_type = toast_type
        self.parent_widget = parent

        # Gölge efekti
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setOffset(0, 4)
        self.shadow.setColor(QColor(0, 0, 0, 70))
        self.setGraphicsEffect(self.shadow)

        # Düzen
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(14, 10, 14, 10)
        main_layout.setSpacing(12)

        # İkon belirleme
        icon_label = QLabel()
        if toast_type == "success":
            icon_img = qta.icon("mdi6.checkbox-marked-circle-outline", color="#10B981").pixmap(24, 24)
        elif toast_type == "error":
            icon_img = qta.icon("mdi6.alert-circle-outline", color="#FF5252").pixmap(24, 24)
        else:  # info
            icon_img = qta.icon("mdi6.information-outline", color="#3B82F6").pixmap(24, 24)
        icon_label.setPixmap(icon_img)
        main_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Metin düzeni
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        title_lbl = QLabel(title)
        title_lbl.setObjectName("toast_title")
        text_layout.addWidget(title_lbl)

        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("toast_message")
        msg_lbl.setWordWrap(True)
        text_layout.addWidget(msg_lbl)

        main_layout.addLayout(text_layout, stretch=1)

        # Aktif listeye ekle ve konumlandır
        self.target_y = 20
        ToastNotification._active_toasts.append(self)
        self._reposition_all()

        # Giriş animasyonu (Sağdan içeri kayma)
        self.setWindowOpacity(0.0)
        start_x = self.parent_widget.width() # Ekranın dışından başla
        self.target_x = self.parent_widget.width() - self.width() - 20
        self.move(start_x, self.target_y)

        # Pozisyon animasyonu
        self.pos_anim = QPropertyAnimation(self, b"pos", self)
        self.pos_anim.setDuration(350)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_anim.setStartValue(QPoint(start_x, self.target_y))
        self.pos_anim.setEndValue(QPoint(self.target_x, self.target_y))
        self.pos_anim.start()

        # Otomatik kapanma zamanlayıcısı
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close_toast)
        self.timer.start(self.duration)

    def _reposition_all(self):
        """Tüm aktif toastları dikey olarak üst üste stack eder."""
        # Silinmiş olanları temizle
        ToastNotification._active_toasts = [
            t for t in ToastNotification._active_toasts 
            if not sip.isdeleted(t)
        ]
        
        y_offset = 20
        for toast in ToastNotification._active_toasts:
            toast.target_y = y_offset
            toast.target_x = self.parent_widget.width() - toast.width() - 20
            toast.animate_to_target()
            y_offset += toast.height() + 10

    def animate_to_target(self):
        """Toast'ı hedef koordinatlarına kaydırır."""
        if hasattr(self, "pos_anim") and self.pos_anim.state() == QPropertyAnimation.State.Running:
            self.pos_anim.stop()
            
        self.pos_anim = QPropertyAnimation(self, b"pos", self)
        self.pos_anim.setDuration(250)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.pos_anim.setStartValue(self.pos())
        self.pos_anim.setEndValue(QPoint(self.target_x, self.target_y))
        self.pos_anim.start()

    def close_toast(self):
        """Bildirimi kapatma animasyonunu çalıştırır ve kaldırır."""
        if sip.isdeleted(self):
            return
            
        # Çıkış animasyonu (Sağa kayarak çıkma)
        if hasattr(self, "pos_anim") and self.pos_anim.state() == QPropertyAnimation.State.Running:
            self.pos_anim.stop()
            
        self.pos_anim = QPropertyAnimation(self, b"pos", self)
        self.pos_anim.setDuration(300)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.pos_anim.setStartValue(self.pos())
        self.pos_anim.setEndValue(QPoint(self.parent_widget.width(), self.y()))
        
        def on_finished():
            if not sip.isdeleted(self):
                self.hide()
                if self in ToastNotification._active_toasts:
                    ToastNotification._active_toasts.remove(self)
                self.deleteLater()
                # Kalanları yeniden hizala
                self._reposition_all()
                
        self.pos_anim.finished.connect(on_finished)
        self.pos_anim.start()


class ToastManager:
    """Toast bildirimlerini kolayca çağırmak için yönetici arayüzü."""
    
    @staticmethod
    def show(parent, title: str, message: str, toast_type: str = "success", duration: int = 3000):
        """Dinamik olarak yeni bir toast bildirimi gösterir."""
        # parent olarak MainWindow bulmaya çalışalım
        main_win = parent
        while main_win and main_win.parentWidget() is not None:
            main_win = main_win.parentWidget()
            
        toast = ToastNotification(main_win, title, message, toast_type, duration)
        toast.show()
        return toast
