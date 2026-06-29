# -*- coding: utf-8 -*-
"""
Özel Başlık Çubuğu Widget'ı (TitleBar)
Kenarlıksız pencereler için sürükleme, kapatma, küçültme ve büyütme işlevlerini sağlar.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QIcon
import qtawesome as qta


class TitleBar(QWidget):
    """
    Uygulama başlık çubuğu widget'ı.
    Pencereyi taşımak için sürükleme alanı sunar ve standart kontrol butonlarını barındırır.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("custom_title_bar")
        self.setFixedHeight(48)
        
        # Sürükleme değişkeni
        self._drag_pos = QPoint()
        self._parent_window = parent
        
        # Düzen
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)
        
        # Logo / İkon
        self.logo_label = QLabel()
        self.logo_label.setObjectName("title_bar_logo")
        # Zümrüt Yeşili tonlarında bir beyin veya şimşek simgesi
        self.logo_label.setPixmap(
            qta.icon("mdi6.brain", color="#10B981").pixmap(18, 18)
        )
        layout.addWidget(self.logo_label)
        
        # Uygulama Başlığı
        self.title_label = QLabel("BrainDump")
        self.title_label.setObjectName("title_bar_text")
        self.title_label.setStyleSheet("font-weight: 700; font-size: 13px; color: #f4f4f5; letter-spacing: 0.5px;")
        layout.addWidget(self.title_label)
        
        # Sürüm Bilgisi (Küçük)
        self.version_label = QLabel("v0.1.0")
        self.version_label.setObjectName("title_bar_version")
        self.version_label.setStyleSheet("font-size: 10px; color: #71717a; margin-left: 4px;")
        layout.addWidget(self.version_label)
        
        # Esnek boşluk (Başlık ile butonlar arası)
        layout.addStretch()
        
        # Kontrol Butonları
        # 1. Simge durumuna getir (Minimize)
        self.btn_minimize = QPushButton()
        self.btn_minimize.setObjectName("title_btn_minimize")
        self.btn_minimize.setToolTip("Küçült")
        self.btn_minimize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_minimize.setIcon(qta.icon("mdi6.minus", color="#a1a1aa"))
        self.btn_minimize.setFixedSize(32, 32)
        self.btn_minimize.clicked.connect(self._minimize_window)
        layout.addWidget(self.btn_minimize)
        
        # 2. Ekranı kapla / Büyüt (Maximize/Restore)
        self.btn_maximize = QPushButton()
        self.btn_maximize.setObjectName("title_btn_maximize")
        self.btn_maximize.setToolTip("Büyüt")
        self.btn_maximize.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_maximize.setIcon(qta.icon("mdi6.crop-square", color="#a1a1aa"))
        self.btn_maximize.setFixedSize(32, 32)
        self.btn_maximize.clicked.connect(self._maximize_restore_window)
        layout.addWidget(self.btn_maximize)
        
        # 3. Kapat (Close)
        self.btn_close = QPushButton()
        self.btn_close.setObjectName("title_btn_close")
        self.btn_close.setToolTip("Kapat")
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setIcon(qta.icon("mdi6.close", color="#a1a1aa"))
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.clicked.connect(self._close_window)
        layout.addWidget(self.btn_close)

    def _minimize_window(self):
        """Pencereyi simge durumuna getirir."""
        win = self.window()
        if win:
            win.showMinimized()

    def _maximize_restore_window(self):
        """Pencereyi ekranı kaplayacak şekilde büyütür veya eski boyutuna getirir."""
        win = self.window()
        if win:
            if win.isMaximized():
                win.showNormal()
                self.btn_maximize.setIcon(qta.icon("mdi6.crop-square", color="#a1a1aa"))
                self.btn_maximize.setToolTip("Büyüt")
            else:
                win.showMaximized()
                self.btn_maximize.setIcon(qta.icon("mdi6.checkbox-multiple-blank-outline", color="#a1a1aa"))
                self.btn_maximize.setToolTip("Aşağı Getir")

    def _close_window(self):
        """Pencereyi kapatır."""
        win = self.window()
        if win:
            win.close()

    def mousePressEvent(self, event):
        """Pencereyi sürüklemek için tıklama noktasını kaydeder."""
        if event.button() == Qt.MouseButton.LeftButton:
            win = self.window()
            if win and not win.isMaximized():
                # Pencere normal moddaysa sürüklemeye izin ver
                self._drag_pos = event.globalPosition().toPoint() - win.pos()
                event.accept()

    def mouseMoveEvent(self, event):
        """Fare basılı tutularak hareket ettirildiğinde pencereyi taşır."""
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            win = self.window()
            if win and not win.isMaximized():
                win.move(event.globalPosition().toPoint() - self._drag_pos)
                event.accept()

    def mouseReleaseEvent(self, event):
        """Tıklama bırakıldığında sürükleme konumunu temizler."""
        self._drag_pos = QPoint()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Başlık çubuğuna çift tıklandığında pencereyi büyütür veya normale döndürür."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._maximize_restore_window()
            event.accept()
