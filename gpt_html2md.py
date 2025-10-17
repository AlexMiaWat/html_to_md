import argparse
import requests
from html.parser import HTMLParser
import re

class HTML2MD(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.ignore_content = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ('script','style'):
            self.ignore_content = True

    def handle_endtag(self, tag):
        if tag.lower() in ('script','style'):
            self.ignore_content = False

    def handle_data(self, data):
        if not self.ignore_content and data.strip():
            self.out.append(data.strip())

    def to_markdown(self):
        text = '\n\n'.join(self.out)
        return re.sub(r'\n{3,}', '\n\n', text) + '\n'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch website and convert HTML to Markdown')
    parser.add_argument('-u','--url', required=True, help='Website URL')
    parser.add_argument('outfile', nargs='?', default='output.md', help='Output Markdown file')
    args = parser.parse_args()

    response = requests.get(args.url, headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()
    html_content = response.text

    parser_md = HTML2MD()
    parser_md.feed(html_content)
    markdown_text = parser_md.to_markdown()

    with open(args.outfile,'w',encoding='utf-8') as f:
        f.write(markdown_text)

    print(f'Markdown saved to {args.outfile}')
