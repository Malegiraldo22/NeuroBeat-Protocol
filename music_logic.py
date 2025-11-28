import os
import re
import shutil
import platform
import subprocess
# Librerías externas
try:
    import mutagen
    from mutagen.easyid3 import EasyID3
    from mutagen.flac import FLAC
    from send2trash import send2trash
except ImportError:
    print("Error: Faltan librerías. Ejecuta: pip install mutagen send2trash")
    exit()

class MusicLogic:
    def __init__(self):
        self.music_files = [] 
        self.duplicates_groups = []
        self.metadata_fixes = []
        self.cancel_scan = False

    def get_supported_extensions(self):
        return ('.mp3', '.flac', '.ogg', '.wav', '.m4a')

    def scan_folder(self, folder_path, progress_callback=None):
        """
        Escanea la carpeta.
        progress_callback: función que acepta (progreso_actual, total, texto_estado)
        """
        self.music_files = []
        self.metadata_fixes = []
        paths = []
        
        # 1. Recolectar archivos
        for r, d, f in os.walk(folder_path):
            for file in f:
                if file.lower().endswith(self.get_supported_extensions()):
                    paths.append(os.path.join(r, file))
        
        total = len(paths)
        
        # 2. Procesar Metadata
        files_data = []
        for i, path in enumerate(paths):
            if self.cancel_scan: break
            
            # Notificar progreso a la UI si existe callback
            if progress_callback and i % 5 == 0:
                progress_callback(i, total, f"Analizando: {os.path.basename(path)}")
            
            meta = self._read_metadata(path)
            files_data.append(meta)
            
            # Inferencia de etiquetas
            fix = self._infer_metadata(meta)
            if fix:
                self.metadata_fixes.append(fix)

        # 3. Ordenar (Artista -> Album -> Titulo)
        files_data.sort(key=lambda x: (x['artist'].lower(), x['album'].lower(), x['title'].lower()))
        self.music_files = files_data
        
        # 4. Detectar Duplicados
        self._analyze_duplicates()
        
        return len(self.music_files)

    def _read_metadata(self, path):
        data = {
            "path": path, 
            "filename": os.path.basename(path),
            "artist": "Desconocido", 
            "album": "Desconocido", 
            "title": os.path.basename(path), 
            "album_artist": None, 
            "bitrate": 0
        }
        try:
            audio = mutagen.File(path, easy=True)
            if audio:
                data['artist'] = audio.get('artist', ['Desconocido'])[0]
                data['album'] = audio.get('album', ['Desconocido'])[0]
                data['title'] = audio.get('title', [os.path.basename(path)])[0]
                data['album_artist'] = audio.get('albumartist', [None])[0]
                
                if hasattr(audio, 'info') and hasattr(audio.info, 'bitrate'):
                    data['bitrate'] = int(audio.info.bitrate / 1000)
        except Exception:
            pass # Si falla, se queda con los valores por defecto
        return data

    def _infer_metadata(self, meta):
        """Devuelve un objeto 'fix' si encuentra una sugerencia, o None"""
        if not meta['artist'] or meta['artist'].lower() in ["desconocido", "unknown", ""]:
            suggested = None
            source = ""
            
            # A: Album Artist
            if meta['album_artist'] and meta['album_artist'].lower() not in ["", "desconocido"]:
                suggested = meta['album_artist']
                source = "Tag: Album Artist"
            
            # B: Carpeta
            if not suggested:
                parent = os.path.basename(os.path.dirname(meta['path']))
                if parent.lower() not in ["music", "musica", "cd1", "downloads"]:
                    suggested = parent
                    source = "Carpeta"

            if suggested:
                return {
                    "path": meta['path'],
                    "filename": meta['filename'],
                    "current": meta['artist'],
                    "suggested": suggested,
                    "source": source
                }
        return None

    def _analyze_duplicates(self):
        groups = {}
        for s in self.music_files:
            # Normalización para comparar
            k_art = re.sub(r'[^a-zA-Z0-9]', '', s['artist']).lower()
            k_tit = re.sub(r'[^a-zA-Z0-9]', '', s['title']).lower()
            key = (k_art, k_tit)
            
            if key not in groups: groups[key] = []
            groups[key].append(s)
        
        self.duplicates_groups = []
        for k, songs in groups.items():
            if len(songs) > 1:
                # Ordenar: Mayor Bitrate primero
                songs.sort(key=lambda x: x['bitrate'], reverse=True)
                self.duplicates_groups.append(songs)

    def update_tag_artist(self, path, new_artist):
        """Escribe el cambio en el archivo físico"""
        try:
            if path.endswith(".mp3"):
                audio = EasyID3(path)
            elif path.endswith(".flac"):
                audio = FLAC(path)
            else:
                return False # No soportado aun
            
            audio['artist'] = new_artist
            audio.save()
            return True
        except Exception as e:
            print(f"Error logic update: {e}")
            return False

    def recycle_files(self, paths_list):
        """Envía una lista de rutas a la papelera"""
        count = 0
        for path in paths_list:
            if os.path.exists(path):
                try:
                    send2trash(path)
                    count += 1
                except Exception as e:
                    print(f"Error reciclando {path}: {e}")
        return count

    def open_file_system(self, path):
        """Abre el archivo con el reproductor del sistema"""
        try:
            if platform.system() == 'Windows': os.startfile(path)
            elif platform.system() == 'Darwin': subprocess.call(('open', path))
            else: subprocess.call(('xdg-open', path))
        except: pass