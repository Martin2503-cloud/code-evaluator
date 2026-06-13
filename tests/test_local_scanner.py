import tempfile
from pathlib import Path

from evaluator.scanner.local import LocalScanner


class TestLocalScanner:
    def test_scans_py_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.py").write_text("")
            Path(tmp, "b.py").write_text("")
            Path(tmp, "c.txt").write_text("")
            Path(tmp, "sub").mkdir()
            Path(tmp, "sub", "d.py").write_text("")

            files = LocalScanner(tmp).scan()
            assert len(files) == 3
            assert any(f.endswith("a.py") for f in files)
            assert any(f.endswith("d.py") for f in files)

    def test_no_py_files_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "readme.md").write_text("")
            files = LocalScanner(tmp).scan()
            assert files == []

    def test_invalid_directory_raises(self):
        import pytest
        with pytest.raises(NotADirectoryError):
            LocalScanner("/nonexistent/path").scan()
