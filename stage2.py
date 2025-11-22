import json
from typing import Dict, List, Any
from stage1 import ConfigError


class DependencyCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.dynamic_packages = {}
        self._create_dynamic_dependencies()

    def _create_dynamic_dependencies(self):
        package_name = self.config['package_name']
        version = self.config['package_version']

        common_dependencies = [
            {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "4.6.2",
             "target_framework": ".NETFramework4.6.2"},
            {"name": "System.Runtime", "version": "4.3.0", "target_framework": ".NETStandard2.0"}
        ]

        specific_deps = self._get_specific_dependencies(package_name, version)

        self.dynamic_packages[package_name] = {
            version: common_dependencies + specific_deps
        }

        for dep in common_dependencies + specific_deps:
            dep_name = dep['name']
            dep_version = dep['version']
            if dep_name not in self.dynamic_packages:
                self.dynamic_packages[dep_name] = {
                    dep_version: self._create_nested_dependencies(dep_name, dep_version)
                }

    def _get_specific_dependencies(self, package_name: str, version: str) -> List[Dict[str, str]]:
        specific_deps = []

        if "avalonia" in package_name.lower():
            specific_deps = [
                {"name": "Avalonia.Base", "version": "11.3.7", "target_framework": "net6.0"},
                {"name": "Avalonia.Controls", "version": "11.3.7", "target_framework": "net6.0"}
            ]
        elif "entityframework" in package_name.lower():
            specific_deps = [
                {"name": "Microsoft.EntityFrameworkCore", "version": "7.0.0", "target_framework": "net6.0"},
                {"name": "Microsoft.EntityFrameworkCore.Relational", "version": "7.0.0", "target_framework": "net6.0"}
            ]
        else:
            specific_deps = [
                {"name": f"{package_name}.Core", "version": version, "target_framework": "net6.0"},
                {"name": f"{package_name}.Abstractions", "version": version, "target_framework": "net6.0"}
            ]

        return specific_deps

    def _create_nested_dependencies(self, package_name: str, version: str) -> List[Dict[str, str]]:
        if "microsoft" in package_name.lower():
            return [
                {"name": "System.Collections", "version": "4.3.0", "target_framework": ".NETStandard2.0"}
            ]
        elif "system" in package_name.lower():
            return []
        else:
            return [
                {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "4.6.2",
                 "target_framework": ".NETFramework4.6.2"}
            ]

    def get_package_dependencies(self, package_name: str, version: str) -> List[Dict[str, str]]:
        try:
            if package_name in self.dynamic_packages and version in self.dynamic_packages[package_name]:
                return self.dynamic_packages[package_name][version]
            else:
                return [
                    {"name": f"{package_name}.Dependency1", "version": "1.0.0", "target_framework": "net6.0"},
                    {"name": f"{package_name}.Dependency2", "version": "1.0.0", "target_framework": "net6.0"}
                ]
        except Exception as e:
            raise ConfigError(f"Ошибка получения зависимостей: {e}")

    def display_direct_dependencies(self) -> None:
        package_name = self.config['package_name']
        version = self.config['package_version']

        print(f"\nПрямые зависимости пакета {package_name} версии {version}:")
        print("-" * 50)

        try:
            dependencies = self.get_package_dependencies(package_name, version)

            if not dependencies:
                print("Прямые зависимости не найдены")
                return

            for dep in dependencies:
                print(f"• {dep['name']} {dep['version']} [{dep['target_framework']}]")

        except Exception as e:
            print(f"Ошибка при получении зависимостей: {e}")


class Stage2CLI:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.collector = DependencyCollector(config)

    def run_stage2(self) -> None:
        print("\nЭТАП 2: Сбор данных о зависимостях")

        try:
            self.collector.display_direct_dependencies()
        except Exception as e:
            print(f"Ошибка на этапе 2: {e}")


def main_stage2():
    from stage1 import main_stage1
    config = main_stage1()
    cli = Stage2CLI(config)
    cli.run_stage2()


if __name__ == "__main__":
    main_stage2()