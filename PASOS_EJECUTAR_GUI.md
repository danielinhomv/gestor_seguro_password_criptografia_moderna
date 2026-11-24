# 🚀 CÓMO EJECUTAR Y PROBAR LA INTERFAZ GRÁFICA

## ✅ PASO 1: EJECUTAR LA INTERFAZ

### Opción A: Doble clic en el archivo (MÁS FÁCIL)

```
1. Ve a la carpeta del proyecto
2. Busca el archivo: INICIAR_GUI.bat
3. Haz DOBLE CLIC en él
4. ¡Se abrirá la ventana!
```

### Opción B: Desde PowerShell (RECOMENDADO)

```powershell
# 1. Abre PowerShell en la carpeta del proyecto
# 2. Activa el entorno virtual
.\.venv\Scripts\activate

# 3. Ejecuta la interfaz
python main_gui.py
```

### Opción C: Comando completo (SIN ACTIVAR ENTORNO)

```powershell
# En la carpeta del proyecto:
.\.venv\Scripts\python main_gui.py
```

---

## 🧪 PASO 2: PRUEBA COMPLETA DE FUNCIONALIDAD

### 📝 TEST 1: CREAR BÓVEDA (Primera vez)

**Qué hacer:**
1. Se abre una ventana que dice "🔐 Gestor Seguro"
2. En "Contraseña Maestra" escribe: `MiPassword2024!`
3. Haz clic en el botón **"✨ Crear Nueva"**

**Resultado esperado:**
✅ Aparece mensaje: "Bóveda creada en: C:\Users\gladys\gestor-seguro\vault.json"
✅ Se abre la ventana principal (vacía por ahora)

**Si falla:** Revisa que la contraseña tenga al menos 8 caracteres

---

### 📝 TEST 2: AÑADIR PRIMERA CONTRASEÑA

**Qué hacer:**
1. En la ventana principal, clic en **"➕ Añadir Contraseña"**
2. Aparece un formulario, llénalo así:
   - 🌐 Sitio: `github.com`
   - 👤 Usuario: `gladys`
   - 🔑 Contraseña: Haz clic en **"🎲 Generar"** (genera automática)
   - 📝 Notas: `Mi cuenta principal de GitHub`
3. Clic en **"💾 Guardar"**

**Resultado esperado:**
✅ Mensaje: "Contraseña guardada para: github.com"
✅ Aparece una fila en la tabla con: `github.com | gladys | 👁️ Ver 📋 Copiar ✏️ Editar 🗑️ Eliminar`
✅ Abajo dice: "Total: 1 contraseña(s)"

---

### 📝 TEST 3: AÑADIR MÁS CONTRASEÑAS

**Qué hacer:**
Repite el TEST 2 con estos datos:

**Segunda contraseña:**
- Sitio: `gmail.com`
- Usuario: `gladys@gmail.com`
- Generar contraseña automática

**Tercera contraseña:**
- Sitio: `facebook.com`
- Usuario: `gladys.dev`
- Generar contraseña automática

**Resultado esperado:**
✅ Ahora hay 3 filas en la tabla
✅ Abajo dice: "Total: 3 contraseña(s)"

---

### 📝 TEST 4: VER DETALLES DE UNA CONTRASEÑA

**Qué hacer:**
1. Haz **DOBLE CLIC** en la fila de `github.com`
2. Se abre una ventana con todos los detalles

**Resultado esperado:**
✅ Muestra:
   - 🌐 Sitio: github.com
   - 👤 Usuario: gladys
   - 🔑 Contraseña: ●●●●●●●●●● (oculta)
   - 📝 Notas: Mi cuenta principal de GitHub

---

### 📝 TEST 5: MOSTRAR/OCULTAR CONTRASEÑA

**Qué hacer:**
1. En la ventana de detalles (del TEST 4)
2. Haz clic en el botón **"👁️"** al lado de la contraseña

**Resultado esperado:**
✅ La contraseña se revela (ej: `Kx9#mP2@qL4$wR7^nT1!zY8%`)
✅ El botón cambia a **"🙈"**
✅ Si vuelves a hacer clic, se oculta otra vez

---

### 📝 TEST 6: COPIAR CONTRASEÑA AL PORTAPAPELES

**Qué hacer:**
1. En la ventana de detalles (con github.com abierto)
2. Haz clic en el botón **"📋"** al lado de la contraseña
3. Abre el Bloc de notas (Notepad)
4. Pega con `Ctrl + V`

**Resultado esperado:**
✅ Mensaje en la barra inferior: "✓ Contraseña copiado al portapapeles"
✅ En el Bloc de notas aparece la contraseña completa
✅ El mensaje desaparece después de 3 segundos

---

### 📝 TEST 7: BUSCAR CONTRASEÑAS

**Qué hacer:**
1. Cierra la ventana de detalles
2. En la ventana principal, en el campo **"🔍 Buscar:"** escribe: `git`
3. Escribe: `gmail`
4. Borra el texto

**Resultado esperado:**
✅ Al escribir "git": Solo aparece github.com
✅ Al escribir "gmail": Solo aparece gmail.com
✅ Al borrar: Aparecen las 3 contraseñas otra vez
✅ La barra dice: "Mostrando X de 3 contraseñas"

---

### 📝 TEST 8: EDITAR UNA CONTRASEÑA

**Qué hacer:**
1. Haz doble clic en `facebook.com`
2. Clic en **"✏️ Editar"**
3. Cambia el usuario a: `gladys.facebook`
4. En notas escribe: `Cuenta personal`
5. Clic en **"💾 Guardar"**

**Resultado esperado:**
✅ Mensaje: "Contraseña actualizada"
✅ En la tabla, facebook.com ahora muestra usuario: `gladys.facebook`
✅ Si abres detalles, las notas dicen "Cuenta personal"

---

### 📝 TEST 9: ELIMINAR UNA CONTRASEÑA

**Qué hacer:**
1. Haz doble clic en `facebook.com`
2. Clic en **"🗑️ Eliminar"**
3. Aparece confirmación: "¿Eliminar contraseña de...?"
4. Clic en **"Yes"**

**Resultado esperado:**
✅ Mensaje: "Contraseña eliminada"
✅ Ya no aparece facebook.com en la tabla
✅ Ahora hay solo 2 contraseñas
✅ Barra dice: "Total: 2 contraseña(s)"

---

### 📝 TEST 10: CERRAR Y REABRIR BÓVEDA

**Qué hacer:**
1. En la ventana principal, clic en **"🔒 Cerrar Bóveda"**
2. Confirma que quieres cerrar: clic en **"Yes"**
3. Se cierra todo
4. Ejecuta otra vez: `python main_gui.py`
5. En "Contraseña Maestra" escribe: `MiPassword2024!`
6. Clic en **"🔓 Abrir Bóveda"**

**Resultado esperado:**
✅ La bóveda se abre
✅ Siguen apareciendo las 2 contraseñas (github y gmail)
✅ ¡Todo se guardó correctamente!

---

### 📝 TEST 11: CONTRASEÑA INCORRECTA

**Qué hacer:**
1. Cierra todo
2. Ejecuta: `python main_gui.py`
3. Escribe una contraseña INCORRECTA: `wrongpass123`
4. Clic en **"🔓 Abrir Bóveda"**

**Resultado esperado:**
✅ Aparece error: "❌ Contraseña incorrecta"
✅ El campo de contraseña se borra
✅ La bóveda NO se abre

---

### 📝 TEST 12: CAMBIAR CONTRASEÑA MAESTRA

**Qué hacer:**
1. Abre la bóveda con la contraseña correcta
2. Clic en **"🔑 Cambiar Contraseña Maestra"**
3. Nueva contraseña: `NuevaPass2024!`
4. Repetir: `NuevaPass2024!`
5. Clic en **"💾 Cambiar"**
6. Cierra todo
7. Ejecuta otra vez e intenta abrir con `NuevaPass2024!`

**Resultado esperado:**
✅ Mensaje: "Contraseña maestra cambiada"
✅ Al reabrir con la nueva contraseña: funciona
✅ Si intentas con la antigua (`MiPassword2024!`): error
✅ Las contraseñas guardadas siguen ahí (github y gmail)

---

### 📝 TEST 13: GENERADOR DE CONTRASEÑAS

**Qué hacer:**
1. Clic en **"➕ Añadir Contraseña"**
2. Haz clic en **"🎲 Generar"** varias veces
3. Observa cómo cambia la contraseña generada

**Resultado esperado:**
✅ Cada vez genera una contraseña diferente
✅ Tiene ~20 caracteres
✅ Incluye letras, números y símbolos (ej: `Kx9#mP2@qL4$wR7^nT1!`)

---

### 📝 TEST 14: BOTÓN ACTUALIZAR

**Qué hacer:**
1. Con la bóveda abierta
2. Clic en **"🔄 Actualizar"**

**Resultado esperado:**
✅ La lista se recarga
✅ Sigue mostrando todas las contraseñas

---

## 🎯 CHECKLIST FINAL

Marca cada test que completes:

- [ ] TEST 1: Crear bóveda ✅
- [ ] TEST 2: Añadir primera contraseña ✅
- [ ] TEST 3: Añadir más contraseñas ✅
- [ ] TEST 4: Ver detalles ✅
- [ ] TEST 5: Mostrar/ocultar contraseña ✅
- [ ] TEST 6: Copiar al portapapeles ✅
- [ ] TEST 7: Buscar contraseñas ✅
- [ ] TEST 8: Editar contraseña ✅
- [ ] TEST 9: Eliminar contraseña ✅
- [ ] TEST 10: Cerrar y reabrir ✅
- [ ] TEST 11: Contraseña incorrecta ✅
- [ ] TEST 12: Cambiar contraseña maestra ✅
- [ ] TEST 13: Generador de contraseñas ✅
- [ ] TEST 14: Botón actualizar ✅

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Problema: "No se abre ninguna ventana"

**Solución:**
```powershell
# Verifica que las dependencias estén instaladas
.\.venv\Scripts\python -m pip list

# Deberías ver:
# cryptography, argon2-cffi, pytest, pyperclip

# Si falta alguna:
.\.venv\Scripts\pip install -r requirements.txt
```

### Problema: "ModuleNotFoundError: No module named 'tkinter'"

**Solución:**
Tkinter viene con Python. Si falta, reinstala Python desde python.org marcando la opción "tcl/tk and IDLE".

### Problema: "No se puede copiar al portapapeles"

**Solución:**
En algunos sistemas pyperclip puede fallar. Es un problema menor, el resto funciona.

### Problema: "La ventana se ve cortada o pequeña"

**Solución:**
Esto es normal en algunas resoluciones. Puedes editar `gestor/gui.py` y cambiar:
```python
self.root.geometry("900x600")  # Cambiar a 1000x700 por ejemplo
```

---

## 📸 CAPTURAS ESPERADAS

### Ventana de Login:
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
│  │ [ingresa aquí]              │    │
│  └─────────────────────────────┘    │
│                                      │
│  [🔓 Abrir Bóveda] [✨ Crear Nueva] │
└──────────────────────────────────────┘
```

### Ventana Principal (con 3 contraseñas):
```
┌────────────────────────────────────────────────┐
│ 🔐 Gestor Seguro - vault.json                  │
├────────────────────────────────────────────────┤
│ [➕ Añadir] [🔄 Actualizar] [🔑 Cambiar Pass]  │
│ 🔍 Buscar: [________]              [🔒 Cerrar] │
├────────────────────────────────────────────────┤
│ github.com    │ gladys        │ 👁️ Ver 📋 ...  │
│ gmail.com     │ gladys@...    │ 👁️ Ver 📋 ...  │
│ facebook.com  │ gladys.dev    │ 👁️ Ver 📋 ...  │
├────────────────────────────────────────────────┤
│ Total: 3 contraseña(s)                         │
└────────────────────────────────────────────────┘
```

---

## 🎉 ¡TODO LISTO!

Si completaste todos los tests, tu interfaz gráfica funciona **PERFECTAMENTE**.

**Ahora puedes:**
- Usar el gestor para tus contraseñas reales
- Leer `GUIA_ESTUDIO.md` para entender cómo funciona internamente
- Leer `INSTRUCCIONES_GUI.md` para tips avanzados

**Siguiente paso:** Haz backup de `vault.json` regularmente ⚠️
