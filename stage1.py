import json
import os
import argparse
import sys
from typing import Dict, Any

class ConfigError(Exception): pass

class ValidationError(Exception): pass

class Stage1Config:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.default_config = {
            "package_name": "Newtonsoft.Json",
            "repository_url": "https://api.nuget.org/v3/index.json",
            "test_mode": False,
            "test_repository_path": "",
            "package_version": "13.0.1",
            "ascii_tree": False,
            "max_depth": 3,
            "filter_substring": ""
        }
        self.config = self.default_config.copy()

    def load_config(self) -> Dict[str, Any]:
        try:
            if not os.path.exists(self.config_path):
                self._create_default_config()
                return self.config

            with open(self.config_path, 'r', encoding='utf-8') as f:
                file_config = json.load(f)

            for key, value in file_config.items():
                if key in self.config:
                    self.config[key] = value

            self._validate_config()
            return self.config

        except json.JSONDecodeError as e:
            raise ConfigError(f"Ошибка парсинга JSON: {e}")
        except Exception as e:
            raise ConfigError(f"Ошибка загрузки конфигурации: {e}")

    def _create_default_config(self) -> None:
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, indent=2, ensure_ascii=False)
            print(f"Создан файл конфигурации по умолчанию: {self.config_path}")
        except Exception as e:
            raise ConfigError(f"Ошибка создания конфигурационного файла: {e}")

    def _validate_config(self) -> None:
        errors = []

        if not self.config["package_name"]:
            errors.append("Имя пакета не может быть пустым")

        if self.config["test_mode"]:
            if not self.config["test_repository_path"]:
                errors.append("В тестовом режиме должен быть указан путь к тестовому репозиторию")
        else:
            if not self.config["repository_url"]:
                errors.append("URL репозитория не может быть пустым")

        if not self.config["package_version"]:
            errors.append("Версия пакета не может быть пустой")

        try:
            max_depth = int(self.config["max_depth"])
            if max_depth < 1:
                errors.append("Максимальная глубина должна быть положительным числом")
        except (ValueError, TypeError):
            errors.append("Максимальная глубина должна быть целым числом")

        if errors:
            raise ValidationError("; ".join(errors))

    def display_config(self) -> None:
        print("Текущая конфигурация:")
        print("-" * 40)
        for key, value in self.config.items():
            print(f"{key}: {value}")
        print("-" * 40)

class Stage1CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description='Визуализатор графа зависимостей пакетов NuGet - Этап 1'
        )
        self._setup_parser()

    def _setup_parser(self) -> None:
        self.parser.add_argument(
            '--config',
            type=str,
            default='config.json',
            help='Путь к конфигурационному файлу (по умолчанию: config.json)'
        )

        self.parser.add_argument(
            '--package',
            type=str,
            help='Имя анализируемого пакета'
        )

        self.parser.add_argument(
            '--url',
            type=str,
            help='URL репозитория пакетов'
        )

        self.parser.add_argument(
            '--test-mode',
            action='store_true',
            help='Режим работы с тестовым репозиторием'
        )

        self.parser.add_argument(
            '--test-path',
            type=str,
            help='Путь к файлу тестового репозитория'
        )

        self.parser.add_argument(
            '--version',
            type=str,
            help='Версия пакета'
        )

        self.parser.add_argument(
            '--ascii-tree',
            action='store_true',
            help='Вывод зависимостей в формате ASCII-дерева'
        )

        self.parser.add_argument(
            '--max-depth',
            type=int,
            help='Максимальная глубина анализа зависимостей'
        )

        self.parser.add_argument(
            '--filter',
            type=str,
            help='Подстрока для фильтрации пакетов'
        )

    def run_stage1(self) -> Dict[str, Any]:
        try:
            args = self.parser.parse_args()

            config_manager = Stage1Config(args.config)
            config = config_manager.load_config()

            if args.package:
                config['package_name'] = args.package
            if args.url:
                config['repository_url'] = args.url
            if args.test_mode is not None:
                config['test_mode'] = args.test_mode
            if args.test_path:
                config['test_repository_path'] = args.test_path
            if args.version:
                config['package_version'] = args.version
            if args.ascii_tree is not None:
                config['ascii_tree'] = args.ascii_tree
            if args.max_depth:
                config['max_depth'] = args.max_depth
            if args.filter:
                config['filter_substring'] = args.filter

            config_manager._validate_config()
            config_manager.display_config()

            return config

        except (ConfigError, ValidationError) as e:
            print(f"Ошибка конфигурации: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)

def main_stage1():
    cli = Stage1CLI()
    config = cli.run_stage1()
    return config

if __name__ == "__main__":
    main_stage1()