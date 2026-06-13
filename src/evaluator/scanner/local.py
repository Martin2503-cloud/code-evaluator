from pathlib import Path

from evaluator.scanner.base import Scanner


class LocalScanner(Scanner):
    """Escáner que recorre un directorio local en busca de archivos .py.

    Busca recursivamente todos los archivos con extensión .py dentro del
    directorio especificado.

    Args:
        path: Ruta al directorio raíz del proyecto a escanear.

    Example:
        >>> import tempfile; from pathlib import Path
        >>> with tempfile.TemporaryDirectory() as tmp:
        ...     Path(tmp, "app.py").write_text("x=1")
        ...     Path(tmp, "sub").mkdir()
        ...     Path(tmp, "sub", "mod.py").write_text("y=2")
        ...     s = LocalScanner(tmp)
        ...     len(s.scan())
        2
    """
    def __init__(self, path: str) -> None:
        self._root = Path(path)

    def scan(self) -> list[str]:
        """Escanea el directorio recursively y devuelve los .py encontrados.

        Returns:
            Lista de rutas absolutas a archivos .py.

        Raises:
            NotADirectoryError: Si la ruta proporcionada no existe o no es un directorio.
        """
        if not self._root.is_dir():
            raise NotADirectoryError(f"Not a directory: {self._root}")
        return [
            str(p) for p in self._root.rglob("*.py") if p.is_file()
        ]
