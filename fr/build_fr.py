import re, glob, unicodedata, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
def key(hw):
    s=unicodedata.normalize('NFD',re.sub(r'\(.*?\)','',hw).lower().replace('œ','oe').replace('æ','ae'))
    return ''.join(c for c in s if c.isalpha() and c.isascii())
entries={}; en2fr={}
for f in sorted(glob.glob('src/*.tex')):
    txt=open(f).read()
    for ch in re.split(r'\n(?=%EN )','\n'+txt):
        ch=ch.strip()
        m=re.match(r'%EN (.*)\n(\\E\*?\{([^}]*)\}.*)',ch,re.S)
        if not m: continue
        en,body,fr=m.group(1).strip(),m.group(2).strip(),m.group(3)
        en2fr[en]=fr
        k=key(fr)
        while k in entries: k+='z'   # homograph safety
        entries[k]=(fr,body)
def fix_xr(t):
    def r(m):
        w=m.group(1)
        return '\\xr{'+en2fr.get(w,w)+'}'
    return re.sub(r'\\xr\{([^}]*)\}',r,t)
ks=sorted(entries); out=[]; cur=None
for k in ks:
    L=k[0].upper()
    if L!=cur:
        if cur: out.append('\\end{multicols}')
        out.append(f'\\LetterHead{{{L}}}\n\\begin{{multicols}}{{2}}'); cur=L
    out.append(fix_xr(entries[k][1]))
out.append('\\end{multicols}')
body=('\n\n'.join(out)+'\n').replace('---','—').replace('--','–')
open('body.tex','w').write(body)
frset={key(v[0]) for v in entries.values()}
miss=sorted({x for x in re.findall(r'\\xr\{([^}]*)\}',body) if key(x) not in frset})
att=sum(1 for e in entries.values() if e[1].startswith('\\E*'))
print(f'{len(entries)} articles, {att} attestés; renvois manquants: {miss}')
# roots
W=r"[a-zà-ÿœ'][a-zà-ÿœ' ,\-]*?"
roots={}
for fr,ch in entries.values():
    m=re.match(r'\\E\*?\{[^}]*\}\{[^}]*\}\{[^}]*\}\{((?:[^{}]|\{[^{}]*\})*)\}',ch)
    if not m: continue
    ety=m.group(1)
    for gm in re.finditer(r'([\u0370-\u03ff\u1f00-\u1fff][\u0370-\u03ff\u1f00-\u1fff\s,()-]*?[\u0370-\u03ff\u1f00-\u1fff])\s+('+W+r')(?=\s*[+;\]\(]|$|,\s*(?:formé|d\'après|fr\.|lat\.))',ety):
        g,gl=gm.group(1).strip(),gm.group(2).strip(' ,')
        if gl and gl!='priv': roots.setdefault(('gr',g),[gl,set()])[1].add(fr)
    for lm in re.finditer(r'\\la\{([^}]*)\}\s+('+W+r')(?=\s*[+;\]\(]|$|,\s*(?:formé|d\'après|fr\.))',ety):
        if 'fr.' in ety[max(0,lm.start()-6):lm.start()]: continue
        roots.setdefault(('lat',lm.group(1)),[lm.group(2).strip(' ,'),set()])[1].add(fr)
def rk(it):
    (l,w),_=it; s=unicodedata.normalize('NFD',w.lower())
    return (l!='gr',''.join(c for c in s if unicodedata.category(c)!='Mn'))
lines=['{\\color{rubric}\\scshape Grec}\\par\\smallskip']; last='gr'
for (l,w),(gl,hws) in sorted(roots.items(),key=rk):
    if l!=last: lines.append('\\medskip{\\color{rubric}\\scshape Latin}\\par\\smallskip'); last=l
    ww=w if l=='gr' else f'\\textit{{{w}}}'
    lines.append(f'\\hangindent=1em\\hangafter=1 \\textbf{{{ww}}} {gl} : '+', '.join(sorted(hws,key=key))+'.\\par')
open('roots.tex','w').write(('\n'.join(lines)+'\n').replace('---','—').replace('--','–'))
print(len(roots),'racines')
