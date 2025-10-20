#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Text Extractor

Извлекает текст из HTML-содержимого рекурсивно, размещая текст каждого тега на отдельной строке с пустыми строками для разделения.
Форматирует таблицы как Markdown. Игнорирует указанные теги и поддерживает кодировку UTF-8.

Функции:
- Поддержка HTML из файлов, URL или строк
- Рекурсивный обход элементов HTML
- Игнорирование тегов script, style, meta, link, noscript
- Каждый тег на отдельной строке с пустыми строками
- Таблицы форматируются как Markdown
- Обработка списков, цитат, кода и горизонтальных линий
- Вывод простого текста с правильной кодировкой UTF-8

Использование:
  python html_text_extract.py input.html
  python html_text_extract.py -u https://example.com
  python html_text_extract.py -s "<h1>Test</h1><p>Text</p>"
"""

import sys
import argparse
import requests
from html.parser import HTMLParser
from html_to_md.HTMLTreeBuilder import Element, HTMLTreeBuilder, extract_text, extract_table_text

import io
import sys

# Убедиться в кодировке UTF-8 для stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def read_input(path=None, url=None, string=None):
    """Читает HTML-ввод из файла, URL или строки."""
    
    # Обработка строкового ввода: сначала пытаемся прочитать как файл, иначе считаем HTML
    if string:
        try:
            with open(string, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return string  # Считаем строкой HTML
    
    # Обработка URL-ввода
    if url:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'  # Принудительно устанавливаем UTF-8
        return response.text
        
    # Обработка stdin или файла
    if not path or path == "-":
        return sys.stdin.read()
        
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def html_to_text(html):
    """Преобразует строку HTML в отформатированный текст с таблицами Markdown."""
    
    # Парсим HTML и строим дерево
    parser = HTMLTreeBuilder()
    parser.feed(html)
    tree = parser.get_tree()
    
    # Извлекаем текст из дерева
    text = extract_text(tree)
    
    # Очищаем: удаляем пустые строки и обеспечиваем завершающий перевод строки
    return "\n".join(line for line in text.split("\n") if line.strip()) + "\n" if text else ""

def main():
    """Основная функция для парсинга аргументов и выполнения конвертации."""
    
    ap = argparse.ArgumentParser(description="Извлечение текста из HTML с новыми строками и таблицами Markdown")
    ap.add_argument("input", nargs="?", help="HTML-файл или '-' для stdin")
    ap.add_argument("-o", "--output", required=False, help="Файл вывода (по умолчанию: stdout)")
    ap.add_argument("-u", "--url", help="URL для получения")
    ap.add_argument("-s", "--string", help="HTML-строка или путь к файлу")
    
    args = ap.parse_args()
    
    try:
        # Читаем ввод из указанного источника
        html = read_input(args.input, args.url, args.string)
        
        # Преобразуем HTML в отформатированный текст
        text = html_to_text(html)
        
        # Выводим результат
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            print(text)
        
    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()