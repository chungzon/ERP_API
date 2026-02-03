"""API documentation endpoint."""

import os
import re
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse

router = APIRouter(prefix="/api/doc", tags=["Documentation"])

# Path to API_REFERENCE.txt
DOC_PATH = Path(__file__).parent.parent.parent / "doc" / "API_REFERENCE.txt"


def _txt_to_html(content: str) -> str:
    """Convert API_REFERENCE.txt to styled HTML."""

    # Escape HTML special characters
    content = content.replace("&", "&amp;")
    content = content.replace("<", "&lt;")
    content = content.replace(">", "&gt;")

    lines = content.split("\n")
    html_lines = []
    in_json = False
    in_code = False

    for line in lines:
        # Detect JSON blocks
        if line.strip().startswith("{") and not in_json:
            in_json = True
            html_lines.append('<pre class="json">')

        if in_json:
            html_lines.append(line)
            if line.strip().startswith("}") and line.strip().endswith("}"):
                in_json = False
                html_lines.append("</pre>")
            continue

        # Main title (=== lines)
        if line.startswith("=" * 40):
            html_lines.append('<hr class="title-line">')
            continue

        # Section headers (### lines)
        if line.startswith("#" * 40):
            html_lines.append('<hr class="section-line">')
            continue

        # Subsection dividers (--- lines)
        if line.startswith("-" * 40):
            html_lines.append('<hr class="subsection-line">')
            continue

        # Main headers (centered text between === lines)
        if "ERP 系統 API 完整說明文件" in line:
            html_lines.append(f'<h1 class="main-title">{line.strip()}</h1>')
            continue

        # Section titles (【...】)
        match = re.match(r'^【(.+)】(.*)$', line.strip())
        if match:
            html_lines.append(f'<h2 class="section-title">【{match.group(1)}】{match.group(2)}</h2>')
            continue

        # API titles in section headers
        if line.strip() and all(c in "# " for c in line[:5]) and "API" in line:
            html_lines.append(f'<h2 class="api-section">{line.strip().replace("#", "").strip()}</h2>')
            continue

        # HTTP methods
        if re.match(r'^(GET|POST|PUT|DELETE|PATCH)\s+/', line.strip()):
            html_lines.append(f'<code class="http-method">{line.strip()}</code>')
            continue

        # Curl commands
        if line.strip().startswith("curl "):
            html_lines.append(f'<pre class="curl">{line}</pre>')
            continue

        # Comments starting with #
        if line.strip().startswith("# "):
            html_lines.append(f'<p class="comment">{line.strip()}</p>')
            continue

        # Table-like content (with multiple spaces as separator)
        if "  " in line and not line.strip().startswith("-"):
            html_lines.append(f'<pre class="table-row">{line}</pre>')
            continue

        # Regular text
        if line.strip():
            html_lines.append(f'<p>{line}</p>')
        else:
            html_lines.append('<br>')

    body_content = "\n".join(html_lines)

    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERP API 說明文件</title>
    <style>
        :root {{
            --bg-color: #1a1a2e;
            --card-bg: #16213e;
            --text-color: #eee;
            --accent-color: #0f3460;
            --highlight: #e94560;
            --success: #00d9ff;
            --border-color: #0f3460;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }}

        h1.main-title {{
            text-align: center;
            color: var(--success);
            font-size: 2em;
            margin: 20px 0;
            padding: 20px;
            background: var(--card-bg);
            border-radius: 10px;
            border: 1px solid var(--border-color);
        }}

        h2.section-title {{
            color: var(--highlight);
            background: var(--card-bg);
            padding: 15px 20px;
            border-radius: 8px;
            margin-top: 30px;
            border-left: 4px solid var(--highlight);
        }}

        h2.api-section {{
            color: var(--success);
            text-align: center;
            padding: 20px;
            margin: 40px 0 20px;
            background: linear-gradient(135deg, var(--card-bg), var(--accent-color));
            border-radius: 10px;
        }}

        hr.title-line {{
            border: none;
            height: 3px;
            background: linear-gradient(90deg, transparent, var(--success), transparent);
            margin: 10px 0;
        }}

        hr.section-line {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--highlight), transparent);
            margin: 30px 0;
        }}

        hr.subsection-line {{
            border: none;
            height: 1px;
            background: var(--border-color);
            margin: 15px 0;
        }}

        code.http-method {{
            display: inline-block;
            background: var(--accent-color);
            color: var(--success);
            padding: 8px 16px;
            border-radius: 5px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 1.1em;
            font-weight: bold;
            margin: 10px 0;
        }}

        pre.json {{
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            border: 1px solid var(--border-color);
            margin: 10px 0;
        }}

        pre.curl {{
            background: #0d1117;
            color: #ffa657;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85em;
            border: 1px solid var(--border-color);
            margin: 5px 0;
            white-space: pre-wrap;
            word-break: break-all;
        }}

        pre.table-row {{
            background: transparent;
            color: var(--text-color);
            padding: 5px 10px;
            margin: 2px 0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            white-space: pre;
        }}

        p {{
            margin: 8px 0;
            padding-left: 10px;
        }}

        p.comment {{
            color: #8b949e;
            font-style: italic;
            margin: 15px 0 5px;
            padding-left: 0;
        }}

        br {{
            display: block;
            content: "";
            margin: 5px 0;
        }}

        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: var(--bg-color);
        }}

        ::-webkit-scrollbar-thumb {{
            background: var(--accent-color);
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: var(--highlight);
        }}
    </style>
</head>
<body>
{body_content}
</body>
</html>'''

    return html


@router.get("/reference", response_class=HTMLResponse)
def get_api_reference_html():
    """Get API reference documentation as styled HTML."""
    if not DOC_PATH.exists():
        return HTMLResponse(
            content="<html><body><h1>Documentation not found</h1></body></html>",
            status_code=404
        )

    content = DOC_PATH.read_text(encoding="utf-8")
    html = _txt_to_html(content)
    return HTMLResponse(content=html)


@router.get("/reference/raw", response_class=PlainTextResponse)
def get_api_reference_raw():
    """Get API reference documentation as plain text."""
    if not DOC_PATH.exists():
        return PlainTextResponse(
            content="Documentation not found",
            status_code=404
        )

    content = DOC_PATH.read_text(encoding="utf-8")
    return PlainTextResponse(content=content)


@router.get("/health", response_class=PlainTextResponse)
def health():
    """Health check endpoint."""
    return "OK"
