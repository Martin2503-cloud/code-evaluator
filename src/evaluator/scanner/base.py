from abc import ABC, abstractmethod


class Scanner(ABC):
    """Escáner de código fuente.

    Interfaz base para todas las fuentes de código.
    Cada Scanner sabe cómo encontrar archivos .py desde un origen distinto.

    Example:
        >>> class MiScanner(Scanner):
        ...     def scan(self) -> list[str]:
        ...         return ["src/app.py"]
        >>> s = MiScanner()
        >>> s.scan()
        ['src/app.py']
    """

    @abstractmethod
    def scan(self) -> list[str]:
        """Escanea el origen y devuelve rutas de archivos .py.

        Returns:
            Lista de rutas absolutas a archivos .py encontrados.
            Vacía si no se encuentra ningún archivo.

        Raises:
            NotImplementedError: Si la subclase no implementa este método.
        """
        ...
