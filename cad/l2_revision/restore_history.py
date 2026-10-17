"""Restore exact historical STEP parts, without overwriting differing files."""
from pathlib import Path, PurePosixPath
import argparse, json, zipfile

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / 'releases/Quietmirror-L2-Research/history'
BASE = HISTORY / 'R3_2_BASELINE_ASSEMBLY.zip'

def safe_path(destination, name):
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts:
        raise ValueError('Unsafe archive member: ' + name)
    target = (destination / Path(*rel.parts)).resolve()
    if not target.is_relative_to(destination.resolve()):
        raise ValueError('Destination escaped: ' + name)
    return target

def prepare():
    # R3.1/R3.2 historical STEP packages are deltas over R3.
    chain = [
        ('releases/Fenrir-MiniSE-R3/R3_STEP.zip', 'exports/rebuild_r3/assembly/'),
        ('releases/Fenrir-MiniSE-R3.1/R3_1_STEP.zip', 'exports/rebuild_r3_1/assembly/'),
        ('releases/Fenrir-MiniSE-R3.2/R3_2_STEP.zip', 'exports/rebuild_r3_2/assembly/'),
    ]
    parts = {}
    for archive, prefix in chain:
        with zipfile.ZipFile(ROOT / archive) as z:
            parts.update({'assembly/' + PurePosixPath(n).name: z.read(n)
                          for n in z.namelist() if n.startswith(prefix) and n.endswith('.step')})
    assert len(parts) == 72, len(parts)
    for name, data in parts.items():
        current = ROOT / 'exports/rebuild_r3_2' / name
        if current.exists() and current.read_bytes() != data:
            raise ValueError('Local R3.2 differs from published archive chain: ' + name)
    with zipfile.ZipFile(BASE, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for name, data in sorted(parts.items()):
            z.writestr(name, data)
        z.writestr('BASELINE_SOURCE.json', json.dumps({
            'commit': 'f1b1090931d717117287ea2b79c2e14ddc234937',
            'parts': 72, 'source_archive_chain': [p[0] for p in chain],
            'verification': 'Exact byte equality to the preserved local R3.2 assembly',
        }, indent=2))
    print('Prepared exact 72-part baseline:', BASE)

def materialize(version):
    with zipfile.ZipFile(BASE) as z:
        baseline = {n: z.read(n) for n in z.namelist() if n.endswith('.step')}
    if version == 'R3.2':
        return baseline
    archive = HISTORY / (version + '_CAD_DELTA.zip')
    with zipfile.ZipFile(archive) as z:
        manifest = json.loads(z.read('RESTORE_MANIFEST.json'))
        result = {}
        for row in manifest['files']:
            name = row['path']
            data = baseline[name] if row['source'] == 'R3.2 preserved baseline' else z.read(name)
            assert len(data) == row['bytes'], name
            result[name] = data
        return result

def audit():
    entries = json.loads((HISTORY / 'INDEX.json').read_text())
    checked = []
    for row in entries:
        parts = materialize(row['version'])
        assert len(parts) == row['files']
        local = ROOT / 'exports/l2_revision' / row['version']
        mismatches = [name for name, data in parts.items()
                      if (local / name).exists() and (local / name).read_bytes() != data]
        assert not mismatches, (row['version'], mismatches)
        checked.append({'version': row['version'], 'restorable_step_files': len(parts)})
    report = {'baseline_parts': 72, 'candidate_archives': len(checked),
              'all_archive_members_resolved': True,
              'all_present_local_step_bytes_equal': True, 'versions': checked,
              'scope': 'Archive restoration integrity, not CAD/printing/fit acceptance.'}
    out = ROOT / 'reports/l2_revision/history_restoration.json'
    out.write_text(json.dumps(report, indent=2) + '\n')
    print('All historical archives restore:', len(checked))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('version', nargs='?')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--prepare-baseline', action='store_true')
    parser.add_argument('--audit', action='store_true')
    args = parser.parse_args()
    if args.prepare_baseline:
        prepare()
    if args.audit:
        audit()
    if args.version:
        if args.output is None:
            parser.error('--output is required; choose the explicit restoration folder')
        parts = materialize(args.version)
        # Check all destinations before writing any part.
        for name, data in parts.items():
            target = safe_path(args.output, name)
            if target.exists() and target.read_bytes() != data:
                raise FileExistsError('Will not replace differing file: ' + str(target))
        for name, data in parts.items():
            target = safe_path(args.output, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_bytes(data)
        print('Restored', args.version, len(parts), 'STEP parts to', args.output.resolve())

if __name__ == '__main__':
    main()
