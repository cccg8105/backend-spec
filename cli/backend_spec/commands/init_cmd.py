import datetime
import shutil
import stat
from pathlib import Path
from typing import Dict

from backend_spec.detector.ecosystem_detector import detect_ecosystem, ECOSYSTEM_SIGNATURES
from backend_spec.detector.version_extractor import extract_version, compute_next_milestone
from backend_spec.validator.schema_validator import locate_framework_asset
from backend_spec.commands.update_cmd import (
    _install_harness_skills,
    _update_managed_markdown,
    _update_pre_commit_hook,
)

SCHEME_LABELS: Dict[str, str] = {
    "semver": "SemVer 2.0.0",
    "calver": "CalVer (YYYY.MM.MICRO)",
    "sequential": "Sequential Versioning",
}


def _render_placeholders(text: str, context: Dict[str, str]) -> str:
    rendered = text
    for key, val in context.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", val)
    return rendered


def run_init(
    target_dir: Path,
    harness: str = "all",
    versioning: str = "semver",
    interactive: bool = False,
    force: bool = False,
):
    target_dir = Path(target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n🚀 Inicializando backend-spec v1.1 en: {target_dir}")

    templates_root = locate_framework_asset("templates")
    harnesses_root = locate_framework_asset("harnesses")

    if not templates_root or not (templates_root / ".spec" / "docs").exists():
        raise RuntimeError(
            "No se encontraron las plantillas base de backend-spec. "
            "Verifica la instalación del paquete (templates/.spec/docs)."
        )

    # 1. Detección Greenfield vs Brownfield
    detection = detect_ecosystem(target_dir)
    print(f"ℹ️  {detection['message']}")

    selected_sig = {
        "ecosystem": "node",
        "name": "Node.js / TypeScript",
        "manifest": "package.json",
        "version_file": "package.json",
        "format": "json",
        "field": "version",
        "src_ext": ".ts",
        "src_dir": "src",
        "test_pattern": "tests/unit/{slug}.spec.ts",
    }
    current_version = "0.1.0"

    if detection["mode"] == "brownfield" and detection["detected"]:
        selected_sig = detection["detected"]
        version_path = detection["version_path"]
        extracted = extract_version(version_path, selected_sig["format"])
        if extracted:
            current_version = extracted
            print(f"✔ Versión actual detectada en {version_path.name}: {current_version}")
        elif selected_sig["format"] == "plain" and not version_path.exists():
            version_path.write_text(f"{current_version}\n", encoding="utf-8")
            print(f"✔ Creado archivo de versión para Go: {version_path.name} ({current_version})")

    if interactive:
        if detection["mode"] == "greenfield" or not detection["detected"]:
            print("\nConfiguración de ecosistema backend:")
            for idx, sig in enumerate(ECOSYSTEM_SIGNATURES, 1):
                print(f"  {idx}. {sig['name']}")
            try:
                choice = input(f"Selecciona ecosistema (1-{len(ECOSYSTEM_SIGNATURES)}) [1]: ").strip()
                sel_idx = int(choice) - 1 if choice else 0
                if 0 <= sel_idx < len(ECOSYSTEM_SIGNATURES):
                    selected_sig = ECOSYSTEM_SIGNATURES[sel_idx]
            except Exception:
                pass

        try:
            scheme_in = input(
                f"Esquema de versionamiento (semver/calver/sequential) [{versioning}]: "
            ).strip().lower()
            if scheme_in in SCHEME_LABELS:
                versioning = scheme_in
            ver_in = input(f"Versión inicial [{current_version}]: ").strip()
            if ver_in:
                current_version = ver_in.lstrip("vV")
        except Exception:
            pass

    if current_version == "0.1.0" and versioning == "calver":
        today_dt = datetime.date.today()
        current_version = f"{today_dt.year}.{today_dt.month:02d}.0"

    milestone_version = compute_next_milestone(current_version, versioning)
    today_iso = datetime.date.today().isoformat()

    docs_dir = target_dir / "docs"
    spec_dir = target_dir / ".spec"
    blueprints_dest = spec_dir / "templates"

    docs_dir.mkdir(parents=True, exist_ok=True)
    blueprints_dest.mkdir(parents=True, exist_ok=True)

    # 2. Copiar blueprints de referencia para el agente a .spec/templates/
    blueprints_src = templates_root / ".spec" / "templates"
    if blueprints_src.exists():
        for bp_file in blueprints_src.glob("*.md"):
            dest_bp = blueprints_dest / bp_file.name
            if not dest_bp.exists() or force:
                shutil.copy2(bp_file, dest_bp)
        print("✔ Blueprints del agente instalados en: .spec/templates/")

    # 3. Renderizar documentos base limpios en docs/
    placeholders = {
        "PROJECT_NAME": target_dir.name,
        "CURRENT_VERSION": current_version.lstrip("vV"),
        "MILESTONE_VERSION": milestone_version,
        "RUNTIME_NAME": selected_sig["name"],
        "MANIFEST_FILE": selected_sig["version_file"],
        "SRC_EXT": selected_sig["src_ext"],
        "VERSIONING_SCHEME": versioning,
        "VERSIONING_SCHEME_LABEL": SCHEME_LABELS.get(versioning, versioning),
        "TODAY": today_iso,
    }

    clean_docs_src = templates_root / ".spec" / "docs"
    for comp in ("functional", "technical", "backlog"):
        src_comp = clean_docs_src / comp
        dest_comp = docs_dir / comp
        dest_comp.mkdir(parents=True, exist_ok=True)
        for src_md in src_comp.rglob("*.md"):
            rel = src_md.relative_to(src_comp)
            dest_md = dest_comp / rel
            dest_md.parent.mkdir(parents=True, exist_ok=True)
            if not dest_md.exists() or force:
                raw_text = src_md.read_text(encoding="utf-8")
                dest_md.write_text(_render_placeholders(raw_text, placeholders), encoding="utf-8")
        print(f"✔ Inicializado módulo limpio: docs/{comp}")

    use_cases_dir = docs_dir / "functional" / "use-cases"
    use_cases_dir.mkdir(parents=True, exist_ok=True)
    gitkeep = use_cases_dir / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")

    # Determinar qué harnesses se van a instalar
    harnesses_to_install = []
    for h_name in ("antigravity", "cursor", "claude", "windsurf"):
        if harness in ("all", h_name):
            harnesses_to_install.append(h_name)

    harnesses_yaml = "harnesses:\n" + "\n".join(f"  - {h}" for h in harnesses_to_install)

    # 4. Generar .spec/config.yaml enriquecido
    config_content = f"""# ==============================================================================
# backend-spec v1.1 - Configuración del Proyecto
# ==============================================================================

version: "1.1.0"
project_name: "{target_dir.name}"
ecosystem: "{selected_sig['ecosystem']}"
runtime_name: "{selected_sig['name']}"
src_ext: "{selected_sig['src_ext']}"
src_dir: "{selected_sig['src_dir']}"
test_pattern: "{selected_sig['test_pattern']}"

versioning_scheme: "{versioning}"
current_version: "{current_version.lstrip('vV')}"
current_milestone: "{milestone_version}"

version_file:
  path: "{selected_sig['version_file']}"
  format: "{selected_sig['format']}"
  field: "{selected_sig['field']}"

domains:
  - core

{harnesses_yaml}

paths:
  functional_docs: "docs/functional"
  technical_docs: "docs/technical"
  backlog: "docs/backlog"
  templates: ".spec/templates"
"""
    (spec_dir / "config.yaml").write_text(config_content, encoding="utf-8")
    print("✔ Generado archivo de configuración: .spec/config.yaml")

    # 5. Copiar .graphifyignore y .gitignore
    graphifyignore_src = templates_root / ".graphifyignore"
    graphifyignore_dest = target_dir / ".graphifyignore"
    if graphifyignore_src.exists() and (not graphifyignore_dest.exists() or force):
        shutil.copy2(graphifyignore_src, graphifyignore_dest)
        print("✔ Generado archivo de exclusión: .graphifyignore")

    gitignore_src = templates_root / ".gitignore"
    gitignore_dest = target_dir / ".gitignore"
    if gitignore_src.exists() and not gitignore_dest.exists():
        shutil.copy2(gitignore_src, gitignore_dest)
        print("✔ Generado archivo base: .gitignore")

    # 6. Instalar Harness Adapters y Skills
    if harnesses_root and harnesses_root.exists():
        for h in harnesses_to_install:
            if h == "antigravity":
                gemini_rules = target_dir / ".gemini" / "rules"
                gemini_rules.mkdir(parents=True, exist_ok=True)
                src_rule = harnesses_root / "antigravity" / "rules" / "backend-spec.md"
                if src_rule.exists():
                    _update_managed_markdown(gemini_rules / "backend-spec.md", src_rule, dry_run=False)
                    print("✔ Adaptador instalado: .gemini/rules/backend-spec.md (Google Antigravity)")

                skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=False)
                if skills_inst:
                    print(f"✔ Skills Antigravity instaladas: {', '.join(skills_inst)}")

            elif h == "cursor":
                cursor_rules = target_dir / ".cursor" / "rules"
                cursor_commands = target_dir / ".cursor" / "commands"
                cursor_rules.mkdir(parents=True, exist_ok=True)
                cursor_commands.mkdir(parents=True, exist_ok=True)
                src = harnesses_root / "cursor" / "rules" / "backend-spec.mdc"
                if src.exists():
                    _update_managed_markdown(cursor_rules / "backend-spec.mdc", src, dry_run=False)
                    print("✔ Adaptador instalado: .cursor/rules/backend-spec.mdc (Cursor)")
                cmd_src = templates_root / ".cursor" / "commands"
                if cmd_src.exists():
                    for f in cmd_src.glob("*.md"):
                        shutil.copy2(f, cursor_commands / f.name)
                        print(f"✔ Comando Cursor instalado: .cursor/commands/{f.name}")

                skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=False)
                if skills_inst:
                    print(f"✔ Skills Cursor instaladas: {', '.join(skills_inst)}")

            elif h == "claude":
                claude_commands = target_dir / ".claude" / "commands"
                claude_commands.mkdir(parents=True, exist_ok=True)
                src = harnesses_root / "claude" / "CLAUDE.md"
                if src.exists():
                    _update_managed_markdown(target_dir / "CLAUDE.md", src, dry_run=False)
                    print("✔ Adaptador instalado: CLAUDE.md (Claude Code CLI)")
                cmd_src = templates_root / ".claude" / "commands"
                if cmd_src.exists():
                    for f in cmd_src.glob("*.md"):
                        shutil.copy2(f, claude_commands / f.name)
                        print(f"✔ Comando Claude Code instalado: .claude/commands/{f.name}")

                skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=False)
                if skills_inst:
                    print(f"✔ Skills Claude Code instaladas: {', '.join(skills_inst)}")

            elif h == "windsurf":
                windsurf_workflows = target_dir / ".windsurf" / "workflows"
                windsurf_workflows.mkdir(parents=True, exist_ok=True)
                src = harnesses_root / "windsurf" / ".windsurfrules"
                if src.exists():
                    _update_managed_markdown(target_dir / ".windsurfrules", src, dry_run=False)
                    print("✔ Adaptador instalado: .windsurfrules (Windsurf)")
                wf_src = templates_root / ".windsurf" / "workflows"
                if wf_src.exists():
                    for f in wf_src.glob("*.md"):
                        shutil.copy2(f, windsurf_workflows / f.name)
                        print(f"✔ Workflow Windsurf instalado: .windsurf/workflows/{f.name}")

                skills_inst = _install_harness_skills(target_dir, templates_root, harnesses_root, h, dry_run=False)
                if skills_inst:
                    print(f"✔ Skills Windsurf instaladas: {', '.join(skills_inst)}")

    # 7. Instalar Git Pre-commit Hook si existe .git
    git_dir = target_dir / ".git"
    if git_dir.exists() and git_dir.is_dir():
        hook_src = templates_root / ".githooks" / "pre-commit"
        if hook_src.exists():
            res_hook = _update_pre_commit_hook(target_dir, hook_src, dry_run=False)
            if res_hook != "NO_GIT":
                print("✔ Git Hook instalado: .git/hooks/pre-commit (Validación --staged contra commits fantasma)")

    print("\n✨ ¡backend-spec v1.1 inicializado con éxito!")
    if detection["mode"] == "brownfield":
        print("👉 Proyecto existente detectado: ejecuta 'backend-spec bootstrap' (o '/spec-bootstrap') para inventariar tu arquitectura actual.")
    print("👉 Explora 'docs/technical/index.md' y 'docs/backlog/pending.md'.\n")
