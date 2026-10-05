"""Install a Rephysics package into a compatible game, with rollback backups."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def install(game: Path) -> Path:
    game = game.resolve()
    if not game.is_dir(): raise ValueError('Game folder does not exist')
    source_game = (game/'cpe'/'backend.py').is_file() and (game/'cube_core.py').is_file()
    if not source_game:
        raise ValueError('Flash requires the updated game source with cpe/backend.py. Flash source, then rebuild the executable.')
    source = Path(__file__).parent
    destination, config = game/'cpe_rephysics', game/'cpe-backend.json'
    backup = game/'backup'/'rephysics'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup.mkdir(parents=True)
    manifest = {'package_existed': destination.exists(), 'config_existed': config.exists(), 'game': str(game)}
    if destination.exists(): shutil.copytree(destination, backup/'cpe_rephysics')
    if config.exists(): shutil.copy2(config, backup/'cpe-backend.json')
    (backup/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    staged = Path(tempfile.mkdtemp(prefix='.rephysics-', dir=game))
    try:
        shutil.copytree(source, staged/'cpe_rephysics', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (staged/'cpe_rephysics').glob('*.py')}
        if destination.exists(): shutil.rmtree(destination)
        shutil.move(str(staged/'cpe_rephysics'), destination)
        payload = {'backend': 'rephysics', 'version': '0.1.0', 'backup': str(backup.relative_to(game)), 'sha256': hashes}
        staged_config = staged/'cpe-backend.json'
        staged_config.write_text(json.dumps(payload, indent=2), encoding='utf-8')
        os.replace(staged_config, config)
    except Exception:
        restore(game, backup)
        raise
    finally:
        shutil.rmtree(staged)
    return backup


def restore(game: Path, backup: Path) -> None:
    game, backup = game.resolve(), backup.resolve()
    if not backup.is_relative_to(game/'backup'/'rephysics'): raise ValueError('Backup must be inside this game')
    manifest = json.loads((backup/'manifest.json').read_text(encoding='utf-8'))
    if manifest['game'] != str(game): raise ValueError('Backup belongs to another game')
    destination = game/'cpe_rephysics'
    if destination.exists(): shutil.rmtree(destination)
    if manifest['package_existed']: shutil.copytree(backup/'cpe_rephysics', destination)
    config = game/'cpe-backend.json'
    if manifest['config_existed']: shutil.copy2(backup/'cpe-backend.json', config)
    else: config.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description='Close the game before flashing or restoring CPE Rephysics.')
    parser.add_argument('action', choices=['install', 'restore'])
    parser.add_argument('--game', required=True, type=Path)
    parser.add_argument('--backup', type=Path)
    args = parser.parse_args()
    if args.action == 'install': print('Flashed CPE Rephysics. Backup:', install(args.game))
    else:
        if args.backup is None: parser.error('restore requires --backup')
        restore(args.game, args.backup); print('Restored previous engine. Rebuild the game executable.')

if __name__ == '__main__': main()
