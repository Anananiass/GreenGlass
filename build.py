"""Gera versões autossuficientes do site em dist/ (CSS, JS e imagens embutidos).

Cada arquivo de dist/ funciona sozinho: basta subir dist/index.html e
dist/ecojoias.html para o GitHub, sem as pastas css/, js/ e img/.

Uso:  python build.py
"""
import base64
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIST = RAIZ / "dist"
PAGINAS = ["index.html", "ecojoias.html"]
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}


def ler(caminho):
    return (RAIZ / caminho.split("?")[0]).read_text(encoding="utf-8")


def data_uri(caminho):
    arquivo = RAIZ / caminho.split("?")[0]
    return f"data:{MIME[arquivo.suffix.lower()]};base64,{base64.b64encode(arquivo.read_bytes()).decode()}"


def embutir(nome):
    html = (RAIZ / nome).read_text(encoding="utf-8")
    html = re.sub(r'<link rel="stylesheet" href="(css/[^"]+)">',
                  lambda m: "<style>\n" + ler(m.group(1)) + "\n</style>", html)
    html = re.sub(r'<script src="(js/[^"]+)"></script>',
                  lambda m: "<script>\n" + ler(m.group(1)) + "\n</script>", html)
    # caminhos de imagem entre aspas, no HTML ou dentro do JS
    html = re.sub(r"""(["'])(img/[^"']+)\1""",
                  lambda m: m.group(1) + data_uri(m.group(2)) + m.group(1), html)
    sobras = re.findall(r"""["'](?:css|js|img)/[^"']*["']""", html)
    if sobras:
        raise SystemExit(f"{nome}: referências locais não embutidas: {sobras}")
    return html


DIST.mkdir(exist_ok=True)
for pagina in PAGINAS:
    saida = DIST / pagina
    saida.write_text(embutir(pagina), encoding="utf-8")
    print(f"{pagina:15} -> dist/{pagina}  ({saida.stat().st_size / 1024:.0f} KB)")
