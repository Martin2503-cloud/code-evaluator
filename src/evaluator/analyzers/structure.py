import ast

from evaluator.models import Finding
from evaluator.analyzers.base import Analyzer


class StructureAnalyzer(Analyzer):
    """Analizador de arquitectura usando el módulo AST de Python.

    Analiza el código fuente sin ejecutarlo para detectar:
      - Funciones demasiado largas (> 50 líneas)
      - Funciones con demasiados parámetros (> 6)
      - Herencia excesivamente profunda (> 3 niveles)

    No requiere herramientas externas; funciona sobre cualquier Python >= 3.9.

    Example:
        >>> a = StructureAnalyzer()
        >>> code = "def f(a, b, c, d, e, f, g, h): pass"
        >>> findings = a.analyze_source(code)
        >>> len(findings)
        1
        >>> findings[0].message
        'Too many parameters in f: 8'
    """
    def analyze(self, files: list[str]) -> list[Finding]:
        """Analiza archivos .py del disco usando AST.

        Args:
            files: Lista de rutas a archivos .py.

        Returns:
            Hallazgos de arquitectura (funciones largas, muchos params, herencia profunda).
        """
        findings: list[Finding] = []
        for filepath in files:
            try:
                with open(filepath, encoding="utf-8") as f:
                    source = f.read()
            except OSError:
                continue
            findings.extend(self.analyze_source(source, filepath))
        return findings

    def analyze_source(self, source: str, filename: str = "<unknown>") -> list[Finding]:
        """Analiza código fuente en memoria usando AST.

        Útil para tests o cuando el código ya está cargado en memoria.

        Args:
            source: Código fuente como string.
            filename: Nombre del archivo (para referencia en hallazgos).

        Returns:
            Hallazgos de arquitectura.

        Example:
            >>> a = StructureAnalyzer()
            >>> code = "def long():\\n" + "    pass\\n" * 60
            >>> len(a.analyze_source(code))
            1
        """
        try:
            tree = ast.parse(source, filename=filename)
        except SyntaxError:
            return []
        return self._analyze_file(filename, tree)

    def _analyze_file(self, filepath: str, tree: ast.AST) -> list[Finding]:
        """Recorre el AST y genera hallazgos por función o clase problemática.

        Args:
            filepath: Ruta del archivo (para identificar hallazgos).
            tree: AST parseado del archivo.

        Returns:
            Hallazgos detectados en el AST.
        """
        findings: list[Finding] = []
        class_map = self._build_class_map(tree)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                num_lines = self._node_line_count(node)
                if num_lines > 50:
                    findings.append(Finding(
                        file=filepath,
                        line=node.lineno or 0,
                        severity="warning",
                        message=f"Function too long: {node.name} ({num_lines} lines)",
                        dimension="architecture",
                    ))
                num_params = len(node.args.args)
                if num_params > 6:
                    findings.append(Finding(
                        file=filepath,
                        line=node.lineno or 0,
                        severity="warning",
                        message=f"Too many parameters in {node.name}: {num_params}",
                        dimension="architecture",
                    ))
            elif isinstance(node, ast.ClassDef):
                depth = self._compute_true_depth(node.name, class_map)
                if depth > 3:
                    findings.append(Finding(
                        file=filepath,
                        line=node.lineno or 0,
                        severity="info",
                        message=f"Deep inheritance in {node.name}: depth {depth}",
                        dimension="architecture",
                    ))
        return findings

    @staticmethod
    def _node_line_count(node: ast.AST) -> int:
        """Calcula líneas que ocupa un nodo AST.

        Usa end_lineno (Python 3.8+) cuando está disponible.

        Args:
            node: Nodo AST (FunctionDef, ClassDef, etc.).

        Returns:
            Cantidad de líneas que ocupa el nodo.
        """
        if hasattr(node, "end_lineno") and hasattr(node, "lineno"):
            return (node.end_lineno or node.lineno) - (node.lineno or 0) + 1
        return 0

    @staticmethod
    def _inheritance_depth(cls_node: ast.ClassDef) -> int:
        """Calcula profundidad de herencia directa (bases inmediatas).

        Nota: Preferir _compute_true_depth para herencia en cadena.

        Args:
            cls_node: Nodo ClassDef del AST.

        Returns:
            Cantidad de clases base directas.
        """
        return len(cls_node.bases)

    def _build_class_map(self, tree: ast.AST) -> dict[str, ast.ClassDef]:
        """Construye un mapa nombre → ClassDef desde el AST.

        Args:
            tree: AST del archivo.

        Returns:
            Diccionario con nombre de clase como clave y su nodo AST como valor.
        """
        return {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, ast.ClassDef)
        }

    def _compute_true_depth(self, name: str, class_map: dict[str, ast.ClassDef], depth: int = 0) -> int:
        """Calcula la profundidad real de herencia siguiendo la cadena.

        Recorre recursivamente las clases base para determinar
        cuántos niveles de herencia tiene una clase.

        Args:
            name: Nombre de la clase a evaluar.
            class_map: Mapa de todas las clases del archivo.
            depth: Profundidad acumulada (usar 0 en llamada inicial).

        Returns:
            Profundidad máxima de la cadena de herencia.
        """
        cls = class_map.get(name)
        if not cls or not cls.bases:
            return depth
        max_base = 0
        for base in cls.bases:
            if isinstance(base, ast.Name):
                max_base = max(max_base, self._compute_true_depth(base.id, class_map, depth + 1))
        return max_base if max_base > 0 else depth
