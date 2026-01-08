import re

def chunk_faq(text: str):
    blocks = re.split(r"(?=Q:\s)", text)
    chunks = []
    for b in blocks:
        if "A:" in b:
            q, a = b.split("A:", 1)
            chunks.append({
                "content": f"{q.strip()}\nA: {a.strip()}",
                "question": q.replace("Q:", "").strip()
            })
    return chunks

def chunk_numbered_sections(text: str):
    pattern = re.compile(r'(\d+\.\d+)\s+[A-Z]')
    matches = list(pattern.finditer(text))
    sections = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sec = text[start:end].strip()
        if len(sec) > 120:
            sections.append(sec)
    return sections
