import re,sys,collections
lines=[l for l in open('usage_census.txt').read().split('\nNOTES',1)[1].splitlines()[1:] if l.strip()]
cats={'redraw/new art':r'\b(redraw|regen|new art|make (it|a|an|new|more)|generate|draw|render|redo|re-?do)\b',
'cut/remove/delete':r'\b(cut|remove|delete|drop|kill|get rid)\b',
'size/scale':r'\b(size|scale|bigger|smaller|larger|tiny|huge|giant|tall|small)\b',
'rename/name':r'\b(rename|name|called)\b',
'description':r'\b(description|describe)\b',
'facing/north/side':r'\b(facing|north|south|east|west|side view|back view|from behind)\b',
'move biome/tier':r'\b(move|biome|belongs|tier)\b',
'pick a letter':r'\b(use|pick|choose|go with|keep)\s+[A-Z]\b|\b[A-Z]\s+is\s+(best|good|great|fine)',
'keep/accept current':r'\b(keep|fine|good|ok|okay|accept|looks great|love)\b',
'colour/style':r'\b(colou?r|palette|brown|style|outline|shading|realistic|alien)\b',
'canon/star wars':r'\b(canon|star wars|wookieepedia|movie|film)\b',
'more variants':r'\b(more|variants?|versions?|options)\b'}
c=collections.Counter(); multi=0; lens=[]
for l in lines:
    t=l.split(': ',1)[-1]; lens.append(len(t)); hit=[k for k,p in cats.items() if re.search(p,t,re.I)]
    for h in hit: c[h]+=1
    if len(hit)>=2: multi+=1
lens.sort()
print('notes',len(lines),'median chars',lens[len(lens)//2],'p90',lens[int(.9*len(lens))],'multi-category',multi)
for k,v in c.most_common(): print(f'{k:22s}{v}')
