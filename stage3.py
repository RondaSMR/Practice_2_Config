import json
from typing import Dict, List, Set, Any
from stage2 import DependencyCollector

class DependencyGraph:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.collector = DependencyCollector(config)
        self.graph: Dict[str, List[str]] = {}
        self.visited: Set[str] = set()
        self.cyclic_dependencies: Set[str] = set()

    def dfs_build_graph(self, package_name: str, version: str, depth: int = 0, path: List[str] = None) -> None:
        if path is None:
            path = []

        if depth >= self.config['max_depth']:
            return

        package_key = f"{package_name}@{version}"

        if package_key in path:
            cycle_path = " -> ".join(path + [package_key])
            self.cyclic_dependencies.add(cycle_path)
            return

        if package_key in self.visited:
            return

        self.visited.add(package_key)
        current_path = path + [package_key]

        try:
            dependencies_data = self.collector.get_package_dependencies(package_name, version)
            dependencies = [(dep['name'], self._extract_version(dep['version'])) for dep in dependencies_data]

            if self.config['filter_substring']:
                dependencies = [(name, ver) for name, ver in dependencies
                                if self.config['filter_substring'] not in name]

            self.graph[package_key] = []

            for dep_name, dep_version in dependencies:
                dep_key = f"{dep_name}@{dep_version}"
                self.graph[package_key].append(dep_key)

                self.dfs_build_graph(dep_name, dep_version, depth + 1, current_path)

        except Exception as e:
            print(f"Ошибка при обработке пакета {package_name}: {e}")

    def _extract_version(self, version_range: str) -> str:
        if version_range.startswith('[') and version_range.endswith(']'):
            return version_range[1:-1]
        return version_range

    def display_graph(self) -> None:
        print(f"\nГраф зависимостей (максимальная глубина: {self.config['max_depth']}):")
        print("-" * 60)

        if not self.graph:
            print("Граф пуст")
            return

        for package, dependencies in self.graph.items():
            print(f"{package}:")
            if dependencies:
                for dep in dependencies:
                    print(f"  └── {dep}")
            else:
                print("  └── (нет зависимостей)")

        if self.cyclic_dependencies:
            print(f"\nОбнаружены циклические зависимости:")
            for cycle in self.cyclic_dependencies:
                print(f"{cycle}")

class Stage3CLI:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.graph_builder = DependencyGraph(config)

    def run_stage3(self) -> None:
        print("\nЭТАП 3: Основные операции с графом зависимостей")

        package_name = self.config['package_name']
        version = self.config['package_version']

        print(f"Анализ пакета {package_name} версии {version}")
        self.graph_builder.dfs_build_graph(package_name, version)

        self.graph_builder.display_graph()

        self._demonstrate_different_cases()

    def _demonstrate_different_cases(self) -> None:
        print("\nДЕМОНСТРАЦИЯ РАЗЛИЧНЫХ СЛУЧАЕВ")

        test_cases = [
            {"package": "Newtonsoft.Json", "version": "13.0.1", "max_depth": 2, "filter": ""},
            {"package": "NLog", "version": "5.0.0", "max_depth": 3, "filter": "System"},
            {"package": "AutoMapper", "version": "12.0.0", "max_depth": 1, "filter": ""},
        ]

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Тестовый случай {i} ---")
            print(f"Пакет: {test_case['package']}, Версия: {test_case['version']}")
            print(f"Макс.глубина: {test_case['max_depth']}, Фильтр: '{test_case['filter']}'")

            graph_builder = DependencyGraph({
                **self.config,
                'package_name': test_case['package'],
                'package_version': test_case['version'],
                'max_depth': test_case['max_depth'],
                'filter_substring': test_case['filter']
            })

            graph_builder.dfs_build_graph(test_case['package'], test_case['version'])

            root_key = f"{test_case['package']}@{test_case['version']}"
            if root_key in graph_builder.graph:
                deps = graph_builder.graph[root_key]
                if deps:
                    print(f"Зависимости: {', '.join(deps)}")
                else:
                    print("Зависимости не найдены")
            print("-" * 30)

def main_stage3():
    from stage1 import main_stage1

    config = main_stage1()

    cli = Stage3CLI(config)
    cli.run_stage3()

if __name__ == "__main__":
    main_stage3()