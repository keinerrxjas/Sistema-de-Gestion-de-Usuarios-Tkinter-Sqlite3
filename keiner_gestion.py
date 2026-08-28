import tkinter as tk
from tkinter import messagebox
import sqlite3
from PIL import Image, ImageTk
import os

os.system("cls")

def ConectarBase():
    conexion = sqlite3.connect("keiner_gestion.db")
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keiner_gestion (
            id INT PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            direccion TEXT NOT NULL,
            correo TEXT NOT NULL,
            telefono VARCHAR(100)
        )
    """)

    conexion.commit()

    return conexion

ventana = tk.Tk()
ventana.title("Gestion de Usuarios")
ventana.geometry("800x500")
ventana.iconbitmap("logo_caribe_tkinter.ico")

imagen = Image.open("logo_caribe_tkinter.ico")
imagen = imagen.resize((40,40))
foto = ImageTk.PhotoImage(imagen)

imagenLabel = tk.Label(ventana, image=foto)
imagenLabel.pack(pady=(10,0))

Titulo = tk.Label(
    ventana,
    text="Sistema Gestion Usuarios",
    font=("Arial", 20, "bold")
)
Titulo.pack(pady=(10, 10))


frame_datos = tk.Frame(ventana)
frame_datos.pack(pady=20)


IDLabel = tk.Label(
    frame_datos,
    text="ID:"
)
IDLabel.grid(row=0, column=0, padx=10, pady=5)

IdEntry = tk.Entry(
    frame_datos,
    width=30
)
IdEntry.grid(row=0, column=1, padx=10, pady=5)

NombreLabel = tk.Label(
    frame_datos,
    text="Nombre:"
)
NombreLabel.grid(row=1, column=0, padx=10, pady=5)

NombreEntry = tk.Entry(
    frame_datos,
    width=30
)
NombreEntry.grid(row=1, column=1, padx=10, pady=5)

ApellidoLabel = tk.Label(
    frame_datos,
    text="Apellido:"
)
ApellidoLabel.grid(row=2, column=0, padx=10, pady=5)

ApellidoEntry = tk.Entry(
    frame_datos,
    width=30
)
ApellidoEntry.grid(row=2, column=1, padx=10, pady=5)

DireccionLabel = tk.Label(
    frame_datos,
    text="Direccion:"
)
DireccionLabel.grid(row=3, column=0, padx=10, pady=5)

DireccionEntry = tk.Entry(
    frame_datos,
    width=30
)
DireccionEntry.grid(row=3, column=1, padx=10, pady=5)

CorreoLabel = tk.Label(
    frame_datos,
    text="Correo:"
)
CorreoLabel.grid(row=4, column=0, padx=10, pady=5)

CorreoEntry = tk.Entry(
    frame_datos,
    width=30
)
CorreoEntry.grid(row=4, column=1, padx=10, pady=5)

NumeroLabel = tk.Label(
    frame_datos,
    text="Número:"
)
NumeroLabel.grid(row=5, column=0, padx=10, pady=5)

NumeroEntry = tk.Entry(
    frame_datos,
    width=30
)
NumeroEntry.grid(row=5, column=1, padx=10, pady=5)

def Guardar(): 
    id = IdEntry.get() 
    nombre = NombreEntry.get() 
    apellido = ApellidoEntry.get()
    direccion = DireccionEntry.get() 
    correo = CorreoEntry.get() 
    numero = NumeroEntry.get() 

    if not id or not nombre or not apellido or not direccion or not correo or not numero:
        messagebox.showerror(
            "Error",
            "Por favor, completa todos los campos"
        )
    

        IdEntry.delete(0, tk.END) 
        NombreEntry.delete(0, tk.END) 
        ApellidoEntry.delete(0, tk.END) 
        DireccionEntry.delete(0,tk.END)
        CorreoEntry.delete(0, tk.END) 
        NumeroEntry.delete(0, tk.END)

        return
 
    conexion = ConectarBase() 
    cursor = conexion.cursor() 
    
    cursor.execute("""
        INSERT INTO keiner_gestion
        (id, nombre, apellido, direccion, correo, telefono)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (id, nombre, apellido, direccion, correo, numero)) 
 
    conexion.commit() 
    conexion.close() 
 
    messagebox.showinfo("Exito", "Usuario Agregado Correctamente") 

    IdEntry.delete(0, tk.END) 
    NombreEntry.delete(0, tk.END) 
    ApellidoEntry.delete(0, tk.END) 
    DireccionEntry.delete(0,tk.END)
    CorreoEntry.delete(0, tk.END) 
    NumeroEntry.delete(0, tk.END)

def Consultar():
    id_usuario =IdEntry.get()

    conexion = ConectarBase()
    cursor = conexion.cursor()

    cursor.execute(
        "SELECT * FROM keiner_gestion WHERE id = ?",
        (id_usuario,)
    )

    busqueda = cursor.fetchone()
    conexion.close()

    if busqueda:

        NombreEntry.delete(0, tk.END) 
        ApellidoEntry.delete(0, tk.END)
        DireccionEntry.delete(0, tk.END)
        CorreoEntry.delete(0, tk.END) 
        NumeroEntry.delete(0, tk.END)

        NombreEntry.insert(0,busqueda[1]) 
        ApellidoEntry.insert(0,busqueda[2])
        DireccionEntry.insert(0,busqueda[3])
        CorreoEntry.insert(0,busqueda[4])
        NumeroEntry.insert(0,busqueda[5])

    elif id_usuario == "":
        messagebox.showwarning("Advertencia","Debes Administrar un ID para buscar")

    else:
        messagebox.showerror(
            "Error",
            f"No existe un usuario con ese ID"
        )

        IdEntry.delete(0, tk.END) 
        NombreEntry.delete(0, tk.END) 
        ApellidoEntry.delete(0, tk.END) 
        DireccionEntry.delete(0,tk.END)
        CorreoEntry.delete(0, tk.END) 
        NumeroEntry.delete(0, tk.END)


def Salir():
    valor = messagebox.askquestion("Salir","¿Desea Salir de la aplicacion?")

    if valor == "yes":
        ventana.destroy()

def EliminarUsuario():
    conexion = ConectarBase()
    cursor = conexion.cursor()

    if IdEntry.get() == "":
        messagebox.showerror("Error","Debes Ingresar un ID")
    else:
        cursor.execute("""
        delete from keiner_gestion
        where id = ?
        """, (IdEntry.get(),))


        conexion.commit()
        messagebox.showwarning("Advertencia","Usuario Eliminado")
        conexion.close()

        IdEntry.delete(0, tk.END) 
        NombreEntry.delete(0, tk.END) 
        ApellidoEntry.delete(0, tk.END) 
        DireccionEntry.delete(0, tk.END)
        CorreoEntry.delete(0, tk.END) 
        NumeroEntry.delete(0, tk.END)
def Actualizar():
    if IdEntry.get() == "":
        messagebox.showwarning(
            "Advertencia",
            "Seleccione un registro"
        )
        return

    conexion = ConectarBase()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE keiner_gestion
        SET
            nombre = ?,
            apellido = ?,
            direccion = ?,
            correo = ?,
            telefono = ?
        Where id = ?

""", (NombreEntry.get(),ApellidoEntry.get(),DireccionEntry.get(),CorreoEntry.get(),NumeroEntry.get(),IdEntry.get()))

    conexion.commit()
    conexion.close()

    messagebox.showinfo("Actualizar", "Informacion Actualizada Correctamente")

    IdEntry.delete(0, tk.END) 
    NombreEntry.delete(0, tk.END) 
    ApellidoEntry.delete(0, tk.END)
    DireccionEntry.delete(0, tk.END)
    CorreoEntry.delete(0, tk.END) 
    NumeroEntry.delete(0, tk.END)


#MENUS
barra_menu = tk.Menu(ventana)

def Contador():
    conexion = ConectarBase()
    cursor = conexion.cursor()

    cursor.execute("select count(*) from keiner_gestion")

    contador = cursor.fetchone()

    messagebox.showinfo("Total de Usuarios",f"Usuarios en Total: {contador[0]}")
    conexion.commit()
    conexion.close()


menu_ayuda = tk.Menu(barra_menu,tearoff=0)
menu_ayuda.add_command(label="Contador de Usuarios", command=lambda: Contador())
barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)

menu_estudiantes = tk.Menu(barra_menu,tearoff=0)
menu_estudiantes.add_command(label="Estudiantes", command=lambda: messagebox.showinfo("Estudiantes","Estudiantes: Keiner Rojas y Juan Rodriguez"))

barra_menu.add_cascade(label="Estudiantes", menu=menu_estudiantes)


ventana.config(menu=barra_menu)


# BOTONES
botones_frame = tk.Frame(ventana)
botones_frame.pack(pady=(15,0))

BotonAgregar = tk.Button(botones_frame,text="Agregar",width=10,command=Guardar)
BotonAgregar.grid(row=0, column=0, padx=5)

BotonConsulta = tk.Button(botones_frame,text="Consultar",width=10,command=Consultar)
BotonConsulta.grid(row=0, column=1, padx=5)

BotonActualizar = tk.Button(botones_frame,text="Actualizar",width=10,command=Actualizar)
BotonActualizar.grid(row=0, column=3, padx=5)

Eliminar = tk.Button(botones_frame,text="Eliminar",width=10,command=EliminarUsuario)
Eliminar.grid(row=0, column=4, padx=5)

Salir = tk.Button(botones_frame,text="Salir",width=10,command=Salir)
Salir.grid(row=0, column=5, padx=5)

ventana.mainloop()