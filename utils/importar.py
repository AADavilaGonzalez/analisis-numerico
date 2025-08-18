import importlib
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path
from typing import Any

def importar_dependencia_opcional(
    paquete: str,
    modulo: str = "",
    objeto: str = "",
    advertencia: str = "",
    tmpdir: str = "",
    auto: bool = False
) -> Any:

    modulo = modulo or paquete

    #Agregar tmpdir a path para checar si esta ahi
    tmp_path = Path(tmpdir) if tmpdir else Path(sys.argv[0]).parent/"lib"
    tmp_path_str = str(tmp_path.resolve())
    agregado_a_path = False
    if tmp_path.is_dir() and not tmp_path_str in sys.path:
            sys.path.append(tmp_path_str)
            agregado_a_path = True

    if not find_spec(modulo.partition(".")[0]):

        def instalar_paquete(instalar_global: bool = False) -> bool:
            nonlocal agregado_a_path
            args = [sys.executable, "-m", "pip", "install", paquete]
            if not instalar_global:
                if not agregado_a_path:
                    sys.path.append(tmp_path_str)
                    agregado_a_path = True
                args.extend(["--target", tmp_path_str])
            return subprocess.run(args).returncode == 0

        def dialogo() -> bool:
            print(f"El paquete '{paquete}' no ha sido encontrado.")
            if advertencia: print(advertencia)

            print("Desea instalar el paquete en el entorno actual?(s/N)")
            if input().lower().startswith("s"):
                return instalar_paquete(instalar_global=True)

            print( "Desea instalar el paquete de forma externa en",
                    f"{tmp_path_str}?(s/N)", sep="\n")
            if input().lower().startswith("s"):
                return instalar_paquete()

            return False

        instalar = instalar_paquete if auto else dialogo
        if not instalar():
            if not auto: print(f"No se ha instalado '{paquete}'")
            if agregado_a_path: sys.path.pop()
            return None

    try:
        modulo_encontrado = importlib.import_module(modulo)
        if objeto:
            return getattr(modulo_encontrado, objeto)
        else:
            return modulo_encontrado
    except Exception:
        if agregado_a_path: sys.path.pop()
        raise
