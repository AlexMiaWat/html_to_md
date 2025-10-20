import sys
from html.parser import HTMLParser
"""
Модуль для построения дерева HTML-элементов и извлечения текста.
Содержит классы Element и HTMLTreeBuilder, а также функции extract_text и extract_table_text.
"""

class Element:
    """Представляет HTML-элемент с тегом, атрибутами, дочерними элементами и ссылкой на родителя."""
    
    def __init__(self, tag, attrs=None, parent=None):
        self.tag = tag  # Имя тега HTML (например, 'div', 'p', 'table')
        self.attrs = attrs or {}  # Словарь атрибутов элемента
        self.children = []  # Список дочерних элементов и текстовых узлов
        self.parent = parent  # Ссылка на родительский элемент

    def add_child(self, child):
        """Добавить дочерний элемент или текстовый узел к этому элементу."""
        self.children.append(child)

    def __repr__(self):
        """Строковое представление для отладки."""
        return f"Element({self.tag})"


class HTMLTreeBuilder(HTMLParser):
    """Пользовательский парсер HTML, который строит дерево структуры HTML-элементов."""
    
    # Пустые теги (самозакрывающиеся), которые не имеют закрывающих тегов
    void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", 
                 "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.root = Element("root")  # Корневой элемент дерева
        self.current = self.root  # Текущий обрабатываемый элемент
        self.tag_stack = []  # Стек для отслеживания открытых тегов для правильной вложенности

    def handle_starttag(self, tag, attrs):
        """Обрабатывает открывающие HTML-теги."""
        element = Element(tag, dict(attrs), self.current)
        self.current.add_child(element)
        
        # Для непустых тегов добавляем в стек и устанавливаем как текущий
        if tag not in self.void_tags:
            self.current = element
            self.tag_stack.append(tag)

    def handle_endtag(self, tag):
        """Обрабатывает закрывающие HTML-теги."""
        # Пустые теги не требуют обработки закрытия
        if tag in self.void_tags:
            return
            
        # Извлекаем из стека до нахождения соответствующего тега или достижения корня
        while self.tag_stack and self.current.tag != tag and self.current.parent:
            self.tag_stack.pop()
            self.current = self.current.parent
            
        # Если найден совпадающий тег, удаляем из стека и переходим к родителю
        if self.tag_stack and self.current.tag == tag and self.current.parent:
            self.tag_stack.pop()
            self.current = self.current.parent

    def handle_data(self, data):
        """Обрабатывает текстовое содержимое между HTML-тегами."""
        # Добавляем только непустой текст
        if data.strip():
            self.current.add_child(data.strip())

    def get_tree(self):
        """Отладочный метод для вывода структуры дерева (для разработки)."""
        print(f"[DEBUG] У корня {len(self.root.children)} дочерних элементов", file=sys.stderr)
        for i, child in enumerate(self.root.children):
            print(f"[DEBUG] Дочерний элемент #{i+1}: {child.tag}", file=sys.stderr)
            for j, subchild in enumerate(child.children):
                print(f"[DEBUG]   Подэлемент #{j+1} тега <{child.tag}>: {subchild}", file=sys.stderr)
                if isinstance(subchild, Element):
                    for k, subsubchild in enumerate(subchild.children):
                        print(f"[DEBUG]     Подподэлемент #{k+1} тега <{subchild.tag}>: {subsubchild}", file=sys.stderr)
        return self.root


def extract_text(element, ignored_tags={"script", "style", "meta", "link", "noscript"}, is_root=False):
    """Рекурсивно извлекает текст из дерева HTML-элементов с правильной форматировкой.
    
    Args:
        element: Текущий элемент (Element или строка)
        ignored_tags: Набор тегов для игнорирования
        is_root: Флаг, указывающий, является ли текущий элемент корнем
    """
    
    # Пропускаем игнорируемые теги полностью
    if isinstance(element, Element) and element.tag in ignored_tags:
        return ""
        
    # Обрабатываем специальные случаи: таблицы и горизонтальные линии
    if isinstance(element, Element) and element.tag == "table":
        return extract_table_text(element, ignored_tags)
    if isinstance(element, Element) and element.tag == "hr":
        return "---\n\n"
        
    # Обрабатываем текстовые узлы (строки)
    if not isinstance(element, Element):
        return element.strip() + "\n\n" if element.strip() else ""
    
    # Обрабатываем дочерние элементы рекурсивно
    text = []
    for i, child in enumerate(element.children):
        if isinstance(child, str):
            # Текстовое содержимое получает свою строку с двойным новым символом
            text.append(child.strip() + "\n\n" if child.strip() else "")
        elif isinstance(child, Element):
            # Рекурсивно обрабатываем вложенные элементы
            child_text = extract_text(child, ignored_tags)
            if child_text:
                # Добавляем перевод строки перед каждым дочерним элементом, кроме первого
                if i > 0:
                    text.append("\n")
                
                # Добавляем дополнительный перевод строки перед списками и заголовками для правильного разделения
                if child.tag in {"h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol"}:
                    text.append("\n")
                
                # Добавляем дополнительный перевод строки перед тегом a для правильного разделения
                if child.tag == "a":
                    text.append("\n")
                
                # Убираем лишние переносы строк в начале и конце текста, чтобы избежать дублирования
                child_text = child_text.strip()
                text.append(child_text)

    # Объединяем весь текст и удаляем пустые элементы
    content = "".join(t for t in text if t).strip()
    
    # Применяем форматирование в зависимости от тега
    if element.tag == "h1":
        content = f"# {content}"
    elif element.tag == "h2":
        content = f"## {content}"
    elif element.tag == "h3":
        content = f"### {content}"
    elif element.tag == "h4":
        content = f"#### {content}"
    elif element.tag == "h5":
        content = f"##### {content}"
    elif element.tag == "h6":
        content = f"###### {content}"
    elif element.tag == "strong":
        content = f"**{content}**"
    elif element.tag == "em":
        content = f"*{content}*"
    elif element.tag == "a":
        href = element.attrs.get("href", "")
        text_content = content or href
        content = f"[{text_content}]({href})"
    elif element.tag == "ul":
        # Преобразуем каждый элемент списка в `-`
        lines = content.split("\n")
        formatted_lines = []
        for line in lines:
            if line.strip():
                formatted_lines.append(f"- {line}")
            else:
                formatted_lines.append(line)
        content = "\n".join(formatted_lines)
    elif element.tag == "ol":
        # Преобразуем каждый элемент списка в нумерованный
        lines = content.split("\n")
        formatted_lines = []
        # Сбрасываем счётчик для каждого нового списка
        list_counter = 1
        for line in lines:
            if line.strip():
                formatted_lines.append(f"{list_counter}. {line}")
                list_counter += 1
            else:
                formatted_lines.append(line)
        content = "\n".join(formatted_lines)

    # Добавляем двойной перевод строки после большинства тегов (кроме root, html, body, head, div)
    if content and element.tag not in {"root", "html", "body", "head", "div"}:
        return content + "\n\n"
    return content
    
    # Объединяем весь текст и удаляем пустые элементы
    content = "".join(t for t in text if t).strip()
    
    # Применяем форматирование в зависимости от тега
    if element.tag == "h1":
        content = f"# {content}"
    elif element.tag == "h2":
        content = f"## {content}"
    elif element.tag == "h3":
        content = f"### {content}"
    elif element.tag == "h4":
        content = f"#### {content}"
    elif element.tag == "h5":
        content = f"##### {content}"
    elif element.tag == "h6":
        content = f"###### {content}"
    elif element.tag == "strong":
        content = f"**{content}**"
    elif element.tag == "em":
        content = f"*{content}*"
    elif element.tag == "a":
        href = element.attrs.get("href", "")
        text_content = content or href
        content = f"[{text_content}]({href})"
    elif element.tag == "ul":
        # Преобразуем каждый элемент списка в `-`
        lines = content.split("\n")
        formatted_lines = []
        for line in lines:
            if line.strip():
                formatted_lines.append(f"- {line}")
            else:
                formatted_lines.append(line)
        content = "\n".join(formatted_lines)
    elif element.tag == "ol":
        # Преобразуем каждый элемент списка в нумерованный
        lines = content.split("\n")
        formatted_lines = []
        # Сбрасываем счётчик для каждого нового списка
        list_counter = 1
        for line in lines:
            if line.strip():
                formatted_lines.append(f"{list_counter}. {line}")
                list_counter += 1
            else:
                formatted_lines.append(line)
        content = "\n".join(formatted_lines)

    # Добавляем двойной перевод строки после большинства тегов (кроме root, html, body, head, div)
    if content and element.tag not in {"root", "html", "body", "head", "div"}:
        return content + "\n\n"
    return content
    
    # Добавляем двойной перевод строки после большинства тегов (кроме root, html, body, head, div)
    if content and element.tag not in {"root", "html", "body", "head", "div"}:
        return content + "\n\n"
    return content


def extract_table_text(table_elem, ignored_tags):
    """Извлекает содержимое таблицы и форматирует как Markdown."""
    
    rows = []
    for child in table_elem.children:
        if isinstance(child, Element) and child.tag == "tr":
            row_text = []
            for cell in child.children:
                if isinstance(cell, Element) and cell.tag in ("th", "td"):
                    # Извлекаем текст из ячейки и экранируем символы вертикальной черты
                    cell_text = extract_text(cell, ignored_tags).strip()
                    if cell_text:
                        cell_text = cell_text.replace("|", "\\|").strip("\n")
                        row_text.append(cell_text)
            if row_text:
                rows.append(row_text)
    
    # Возвращаем пустую строку, если не найдено валидных строк
    if not rows:
        return ""
        
    # Строим таблицу в формате Markdown
    result = ["| " + " | ".join(rows[0]) + " |"]
    result.append("| " + " | ".join("---" for _ in rows[0]) + " |")
    for row in rows[1:]:
        result.append("| " + " | ".join(row) + " |")
        
    return "\n".join(result) + "\n\n"