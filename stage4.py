from typing import Dict, List, Set, Any
from stage3 import DependencyGraph


class ReverseDependencyAnalyzer:
    def __init__(self, graph: Dict[str, List[str]]):
        self.graph = graph
        self.reverse_graph: Dict[str, List[str]] = {}

    def build_reverse_graph(self) -> None:
        self.reverse_graph = {}

        for package, dependencies in self.graph.items():
            for dep in dependencies:
                if dep not in self.reverse_graph:
                    self.reverse_graph[dep] = []
                if package not in self.reverse_graph[dep]:
                    self.reverse_graph[dep].append(package)

            if package not in self.reverse_graph:
                self.reverse_graph[package] = []

    def find_reverse_dependencies(self, target_package: str, max_depth: int = 3) -> Dict[str, Any]:
        if not self.reverse_graph:
            self.build_reverse_graph()

        result = {
            'target': target_package,
            'reverse_deps': [],
            'all_dependencies': set()
        }

        self._dfs_reverse_deps(target_package, max_depth, 0, set(), result)
        return result

    def _dfs_reverse_deps(self, current_package: str, max_depth: int,
                          current_depth: int, visited: Set[str], result: Dict[str, Any]) -> None:
        if current_depth > max_depth or current_package in visited:
            return

        visited.add(current_package)

        if current_package in self.reverse_graph:
            for dependent in self.reverse_graph[current_package]:
                if dependent not in result['all_dependencies']:
                    result['reverse_deps'].append({
                        'package': dependent,
                        'depth': current_depth
                    })
                    result['all_dependencies'].add(dependent)

                self._dfs_reverse_deps(dependent, max_depth, current_depth + 1, visited, result)

    def display_reverse_dependencies(self, target_package: str, max_depth: int = 3) -> None:
        result = self.find_reverse_dependencies(target_package, max_depth)

        print(f"\nОбратные зависимости для пакета {target_package}:")
        print("-" * 50)

        if not result['reverse_deps']:
            print("  Обратные зависимости не найдены")
            return

        result['reverse_deps'].sort(key=lambda x: (x['depth'], x['package']))

        for dep in result['reverse_deps']:
            indent = "  " * dep['depth']
            arrow = "↳ " if dep['depth'] > 0 else "• "
            print(f"{indent}{arrow}{dep['package']}")


class Stage4CLI:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.graph_builder = DependencyGraph(config)

    def run_stage4(self) -> None:
        print("\nЭТАП 4: Обратные зависимости")

        package_name = self.config['package_name']
        version = self.config['package_version']

        print(f"Построение графа для {package_name}@{version}...")
        self.graph_builder.dfs_build_graph(package_name, version)

        analyzer = ReverseDependencyAnalyzer(self.graph_builder.graph)

        test_packages = [
            f"{package_name}@{version}",
            'Microsoft.NETFramework.ReferenceAssemblies@4.6.2',
            'System.Runtime@4.3.0'
        ]

        for test_package in test_packages:
            print(f"\nАнализ пакета: {test_package}")
            print("-" * 40)
            analyzer.display_reverse_dependencies(test_package, max_depth=2)


def main_stage4():
    from stage1 import main_stage1
    config = main_stage1()
    cli = Stage4CLI(config)
    cli.run_stage4()


if __name__ == "__main__":
    main_stage4()