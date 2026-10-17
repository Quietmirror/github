"""Publish the existing L2 research geometry under the R3.3 version layout.

This is a packaging/versioning step. It does not rebuild CAD or change any
validation result. Run from the complete repository with the L2 assets present.
"""
from pathlib import Path
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'releases/Quietmirror-L2-Research'
DEST = ROOT / 'releases/Fenrir-MiniSE-R3.3'
REPORT = ROOT / 'reports/rebuild_r3_3'
SOURCE_COMMIT = '4bce8639f48f880ffa490caaed50b67829bd5343'

ALIASES = {
    'FENRIR_MINISE_R3_3.FCStd': 'FULL_ASSEMBLY_COMMON.FCStd',
    'FENRIR_MINISE_R3_3_PLA_PRINT_PLATE.3mf': 'COMMON_ALL_PARTS_SINGLE_PLATE.3mf',
    'R3_3_PRINT_STL.zip': 'COMMON_ALL_PARTS_STL.zip',
    'R3_3_STEP.zip': 'COMMON_INDIVIDUAL_STEP.zip',
    'R3_3_FULL_ASSEMBLY_STEP.zip': 'FULL_ASSEMBLY_COMMON_STEP.zip',
    'R3_3_CAD_VIEWS.zip': 'COMMON_ALL_CAD_VIEWS.zip',
    'FENRIR_MINISE_R3_3_H_EST.FCStd': 'FULL_ASSEMBLY_H.FCStd',
    'FENRIR_MINISE_R3_3_H_EST_PLA_PRINT_PLATE.3mf': 'H_ALL_PARTS_SINGLE_PLATE.3mf',
    'R3_3_H_EST_PRINT_STL.zip': 'H_ALL_PARTS_STL.zip',
    'R3_3_H_EST_STEP.zip': 'H_INDIVIDUAL_STEP.zip',
    'R3_3_H_EST_FULL_ASSEMBLY_STEP.zip': 'FULL_ASSEMBLY_H_STEP.zip',
    'R3_3_H_EST_CAD_VIEWS.zip': 'H_ALL_CAD_VIEWS.zip',
    'FENRIR_MINISE_R3_3_D_EST.FCStd': 'FULL_ASSEMBLY_D.FCStd',
    'FENRIR_MINISE_R3_3_D_EST_PLA_PRINT_PLATE.3mf': 'D_ALL_PARTS_SINGLE_PLATE.3mf',
    'R3_3_D_EST_PRINT_STL.zip': 'D_ALL_PARTS_STL.zip',
    'R3_3_D_EST_STEP.zip': 'D_INDIVIDUAL_STEP.zip',
    'R3_3_D_EST_FULL_ASSEMBLY_STEP.zip': 'FULL_ASSEMBLY_D_STEP.zip',
    'R3_3_D_EST_CAD_VIEWS.zip': 'D_ALL_CAD_VIEWS.zip',
    'R3_3_BOTH_ADAPTER_KITS_SINGLE_PLATE.3mf': 'BOTH_ADAPTER_KITS_SINGLE_PLATE.3mf',
    'R3_3_VALIDATION_REPORTS.zip': 'ALL_VALIDATION_REPORTS.zip',
    'R3_3_DESIGN_STUDIES.zip': 'TOPOLOGY_AND_SIDE_COMPARISON_VIEWS.zip',
}
VIEWS = {
    'R3_3_FOUR_VIEWS.png': 'F1H/FOUR_VIEWS.png',
    'R3_3_SIDE_DETAIL.png': 'F1H/side_detail.png',
    'R3_3_PRINT_PLATE.png': 'F1H/PRINT_PLATE.png',
    'R3_3_H_EST_FOUR_VIEWS.png': 'L2_H_EST/FOUR_VIEWS.png',
    'R3_3_D_EST_FOUR_VIEWS.png': 'L2_D_EST/FOUR_VIEWS.png',
    'R3_3_MASS_PARTITIONS.png': 'studies/A_B_C_D_EXPLAINED.png',
    'R3_2_VS_R3_3.png': 'studies/R32_F1H_COMPARISON.png',
}

def put(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf8', newline='\n')

def copy_exact(src, target, records):
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, target)
    assert target.read_bytes() == src.read_bytes(), target
    records.append({'path': target.relative_to(ROOT).as_posix(),
                    'source': src.relative_to(ROOT).as_posix(),
                    'bytes': target.stat().st_size, 'byte_identical': True})

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    REPORT.mkdir(parents=True, exist_ok=True)
    records = []
    for target, source in ALIASES.items():
        copy_exact(SOURCE/source, DEST/target, records)
    for target, source in VIEWS.items():
        copy_exact(ROOT/'views/l2_revision'/source, ROOT/'views/rebuild_r3_3'/target, records)
    counts = {}
    for variant, archive, folder, expected in [
        ('common', 'COMMON_ALL_PARTS_STL.zip', 'print', 9),
        ('H_EST', 'H_ALL_PARTS_STL.zip', 'h/print', 11),
        ('D_EST', 'D_ALL_PARTS_STL.zip', 'd/print', 11),
    ]:
        with zipfile.ZipFile(SOURCE/archive) as z:
            assert z.testzip() is None, archive
            names = [n for n in z.namelist() if n.lower().endswith('.stl')]
            assert len(names) == expected, (variant, len(names))
            counts[variant] = len(names)
            for name in names:
                assert name == Path(name).name, name
                target = ROOT/'exports/rebuild_r3_3'/folder/name
                target.parent.mkdir(parents=True, exist_ok=True)
                data = z.read(name)
                target.write_bytes(data)
                assert target.read_bytes() == data
                records.append({'path': target.relative_to(ROOT).as_posix(),
                                'source_archive': (SOURCE/archive).relative_to(ROOT).as_posix(),
                                'member': name, 'bytes': len(data), 'byte_identical': True})
    for name in ALIASES:
        if name.endswith(('.zip', '.FCStd', '.3mf')):
            with zipfile.ZipFile(DEST/name) as z:
                assert z.testzip() is None, name
    # A source bundle for use in the complete repository; not a bundled CAD runtime.
    source_files = []
    for folder in ['cad/rebuild_r2', 'cad/rebuild_r3', 'cad/rebuild_r3_1',
                   'cad/rebuild_r3_2', 'cad/l2_revision', 'cad/rebuild_r3_3']:
        source_files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file()
                            and '__pycache__' not in p.parts
                            and p.suffix in ['.py', '.json', '.md', '.ps1', '.ini'])
    source_files.extend([ROOT/'LICENSE', ROOT/'NOTICE.md'])
    with zipfile.ZipFile(DEST/'R3_3_SOURCE.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(set(source_files)):
            z.write(p, p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(DEST/'R3_3_SOURCE.zip') as z:
        assert z.testzip() is None
    manifest = {'version': 'r3_3', 'display_version': 'R3.3',
                'source_commit': SOURCE_COMMIT, 'geometry_changed': False,
                'internal_variant_ids': ['F1H', 'L2_H_EST', 'L2_D_EST', 'L2_BOTH_EST'],
                'full_spec_acceptance': False, 'real_electronics_fit': False,
                'printable_part_counts': counts, 'aliases': records}
    put(DEST/'R3_3_MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    check = {'version': 'r3_3', 'package_validation_passed': True,
             'geometry_changed': False, 'byte_identical_aliases': len(records),
             'printable_part_counts': counts, 'archive_integrity_checked': True,
             'scope': 'Packaging integrity only. Inherit engineering results and all blockers from L2.'}
    put(REPORT/'package_checks.json', json.dumps(check, indent=2)+'\n')
    print(json.dumps(check, ensure_ascii=False), flush=True)

if __name__ == '__main__':
    main()
