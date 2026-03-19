from __future__ import annotations

import json
import unittest
from pathlib import Path

from camera_calibration_lab.io_utils import pair_stereo_images, write_json


class IoUtilsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workspace = Path(__file__).resolve().parents[1] / '.tmp_tests' / self._testMethodName
        self.workspace.mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        for path in sorted(self.workspace.rglob('*'), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        if self.workspace.exists():
            self.workspace.rmdir()

    def test_pair_stereo_images_matches_same_filename(self) -> None:
        left_dir = self.workspace / 'left'
        right_dir = self.workspace / 'right'
        left_dir.mkdir()
        right_dir.mkdir()
        (left_dir / '001.jpg').write_bytes(b'a')
        (left_dir / '002.jpg').write_bytes(b'b')
        (right_dir / '001.jpg').write_bytes(b'c')
        (right_dir / '003.jpg').write_bytes(b'd')

        pairs = pair_stereo_images(left_dir, right_dir)

        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][0].name, '001.jpg')
        self.assertEqual(pairs[0][1].name, '001.jpg')

    def test_write_json_serializes_nested_values(self) -> None:
        output = self.workspace / 'out' / 'result.json'

        write_json(output, {'name': 'demo', 'values': [1, 2, 3]})

        payload = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(payload['name'], 'demo')
        self.assertEqual(payload['values'], [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
