#!/usr/bin/env python3
"""Generates festivals.json (2026-2035) by astronomical calculation for Ahmedabad.
Amanta months, Lahiri ayanamsa, udaya-tithi (and pradosh/midnight/midday) rules.
Output dates are CALCULATED, not checked against a printed Panchang -> verified=false.
"""
import math, json, datetime as dt, bisect, sys, os
R = math.pi / 180
LAT, LON = 23.0225, 72.5714  # Ahmedabad
Y0, Y1 = 2026, 2035

TERMS = [(0,0,1,0,6288774),(2,0,-1,0,1274027),(2,0,0,0,658314),(0,0,2,0,213618),(0,1,0,0,-185116),
(0,0,0,2,-114332),(2,0,-2,0,58793),(2,-1,-1,0,57066),(2,0,1,0,53322),(2,-1,0,0,45758),(0,1,-1,0,-40923),
(1,0,0,0,-34720),(0,1,1,0,-30383),(2,0,0,-2,15327),(0,0,1,2,-12528),(0,0,1,-2,10980),(4,0,-1,0,10675),
(0,0,3,0,10034),(4,0,-2,0,8548),(2,1,-1,0,-7888),(2,1,0,0,-6766),(1,0,-1,0,-5163),(1,1,0,0,4987),
(2,-1,1,0,4036),(2,0,2,0,3994),(4,0,0,0,3861),(2,0,-3,0,3665),(0,1,-2,0,-2689),(2,0,-1,2,-2602),
(2,-1,-2,0,2390),(1,0,1,0,-2348),(2,-2,0,0,2236),(0,1,2,0,-2120),(0,2,0,0,-2069),(2,-2,-1,0,2048),
(2,0,1,-2,-1773),(2,0,0,2,-1595),(4,-1,-1,0,1215),(0,0,2,2,-1110),(3,0,-1,0,-892),(2,1,1,0,-810),
(4,-1,-2,0,759),(0,2,-1,0,-713),(2,2,-1,0,-700),(2,1,-2,0,691),(2,-1,0,-2,596),(4,0,1,0,549),
(0,0,4,0,537),(4,-1,0,0,520),(1,0,-2,0,-487)]

def jd(y, m, d, h=0.0):
    if m <= 2: y -= 1; m += 12
    A = y // 100; B = 2 - A + A // 4
    return math.floor(365.25*(y+4716)) + math.floor(30.6001*(m+1)) + d + B - 1524.5 + h/24.0
def T(j): return (j - 2451545.0) / 36525.0
def sun(j):
    t = T(j); L0 = 280.46646 + 36000.76983*t; M = (357.52911 + 35999.05029*t)*R
    C = (1.914602-0.004817*t)*math.sin(M) + 0.019993*math.sin(2*M) + 0.000289*math.sin(3*M)
    om = (125.04 - 1934.136*t)*R
    return (L0 + C - 0.00569 - 0.00478*math.sin(om)) % 360, L0 % 360
def moon(j):
    t = T(j); L = 218.3164477 + 481267.88123421*t
    D = (297.8501921 + 445267.1114034*t)*R; M = (357.5291092 + 35999.0502909*t)*R
    Mp = (134.9633964 + 477198.8675055*t)*R; F = (93.2720950 + 483202.0175233*t)*R
    E = 1 - 0.002516*t - 0.0000074*t*t; s = 0
    for d, m, mp, f, c in TERMS:
        s += c * (E**abs(m)) * math.sin(d*D + m*M + mp*Mp + f*F)
    s += 3958*math.sin((119.75+131.849*t)*R) + 1962*math.sin(L*R - F) + 318*math.sin((53.09+479264.290*t)*R)
    om = (125.04 - 1934.136*t)*R
    return (L + s/1e6 - 0.00478*math.sin(om)) % 360
def ayan(j): return 23.85694 + 1.396971*T(j)
def tithi(j): return int(((moon(j) - sun(j)[0]) % 360) / 12) + 1

def sunevents(date):
    y, m, d = date.year, date.month, date.day
    jn = jd(y, m, d, 12 - LON/15)
    lam, L0 = sun(jn); t = T(jn); eps = (23.4393 - 0.0130042*t)*R; l = lam*R
    dec = math.asin(math.sin(eps)*math.sin(l))
    ra = math.degrees(math.atan2(math.cos(eps)*math.sin(l), math.cos(l))) % 360
    eot = ((L0 - 0.0057183 - ra + 180) % 360) - 180
    noon = 12 - LON/15 - eot*4/60
    cosH = (math.sin(-0.833*R) - math.sin(LAT*R)*math.sin(dec)) / (math.cos(LAT*R)*math.cos(dec))
    H = math.degrees(math.acos(cosH)) / 15
    base = jd(y, m, d, 0)
    return base + (noon-H)/24, base + (noon+H)/24

# ---- new moons & lunar months (Amanta) ----
def g(j): return ((moon(j) - sun(j)[0] + 180) % 360) - 180
nms = []
for k in range(300, 470):
    a = 2451550.09766 + 29.530588861*k; lo, hi = a-3, a+3
    for _ in range(50):
        mid = (lo+hi)/2
        if g(mid) < 0: lo = mid
        else: hi = mid
    nms.append((lo+hi)/2)
sg = [int(((sun(n)[0] - ayan(n)) % 360) / 30) for n in nms]
months = []
for i in range(len(nms)-1):
    months.append(dict(start=nms[i], adhik=(sg[i] == sg[i+1]), n=((sg[i]+1) % 12)+1))
starts = [m['start'] for m in months]

days = []
d0 = dt.date(2025, 10, 1)
while d0 <= dt.date(2036, 3, 31):
    rise, sset = sunevents(d0)
    mi = bisect.bisect_right(starts, rise) - 1
    y, m, d = d0.year, d0.month, d0.day
    days.append(dict(date=d0, mi=mi, sr=tithi(rise), mid=tithi(jd(y, m, d, 18.5)), noon=tithi(jd(y, m, d, 6.5)),
                     pr=tithi(sset + 1/24)))
    d0 += dt.timedelta(days=1)
bymonth = {}
for dd in days: bymonth.setdefault(dd['mi'], []).append(dd)

MN = ['', 'ચૈત્ર', 'વૈશાખ', 'જેઠ', 'અષાઢ', 'શ્રાવણ', 'ભાદરવો', 'આસો', 'કારતક', 'માગશર', 'પોષ', 'મહા', 'ફાગણ']
TN = ['', 'એકમ', 'બીજ', 'ત્રીજ', 'ચોથ', 'પાંચમ', 'છઠ', 'સાતમ', 'આઠમ', 'નોમ', 'દશમ', 'અગિયારસ', 'બારસ', 'તેરસ', 'ચૌદશ', 'પૂનમ']
def tlabel(n, t):
    if t == 30: return f'{MN[n]} વદ અમાસ', 'વદ'
    if t == 15: return f'{MN[n]} સુદ પૂનમ', 'સુદ'
    if t < 15: return f'{MN[n]} સુદ {t}', 'સુદ'
    return f'{MN[n]} વદ {t-15}', 'વદ'
KEY = {'sunrise': 'sr', 'midnight': 'mid', 'midday': 'noon', 'pradosh': 'pr'}
RULE_GU = {'sunrise': 'ઉદય તિથિ', 'midnight': 'મધ્યરાત્રિ (નિશીથ) તિથિ', 'midday': 'મધ્યાહ્ન તિથિ', 'pradosh': 'પ્રદોષ કાળ તિથિ'}
def pick(ds, t, rule):
    k = KEY[rule]
    for dd in ds:
        if dd[k] == t: return dd
    for i, dd in enumerate(ds[:-1]):  # kshaya tithi
        if dd['sr'] == ((t-2) % 30)+1 and ds[i+1]['sr'] == (t % 30)+1: return dd
    if t == 1 and ds and ds[0]['sr'] == 2: return ds[0]  # pratipada fell between sunrises (kshaya at month start)
    return None

HI, GJ, JN, NA, EP, OT = 'hindu', 'gujarati', 'jain', 'national', 'ekadashi_purnima', 'other'
SM = 'સ્માર્ત / ગુજરાતી પરંપરા'
# slug, name, n, t, rule, cats, tradition, major, extra
F = []
def f(slug, name, n, t, rule='sunrise', cats=(HI,), trad=SM, major=False, **x): F.append((slug, name, n, t, rule, cats, trad, major, x))
f('vasant-panchami', 'વસંત પંચમી', 11, 5, cats=(HI,), major=True)
f('ratha-saptami', 'રથ સપ્તમી', 11, 7)
f('jaya-ekadashi', 'જયા એકાદશી', 11, 11, cats=(HI, EP))
f('mahashivratri', 'મહા શિવરાત્રી', 11, 29, 'midnight', (HI, GJ), major=True)
f('phalgun-poonam', 'ફાગણ સુદ પૂનમ', 12, 15, cats=(HI, EP))
f('holika-dahan', 'હોલિકા દહન', 12, 15, 'pradosh', (GJ, HI), major=True, series='holi')
f('holi', 'હોળી', 12, 15, 'pradosh', (GJ, HI), major=True, series='holi')
f('rang-panchami', 'રંગ પંચમી', 12, 20)
f('chaitra-navratri', 'ચૈત્ર નવરાત્રી પ્રારંભ', 1, 1, cats=(HI, GJ), major=True)
f('gudi-padwa', 'ગુડી પડવો', 1, 1, cats=(HI,), major=True)
f('chaitra-sud-1', 'ગુજરાતી ચૈત્ર સુદ પ્રતિપદા (એકમ)', 1, 1, cats=(GJ, HI))
f('ram-navami', 'રામ નવમી', 1, 9, 'midday', (HI, GJ), major=True)
f('hanuman-jayanti', 'હનુમાન જયંતિ', 1, 15, cats=(HI, GJ, EP), major=True)
f('mahavir-jayanti', 'મહાવીર જયંતિ', 1, 13, cats=(JN,), trad='જૈન (શ્વેતાંબર/દિગંબર)', major=True)
f('akshaya-tritiya', 'અક્ષય તૃતીયા', 2, 3, cats=(HI, GJ), major=True)
f('parashuram-jayanti', 'પરશુરામ જયંતિ', 2, 3, 'pradosh')
f('ganga-dussehra', 'ગંગા દશેરા', 3, 10)
f('nirjala-ekadashi', 'નિર્જળા એકાદશી', 3, 11, cats=(HI, EP))
f('rath-yatra', 'રથયાત્રા', 4, 2, cats=(GJ, HI), major=True)
f('ashadhi-bij', 'અષાઢી બીજ', 4, 2, cats=(GJ, OT), major=True)
f('devshayani', 'દેવશયની એકાદશી', 4, 11, cats=(HI, EP), major=True)
f('guru-purnima', 'ગુરુ પૂર્ણિમા', 4, 15, cats=(HI, EP), major=True)
f('shravan-start', 'શ્રાવણ માસ પ્રારંભ', 5, 1, cats=(GJ, HI), major=True)
f('raksha-bandhan', 'રક્ષાબંધન (બળેવ)', 5, 15, 'midday', (GJ, HI, EP), major=True)
f('nag-panchami', 'નાગ પંચમી', 5, 20, 'midday', (GJ, HI))
f('janmashtami', 'જન્માષ્ટમી', 5, 23, 'midnight', (GJ, HI), major=True)
f('gokulashtami', 'ગોકુળાષ્ટમી', 5, 23, 'midnight', (GJ, HI), major=True)
f('ganesh-chaturthi', 'ગણેશ ચતુર્થી', 6, 4, 'midday', (GJ, HI), major=True)
f('rishi-panchami', 'ઋષિ પંચમી', 6, 5, 'midday')
f('radhashtami', 'રાધાષ્ટમી', 6, 8)
f('anant-chaturdashi', 'અનંત ચતુર્દશી', 6, 14, cats=(HI, GJ), major=True)
f('bhadarvi-poonam', 'ભાદરવી પૂનમ', 6, 15, cats=(GJ, EP), major=True)
f('ambaji-mela', 'અંબાજી ભાદરવી પૂનમ મેળો (પૂનમ દિવસ)', 6, 15, cats=(GJ, OT), trad='ગુજરાત (અંબાજી) – મેળો અનેક દિવસ ચાલે છે; તારીખો મંદિર ટ્રસ્ટ પાસેથી ચકાસો')
f('pitru-start', 'પિતૃ પક્ષ પ્રારંભ', 6, 16, cats=(HI,), major=True)
f('sarvapitru', 'સર્વ પિતૃ અમાવસ્યા (પિતૃ પક્ષ સમાપ્તિ)', 6, 30, cats=(HI, EP), major=True)
f('ghatasthapana', 'ઘટસ્થાપના', 7, 1, cats=(GJ, HI), major=True)
for i, nm in enumerate(['પ્રથમા', 'બીજ', 'ત્રીજ', 'ચોથ', 'પાંચમ', 'છઠ્ઠ', 'સાતમ', 'આઠમ', 'નોમ'], 1):
    f(f'navratri-{i}', f'શારદીય નવરાત્રી દિવસ {i}: {nm}', 7, i, cats=(GJ, HI), major=(i in (1, 8, 9)), series='navratri')
f('durgashtami', 'દુર્ગાષ્ટમી', 7, 8, cats=(GJ, HI), major=True)
f('mahanavami', 'મહાનવમી', 7, 9, cats=(GJ, HI), major=True)
f('dussehra', 'વિજયા દશમી / દશેરા', 7, 10, 'midday', (GJ, HI), major=True)
f('sharad-purnima', 'શરદ પૂર્ણિમા', 7, 15, 'pradosh', (GJ, HI, EP), major=True)
f('rama-ekadashi', 'રમા એકાદશી', 7, 26, cats=(GJ, HI, EP), major=True, series='diwali')
f('vagh-baras', 'વાઘ બારસ', 7, 27, 'pradosh', (GJ,), major=True, series='diwali')
f('dhanteras', 'ધનતેરસ', 7, 28, 'pradosh', (GJ, HI), major=True, series='diwali')
f('kali-chaudash', 'કાળી ચૌદશ', 7, 29, 'pradosh', (GJ, HI), major=True, series='diwali')
f('diwali', 'દિવાળી / દીપાવલી / લક્ષ્મી પૂજન', 7, 30, 'pradosh', (GJ, HI), major=True, series='diwali')
f('gujarati-new-year', 'ગુજરાતી નવું વર્ષ / બેસ્ટુ વર્ષ', 8, 1, cats=(GJ, HI), major=True, series='diwali')
f('govardhan', 'ગોવર્ધન પૂજા', 8, 1, cats=(GJ, HI), major=True, series='diwali')
f('annakut', 'અન્નકૂટ', 8, 1, cats=(GJ, HI), series='diwali')
f('bhai-beej', 'ભાઈ બીજ', 8, 2, 'midday', (GJ, HI), major=True, series='diwali')
f('labh-pancham', 'લાભ પાંચમ', 8, 5, cats=(GJ, HI), major=True, series='diwali')
f('jalaram-jayanti', 'જલારામ જયંતિ', 8, 7, cats=(GJ, OT), major=True)
f('dev-uthi', 'દેવ ઉઠી એકાદશી', 8, 11, cats=(HI, EP), major=True)
f('tulsi-vivah', 'તુલસી વિવાહ', 8, 12, cats=(HI,))
f('dev-diwali', 'દેવ દિવાળી / કાર્તિક પૂર્ણિમા', 8, 15, 'pradosh', (HI, GJ, EP), major=True, series='diwali')
f('mokshada-ekadashi', 'મોક્ષદા એકાદશી', 9, 11, cats=(HI, EP))
f('gita-jayanti', 'ગીતા જયંતિ', 9, 11, cats=(HI,))
f('dattatreya-jayanti', 'દત્તાત્રેય જયંતિ', 9, 15, 'pradosh', (HI, EP))
f('vaikuntha-ekadashi', 'વૈકુંઠ એકાદશી', 10, 11, cats=(HI, EP))
# Jain
f('samvatsari', 'સંવત્સરી (શ્વેતાંબર મૂર્તિપૂજક, તપાગચ્છ)', 6, 4, cats=(JN,), trad='જૈન શ્વેતાંબર – ભાદરવા સુદ ચોથ (ગણતરી); પરંપરા/ગચ્છ મુજબ તારીખ બદલાઈ શકે', major=True)
f('digambar-das-lakshan-start', 'દશલક્ષણ પર્વ પ્રારંભ', 6, 5, cats=(JN,), trad='જૈન દિગંબર')
f('digambar-das-lakshan-end', 'દશલક્ષણ પર્વ સમાપ્તિ', 6, 14, cats=(JN,), trad='જૈન દિગંબર')
f('mahavir-nirvan', 'મહાવીર નિર્વાણ દિવસ', 7, 30, 'sunrise', (JN,), trad='જૈન – આસો અમાસ (ઉદય તિથિ)', major=True)
f('jnan-panchami', 'જ્ઞાન પંચમી (સૌભાગ્ય પંચમી)', 8, 5, cats=(JN,), trad='જૈન')
f('kartik-poonam-jain', 'કાર્તિક પૂર્ણિમા – શત્રુંજય (પાલિતાણા) યાત્રા', 8, 15, cats=(JN,), trad='જૈન – કાર્તિક પૂર્ણિમા અવલોકન', major=True)

def rec(slug, name, dd, n, t, rule, cats, trad, major, x, src=None):
    tl, pk = tlabel(n, t)
    d = dd.isoformat()
    r = dict(id=f'{slug}-{d}', n=name, d=d, year=dd.year, h=1 if major else 0, tithi=tl, paksha=pk,
             category=cats[0], cats=list(cats), tradition=trad, major=bool(major),
             source=src or f'ખગોળીય ગણતરી (અમદાવાદ, અમાંત, લાહિરી) – {RULE_GU.get(rule, "")}',
             verified=False, verified_note='ચકાસણી બાકી')
    r.update(x); return r
lunar = []
ADH = []
named_keys = set()
for mi, mo in enumerate(months):
    ds = bymonth.get(mi)
    if not ds: continue
    if mo['adhik']: ADH.append((ds[0]['date'].isoformat(), ds[-1]['date'].isoformat(), MN[mo['n']])); continue
    if not (dt.date(2025, 12, 1) <= ds[0]['date'] <= dt.date(2036, 1, 31)): continue
    for slug, name, n, t, rule, cats, trad, major, x in F:
        if n != mo['n']: continue
        dd = pick(ds, t, rule) or (pick(ds, t, 'sunrise') if rule != 'sunrise' else None)
        if not dd or not (Y0 <= dd['date'].year <= Y1): continue
        lunar.append(rec(slug, name, dd['date'], n, t, rule, cats, trad, major, x))
        named_keys.add((dd['date'], t))
    # generic ekadashi / purnima / amavasya
    if mo['n'] != 0:
        for t, nm in ((11, 'એકાદશી'), (26, 'એકાદશી'), (15, 'પૂનમ'), (30, 'અમાસ')):
            dd = pick(ds, t, 'sunrise')
            if not dd or not (Y0 <= dd['date'].year <= Y1) or (dd['date'], t) in named_keys: continue
            tl, pk = tlabel(mo['n'], t)
            nm2 = f"{MN[mo['n']]} {pk} {nm}" if t in (11, 26) else tl
            lunar.append(rec(f'gen-{t}', nm2, dd['date'], mo['n'], t, 'sunrise', (EP,), 'સ્માર્ત (ઉદય તિથિ)', False, {}))

def add_derived(slug_from, slug, name, delta, cats, major, series=None):
    for r in [x for x in lunar if x['id'].startswith(slug_from + '-2') or x['id'].startswith(slug_from + '-1')]:
        if not r['id'].startswith(slug_from + '-20'): continue
        d = dt.date.fromisoformat(r['d']) + dt.timedelta(days=delta)
        if not (Y0 <= d.year <= Y1): continue
        x = {'series': series} if series else {}
        lunar.append(dict(r, id=f'{slug}-{d.isoformat()}', n=name, d=d.isoformat(), year=d.year, category=cats[0], cats=list(cats),
                          h=1 if major else 0, major=major, **x, source=r['source'] + f' (સંબંધિત તહેવાર {delta:+d} દિવસ)'))
add_derived('holi', 'dhuleti', 'ધુળેટી', 1, (GJ, HI), True, 'holi')
add_derived('janmashtami', 'nand-mahotsav', 'નંદ મહોત્સવ', 1, (GJ, HI), False)
add_derived('samvatsari', 'paryushan-start', 'પર્યુષણ પર્વ પ્રારંભ (શ્વેતાંબર, ૮ દિવસ)', -7, (JN,), True)
add_derived('samvatsari', 'paryushan-end', 'પર્યુષણ પર્વ સમાપ્તિ (સંવત્સરી પછી ક્ષમાપના)', 1, (JN,), False)
# Rang panchami etc. already direct. Shravan Mondays (Amanta Shravan, nija)
for mi, mo in enumerate(months):
    if mo['n'] == 5 and not mo['adhik'] and bymonth.get(mi):
        k = 0
        for dd in bymonth[mi]:
            if dd['date'].weekday() == 0 and Y0 <= dd['date'].year <= Y1:
                k += 1; tl, pk = tlabel(5, dd['sr'] if dd['sr'] else 1)
                lunar.append(rec(f'shravan-somvar{k}', f'શ્રાવણ સોમવાર ({k})', dd['date'], 5, dd['sr'], 'sunrise', (GJ, HI), SM, False, {}))
# Parsi New Year (Shahenshahi): fixed 365-day year, no leap days
for y in range(Y0, Y1+1):
    day = 15 if y <= 2027 else 14 if y <= 2031 else 13
    d = dt.date(y, 8, day)
    lunar.append(dict(id=f'parsi-new-year-{d}', n='પારસી નવું વર્ષ (નવરોઝ, શહેનશાહી)', d=d.isoformat(), year=y, h=1, tithi='', paksha='',
                      category=OT, cats=[OT], tradition='પારસી (શહેનશાહી કેલેન્ડર)', major=True,
                      source='શહેનશાહી કેલેન્ડર ગણતરી (કોઈ લીપ વર્ષ નહીં) – ફક્ત અંદાજ', verified=False, verified_note='ચકાસણી બાકી'))

def fx(slug, name, md, cats, major, trad, h=1, verified=True, src='નિશ્ચિત ગ્રેગોરિયન તારીખ'):
    return dict(id=slug, n=name, md=md, h=h, category=cats[0], cats=list(cats), tradition=trad, major=major, source=src,
                verified=verified, verified_note='' if verified else 'ચકાસણી બાકી')
fixed = [
 fx('uttarayan', 'ઉત્તરાયણ / મકરસંક્રાંતિ', '01-14', (GJ, HI), True, 'ગુજરાતી પરંપરા', src='ગુજરાતમાં પરંપરાગત રીતે 14 જાન્યુઆરી (સંક્રાંતિ ક્ષણ વર્ષ પ્રમાણે બદલાઈ શકે)'),
 fx('vasi-uttarayan', 'વાસી ઉત્તરાયણ', '01-15', (GJ, HI), True, 'ગુજરાતી પરંપરા', src='ઉત્તરાયણ પછીનો દિવસ'),
 fx('republic-day', 'પ્રજાસત્તાક દિવસ', '01-26', (NA,), True, 'રાષ્ટ્રીય'),
 fx('ambedkar-jayanti', 'ડૉ. આંબેડકર જયંતિ', '04-14', (NA,), False, 'રાષ્ટ્રીય'),
 fx('gujarat-day', 'ગુજરાત સ્થાપના દિવસ', '05-01', (NA, GJ), True, 'ગુજરાત'),
 fx('independence-day', 'સ્વાતંત્ર્ય દિવસ', '08-15', (NA,), True, 'રાષ્ટ્રીય'),
 fx('gandhi-jayanti', 'ગાંધી જયંતિ', '10-02', (NA,), True, 'રાષ્ટ્રીય'),
 fx('ekta-divas', 'સરદાર પટેલ જયંતિ (રાષ્ટ્રીય એકતા દિવસ)', '10-31', (NA, OT), False, 'રાષ્ટ્રીય', h=0),
 fx('christmas', 'નાતાલ', '12-25', (NA,), False, 'રાષ્ટ્રીય/ખ્રિસ્તી'),
]
lunar.sort(key=lambda r: (r['d'], not r['major'], r['n']))
out = dict(version=1, fixed=fixed, lunar=lunar,
           meta=dict(generated_by='tools/gen.py', location='Ahmedabad (23.0225N, 72.5714E)', years=[Y0, Y1], calendar='Amanta, Vikram',
                     note='તમામ lunar તારીખો ગણતરી આધારિત છે – છાપેલા પંચાંગ સાથે ચકાસણી બાકી (verified=false).',
                     adhik_months=ADH))
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'generated.json'), 'w'), ensure_ascii=False, indent=1)
print(len(fixed), 'fixed;', len(lunar), 'dated; adhik:', ADH)
