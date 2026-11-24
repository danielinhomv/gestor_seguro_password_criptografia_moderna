# 🔑 ¿QUÉ PASA AL CAMBIAR LA CONTRASEÑA MAESTRA?

## 🎯 Respuesta Corta

**Cuando cambias la contraseña maestra:**
- ✅ Se genera una **nueva sal aleatoria**
- ✅ Se deriva una **nueva clave maestra** con la nueva contraseña
- ✅ Se **re-envuelve** la DEK (clave de datos) con la nueva clave maestra
- ✅ **NO se tocan** las contraseñas guardadas (siguen cifradas con la misma DEK)
- ⚡ Es **muy rápido** (1-2 segundos) sin importar cuántas contraseñas tengas

---

## 📊 COMPARACIÓN: Con vs Sin Envelope Encryption

### ❌ **SIN Envelope Encryption (diseño malo)**

```
Contraseña Maestra → KDF → Clave → Cifra TODAS las entradas directamente

Al cambiar contraseña:
1. Generar nueva clave maestra
2. Descifrar TODAS las entradas con clave vieja
3. Re-cifrar TODAS las entradas con clave nueva
4. Guardar TODO en disco

Tiempo: 10,000 entradas × 10ms = 100 segundos ⏱️ (MUY LENTO)
```

### ✅ **CON Envelope Encryption (tu diseño)**

```
Contraseña Maestra → KDF → Clave Maestra → Envuelve → DEK
                                                        ↓
                                            DEK cifra todas las entradas

Al cambiar contraseña:
1. Generar nueva sal
2. Derivar nueva clave maestra
3. Re-envolver LA DEK (un solo objeto pequeño)
4. Guardar solo la cabecera

Tiempo: 1 operación × ~200ms = 0.2 segundos ⚡ (INSTANTÁNEO)
```

---

## 🔄 FLUJO DETALLADO PASO A PASO

### **ANTES del cambio:**

```
vault.json contiene:
{
  "vault_id": "abc-123",
  "kdf": {
    "algorithm": "argon2id",
    "salt": "9a7f3c2e..."  ← Sal ANTIGUA
  },
  "wrapped_key": "AQH3k9..."  ← DEK envuelta con clave ANTIGUA
  "entries": {
    "entry-1": "AQxK7p...",  ← Cifrado con DEK (no cambia)
    "entry-2": "BRyL8q...",  ← Cifrado con DEK (no cambia)
    "entry-3": "CSzM9r..."   ← Cifrado con DEK (no cambia)
  }
}
```

### **DURANTE el cambio:**

#### **Paso 1: Generar nueva sal aleatoria**
```python
# gestor/vault.py - línea 125
new_params = KdfParams.new(
    self._params.algorithm,
    **{k: getattr(self._params, k) for k in (...)}
)
# Internamente llama a:
# generate_salt() → nueva_sal = secrets.token_bytes(16)
```

**Estado:**
- ✅ Nueva sal: `b4c8e1f7...` (diferente a la antigua)

---

#### **Paso 2: Derivar nueva clave maestra**
```python
# gestor/vault.py - línea 128
# Se ejecuta dentro de _wrap_dek():
nueva_clave_maestra = derive_master_key("NuevaPassword2024!", new_params)

# Argon2id procesa:
# - Nueva contraseña: "NuevaPassword2024!"
# - Nueva sal: b4c8e1f7...
# - Mismo trabajo: 3 iter × 64 MB
# → Resultado: nueva_clave_maestra = e5d9f2a3... (32 bytes)
```

**Estado:**
- ✅ Antigua clave maestra: `9a7f3c2e...` (en RAM, se descartará)
- ✅ Nueva clave maestra: `e5d9f2a3...` (en RAM)

---

#### **Paso 3: Separar nueva clave en KEK_enc + KEK_mac**
```python
# gestor/vault.py - línea 65 (dentro de _wrap_dek)
kek_enc, kek_mac = derive_subkeys(nueva_clave_maestra, KEK_PURPOSE)

# HKDF genera:
# → nueva_KEK_enc = f7b3d8...  (32 bytes)
# → nueva_KEK_mac = c2a6e1...  (32 bytes)
```

**Estado:**
- ✅ Nuevas KEK derivadas de la nueva clave maestra

---

#### **Paso 4: Obtener la DEK actual (que NO cambia)**
```python
# gestor/vault.py - línea 127
dek = self._enc_key + self._mac_key  # 64 bytes

# Esta es LA MISMA DEK que se ha usado todo el tiempo
# DEK = a1b2c3d4... (32 bytes) + e5f6g7h8... (32 bytes)
```

**Clave:** ⭐ **La DEK NO cambia, solo se envuelve con nueva clave**

---

#### **Paso 5: Re-envolver la DEK con las nuevas KEK**
```python
# gestor/vault.py - línea 128
self._wrapped_dek = _wrap_dek(nueva_password, new_params, self._vault_id, dek)

# Internamente hace:
# 1. Genera IV aleatorio: iv_nuevo = secrets.token_bytes(16)
# 2. Cifra DEK con nueva_KEK_enc:
#    ciphertext = AES-256-CBC(nueva_KEK_enc, iv_nuevo, dek)
# 3. Calcula HMAC con nueva_KEK_mac:
#    hmac = HMAC-SHA256(nueva_KEK_mac, version|AD|iv_nuevo|ciphertext)
# 4. Resultado: wrapped_dek_nueva = version|iv_nuevo|ciphertext|hmac
```

**Estado:**
- ✅ Nueva DEK envuelta: `AQJ5m3...` (diferente blob, pero contiene la misma DEK)
- ✅ Antigua DEK envuelta: `AQH3k9...` (se descarta)
- ⭐ **DEK interna:** Sigue siendo `a1b2c3d4...` (NO cambió)

---

#### **Paso 6: Actualizar parámetros y guardar**
```python
# gestor/vault.py - líneas 129-130
self._params = new_params      # Nuevos parámetros (incluye nueva sal)
self.save()                    # Guardar en vault.json
```

**Estado en disco:**
```json
{
  "vault_id": "abc-123",         ← Igual
  "kdf": {
    "algorithm": "argon2id",     ← Igual
    "salt": "b4c8e1f7..."        ← ⭐ NUEVA SAL
  },
  "wrapped_key": "AQJ5m3..."     ← ⭐ NUEVA DEK ENVUELTA
  "entries": {
    "entry-1": "AQxK7p...",      ← ✅ NO CAMBIÓ (mismo ciphertext)
    "entry-2": "BRyL8q...",      ← ✅ NO CAMBIÓ (mismo ciphertext)
    "entry-3": "CSzM9r..."       ← ✅ NO CAMBIÓ (mismo ciphertext)
  }
}
```

---

### **DESPUÉS del cambio:**

#### **Al abrir con la NUEVA contraseña:**

```python
# Usuario escribe: "NuevaPassword2024!"

# 1. Leer parámetros del disco:
params = {
    "salt": "b4c8e1f7...",       ← La nueva sal
    "algorithm": "argon2id",
    ...
}

# 2. Derivar clave maestra:
clave_maestra = derive_master_key("NuevaPassword2024!", params)
# → Resultado: e5d9f2a3... (misma que se usó para envolver)

# 3. Derivar KEK:
kek_enc, kek_mac = derive_subkeys(clave_maestra, KEK_PURPOSE)

# 4. Desenvolver DEK:
dek = decrypt(kek_enc, kek_mac, wrapped_dek, AD)
# → Verifica HMAC ✓
# → Descifra: dek = a1b2c3d4... (¡LA MISMA DEK de siempre!)

# 5. Usar DEK para descifrar entradas:
entry_1 = decrypt(dek[:32], dek[32:], "AQxK7p...", AD)
# → Funciona porque "AQxK7p..." se cifró con la misma DEK
```

**✅ Resultado:** Todo funciona normal, las contraseñas se recuperan correctamente.

---

#### **Al intentar abrir con la ANTIGUA contraseña:**

```python
# Usuario escribe (por error): "MiPassword2024!"

# 1. Leer parámetros del disco:
params = {
    "salt": "b4c8e1f7...",       ← La nueva sal
    ...
}

# 2. Derivar clave maestra:
clave_maestra = derive_master_key("MiPassword2024!", params)
# → Resultado: x9y8z7... (DIFERENTE, porque contraseña + sal diferentes)

# 3. Derivar KEK:
kek_enc, kek_mac = derive_subkeys(clave_maestra, KEK_PURPOSE)
# → KEK erróneas

# 4. Intentar desenvolver DEK:
dek = decrypt(kek_enc, kek_mac, wrapped_dek, AD)
# → Calcula HMAC con KEK_mac errónea
# → HMAC NO coincide con el guardado
# → ❌ raise InvalidPasswordError("Contraseña incorrecta")
```

**❌ Resultado:** No puede abrir la bóveda (como debe ser).

---

## 🧪 DEMOSTRACIÓN PRÁCTICA

### **Prueba 1: Cambiar contraseña**

```python
from gestor import Vault, FileStorage

# 1. Crear bóveda con contraseña "antigua123"
storage = FileStorage("test.json")
with Vault.create(storage, "antigua123") as v:
    id1 = v.add_entry("github.com", "user", "pass123")
    id2 = v.add_entry("gmail.com", "user", "pass456")

# 2. Cambiar contraseña a "nueva456"
with Vault.open(storage, "antigua123") as v:
    v.change_master_password("nueva456")
    # ⚡ Rápido: solo re-envuelve 1 DEK

# 3. Abrir con nueva contraseña
with Vault.open(storage, "nueva456") as v:
    print(v.get_entry(id1))  # ✅ Funciona
    print(v.get_entry(id2))  # ✅ Funciona

# 4. Intentar abrir con antigua contraseña
try:
    Vault.open(storage, "antigua123")  # ❌ Falla
except Exception as e:
    print(f"Error: {e}")  # "Contraseña incorrecta"
```

### **Prueba 2: Medir velocidad**

```python
import time
from gestor import Vault, FileStorage

storage = FileStorage("velocidad.json")
with Vault.create(storage, "pass123") as v:
    # Añadir 100 contraseñas
    for i in range(100):
        v.add_entry(f"sitio{i}.com", f"user{i}", f"pass{i}")

# Medir tiempo de cambio
with Vault.open(storage, "pass123") as v:
    inicio = time.time()
    v.change_master_password("nueva_pass_segura")
    fin = time.time()
    print(f"Tiempo: {fin - inicio:.3f} segundos")
    # Resultado típico: 0.200 segundos
    # ⚡ Independiente del número de entradas
```

---

## 📊 TABLA COMPARATIVA

| Aspecto | Sin Envelope | Con Envelope (tu proyecto) |
|---------|--------------|----------------------------|
| **Qué se re-cifra** | Todas las entradas | Solo la DEK |
| **Tiempo con 10 entradas** | ~1 segundo | ~0.2 segundos |
| **Tiempo con 1,000 entradas** | ~100 segundos | ~0.2 segundos |
| **Tiempo con 10,000 entradas** | ~1,000 segundos | ~0.2 segundos |
| **Crece con más entradas** | ❌ Sí, linealmente | ✅ No, constante |
| **Cambios en disco** | Todo el archivo | Solo cabecera |
| **Riesgo de corrupción** | ❌ Alto | ✅ Bajo |

---

## 🔐 SEGURIDAD AL CAMBIAR CONTRASEÑA

### ✅ **Qué se mantiene seguro:**

1. **Las contraseñas guardadas:** Siguen cifradas con la misma DEK
2. **Nueva sal:** Protege contra ataques de tablas precalculadas
3. **Nueva derivación:** Argon2id/PBKDF2 se ejecuta completo otra vez
4. **Mismo nivel de seguridad:** No se degrada al cambiar

### ✅ **Qué mejora:**

1. **Nueva sal aleatoria:** Si alguien tenía rainbow tables para la sal antigua, ya no sirven
2. **Nuevo HMAC:** El wrapped_key tiene nuevo tag de autenticación
3. **Nuevo IV:** El cifrado de la DEK usa nuevo IV aleatorio

### ⚠️ **Qué NO cambia:**

1. **La DEK interna:** Es la misma (por diseño, para no re-cifrar todo)
2. **Los ciphertexts de entradas:** Son exactamente los mismos bytes
3. **El vault_id:** Identificador único de la bóveda

---

## 🎯 VENTAJAS DEL ENVELOPE ENCRYPTION

### 1️⃣ **Velocidad**
- Cambiar contraseña = 0.2 segundos
- No importa si tienes 10 o 10,000 entradas

### 2️⃣ **Seguridad**
- Si te roban el disco y lo analizas 2 veces (antes y después del cambio):
  - Las entradas tienen el mismo ciphertext
  - Pero NO puedes derivar nada útil de eso
  - Necesitas romper Argon2id (prácticamente imposible)

### 3️⃣ **Integridad**
- Solo se modifica la cabecera del archivo
- Menos probabilidad de corrupción
- Si falla el cambio, las entradas siguen intactas

### 4️⃣ **Rotación de contraseñas**
- Puedes cambiar tu contraseña maestra regularmente
- Sin penalización de rendimiento

---

## 💡 ANALOGÍA DEL MUNDO REAL

Imagina que tienes una **caja fuerte** (DEK) con todas tus joyas (contraseñas) dentro.

### ❌ **Sin Envelope Encryption:**
```
Contraseña → Abre CADA joya individualmente

Al cambiar contraseña:
1. Sacar TODAS las joyas
2. Ponerlas en una nueva caja con nueva llave
3. Volver a guardar TODO
⏱️ Si tienes 10,000 joyas = horas de trabajo
```

### ✅ **Con Envelope Encryption:**
```
Contraseña → Abre la caja fuerte → Caja contiene todas las joyas

Al cambiar contraseña:
1. La caja fuerte sigue cerrada con su propia llave (DEK)
2. Solo cambias la LLAVE MAESTRA que abre la caja fuerte
3. Las joyas adentro ni se enteran
⚡ Tiempo: segundos, sin importar cuántas joyas
```

---

## 🔬 VERIFICACIÓN EN EL CÓDIGO

### **Método que hace el cambio:**

```python
# gestor/vault.py - líneas 123-130
def change_master_password(self, new_password: str) -> None:
    """Nueva sal + re-envoltura de la DEK. Las entradas no se re-cifran."""
    self._require_unlocked()
    
    # 1. Generar nuevos parámetros con nueva sal
    new_params = KdfParams.new(
        self._params.algorithm,
        **{k: getattr(self._params, k)
           for k in ("time_cost", "memory_cost", "parallelism", "iterations")})
    
    # 2. Obtener DEK actual (que NO cambia)
    dek = self._enc_key + self._mac_key
    
    # 3. Re-envolver DEK con nueva contraseña
    self._wrapped_dek = _wrap_dek(new_password, new_params, self._vault_id, dek)
    
    # 4. Actualizar parámetros y guardar
    self._params = new_params
    self.save()
    
    # ⚠️ NOTA: self._entries NO se toca
```

### **Lo que NO hace:**

```python
# ❌ Este código NO existe (y no debe existir):
def change_master_password_MALO(self, new_password: str):
    # NO hace esto:
    for entry_id, blob in self._entries.items():
        old_plaintext = decrypt(OLD_dek, blob)  # ❌
        new_ciphertext = encrypt(NEW_dek, old_plaintext)  # ❌
        self._entries[entry_id] = new_ciphertext  # ❌
```

---

## 🎓 RESUMEN FINAL

**Al cambiar la contraseña maestra:**

✅ **Qué CAMBIA:**
- Sal aleatoria (nueva)
- Clave maestra derivada (nueva)
- KEK (claves de envoltura, nuevas)
- DEK envuelta (nuevo blob cifrado)
- HMAC de la DEK envuelta (nuevo tag)

❌ **Qué NO CAMBIA:**
- DEK interna (misma)
- Ciphertexts de entradas (mismos)
- Número de entradas (mismo)
- Vault ID (mismo)

⚡ **Resultado:**
- Proceso rápido (~0.2 segundos)
- Seguridad mantenida
- Contraseñas intactas
- Archivo mínimamente modificado

---

## 🚀 PRUÉBALO TÚ MISMO

### **En la GUI:**

1. Abre la bóveda: `python main_gui.py`
2. Añade 3-4 contraseñas
3. Clic en **"🔑 Cambiar Contraseña Maestra"**
4. Nueva contraseña: `NuevaSuperPass2024!`
5. Repite: `NuevaSuperPass2024!`
6. Clic en **"💾 Cambiar"**
7. Cierra todo
8. Abre otra vez con la **nueva** contraseña
9. ✅ Todas tus contraseñas siguen ahí

### **En la CLI:**

```powershell
# Crear y añadir
python -m gestor.cli init
python -m gestor.cli add github.com user1 --generate 20
python -m gestor.cli add gmail.com user2 --generate 20

# Cambiar contraseña maestra
python -m gestor.cli passwd

# Verificar que funciona
python -m gestor.cli list
python -m gestor.cli get github
```

---

**¿Necesitas más detalles sobre algún paso específico?** 🔑
