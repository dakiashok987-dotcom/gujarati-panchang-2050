#!/usr/bin/env python3
"""Merges tools/generated.json (calculated lunar dates) into www/festivals.json.
Existing 'fixed' entries are kept untouched. 'lunar' is replaced by generated entries (v=false = unverified).
Existing lunar entries that are NOT generated (e.g. hand-verified ones, ids not starting with a generated slug) are preserved."""
import json, os, re, datetime as dt, sys
here = os.path.dirname(os.path.abspath(__file__))
tgt = os.path.join(here, '..', 'www', 'festivals.json')
cur = json.load(open(tgt)); gen = json.load(open(os.path.join(here, 'generated.json')))
TN = ['', 'એકમ', 'બીજ', 'ત્રીજ', 'ચોથ', 'પાંચમ', 'છઠ', 'સાતમ', 'આઠમ', 'નોમ', 'દશમ', 'અગિયારસ', 'બારસ', 'તેરસ', 'ચૌદશ', 'પૂનમ']
keep = [r for r in cur.get('lunar', []) if 'id' not in r]          # user's own / hand-verified entries
out = []
for r in gen['lunar']:
    if r['id'].startswith('gen-'): continue                          # skip generic ekadashi/purnima/amas list (keeps app uncluttered)
    parts = r['tithi'].split()
    tit = ''
    if parts:
        last = parts[-1]
        tit = last if last in ('પૂનમ', 'અમાસ') else TN[int(last)]
    o = dict(d=r['d'], n=r['n'], v=False, tithi=tit, paksha=(r['paksha'] + ' પક્ષ (' + parts[0] + ')') if parts else '', nak='',
             id=r['id'], category=r['category'], cats=r['cats'], tradition=r['tradition'], major=r['major'], source=r['source'])
    if 'series' in r: o['series'] = r['series']
    out.append(o)
seen = {(r['d'], r['n']) for r in keep}
lunar = keep + [r for r in out if (r['d'], r['n']) not in seen]
lunar.sort(key=lambda r: (r['d'], not r.get('major', False), r['n']))
for r in lunar:
    dt.date.fromisoformat(r['d']); assert r['n'] and isinstance(r['v'], bool)
res = dict(version=max(2, cur.get('version', 1)), fixed=cur['fixed'], lunar=lunar)
with open(tgt, 'w', encoding='utf-8') as f:
    f.write('{"version":%d,\n"fixed":[\n%s],\n"lunar":[\n%s]}\n' % (res['version'],
        ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in res['fixed']) + '\n',
        ',\n'.join(json.dumps(x, ensure_ascii=False, separators=(',', ':')) for x in lunar) + '\n'))
print('fixed', len(res['fixed']), 'lunar', len(lunar), 'kept', len(keep))
