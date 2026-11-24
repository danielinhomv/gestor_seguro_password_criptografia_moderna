# 🔐 Gestor Seguro de Contraseñas

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/Security-AES--256--CBC%20%2B%20Argon2id-red.svg)](CUMPLIMIENTO_REQUISITOS.md)

**Gestor de contraseñas de conocimiento cero con criptografía moderna:**  
KDF adaptativas (Argon2id/PBKDF2) + AES-256-CBC + HMAC-SHA256 + Envelope Encryption

---

## ✨ Características

- 🔒 **Cifrado robusto:** AES-256-CBC + HMAC-SHA256 (Encrypt-then-MAC)
- 🔑 **KDF adaptativas:** Argon2id (por defecto) o PBKDF2-HMAC-SHA256
- 🧂 **Sal criptográfica:** 128 bits únicos por bóveda
- 🗄️ **Envelope encryption:** Cambio rápido de contraseña maestra
- 🔐 **Conocimiento cero:** Almacenamiento solo ve datos cifrados
- 🎨 **Interfaz gráfica moderna:** GUI completa con Tkinter
- ⌨️ **CLI completa:** Comandos para automatización
- 🧪 **Suite de pruebas:** pytest con cobertura completa
- 📚 **Documentación extensiva:** Guías educativas y técnicas

---

# Gestor Seguro de Contraseñas — KDF + Almacenamiento de Conocimiento Cero

## Estructura

```
gestor-seguro/
├── gestor/
│   ├── kdf.py        # Sal (CSPRNG), Argon2id / PBKDF2-HMAC-SHA256, HKDF para subclaves
│   ├── cipher.py     # AES-256-CBC + PKCS#7 + HMAC-SHA256 (Encrypt-then-MAC)
│   ├── vault.py      # Bóveda: jerarquía de claves, entradas, cambio de contraseña maestra
│   ├── storage.py    # Backends (archivo local atómico / memoria / extensible a remoto)
│   ├── errors.py     # Excepciones con mensajes genéricos (sin oráculos)
│   └── cli.py        # Línea de comandos
├── tests/            # test_kdf.py, test_cipher.py, test_vault.py (pytest)
├── ejemplo.py        # Demostración del flujo completo
└── requirements.txt
```

## Uso

```powershell
python -m venv .venv; .\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m pytest -v      # pruebas
.\.venv\Scripts\python ejemplo.py        # demostración
.\.venv\Scripts\python -m gestor.cli init
.\.venv\Scripts\python -m gestor.cli add github.com gladys --generate 24
.\.venv\Scripts\python -m gestor.cli get github
```

## Diseño criptográfico

```
contraseña maestra ─ NFKC ─┐
sal aleatoria 128 bits ────┴─> Argon2id (t=3, m=64 MiB, p=4)  |  PBKDF2-SHA256 (600 000 it.)
                                  └─> clave maestra (256 bits, solo en RAM)
                                        └─> HKDF-SHA256 ─> KEK_aes ‖ KEK_hmac
                                              └─ envuelve (EtM) ─> DEK aleatoria (256+256 bits)
                                                                      └─ cifra (EtM) ─> cada entrada
```

| Decisión | Motivo |
|---|---|
| Argon2id por defecto | Resistente a GPU/ASIC (memory-hard); PBKDF2 como alternativa compatible con FIPS |
| Sal única de 16 B por bóveda, renovada al cambiar la contraseña | Impide tablas precalculadas y que dos usuarios con la misma contraseña obtengan la misma clave |
| HKDF para separar claves AES y HMAC | Nunca reutilizar la misma clave para dos primitivas |
| IV aleatorio por cifrado | CBC exige IV impredecible |
| **Encrypt-then-MAC**, HMAC verificado con `compare_digest` **antes** de descifrar | Elimina el padding oracle; cualquier bit alterado → mismo error genérico |
| El HMAC cubre versión ‖ len(AD) ‖ AD ‖ IV ‖ ciphertext | Autentica todo; el prefijo de longitud evita ambigüedades |
| AD = `vault_id \| entry_id` | No se puede mover un ciphertext a otra entrada u otra bóveda |
| AD del envoltorio = cabecera (id + parámetros KDF) | Manipular parámetros → la bóveda no abre; además se exigen mínimos |
| Envelope encryption (DEK) | Cambiar la contraseña maestra no re-cifra todas las entradas |
| No se guarda ningún hash de la contraseña | La verificación es el propio HMAC del envoltorio: el almacén no tiene nada que atacar salvo la KDF |

**Conocimiento cero:** el almacenamiento solo recibe parámetros públicos, la DEK envuelta y blobs
cifrados (incluidos nombres de sitio y usuario). Todo el cifrado y descifrado ocurre en el cliente,
así que `StorageBackend` puede ser un servidor remoto sin cambiar nada.

## Limitaciones conocidas (para producción)

- **Rollback/borrado:** un servidor malicioso podría devolver una versión antigua de la bóveda o
  eliminar entradas enteras. Se mitiga con un MAC sobre el índice de entradas + un contador de
  versión verificado por el cliente.
- **Memoria:** en Python no se puede borrar de forma fiable una clave de la RAM (`bytes` es inmutable).
- **AES-CBC + HMAC** se usa porque lo exige la especificación; en un diseño nuevo, un AEAD
  (AES-256-GCM o XChaCha20-Poly1305) es más sencillo y menos propenso a errores.
- Los metadatos visibles son el número de entradas y el tamaño aproximado de cada una.


---

## 🚀 Inicio Rápido

### Instalación

```powershell
# Clonar repositorio
git clone https://github.com/TU_USUARIO/gestor-seguro.git
cd gestor-seguro

# Crear entorno virtual e instalar dependencias
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Uso con Interfaz Gráfica (Recomendado)

```powershell
# Opción 1: Script de inicio
.\INICIAR_GUI.bat

# Opción 2: Comando directo
python main_gui.py
```

### Uso con CLI

```powershell
# Crear bóveda
python -m gestor.cli init

# Añadir contraseña con generador automático
python -m gestor.cli add github.com usuario --generate 24

# Buscar contraseña
python -m gestor.cli get github

# Listar todas
python -m gestor.cli list

# Cambiar contraseña maestra
python -m gestor.cli passwd
```

---

## 📚 Documentación

| Documento | Descripción |
|-----------|-------------|
| [**GUIA_ESTUDIO.md**](GUIA_ESTUDIO.md) | 📖 Guía completa de aprendizaje con ejemplos |
| [**INSTRUCCIONES_GUI.md**](INSTRUCCIONES_GUI.md) | 🎨 Manual de uso de la interfaz gráfica |
| [**PASOS_EJECUTAR_GUI.md**](PASOS_EJECUTAR_GUI.md) | 🧪 14 tests para verificar funcionamiento |
| [**CUMPLIMIENTO_REQUISITOS.md**](CUMPLIMIENTO_REQUISITOS.md) | ✅ Verificación de requisitos del proyecto |
| [**QUE_PASA_AL_CAMBIAR_PASSWORD.md**](QUE_PASA_AL_CAMBIAR_PASSWORD.md) | 🔑 Explicación de envelope encryption |

---

## 🔐 Seguridad

### Decisiones Criptográficas

| Componente | Implementación | Justificación |
|------------|----------------|---------------|
| **KDF** | Argon2id (t=3, m=64MiB, p=4) | Resistente a GPU/ASIC (memory-hard) |
| **Alternativa KDF** | PBKDF2-SHA256 (600k iter) | Compatible FIPS, estándar OWASP 2023+ |
| **Cifrado** | AES-256-CBC + PKCS#7 | Estándar industria, IV aleatorio por operación |
| **Autenticación** | HMAC-SHA256 | Verificación de integridad en modo Encrypt-then-MAC |
| **Sal** | 128 bits (CSPRNG) | Única por bóveda, renovada al cambiar contraseña |
| **Separación de claves** | HKDF-SHA256 | Claves AES y HMAC siempre independientes |
| **Associated Data** | vault_id \| entry_id | Previene ataques de manipulación de contexto |
| **Envelope Encryption** | KEK → DEK → Datos | Cambio rápido de contraseña maestra |

### Protección contra Ataques

- ✅ **Padding Oracle:** Encrypt-then-MAC + verificación antes de descifrar
- ✅ **Timing attacks:** `hmac.compare_digest()` en tiempo constante
- ✅ **Rainbow tables:** Sal única por bóveda
- ✅ **Fuerza bruta:** Argon2id con alto costo computacional
- ✅ **Manipulación:** HMAC sobre versión + AD + IV + ciphertext
- ✅ **Replay attacks:** Associated Data por contexto

---

## 🏗️ Arquitectura

```
Contraseña Maestra ─ NFKC ─┐
Sal aleatoria (128 bits) ──┴─> Argon2id (t=3, m=64MiB, p=4)
                                     │
                              Clave Maestra (256 bits, solo RAM)
                                     │
                              HKDF-SHA256
                                     │
                           ┌─────────┴─────────┐
                     KEK_aes (256)      KEK_hmac (256)
                           │
                    envuelve (AES+HMAC)
                           │
                     DEK aleatoria (512 bits)
                           │
                    cifra (AES+HMAC)
                           │
                   ┌───────┼───────┐
              Entrada 1  Entrada 2  Entrada N
```

---

## 📂 Estructura del Proyecto

```
gestor-seguro/
├── gestor/                      # Código fuente principal
│   ├── __init__.py             # Exportaciones públicas
│   ├── errors.py               # Excepciones personalizadas
│   ├── kdf.py                  # Derivación de claves (Argon2/PBKDF2)
│   ├── cipher.py               # Cifrado AES-256-CBC + HMAC-SHA256
│   ├── storage.py              # Backends de almacenamiento
│   ├── vault.py                # Gestión de bóveda (envelope encryption)
│   ├── cli.py                  # Interfaz de línea de comandos
│   └── gui.py                  # Interfaz gráfica (Tkinter)
│
├── tests/                       # Suite de pruebas
│   ├── conftest.py             # Configuración pytest
│   ├── test_kdf.py             # Tests de derivación de claves
│   ├── test_cipher.py          # Tests de cifrado/descifrado
│   └── test_vault.py           # Tests de bóveda completa
│
├── docs/                        # Documentación
│   ├── GUIA_ESTUDIO.md         # Guía educativa completa
│   ├── INSTRUCCIONES_GUI.md    # Manual de interfaz gráfica
│   ├── CUMPLIMIENTO_REQUISITOS.md  # Verificación de requisitos
│   └── ...
│
├── ejemplo.py                   # Demostración del flujo completo
├── main_gui.py                  # Lanzador de interfaz gráfica
├── INICIAR_GUI.bat             # Script de inicio para Windows
├── requirements.txt             # Dependencias del proyecto
├── README.md                    # Este archivo
└── .gitignore                   # Archivos ignorados por Git
```

---

## 🧪 Pruebas

```powershell
# Ejecutar todas las pruebas
pytest -v

# Ejecutar pruebas específicas
pytest tests/test_vault.py -v

# Con cobertura
pytest --cov=gestor --cov-report=html
```

---

## 🎯 Casos de Uso

### Gestión Personal de Contraseñas
- Almacenamiento local seguro
- Generación de contraseñas robustas
- Búsqueda y organización intuitiva

### Desarrollo de Software Seguro
- Referencia de implementación criptográfica
- Estudio de envelope encryption
- Ejemplo de arquitectura de conocimiento cero

### Educación en Criptografía
- Código documentado y comentado
- Guías paso a paso
- Ejemplos prácticos de conceptos teóricos

---

## ⚠️ Limitaciones

### Para Producción
- **Memoria:** Python no puede borrar claves de RAM de forma garantizada
- **Rollback:** Servidor malicioso podría devolver versión antigua
- **Metadatos:** Número de entradas y tamaños son visibles
- **Recomendación:** Para uso profesional, considera Bitwarden, 1Password, o KeePassXC

### Diseño Académico
Este proyecto implementa criptografía moderna según especificaciones académicas. Para uso en producción, considera:
- Usar AEAD (AES-GCM o ChaCha20-Poly1305) en lugar de AES-CBC+HMAC
- Implementar sincronización multi-dispositivo
- Añadir 2FA y recuperación de cuenta
- Auditoría de seguridad profesional

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

---

## 🙏 Reconocimientos

- **Argon2:** Password Hashing Competition winner
- **Cryptography.io:** Biblioteca criptográfica robusta
- **OWASP:** Guías de seguridad y buenas prácticas
- **NIST:** Estándares de criptografía (SP 800-132, SP 800-63B)

---

## 📞 Contacto

Para preguntas, sugerencias o reportes de seguridad, abre un issue en GitHub.

---

**⭐ Si te resultó útil este proyecto, considera darle una estrella en GitHub!**
