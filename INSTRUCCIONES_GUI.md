# 🎨 INTERFAZ GRÁFICA - GESTOR SEGURO

## 🚀 Cómo Ejecutar

### 1. Instalar dependencias (si aún no lo hiciste)

```powershell
# Activar entorno virtual
.\.venv\Scripts\activate

# Instalar nueva dependencia (pyperclip para copiar al portapapeles)
pip install -r requirements.txt
```

### 2. Ejecutar la interfaz gráfica

```powershell
# Opción 1: Archivo lanzador
python main_gui.py

# Opción 2: Módulo directo
python -m gestor.gui
```

---

## 🎯 Características de la Interfaz

### ✨ Ventana de Login

- **Crear bóveda nueva:** Primera vez o crear nueva bóveda
- **Abrir bóveda existente:** Desbloquear con contraseña maestra
- **Seleccionar archivo:** Puedes cambiar la ubicación de `vault.json`

### 🗄️ Ventana Principal

#### **Gestión de Contraseñas**
- ➕ **Añadir contraseña:** Con generador automático de contraseñas seguras
- 👁️ **Ver detalles:** Doble clic en cualquier entrada
- ✏️ **Editar:** Modificar sitio, usuario, contraseña o notas
- 🗑️ **Eliminar:** Con confirmación para evitar borrados accidentales

#### **Funciones Especiales**
- 🔍 **Búsqueda en tiempo real:** Filtra mientras escribes
- 📋 **Copiar al portapapeles:** Un clic para copiar contraseñas
- 👁️/🙈 **Mostrar/Ocultar:** Toggle para revelar contraseñas
- 🔑 **Cambiar contraseña maestra:** Sin re-cifrar todas las entradas

#### **Interfaz Intuitiva**
- 🎨 Diseño moderno con emojis
- 📊 Barra de estado con información útil
- ⌨️ Atajos de teclado (Enter en login)
- 🔒 Cierre seguro con bloqueo de bóveda

---

## 📸 Guía Visual de Uso

### **Paso 1: Pantalla de Inicio**

```
┌──────────────────────────────────────┐
│      🔐 Gestor Seguro                │
│  Protege tus contraseñas con         │
│  criptografía moderna                │
│                                      │
│  ┌─ Archivo de Bóveda ─────────┐    │
│  │ vault.json                  │    │
│  └─────────────────────────────┘    │
│                                      │
│  ┌─ Contraseña Maestra ────────┐    │
│  │ ●●●●●●●●●●●●               │    │
│  └─────────────────────────────┘    │
│                                      │
│  [🔓 Abrir Bóveda] [✨ Crear Nueva] │
│                                      │
│  💡 Primera vez: haz clic en         │
│     'Crear Nueva'                    │
└──────────────────────────────────────┘
```

### **Paso 2: Ventana Principal**

```
┌────────────────────────────────────────────────────────────┐
│ 🔐 Gestor Seguro - vault.json                              │
├────────────────────────────────────────────────────────────┤
│ [➕ Añadir] [🔄 Actualizar] [🔑 Cambiar Pass]    [🔒 Cerrar]│
│ 🔍 Buscar: [________________]                               │
├────────────────────────────────────────────────────────────┤
│ 🌐 Sitio      │ 👤 Usuario    │ ⚡ Acciones               │
├────────────────────────────────────────────────────────────┤
│ github.com    │ gladys        │ 👁️ Ver  📋 Copiar  ✏️ Editar │
│ gmail.com     │ user@mail.com │ 👁️ Ver  📋 Copiar  ✏️ Editar │
│ facebook.com  │ miuser        │ 👁️ Ver  📋 Copiar  ✏️ Editar │
└────────────────────────────────────────────────────────────┘
│ Total: 3 contraseña(s)                                     │
└────────────────────────────────────────────────────────────┘
```

### **Paso 3: Añadir Contraseña**

```
┌──────────────────────────────────────┐
│ ➕ Añadir Contraseña                  │
├──────────────────────────────────────┤
│ 🌐 Sitio:                             │
│ [github.com________________]          │
│                                       │
│ 👤 Usuario:                           │
│ [miusuario________________]           │
│                                       │
│ 🔑 Contraseña:                        │
│ [__________________] [🎲 Generar]     │
│                                       │
│ 📝 Notas:                             │
│ ┌─────────────────────────┐          │
│ │ Token 2FA: ABCD1234     │          │
│ │                         │          │
│ └─────────────────────────┘          │
│                                       │
│    [💾 Guardar]  [Cancelar]          │
└──────────────────────────────────────┘
```

### **Paso 4: Ver Detalles (Doble Clic)**

```
┌──────────────────────────────────────┐
│ 🔑 github.com                         │
├──────────────────────────────────────┤
│ 🌐 Sitio:       github.com            │
│ 👤 Usuario:     gladys                │
│ 🔑 Contraseña:  [●●●●●●●] [👁️] [📋]  │
│ 📝 Notas:       Token 2FA: ABCD1234  │
│                                       │
│   [✏️ Editar] [🗑️ Eliminar] [Cerrar]  │
└──────────────────────────────────────┘
```

---

## 🎮 Flujo de Trabajo Típico

### **Primera Vez (Crear Bóveda)**

1. Ejecutar `python main_gui.py`
2. Ingresar contraseña maestra (mínimo 8 caracteres)
3. Clic en **✨ Crear Nueva**
4. ¡Listo! Ya puedes añadir contraseñas

### **Uso Diario**

1. Ejecutar `python main_gui.py`
2. Ingresar contraseña maestra
3. Clic en **🔓 Abrir Bóveda**
4. Buscar la contraseña que necesitas
5. Doble clic para ver detalles
6. Clic en **📋** para copiar al portapapeles
7. Pegar donde la necesites (Ctrl+V)

### **Añadir Nueva Contraseña**

1. Clic en **➕ Añadir Contraseña**
2. Rellenar sitio y usuario
3. Clic en **🎲 Generar** para crear contraseña segura
4. (Opcional) Añadir notas
5. Clic en **💾 Guardar**

### **Editar Contraseña Existente**

1. Doble clic en la entrada
2. Clic en **✏️ Editar**
3. Modificar campos necesarios
4. Clic en **💾 Guardar**

### **Cambiar Contraseña Maestra**

1. Clic en **🔑 Cambiar Contraseña Maestra**
2. Ingresar nueva contraseña (2 veces)
3. Clic en **💾 Cambiar**
4. ✅ La próxima vez usa la nueva contraseña

---

## ⌨️ Atajos de Teclado

| Acción | Atajo |
|--------|-------|
| Abrir bóveda (login) | `Enter` |
| Buscar | Click en campo búsqueda |
| Ver detalles | Doble clic en entrada |
| Cerrar ventana de detalles | `Escape` |

---

## 🔒 Seguridad en la Interfaz

### ✅ **Características de Seguridad**

- **Contraseñas ocultas por defecto:** Mostradas como `●●●●●●`
- **Toggle show/hide:** Botón 👁️/🙈 para revelar temporalmente
- **Confirmación de borrado:** Evita eliminaciones accidentales
- **Bloqueo al cerrar:** La bóveda se bloquea automáticamente
- **Clipboard timeout:** El mensaje de copiado desaparece en 3 segundos

### ⚠️ **Buenas Prácticas**

- No dejes la aplicación abierta sin supervisión
- Cierra la bóveda cuando termines (`🔒 Cerrar Bóveda`)
- No tomes capturas de pantalla con contraseñas visibles
- Limpia el portapapeles después de pegar la contraseña

---

## 🛠️ Solución de Problemas

### **Error: "No module named 'tkinter'"**

```powershell
# En Windows, Tkinter viene con Python
# Si falta, reinstala Python marcando "tcl/tk and IDLE"
```

### **Error: "No module named 'pyperclip'"**

```powershell
pip install pyperclip
```

### **Problema: La ventana no aparece centrada**

Esto es normal en algunas configuraciones. La funcionalidad no se ve afectada.

### **Problema: No puedo copiar al portapapeles**

En algunos sistemas, pyperclip necesita xclip o xsel. En Windows normalmente funciona sin problemas.

---

## 🎨 Personalización

### **Cambiar el tamaño de la ventana**

Edita `gestor/gui.py`:

```python
# En LoginWindow.__init__
self.root.geometry("450x350")  # Cambiar estas dimensiones

# En MainWindow.__init__
self.root.geometry("900x600")  # Cambiar estas dimensiones
```

### **Cambiar el archivo de bóveda por defecto**

Edita `gestor/gui.py`:

```python
# En LoginWindow.__init__
self.vault_path = tk.StringVar(value="mi_boveda.json")  # Cambiar nombre
```

### **Cambiar longitud de contraseñas generadas**

Edita `gestor/gui.py`, función `generate_password()`:

```python
pwd = "".join(secrets.choice(alphabet) for _ in range(20))  # Cambiar 20
```

---

## 🆚 CLI vs GUI

| Característica | CLI | GUI |
|----------------|-----|-----|
| Facilidad de uso | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Velocidad | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Búsqueda visual | ❌ | ✅ |
| Copiar al portapapeles | Manual | Un clic |
| Scripts/Automatización | ✅ | ❌ |
| Mostrar/ocultar contraseñas | ❌ | ✅ |
| Para principiantes | ❌ | ✅ |
| Para usuarios avanzados | ✅ | ✅ |

**Recomendación:** 
- **GUI** para uso diario interactivo
- **CLI** para scripts, automatización o servidores sin interfaz gráfica

---

## 🚀 Próximos Pasos

1. **Prueba la interfaz:**
   ```powershell
   python main_gui.py
   ```

2. **Añade algunas contraseñas de prueba**

3. **Explora todas las funciones:**
   - Buscar
   - Copiar
   - Editar
   - Cambiar contraseña maestra

4. **Lee la guía de estudio** (`GUIA_ESTUDIO.md`) para entender cómo funciona internamente

---

## 💡 Tips Útiles

- **Backup:** Copia `vault.json` regularmente
- **Contraseña maestra fuerte:** Usa al menos 12 caracteres
- **Genera contraseñas:** Usa el botón 🎲 para contraseñas seguras
- **Notas útiles:** Guarda tokens 2FA, respuestas secretas, etc.
- **Búsqueda rápida:** Escribe mientras estás en la ventana principal

---

## 🎉 ¡Disfruta tu Gestor Seguro con Interfaz Gráfica!

Ahora puedes gestionar tus contraseñas de forma visual, segura y cómoda.

**¿Preguntas o problemas?** Revisa la `GUIA_ESTUDIO.md` para entender cómo funciona todo internamente.
