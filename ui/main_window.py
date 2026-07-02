"""
BrainDump — Ana Pencere (MainWindow)
QMainWindow alt sınıfı. Sidebar + QStackedWidget yapısı.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QStatusBar, QLabel,
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QPoint, QRect
)
from PyQt6.QtGui import QFont, QShortcut, QKeySequence

from ui.sidebar import Sidebar
from ui.widgets.dashboard_page import DashboardPage
from ui.widgets.new_note_page import NewNotePage
from ui.widgets.notes_page import NotesPage
from ui.widgets.goals_page import GoalsPage
from ui.widgets.stats_page import StatsPage
from ui.widgets.settings_page import SettingsPage
from ui.widgets.title_bar import TitleBar


class MainWindow(QMainWindow):
    """
    BrainDump ana penceresi.
    Üst: Özel başlık çubuğu (TitleBar)
    Sol: Daraltılabilir sidebar
    Sağ: QStackedWidget ile sayfa geçişi
    Alt: Minimal status bar
    """

    APP_TITLE = "BrainDump"
    APP_VERSION = "v0.1.0"
    DEFAULT_WIDTH = 1200
    DEFAULT_HEIGHT = 800
    MIN_WIDTH = 900
    MIN_HEIGHT = 600
    BORDER_WIDTH = 6  # Boyutlandırma için kenar genişliği

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.APP_TITLE)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.resize(self.DEFAULT_WIDTH, self.DEFAULT_HEIGHT)

        # Kenarlıksız pencere bayrağı
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setMouseTracking(True)

        # Boyutlandırma yönü takip değişkeni
        self._resize_direction = None
        self._drag_pos = QPoint()
        self._window_rect = QRect()

        # Pencereyi ekranın ortasına konumlandır
        self._center_on_screen()

        # Arayüzü oluştur
        self._setup_ui()

    def _center_on_screen(self):
        """Pencereyi ekranın ortasına konumlandırır."""
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.DEFAULT_WIDTH) // 2
            y = (screen_geometry.height() - self.DEFAULT_HEIGHT) // 2
            self.move(x, y)

    def _setup_ui(self):
        """Ana arayüz yapısını oluşturur."""
        # Merkezi widget
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        self.setCentralWidget(central_widget)

        # Ana dikey layout: Başlık Çubuğu + İçerik Bölümü
        window_layout = QVBoxLayout(central_widget)
        window_layout.setContentsMargins(1, 1, 1, 1)  # 1px dış çerçeve çizgisi için boşluk
        window_layout.setSpacing(0)

        # --- Özel Başlık Çubuğu ---
        self._title_bar = TitleBar(self)
        window_layout.addWidget(self._title_bar)

        # Yatay içerik alanı layout'u: Sidebar (sol) + İçerik (sağ)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        window_layout.addLayout(main_layout)

        # --- Sidebar ---
        self._sidebar = Sidebar()
        self._sidebar.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self._sidebar)

        # --- İçerik Alanı (QStackedWidget) ---
        content_wrapper = QWidget()
        content_wrapper.setObjectName("content_area")
        content_layout = QHBoxLayout(content_wrapper)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._stacked_widget = QStackedWidget()
        content_layout.addWidget(self._stacked_widget)

        main_layout.addWidget(content_wrapper, 1)  # stretch=1 ile genişlesin

        # --- Sayfaları Ekle ---
        dashboard = DashboardPage()
        dashboard.page_requested.connect(self._on_dashboard_page_requested)

        new_note = NewNotePage()
        new_note.note_saved.connect(self._on_note_saved)
        new_note.cancel_clicked.connect(self._on_note_cancelled)

        self._pages = [
            dashboard,
            new_note,
            NotesPage(),
            GoalsPage(),
            StatsPage(),
            SettingsPage(),
        ]

        for page in self._pages:
            self._stacked_widget.addWidget(page)

        # İlk sayfa: Dashboard
        self._stacked_widget.setCurrentIndex(0)
        self._current_page_index = 0

        # --- Klavye Kısayolları ---
        self._setup_shortcuts()

    def _on_page_changed(self, index: int):
        """Sidebar'dan gelen sayfa değişikliği sinyalini işler."""
        if index == self._current_page_index:
            return

        # Yeni sayfayı getir
        new_page = self._pages[index]
        old_page = self._pages[self._current_page_index]

        # Sayfa verilerini dinamik olarak yenile
        if hasattr(new_page, "load_stats"):
            new_page.load_stats()
        elif hasattr(new_page, "load_notes"):
            new_page.load_notes()
        elif hasattr(new_page, "load_goals"):
            new_page.load_goals()
        elif hasattr(new_page, "load_dashboard"):
            new_page.load_dashboard()

        # Geçiş yönünü belirle (yukarı/aşağı)
        direction = 1 if index > self._current_page_index else -1

        # Animasyonlu geçiş
        self._animate_page_transition(old_page, new_page, direction)

        self._stacked_widget.setCurrentIndex(index)
        self._current_page_index = index

    def _animate_page_transition(self, old_page: QWidget, new_page: QWidget, direction: int):
        """Sayfa geçişi animasyonu — slide efekti."""
        # Slide-up/down animasyonu
        slide_anim = QPropertyAnimation(new_page, b"pos")
        slide_anim.setDuration(240)
        slide_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Sayfanın orijinal konumunu al (stacked widget içindeki koordinatlar)
        orig_pos = new_page.pos()
        dy = 20 if direction > 0 else -20
        slide_anim.setStartValue(QPoint(orig_pos.x(), orig_pos.y() + dy))
        slide_anim.setEndValue(orig_pos)

        # Paralel animasyon grubu (gelecekte ekleme yapılabilmesi için yapıyı koruyoruz)
        anim_group = QParallelAnimationGroup(self)
        anim_group.addAnimation(slide_anim)

        # Animasyon tamamlandığında konumu sabitle
        def on_finished():
            new_page.move(orig_pos)

        anim_group.finished.connect(on_finished)
        anim_group.start()

        # Animasyonu referans olarak sakla (garbage collection önlemi)
        self._current_animation = anim_group

    def _on_dashboard_page_requested(self, index: int):
        """Dashboard'daki eylem kartlarından gelen sayfa geçiş taleplerini işler."""
        self._sidebar.set_current_index(index)
        self._on_page_changed(index)

    def _on_note_saved(self):
        """Not başarıyla kaydedildiğinde Notlar sayfasına geçiş yapar ve listeyi yeniler."""
        notes_page = self._pages[2]
        if hasattr(notes_page, "load_notes"):
            notes_page.load_notes()
        self._sidebar.set_current_index(2)
        self._on_page_changed(2)

    def _on_note_cancelled(self):
        """Not yazma iptal edildiğinde ana panele (Dashboard) geçiş yapar."""
        self._sidebar.set_current_index(0)
        self._on_page_changed(0)

    # --- Kenardan Boyutlandırma (Edge Resize) İşlemleri ---

    def _get_resize_direction(self, pos):
        """Fare koordinatlarına göre boyutlandırma yönünü belirler."""
        w = self.width()
        h = self.height()
        b = self.BORDER_WIDTH
        
        x = pos.x()
        y = pos.y()
        
        direction = []
        
        if x < b:
            direction.append("left")
        elif x > w - b:
            direction.append("right")
            
        if y < b:
            direction.append("top")
        elif y > h - b:
            direction.append("bottom")
            
        return "-".join(direction) if direction else None

    def _update_cursor(self, direction):
        """Boyutlandırma yönüne göre fare imlecini günceller."""
        if not direction:
            self.unsetCursor()
            return
            
        if direction in ("left", "right"):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif direction in ("top", "bottom"):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif direction in ("top-left", "bottom-right"):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif direction in ("top-right", "bottom-left"):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)

    def mousePressEvent(self, event):
        """Fare tıklandığında boyutlandırma başlangıç koordinatlarını kaydeder."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()
            self._window_rect = self.geometry()
            self._resize_direction = self._get_resize_direction(event.position().toPoint())
            if self._resize_direction:
                event.accept()
            else:
                super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Fare hareket ettikçe pencere boyutunu dinamik olarak günceller veya imleci değiştirir."""
        pos = event.position().toPoint()
        
        # Eğer bir boyutlandırma işlemi aktif değilse, sadece kenarlarda imleci güncelle
        if event.buttons() == Qt.MouseButton.NoButton:
            direction = self._get_resize_direction(pos)
            self._update_cursor(direction)
            super().mouseMoveEvent(event)
            return

        if self._resize_direction and not self.isMaximized():
            delta = event.globalPosition().toPoint() - self._drag_pos
            rect = QRect(self._window_rect)
            
            # Yatay boyutlandırma
            if "left" in self._resize_direction:
                new_width = rect.width() - delta.x()
                if new_width >= self.minimumWidth():
                    rect.setLeft(rect.left() + delta.x())
            elif "right" in self._resize_direction:
                new_width = rect.width() + delta.x()
                if new_width >= self.minimumWidth():
                    rect.setRight(rect.right() + delta.x())
                    
            # Dikey boyutlandırma
            if "top" in self._resize_direction:
                new_height = rect.height() - delta.y()
                if new_height >= self.minimumHeight():
                    rect.setTop(rect.top() + delta.y())
            elif "bottom" in self._resize_direction:
                new_height = rect.height() + delta.y()
                if new_height >= self.minimumHeight():
                    rect.setBottom(rect.bottom() + delta.y())
                    
            self.setGeometry(rect)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Fare tıklaması bırakıldığında boyutlandırma modunu kapatır."""
        self._resize_direction = None
        self.unsetCursor()
        super().mouseReleaseEvent(event)

    def _setup_shortcuts(self):
        """Uygulama genelindeki klavye kısayollarını tanımlar."""
        # Dashboard: Ctrl+D
        self.shortcut_dashboard = QShortcut(QKeySequence("Ctrl+D"), self)
        self.shortcut_dashboard.activated.connect(lambda: self._switch_to_page(0))
        
        # Yeni Not: Ctrl+N
        self.shortcut_new_note = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new_note.activated.connect(lambda: self._switch_to_page(1))
        
        # Notlarım: Ctrl+L
        self.shortcut_notes = QShortcut(QKeySequence("Ctrl+L"), self)
        self.shortcut_notes.activated.connect(lambda: self._switch_to_page(2))
        
        # Hedeflerim: Ctrl+H
        self.shortcut_goals = QShortcut(QKeySequence("Ctrl+H"), self)
        self.shortcut_goals.activated.connect(lambda: self._switch_to_page(3))
        
        # İstatistikler: Ctrl+I
        self.shortcut_stats = QShortcut(QKeySequence("Ctrl+I"), self)
        self.shortcut_stats.activated.connect(lambda: self._switch_to_page(4))
        
        # Ayarlar: Ctrl+Comma
        self.shortcut_settings = QShortcut(QKeySequence("Ctrl+,"), self)
        self.shortcut_settings.activated.connect(lambda: self._switch_to_page(5))
        
        # Esc tuşu ile kapatma/iptal
        self.shortcut_escape = QShortcut(QKeySequence("Escape"), self)
        self.shortcut_escape.activated.connect(self._on_escape_pressed)

    def _switch_to_page(self, index: int):
        """Sidebar'ı tetikleyerek sayfaya geçiş yapar."""
        self._sidebar.set_current_index(index)
        self._on_page_changed(index)

    def _on_escape_pressed(self):
        """Escape tuşu basıldığında detay pencerelerini veya Yeni Not sayfasını kapatır."""
        if self._current_page_index == 1:
            new_note_page = self._pages[1]
            if hasattr(new_note_page, "_on_cancel_clicked"):
                new_note_page._on_cancel_clicked()



