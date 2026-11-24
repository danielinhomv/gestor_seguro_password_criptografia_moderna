"""Interfaz gráfica moderna para el Gestor Seguro de Contraseñas.

Características:
- Crear y abrir bóvedas
- Añadir, buscar, editar y eliminar contraseñas
- Generador de contraseñas seguras
- Copiar al portapapeles
- Mostrar/ocultar contraseñas
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
import secrets
import string
import pyperclip
from pathlib import Path
from typing import Optional

from .errors import GestorError, InvalidPasswordError
from .storage import FileStorage
from .vault import Vault


class LoginWindow:
    """Ventana de login: crear o abrir bóveda."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🔐 Gestor Seguro de Contraseñas")
        self.root.geometry("450x350")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Variables
        self.vault_path = tk.StringVar(value="vault.json")
        self.password = tk.StringVar()
        self.vault: Optional[Vault] = None
        self.storage: Optional[FileStorage] = None
        
        self.create_widgets()

    def center_window(self):
        """Centrar ventana en la pantalla."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Crear controles de la ventana de login."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title = ttk.Label(
            main_frame,
            text="🔐 Gestor Seguro",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(0, 10))

        subtitle = ttk.Label(
            main_frame,
            text="Protege tus contraseñas con criptografía moderna",
            font=("Arial", 9)
        )
        subtitle.pack(pady=(0, 30))

        # Archivo de bóveda
        vault_frame = ttk.LabelFrame(main_frame, text="Archivo de Bóveda", padding="10")
        vault_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Entry(
            vault_frame,
            textvariable=self.vault_path,
            font=("Arial", 10)
        ).pack(fill=tk.X)

        # Contraseña maestra
        pass_frame = ttk.LabelFrame(main_frame, text="Contraseña Maestra", padding="10")
        pass_frame.pack(fill=tk.X, pady=(0, 20))

        self.pass_entry = ttk.Entry(
            pass_frame,
            textvariable=self.password,
            show="●",
            font=("Arial", 10)
        )
        self.pass_entry.pack(fill=tk.X)
        self.pass_entry.bind("<Return>", lambda e: self.open_vault())

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="🔓 Abrir Bóveda",
            command=self.open_vault,
            width=20
        ).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="✨ Crear Nueva",
            command=self.create_vault,
            width=20
        ).pack(side=tk.LEFT)

        # Info
        info_text = "💡 Primera vez: haz clic en 'Crear Nueva'"
        ttk.Label(
            main_frame,
            text=info_text,
            font=("Arial", 8),
            foreground="gray"
        ).pack(pady=(20, 0))

    def create_vault(self):
        """Crear nueva bóveda."""
        password = self.password.get()
        if len(password) < 8:
            messagebox.showerror(
                "Error",
                "La contraseña maestra debe tener al menos 8 caracteres."
            )
            return

        path = Path(self.vault_path.get())
        if path.exists():
            if not messagebox.askyesno(
                "Confirmar",
                f"¿Sobrescribir '{path.name}'?\n\n⚠️ Se perderán todas las contraseñas guardadas."
            ):
                return

        try:
            self.storage = FileStorage(path)
            self.vault = Vault.create(self.storage, password, overwrite=True)
            messagebox.showinfo(
                "¡Éxito!",
                f"Bóveda creada en:\n{path.absolute()}"
            )
            self.open_main_window()
        except GestorError as e:
            messagebox.showerror("Error", str(e))

    def open_vault(self):
        """Abrir bóveda existente."""
        password = self.password.get()
        if not password:
            messagebox.showwarning("Atención", "Ingresa la contraseña maestra.")
            return

        path = Path(self.vault_path.get())
        if not path.exists():
            messagebox.showerror(
                "Error",
                f"No existe '{path.name}'.\n\nUsa 'Crear Nueva' primero."
            )
            return

        try:
            self.storage = FileStorage(path)
            self.vault = Vault.open(self.storage, password)
            self.open_main_window()
        except InvalidPasswordError:
            messagebox.showerror("Error", "❌ Contraseña incorrecta")
            self.password.set("")
            self.pass_entry.focus()
        except GestorError as e:
            messagebox.showerror("Error", str(e))

    def open_main_window(self):
        """Abrir ventana principal."""
        self.root.withdraw()  # Ocultar ventana de login
        main_win = tk.Toplevel(self.root)
        MainWindow(main_win, self.vault, self.storage, self.vault_path.get())


class MainWindow:
    """Ventana principal: gestión de contraseñas."""

    def __init__(self, root: tk.Toplevel, vault: Vault, storage: FileStorage, vault_path: str):
        self.root = root
        self.vault = vault
        self.storage = storage
        self.vault_path = vault_path
        
        self.root.title(f"🔐 Gestor Seguro - {Path(vault_path).name}")
        self.root.geometry("900x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        """Crear controles de la ventana principal."""
        # Frame superior: botones de acción
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)

        ttk.Button(
            top_frame,
            text="➕ Añadir Contraseña",
            command=self.add_entry_dialog
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            top_frame,
            text="🔄 Actualizar",
            command=self.refresh_list
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            top_frame,
            text="🔑 Cambiar Contraseña Maestra",
            command=self.change_master_password
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            top_frame,
            text="🔒 Cerrar Bóveda",
            command=self.on_close
        ).pack(side=tk.RIGHT)

        # Búsqueda
        search_frame = ttk.Frame(self.root, padding="0 0 10 10")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="🔍 Buscar:").pack(side=tk.LEFT, padx=(10, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.refresh_list())
        
        ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=40
        ).pack(side=tk.LEFT)

        # Lista de contraseñas (Treeview)
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ("sitio", "usuario", "acciones")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("sitio", text="🌐 Sitio")
        self.tree.heading("usuario", text="👤 Usuario")
        self.tree.heading("acciones", text="⚡ Acciones")

        self.tree.column("sitio", width=250)
        self.tree.column("usuario", width=200)
        self.tree.column("acciones", width=400)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Doble clic para ver detalles
        self.tree.bind("<Double-1>", self.show_entry_details)

        # Status bar
        self.status_var = tk.StringVar(value="Bóveda desbloqueada ✓")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="5"
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def refresh_list(self):
        """Actualizar lista de contraseñas."""
        # Limpiar lista
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Obtener búsqueda
        search = self.search_var.get().lower()

        # Cargar entradas
        try:
            entries = self.vault.list_entries()
            
            # Filtrar por búsqueda
            if search:
                entries = [e for e in entries if search in e["site"].lower() or search in e["username"].lower()]

            # Insertar en la lista
            for entry in entries:
                self.tree.insert(
                    "",
                    tk.END,
                    iid=entry["id"],
                    values=(
                        entry["site"],
                        entry["username"],
                        "👁️ Ver  📋 Copiar  ✏️ Editar  🗑️ Eliminar"
                    )
                )

            # Actualizar status
            total = len(entries)
            all_entries = len(self.vault.list_entries())
            if search:
                self.status_var.set(f"Mostrando {total} de {all_entries} contraseñas")
            else:
                self.status_var.set(f"Total: {total} contraseña(s)")

        except GestorError as e:
            messagebox.showerror("Error", str(e))

    def show_entry_details(self, event=None):
        """Mostrar detalles de una entrada (doble clic)."""
        selection = self.tree.selection()
        if not selection:
            return

        entry_id = selection[0]
        try:
            entry = self.vault.get_entry(entry_id)
            
            # Crear ventana de detalles
            detail_win = tk.Toplevel(self.root)
            detail_win.title(f"🔑 {entry['site']}")
            detail_win.geometry("500x400")
            detail_win.resizable(False, False)
            detail_win.transient(self.root)
            detail_win.grab_set()

            frame = ttk.Frame(detail_win, padding="20")
            frame.pack(fill=tk.BOTH, expand=True)

            # Campos
            fields = [
                ("🌐 Sitio:", entry["site"]),
                ("👤 Usuario:", entry["username"]),
                ("🔑 Contraseña:", entry["password"]),
                ("📝 Notas:", entry.get("notes", "")),
            ]

            for i, (label, value) in enumerate(fields):
                ttk.Label(frame, text=label, font=("Arial", 10, "bold")).grid(
                    row=i, column=0, sticky=tk.W, pady=5
                )
                
                if label == "🔑 Contraseña:":
                    # Frame para contraseña con botón
                    pass_frame = ttk.Frame(frame)
                    pass_frame.grid(row=i, column=1, sticky=tk.W, pady=5)
                    
                    pass_var = tk.StringVar(value="●" * len(value))
                    pass_entry = ttk.Entry(pass_frame, textvariable=pass_var, width=30, state="readonly")
                    pass_entry.pack(side=tk.LEFT, padx=(0, 5))
                    
                    show_var = tk.BooleanVar(value=False)
                    
                    def toggle_password():
                        if show_var.get():
                            pass_var.set(value)
                            toggle_btn.config(text="🙈")
                        else:
                            pass_var.set("●" * len(value))
                            toggle_btn.config(text="👁️")
                    
                    toggle_btn = ttk.Button(pass_frame, text="👁️", width=3, command=toggle_password)
                    toggle_btn.pack(side=tk.LEFT, padx=(0, 5))
                    
                    ttk.Button(
                        pass_frame,
                        text="📋",
                        width=3,
                        command=lambda: self.copy_to_clipboard(value, "Contraseña")
                    ).pack(side=tk.LEFT)
                else:
                    text = tk.Text(frame, height=1 if i < 3 else 3, width=35, wrap=tk.WORD)
                    text.insert("1.0", value)
                    text.config(state="disabled")
                    text.grid(row=i, column=1, sticky=tk.W, pady=5)

            # Botones
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=(20, 0))

            ttk.Button(
                btn_frame,
                text="✏️ Editar",
                command=lambda: [detail_win.destroy(), self.edit_entry_dialog(entry_id)]
            ).pack(side=tk.LEFT, padx=5)

            ttk.Button(
                btn_frame,
                text="🗑️ Eliminar",
                command=lambda: [detail_win.destroy(), self.delete_entry(entry_id)]
            ).pack(side=tk.LEFT, padx=5)

            ttk.Button(
                btn_frame,
                text="Cerrar",
                command=detail_win.destroy
            ).pack(side=tk.LEFT, padx=5)

        except GestorError as e:
            messagebox.showerror("Error", str(e))

    def add_entry_dialog(self):
        """Diálogo para añadir nueva entrada."""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Añadir Contraseña")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        site_var = tk.StringVar()
        username_var = tk.StringVar()
        password_var = tk.StringVar()
        notes_var = tk.StringVar()

        # Campos
        ttk.Label(frame, text="🌐 Sitio:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=site_var, width=40).grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="👤 Usuario:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=username_var, width=40).grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="🔑 Contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        pass_frame = ttk.Frame(frame)
        pass_frame.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        pass_entry = ttk.Entry(pass_frame, textvariable=password_var, width=30)
        pass_entry.pack(side=tk.LEFT, padx=(0, 5))

        def generate_password():
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
            pwd = "".join(secrets.choice(alphabet) for _ in range(20))
            password_var.set(pwd)

        ttk.Button(pass_frame, text="🎲 Generar", command=generate_password).pack(side=tk.LEFT)

        ttk.Label(frame, text="📝 Notas:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        notes_text = tk.Text(frame, width=40, height=5)
        notes_text.grid(row=3, column=1, pady=5)

        def save_entry():
            site = site_var.get().strip()
            username = username_var.get().strip()
            password = password_var.get()

            if not site or not username or not password:
                messagebox.showwarning("Atención", "Completa sitio, usuario y contraseña.")
                return

            try:
                notes = notes_text.get("1.0", tk.END).strip()
                self.vault.add_entry(site, username, password, notes)
                messagebox.showinfo("¡Éxito!", f"Contraseña guardada para:\n{site}")
                dialog.destroy()
                self.refresh_list()
            except GestorError as e:
                messagebox.showerror("Error", str(e))

        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(btn_frame, text="💾 Guardar", command=save_entry).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def edit_entry_dialog(self, entry_id: str):
        """Diálogo para editar entrada existente."""
        try:
            entry = self.vault.get_entry(entry_id)
        except GestorError as e:
            messagebox.showerror("Error", str(e))
            return

        dialog = tk.Toplevel(self.root)
        dialog.title(f"✏️ Editar - {entry['site']}")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # Variables
        site_var = tk.StringVar(value=entry["site"])
        username_var = tk.StringVar(value=entry["username"])
        password_var = tk.StringVar(value=entry["password"])

        # Campos
        ttk.Label(frame, text="🌐 Sitio:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=site_var, width=40).grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="👤 Usuario:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=username_var, width=40).grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="🔑 Contraseña:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(frame, textvariable=password_var, width=40).grid(row=2, column=1, pady=5)

        ttk.Label(frame, text="📝 Notas:").grid(row=3, column=0, sticky=tk.NW, pady=5)
        notes_text = tk.Text(frame, width=40, height=5)
        notes_text.insert("1.0", entry.get("notes", ""))
        notes_text.grid(row=3, column=1, pady=5)

        def save_changes():
            try:
                notes = notes_text.get("1.0", tk.END).strip()
                self.vault.update_entry(
                    entry_id,
                    site=site_var.get().strip(),
                    username=username_var.get().strip(),
                    password=password_var.get(),
                    notes=notes
                )
                messagebox.showinfo("¡Éxito!", "Contraseña actualizada.")
                dialog.destroy()
                self.refresh_list()
            except GestorError as e:
                messagebox.showerror("Error", str(e))

        # Botones
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(btn_frame, text="💾 Guardar", command=save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def delete_entry(self, entry_id: str):
        """Eliminar una entrada."""
        try:
            entry = self.vault.get_entry(entry_id)
            if messagebox.askyesno(
                "Confirmar eliminación",
                f"¿Eliminar contraseña de:\n\n🌐 {entry['site']}\n👤 {entry['username']}?\n\n⚠️ Esta acción no se puede deshacer."
            ):
                self.vault.delete_entry(entry_id)
                messagebox.showinfo("¡Eliminado!", "Contraseña eliminada.")
                self.refresh_list()
        except GestorError as e:
            messagebox.showerror("Error", str(e))

    def change_master_password(self):
        """Cambiar contraseña maestra."""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔑 Cambiar Contraseña Maestra")
        dialog.geometry("450x300")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()

        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="⚠️ Cambiará la contraseña para desbloquear la bóveda.\nLas contraseñas guardadas NO se modifican.",
            wraplength=350,
            justify=tk.CENTER
        ).pack(pady=(0, 20))

        ttk.Label(frame, text="Nueva contraseña maestra:").pack()
        new_pass_var = tk.StringVar()
        ttk.Entry(frame, textvariable=new_pass_var, show="●", width=30).pack(pady=5)

        ttk.Label(frame, text="Repite la contraseña:").pack()
        confirm_var = tk.StringVar()
        ttk.Entry(frame, textvariable=confirm_var, show="●", width=30).pack(pady=5)

        def save_new_password():
            new_pass = new_pass_var.get()
            confirm = confirm_var.get()

            if len(new_pass) < 8:
                messagebox.showerror("Error", "La contraseña debe tener al menos 8 caracteres.")
                return

            if new_pass != confirm:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return

            try:
                self.vault.change_master_password(new_pass)
                messagebox.showinfo(
                    "¡Éxito!",
                    "Contraseña maestra cambiada.\n\n✅ Usa la nueva contraseña la próxima vez."
                )
                dialog.destroy()
            except GestorError as e:
                messagebox.showerror("Error", str(e))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(20, 0))

        ttk.Button(btn_frame, text="💾 Cambiar", command=save_new_password).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def copy_to_clipboard(self, text: str, label: str = "Texto"):
        """Copiar al portapapeles."""
        try:
            pyperclip.copy(text)
            self.status_var.set(f"✓ {label} copiado al portapapeles")
            self.root.after(3000, lambda: self.status_var.set(f"Total: {len(self.vault.list_entries())} contraseña(s)"))
        except Exception:
            messagebox.showwarning("Atención", "No se pudo copiar al portapapeles.")

    def on_close(self):
        """Cerrar bóveda y aplicación."""
        if messagebox.askyesno("Cerrar", "¿Cerrar la bóveda?"):
            self.vault.lock()
            self.root.destroy()
            self.root.master.destroy()


def main():
    """Punto de entrada de la aplicación GUI."""
    root = tk.Tk()
    
    # Configurar estilo
    style = ttk.Style()
    style.theme_use("clam")
    
    LoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
