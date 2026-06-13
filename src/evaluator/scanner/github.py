import shutil
import subprocess
import tempfile
from pathlib import Path

from evaluator.scanner.base import Scanner


class GithubScanner(Scanner):
    """Escáner que clona un repositorio GitHub y escanea sus archivos .py.

    Clona el repositorio a un directorio temporal, escanea los archivos .py,
    y limpia el directorio temporal al finalizar (vía __del__).

    Args:
        url: URL completa del repositorio GitHub (https://github.com/usuario/repo).

    Raises:
        RuntimeError: Si el clonado falla por timeout o error de git.

    Example:
        >>> s = GithubScanner("https://github.com/usuario/repo")
        >>> # s.scan()  # requiere conexión a internet y git instalado
    """
    def __init__(self, url: str) -> None:
        self._url = url
        self._tmpdir: str | None = None

    def scan(self) -> list[str]:
        """Clona el repo y devuelve los archivos .py encontrados.

        Returns:
            Lista de rutas absolutas a archivos .py dentro del repo clonado.

        Raises:
            RuntimeError: Si git clone falla (URL inválida, timeout, red).
        """
        self._tmpdir = tempfile.mkdtemp()
        try:
            subprocess.run(
                ["git", "clone", self._url, self._tmpdir],
                capture_output=True, check=True, timeout=120,
            )
            return [
                str(p) for p in Path(self._tmpdir).rglob("*.py") if p.is_file()
            ]
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            self._cleanup()
            raise RuntimeError(f"Failed to clone {self._url}") from e

    def _cleanup(self) -> None:
        """Elimina el directorio temporal si existe."""
        if self._tmpdir:
            shutil.rmtree(self._tmpdir, ignore_errors=True)
            self._tmpdir = None

    def __del__(self) -> None:
        """Garantiza limpieza del directorio temporal al destruir el objeto."""
        self._cleanup()
