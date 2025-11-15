import subprocess
import os
from typing import Dict, List, Any
from stage3 import DependencyGraph

class GraphVisualizer:

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.graph_builder = DependencyGraph(config)

    def generate_graphviz_dot(self, graph: Dict[str, List[str]]) -> str:
        dot_lines = [
            "digraph DependencyGraph {",
            "    rankdir=TB;",
            "    node [shape=box, style=filled, fillcolor=lightblue];",
            "    edge [color=darkgreen];",
            ""
        ]

        for package in graph.keys():
            if package == f"{self.config['package_name']}@{self.config['package_version']}":
                dot_lines.append(f'    "{package}" [fillcolor=orange];')
            else:
                dot_lines.append(f'    "{package}";')

        dot_lines.append("")

        for package, dependencies in graph.items():
            for dep in dependencies:
                dot_lines.append(f'    "{package}" -> "{dep}";')

        dot_lines.append("}")

        return "\n".join(dot_lines)

    def generate_ascii_tree(self, graph: Dict[str, List[str]], start_node: str) -> List[str]:
        result = []

        def build_ascii_tree(node: str, prefix: str = "", is_last: bool = True) -> None:
            connector = "└── " if is_last else "├── "
            result.append(prefix + connector + node)

            if node in graph:
                dependencies = graph[node]
                new_prefix = prefix + ("    " if is_last else "│   ")

                for i, dep in enumerate(dependencies):
                    is_last_dep = i == len(dependencies) - 1
                    build_ascii_tree(dep, new_prefix, is_last_dep)

        build_ascii_tree(start_node)
        return result

    def display_ascii_tree(self, graph: Dict[str, List[str]], start_node: str) -> None:
        print(f"\nASCII-дерево зависимостей для {start_node}:")
        print("=" * 60)

        tree_lines = self.generate_ascii_tree(graph, start_node)
        for line in tree_lines:
            print(line)

    def save_dot_file(self, dot_content: str, filename: str = "dependency_graph.dot") -> str:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dot_content)
        return filename

    def generate_image(self, dot_filename: str, output_format: str = "png") -> str:
        output_filename = dot_filename.replace('.dot', f'.{output_format}')

        try:
            subprocess.run([
                'dot', f'-T{output_format}',
                dot_filename, '-o', output_filename
            ], check=True)
            return output_filename
        except subprocess.CalledProcessError as e:
            print(f"Ошибка генерации изображения: {e}")
            return ""

    def display_graph_info(self, graph: Dict[str, Any]) -> None:
        total_nodes = len(graph)
        total_edges = sum(len(dependencies) for dependencies in graph.values())

        print(f"\nСтатистика графа:")
        print(f"   Всего узлов (пакетов): {total_nodes}")
        print(f"   Всего рёбер (зависимостей): {total_edges}")
        print(f"   Максимальная глубина: {self.config['max_depth']}")

        if self.config['filter_substring']:
            print(f"   Фильтр: '{self.config['filter_substring']}'")

class Stage5CLI:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.visualizer = GraphVisualizer(config)

    def run_stage5(self) -> None:
        print("\nЭТАП 5: Визуализация графа зависимостей")

        package_name = self.config['package_name']
        version = self.config['package_version']

        print(f"Построение графа для {package_name}@{version}...")
        self.visualizer.graph_builder.dfs_build_graph(package_name, version)
        graph = self.visualizer.graph_builder.graph

        if not graph:
            print("Граф пуст")
            return

        start_node = f"{package_name}@{version}"

        self.visualizer.display_graph_info(graph)

        print("\n1. Текстовое представление графа на языке Graphviz DOT:")

        dot_content = self.visualizer.generate_graphviz_dot(graph)
        print(dot_content)

        dot_filename = self.visualizer.save_dot_file(dot_content)
        print(f"DOT-файл сохранен как: {dot_filename}")

        print("\n2. Генерация изображения графа:")

        image_filename = self.visualizer.generate_image(dot_filename)
        if image_filename:
            print(f"Изображение графа сохранено как: {image_filename}")
            print("Для просмотра откройте файл в браузере или графическом просмотрщике.")
        else:
            print("Для генерации изображений установите Graphviz")

        print("\n3. ASCII-дерево зависимостей:")
        if start_node in graph:
            self.visualizer.display_ascii_tree(graph, start_node)
        else:
            print(f"Начальный узел {start_node} не найден в графе")

        print("\n4. Демонстрация для трех различных пакетов:")

        self._demonstrate_multiple_packages()

    def _demonstrate_multiple_packages(self) -> None:
        if self.config['test_mode']:
            demo_packages = [
                {"name": "A", "version": "1.0.0", "desc": "Базовый пакет с двумя зависимостями"},
                {"name": "B", "version": "1.0.0", "desc": "Пакет с одной зависимостью"},
                {"name": "C", "version": "1.0.0", "desc": "Пакет с двумя зависимостями"}
            ]
        else:
            demo_packages = [
                {"name": "Newtonsoft.Json", "version": "13.0.1", "desc": "Популярная JSON библиотека"},
                {"name": "NLog", "version": "5.0.0", "desc": "Библиотека логирования"},
                {"name": "AutoMapper", "version": "12.0.0", "desc": "Библиотека маппинга объектов"}
            ]

        for i, pkg in enumerate(demo_packages, 1):
            print(f"--- Пакет {i}: {pkg['name']} {pkg['version']} ---")
            print(f"Описание: {pkg['desc']}")
            print("-" * 50)

            temp_config = {**self.config, 'package_name': pkg['name'], 'package_version': pkg['version']}
            temp_visualizer = GraphVisualizer(temp_config)
            temp_visualizer.graph_builder.dfs_build_graph(pkg['name'], pkg['version'])
            temp_graph = temp_visualizer.graph_builder.graph

            if temp_graph:
                start_node = f"{pkg['name']}@{pkg['version']}"
                print(f"Узлы: {len(temp_graph)}, Зависимости: {sum(len(deps) for deps in temp_graph.values())}")

                if start_node in temp_graph:
                    deps = temp_graph[start_node]
                    if deps:
                        print(f"Прямые зависимости: {', '.join(deps)}")
                    else:
                        print("Прямые зависимости: нет")
            else:
                print("Граф пуст")
            print("Демонстрация завершена\n")

def main_stage5():
    from stage1 import main_stage1

    config = main_stage1()

    cli = Stage5CLI(config)
    cli.run_stage5()

if __name__ == "__main__":
    main_stage5()