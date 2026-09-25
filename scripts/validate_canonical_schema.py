#!/usr/bin/env python3
from pathlib import Path
import json, sys, yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

ROOT=Path(__file__).resolve().parents[1]
SCHEMAS=ROOT/'schemas'
MAPPING={
 'metamodel.yaml':'metamodel.schema.json','properties.yaml':'properties.schema.json','constraints.yaml':'constraints.schema.json',
 'viewpoints.yaml':'viewpoints.schema.json','guidance.yaml':'guidance.schema.json','notation.yaml':'notation.schema.json','provenance.yaml':'provenance.schema.json','version.yaml':'version.schema.json'}

def load_yaml(p): return yaml.safe_load(p.read_text(encoding='utf-8'))
def load_json(p): return json.loads(p.read_text(encoding='utf-8'))

def validator(schema_name):
    schema=load_json(SCHEMAS/schema_name)
    common=load_json(SCHEMAS/'common-definitions.schema.json')
    registry=Registry().with_resource(common['$id'], Resource.from_contents(common))
    return Draft202012Validator(schema,registry=registry,format_checker=FormatChecker())

def validate_package(directory):
    errors=[]
    for file_name,schema_name in MAPPING.items():
        p=directory/file_name
        if not p.is_file(): errors.append(f'missing {p}'); continue
        doc=load_yaml(p)
        for e in sorted(validator(schema_name).iter_errors(doc), key=lambda x:list(x.absolute_path)):
            path='.'.join(map(str,e.absolute_path)) or '<root>'
            errors.append(f'{file_name}:{path}: {e.message}')
    return errors

def main():
    targets=[ROOT/'examples'/'architecture-lite', ROOT/'templates'/'metamodel']
    for target in targets:
        errs=validate_package(target)
        if errs: raise ValueError(f'{target}:\n'+'\n'.join(errs))
    negative_dir=ROOT/'tests'/'schema-invalid'
    for p in sorted(negative_dir.glob('*.yaml')):
        case=load_yaml(p); v=validator(case['schema'])
        if not list(v.iter_errors(case['document'])):
            raise ValueError(f'Negative schema case unexpectedly passed: {p.name}')
    print('Canonical schema v1 + guidance OK: 2 valid packages, 4 invalid fixtures rejected')
    return 0
if __name__=='__main__':
    try: raise SystemExit(main())
    except Exception as exc:
        print(str(exc),file=sys.stderr); raise SystemExit(1)
