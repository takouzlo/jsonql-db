# jsonql/browser.py
import flet as ft
import jsonql
import json
from pathlib import Path

class BrowserApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = None
        self.setup_ui()
        self.auto_connect()

    def setup_ui(self):
        self.page.title = "JSONQL Browser"
        self.page.padding = 10
        self.page.scroll = None  # Désactive le scroll global

        # --- HEADER ---
        header = ft.Row([
            ft.Icon(ft.Icons.DATA_OBJECT, size=28),
            ft.Text("JSONQL", size=24, weight="bold"),
            ft.Text("— Lightweight JSON Database", size=14, color=ft.Colors.GREY)
        ], alignment=ft.MainAxisAlignment.START)

        # --- DB PATH + ACTIONS ---
        self.db_path_field = ft.TextField(label="DB folder", value="my_db", expand=True, dense=True)
        connect_btn = ft.IconButton(ft.Icons.PLAY_CIRCLE_OUTLINE, tooltip="Connect", on_click=self.on_connect)
        delete_btn = ft.IconButton(ft.Icons.DELETE_FOREVER, icon_color=ft.Colors.RED, tooltip="Delete DB", on_click=self.on_delete_db)

        db_row = ft.Row([self.db_path_field, connect_btn, delete_btn], expand=True)

        # --- TABLE MANAGEMENT ---
        self.new_table_field = ft.TextField(label="New table", hint_text="e.g. users", width=150, dense=True)
        create_btn = ft.ElevatedButton("Create", on_click=self.on_create_table, height=38)
        self.tables_dropdown = ft.Dropdown(label="Table", width=180, dense=True, on_change=self.on_table_change)

        table_row = ft.Row([self.new_table_field, create_btn, self.tables_dropdown], spacing=10)

        # --- DATA TABLE (avec scroll interne) ---
        self.data_table = ft.DataTable(
            columns=[ft.DataColumn(ft.Text("No table"))],
            rows=[ft.DataRow([ft.DataCell(ft.Text("Connect to a DB"))])],
            heading_row_color=ft.Colors.BLACK12,
        )
        table_container = ft.Container(
            content=ft.Column([self.data_table], scroll=ft.ScrollMode.ADAPTIVE, height=250),
            border=ft.border.all(1, ft.Colors.OUTLINE),
            border_radius=6,
            padding=8
        )

        # --- QUERY + RESULT ---
        self.query_field = ft.TextField(
            label="SQL Query",
            hint_text="SELECT * FROM devices WHERE room='A101'",
            multiline=True,
            min_lines=2,
            max_lines=3,
            dense=True,
            expand=True
        )
        run_btn = ft.ElevatedButton("Run", icon=ft.Icons.PLAY_ARROW, on_click=self.on_run_query)

        query_row = ft.Row([self.query_field, run_btn], expand=True)

        self.result_output = ft.Text(
            "Result will appear here...",
            size=12,
            selectable=True,
            font_family="monospace"
        )
        result_container = ft.Container(
            content=ft.Column([self.result_output], scroll=ft.ScrollMode.ADAPTIVE, auto_scroll=True),
            height=120,
            padding=10,
            border=ft.border.all(1, ft.Colors.OUTLINE_VARIANT),
            border_radius=6,
            bgcolor=ft.Colors.BLACK12
        )

        # --- ASSEMBLAGE ---
        self.page.add(
            header,
            ft.Divider(height=1),
            db_row,
            ft.Divider(height=1),
            table_row,
            ft.Divider(height=1),
            ft.Text("Data", size=16, weight="bold"),
            table_container,
            ft.Divider(height=1),
            ft.Text("Query", size=16, weight="bold"),
            query_row,
            ft.Text("Result", size=16, weight="bold"),
            result_container,
            ft.Divider(height=1),
            ft.Text("💡 Commands: SELECT • INSERT • UPDATE • DELETE", size=11, color=ft.Colors.GREY)
        )

    # --- LOGIQUE ---
    def on_connect(self, e):
        try:
            self.db = jsonql.connect(self.db_path_field.value)
            self.refresh_tables()
            self.page.snack_bar = ft.SnackBar(ft.Text("✅ Connected"), open=True)
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"❌ {ex}"), open=True)
        self.page.update()

    def on_delete_db(self, e):
        if not self.db:
            return

        def do_delete(_):
            try:
                self.db.drop_database()  # ← Fonctionne maintenant !
                self.db = None
                self.tables_dropdown.options = []
                self.tables_dropdown.value = None
                self.update_table_view([])
                self.show_result("✅ Database deleted!")
                self.page.dialog.open = False
                self.page.snack_bar = ft.SnackBar(ft.Text("🗑️ DB folder deleted"), open=True)
            except Exception as ex:
                self.show_result(f"❌ Delete error: {ex}")
            self.page.update()

        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Delete Database?"),
            content=ft.Text(f"This will delete '{self.db.db_path}' and all tables."),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: setattr(self.page, "dialog", None)),
                ft.TextButton("Delete", on_click=do_delete, style=ft.ButtonStyle(color=ft.Colors.RED))
            ]
        )
        self.page.dialog.open = True
        self.page.update()

    def refresh_tables(self):
        if not self.db:
            return
        tables = self.db.list_tables()
        self.tables_dropdown.options = [ft.dropdown.Option(t) for t in tables]
        if tables and not self.tables_dropdown.value:
            self.tables_dropdown.value = tables[0]
        self.page.update()
        self.load_table()

    def on_create_table(self, e):
        name = self.new_table_field.value.strip()
        if not name or not self.db:
            return
        if not name.isalnum():
            self.show_result("❌ Table name must be alphanumeric")
            return
        try:
            self.db.create_table(name)
            self.new_table_field.value = ""
            self.refresh_tables()
            self.show_result(f"✅ Table '{name}' created")
        except Exception as ex:
            self.show_result(f"❌ {ex}")
        self.page.update()

    def on_table_change(self, e):
        self.load_table()

    def load_table(self):
        if not self.db or not self.tables_dropdown.value:
            self.update_table_view([])
            return
        try:
            rows = self.db.select(self.tables_dropdown.value)
            self.update_table_view(rows)
        except Exception as ex:
            self.update_table_view([])
            self.show_result(f"❌ Load error: {ex}")

    def update_table_view(self, rows):
        if not rows:
            self.data_table.columns = [ft.DataColumn(ft.Text("Empty"))]
            self.data_table.rows = [ft.DataRow([ft.DataCell(ft.Text("No data"))])]
        else:
            cols = list(rows[0].keys())
            self.data_table.columns = [ft.DataColumn(ft.Text(str(c))) for c in cols]
            self.data_table.rows = [
                ft.DataRow([ft.DataCell(ft.Text(str(row.get(c, "")))) for c in cols])
                for row in rows
            ]
        self.page.update()

    def on_run_query(self, e):
        if not self.db:
            self.show_result("❌ Not connected")
            return
        try:
            result = self.db.query(self.query_field.value)
            self.show_result(json.dumps(result, indent=2, ensure_ascii=False) if isinstance(result, (dict, list)) else str(result))
            
            # 🔁 RAFFRAÎCHISSEMENT AUTO après INSERT/UPDATE/DELETE
            if any(kw in self.query_field.value.upper() for kw in ["INSERT", "UPDATE", "DELETE"]):
                self.refresh_tables()
                if self.tables_dropdown.value:
                    self.load_table()
        except Exception as ex:
            self.show_result(f"❌ {ex}")
        self.page.update()

    def show_result(self, text: str):
        self.result_output.value = text
        self.page.update()

    def auto_connect(self):
        if Path(self.db_path_field.value).exists():
            self.on_connect(None)

def main(page: ft.Page):
    BrowserApp(page)

if __name__ == "__main__":
    ft.app(target=main)