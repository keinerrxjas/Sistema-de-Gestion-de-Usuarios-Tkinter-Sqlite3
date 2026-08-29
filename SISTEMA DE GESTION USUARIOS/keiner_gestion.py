"""
Sistema de Gestión de Usuarios
Tkinter + SQLite3 - CRUD completo con ID autoincrement, búsqueda por nombre,
selección de imagen y adjuntar archivo.

Interfaz: paleta blanco + morado, con panel de vista (foto/GIF) a la derecha
y menús superiores para conectar/desconectar la base de datos y ver el
total de usuarios registrados.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import shutil

try:
    from PIL import Image, ImageTk, ImageSequence
    PIL_OK = True
except ImportError:
    PIL_OK = False

IMG_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico"}
ASSETS_DIR = "adjuntos"
os.makedirs(ASSETS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# PALETA DE COLORES
# ---------------------------------------------------------------------------
MORADO_OSCURO = "#4B2E83"
MORADO = "#6C3FC5"
MORADO_CLARO = "#8E6FE0"
MORADO_PASTEL = "#F1ECFB"
BLANCO = "#FFFFFF"
GRIS_TEXTO = "#4A4453"
VERDE = "#2ecc71"
NARANJA = "#e67e22"
ROJO = "#e74c3c"
GRIS = "#7f8c8d"

# Ruta de la foto o GIF que se muestra junto al formulario.
RUTA_IMAGEN_LATERAL = "k_galactica.png"

NOMBRE_BD = "keiner.db"


# ---------------------------------------------------------------------------
# APLICACIÓN
# ---------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Gestión de Usuarios")
        self.geometry("1000x700")
        self.minsize(980, 600)
        self.configure(bg=BLANCO)
        self.resizable(True, True)

        self.id_seleccionado = None
        self.imagen_path_actual = None
        self.archivo_path_actual = None
        self.imagen_tk = None  # referencia viva para el preview del formulario

        # Estado de la conexión a la base de datos
        self.con = None
        self.conectado = False

        # Para el GIF animado del panel de vista
        self.gif_frames = []
        self.gif_index = 0
        self.gif_after_id = None

        self._configurar_estilos()
        self._construir_menu()
        self._construir_ui()
        self._cargar_imagen_lateral(RUTA_IMAGEN_LATERAL)
        self._cargar_tabla([])

    # -------------------------------------------------------------
    # ESTILOS ttk
    # -------------------------------------------------------------
    def _configurar_estilos(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Treeview",
                         background=BLANCO,
                         fieldbackground=BLANCO,
                         foreground=GRIS_TEXTO,
                         rowheight=26,
                         borderwidth=0,
                         font=("Segoe UI", 9))
        style.configure("Treeview.Heading",
                         background=MORADO,
                         foreground=BLANCO,
                         font=("Segoe UI", 9, "bold"),
                         borderwidth=0)
        style.map("Treeview.Heading", background=[("active", MORADO_OSCURO)])
        style.map("Treeview",
                  background=[("selected", MORADO_CLARO)],
                  foreground=[("selected", BLANCO)])

        style.configure("TCombobox",
                         fieldbackground=BLANCO,
                         background=BLANCO)

    def _boton(self, parent, texto, color, comando, width=16):
        return tk.Button(parent, text=texto, bg=color, fg=BLANCO,
                          activebackground=MORADO_OSCURO, activeforeground=BLANCO,
                          font=("Segoe UI", 9, "bold"), relief="flat",
                          cursor="hand2", command=comando, width=width, pady=6)

    # -------------------------------------------------------------
    # MENÚ SUPERIOR
    # -------------------------------------------------------------
    def _construir_menu(self):
        menubar = tk.Menu(self)

        menu_bd = tk.Menu(menubar, tearoff=0)
        menu_bd.add_command(label="Conectar base de datos", command=self.conectar_bd)
        menu_bd.add_command(label="Desconectar base de datos", command=self.desconectar_bd)
        menu_bd.add_separator()
        menu_bd.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Base de Datos", menu=menu_bd)

        menu_reportes = tk.Menu(menubar, tearoff=0)
        menu_reportes.add_command(label="Ver total de usuarios", command=self.contar_usuarios)
        menubar.add_cascade(label="Reportes", menu=menu_reportes)

        self.config(menu=menubar)

    # -------------------------------------------------------------
    # CONEXIÓN A LA BASE DE DATOS
    # -------------------------------------------------------------
    def conectar_bd(self):
        if self.conectado:
            messagebox.showinfo("Base de Datos", "Ya existe una conexión activa.")
            return
        try:
            self.con = sqlite3.connect(NOMBRE_BD)
            cur = self.con.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT,
                    direccion TEXT,
                    ciudad TEXT,
                    codigo_postal TEXT,
                    genero TEXT,
                    activo TEXT,
                    tipo_usuario TEXT,
                    imagen_path TEXT,
                    archivo_path TEXT
                )
            """)
            self.con.commit()
            self.conectado = True
            messagebox.showinfo("Base de Datos", "Conexión establecida correctamente.")
            self.mostrar_todos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{e}")

    def desconectar_bd(self):
        if not self.conectado:
            messagebox.showinfo("Base de Datos", "No hay ninguna conexión activa.")
            return
        try:
            self.con.close()
        except Exception:
            pass
        self.con = None
        self.conectado = False
        self._cargar_tabla([])
        messagebox.showinfo("Base de Datos", "Conexión cerrada correctamente.")

    def _bd_lista(self):
        if not self.conectado or self.con is None:
            messagebox.showwarning(
                "Base de Datos",
                "Debes conectar la base de datos primero\n(menú Base de Datos → Conectar base de datos)."
            )
            return False
        return True

    def contar_usuarios(self):
        if not self._bd_lista():
            return
        cur = self.con.cursor()
        cur.execute("SELECT COUNT(*) FROM usuarios")
        total = cur.fetchone()[0]
        messagebox.showinfo("Total de usuarios", f"Actualmente hay {total} usuario(s) registrados.")

    # -------------------------------------------------------------
    # UI
    # -------------------------------------------------------------
    def _construir_ui(self):
        # ---- Encabezado ----
        header = tk.Frame(self, bg=MORADO)
        header.pack(fill="x")
        tk.Label(header, text="FORMULARIO DE REGISTRO DE USUARIOS", bg=MORADO, fg=BLANCO,
                 font=("Segoe UI", 15, "bold"), pady=16).pack()

        contenido = tk.Frame(self, bg=BLANCO)
        contenido.pack(fill="both", expand=True)

        # =========================================================
        # PANEL PRINCIPAL (izquierda) - formulario, búsqueda y tabla
        # =========================================================
        panel_der = tk.Frame(contenido, bg=BLANCO)
        panel_der.pack(side="left", fill="both", expand=True)

        # ---- Tarjeta del formulario ----
        tarjeta = tk.Frame(panel_der, bg=MORADO_PASTEL, bd=0)
        tarjeta.pack(fill="x", padx=20, pady=15)

        frm = tk.Frame(tarjeta, bg=MORADO_PASTEL, width=40)
        frm.pack(side="left", fill="y", padx=15, pady=15)
        frm.pack_propagate(False)

        # ---- Logo/foto fijo (ver RUTA_IMAGEN_LATERAL), sin cuadro visible ----
        frm_logo = tk.Frame(tarjeta, bg=MORADO_PASTEL, width=170, height=230)
        frm_logo.pack(side="right", padx=(0, 20), pady=15)
        frm_logo.pack_propagate(False)
        self.lbl_logo = tk.Label(frm_logo, bg=MORADO_PASTEL, fg=MORADO,
                                  text="🖼", font=("Segoe UI", 24), justify="center")
        self.lbl_logo.pack(fill="both", expand=True)

        # ---- Variables ----
        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_direccion = tk.StringVar()
        self.var_ciudad = tk.StringVar()
        self.var_cp = tk.StringVar()
        self.var_genero = tk.StringVar(value="Masculino")
        self.var_activo = tk.BooleanVar()
        self.var_tipo = tk.StringVar()
        self.var_buscar = tk.StringVar()
        self.var_archivo_lbl = tk.StringVar(value="Archivo: No adjunto")

        etq_kw = dict(bg=MORADO_PASTEL, fg=GRIS_TEXTO, font=("Segoe UI", 9, "bold"))

        # ---- Fila 1: Nombre / Apellido ----
        tk.Label(frm, text="Nombre:", **etq_kw).grid(row=0, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(frm, textvariable=self.var_nombre, width=25, relief="solid", bd=1).grid(row=0, column=1, sticky="w", padx=5, pady=6)

        tk.Label(frm, text="Apellido:", **etq_kw).grid(row=0, column=2, sticky="e", padx=5, pady=6)
        tk.Entry(frm, textvariable=self.var_apellido, width=25, relief="solid", bd=1).grid(row=0, column=3, sticky="w", padx=5, pady=6)

        # ---- Fila 2: Dirección / Ciudad ----
        tk.Label(frm, text="Dirección:", **etq_kw).grid(row=1, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(frm, textvariable=self.var_direccion, width=25, relief="solid", bd=1).grid(row=1, column=1, sticky="w", padx=5, pady=6)

        tk.Label(frm, text="Ciudad:", **etq_kw).grid(row=1, column=2, sticky="e", padx=5, pady=6)
        tk.Entry(frm, textvariable=self.var_ciudad, width=25, relief="solid", bd=1).grid(row=1, column=3, sticky="w", padx=5, pady=6)

        # ---- Fila 3: Código Postal / Género ----
        tk.Label(frm, text="Código Postal:", **etq_kw).grid(row=2, column=0, sticky="e", padx=5, pady=6)
        tk.Entry(frm, textvariable=self.var_cp, width=25, relief="solid", bd=1).grid(row=2, column=1, sticky="w", padx=5, pady=6)

        tk.Label(frm, text="Género:", **etq_kw).grid(row=2, column=2, sticky="e", padx=5, pady=6)
        frm_genero = tk.Frame(frm, bg=MORADO_PASTEL)
        frm_genero.grid(row=2, column=3, sticky="w")
        tk.Radiobutton(frm_genero, text="Masculino", variable=self.var_genero, value="Masculino",
                        bg=MORADO_PASTEL, fg=GRIS_TEXTO, selectcolor=BLANCO,
                        activebackground=MORADO_PASTEL).pack(anchor="w")
        tk.Radiobutton(frm_genero, text="Femenino", variable=self.var_genero, value="Femenino",
                        bg=MORADO_PASTEL, fg=GRIS_TEXTO, selectcolor=BLANCO,
                        activebackground=MORADO_PASTEL).pack(anchor="w")

        # ---- Fila 4: Usuario activo / Tipo de usuario ----
        tk.Checkbutton(frm, text="Usuario activo", variable=self.var_activo,
                        bg=MORADO_PASTEL, fg=GRIS_TEXTO, selectcolor=BLANCO,
                        activebackground=MORADO_PASTEL, font=("Segoe UI", 9, "bold")).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=5, pady=10)

        tk.Label(frm, text="Tipo de usuario:", **etq_kw).grid(row=3, column=2, sticky="e", padx=5, pady=5)
        combo_tipo = ttk.Combobox(frm, textvariable=self.var_tipo, state="readonly",
                                   values=["Administrador", "Estándar", "Invitado"], width=22)
        combo_tipo.grid(row=3, column=3, sticky="w", padx=5, pady=5)

        # ---- Fila 5: Imagen / botones / preview ----
        tk.Label(frm, text="Imagen:", **etq_kw).grid(row=4, column=0, sticky="ne", padx=5, pady=5)

        frm_img_btns = tk.Frame(frm, bg=MORADO_PASTEL)
        frm_img_btns.grid(row=4, column=1, sticky="nw", padx=5, pady=5)
        self._boton(frm_img_btns, "Seleccionar Imagen", MORADO, self.seleccionar_imagen, width=20).pack(pady=2)
        self._boton(frm_img_btns, "📎 Adjuntar Archivo", MORADO_CLARO, self.adjuntar_archivo, width=20).pack(pady=2)
        tk.Label(frm_img_btns, textvariable=self.var_archivo_lbl, bg=MORADO_PASTEL,
                 fg=GRIS_TEXTO, font=("Segoe UI", 8)).pack(pady=(8, 0), anchor="w")

        frm_preview = tk.Frame(frm, relief="solid", bd=1, width=150, height=130, bg=BLANCO,
                                highlightbackground=MORADO, highlightthickness=1)
        frm_preview.grid(row=4, column=2, columnspan=2, sticky="w", padx=5, pady=5)
        frm_preview.grid_propagate(False)
        frm_preview.pack_propagate(False)
        self.lbl_preview = tk.Label(frm_preview, bg=BLANCO)
        self.lbl_preview.pack(fill="both", expand=True)

        # ---- Botones principales ----
        frm_botones = tk.Frame(panel_der, bg=BLANCO)
        frm_botones.pack(fill="x", padx=25, pady=(0, 15))

        self._boton(frm_botones, "+ INSERTAR", VERDE, self.insertar, width=15).pack(side="left", padx=3)
        self._boton(frm_botones, "✎ ACTUALIZAR", NARANJA, self.actualizar, width=15).pack(side="left", padx=3)
        self._boton(frm_botones, "🗑 ELIMINAR", ROJO, self.eliminar, width=15).pack(side="left", padx=3)
        self._boton(frm_botones, "↺ LIMPIAR", MORADO, self.limpiar, width=15).pack(side="left", padx=3)
        self._boton(frm_botones, "⏻ SALIR", GRIS, self.destroy, width=15).pack(side="left", padx=3)

        # ---- Búsqueda ----
        frm_buscar = tk.Frame(panel_der, bg=BLANCO)
        frm_buscar.pack(fill="x", padx=25)
        tk.Label(frm_buscar, text="Buscar:", bg=BLANCO, fg=GRIS_TEXTO,
                 font=("Segoe UI", 9, "bold")).pack(side="left")
        tk.Entry(frm_buscar, textvariable=self.var_buscar, width=30, relief="solid", bd=1).pack(side="left", padx=8)
        self._boton(frm_buscar, "🔍 Buscar", MORADO, self.buscar, width=12).pack(side="left", padx=3)
        self._boton(frm_buscar, "Mostrar Todos", MORADO_CLARO, self.mostrar_todos, width=14).pack(side="left", padx=3)

        # ---- Tabla ----
        frm_tabla = tk.Frame(panel_der, bg=BLANCO)
        frm_tabla.pack(fill="both", expand=True, padx=25, pady=(12, 20))

        columnas = ("id", "nombre", "apellido", "direccion", "ciudad",
                    "codigo_postal", "genero", "estado", "tipo_usuario")
        self.tree = ttk.Treeview(frm_tabla, columns=columnas, show="headings", height=8)
        encabezados = {
            "id": "ID", "nombre": "Nombre", "apellido": "Apellido",
            "direccion": "Dirección", "ciudad": "Ciudad",
            "codigo_postal": "Código Postal", "genero": "Género",
            "estado": "Estado", "tipo_usuario": "Tipo Usuario"
        }
        anchos = {"id": 40, "nombre": 90, "apellido": 90, "direccion": 120,
                  "ciudad": 80, "codigo_postal": 90, "genero": 70,
                  "estado": 70, "tipo_usuario": 100}
        for col in columnas:
            self.tree.heading(col, text=encabezados[col])
            self.tree.column(col, width=anchos[col], anchor="center")

        scroll_y = ttk.Scrollbar(frm_tabla, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(frm_tabla, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frm_tabla.grid_rowconfigure(0, weight=1)
        frm_tabla.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.al_seleccionar_fila)

    # -------------------------------------------------------------
    # FOTO / GIF FIJA DEL FORMULARIO
    # -------------------------------------------------------------
    def _cargar_imagen_lateral(self, ruta):
        """Muestra en el cuadro fijo del formulario la foto o GIF indicado en
        RUTA_IMAGEN_LATERAL. Si el archivo no existe, deja el ícono por defecto."""
        if self.gif_after_id is not None:
            self.after_cancel(self.gif_after_id)
            self.gif_after_id = None
        self.gif_frames = []
        self.gif_index = 0

        if not ruta or not os.path.exists(ruta):
            return  # se conserva el ícono por defecto (🖼)

        if PIL_OK:
            try:
                img = Image.open(ruta)
                for frame in ImageSequence.Iterator(img):
                    f = frame.convert("RGBA").copy()
                    f.thumbnail((160, 220))
                    self.gif_frames.append(ImageTk.PhotoImage(f))
                if self.gif_frames:
                    self.lbl_logo.configure(image=self.gif_frames[0], text="")
                    if len(self.gif_frames) > 1:
                        self._animar_gif()
                    return
            except Exception as e:
                print(f"[Pillow] No se pudo cargar la imagen: {e}")

        # Fallback sin Pillow: solo el primer cuadro, sin animación
        try:
            img = tk.PhotoImage(file=ruta)
            self.gif_frames = [img]
            self.lbl_logo.configure(image=img, text="")
        except Exception as e:
            print(f"[Tkinter PhotoImage] No se pudo cargar la imagen: {e}")

    def _animar_gif(self):
        if not self.gif_frames:
            return
        self.lbl_logo.configure(image=self.gif_frames[self.gif_index])
        self.gif_index = (self.gif_index + 1) % len(self.gif_frames)
        self.gif_after_id = self.after(100, self._animar_gif)

    # -------------------------------------------------------------
    # IMAGEN / ARCHIVO (formulario)
    # -------------------------------------------------------------
    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp *.ico"),
                ("Todos los archivos", "*.*"),
            ]
        )
        if not ruta:
            return
        destino = os.path.join(ASSETS_DIR, os.path.basename(ruta))
        try:
            if os.path.abspath(ruta) != os.path.abspath(destino):
                shutil.copy(ruta, destino)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar la imagen:\n{e}")
            return
        self.imagen_path_actual = destino
        self._mostrar_preview(destino)

    def _mostrar_preview(self, ruta):
        if not ruta or not os.path.exists(ruta):
            self.lbl_preview.configure(image="", text="Sin imagen", compound="center")
            self.imagen_tk = None
            return

        self.imagen_tk = None

        if PIL_OK:
            try:
                img = Image.open(ruta)
                img = img.convert("RGBA") if img.mode not in ("RGB", "RGBA") else img
                img.thumbnail((140, 120))
                self.imagen_tk = ImageTk.PhotoImage(img)
                self.lbl_preview.configure(image=self.imagen_tk, text="", compound="center")
                return
            except Exception as e:
                print(f"[Pillow] No se pudo cargar la imagen: {e}")

        try:
            self.imagen_tk = tk.PhotoImage(file=ruta)
            ancho, alto = self.imagen_tk.width(), self.imagen_tk.height()
            factor = max(1, ancho // 140, alto // 120)
            if factor > 1:
                self.imagen_tk = self.imagen_tk.subsample(factor, factor)
            self.lbl_preview.configure(image=self.imagen_tk, text="", compound="center")
            return
        except Exception as e:
            print(f"[Tkinter PhotoImage] No se pudo cargar la imagen: {e}")

        mensaje = "No se pudo mostrar\nla imagen."
        if not PIL_OK:
            mensaje += "\nInstala Pillow:\npip install pillow"
        self.lbl_preview.configure(image="", text=mensaje, compound="center")

    def adjuntar_archivo(self):
        ruta = filedialog.askopenfilename(title="Adjuntar archivo")
        if not ruta:
            return
        destino = os.path.join(ASSETS_DIR, os.path.basename(ruta))
        try:
            if os.path.abspath(ruta) != os.path.abspath(destino):
                shutil.copy(ruta, destino)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar el archivo:\n{e}")
            return
        self.archivo_path_actual = destino
        self.var_archivo_lbl.set(f"Archivo: {os.path.basename(destino)}")

        ext = os.path.splitext(destino)[1].lower()
        if ext in IMG_EXTENSIONS:
            self.imagen_path_actual = destino
            self._mostrar_preview(destino)

    # -------------------------------------------------------------
    # VALIDACIÓN
    # -------------------------------------------------------------
    def _validar(self):
        if not self.var_nombre.get().strip():
            messagebox.showwarning("Validación", "El campo Nombre es obligatorio.")
            return False
        return True

    def _valores_formulario(self):
        return (
            self.var_nombre.get().strip(),
            self.var_apellido.get().strip(),
            self.var_direccion.get().strip(),
            self.var_ciudad.get().strip(),
            self.var_cp.get().strip(),
            self.var_genero.get(),
            "Activo" if self.var_activo.get() else "Inactivo",
            self.var_tipo.get(),
            self.imagen_path_actual,
            self.archivo_path_actual,
        )

    # -------------------------------------------------------------
    # CRUD (requieren conexión activa)
    # -------------------------------------------------------------
    def insertar(self):
        if not self._bd_lista():
            return
        if not self._validar():
            return
        cur = self.con.cursor()
        cur.execute("""
            INSERT INTO usuarios
            (nombre, apellido, direccion, ciudad, codigo_postal, genero, activo, tipo_usuario, imagen_path, archivo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, self._valores_formulario())
        self.con.commit()
        messagebox.showinfo("Éxito", "Usuario insertado correctamente.")
        self.limpiar()
        self.mostrar_todos()

    def actualizar(self):
        if not self._bd_lista():
            return
        if self.id_seleccionado is None:
            messagebox.showwarning("Actualizar", "Selecciona un usuario de la tabla primero.")
            return
        if not self._validar():
            return
        cur = self.con.cursor()
        cur.execute("""
            UPDATE usuarios SET
                nombre=?, apellido=?, direccion=?, ciudad=?, codigo_postal=?,
                genero=?, activo=?, tipo_usuario=?, imagen_path=?, archivo_path=?
            WHERE id=?
        """, self._valores_formulario() + (self.id_seleccionado,))
        self.con.commit()
        messagebox.showinfo("Éxito", "Usuario actualizado correctamente.")
        self.limpiar()
        self.mostrar_todos()

    def eliminar(self):
        if not self._bd_lista():
            return
        if self.id_seleccionado is None:
            messagebox.showwarning("Eliminar", "Selecciona un usuario de la tabla primero.")
            return
        if not messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este usuario?"):
            return
        cur = self.con.cursor()
        cur.execute("DELETE FROM usuarios WHERE id=?", (self.id_seleccionado,))
        self.con.commit()
        messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
        self.limpiar()
        self.mostrar_todos()

    def limpiar(self):
        self.id_seleccionado = None
        self.var_nombre.set("")
        self.var_apellido.set("")
        self.var_direccion.set("")
        self.var_ciudad.set("")
        self.var_cp.set("")
        self.var_genero.set("Masculino")
        self.var_activo.set(False)
        self.var_tipo.set("")
        self.var_buscar.set("")
        self.var_archivo_lbl.set("Archivo: No adjunto")
        self.imagen_path_actual = None
        self.archivo_path_actual = None
        self._mostrar_preview(None)
        for item in self.tree.selection():
            self.tree.selection_remove(item)

    # -------------------------------------------------------------
    # BÚSQUEDA / LISTADO (requieren conexión activa)
    # -------------------------------------------------------------
    def mostrar_todos(self):
        if not self.conectado or self.con is None:
            self._cargar_tabla([])
            return
        cur = self.con.cursor()
        cur.execute("SELECT id, nombre, apellido, direccion, ciudad, codigo_postal, genero, activo, tipo_usuario FROM usuarios ORDER BY id")
        filas = cur.fetchall()
        self._cargar_tabla(filas)

    def buscar(self):
        if not self._bd_lista():
            return
        termino = self.var_buscar.get().strip()
        if not termino:
            self.mostrar_todos()
            return
        cur = self.con.cursor()
        cur.execute("""
            SELECT id, nombre, apellido, direccion, ciudad, codigo_postal, genero, activo, tipo_usuario
            FROM usuarios WHERE nombre LIKE ? ORDER BY id
        """, (f"%{termino}%",))
        filas = cur.fetchall()
        if not filas:
            messagebox.showinfo("Buscar", "No se encontraron usuarios con ese nombre.")
        self._cargar_tabla(filas)

    def _cargar_tabla(self, filas):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for fila in filas:
            self.tree.insert("", "end", values=fila)

    # -------------------------------------------------------------
    # SELECCIÓN DE FILA -> CARGA EN FORMULARIO
    # -------------------------------------------------------------
    def al_seleccionar_fila(self, event):
        if not self.conectado or self.con is None:
            return
        sel = self.tree.selection()
        if not sel:
            return
        valores = self.tree.item(sel[0], "values")
        id_usuario = valores[0]

        cur = self.con.cursor()
        cur.execute("SELECT * FROM usuarios WHERE id=?", (id_usuario,))
        fila = cur.fetchone()
        if not fila:
            return

        (self.id_seleccionado, nombre, apellido, direccion, ciudad, cp,
         genero, activo, tipo, imagen_path, archivo_path) = fila

        self.var_nombre.set(nombre or "")
        self.var_apellido.set(apellido or "")
        self.var_direccion.set(direccion or "")
        self.var_ciudad.set(ciudad or "")
        self.var_cp.set(cp or "")
        self.var_genero.set(genero or "Masculino")
        self.var_activo.set(activo == "Activo")
        self.var_tipo.set(tipo or "")

        self.imagen_path_actual = imagen_path
        self.archivo_path_actual = archivo_path
        self.var_archivo_lbl.set(
            f"Archivo: {os.path.basename(archivo_path)}" if archivo_path else "Archivo: No adjunto"
        )
        self._mostrar_preview(imagen_path)


if __name__ == "__main__":
    app = App()
    app.resizable(False,False)
    app.iconbitmap("logo_caribe_tkinter.ico")
    app.mainloop()