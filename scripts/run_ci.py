#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path


def run(cmd, cwd):
    print('+', ' '.join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], cwd=cwd, check=True)


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument('--project-root', default='.'); ap.add_argument('--reports-dir')
    a=ap.parse_args(); root=Path(a.project_root).resolve(); py=sys.executable
    reports=Path(a.reports_dir).resolve() if a.reports_dir else root/'reports'/'ci'
    reports.mkdir(parents=True, exist_ok=True)

    commands = [
        [py,'scripts/validate_project.py'],
        [py,'scripts/validate_model_robustness.py','--project-root','.'],
        [py,'scripts/validate_canonical_schema.py'],
        [py,'scripts/test_mmp_manifest_contract.py'],
        [py,'scripts/test_mmp_export.py'],
        [py,'scripts/test_mmp_import.py'],
        [py,'scripts/test_mmp_core013_candidate.py'],
        [py,'scripts/test_mmp_pairwise_foundation.py'],
        [py,'scripts/test_mmp_pairwise_candidate.py'],
        [py,'scripts/test_mmp_effective_pairs.py'],
        [py,'scripts/test_mmp_pair_inheritance.py'],
        [py,'scripts/test_mmp_typed_endpoints_foundation.py'],
        [py,'scripts/test_mmp_typed_endpoints_package.py'],
        [py,'scripts/test_mmp_typed_pair_contract.py'],
        [py,'scripts/test_mmp_typed_pair_package.py'],
        [py,'scripts/test_mmp_core015_core016_integration.py'],
        [py,'scripts/test_mmp_post_core016_review.py'],
        [py,'scripts/test_mmp_core007_016_review.py'],
        [py,'scripts/test_mmp_post_pr81_review.py'],
        [py,'scripts/test_mmp_instance_cardinality.py'],
        [py,'scripts/test_mmp_instance_graph.py'],
        [py,'scripts/test_mmp_typed_instance_graph.py'],
        [py,'scripts/test_mmp_junction_instance_graph.py'],
        [py,'scripts/test_mmp_typed_graph_vectors.py'],
        [py,'scripts/test_mmp_inherited_typed_pairs.py'],
        [py,'scripts/test_mmp_inherited_pairs_instance_gate.py'],
        [py,'scripts/test_mmp_inherited_instance_vectors.py'],
        [py,'scripts/test_mmp_inherited_pairs_full_package.py'],
        [py,'scripts/test_mmp_junction_structure.py'],
        [py,'scripts/test_mmp_junction_profile_boundary.py'],
        [py,'scripts/test_mmp_junction_package_profile.py'],
        [py,'scripts/test_mmp_junction_profile_graph_package.py'],
        [py,'scripts/test_mmp_relation_inheritance_package.py'],
        [py,'scripts/test_mmp_effective_pairs_package.py'],
        [py,'scripts/test_mmp_interop.py'],
        [py,'scripts/test_mmp_consumer_security.py'],
        [py,'scripts/test_mmp_consumer_semantics.py'],
        [py,'scripts/test_mmp_identity_evolution.py'],
        [py,'scripts/test_mmp_conformance_declaration.py'],
        [py,'scripts/test_mmp_core_compatibility_review.py'],
        [py,'scripts/test_mmp_effective_properties.py'],
        [py,'scripts/test_mmp_cardinality.py'],
        [py,'scripts/test_mmp_defaults.py'],
        [py,'scripts/test_mmp_relationship_semantics.py'],
        [py,'scripts/test_mmp_version_extensions.py'],
        [py,'scripts/test_mmp_1_1_readiness.py'],
        [py,'scripts/test_mmp_relation_inheritance.py'],
        [py,'scripts/test_mmp_required_policy.py'],
        [py,'scripts/test_mmp_canonical_values.py'],
        [py,'scripts/test_mmp_extension_negotiation.py'],
        [py,'scripts/run_mmp_core_semantic_suite.py'],
        [py,'scripts/test_mmp_strict_coverage.py'],
        [py,'scripts/test_mmp_version_decision.py'],
        [py,'scripts/test_mmp_release_kit.py'],
        [py,'scripts/test_mmp_release_workflow.py'],
        [py,'scripts/test_semantic_validator.py'],
        [py,'scripts/test_sparx_mapping.py'],
        [py,'scripts/test_mdg_generator.py'],
        [py,'scripts/test_mdg_validation.py'],
        [py,'scripts/test_documentation_generator.py'],
        [py,'scripts/test_documentation_exports.py'],
        [py,'scripts/test_sparx_importer.py'],
        [py,'scripts/test_metamodel_diff.py'],
        [py,'scripts/test_source_adaptation.py'],
        [py,'scripts/test_workspace_resume.py'],
        [py,'scripts/project_hygiene.py','--project-root','.','--mode','checkpoint','--fix'],
        [py,'scripts/lint_gpt_project.py','--project-root','.'],
        [py,'scripts/project_hygiene.py','--project-root','.','--mode','final'],
    ]
    for cmd in commands: run(cmd, root)

    # The checkpoint hygiene gate may remove dist/, including a reports path
    # located below it. Recreate the report directory after all hygiene gates.
    reports.mkdir(parents=True, exist_ok=True)
    report={
        'status':'pass',
        'gates':[cmd[1] for cmd in commands],
        'gate_count':len(commands),
    }
    (reports/'ci-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'CI PASS: {len(commands)} gates')
    return 0

if __name__=='__main__': raise SystemExit(main())
