import argparse
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from backend_spec.commands.bootstrap_cmd import run_bootstrap
from backend_spec.commands.check_cmd import run_check
from backend_spec.commands.init_cmd import run_init
from backend_spec.commands.new_req_cmd import run_new_req
from backend_spec.commands.resolve_cmd import run_resolve
from backend_spec.commands.sync_index_cmd import run_sync_index
from backend_spec.commands.update_cmd import run_update


def main():
    parser = argparse.ArgumentParser(
        prog="backend-spec",
        description="Framework y CLI v1.0 para desarrollo backend guiado por especificaciones con agentes de IA",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponibles")

    # Command: init
    init_parser = subparsers.add_parser("init", help="Inicializa backend-spec en el proyecto destino")
    init_parser.add_argument(
        "--harness",
        choices=["all", "antigravity", "cursor", "claude", "windsurf"],
        default="all",
        help="Harness de IA a configurar",
    )
    init_parser.add_argument(
        "--versioning",
        choices=["semver", "calver", "sequential"],
        default="semver",
        help="Estrategia de versionamiento",
    )
    init_parser.add_argument("-i", "--interactive", action="store_true", help="Modo interactivo")
    init_parser.add_argument("-f", "--force", action="store_true", help="Sobrescribir archivos existentes")
    init_parser.add_argument("--dir", default=".", help="Directorio destino (por defecto .)")

    # Command: update
    update_parser = subparsers.add_parser(
        "update",
        help="Actualiza plantillas, reglas de agentes y hooks del framework sin alterar docs/",
    )
    update_parser.add_argument(
        "--harness",
        choices=["all", "antigravity", "cursor", "claude", "windsurf"],
        default=None,
        help="Harness a actualizar o añadir (por defecto auto-detecta los instalados)",
    )
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Previsualiza los cambios sin modificar ningún archivo en disco",
    )
    update_parser.add_argument("--dir", default=".", help="Directorio del proyecto")

    # Command: bootstrap
    boot_parser = subparsers.add_parser(
        "bootstrap",
        help="Escanea un repositorio existente (Brownfield) y pre-pobla tech-stack.md y .spec/bootstrap-report.md",
    )
    boot_parser.add_argument(
        "--mode",
        choices=["auto", "full", "progressive"],
        default="auto",
        help="Modalidad de onboarding (full levanta todo, progressive levanta flujo crítico)",
    )
    boot_parser.add_argument(
        "--reset",
        action="store_true",
        help="Reinicia las casillas de verificación de .spec/bootstrap-report.md",
    )
    boot_parser.add_argument("--dir", default=".", help="Directorio del proyecto")

    # Command: req:new
    new_req_parser = subparsers.add_parser("req:new", help="Crea un nuevo requerimiento atómico delimitado")
    new_req_parser.add_argument("title", nargs="?", default=None, help="Título del requerimiento (opcional si se usa --from-audit)")
    new_req_parser.add_argument("--domain", default="core", help="Dominio de negocio (ej. auth, billing, core)")
    new_req_parser.add_argument("--priority", choices=["P1", "P2", "P3"], default="P2", help="Prioridad")
    new_req_parser.add_argument(
        "--impact",
        choices=["MAJOR", "MINOR", "PATCH"],
        default="MINOR",
        help="Impacto de versión (PATCH activa automáticamente el carril Fast-Track)",
    )
    new_req_parser.add_argument("--version", dest="target_version", default=None, help="Versión objetivo")
    new_req_parser.add_argument("--uc", dest="uc_ref", default=None, help="Ruta al caso de uso vinculado")
    new_req_parser.add_argument(
        "--fast-track",
        action="store_true",
        help="Activa explícitamente el carril ligero Micro-Spec sin exigir caso de uso nuevo",
    )
    new_req_parser.add_argument(
        "--from-audit",
        dest="from_audit",
        default=None,
        help="Promueve un hallazgo de docs/backlog/audit-proposals.md (ej. AUDIT-CORE-001) a requerimiento",
    )
    new_req_parser.add_argument("--dir", default=".", help="Directorio del proyecto")

    # Command: check
    check_parser = subparsers.add_parser(
        "check", help="Valida integridad de enlaces físicos, esquemas JSON, fronteras y commits"
    )
    check_parser.add_argument(
        "--staged",
        action="store_true",
        help="Verifica git diff --cached para bloquear commits fantasma sin trazabilidad",
    )
    check_parser.add_argument("--dir", default=".", help="Directorio del proyecto")

    # Command: sync
    sync_parser = subparsers.add_parser(
        "sync", help="Sincroniza en disco docs/backlog/index.md y docs/functional/index.md"
    )
    sync_parser.add_argument("--dir", default=".", help="Directorio del proyecto")

    # Command: resolve
    resolve_parser = subparsers.add_parser(
        "resolve", help="Archiva un requerimiento resuelto en changelog.md y sincroniza índices"
    )
    resolve_parser.add_argument("req_id", help="Identificador del requerimiento (ej. REQ-AUTH-001)")
    resolve_parser.add_argument(
        "--bump",
        action="store_true",
        help="Actualiza la versión en el manifiesto del proyecto (con protección anti-downgrade)",
    )
    resolve_parser.add_argument(
        "--force-version",
        action="store_true",
        help="Permite forzar en el manifiesto una versión inferior a la actual",
    )
    resolve_parser.add_argument("--dir", default=".", help="Directorio del proyecto")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    project_dir = Path(getattr(args, "dir", ".")).resolve()

    if args.command == "init":
        run_init(
            target_dir=project_dir,
            harness=args.harness,
            versioning=args.versioning,
            interactive=args.interactive,
            force=args.force,
        )
    elif args.command == "bootstrap":
        run_bootstrap(project_root=project_dir, mode=args.mode, reset=args.reset)
    elif args.command == "update":
        ok = run_update(
            target_dir=project_dir,
            harness=args.harness,
            dry_run=args.dry_run,
        )
        sys.exit(0 if ok else 1)
    elif args.command == "req:new":
        req_id = run_new_req(
            project_root=project_dir,
            domain=args.domain,
            title=args.title,
            priority=args.priority,
            impact=args.impact,
            target_version=args.target_version,
            uc_ref=args.uc_ref,
            fast_track=args.fast_track,
            from_audit=args.from_audit,
        )
        if not req_id:
            sys.exit(1)
    elif args.command == "check":
        success = run_check(project_root=project_dir, check_staged=args.staged)
        sys.exit(0 if success else 1)
    elif args.command == "sync":
        run_sync_index(project_root=project_dir)
    elif args.command == "resolve":
        ok = run_resolve(
            project_root=project_dir,
            req_id=args.req_id,
            auto_bump=args.bump,
            force_version=args.force_version,
        )
        if not ok:
            sys.exit(1)


if __name__ == "__main__":
    main()
