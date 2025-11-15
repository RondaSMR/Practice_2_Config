import json
from typing import Dict, List, Any
from stage1 import ConfigError

class DependencyCollector:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_packages = {
            "Newtonsoft.Json": {
                "13.0.1": [
                    {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "[4.6.2]",
                     "target_framework": ".NETFramework4.6.2"},
                    {"name": "System.Runtime.CompilerServices.Unsafe", "version": "[5.0.0]",
                     "target_framework": ".NETStandard2.0"},
                    {"name": "System.Threading.Tasks.Extensions", "version": "[4.5.4]",
                     "target_framework": ".NETStandard2.0"}
                ]
            },
            "NLog": {
                "5.0.0": [
                    {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "[4.6.2]",
                     "target_framework": ".NETFramework4.6.2"},
                    {"name": "System.Text.Json", "version": "[6.0.5]", "target_framework": ".NETStandard2.0"}
                ]
            },
            "AutoMapper": {
                "12.0.0": [
                    {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "[4.6.2]",
                     "target_framework": ".NETFramework4.6.2"},
                    {"name": "System.Linq.Expressions", "version": "[4.3.0]", "target_framework": ".NETStandard2.0"}
                ]
            },
            "Microsoft.NETFramework.ReferenceAssemblies": {
                "4.6.2": []  # Нет зависимостей
            },
            "System.Runtime.CompilerServices.Unsafe": {
                "5.0.0": [
                    {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "[4.6.2]",
                     "target_framework": ".NETFramework4.6.2"}
                ]
            },
            "System.Threading.Tasks.Extensions": {
                "4.5.4": [
                    {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "[4.6.2]",
                     "target_framework": ".NETFramework4.6.2"}
                ]
            },
            "System.Text.Json": {
                "6.0.5": [
                    {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "[4.6.2]",
                     "target_framework": ".NETFramework4.6.2"}
                ]
            },
            "System.Linq.Expressions": {
                "4.3.0": [
                    {"name": "Microsoft.NETFramework.ReferenceAssemblies", "version": "[4.6.2]",
                     "target_framework": ".NETFramework4.6.2"}
                ]
            }
        }

    def get_package_dependencies(self, package_name: str, version: str) -> List[Dict[str, str]]:
        try:
            if package_name in self.test_packages and version in self.test_packages[package_name]:
                return self.test_packages[package_name][version]
            else:
                return []

        except Exception as e:
            raise ConfigError(f"Ошибка получения зависимостей пакета {package_name} {version}: {e}")

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