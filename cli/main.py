import sys
from pathlib import Path

# Configurar stdout/stderr en UTF-8 para compatibilidad universal con Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Agregar el paquete al PYTHONPATH
cli_dir = Path(__file__).resolve().parent
if str(cli_dir) not in sys.path:
    sys.path.insert(0, str(cli_dir))

from backend_spec.__main__ import main

if __name__ == "__main__":
    main()
