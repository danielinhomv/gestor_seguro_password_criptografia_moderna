import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Parámetros mínimos para que los tests sean rápidos (NO usar en producción).
FAST_ARGON2 = {"time_cost": 1, "memory_cost": 8 * 1024, "parallelism": 1}
FAST_PBKDF2 = {"iterations": 100_000}
