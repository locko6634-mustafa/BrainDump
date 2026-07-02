# -*- coding: utf-8 -*-
"""
JSON tabanlı veri yönetim modülü (JSONManager).
Notların ve hedeflerin JSON dosyalarında saklanmasını, okunmasını ve yönetilmesini sağlar.
Tarihleri ISO 8601 formatında saklar ve veri göçü (migration) gerçekleştirir.
"""

import json
import os
import uuid
from datetime import datetime
from core.utils import parse_turkish_date


class JSONManager:
    """Notlar ve hedefler için JSON dosya tabanlı veri depolama yöneticisi."""

    def __init__(self, data_dir=None):
        if data_dir is None:
            # Proje ana dizinindeki 'data' klasörünü varsayılan olarak kullan
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.data_dir = os.path.join(base_dir, "data")
        else:
            self.data_dir = data_dir

        os.makedirs(self.data_dir, exist_ok=True)

        self.notes_file = os.path.join(self.data_dir, "notes.json")
        self.goals_file = os.path.join(self.data_dir, "goals.json")

        self._init_files()
        self._migrate_data()

    def _init_files(self):
        """Dosyalar mevcut değilse boş listelerle veya demo verileriyle başlatır."""
        # Notlar dosyası yoksa varsayılan notlarla oluştur (ISO formatında)
        if not os.path.exists(self.notes_file):
            demo_notes = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Proje Planı",
                    "content": "Yeni projenin genel yapısı ve zaman çizelgesi hakkında notlar.",
                    "date": "2025-06-12",
                    "category": "İş",
                    "tags": ["proje", "plan", "iş"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Toplantı Notları",
                    "content": "Haftalık ekip toplantısında alınan kararlar ve görev dağılımı.",
                    "date": "2025-06-15",
                    "category": "Kişisel",
                    "tags": ["toplantı", "ekip"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Alışveriş Listesi",
                    "content": "Haftalık market alışverişi için gerekli ürünlerin listesi.",
                    "date": "2025-06-18",
                    "category": "Proje",
                    "tags": ["market", "kişisel"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Kitap Özetleri",
                    "content": "Okuduğum kitapların kısa özetleri ve önemli alıntılar.",
                    "date": "2025-06-20",
                    "category": "Fikir",
                    "tags": ["kitap", "okuma", "fikir"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Fikir Tahtası",
                    "content": "Yeni proje fikirleri ve beyin fırtınası sonuçları.",
                    "date": "2025-06-23",
                    "category": "Genel",
                    "tags": ["fikir", "proje"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Haftalık Özet",
                    "content": "Bu haftanın özeti: tamamlanan görevler ve gelecek planlar.",
                    "date": "2025-06-25",
                    "category": "İş",
                    "tags": ["haftalık", "rapor", "iş"]
                }
            ]
            self._write_json(self.notes_file, demo_notes)

        # Hedefler dosyası yoksa varsayılan hedeflerle oluştur
        if not os.path.exists(self.goals_file):
            now_iso = datetime.now().date().isoformat()
            demo_goals = [
                {"id": str(uuid.uuid4()), "text": "Proje raporunu tamamla", "completed": True, "period": "daily", "progress": 1, "total_progress": 1, "created_at": now_iso, "completed_at": now_iso},
                {"id": str(uuid.uuid4()), "text": "E-postaları yanıtla", "completed": True, "period": "daily", "progress": 1, "total_progress": 1, "created_at": now_iso, "completed_at": now_iso},
                {"id": str(uuid.uuid4()), "text": "Spor yap (30 dk)", "completed": False, "period": "daily", "progress": 0, "total_progress": 1, "created_at": now_iso, "completed_at": None},
                {"id": str(uuid.uuid4()), "text": "Kitap oku (20 sayfa)", "completed": False, "period": "weekly", "progress": 5, "total_progress": 20, "created_at": now_iso, "completed_at": None},
                {"id": str(uuid.uuid4()), "text": "Yeni not al", "completed": False, "period": "weekly", "progress": 0, "total_progress": 1, "created_at": now_iso, "completed_at": None},
                {"id": str(uuid.uuid4()), "text": "Günlük özet yaz", "completed": False, "period": "monthly", "progress": 12, "total_progress": 30, "created_at": now_iso, "completed_at": None}
            ]
            self._write_json(self.goals_file, demo_goals)

    def _migrate_data(self):
        """Notlar ve hedeflerdeki eski Türkçe tarih verilerini ISO 8601 formatına çevirir."""
        # 1. Notlar Migration'ı
        notes = self.get_all_notes()
        notes_updated = False
        for n in notes:
            d = n.get("date")
            if d:
                # ISO 8601 tarih kontrolü (YYYY-MM-DD veya YYYY-MM-DDTHH:MM:SS)
                try:
                    # Zaten ISO formatındaysa parse_turkish_date doğru datetime döndürecektir
                    # ama biz biçimini YYYY-MM-DD yapmayı garanti edelim
                    parsed = parse_turkish_date(d)
                    if parsed:
                        iso_date = parsed.strftime("%Y-%m-%d")
                        if d != iso_date:
                            n["date"] = iso_date
                            notes_updated = True
                except Exception as e:
                    print(f"[UYARI] Tarih dönüştürülemedi: {d}, Hata: {e}")
        if notes_updated:
            self._write_json(self.notes_file, notes)

        # 2. Hedefler Migration'ı
        goals = self.get_all_goals()
        goals_updated = False
        now_iso = datetime.now().date().isoformat()
        for g in goals:
            # created_at ve completed_at alanları yoksa ekle
            if "created_at" not in g:
                g["created_at"] = now_iso
                goals_updated = True
            if g.get("completed", False):
                if "completed_at" not in g or g["completed_at"] is None:
                    g["completed_at"] = now_iso
                    goals_updated = True
            else:
                if g.get("completed_at") is not None:
                    g["completed_at"] = None
                    goals_updated = True
        if goals_updated:
            self._write_json(self.goals_file, goals)

    def _read_json(self, filepath):
        """Verilen JSON dosyasını okur."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[HATA] Dosya okunamadı {filepath}: {e}")
            return []

    def _write_json(self, filepath, data):
        """Verileri JSON formatında dosyaya yazar."""
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"[HATA] Dosyaya yazılamadı {filepath}: {e}")
            return False

    # --- NOT İŞLEMLERİ (CRUD) ---

    def get_all_notes(self):
        """Tüm notları listeler."""
        return self._read_json(self.notes_file)

    def add_note(self, title, content, category, tags=None, date=None):
        """Yeni bir not ekler. Tarih belirtilmezse varsayılan ISO 8601 olarak kaydeder."""
        if tags is None:
            tags = []
        if not date:
            date = datetime.now().date().isoformat()
        else:
            # Gelen tarih Türkçe veya başka bir biçimdeyse ISO formatına çevirip kaydet
            parsed = parse_turkish_date(date)
            if parsed:
                date = parsed.strftime("%Y-%m-%d")

        notes = self.get_all_notes()
        new_note = {
            "id": str(uuid.uuid4()),
            "title": title,
            "content": content,
            "category": category,
            "tags": tags,
            "date": date
        }
        notes.append(new_note)
        self._write_json(self.notes_file, notes)
        return new_note

    def update_note(self, note_id, title, content, category, tags=None):
        """Mevcut bir notu günceller."""
        notes = self.get_all_notes()
        updated = False
        for n in notes:
            if n["id"] == note_id:
                n["title"] = title
                n["content"] = content
                n["category"] = category
                if tags is not None:
                    n["tags"] = tags
                updated = True
                break
        if updated:
            self._write_json(self.notes_file, notes)
            return True
        return False

    def delete_note(self, note_id):
        """Bir notu siler."""
        notes = self.get_all_notes()
        filtered_notes = [n for n in notes if n["id"] != note_id]
        if len(notes) != len(filtered_notes):
            self._write_json(self.notes_file, filtered_notes)
            return True
        return False

    def update_note_pin(self, note_id, is_pinned):
        """Notun sabitleme durumunu günceller."""
        notes = self.get_all_notes()
        updated = False
        for n in notes:
            if n["id"] == note_id:
                n["is_pinned"] = is_pinned
                updated = True
                break
        if updated:
            self._write_json(self.notes_file, notes)
            return True
        return False

    # --- HEDEF İŞLEMLERİ ---

    def get_all_goals(self):
        """Tüm hedefleri listeler."""
        return self._read_json(self.goals_file)

    def add_goal(self, text, completed=False, period="daily", progress=0, total_progress=1):
        """Yeni bir hedef ekler. Zaman damgalarını barındırır."""
        goals = self.get_all_goals()
        now_iso = datetime.now().date().isoformat()
        new_goal = {
            "id": str(uuid.uuid4()),
            "text": text,
            "completed": completed,
            "period": period,
            "progress": progress,
            "total_progress": total_progress,
            "created_at": now_iso,
            "completed_at": now_iso if completed else None
        }
        goals.append(new_goal)
        self._write_json(self.goals_file, goals)
        return new_goal

    def update_goal_status(self, goal_id, completed):
        """Bir hedefin tamamlanma durumunu ve completed_at zamanını günceller."""
        goals = self.get_all_goals()
        updated = False
        now_iso = datetime.now().date().isoformat()
        for g in goals:
            if g["id"] == goal_id:
                g["completed"] = completed
                if completed:
                    g["progress"] = g.get("total_progress", 1)
                    g["completed_at"] = now_iso
                else:
                    g["progress"] = 0
                    g["completed_at"] = None
                updated = True
                break
        if updated:
            self._write_json(self.goals_file, goals)
            return True
        return False

    def update_goal(self, goal_id, **kwargs):
        """Bir hedefin belirtilen tüm alanlarını günceller."""
        goals = self.get_all_goals()
        updated = False
        now_iso = datetime.now().date().isoformat()
        for g in goals:
            if g["id"] == goal_id:
                for key, val in kwargs.items():
                    g[key] = val
                
                # Eğer completed değiştiyse tamamlanma zamanını yönet
                if "completed" in kwargs:
                    if kwargs["completed"]:
                        g["completed_at"] = now_iso
                    else:
                        g["completed_at"] = None
                updated = True
                break
        if updated:
            self._write_json(self.goals_file, goals)
            return True
        return False

    def delete_goal(self, goal_id):
        """Bir hedefi siler."""
        goals = self.get_all_goals()
        filtered_goals = [g for g in goals if g["id"] != goal_id]
        if len(goals) != len(filtered_goals):
            self._write_json(self.goals_file, filtered_goals)
            return True
        return False

    # --- YEDEKLEME VE DIŞA/İÇE AKTARMA ---

    def export_backup(self, export_path):
        """Tüm notları ve hedefleri içeren bir yedek JSON dosyası oluşturur."""
        try:
            backup_data = {
                "notes": self.get_all_notes(),
                "goals": self.get_all_goals()
            }
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"[HATA] Yedek aktarılamadı: {e}")
            return False

    def import_backup(self, import_path):
        """Verilen yedek JSON dosyasını okuyarak veritabanını geri yükler."""
        try:
            with open(import_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            
            if isinstance(backup_data, dict) and "notes" in backup_data and "goals" in backup_data:
                self._write_json(self.notes_file, backup_data["notes"])
                self._write_json(self.goals_file, backup_data["goals"])
                # Import sonrası verilerin ISO göçünü yap
                self._migrate_data()
                return True
            return False
        except Exception as e:
            print(f"[HATA] Yedek yüklenemedi: {e}")
            return False
