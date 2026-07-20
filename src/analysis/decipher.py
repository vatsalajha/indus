import json, glob, math, os
from collections import Counter, defaultdict

HERE=os.path.dirname(os.path.abspath(__file__))
CORP=os.path.join(HERE,"..","..","mayig","corpus"); FEAT=os.path.join(HERE,"..","..","mayig","features")
signs={}
for f in glob.glob(f"{FEAT}/*.json"):
    d=json.load(open(f)); signs[d["id"]]={"desc":d.get("description",""),"M":",".join(d.get("mahadevan_graphemes",[])) or "-"}
texts=[]
for f in glob.glob(f"{CORP}/**/*.json",recursive=True):
    for side in json.load(open(f)):
        gs=[g["id"] for g in side.get("graphemes",[]) if g["id"]!="P000"]  # drop damage marker
        if len(gs)>=2: texts.append(list(reversed(gs)))  # reading order
freq=Counter(s for t in texts for s in t)
N=len(texts)
D=lambda s: signs.get(s,{}).get("desc","?")[:38]

# ================= ATTACK 1: PARADIGMATIC SUBSTITUTION (Kober method, automated) =================
# Context vector per sign: left-neighbor counts, right-neighbor counts, boundary markers
ctx=defaultdict(Counter)
for t in texts:
    for i,s in enumerate(t):
        L = t[i-1] if i>0 else "<START>"
        R = t[i+1] if i<len(t)-1 else "<END>"
        ctx[s]["L:"+L]+=1; ctx[s]["R:"+R]+=1

def cos(a,b):
    keys=set(a)|set(b)
    num=sum(a[k]*b[k] for k in keys)
    da=math.sqrt(sum(v*v for v in a.values())); db=math.sqrt(sum(v*v for v in b.values()))
    return num/(da*db) if da*db else 0

MINF=6
cands=[s for s,c in freq.items() if c>=MINF]
pairs=[]
for i,a in enumerate(cands):
    for b in cands[i+1:]:
        pairs.append((cos(ctx[a],ctx[b]),a,b))
pairs.sort(reverse=True)
print("=== ATTACK 1: SUBSTITUTION PAIRS (signs used in near-identical contexts) ===")
print("High similarity = same functional class (Kober's insight, computed)\n")
for sim,a,b in pairs[:14]:
    print(f"  {sim:.2f}  {a} ~ {b}   [{D(a)}]  ~  [{D(b)}]")

# ================= ATTACK 2: SLOT GRAMMAR =================
# Assign each frequent sign a modal slot from its position distribution, then test template coverage
def slot_of(s):
    pos=[]
    for t in texts:
        L=len(t)
        for i,x in enumerate(t):
            if x==s and L>1: pos.append(i/(L-1))
    if not pos: return "?"
    m=sum(pos)/len(pos)
    term_share=sum(1 for p in pos if p==1.0)/len(pos)
    init_share=sum(1 for p in pos if p==0.0)/len(pos)
    if term_share>0.5: return "SUF"     # suffix slot
    if init_share>0.4: return "OPEN"    # opener
    if m>0.66: return "PRE-SUF"
    if m<0.33: return "EARLY"
    return "BODY"
slotmap={s:slot_of(s) for s in cands}
# numerals hand-flagged by description
for s in cands:
    d=signs.get(s,{}).get("desc","").lower()
    if "stroke" in d and "vertical" in d: slotmap[s]="NUM"

print("\n=== ATTACK 2: DERIVED SLOT CLASSES ===")
byslot=defaultdict(list)
for s,sl in sorted(slotmap.items()): byslot[sl].append(s)
for sl in ["OPEN","EARLY","NUM","BODY","PRE-SUF","SUF"]:
    ss=byslot.get(sl,[])
    if ss: print(f"  {sl:8}: "+", ".join(f"{s}" for s in ss))

# Template test: OPEN? (NUM|EARLY|BODY)* PRE-SUF? SUF?  in reading order
import re
def classify(t):
    return [slotmap.get(s,"RARE") for s in t]
grammar=re.compile(r"^(OPEN)?(EARLY|NUM|BODY|RARE)*(PRE-SUF)?(SUF){0,2}$")
ok=sum(1 for t in texts if grammar.match("".join(f"({c})" for c in classify(t)).replace(")(","|").strip("()") ) is not None)
# simpler check: monotonicity of slot order
order={"OPEN":0,"EARLY":1,"NUM":1,"BODY":2,"RARE":2,"PRE-SUF":3,"SUF":4}
def monotone(t):
    cs=[order[c] for c in classify(t)]
    # allow equal, require non-decreasing except RARE/BODY free
    return all(cs[i]<=cs[i+1] or {cs[i],cs[i+1]}<= {1,2} for i in range(len(cs)-1))
mono=sum(1 for t in texts if monotone(t))
print(f"\n  Texts obeying the slot template (monotone order OPEN<EARLY/NUM<BODY<PRE-SUF<SUF): {mono}/{N} = {100*mono/N:.0f}%")
import random
random.seed(7)
sh=0
for t in texts:
    tt=t[:]; random.shuffle(tt)
    if monotone(tt): sh+=1
print(f"  Same test on order-shuffled texts (control):                                    {sh}/{N} = {100*sh/N:.0f}%")

# ================= ATTACK 3: AGGLUTINATION TEST =================
print("\n=== ATTACK 3: SUFFIX-STACKING (Dravidian agglutination prediction) ===")
# What sits immediately before the jar? And before THAT? Chain depth
jar="P324"
pre1=Counter(); pre2=Counter(); after=Counter()
for t in texts:
    for i,s in enumerate(t):
        if s==jar:
            if i>=1: pre1[t[i-1]]+=1
            if i>=2: pre2[t[i-2]]+=1
            if i<len(t)-1: after[t[i+1]]+=1
print(f"  Jar occurrences with something AFTER it: {sum(after.values())} (suffix should be near-final)")
print("  What follows jar (should be only closers if jar is a suffix):")
for s,c in after.most_common(5):
    print(f"    x{c}  {s}  [{D(s)}]  slot={slotmap.get(s,'RARE')}")
print("  Top fillers of the slot right before jar (the STEM position):")
for s,c in pre1.most_common(8):
    print(f"    x{c}  {s}  [{D(s)}]")
# suffix chain: PRE-SUF class then SUF then terminal-logogram => 3-deep chain like Dravidian
chain3=0
for t in texts:
    cs=classify(t)
    for i in range(len(cs)-2):
        if cs[i]=="PRE-SUF" and cs[i+1]=="SUF": chain3+=1; break
print(f"\n  Texts showing a 2-deep ending chain (PRE-SUF + SUF), the agglutinative signature: {chain3} ({100*chain3/N:.0f}%)")

# ================= ATTACK 4: NUMERAL PHRASES (step 4 of the playbook) =================
print("\n=== ATTACK 4: WHAT DO THEY COUNT? (numeral + noun extraction) ===")
nums=[s for s in cands if slotmap.get(s)=="NUM"]
counted=Counter()
for t in texts:
    for i,s in enumerate(t):
        if s in nums and i<len(t)-1:
            counted[t[i+1]]+=1
print("  Signs most often counted (immediately follow a numeral):")
for s,c in counted.most_common(8):
    print(f"    x{c}  {s}  [{D(s)}]")