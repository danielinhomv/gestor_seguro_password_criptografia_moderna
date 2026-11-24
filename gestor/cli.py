"""CLI mínima.  Uso:  python -m gestor.cli [--vault RUTA] {init,add,get,list,rm,passwd}"""

from __future__ import annotations

import argparse
import getpass
import secrets
import string
import sys

from .errors import GestorError
from .kdf import ARGON2ID, PBKDF2_SHA256
from .storage import FileStorage
from .vault import Vault


def generate_password(length: int = 20) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{};:,.?"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def _ask_new_password(prompt: str) -> str:
    pw = getpass.getpass(prompt)
    if len(pw) < 12:
        sys.exit("La contraseña maestra debe tener al menos 12 caracteres.")
    if pw != getpass.getpass("Repítela: "):
        sys.exit("Las contraseñas no coinciden.")
    return pw


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="gestor")
    p.add_argument("--vault", default="vault.json", help="ruta de la bóveda")
    sub = p.add_subparsers(dest="cmd", required=True)

    init = sub.add_parser("init", help="crear bóveda")
    init.add_argument("--kdf", choices=[ARGON2ID, PBKDF2_SHA256], default=ARGON2ID)

    add = sub.add_parser("add", help="añadir entrada")
    add.add_argument("site")
    add.add_argument("username")
    add.add_argument("--generate", type=int, metavar="N", help="generar contraseña de N caracteres")

    get = sub.add_parser("get", help="buscar entradas por sitio")
    get.add_argument("site")

    sub.add_parser("list", help="listar entradas")
    rm = sub.add_parser("rm", help="borrar entrada")
    rm.add_argument("entry_id")
    sub.add_parser("passwd", help="cambiar contraseña maestra")

    args = p.parse_args(argv)
    storage = FileStorage(args.vault)

    try:
        if args.cmd == "init":
            Vault.create(storage, _ask_new_password("Nueva contraseña maestra: "),
                         kdf_algorithm=args.kdf)
            print(f"Bóveda creada en {args.vault}")
            return

        with Vault.open(storage, getpass.getpass("Contraseña maestra: ")) as vault:
            if args.cmd == "add":
                pw = generate_password(args.generate) if args.generate else \
                    getpass.getpass(f"Contraseña para {args.site}: ")
                entry_id = vault.add_entry(args.site, args.username, pw)
                print(f"Guardada (id {entry_id})" + (f": {pw}" if args.generate else ""))
            elif args.cmd == "get":
                for e in vault.find(args.site) or []:
                    print(f"{e['site']}  {e['username']}  {e['password']}")
            elif args.cmd == "list":
                for e in vault.list_entries():
                    print(f"{e['id']}  {e['site']}  {e['username']}")
            elif args.cmd == "rm":
                vault.delete_entry(args.entry_id)
                print("Entrada eliminada")
            elif args.cmd == "passwd":
                vault.change_master_password(_ask_new_password("Nueva contraseña maestra: "))
                print("Contraseña maestra cambiada")
    except (GestorError, FileNotFoundError, FileExistsError) as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
