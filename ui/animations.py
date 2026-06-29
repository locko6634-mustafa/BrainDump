# -*- coding: utf-8 -*-
"""
BrainDump — Animasyon ve Etkileşim Bileşenleri
TactileButton, HoverCard ve StaggerAnimationHelper sınıfları.
"""

from PyQt6.QtWidgets import (
    QPushButton, QFrame, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint,
    QParallelAnimationGroup, QTimer
)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6 import sip


class TactileButton(QPushButton):
    """
    Tıklama esnasında içeri doğru kayma (offset) efekti uygulayarak
    fiziksel geri bildirim sunan son derece kararlı modern buton.
    """
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        """Butona basıldığında içeriği kaydırarak basılma hissi verir."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setStyleSheet(self.styleSheet() + " padding-top: 3px; padding-left: 2px; ")
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Tıklama bırakıldığında normal konumuna döner."""
        if event.button() == Qt.MouseButton.LeftButton:
            clean_style = self.styleSheet().replace(" padding-top: 3px; padding-left: 2px; ", "")
            self.setStyleSheet(clean_style)
        super().mouseReleaseEvent(event)


class HoverCard(QFrame):
    """
    Üzerine gelindiğinde gölge derinliği pürüzsüzce artan ve zümrüt yeşili sınır
    vurgusu kazanan modern kart bileşeni (Köşe Yarıçapı: 12px standart).
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hover_card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Varsayılan QSS stili
        self.setStyleSheet(
            "QFrame#hover_card { background-color: #18181b; border: 1px solid #27272a; border-radius: 12px; }"
        )
        
        # Animasyon özellikleri başlangıç değerleri
        self._border_alpha = 0
        self._shadow_blur = 12
        
        # Gölgeyi oluştur
        self._create_shadow()
        
        # Gölge blur animasyonu
        self._blur_anim = QPropertyAnimation(self, b"shadow_blur", self)
        self._blur_anim.setDuration(220)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Sınır çizgisi renk animasyonu
        self._border_anim = QPropertyAnimation(self, b"border_alpha", self)
        self._border_anim.setDuration(220)
        self._border_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _create_shadow(self):
        """Gölge efektini oluşturur veya silinmişse yeniden atar."""
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(self._shadow_blur)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self._shadow)

    def _ensure_shadow_exists(self):
        """Gölge efektinin C++ tarafında silinip silinmediğini kontrol edip gerekirse oluşturur."""
        if not hasattr(self, "_shadow") or sip.isdeleted(self._shadow):
            self._create_shadow()

    @pyqtProperty(int)
    def shadow_blur(self) -> int:
        return self._shadow_blur

    @shadow_blur.setter
    def shadow_blur(self, value: int):
        self._shadow_blur = value
        self._ensure_shadow_exists()
        if not sip.isdeleted(self._shadow):
            self._shadow.setBlurRadius(value)

    @pyqtProperty(int)
    def border_alpha(self) -> int:
        return self._border_alpha

    @border_alpha.setter
    def border_alpha(self, value: int):
        self._border_alpha = value
        bg_color = "#1c1c21" if value > 0 else "#18181b"
        self.setStyleSheet(
            f"QFrame#hover_card {{ "
            f"  background-color: {bg_color}; "
            f"  border: 1px solid rgba(16, 185, 129, {value / 255.0}); "
            f"  border-radius: 12px; "
            f"}}"
        )
        self._ensure_shadow_exists()
        if not sip.isdeleted(self._shadow):
            self._shadow.setColor(QColor(16, 185, 129, int(80 + (120 - 80) * (value / 255.0))))

    def enterEvent(self, event):
        """Fare kartın üzerine geldiğinde yükselme efekti başlar."""
        self._ensure_shadow_exists()
        self._blur_anim.stop()
        self._blur_anim.setStartValue(self._shadow_blur)
        self._blur_anim.setEndValue(24)
        self._blur_anim.start()
        
        self._border_anim.stop()
        self._border_anim.setStartValue(self._border_alpha)
        self._border_anim.setEndValue(200)
        self._border_anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Fare karttan ayrıldığında kart normale döner."""
        self._ensure_shadow_exists()
        self._blur_anim.stop()
        self._blur_anim.setStartValue(self._shadow_blur)
        self._blur_anim.setEndValue(12)
        self._blur_anim.start()
        
        self._border_anim.stop()
        self._border_anim.setStartValue(self._border_alpha)
        self._border_anim.setEndValue(0)
        self._border_anim.start()
        super().leaveEvent(event)


class StaggerAnimationHelper:
    """
    Bir layout içerisindeki elemanları sırayla,
    aşağıdan yukarıya doğru kaydırarak (fade-in + slide-up) ekrana getiren yardımcı sınıf.
    """
    @staticmethod
    def stagger_widgets(widgets, start_delay=50, interval=40):
        """
        Verilen widget listesine sırayla animasyon uygular.
        :param widgets: Animasyon uygulanacak QWidget listesi
        :param start_delay: İlk animasyon başlamadan önceki gecikme (ms)
        :param interval: Elemanlar arasındaki animasyon gecikmesi (ms)
        """
        anim_group = QParallelAnimationGroup()
        anim_group._animations = []
        
        for i, widget in enumerate(widgets):
            # Widget veya C++ nesnesi silinmişse atla
            if sip.isdeleted(widget):
                continue
                
            if not widget.isVisible():
                widget.setVisible(True)
                
            # Halihazırda bir grafik efekti varsa (örn: HoverCard drop shadow), 
            # yeni bir opacity efekti atayıp eski efekti ezmiyoruz.
            has_existing_effect = widget.graphicsEffect() is not None
            
            op_effect = None
            op_anim = None
            if not has_existing_effect:
                op_effect = QGraphicsOpacityEffect(widget)
                widget.setGraphicsEffect(op_effect)
                op_effect.setOpacity(0.0)
                
                op_anim = QPropertyAnimation(op_effect, b"opacity")
                op_anim.setDuration(250)
                op_anim.setStartValue(0.0)
                op_anim.setEndValue(1.0)
                op_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            orig_pos = widget.pos()
            pos_anim = QPropertyAnimation(widget, b"pos")
            pos_anim.setDuration(280)
            pos_anim.setEasingCurve(QEasingCurve.Type.OutBack)
            
            delay = start_delay + (i * interval)
            
            def make_trigger(w=widget, op=op_anim, pos=pos_anim, o_pos=orig_pos):
                def trigger():
                    if sip.isdeleted(w):
                        return
                    current_pos = w.pos()
                    pos.setStartValue(QPoint(current_pos.x(), current_pos.y() + 15))
                    pos.setEndValue(current_pos)
                    
                    if op is not None:
                        op.start()
                    pos.start()
                return trigger
                
            timer = QTimer(widget)
            timer.setSingleShot(True)
            timer.timeout.connect(make_trigger())
            timer.start(delay)
            
            # Animasyonları ve timer'ı canlı tutmak için sakla
            if op_anim is not None:
                anim_group._animations.append(op_anim)
            anim_group._animations.extend([pos_anim, timer])
            
        def cleanup():
            for w in widgets:
                if sip.isdeleted(w):
                    continue
                try:
                    # Sadece bizim dinamik olarak atadığımız opacity efektini temizliyoruz.
                    # HoverCard gibi kendi yerleşik efekti (shadow) olanlara dokunmuyoruz.
                    if not isinstance(w, HoverCard) and not w.inherits("HoverCard"):
                        w.setGraphicsEffect(None)
                except Exception:
                    pass
        
        total_duration = start_delay + (len(widgets) * interval) + 300
        cleanup_timer = QTimer()
        cleanup_timer.setSingleShot(True)
        StaggerAnimationHelper._active_timer = cleanup_timer
        cleanup_timer.timeout.connect(cleanup)
        cleanup_timer.start(total_duration)
