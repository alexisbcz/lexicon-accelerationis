import re, glob, unicodedata, sys
def key(hw):
    s=unicodedata.normalize('NFD',hw.lower())
    return ''.join(c for c in s if c.isalpha() and c.isascii())
entries={}
for f in sorted(glob.glob('src/*.tex')):
    txt=open(f).read()
    txt='\n'.join(l for l in txt.split('\n') if not l.lstrip().startswith('%'))
    for chunk in re.split(r'\n(?=\\E[*{])', '\n'+txt):
        chunk=chunk.strip()
        if not chunk.startswith('\\E'): continue
        m=re.match(r'\\E\*?\{([^}]*)\}',chunk)
        entries[key(m.group(1))]=(m.group(1),chunk)
keys=sorted(entries)
out=[]; cur=None
for k in keys:
    L=k[0].upper()
    if L!=cur:
        if cur: out.append('\\end{multicols}')
        out.append(f'\\LetterHead{{{L}}}\n\\begin{{multicols}}{{2}}')
        cur=L
    out.append(entries[k][1])
out.append('\\end{multicols}')
open('body.tex','w').write(('\n\n'.join(out)+'\n').replace('---','—').replace('--','–'))
# cross-ref check
allt='\n'.join(e[1] for e in entries.values())
missing=sorted({x for x in re.findall(r'\\xr\{([^}]*)\}',allt) if key(x) not in entries})
attested=sum(1 for e in entries.values() if e[1].startswith('\\E*'))
print(f'{len(entries)} entries, {attested} attested ({100*attested/len(entries):.1f}%)')
print('missing xrefs:',missing)
# roots index
roots={}
for hw,ch in entries.values():
    m=re.match(r'\\E\*?\{[^}]*\}\{[^}]*\}\{[^}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}',ch)
    if not m: continue
    ety=m.group(1)
    for gm in re.finditer(r'([\u0370-\u03ff\u1f00-\u1fff][\u0370-\u03ff\u1f00-\u1fff\s,()-]*?[\u0370-\u03ff\u1f00-\u1fff])\s+((?:[a-z][a-z ,\-]*?))(?=\s*[+;\]\(]|$|,\s*(?:f\.|after|Fr\.|L\.))',ety):
        g,gl=gm.group(1).strip(),gm.group(2).strip(' ,')
        if not gl or gl in('priv',): continue
        roots.setdefault(('Gk',g),[gl,set()])[1].add(hw)
    for lm in re.finditer(r'\\la\{([^}]*)\}\s+([a-z][a-z ,\-]*?)(?=\s*[+;\]\(]|$|,\s*(?:f\.|after|Fr\.))',ety):
        g,gl=lm.group(1),lm.group(2).strip(' ,')
        if 'Fr.' in ety[max(0,lm.start()-6):lm.start()]: continue
        roots.setdefault(('L',g),[gl,set()])[1].add(hw)
def rk(item):
    (lang,w),_=item
    s=unicodedata.normalize('NFD',w.lower())
    return (0 if lang=='Gk' else 1, ''.join(c for c in s if unicodedata.category(c)!='Mn'))
lines=['{\\color{rubric}\\scshape Greek}\\par\\smallskip']
lastlang='Gk'
for (lang,w),(gl,hws) in sorted(roots.items(),key=rk):
    if lang!=lastlang:
        lines.append('\\medskip{\\color{rubric}\\scshape Latin}\\par\\smallskip'); lastlang=lang
    ww=w if lang=='Gk' else f'\\textit{{{w}}}'
    lines.append(f'\\hangindent=1em\\hangafter=1 \\textbf{{{ww}}} {gl}: '+', '.join(sorted(hws,key=key))+'.\\par')
open('roots.tex','w').write(('\n'.join(lines)+'\n').replace('---','—').replace('--','–'))
print(len(roots),'roots')
