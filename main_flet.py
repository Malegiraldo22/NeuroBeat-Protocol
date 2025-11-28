import flet as ft
import threading
import os
from music_logic import MusicLogic

# --- PALETA DE COLORES CYBERPUNK ---
CP_BG = "#050505"           # Negro casi absoluto
CP_SURFACE = "#0f0f0f"      # Gris muy oscuro
CP_RED = "#ff003c"          # Rojo Neón (Estilo Samurai/Arasaka)
CP_RED_DIM = "#590015"      # Rojo oscuro
CP_CYAN = "#00f0ff"         # Cyan Neón
CP_YELLOW = "#fcee0a"       # Amarillo Cyberpunk
CP_TEXT = "#e0e0e0"         # Blanco sucio
CP_TEXT_DIM = "#787878"     # Texto secundario
CP_BORDER = "#333333"       # Bordes sutiles

class MusicAppFlet:
    def __init__(self, page: ft.Page):
        self.page = page
        self.logic = MusicLogic()
        self.current_folder = ""
        
        # ESTADO
        self.files_to_delete = set()
        self.btn_delete_all = None 

        # --- CONFIGURACIÓN DE PÁGINA ---
        self.page.title = "NeuroBeat Protocol"
        self.page.padding = 0
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = CP_BG
        self.page.window_width = 1250
        self.page.window_height = 850
        self.page.window_icon = "icon.ico"
        
        # Cargar Fuentes (Google Fonts)
        self.page.fonts = {
            "CyberHeader": "Orbitron",
            "CyberMono": "Roboto Mono",
            "CyberBody": "Rajdhani"
        }
        
        # Tema Global
        self.page.theme = ft.Theme(
            font_family="CyberBody",
            color_scheme=ft.ColorScheme(
                primary=CP_RED,
                background=CP_BG,
                surface=CP_SURFACE,
            )
        )

        self._build_components()
        self._layout()

    def _build_components(self):
        # 1. Botón Seleccionar (Estilo Bloque Rectangular)
        self.btn_select_folder = ft.ElevatedButton(
            "INIT_SYSTEM_SCAN", 
            icon=ft.Icons.TERMINAL,
            style=ft.ButtonStyle(
                color=CP_BG,
                bgcolor=CP_CYAN,
                shape=ft.RoundedRectangleBorder(radius=2), # Esquinas rectas
                text_style=ft.TextStyle(font_family="CyberHeader", weight="bold")
            ),
            height=40,
            on_click=self.pick_folder
        )

        # 2. Tabs
        self.tabs = ft.Tabs(
            selected_index=0,
            animation_duration=200,
            indicator_color=CP_RED,
            label_color=CP_RED,
            label_text_style=ft.TextStyle(font_family="CyberHeader", size=14, weight="bold"),
            unselected_label_color=CP_TEXT_DIM,
            divider_color=CP_BORDER,
            height=50,
            on_change=self.on_tab_change,
            tabs=[
                ft.Tab(text="DATA_LIBRARY", icon=ft.Icons.MEMORY),
                # iconos estándar para asegurar compatibilidad
                ft.Tab(text="CONFLICT_DETECTED", icon=ft.Icons.WARNING_AMBER), 
                ft.Tab(text="METADATA_PATCH", icon=ft.Icons.BUILD),
            ],
        )

        # 3. VISTAS PRINCIPALES

        # --- BIBLIOTECA ---
        self.dt_library = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ARTIST_ID", font_family="CyberHeader", color=CP_RED)),
                ft.DataColumn(ft.Text("ALBUM_KEY", font_family="CyberHeader", color=CP_RED)),
                ft.DataColumn(ft.Text("TRACK_TITLE", font_family="CyberHeader", color=CP_RED)),
                ft.DataColumn(ft.Text("FMT", font_family="CyberHeader", color=CP_CYAN)),
                ft.DataColumn(ft.Text("BITRATE", font_family="CyberHeader", color=CP_CYAN)),
            ],
            heading_row_color=CP_SURFACE,
            heading_row_height=50,
            data_row_min_height=40,
            border=ft.border.all(1, CP_BORDER),
            vertical_lines=ft.border.BorderSide(1, "#111111"),
            horizontal_lines=ft.border.BorderSide(1, "#111111"),
            width=float("inf"),
            column_spacing=20
        )

        # --- DUPLICADOS ---
        self.lv_duplicates = ft.ListView(expand=True, spacing=15, padding=20)
        
        self.btn_delete_all = ft.ElevatedButton(
            "PURGE MARKED (0)", 
            style=ft.ButtonStyle(
                bgcolor=CP_RED,
                color="white",
                shape=ft.RoundedRectangleBorder(radius=2), 
                text_style=ft.TextStyle(font_family="CyberHeader")
            ),
            height=35, 
            on_click=self.delete_all_duplicates,
            disabled=True
        )

        # --- REPARAR ---
        self.dt_fixes = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("FILE_NAME", font_family="CyberHeader")),
                ft.DataColumn(ft.Text("CURRENT_VAL", font_family="CyberHeader")),
                ft.DataColumn(ft.Text("SUGGESTED_VAL [EDIT]", font_family="CyberHeader", color=CP_YELLOW)),
                ft.DataColumn(ft.Text("SOURCE", font_family="CyberHeader")),
                ft.DataColumn(ft.Text("ROOT_PATH", font_family="CyberHeader")),
                ft.DataColumn(ft.Text("EXE", font_family="CyberHeader")),
            ],
            heading_row_color=CP_SURFACE,
            heading_row_height=50,
            data_row_min_height=50,
            border=ft.border.all(1, CP_BORDER),
            width=float("inf"),
            column_spacing=30
        )

        # 4. Estado y Pickers
        self.progress_bar = ft.ProgressBar(width=None, value=0, color=CP_CYAN, bgcolor="#222", visible=False, bar_height=2)
        self.status_text = ft.Text("SYSTEM_READY // WAITING_INPUT...", size=12, color=CP_TEXT_DIM, font_family="CyberMono")

        self.file_picker = ft.FilePicker(on_result=self.on_folder_result)
        self.page.overlay.append(self.file_picker)

    def _layout(self):
        # Cabecera Cyberpunk
        header = ft.Container(
            content=ft.Row(
                [
                    ft.Column([
                        ft.Text("NEUROBEAT", size=28, font_family="CyberHeader", color=CP_YELLOW, weight="bold"),
                        ft.Text("PROTOCOL v5.0", size=12, font_family="CyberMono", color=CP_RED)
                    ], spacing=0),
                    self.btn_select_folder
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            padding=ft.padding.symmetric(horizontal=30, vertical=20),
            bgcolor=CP_BG,
            border=ft.border.only(bottom=ft.BorderSide(1, CP_RED)) 
        )

        self.content_area = ft.Container(
            content=ft.Column([self.dt_library], scroll=ft.ScrollMode.AUTO),
            padding=10,
            expand=True,
            border=ft.border.symmetric(horizontal=ft.BorderSide(1, "#111")) 
        )

        footer = ft.Container(
            content=ft.Column([
                self.progress_bar,
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.SQUARE, size=10, color=CP_RED), # Icono simple
                        self.status_text
                    ], spacing=5),
                    padding=ft.padding.symmetric(horizontal=20, vertical=5)
                )
            ]),
            bgcolor="#080808",
            border=ft.border.only(top=ft.BorderSide(1, CP_BORDER))
        )

        self.page.add(
            header,
            self.tabs,
            self.content_area,
            footer
        )

    # --- LÓGICA ---

    def pick_folder(self, e):
        self.file_picker.get_directory_path()

    def on_folder_result(self, e: ft.FilePickerResultEvent):
        if e.path:
            self.current_folder = e.path
            self.status_text.value = f"TARGET_LOCKED: {e.path}"
            self.status_text.update()
            threading.Thread(target=self.run_scan, daemon=True).start()

    def run_scan(self):
        self.progress_bar.visible = True
        self.progress_bar.update()
        count = self.logic.scan_folder(self.current_folder)
        self.progress_bar.visible = False
        self.status_text.value = f"SCAN_COMPLETE. OBJECTS_FOUND: {count}"
        self.page.update()
        self.refresh_ui()

    def refresh_ui(self):
        # 1. BIBLIOTECA
        self.dt_library.rows.clear()
        
        for song in self.logic.music_files: 
            _, ext = os.path.splitext(song['filename'])
            self.dt_library.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(song['artist'], font_family="CyberBody", weight="bold")),
                    ft.DataCell(ft.Text(song['album'], font_family="CyberBody")),
                    ft.DataCell(ft.Text(song['title'], font_family="CyberBody")),
                    ft.DataCell(ft.Text(ext.upper().replace(".", ""), font_family="CyberMono", color=CP_CYAN, size=12)),
                    ft.DataCell(ft.Text(f"{song['bitrate']} kbps", font_family="CyberMono", size=12)),
                ])
            )
        
        # 2. DUPLICADOS
        self.lv_duplicates.controls.clear()
        self.files_to_delete.clear() 
        
        if self.logic.duplicates_groups:
             self.lv_duplicates.controls.append(
                 ft.Container(
                     content=ft.Row([
                         ft.Text(f"CONFLICTS_DETECTED: {len(self.logic.duplicates_groups)}", color=CP_YELLOW, font_family="CyberHeader"),
                         self.btn_delete_all 
                     ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                     padding=15, 
                     border=ft.border.all(1, CP_RED), 
                     bgcolor=CP_RED_DIM, 
                     border_radius=0 
                 )
             )

        for group in self.logic.duplicates_groups:
            self.lv_duplicates.controls.append(self.create_duplicate_card(group))
        
        self.update_delete_button(refresh_view=False) 

        # 3. REPARAR
        self.dt_fixes.rows.clear()
        for fix in self.logic.metadata_fixes:
            txt_suggested = ft.TextField(
                value=fix['suggested'], 
                text_size=12, height=35, content_padding=10, 
                border_color=CP_BORDER, bgcolor=CP_SURFACE,
                text_style=ft.TextStyle(font_family="CyberMono", color=CP_YELLOW),
                border_radius=0,
                width=200 
            )
            
            path_container = ft.Container(
                content=ft.Text(fix['path'], size=10, color=CP_TEXT_DIM, font_family="CyberMono", no_wrap=False),
                width=300 
            )

            btn_save = ft.IconButton(
                icon=ft.Icons.SAVE, icon_color=CP_CYAN, # Icono simple
                on_click=lambda e, p=fix['path'], txt=txt_suggested: self.save_fix_row(p, txt.value, e.control)
            )

            self.dt_fixes.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(fix['filename'], size=12, weight="bold", font_family="CyberMono")),
                    ft.DataCell(ft.Text(fix['current'], size=12)),
                    ft.DataCell(txt_suggested), 
                    ft.DataCell(ft.Text(fix['source'], size=11, color=CP_CYAN)),
                    ft.DataCell(path_container),
                    ft.DataCell(btn_save),
                ])
            )

        self.page.update()

    # --- LÓGICA VISUAL ---

    def toggle_duplicate_state(self, e, path, icon_ref, label_ref, card_container):
        is_delete = e.control.value 
        
        if is_delete:
            self.files_to_delete.add(path)
            icon_ref.name = ft.Icons.DELETE # Icono simple
            icon_ref.color = CP_RED
            label_ref.value = "PURGE"
            label_ref.color = CP_RED
        else:
            if path in self.files_to_delete:
                self.files_to_delete.remove(path)
            icon_ref.name = ft.Icons.SHIELD # Icono simple
            icon_ref.color = CP_CYAN
            label_ref.value = "SECURE"
            label_ref.color = CP_CYAN
        
        icon_ref.update()
        label_ref.update()
        self.update_delete_button(refresh_view=True)

    def update_delete_button(self, refresh_view=True):
        count = len(self.files_to_delete)
        self.btn_delete_all.text = f"PURGE MARKED ({count})"
        self.btn_delete_all.disabled = (count == 0)
        
        if refresh_view:
            try:
                self.btn_delete_all.update()
            except:
                pass

    # --- GENERADORES ---

    def create_duplicate_card(self, group):
        rows = []
        for i, song in enumerate(group):
            should_delete = (i > 0)
            
            if should_delete:
                self.files_to_delete.add(song['path'])
            
            icon = ft.Icon(
                name=ft.Icons.DELETE if should_delete else ft.Icons.SHIELD,
                color=CP_RED if should_delete else CP_CYAN,
                size=18
            )
            
            label = ft.Text(
                "PURGE" if should_delete else "SECURE",
                size=10, weight="bold", font_family="CyberHeader",
                color=CP_RED if should_delete else CP_CYAN
            )

            switch = ft.Switch(
                value=should_delete, 
                active_color=CP_RED,
                inactive_track_color=CP_SURFACE,
                thumb_color=CP_TEXT,
                on_change=lambda e, p=song['path'], i=icon, l=label: self.toggle_duplicate_state(e, p, i, l, None)
            )

            row = ft.Container(
                content=ft.Column([
                    ft.Row([
                        icon,
                        ft.Text(song['title'], weight="bold", expand=True, font_family="CyberBody", size=16),
                        ft.Container(
                            content=label, 
                            border=ft.border.all(1, CP_RED if should_delete else CP_CYAN), 
                            padding=ft.padding.symmetric(horizontal=8, vertical=2)
                        ),
                        switch
                    ], alignment=ft.MainAxisAlignment.START),
                    
                    ft.Column([
                        ft.Row([
                            ft.Text(f"{song['artist']} // {song['album']}".upper(), size=11, color=CP_TEXT_DIM, font_family="CyberMono"),
                            ft.Text(f"[ {song['bitrate']} KBPS ]", size=11, color=CP_YELLOW, font_family="CyberMono"),
                        ]),
                        ft.Container(
                            content=ft.Text(song['path'], size=10, color=CP_TEXT_DIM, font_family="CyberMono"),
                            bgcolor="#0a0a0a", padding=5, 
                            border=ft.border.only(left=ft.BorderSide(2, CP_BORDER)) 
                        )
                    ], spacing=2)
                ]),
                padding=10,
                border=ft.border.only(bottom=ft.BorderSide(1, "#222")) if i < len(group)-1 else None
            )
            rows.append(row)

        return ft.Container(
            content=ft.Column(rows),
            bgcolor=CP_SURFACE, 
            border=ft.border.all(1, CP_BORDER),
            border_radius=0, 
            padding=0,
            margin=ft.margin.only(bottom=10)
        )

    # --- ACCIONES ---

    def on_tab_change(self, e):
        index = e.control.selected_index
        if index == 0:
            self.content_area.content = ft.Column([self.dt_library], scroll=ft.ScrollMode.AUTO)
        elif index == 1:
            self.content_area.content = self.lv_duplicates
        elif index == 2:
            self.content_area.content = ft.Column([self.dt_fixes], scroll=ft.ScrollMode.AUTO)
        self.page.update()

    def delete_all_duplicates(self, e):
        if not self.files_to_delete:
            return

        to_delete_list = list(self.files_to_delete)
        count = self.logic.recycle_files(to_delete_list)
        
        self.status_text.value = f"OP_SUCCESS: {count} UNITS PURGED. RELOADING SYSTEM..."
        self.files_to_delete.clear()
        self.update_delete_button(refresh_view=True)
        self.page.update()
        
        threading.Thread(target=self.run_scan, daemon=True).start()

    def save_fix_row(self, path, new_artist, btn):
        if self.logic.update_tag_artist(path, new_artist):
            btn.icon = ft.Icons.CHECK_BOX
            btn.icon_color = CP_CYAN
            btn.disabled = True
            self.page.update()

def main(page: ft.Page):
    page.assets_dir = "assets"
    app = MusicAppFlet(page)

ft.app(target=main)