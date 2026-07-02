# -*- coding: utf-8 -*-
"""
BrainDump — Ortak Yardımcı Fonksiyonlar (utils.py)
Tarih formatlama, dil dönüşümleri ve dosya yolları için merkezi yardımcı sınıf.
"""

import sys
import os
from datetime import datetime

# Uygulama Sürüm Bilgisi (Merkezi)
APP_VERSION = "v0.1.0"

def get_categories() -> list[str]:
    """QSettings üzerinden dinamik kategorileri yükler. Boşsa varsayılan listeyi döndürür."""
    from PyQt6.QtCore import QSettings
    settings = QSettings("BrainDump", "BrainDump")
    saved = settings.value("custom_categories", None)
    if saved is None:
        default_cats = ["Genel", "İş", "Kişisel", "Proje", "Fikir"]
        settings.setValue("custom_categories", default_cats)
        return default_cats
    if isinstance(saved, str):
        return [saved]
    return list(saved)

class DynamicCategories(list):
    """Dynamic list class that delegates to QSettings categories."""
    def __iter__(self):
        return iter(get_categories())
    def __len__(self):
        return len(get_categories())
    def __getitem__(self, index):
        return get_categories()[index]
    def __add__(self, other):
        return get_categories() + other
    def __radd__(self, other):
        return other + get_categories()

CATEGORIES = DynamicCategories()

def get_asset_path(relative_path: str) -> str:
    """Asset dosyasının mutlak yolunu döndürür (PyInstaller uyumlu)."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        # core/ klasörünün bir üst dizini (proje kök dizini)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def parse_turkish_date(date_str: str) -> datetime:
    """
    Türkçe ay içeren tarihleri (örn: '29 Haz 2026' veya '2 Tem 2026') datetime nesnesine dönüştürür.
    Zaten ISO formatındaysa veya datetime nesnesiyse ona göre işler.
    """
    if not date_str:
        return None
        
    if isinstance(date_str, datetime):
        return date_str
        
    # ISO 8601 formatı ise (örn: 2026-06-29 veya 2026-06-29T12:00:00)
    try:
        if "T" in date_str:
            return datetime.fromisoformat(date_str)
        else:
            return datetime.strptime(date_str.split()[0], "%Y-%m-%d")
    except ValueError:
        pass

    # Türkçe ay isimleri dönüşüm haritası
    turkish_months = {
        "Oca": "Jan", "Şub": "Feb", "Mar": "Mar", "Nis": "Apr",
        "May": "May", "Haz": "Jun", "Tem": "Jul", "Ağu": "Aug",
        "Eyl": "Sep", "Eki": "Oct", "Kas": "Nov", "Ara": "Dec"
    }
    
    try:
        temp_str = date_str
        for tr, eng in turkish_months.items():
            temp_str = temp_str.replace(tr, eng)
        return datetime.strptime(temp_str, "%d %b %Y")
    except Exception:
        return None

def format_date_tr(dt_or_str) -> str:
    """
    Verilen datetime nesnesi veya ISO tarih stringini Türkçe formatta (örn: '29 Haz 2026') döndürür.
    """
    if not dt_or_str:
        return "Bilinmeyen Tarih"
        
    dt = dt_or_str
    if isinstance(dt_or_str, str):
        dt = parse_turkish_date(dt_or_str)
        if not dt:
            return dt_or_str  # Dönüştürülemiyorsa aynen döndür

    turkish_months_short = [
        "", "Oca", "Şub", "Mar", "Nis", "May", "Haz",
        "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"
    ]
    
    try:
        return f"{dt.day} {turkish_months_short[dt.month]} {dt.year}"
    except Exception:
        return str(dt_or_str)
