#!/usr/bin/env python3
"""Guard release workflow so the format 1.1 kit is actually verified and uploaded."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
workflow=(root/".github/workflows/release.yml").read_text()
assert 'release:' in workflow and 'types: [published]' in workflow
# Legacy kit must remain available and independently checked.
assert 'python scripts/build_mmp_specification.py --print-filename' in workflow
assert 'python scripts/build_mmp_specification.py --output "dist/$LEGACY_KIT_NAME"' in workflow
assert 'python scripts/test_mmp_specification_kit.py --archive "dist/$LEGACY_KIT_NAME"' in workflow
assert 'python scripts/test_mmp_release_kit.py --kit "dist/$LEGACY_KIT_NAME"' in workflow
# Format 1.1 kit must be built and verified before packaging assets.
assert 'python scripts/build_mmp_specification_1_2.py --print-filename' in workflow
assert 'python scripts/build_mmp_specification_1_2.py --output "$MMP_KIT_PATH"' in workflow
assert 'python scripts/verify_mmp_11_release_artifact.py --kit "$MMP_KIT_PATH"' in workflow
assert workflow.index('python scripts/verify_mmp_11_release_artifact.py') < workflow.index('      - name: Upload distributions')
assert '(cd dist && sha256sum "$MMP_KIT_NAME" >> SHA256SUMS.txt)' in workflow
assert 'sha256sum "dist/$LEGACY_KIT_NAME" > "dist/$LEGACY_KIT_NAME.sha256"' in workflow
assert 'dist/mmp-specification-kit-*.zip.sha256' in workflow
assert 'dist/mmp-specification-kit-*.zip dist/mmp-specification-kit-*.zip.sha256' in workflow
assert 'mmp-specification-1.0.0.zip' not in workflow
print("PASS: published release builds, verifies and uploads both MMP kit versions")
