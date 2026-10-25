"""Conservative CORE-013 capability gate for MMP 1.0 compatibility.

This module does not implement a future profile wire contract. An explicit
critical-capability declaration in canonical metamodel.extensions is rejected
until there is a package-bound, interoperable format. Absent declaration keeps
all legacy canonical YAML models unchanged.
"""
from __future__ import annotations

def required_capabilities(metamodel: dict) -> list:
    extensions = metamodel.get("extensions", {})
    if not isinstance(extensions, dict):
        raise ValueError("Invalid metamodel extensions")
    requirements = extensions.get("mmp_required_capabilities", [])
    if not isinstance(requirements, list):
        raise ValueError("mmp_required_capabilities must be a list")
    seen = set()
    for item in requirements:
        if not isinstance(item, dict) or set(item) != {"id", "version"}:
            raise ValueError("Each critical capability needs only id and version")
        ident, version = item["id"], item["version"]
        if not isinstance(ident, str) or not ident.strip() or not isinstance(version, str) or not version.strip():
            raise ValueError("Critical capability id/version must be non-empty strings")
        if (ident, version) in seen:
            raise ValueError("Duplicate critical capability declaration")
        seen.add((ident, version))
    return requirements

def require_legacy_safe(metamodel: dict) -> None:
    requirements = required_capabilities(metamodel)
    if requirements:
        names = ", ".join(f"{x['id']}@{x['version']}" for x in requirements)
        raise ValueError("CORE-013 not_supported: critical capabilities require a future "
                         "package-bound profile contract; refusing silent MMP 1.0 downgrade: " + names)
