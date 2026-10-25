#!/usr/bin/env python3
"""Guard the published-release workflow's MMP kit asset contract."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
workflow=(root/".github/workflows/release.yml").read_text()
assert 'release:' in workflow and 'types: [published]' in workflow
assert 'python scripts/build_mmp_specification.py --print-filename' in workflow
assert 'python scripts/build_mmp_specification.py --output "$MMP_KIT_PATH"' in workflow
assert 'python scripts/test_mmp_specification_kit.py --archive "$MMP_KIT_PATH"' in workflow
assert 'python scripts/test_mmp_release_kit.py --kit "$MMP_KIT_PATH"' in workflow
assert 'sha256sum "$MMP_KIT_NAME" >> SHA256SUMS.txt' in workflow
assert 'dist/mmp-specification-kit-*.zip.sha256' in workflow
assert 'dist/mmp-specification-kit-*.zip dist/mmp-specification-kit-*.zip.sha256' in workflow
assert 'mmp-specification-1.0.0.zip' not in workflow
print("PASS: published release builds and uploads one version-derived MMP kit with checksums")
