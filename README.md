# CPE Rephysics 0.1.0

An experimental independent 2D physics engine for The Cube Beta. The solver is
written in Python and does not use Pymunk or Chipmunk. It preserves CPE/1 numeric
commands and the Integrated Particle Engine (IPE), so existing CPE Node.js,
Java, Aspire, and Go-cache bridges can keep using the same command format.

The first version supports circles and convex polygons, gravity, forces,
rotational impulses, friction, collision particles, floor/side boundaries,
dragging through the game's adapter, and deterministic fixed simulation steps.
Rendering optionally uses Pygame. This is a prototype, not a full replacement
for every Pymunk API: joints, arbitrary segment obstacles, concave meshes,
continuous collision detection, and robust tall-stack stabilization are not
implemented. Boundary segments currently follow the CPE floor/side-wall layout.

## Run

Python 3.11 or newer is required. Physics itself has no external dependencies.

```console
python -m unittest test_rephysics -v
python -m pip install .
```

```python
from cpe_rephysics import CubePhysicsEngine
engine = CubePhysicsEngine()
engine.execute_line('CPE/1 1 2 200 100 20 1 255 90 30')
engine.step(1 / 60)
print(engine.snapshot())
```

## Flash into The Cube Beta

Close the game. Use the updated game source containing `cpe/backend.py`, then
run this command from this repository:

```console
python -m cpe_rephysics.flash install --game "C:\path\to\THE-CUBE-GITHUB"
```

This installs `cpe_rephysics/`, writes `cpe-backend.json`, and records the previous
engine package and configuration in `backup/rephysics/<timestamp>/`. It injects
the engine through the game's Python backend API. It does not patch a running
process or modify executable bytes. Launch the Python game to use it immediately;
rebuild the packaged executable with the updated game build configuration.

Restore using the backup path printed during installation:

```console
python -m cpe_rephysics.flash restore --game "C:\path\to\THE-CUBE-GITHUB" --backup "C:\path\to\THE-CUBE-GITHUB\backup\rephysics\timestamp"
```

Close and restart the game after changing engines. Rebuild the executable after
restoring a packaged game's source. Backups are retained for manual recovery.

## Licence and origin

MIT, copyright (c) 2026 nutty'inc. The CPE protocol, rendering, and IPE modules
derive from the MIT-licensed CPE implementation in The Cube Beta. The independent
solver lives in `cpe_rephysics/physics.py`; no Pymunk solver code is included.
