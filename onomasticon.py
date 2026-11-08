"""Convert NAMES.md (or fr/NOMS.md) into a typeset LaTeX appendix."""
import re, sys
src, dst = sys.argv[1], sys.argv[2]

def inline(t):
    t = t.replace('\\', '\\textbackslash{}')
    for a, b in [('&', '\\&'), ('%', '\\%'), ('#', '\\#'), ('_', '\\_'), ('$', '\\$')]:
        t = t.replace(a, b)
    t = re.sub(r'`([^`]*)`', r'\\texttt{\1}', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'\\textit{\1}', t)
    t = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', t)
    t = re.sub(r'([\u3040-\u30ff\u4e00-\u9fff]+)', r'{\\cjk \1}', t)
    t = t.replace('⚠', '{\\cjk\\color{rubric}⚠}')
    t = re.sub(r'"([^"]*)"', '“\\1”', t)
    t = t.replace('---', '—').replace('--', '–')
    return t

out = []
lines = open(src, encoding='utf-8').read().split('\n')
i = 0
while i < len(lines):
    l = lines[i].rstrip()
    if l.startswith('# ') or l.strip() == '---' or not l.strip():
        i += 1; continue
    if l.startswith('> '):
        out.append('\\OnoNote{' + inline(l[2:].strip()) + '}')
    elif l.startswith('## '):
        out.append('\\OnoHead{' + inline(l[3:].strip()) + '}')
    elif l.startswith('|'):
        rows = []
        while i < len(lines) and lines[i].startswith('|'):
            cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not set(''.join(cells)) <= set('-: '):
                rows.append(cells)
            i += 1
        for r in rows[1:]:
            fig, why, *forms = r
            out.append('\\OnoItem{\\textbf{' + inline(fig) + '}, \\textit{' + inline(why) + '}. '
                       + ' · '.join('\\textsc{' + inline(f) + '}' for f in forms) + '.}')
        continue
    elif re.match(r'^\*\*[^*]+\*\*:?$', l.strip()):
        out.append('\\OnoSub{' + inline(l.strip().strip('*').rstrip(':').strip('*')) + '}')
    elif l.lstrip().startswith('- '):
        out.append('\\OnoItem{' + inline(l.lstrip()[2:]) + '}')
    else:
        out.append('\\OnoPara{' + inline(l.strip()) + '}')
    i += 1
open(dst, 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(dst, len(out), 'lines')
