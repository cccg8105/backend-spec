import re
import json
import datetime
from pathlib import Path
from typing import Optional, Tuple


def extract_version(manifest_path: Path, file_format: str) -> Optional[str]:
    """
    Extrae la versión actual desde el archivo manifiesto según su formato.
    """
    if not manifest_path.exists() or not manifest_path.is_file():
        return None

    content = manifest_path.read_text(encoding="utf-8")

    if file_format == "plain":
        for line in content.splitlines():
            cleaned = line.strip()
            if cleaned and not cleaned.startswith("#"):
                return cleaned.lstrip("vV")
        return None

    if file_format == "json":
        try:
            data = json.loads(content)
            val = data.get("version")
            return str(val).lstrip("vV") if val else None
        except Exception:
            pass

    elif file_format == "toml":
        # Priorizar sección [project] o [package] o [tool.poetry]
        section_match = re.search(
            r'\[(?:project|package|tool\.poetry)\](.*?)(?=\n\[|\Z)',
            content,
            re.DOTALL,
        )
        target = section_match.group(1) if section_match else content
        match = re.search(r'(?m)^\s*version\s*=\s*["\']([^"\']+)["\']', target)
        if match:
            return match.group(1).strip().lstrip("vV")

    elif file_format == "xml":
        # Evitar capturar <version> dentro de <parent> o <dependencies> en pom.xml
        stripped = re.sub(r'<parent>.*?</parent>', '', content, flags=re.DOTALL)
        stripped = re.sub(r'<dependencies>.*?</dependencies>', '', stripped, flags=re.DOTALL)
        stripped = re.sub(r'<build>.*?</build>', '', stripped, flags=re.DOTALL)
        match = re.search(r'<[vV]ersion>([^<]+)</[vV]ersion>', stripped)
        if not match:
            match = re.search(r'<[vV]ersion>([^<]+)</[vV]ersion>', content)
        if match:
            return match.group(1).strip().lstrip("vV")

    elif file_format == "cfg":
        match = re.search(r'(?m)^\s*version\s*=\s*([^\s]+)', content)
        if match:
            return match.group(1).strip().lstrip("vV")

    elif file_format == "gradle":
        match = re.search(r'(?m)^\s*version\s*[= ]\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1).strip().lstrip("vV")

    generic_match = re.search(
        r'version["\']?\s*[:=]\s*["\']([^"\']+)["\']', content, re.IGNORECASE
    )
    if generic_match:
        return generic_match.group(1).strip().lstrip("vV")

    return None


def update_version(manifest_path: Path, file_format: str, new_version: str) -> bool:
    """
    Actualiza la versión en el archivo manifiesto preservando formato y comentarios.
    """
    clean_ver = new_version.strip().lstrip("vV")

    if file_format == "plain":
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(f"{clean_ver}\n", encoding="utf-8")
        return True

    if not manifest_path.exists():
        return False

    content = manifest_path.read_text(encoding="utf-8")

    if file_format == "json":
        try:
            data = json.loads(content)
            data["version"] = clean_ver
            manifest_path.write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            return True
        except Exception:
            pass

    if file_format in ("toml", "cfg"):
        pattern = r'(?m)^(\s*version\s*=\s*["\'])[^"\']+(["\'])'
        if re.search(pattern, content):
            new_content = re.sub(pattern, rf'\g<1>{clean_ver}\g<2>', content, count=1)
            manifest_path.write_text(new_content, encoding="utf-8")
            return True
        if file_format == "cfg":
            cfg_pattern = r'(?m)^(\s*version\s*=\s*)[^\s]+'
            if re.search(cfg_pattern, content):
                new_content = re.sub(cfg_pattern, rf'\g<1>{clean_ver}', content, count=1)
                manifest_path.write_text(new_content, encoding="utf-8")
                return True

    if file_format == "xml":
        pattern = r'(<[vV]ersion>)[^<]+(</[vV]ersion>)'
        if re.search(pattern, content):
            new_content = re.sub(pattern, rf'\g<1>{clean_ver}\g<2>', content, count=1)
            manifest_path.write_text(new_content, encoding="utf-8")
            return True

    if file_format == "gradle":
        pattern = r'(?m)^(\s*version\s*[= ]\s*["\'])[^"\']+(["\'])'
        if re.search(pattern, content):
            new_content = re.sub(pattern, rf'\g<1>{clean_ver}\g<2>', content, count=1)
            manifest_path.write_text(new_content, encoding="utf-8")
            return True

    fallback_pattern = r'(version["\']?\s*[:=]\s*["\'])[^"\']+(["\'])'
    if re.search(fallback_pattern, content, re.IGNORECASE):
        new_content = re.sub(
            fallback_pattern,
            rf'\g<1>{clean_ver}\g<2>',
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        manifest_path.write_text(new_content, encoding="utf-8")
        return True

    return False


def parse_version_tuple(version_str: str) -> Tuple[int, ...]:
    """
    Convierte una cadena de versión ('v1.2.3-beta', '2026.10.1', '2') en una tupla numérica comparable.
    """
    cleaned = version_str.strip().lstrip("vV")
    core = re.split(r'[-+]', cleaned)[0]
    nums = re.findall(r'\d+', core)
    if not nums:
        return (0,)
    return tuple(int(n) for n in nums)


def compare_versions(v_new: str, v_current: str) -> int:
    """
    Compara dos versiones numéricas/semánticas.
    Retorna 1 si v_new > v_current, 0 si son iguales, -1 si v_new < v_current.
    """
    t_new = parse_version_tuple(v_new)
    t_cur = parse_version_tuple(v_current)
    max_len = max(len(t_new), len(t_cur))
    t_new_padded = t_new + (0,) * (max_len - len(t_new))
    t_cur_padded = t_cur + (0,) * (max_len - len(t_cur))
    if t_new_padded > t_cur_padded:
        return 1
    if t_new_padded < t_cur_padded:
        return -1
    return 0


def compute_next_milestone(current_version: str, scheme: str = "semver") -> str:
    """
    Calcula el siguiente milestone lógico a partir de la versión actual del proyecto.
    """
    clean = current_version.strip().lstrip("vV")
    parts = parse_version_tuple(clean)

    if scheme == "calver":
        today = datetime.date.today()
        if len(parts) >= 3 and parts[0] >= 2000 and parts[0] == today.year and parts[1] == today.month:
            return f"v{today.year}.{today.month:02d}.{parts[2] + 1}"
        return f"v{today.year}.{today.month:02d}.1"

    if scheme == "sequential":
        last = parts[-1] + 1
        prefix = ".".join(str(p) for p in parts[:-1])
        return f"v{prefix}.{last}" if prefix else f"v{last}"

    # Default: semver -> incrementa MINOR y reinicia PATCH a 0
    major = parts[0] if len(parts) >= 1 else 0
    minor = parts[1] if len(parts) >= 2 else 1
    return f"v{major}.{minor + 1}.0"
