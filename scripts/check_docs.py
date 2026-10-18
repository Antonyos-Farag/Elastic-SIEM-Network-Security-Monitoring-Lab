#!/usr/bin/env python3
"""Check repository-local Markdown targets and SVG XML with the standard library.

External URLs and Markdown heading anchors are intentionally not checked.
"""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)')
HTML_SRC = re.compile(r'(?:src|href)="([^"]+)"')


def main():
    errors = []
    count = 0
    for document in sorted(ROOT.rglob('*.md')):
        if any(part.startswith('.') for part in document.relative_to(ROOT).parts[:-1]):
            continue
        text = document.read_text(encoding='utf-8')
        for target in LINK.findall(text) + HTML_SRC.findall(text):
            if target.startswith(('#', 'https://', 'http://', 'mailto:')):
                continue
            target = unquote(target.split('#', 1)[0].split('?', 1)[0])
            if target and not (document.parent / target).exists():
                errors.append(f'{document.relative_to(ROOT)}: missing target {target}')
            count += 1
    svgs = list((ROOT / 'assets').glob('*.svg'))
    for svg in svgs:
        try:
            tree = ET.parse(svg)
            if tree.getroot().tag != '{http://www.w3.org/2000/svg}svg':
                errors.append(f'{svg.relative_to(ROOT)}: not an SVG root')
        except ET.ParseError as exc:
            errors.append(f'{svg.relative_to(ROOT)}: {exc}')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {count} local link references and {len(svgs)} SVG file(s).')
    print('External links, heading anchors, Mermaid rendering, and lab behavior were not tested.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
