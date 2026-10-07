"""Regression checks for incremental assets and the editor/build boundary."""
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import build as builder
import serve
from build_assets import copy_asset
from site_pages import render_pages


class BuildChecks(unittest.TestCase):
    def test_asset_bytes_not_timestamps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, destination = root / 'source', root / 'destination'
            original = b'a' * (1024 * 1024 + 7)
            source.write_bytes(original)
            self.assertTrue(copy_asset(source, destination))
            original_stat = source.stat()
            target_time = destination.stat().st_mtime_ns
            os.utime(source, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns + 1000000))
            self.assertFalse(copy_asset(source, destination))
            self.assertEqual(target_time, destination.stat().st_mtime_ns)
            # A same-size edit beyond the first chunk, with the timestamp restored.
            source.write_bytes(original[:-1] + b'b')
            os.utime(source, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
            self.assertTrue(copy_asset(source, destination))
            self.assertEqual(source.read_bytes(), destination.read_bytes())
            destination.unlink()
            self.assertTrue(copy_asset(source, destination))
            source.write_bytes(b'')
            self.assertTrue(copy_asset(source, destination))
            self.assertFalse(copy_asset(source, destination))

    def test_repeat_build_and_text_edit_keep_assets(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(builder, 'DIST', Path(directory)):
            with patch('sys.stdout', new=io.StringIO()):
                builder.build()
            assets = {p: p.stat().st_mtime_ns for p in (builder.DIST / 'assets').rglob('*') if p.is_file()}
            data = json.loads(builder.CONTENT.read_text())
            data['sites']['tas']['intro'] = '构建边界验证文字。'
            with patch.object(builder, 'copy_asset', wraps=copy_asset) as copier, patch('sys.stdout', new=io.StringIO()):
                pages = builder.build(data)
            self.assertIn('构建边界验证文字。', pages['tas/index.html'])
            self.assertEqual(assets, {p: p.stat().st_mtime_ns for p in assets})
            self.assertGreater(copier.call_count, 100)
            self.assertNotIn('构建边界验证文字。', builder.CONTENT.read_text())

    def test_topic_styles_and_links(self):
        data = json.loads(builder.CONTENT.read_text())
        pages, records, images = render_pages(data)
        self.assertEqual((len(pages), len(records)), (60, 489))
        for route, html in pages.items():
            self.assertIn('/assets/style.css', html)
            if route.startswith('arkham/'):
                self.assertIn('/assets/arkham.css', html)
                self.assertNotIn('/assets/tas.css', html)
                self.assertNotIn('href="/people/kevin-conroy/', html)
                self.assertNotIn('href="/tas/', html)
            elif route.startswith('tas/'):
                self.assertIn('/assets/tas.css', html)
                self.assertNotIn('/assets/arkham.css', html)
                self.assertIn('/assets/tas-motion.js', html)
            else:
                self.assertNotIn('/assets/tas.css', html)
                self.assertNotIn('/assets/arkham.css', html)
            if not route.startswith('tas/'):
                self.assertNotIn('/assets/tas-motion.js', html)

    def test_editor_save_conflict_and_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = root / 'archive.json'
            original = builder.CONTENT.read_bytes()
            content.write_bytes(original)
            with patch.object(serve, 'CONTENT', content), patch.object(serve, 'ROOT', root), patch.object(builder, 'DIST', root / 'dist'), patch('sys.stdout', new=io.StringIO()):
                builder.build()
                def request(payload):
                    handler = serve.Handler.__new__(serve.Handler)
                    encoded = json.dumps(payload).encode()
                    handler.rfile = io.BytesIO(encoded)
                    handler.path = '/api/editor'
                    handler.server = SimpleNamespace(server_port=8765)
                    handler.headers = {'Host': '127.0.0.1:8765', 'Origin': 'http://127.0.0.1:8765', 'X-Editor-Token': serve.TOKEN, 'Content-Length': str(len(encoded))}
                    responses = []
                    handler.reply = lambda code, body: responses.append((code, body))
                    handler.do_POST()
                    return responses[0]
                version = serve.digest()
                payload = {'version': version, 'path': ['sites', 'tas', 'intro'], 'value': '编辑器保存验证。'}
                self.assertEqual(request(payload)[0], 200)
                saved = json.loads(content.read_text())
                expected = json.loads(original)
                expected['sites']['tas']['intro'] = payload['value']
                expected['updated'] = saved['updated']
                self.assertEqual(saved, expected)
                self.assertEqual(next((root / 'backups').glob('*.json')).read_bytes(), original)
                self.assertIn(payload['value'], (builder.DIST / 'tas/index.html').read_text())
                self.assertEqual(request(payload)[0], 409)
                payload['version'] = serve.digest()
                forbidden = dict(payload, path=['games', 0, 'developer'])
                self.assertEqual(request(forbidden)[0], 400)
                saved_bytes = content.read_bytes()
                def failed_build(data):
                    if data['sites']['tas']['intro'] == '触发构建失败。':
                        raise RuntimeError('fixture failure')
                    return builder.build(data)
                with patch.object(serve, 'build', side_effect=failed_build):
                    self.assertEqual(request(dict(payload, value='触发构建失败。'))[0], 500)
                self.assertEqual(content.read_bytes(), saved_bytes)
                self.assertFalse(content.with_suffix('.tmp').exists())
                self.assertIn('编辑器保存验证。', (builder.DIST / 'tas/index.html').read_text())


if __name__ == '__main__':
    unittest.main()
