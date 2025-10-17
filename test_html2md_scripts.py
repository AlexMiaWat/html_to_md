#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматизированный тестер для скриптов html2md.py и grok_html2md.py

Тестирует скрипты на реальных сайтах и локальных файлах,
сравнивает результаты и генерирует отчеты.
"""

import subprocess
import sys
import os
import time
from pathlib import Path
import requests
from urllib.parse import urlparse

class HTML2MDTester:
    def __init__(self):
        self.test_dir = Path("test_results")
        self.test_dir.mkdir(exist_ok=True)

        # Список реальных сайтов для тестирования
        self.test_sites = [
            "https://example.com",
            "https://www.rambler.ru/",
            "https://mail.ru/",
            "https://lenta.ru/",
            "https://habr.com/ru/articles/547448",
            "https://ru.wikipedia.org/wiki/HTML",
            "https://developer.mozilla.org/ru/docs/Web/HTML",
            "https://github.com/explore",
            "https://stackoverflow.com/questions",
            "https://www.microsoft.com/",
            "https://www.apple.com/",
            "https://www.google.com/about/",
        ]

        # Локальные файлы для тестирования
        self.local_files = [
            "index.html",
            "test_file.html",
            "example_com_raw.html",
        ]

    def run_command(self, cmd, output_file=None):
        """Запуск команды с захватом вывода"""
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=60
            )

            if output_file:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.stdout)

            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)

    def test_single_site(self, site_url, script_name):
        """Тестирование одного сайта одним скриптом"""
        print(f"  Тестирую {script_name} на {site_url}")

        # Создаем имя файла для результатов
        site_name = urlparse(site_url).netloc.replace(".", "_")
        output_file = self.test_dir / f"{script_name}_{site_name}.md"

        # Определяем команду для запуска
        if script_name == "grok":
            cmd = f'python grok_html2md.py -u "{site_url}"'
        else:
            cmd = f'python html2md.py -u "{site_url}"'

        # Запускаем тест
        success, stdout, stderr = self.run_command(cmd, str(output_file))

        # Подсчитываем статистику
        lines_count = len(stdout.split('\n')) if stdout else 0
        has_tables = '|' in stdout if stdout else False
        has_headers = stdout.count('\n#') if stdout else 0
        has_lists = stdout.count('\n-') if stdout else 0

        # Убираем debug информацию из ошибки, если тест успешен
        error_msg = ""
        if not success:
            # Оставляем только реальные ошибки, убираем debug вывод
            error_lines = [line for line in stderr.split('\n') if line.strip() and not line.strip().startswith('[DEBUG]')]
            error_msg = '\n'.join(error_lines[:3])  # Берем только первые 3 строки ошибок

        return {
            'success': success,
            'lines': lines_count,
            'tables': has_tables,
            'headers': has_headers,
            'lists': has_lists,
            'output_file': output_file,
            'error': error_msg
        }

    def test_local_file(self, filename, script_name):
        """Тестирование локального файла"""
        print(f"  Тестирую {script_name} на файле {filename}")

        if not os.path.exists(filename):
            return {
                'success': False,
                'lines': 0,
                'error': f"Файл {filename} не найден"
            }

        output_file = self.test_dir / f"{script_name}_{Path(filename).stem}.md"

        if script_name == "grok":
            cmd = f'python grok_html2md.py "{filename}"'
        else:
            cmd = f'python html2md.py "{filename}"'

        success, stdout, stderr = self.run_command(cmd, str(output_file))

        lines_count = len(stdout.split('\n')) if stdout else 0
        has_tables = '|' in stdout if stdout else False
        has_headers = stdout.count('\n#') if stdout else 0
        has_lists = stdout.count('\n-') if stdout else 0

        return {
            'success': success,
            'lines': lines_count,
            'tables': has_tables,
            'headers': has_headers,
            'lists': has_lists,
            'output_file': output_file,
            'error': stderr[:200] if stderr else ""
        }

    def generate_report(self, results):
        """Генерация отчета о тестировании"""
        report_file = self.test_dir / "test_report.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Отчет о тестировании HTML2MD скриптов\n\n")
            f.write(f"**Дата тестирования:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # Сводная таблица для сайтов
            f.write("## Результаты тестирования сайтов\n\n")
            f.write("| Сайт | Grok строки | Html2md строки | Разница | Grok таблицы | Html2md таблицы | Grok списки | Html2md списки | Статус |\n")
            f.write("|------|-------------|----------------|---------|---------------|------------------|-------------|----------------|--------|\n")

            for site in self.test_sites:
                site_name = urlparse(site).netloc

                # Результаты grok скрипта
                grok_result = results.get(f"grok_{site_name}", {})
                grok_lines = grok_result.get('lines', 0)
                grok_tables = '+' if grok_result.get('tables') else '-'
                grok_lists = grok_result.get('lists', 0)
                grok_success = '+' if grok_result.get('success') else '-'

                # Результаты html2md скрипта
                html2md_result = results.get(f"html2md_{site_name}", {})
                html2md_lines = html2md_result.get('lines', 0)
                html2md_tables = '+' if html2md_result.get('tables') else '-'
                html2md_lists = html2md_result.get('lists', 0)
                html2md_success = '+' if html2md_result.get('success') else '-'

                # Разница в строках
                if grok_lines > 0 and html2md_lines > 0:
                    diff = html2md_lines - grok_lines
                    diff_str = f"+{diff}" if diff > 0 else str(diff)
                else:
                    diff_str = "N/A"

                # Статус
                if grok_success == '+' and html2md_success == '+':
                    status = "✅ Оба успешны"
                elif grok_success == '+' and html2md_success == '-':
                    status = "⚠️ Только Grok"
                elif grok_success == '-' and html2md_success == '+':
                    status = "⚠️ Только Html2md"
                else:
                    status = "❌ Оба неудачны"

                f.write(f"| {site_name} | {grok_lines} | {html2md_lines} | {diff_str} | {grok_tables} | {html2md_tables} | {grok_lists} | {html2md_lists} | {status} |\n")

            # Сводная таблица для локальных файлов
            f.write("\n## Результаты тестирования локальных файлов\n\n")
            f.write("| Файл | Grok строки | Html2md строки | Разница | Grok таблицы | Html2md таблицы | Grok списки | Html2md списки | Статус |\n")
            f.write("|------|-------------|----------------|---------|---------------|------------------|-------------|----------------|--------|\n")

            for filename in self.local_files:
                if not os.path.exists(filename):
                    continue

                file_stem = Path(filename).stem

                # Результаты grok скрипта
                grok_result = results.get(f"grok_{file_stem}", {})
                grok_lines = grok_result.get('lines', 0)
                grok_tables = '+' if grok_result.get('tables') else '-'
                grok_lists = grok_result.get('lists', 0)
                grok_success = '+' if grok_result.get('success') else '-'

                # Результаты html2md скрипта
                html2md_result = results.get(f"html2md_{file_stem}", {})
                html2md_lines = html2md_result.get('lines', 0)
                html2md_tables = '+' if html2md_result.get('tables') else '-'
                html2md_lists = html2md_result.get('lists', 0)
                html2md_success = '+' if html2md_result.get('success') else '-'

                # Разница в строках
                if grok_lines > 0 and html2md_lines > 0:
                    diff = html2md_lines - grok_lines
                    diff_str = f"+{diff}" if diff > 0 else str(diff)
                else:
                    diff_str = "N/A"

                # Статус
                if grok_success == '+' and html2md_success == '+':
                    status = "✅ Оба успешны"
                elif grok_success == '+' and html2md_success == '-':
                    status = "⚠️ Только Grok"
                elif grok_success == '-' and html2md_success == '+':
                    status = "⚠️ Только Html2md"
                else:
                    status = "❌ Оба неудачны"

                f.write(f"| {filename} | {grok_lines} | {html2md_lines} | {diff_str} | {grok_tables} | {html2md_tables} | {grok_lists} | {html2md_lists} | {status} |\n")

            # Детальная статистика
            f.write("\n## Детальная статистика\n\n")

            grok_success = sum(1 for k, v in results.items() if k.startswith('grok_') and v.get('success'))
            html2md_success = sum(1 for k, v in results.items() if k.startswith('html2md_') and v.get('success'))
            total_tests = len([k for k in results.keys() if 'grok_' in k or 'html2md_' in k]) // 2

            f.write(f"**Общее количество тестов:** {total_tests}\n\n")
            f.write(f"**Grok скрипт:** {grok_success}/{total_tests} успешных ({grok_success/total_tests*100:.1f}%)\n\n")
            f.write(f"**Html2md скрипт:** {html2md_success}/{total_tests} успешных ({html2md_success/total_tests*100:.1f}%)\n\n")

            # Средние показатели
            grok_lines = [v.get('lines', 0) for k, v in results.items() if k.startswith('grok_') and v.get('success')]
            html2md_lines = [v.get('lines', 0) for k, v in results.items() if k.startswith('html2md_') and v.get('success')]

            avg_grok = None
            avg_html2md = None

            if grok_lines:
                avg_grok = sum(grok_lines) // len(grok_lines)
                f.write(f"**Среднее количество строк (Grok):** {avg_grok}\n\n")
            if html2md_lines:
                avg_html2md = sum(html2md_lines) // len(html2md_lines)
                f.write(f"**Среднее количество строк (Html2md):** {avg_html2md}\n\n")

            # Сравнение качества
            if avg_grok is not None and avg_html2md is not None:
                if avg_html2md > avg_grok:
                    f.write(f"**Html2md извлекает больше контента:** +{avg_html2md - avg_grok} строк в среднем\n\n")
                elif avg_grok > avg_html2md:
                    f.write(f"**Grok извлекает больше контента:** +{avg_grok - avg_html2md} строк в среднем\n\n")
                else:
                    f.write("**Оба скрипта извлекают одинаковое количество контента**\n\n")

            # Ошибки (только если они есть)
            errors = [(k, v.get('error', '')) for k, v in results.items() if v.get('error') and v.get('success') == False]
            if errors:
                f.write("## Ошибки\n\n")
                for script_name, error in errors:
                    site_name = script_name.replace('grok_', '').replace('html2md_', '')
                    f.write(f"**{script_name}:** {error}\n\n")

        print(f"Отчет сохранен в: {report_file}")
        return report_file

    def run_all_tests(self):
        """Запуск всех тестов"""
        print("Начинаю тестирование HTML2MD скриптов...\n")

        results = {}

        # Тестирование сайтов
        print("Тестирую сайты в интернете:")
        for site in self.test_sites:
            # Тестируем grok скрипт
            result_key = f"grok_{urlparse(site).netloc}"
            results[result_key] = self.test_single_site(site, "grok")

            # Тестируем html2md скрипт
            result_key = f"html2md_{urlparse(site).netloc}"
            results[result_key] = self.test_single_site(site, "html2md")

        print("\nТестирую локальные файлы:")
        for filename in self.local_files:
            if not os.path.exists(filename):
                    print(f"  Файл {filename} не найден, пропускаю")
                    continue

            # Тестируем grok скрипт
            result_key = f"grok_{Path(filename).stem}"
            results[result_key] = self.test_local_file(filename, "grok")

            # Тестируем html2md скрипт
            result_key = f"html2md_{Path(filename).stem}"
            results[result_key] = self.test_local_file(filename, "html2md")

        # Генерируем отчет
        print("\nГенерирую отчет...")
        report_file = self.generate_report(results)

        print(f"\nТестирование завершено! Результаты в папке: {self.test_dir}")
        print(f"Подробный отчет: {report_file}")

        return results

def main():
    """Главная функция"""
    tester = HTML2MDTester()
    results = tester.run_all_tests()

    # Выводим краткую статистику в консоль
    print("\nКраткая статистика:")

    grok_success = sum(1 for k, v in results.items() if k.startswith('grok_') and v.get('success'))
    html2md_success = sum(1 for k, v in results.items() if k.startswith('html2md_') and v.get('success'))

    total_tests = len([k for k in results.keys() if 'grok_' in k or 'html2md_' in k]) // 2

    print(f"  Grok скрипт: {grok_success}/{total_tests} успешных")
    print(f"  Html2md скрипт: {html2md_success}/{total_tests} успешных")

if __name__ == "__main__":
    main()