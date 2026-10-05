import builtins
import math
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cpe_rephysics import CubePhysicsEngine, physics as p
from cpe_rephysics.flash import install, restore


class RephysicsTests(unittest.TestCase):
    def test_floor_and_collisions_are_finite(self):
        engine = CubePhysicsEngine(500, 400, floor_y=360, particle_seed=1)
        engine.spawn('circle', 210, 100, 20, 1, (200, 100, 30))
        engine.spawn('polygon', 220, 160, 22, 2, (30, 200, 100), sides=5)
        for _ in range(600): engine.step(1/120)
        for record in engine.bodies.values():
            self.assertTrue(math.isfinite(record.body.position.y))
            self.assertLess(record.body.position.y, 360)
        self.assertGreater(len(engine.particles.particles), 0)

    def test_impulse_collision_conserves_linear_momentum(self):
        space = p.Space(); space.gravity = (0, 0)
        a, b = p.Body(1, 50), p.Body(1, 50)
        a.position, b.position = (0, 0), (19, 0)
        a.velocity, b.velocity = (10, 0), (-10, 0)
        ca, cb = p.Circle(a, 10), p.Circle(b, 10)
        ca.elasticity = cb.elasticity = 1
        space.add(a, b, ca, cb); space.step(.001)
        self.assertLess(a.velocity.x, 0)
        self.assertGreater(b.velocity.x, 0)
        self.assertAlmostEqual(a.velocity.x+b.velocity.x, 0)

    def test_numeric_commands_and_pause(self):
        engine = CubePhysicsEngine()
        engine.execute_line('CPE/1 1 2 200 100 20 1 255 90 30')
        engine.execute_line('CPE/1 2 11 1 15 0')
        engine.execute_line('CPE/1 3 40 1')
        before = tuple(engine.bodies[1].body.position)
        engine.step(.1)
        self.assertEqual(before, tuple(engine.bodies[1].body.position))
        engine.execute_line('CPE/1 4 30')
        self.assertFalse(engine.bodies)

    def test_flash_restore_preserves_previous_files(self):
        with tempfile.TemporaryDirectory() as folder:
            game = Path(folder); (game/'cpe').mkdir()
            (game/'cpe'/'backend.py').write_text('# compatible')
            (game/'cube_core.py').write_text('# game')
            (game/'cpe_rephysics').mkdir()
            (game/'cpe_rephysics'/'original.txt').write_text('previous')
            (game/'cpe-backend.json').write_text('{"backend":"classic"}')
            backup = install(game)
            self.assertTrue((game/'cpe_rephysics'/'physics.py').exists())
            restore(game, backup)
            self.assertEqual((game/'cpe_rephysics'/'original.txt').read_text(), 'previous')
            self.assertEqual((game/'cpe-backend.json').read_text(), '{"backend":"classic"}')

if __name__ == '__main__': unittest.main()
