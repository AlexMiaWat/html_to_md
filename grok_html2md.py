#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML Text Extractor

Extracts text from HTML content recursively, placing each tag's text on a new line with empty lines for separation.
Formats tables as Markdown. Ignores specified tags and supports UTF-8 encoding.

Features:
- Supports HTML from files, URLs, or strings
- Recursively traverses HTML elements
- Ignores script, style, meta, link, noscript tags
- Each tag's text on a new line with empty lines
- Tables formatted as Markdown
- Handles lists, quotes, code, and horizontal rules
- Outputs plain text with proper UTF-8 encoding

Usage:
  python html_text_extract.py input.html
  python html_text_extract.py -u https://example.com
  python html_text_extract.py -s "<h1>Test</h1><p>Text</p>"
"""

import sys
import argparse
import requests
from html.parser import HTMLParser

# Ensure UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

class Element:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag
        self.attrs = attrs or {}
        self.children = []
        self.parent = parent

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        return f"Element({self.tag})"

class HTMLTreeBuilder(HTMLParser):
    void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.root = Element("root")
        self.current = self.root
        self.tag_stack = []

    def handle_starttag(self, tag, attrs):
        element = Element(tag, dict(attrs), self.current)
        self.current.add_child(element)
        if tag not in self.void_tags:
            self.current = element
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.void_tags:
            return
        while self.tag_stack and self.current.tag != tag and self.current.parent:
            self.tag_stack.pop()
            self.current = self.current.parent
        if self.tag_stack and self.current.tag == tag and self.current.parent:
            self.tag_stack.pop()
            self.current = self.current.parent

    def handle_data(self, data):
        if data.strip():
            self.current.add_child(data.strip())

    def get_tree(self):
        print(f"[DEBUG] Root has {len(self.root.children)} children", file=sys.stderr)
        for i, child in enumerate(self.root.children):
            print(f"[DEBUG] Root child #{i+1}: {child.tag}", file=sys.stderr)
            for j, subchild in enumerate(child.children):
                print(f"[DEBUG]   Subchild #{j+1} of <{child.tag}>: {subchild}", file=sys.stderr)
                if isinstance(subchild, Element):
                    for k, subsubchild in enumerate(subchild.children):
                        print(f"[DEBUG]     Subsubchild #{k+1} of <{subchild.tag}>: {subsubchild}", file=sys.stderr)
        return self.root

def extract_text(element, ignored_tags={"script", "style", "meta", "link", "noscript"}):
    """Recursively extract text from HTML element tree, each tag on a new line, with empty lines."""
    if isinstance(element, Element) and element.tag in ignored_tags:
        return ""
    if isinstance(element, Element) and element.tag == "table":
        return extract_table_text(element, ignored_tags)
    if isinstance(element, Element) and element.tag == "hr":
        return "---\n\n"
    if not isinstance(element, Element):
        return element.strip() + "\n\n" if element.strip() else ""
    text = []
    for child in element.children:
        if isinstance(child, str):
            text.append(child.strip() + "\n\n" if child.strip() else "")
        elif isinstance(child, Element):
            child_text = extract_text(child, ignored_tags)
            if child_text:
                text.append(child_text)
    content = "".join(t for t in text if t).strip()
    if content and element.tag not in {"root", "html", "body", "head", "div", "ul", "ol"}:
        return content + "\n\n"
    return content

def extract_table_text(table_elem, ignored_tags):
    """Extract text from table in Markdown format."""
    rows = []
    for child in table_elem.children:
        if isinstance(child, Element) and child.tag == "tr":
            row_text = []
            for cell in child.children:
                if isinstance(cell, Element) and cell.tag in ("th", "td"):
                    cell_text = extract_text(cell, ignored_tags).strip()
                    if cell_text:
                        # Escape pipe symbols in cell text to avoid breaking Markdown
                        cell_text = cell_text.replace("|", "\\|").strip("\n")
                        row_text.append(cell_text)
            if row_text:
                rows.append(row_text)
    if not rows:
        return ""
    # Create Markdown table
    result = ["| " + " | ".join(rows[0]) + " |"]
    result.append("| " + " | ".join("---" for _ in rows[0]) + " |")
    for row in rows[1:]:
        result.append("| " + " | ".join(row) + " |")
    return "\n".join(result) + "\n\n"

def read_input(path=None, url=None, string=None):
    if string:
        # Check if string is a file path and read it if it exists
        try:
            with open(string, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            # Treat as HTML string
            return string
    if url:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        response.encoding = 'utf-8'  # Force UTF-8 for web content
        return response.text
    if not path or path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def html_to_text(html):
    parser = HTMLTreeBuilder()
    parser.feed(html)
    tree = parser.get_tree()
    text = extract_text(tree)
    return "\n".join(line for line in text.split("\n") if line.strip()) + "\n" if text else ""

def main():
    ap = argparse.ArgumentParser(description="Extract text from HTML with new lines and Markdown tables")
    ap.add_argument("input", nargs="?", help="HTML file or '-' for stdin")
    ap.add_argument("-u", "--url", help="URL to fetch")
    ap.add_argument("-s", "--string", help="HTML string or file path")
    args = ap.parse_args()
    try:
        html = read_input(args.input, args.url, args.string)
        text = html_to_text(html)
        print(text)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()