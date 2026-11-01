from pathlib import Path
from typing import Optional, Dict, Any, List

ECOSYSTEM_SIGNATURES: List[Dict[str, str]] = [
    {
        "ecosystem": "node",
        "name": "Node.js / TypeScript (NestJS, Express, Fastify)",
        "manifest": "package.json",
        "version_file": "package.json",
        "format": "json",
        "field": "version",
        "src_ext": ".ts",
        "src_dir": "src",
        "test_pattern": "tests/unit/{slug}.spec.ts",
    },
    {
        "ecosystem": "python",
        "name": "Python (FastAPI, Django, Flask)",
        "manifest": "pyproject.toml",
        "version_file": "pyproject.toml",
        "format": "toml",
        "field": "version",
        "src_ext": ".py",
        "src_dir": "src",
        "test_pattern": "tests/unit/test_{slug_snake}.py",
    },
    {
        "ecosystem": "python_legacy",
        "name": "Python (setup.py / setup.cfg)",
        "manifest": "setup.cfg",
        "version_file": "setup.cfg",
        "format": "cfg",
        "field": "version",
        "src_ext": ".py",
        "src_dir": "src",
        "test_pattern": "tests/unit/test_{slug_snake}.py",
    },
    {
        "ecosystem": "java_maven",
        "name": "Java / Spring Boot (Maven)",
        "manifest": "pom.xml",
        "version_file": "pom.xml",
        "format": "xml",
        "field": "version",
        "src_ext": ".java",
        "src_dir": "src/main/java",
        "test_pattern": "src/test/java/{slug_pascal}Test.java",
    },
    {
        "ecosystem": "kotlin_gradle",
        "name": "Kotlin / Spring / Ktor (Gradle Kotlin DSL)",
        "manifest": "build.gradle.kts",
        "version_file": "build.gradle.kts",
        "format": "gradle",
        "field": "version",
        "src_ext": ".kt",
        "src_dir": "src/main/kotlin",
        "test_pattern": "src/test/kotlin/{slug_pascal}Test.kt",
    },
    {
        "ecosystem": "java_gradle",
        "name": "Java / Kotlin (Gradle)",
        "manifest": "build.gradle",
        "version_file": "build.gradle",
        "format": "gradle",
        "field": "version",
        "src_ext": ".java",
        "src_dir": "src/main/java",
        "test_pattern": "src/test/java/{slug_pascal}Test.java",
    },
    {
        "ecosystem": "rust",
        "name": "Rust (Actix, Axum)",
        "manifest": "Cargo.toml",
        "version_file": "Cargo.toml",
        "format": "toml",
        "field": "version",
        "src_ext": ".rs",
        "src_dir": "src",
        "test_pattern": "tests/{slug_snake}_test.rs",
    },
    {
        "ecosystem": "go",
        "name": "Go (Gin, Echo, Fiber)",
        "manifest": "go.mod",
        "version_file": "VERSION",
        "format": "plain",
        "field": "version",
        "src_ext": ".go",
        "src_dir": "internal",
        "test_pattern": "internal/{slug_snake}_test.go",
    },
]

IGNORED_SCAFFOLD_ENTRIES = {
    ".git",
    ".spec",
    "docs",
    "graphify-out",
    ".gitignore",
    ".graphifyignore",
    ".gemini",
    ".cursor",
    ".claude",
    ".windsurf",
    "CLAUDE.md",
    ".windsurfrules",
}


def detect_ecosystem(project_root: Path) -> Dict[str, Any]:
    """
    Detecta si el proyecto es Greenfield (nuevo) o Brownfield (existente).
    Identifica el ecosistema, extensiones de código y archivo manifiesto de versión.
    """
    project_root = Path(project_root).resolve()

    existing_files = [
        f for f in project_root.iterdir() if f.name not in IGNORED_SCAFFOLD_ENTRIES
    ]
    if not existing_files:
        return {
            "mode": "greenfield",
            "detected": None,
            "message": "Directorio vacío o nuevo proyecto. Modo Greenfield activado.",
        }

    for sig in ECOSYSTEM_SIGNATURES:
        manifest_path = project_root / sig["manifest"]
        if manifest_path.exists() and manifest_path.is_file():
            version_path = project_root / sig["version_file"]
            return {
                "mode": "brownfield",
                "detected": sig,
                "manifest_path": manifest_path,
                "version_path": version_path,
                "message": f"Ecosistema detectado: {sig['name']} ({sig['manifest']})",
            }

    csproj_files = list(project_root.glob("*.csproj"))
    if csproj_files:
        csproj = csproj_files[0]
        return {
            "mode": "brownfield",
            "detected": {
                "ecosystem": "dotnet",
                "name": ".NET / ASP.NET Core",
                "manifest": csproj.name,
                "version_file": csproj.name,
                "format": "xml",
                "field": "Version",
                "src_ext": ".cs",
                "src_dir": "src",
                "test_pattern": "tests/{slug_pascal}Tests.cs",
            },
            "manifest_path": csproj,
            "version_path": csproj,
            "message": f"Ecosistema detectado: .NET / ASP.NET Core ({csproj.name})",
        }

    return {
        "mode": "brownfield",
        "detected": None,
        "message": "Proyecto existente detectado (ecosistema personalizado).",
    }
