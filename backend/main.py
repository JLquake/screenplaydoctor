import os, json, tempfile, xml.etree.ElementTree as ET
from fastapi import FastAPI, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def fdx_to_text(fdx: str) -> str:
    root = ET.fromstring(fdx)
    lines = []
    for elem in root.iter():
        if elem.tag in ("SceneHeading", "Dialogue", "Action"):
            lines.append(elem.text or "")
    return "\n".join(lines)

def coverage_report(script_text: str) -> dict:
    prompt = f"""You are a senior story analyst at CAA.
Script:
{script_text[:15_000]}
----
Provide JSON only:
{{
  "logline": "...",
  "strengths": ["..."],
  "weaknesses": ["..."],
  "grammar_issues": ["..."],
  "suggestions": ["..."]
}}"""
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.3)
    return json.loads(response.choices[0].message.content)

@app.post("/upload")
async def upload(file: bytes = File(...)):
    try:
        text = fdx_to_text(file.decode("utf-8"))
    except Exception:
        raise HTTPException(400, "Invalid .fdx file")
    report = coverage_report(text)
    return {"text": text, "report": report}

@app.post("/rewrite")
async def rewrite(script: str = Form(...), note: str = Form(...)):
    prompt = f"""You are a WGA writer doing a polish.
Rewrite the following pages to satisfy this note: "{note}"
Keep every slugline and action line unless you must change it.
Output ONLY the rewritten pages in Final Draft XML paragraph elements.
{script}"""
    response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], temperature=0.4)
    return {"newXml": response.choices[0].message.content}
