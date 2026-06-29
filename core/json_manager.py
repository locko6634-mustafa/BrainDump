# -*- coding: utf-8 -*-
"""
JSON tabanlı veri yönetim modülü (JSONManager).
Notların ve hedeflerin JSON dosyalarında saklanmasını, okunmasını ve yönetilmesini sağlar.
"""

import json
import os
import uuid
from datetime import datetime


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

    def _init_files(self):
        """Dosyalar mevcut değilse boş listelerle veya demo verileriyle başlatır."""
        # Notlar dosyası yoksa varsayılan notlarla oluştur
        if not os.path.exists(self.notes_file):
            demo_notes = [
                {
                    "id": str(uuid.uuid4()),
                    "title": "Proje Planı",
                    "content": "Yeni projenin genel yapısı ve zaman çizelgesi hakkında notlar.",
                    "date": "12 Haz 2025",
                    "category": "İş",
                    "tags": ["proje", "plan", "iş"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Toplantı Notları",
                    "content": "Haftalık ekip toplantısında alınan kararlar ve görev dağılımı.",
                    "date": "15 Haz 2025",
                    "category": "Kişisel",
                    "tags": ["toplantı", "ekip"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Alışveriş Listesi",
                    "content": "Haftalık market alışverişi için gerekli ürünlerin listesi.",
                    "date": "18 Haz 2025",
                    "category": "Proje",
                    "tags": ["market", "kişisel"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Kitap Özetleri",
                    "content": "Okuduğum kitapların kısa özetleri ve önemli alıntılar.",
                    "date": "20 Haz 2025",
                    "category": "Fikir",
                    "tags": ["kitap", "okuma", "fikir"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Fikir Tahtası",
                    "content": "Yeni proje fikirleri ve beyin fırtınası sonuçları.",
                    "date": "23 Haz 2025",
                    "category": "Genel",
                    "tags": ["fikir", "proje"]
                },
                {
                    "id": str(uuid.uuid4()),
                    "title": "Haftalık Özet",
                    "content": "Bu haftanın özeti: tamamlanan görevler ve gelecek planlar.",
                    "date": "25 Haz 2025",
                    "category": "İş",
                    "tags": ["haftalık", "rapor", "iş"]
                }
            ]
            self._write_json(self.notes_file, demo_notes)

        # Hedefler dosyası yoksa varsayılan hedeflerle oluştur
        if not os.path.exists(self.goals_file):
            demo_goals = [
                {"id": str(uuid.uuid4()), "text": "Proje raporunu tamamla", "completed": True, "period": "daily", "progress": 1, "total_progress": 1},
                {"id": str(uuid.uuid4()), "text": "E-postaları yanıtla", "completed": True, "period": "daily", "progress": 1, "total_progress": 1},
                {"id": str(uuid.uuid4()), "text": "Spor yap (30 dk)", "completed": False, "period": "daily", "progress": 0, "total_progress": 1},
                {"id": str(uuid.uuid4()), "text": "Kitap oku (20 sayfa)", "completed": False, "period": "weekly", "progress": 5, "total_progress": 20},
                {"id": str(uuid.uuid4()), "text": "Yeni not al", "completed": False, "period": "weekly", "progress": 0, "total_progress": 1},
                {"id": str(uuid.uuid4()), "text": "Günlük özet yaz", "completed": False, "period": "monthly", "progress": 12, "total_progress": 30}
            ]
            self._write_json(self.goals_file, demo_goals)

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
        """Yeni bir not ekler."""
        if tags is None:
            tags = []
        if not date:
            ay_isimleri = [
                "", "Oca", "Şub", "Mar", "Nis", "May", "Haz",
                "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"
            ]
            bugun = datetime.now()
            date = f"{bugun.day} {ay_isimleri[bugun.month]} {bugun.year}"

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

    # --- HEDEF İŞLEMLERİ ---

    def get_all_goals(self):
        """Tüm hedefleri listeler."""
        return self._read_json(self.goals_file)

    def add_goal(self, text, completed=False, period="daily", progress=0, total_progress=1):
        """Yeni bir hedef ekler."""
        goals = self.get_all_goals()
        new_goal = {
            "id": str(uuid.uuid4()),
            "text": text,
            "completed": completed,
            "period": period,
            "progress": progress,
            "total_progress": total_progress
        }
        goals.append(new_goal)
        self._write_json(self.goals_file, goals)
        return new_goal

    def update_goal_status(self, goal_id, completed):
        """Bir hedefin tamamlanma durumunu günceller."""
        goals = self.get_all_goals()
        updated = False
        for g in goals:
            if g["id"] == goal_id:
                g["completed"] = completed
                # Eğer tamamlandıysa progress'i total_progress yapalım, tamamlanmadıysa 0 yapalım
                if completed:
                    g["progress"] = g.get("total_progress", 1)
                else:
                    g["progress"] = 0
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
        for g in goals:
            if g["id"] == goal_id:
                for key, val in kwargs.items():
                    g[key] = val
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
                return True
            return False
        except Exception as e:
            print(f"[HATA] Yedek yüklenemedi: {e}")
            return False
