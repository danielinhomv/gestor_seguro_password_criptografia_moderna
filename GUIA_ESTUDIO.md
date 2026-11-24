# 📚 GUÍA DE ESTUDIO - GESTOR SEGURO DE CONTRASEÑAS

## 🎯 ¿QUÉ ES ESTE PROGRAMA?

Es un **gestor de contraseñas** (como LastPass, 1Password, Bitwarden) que guardas tus contraseñas de forma **ultra segura** usando criptografía moderna.

**La idea simple:**
- Tienes UNA contraseña maestra que recuerdas
- El programa guarda TODAS tus otras contraseñas cifradas
- Solo tú puedes descifrarlas con tu contraseña maestra

---

## 🧩 ¿POR QUÉ TANTOS ARCHIVOS?

Cada archivo tiene **UNA responsabilidad específica** (principio de diseño: "separación de responsabilidades"). Es como construir con LEGO: cada pieza hace una cosa, pero juntas hacen algo complejo.

### 📂 ESTRUCTURA DEL PROYECTO

```
gestor-seguro/
│
├── gestor/                    ← Carpeta con el código principal
│   ├── errors.py             ← 🚨 Define los tipos de errores
│   ├── kdf.py                ← 🔑 Convierte contraseña → clave criptográfica
│   ├── cipher.py             ← 🔒 Cifra y descifra información
│   ├── storage.py            ← 💾 Guarda archivos en disco
│   ├── vault.py              ← 🗄️ La "bóveda" que gestiona todo
│   └── cli.py                ← ⌨️ Interfaz de línea de comandos
│
├── tests/                     ← Pruebas automáticas
├── ejemplo.py                 ← Demostración educativa
├── requirements.txt           ← Librerías necesarias
└── README.md                  ← Documentación técnica
```

---

## 📖 EXPLICACIÓN ARCHIVO POR ARCHIVO

### 1️⃣ **`errors.py`** - Los Mensajes de Error

**¿Qué hace?**
Define los diferentes tipos de errores que pueden ocurrir.

**¿Por qué existe?**
Para que el programa pueda decirte **exactamente** qué salió mal, pero sin revelar información sensible a un atacante.

**Errores que define:**
```python
GestorError              → Error general
IntegrityError           → Los datos fueron manipulados
InvalidPasswordError     → Contraseña incorrecta
VaultFormatError         → Archivo corrupto
WeakParametersError      → Configuración insegura
EntryNotFoundError       → Contraseña no existe
```

**Ejemplo práctico:**
```python
# Si intentas abrir con contraseña incorrecta:
raise InvalidPasswordError("Contraseña maestra incorrecta")

# Si alguien modificó el archivo cifrado:
raise IntegrityError("Datos manipulados")
```

**🎓 Concepto clave:** Los mensajes son **genéricos a propósito** para no dar pistas a un atacante.

---

### 2️⃣ **`kdf.py`** - Key Derivation Function (Función de Derivación de Claves)

**¿Qué hace?**
Convierte tu contraseña (ej: "MiContraseña123") en una **clave criptográfica** (números aleatorios).

**¿Por qué existe?**
Las contraseñas son débiles y predecibles. Las claves criptográficas deben ser:
- Exactamente 256 bits de longitud
- Completamente aleatorias
- Imposibles de adivinar

**Componentes principales:**

#### a) **Sal (Salt)**
```python
salt = generate_salt()  # 16 bytes aleatorios
```
**¿Qué es?** Números aleatorios únicos para cada usuario.
**¿Para qué?** Dos personas con la misma contraseña tendrán claves distintas.

#### b) **Argon2id** (algoritmo moderno, recomendado)
```python
master_key = derive_master_key("MiContraseña", params)
```
**¿Qué hace?** Aplica un algoritmo MUY lento y costoso a propósito.
**¿Para qué?** Que un atacante tarde AÑOS en probar millones de contraseñas.

**Parámetros de Argon2id:**
```python
time_cost = 3         # Iteraciones (más = más lento)
memory_cost = 64 MB   # RAM necesaria (más = más difícil)
parallelism = 4       # Núcleos CPU (más = más difícil)
```

#### c) **HKDF** (derivación de subclaves)
```python
enc_key, mac_key = derive_subkeys(master_key, b"proposito")
```
**¿Qué hace?** De UNA clave maestra genera VARIAS claves diferentes.
**¿Para qué?** NUNCA usar la misma clave para cifrar y autenticar (regla de oro).

**📊 Diagrama del flujo:**
```
"MiContraseña123"  +  sal aleatoria
        |
        v
    Argon2id (lentísimo, 3 iteraciones × 64 MB)
        |
        v
   clave_maestra (32 bytes)
        |
        v
      HKDF
        |
        +---> clave_cifrado (32 bytes)
        |
        +---> clave_mac (32 bytes)
```

**🎓 Conceptos clave:**
- **Sal:** Evita ataques con tablas precalculadas
- **Iteraciones:** Hacen la derivación LENTA a propósito
- **Separación de claves:** Cada clave tiene un solo propósito

---

### 3️⃣ **`cipher.py`** - Cifrado y Descifrado

**¿Qué hace?**
Cifra (oculta) y descifra (revela) información usando **AES-256-CBC**.

**¿Por qué existe?**
Para que nadie pueda leer tus contraseñas sin tu clave.

**Componentes:**

#### a) **AES-256-CBC** (cifrado)
```python
ciphertext = AES.encrypt(key, plaintext, IV)
```
**¿Qué es?** Algoritmo de cifrado estándar militar.
**256 bits:** Tamaño de la clave (imposible romper por fuerza bruta).
**CBC:** Modo de operación (cada bloque depende del anterior).

#### b) **IV (Vector de Inicialización)**
```python
iv = secrets.token_bytes(16)  # Aleatorio cada vez
```
**¿Qué es?** 16 bytes aleatorios que se usan UNA sola vez.
**¿Para qué?** Cifrar el mismo texto dos veces da resultados diferentes.

#### c) **HMAC-SHA256** (autenticación)
```python
tag = hmac.new(mac_key, data, sha256).digest()
```
**¿Qué es?** "Firma digital" que verifica que nadie tocó los datos.
**¿Para qué?** Detectar si alguien modificó aunque sea un bit.

#### d) **Encrypt-then-MAC** (el orden importa)
```python
# 1. Cifrar
ciphertext = encrypt(plaintext)

# 2. LUEGO calcular HMAC
tag = hmac(ciphertext)

# 3. Al descifrar, primero verificar HMAC
if not verify_hmac(tag):
    raise IntegrityError("¡Datos manipulados!")
# 4. Solo si el HMAC es válido, descifrar
plaintext = decrypt(ciphertext)
```

**¿Por qué este orden?** Evita el ataque "padding oracle" (muy peligroso).

**📦 Formato del blob cifrado:**
```
+--------+------+-------------+------+
| v (1B) |  IV  | ciphertext  | HMAC |
|        | 16B  |  múltiplo   | 32B  |
|        |      |  de 16      |      |
+--------+------+-------------+------+
   |       |         |           |
versión  aleatorio  datos      firma
                   cifrados   digital
```

**🎓 Conceptos clave:**
- **AES:** Cifrado simétrico (misma clave cifra y descifra)
- **IV aleatorio:** Esencial para seguridad de CBC
- **HMAC primero:** Verifica antes de descifrar (evita ataques)
- **Associated Data (AD):** Contexto autenticado pero no cifrado

---

### 4️⃣ **`storage.py`** - Almacenamiento en Disco

**¿Qué hace?**
Guarda y lee archivos del disco duro.

**¿Por qué existe?**
Separar la lógica de almacenamiento permite cambiar DÓNDE guardas (archivo, base de datos, nube) sin tocar el resto del código.

**Dos implementaciones:**

#### a) **FileStorage** (archivo local)
```python
storage = FileStorage("vault.json")
storage.write(data)  # Guarda en disco
data = storage.read() # Lee desde disco
```

**Característica especial:** Escritura atómica
```python
# 1. Escribe en archivo temporal
with open("vault.json.tmp", "wb") as f:
    f.write(data)
    f.flush()
    os.fsync(f.fileno())  # Fuerza escritura al disco

# 2. Reemplaza el archivo original (operación atómica)
os.replace("vault.json.tmp", "vault.json")
```
**¿Por qué?** Si se corta la luz, o tienes el archivo completo original o el nuevo completo. NUNCA un archivo a medias.

#### b) **MemoryStorage** (en RAM)
```python
storage = MemoryStorage()  # Solo para tests
```
**¿Para qué?** Probar el código sin tocar el disco.

**🎓 Concepto clave:**
- **Backend intercambiable:** Puedes guardar en S3, Google Drive, servidor remoto solo cambiando el StorageBackend.
- **Conocimiento cero:** El storage solo ve bytes cifrados, no sabe qué contienen.

---

### 5️⃣ **`vault.py`** - La Bóveda (el cerebro del programa)

**¿Qué hace?**
Coordina TODO: crear bóvedas, añadir/buscar/borrar contraseñas, cambiar contraseña maestra.

**¿Por qué existe?**
Es el "pegamento" que une todos los otros módulos.

**Arquitectura: Envelope Encryption (cifrado de sobre)**

```
Contraseña Maestra "MiPass123"
        |
        v (KDF con sal)
  Clave Maestra (32 bytes) ← Solo existe en RAM, NUNCA se guarda
        |
        v (HKDF)
  KEK (Key Encryption Key) = 64 bytes
        |
        v (cifra con AES+HMAC)
  DEK envuelta ← Esto SÍ se guarda en vault.json
        |
        v (se desenvuelve en RAM)
  DEK (Data Encryption Key) = 64 bytes ← Clave aleatoria generada UNA vez
        |
        v (cifra TODAS las entradas)
  Entrada 1 cifrada
  Entrada 2 cifrada
  Entrada 3 cifrada
  ...
```

**🤔 ¿Por qué tantas claves?**

**Sin envelope encryption:**
```
Cambiar contraseña maestra → Re-cifrar TODAS las entradas (lento!)
```

**Con envelope encryption:**
```
Cambiar contraseña maestra → Solo re-envolver la DEK (rápido!)
Las entradas quedan igual, cifradas con la misma DEK
```

**Métodos principales:**

#### 1. **Crear bóveda**
```python
vault = Vault.create(storage, "MiPassMaestra")
```
**Qué hace:**
1. Genera sal aleatoria
2. Deriva clave maestra de la contraseña
3. Genera DEK aleatoria (64 bytes)
4. Envuelve DEK con la clave maestra
5. Guarda: vault_id + sal + KDF_params + DEK_envuelta

#### 2. **Abrir bóveda**
```python
vault = Vault.open(storage, "MiPassMaestra")
```
**Qué hace:**
1. Lee vault.json del disco
2. Deriva clave maestra (con sal guardada)
3. Desenvuelve DEK verificando HMAC
4. Si el HMAC falla → contraseña incorrecta

#### 3. **Añadir entrada**
```python
entry_id = vault.add_entry("github.com", "usuario", "pass123")
```
**Qué hace:**
1. Crea JSON: `{"site": "github.com", "username": "...", "password": "..."}`
2. Cifra JSON con DEK
3. Calcula HMAC con AD = `vault_id|entry_id`
4. Guarda blob cifrado

#### 4. **Recuperar entrada**
```python
entry = vault.get_entry(entry_id)
print(entry["password"])  # "pass123"
```
**Qué hace:**
1. Lee blob cifrado
2. Verifica HMAC
3. Descifra con DEK
4. Devuelve JSON

#### 5. **Cambiar contraseña maestra**
```python
vault.change_master_password("NuevaPassMaestra")
```
**Qué hace:**
1. Genera NUEVA sal aleatoria
2. Deriva nueva clave maestra
3. Re-envuelve la MISMA DEK
4. Guarda nueva sal + nueva DEK_envuelta
5. ✅ Las entradas NO se tocan

**🔒 Seguridad: Associated Data (AD)**

Cada cifrado incluye contexto:
```python
# Para la DEK envuelta:
AD = "gestor-seguro-vault|v1|{vault_id}|{kdf_params}"

# Para cada entrada:
AD = "entry|{vault_id}|{entry_id}"
```

**¿Por qué?** Evita ataques:
- ❌ No puedes copiar una entrada de una bóveda a otra
- ❌ No puedes cambiar los parámetros KDF sin que falle la apertura
- ❌ No puedes mover el ciphertext de entrada A a entrada B

**🎓 Conceptos clave:**
- **Envelope encryption:** Jerarquía de claves (maestra → KEK → DEK → datos)
- **DEK aleatoria:** Cambiar contraseña maestra es rápido
- **Associated Data:** Contexto autenticado, evita ataques de manipulación

---

### 6️⃣ **`cli.py`** - Interfaz de Usuario

**¿Qué hace?**
La parte que ves: comandos que escribes en la terminal.

**¿Por qué existe?**
Para que NO tengas que usar código Python directamente.

**Comandos disponibles:**

```python
# Crear bóveda
python -m gestor.cli init

# Añadir contraseña
python -m gestor.cli add github.com usuario

# Generar contraseña automática
python -m gestor.cli add gmail.com user --generate 24

# Buscar
python -m gestor.cli get github

# Listar todas
python -m gestor.cli list

# Eliminar
python -m gestor.cli rm <entry_id>

# Cambiar contraseña maestra
python -m gestor.cli passwd
```

**Función auxiliar: generador de contraseñas**
```python
def generate_password(length=20):
    alphabet = "abc...XYZ123!@#$%"
    return "".join(secrets.choice(alphabet) for _ in range(length))
```

---

## 🔄 FLUJO COMPLETO: DE INICIO A FIN

### 🎬 ESCENARIO: Primera vez usando el gestor

#### **Paso 1: Crear bóveda**
```bash
$ python -m gestor.cli init
Nueva contraseña maestra: MiSuperPass2026!
Repítela: MiSuperPass2026!
Bóveda creada en vault.json
```

**Qué pasó internamente:**
```
1. generate_salt() → sal = b'\x9a\x7f...' (16 bytes aleatorios)
2. derive_master_key("MiSuperPass2026!", params)
   → Argon2id procesa 64 MB durante 3 iteraciones
   → clave_maestra = b'\x4b\x2c...' (32 bytes)
3. derive_subkeys(clave_maestra, "KEK")
   → KEK_enc = 32 bytes
   → KEK_mac = 32 bytes
4. secrets.token_bytes(64)
   → DEK = 64 bytes aleatorios
5. encrypt(KEK_enc, KEK_mac, DEK, AD=cabecera)
   → DEK_envuelta = versión|IV|DEK_cifrada|HMAC
6. storage.write(vault.json) →
   {
     "vault_id": "uuid-aleatorio",
     "kdf": {"algorithm": "argon2id", "salt": "...", ...},
     "wrapped_key": "base64(DEK_envuelta)",
     "entries": {}
   }
```

#### **Paso 2: Añadir contraseña**
```bash
$ python -m gestor.cli add github.com gladys --generate 24
Contraseña maestra: MiSuperPass2026!
Guardada (id abc-123): Kx9#mP2@qL4$wR7^nT1!
```

**Qué pasó internamente:**
```
1. vault.open(storage, "MiSuperPass2026!")
   → Lee vault.json
   → Deriva clave_maestra (usando sal guardada)
   → Desenvuelve DEK verificando HMAC
   → Si HMAC incorrecto → InvalidPasswordError

2. generate_password(24) → "Kx9#mP2@qL4$wR7^nT1!"

3. vault.add_entry("github.com", "gladys", "Kx9#...")
   → entry_id = uuid()
   → plaintext = {"site": "github.com", "username": "gladys",
                  "password": "Kx9#...", "created": "2026-11-18T...", ...}
   → plaintext_json = '{"site":"github.com",...}'
   → DEK_enc = DEK[:32], DEK_mac = DEK[32:]
   → AD = "entry|{vault_id}|{entry_id}"
   → iv = secrets.token_bytes(16)
   → ciphertext = AES-256-CBC(DEK_enc, iv, plaintext_json)
   → hmac = HMAC-SHA256(DEK_mac, version|len(AD)|AD|iv|ciphertext)
   → blob = version|iv|ciphertext|hmac
   → entries[entry_id] = base64(blob)
   → storage.write(vault.json)
```

#### **Paso 3: Recuperar contraseña**
```bash
$ python -m gestor.cli get github
Contraseña maestra: MiSuperPass2026!
github.com  gladys  Kx9#mP2@qL4$wR7^nT1!
```

**Qué pasó internamente:**
```
1. vault.open() → desenvuelve DEK
2. vault.find("github")
   → Para cada entrada:
      - blob = base64.decode(entries[entry_id])
      - version|iv|ciphertext|hmac = blob
      - AD = "entry|{vault_id}|{entry_id}"
      - verify_hmac(DEK_mac, version, iv, ciphertext, hmac, AD)
        → Si falla → IntegrityError
      - plaintext = AES-256-CBC.decrypt(DEK_enc, iv, ciphertext)
      - entry = json.loads(plaintext)
      - Si "github" in entry["site"].lower() → añadir a resultados
3. Mostrar resultados
```

---

## 🧪 ARCHIVO `ejemplo.py` - PARA PRACTICAR

**¿Qué hace?**
Demuestra paso a paso cómo funcionan las primitivas criptográficas.

**Cómo ejecutarlo:**
```bash
python ejemplo.py
```

**Salida esperada:**
```
=== 1. Primitivas ===
sal          : 9a7f3c2e...
clave maestra: 4b2c8d1a... (solo existe en RAM)
blob         : 0110f3e4a...
descifrado   : b'mi secreto'
manipulación : detectada -> Fallo de autenticación

=== 2. Bóveda ===
Contenido en disco (lo único que vería un servidor):
{
  "format": "gestor-seguro-vault",
  "kdf": {...},
  "wrapped_key": "AQqI...",
  "entries": {"abc-123": "AQxK..."}
}

Recuperado: {'site': 'github.com', ...}
Contraseña incorrecta -> InvalidPasswordError
```

---

## 🎓 EJERCICIOS PARA PRACTICAR

### **Nivel 1: Básico**

1. **Crear tu primera bóveda**
   ```bash
   python -m gestor.cli init
   ```
   Observa que se crea `vault.json`. Ábrelo y mira su contenido.

2. **Añadir 3 contraseñas**
   ```bash
   python -m gestor.cli add facebook.com user1 --generate 20
   python -m gestor.cli add gmail.com user2 --generate 24
   python -m gestor.cli add twitter.com user3 --generate 16
   ```

3. **Listar todas las entradas**
   ```bash
   python -m gestor.cli list
   ```

4. **Buscar una contraseña**
   ```bash
   python -m gestor.cli get facebook
   ```

### **Nivel 2: Intermedio**

5. **Cambiar contraseña maestra**
   ```bash
   python -m gestor.cli passwd
   ```
   Luego intenta abrir con la contraseña antigua (debe fallar).

6. **Manipular vault.json**
   - Haz una copia de seguridad
   - Abre `vault.json` y cambia un carácter en `wrapped_key`
   - Intenta abrir la bóveda
   - Observa el error: `InvalidPasswordError`

7. **Ejecutar ejemplo.py**
   ```bash
   python ejemplo.py
   ```
   Lee el código y entiende qué hace cada sección.

### **Nivel 3: Avanzado**

8. **Crear script personalizado**
   ```python
   from gestor import Vault, FileStorage

   storage = FileStorage("mi_boveda.json")
   with Vault.create(storage, "pass123") as vault:
       vault.add_entry("test.com", "user", "pass")
   
   with Vault.open(storage, "pass123") as vault:
       for entry in vault.list_entries():
           print(entry)
   ```

9. **Usar MemoryStorage**
   ```python
   from gestor import Vault, MemoryStorage

   storage = MemoryStorage()
   with Vault.create(storage, "temporal") as vault:
       vault.add_entry("ejemplo.com", "user", "pass")
       print(vault.find("ejemplo"))
   # Al terminar, todo se pierde (está en RAM)
   ```

10. **Probar PBKDF2 en lugar de Argon2id**
    ```bash
    python -m gestor.cli init --kdf pbkdf2-sha256
    ```
    Compara la velocidad con Argon2id.

### **Nivel 4: Experto**

11. **Ejecutar las pruebas**
    ```bash
    python -m pytest -v
    python -m pytest tests/test_vault.py -v
    ```

12. **Leer el código de los tests**
    Abre `tests/test_vault.py` y entiende cómo se prueban las funciones.

13. **Modificar parámetros de Argon2id**
    Edita `gestor/kdf.py`:
    ```python
    # Aumentar seguridad (pero será más lento)
    DEFAULT_ARGON2 = {"time_cost": 5, "memory_cost": 128 * 1024, "parallelism": 8}
    ```

---

## 🛡️ CONCEPTOS CRIPTOGRÁFICOS CLAVE

### **1. Sal (Salt)**
- **Qué:** Bytes aleatorios añadidos a la contraseña
- **Para qué:** Dos usuarios con la misma contraseña tendrán claves diferentes
- **Ejemplo:** "pass123" + sal_A ≠ "pass123" + sal_B

### **2. KDF (Key Derivation Function)**
- **Qué:** Convierte contraseña → clave criptográfica
- **Para qué:** Hacerlo MUY lento dificulta ataques de fuerza bruta
- **Ejemplo:** Argon2id tarda ~200ms → probar 1 millón de contraseñas = 55 horas

### **3. Envelope Encryption**
- **Qué:** Jerarquía de claves (maestra → KEK → DEK → datos)
- **Para qué:** Cambiar contraseña maestra sin re-cifrar todo
- **Ejemplo:** 10,000 entradas, cambio de contraseña = 1 segundo (vs 10 minutos)

### **4. Encrypt-then-MAC**
- **Qué:** Primero cifrar, luego calcular HMAC del ciphertext
- **Para qué:** Verificar integridad ANTES de descifrar
- **Ejemplo:** Evita ataques de padding oracle

### **5. Associated Data (AD)**
- **Qué:** Contexto que se autentica pero no se cifra
- **Para qué:** Evitar que un ciphertext válido se use en otro contexto
- **Ejemplo:** AD = "vault_A|entry_1" → no sirve para entry_2

### **6. Conocimiento Cero (Zero Knowledge)**
- **Qué:** El servidor solo ve datos cifrados
- **Para qué:** Ni siquiera el dueño del servidor puede ver tus contraseñas
- **Ejemplo:** `storage.py` solo ve bytes, no sabe qué contienen

---

## 📝 RESUMEN: ¿QUÉ HACE CADA ARCHIVO?

| Archivo | Analogía | Responsabilidad |
|---------|----------|----------------|
| `errors.py` | 🚨 Sistema de alarmas | Define los tipos de errores |
| `kdf.py` | 🔑 Fábrica de llaves | Contraseña → claves criptográficas |
| `cipher.py` | 🔒 Caja fuerte | Cifra y descifra datos |
| `storage.py` | 💾 Archivero | Guarda y lee archivos |
| `vault.py` | 🗄️ Director de banco | Coordina todo, gestiona entradas |
| `cli.py` | ⌨️ Recepcionista | Interfaz que usas tú |

---

## 🚀 COMANDOS RÁPIDOS DE REFERENCIA

```bash
# Setup inicial
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

# Crear bóveda
python -m gestor.cli init

# Añadir contraseña
python -m gestor.cli add sitio.com usuario --generate 24

# Ver contraseña
python -m gestor.cli get sitio

# Listar todas
python -m gestor.cli list

# Eliminar
python -m gestor.cli rm <id>

# Cambiar contraseña maestra
python -m gestor.cli passwd

# Ejecutar ejemplo educativo
python ejemplo.py

# Ejecutar pruebas
python -m pytest -v
```

---

## 🎯 PARA ESTUDIAR EL CÓDIGO

**Orden recomendado:**

1. **Empieza por:** `errors.py` (más simple)
2. **Continúa con:** `storage.py` (lógica de archivos)
3. **Luego:** `kdf.py` (deriva claves)
4. **Después:** `cipher.py` (cifrado)
5. **Finalmente:** `vault.py` (lo junta todo)
6. **Extra:** `cli.py` (interfaz de usuario)

**Para cada archivo:**
1. Lee los comentarios
2. Ejecuta el código en `ejemplo.py`
3. Usa `print()` para ver valores intermedios
4. Experimenta cambiando parámetros

---

## ❓ PREGUNTAS FRECUENTES

**P: ¿Por qué no usar un solo archivo?**
R: Separación de responsabilidades = código más fácil de entender, probar y mantener.

**P: ¿Por qué Argon2id y no solo SHA-256?**
R: SHA-256 es rápido (malo para contraseñas). Argon2id es lento a propósito.

**P: ¿Qué pasa si pierdo vault.json?**
R: Pierdes TODO. Es como perder las llaves de una caja fuerte.

**P: ¿Puedo usar esto para producción?**
R: Es educativo. Para producción, usa gestores establecidos (Bitwarden, 1Password).

**P: ¿Dónde está la contraseña maestra?**
R: NUNCA se guarda. Solo existe en RAM mientras la bóveda está abierta.

---

## 🎉 ¡LISTO PARA EMPEZAR!

1. Ejecuta `python ejemplo.py` para ver las primitivas en acción
2. Crea tu primera bóveda con `python -m gestor.cli init`
3. Añade algunas contraseñas de prueba
4. Explora el código siguiendo el orden recomendado
5. Haz los ejercicios de práctica

**¡Diviértete aprendiendo criptografía! 🔒**
