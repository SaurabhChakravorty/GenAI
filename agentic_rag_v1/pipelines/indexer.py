
from __future__ import annotations
from typing import List, Dict
import os, re, json

def _read_texts(corpus_dir: str) -> List[str]:
    texts=[] 
    for fn in os.listdir(corpus_dir):
        p=os.path.join(corpus_dir, fn)
        if not os.path.isfile(p): continue
        if fn.lower().endswith((".txt",".md")):
            with open(p,"r",encoding="utf-8",errors="ignore") as f:
                texts.append(f.read())
    return texts

def _chunks(text: str, max_tokens: int=1200) -> List[str]:
    # naive chunking by paragraphs
    paras = re.split(r"\n\s*\n", text)
    chunks=[]; cur=""
    for para in paras:
        if len(cur)+len(para) > max_tokens:
            if cur: chunks.append(cur); cur=""
        cur += (para.strip()+"\n\n")
    if cur: chunks.append(cur)
    return chunks

def build_local_index(corpus_dir: str, out_path: str) -> List[Dict]:
    rows=[]; 
    for i, txt in enumerate(_read_texts(corpus_dir)):
        for ch in _chunks(txt):
            rows.append({"text": ch, "meta":{"chunk_id": len(rows)}, "source":"local:index"})
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f)
    return rows

def load_local_index(path: str) -> List[Dict]:
    import json, os
    if not os.path.exists(path): return []
    with open(path,"r",encoding="utf-8") as f:
        return json.load(f)
