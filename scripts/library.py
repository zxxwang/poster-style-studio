import argparse,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]/'styles'
def records():
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted(ROOT.glob('*.json'))]
def main():
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['list','get','add']); p.add_argument('value',nargs='?'); a=p.parse_args(); ROOT.mkdir(exist_ok=True)
    rows=records()
    if a.action=='list': result=[{k:r[k] for k in ('id','name','description','aspect_ratio')} for r in rows]
    elif a.action=='get':
        matches=[r for r in rows if a.value in (r['id'],r['name'])];
        if len(matches)!=1: raise ValueError('风格不存在或名称有歧义')
        result=matches[0]
    else:
        r=json.loads(Path(a.value).read_text(encoding='utf-8')); schema=json.loads((ROOT.parent/'schema.json').read_text())
        for k in schema['required']:
            if k not in r or not isinstance(r[k],str) or not r[k].strip(): raise ValueError('缺少或无效字段: '+k)
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',r['id']): raise ValueError('ID 必须为 ASCII slug')
        if any(x['id']==r['id'] or x['name']==r['name'] for x in rows): raise ValueError('风格已存在，不覆盖')
        r['created_at']=datetime.now(timezone.utc).isoformat(); dest=ROOT/(r['id']+'.json')
        with dest.open('x',encoding='utf-8') as f: json.dump(r,f,ensure_ascii=False,indent=2)
        result={'saved':str(dest),'style':r}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
    try: main()
    except (ValueError,OSError,TypeError) as e: sys.exit(str(e))
