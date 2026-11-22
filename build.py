"""Gera o site estático em dist/ a partir de config.json + guias/*.json.
    python build.py
Estrutura: dist/index.html (código do vídeo) · dist/<slug>/index.html (captura + guia) · dist/guias/<slug>.json
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

AQUI = Path(__file__).resolve().parent
DIST = AQUI / "dist"
CFG = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))
E = html.escape
FONTES = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
          '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">')


def cfg_publico() -> str:
    pub = {k: CFG[k] for k in ("supabase_url", "supabase_key")}
    return json.dumps(pub).replace("</", "<\\/")


def pixel() -> str:
    pid = CFG.get("pixel_id", "").strip()
    if not pid.isdigit():
        return ""
    return ("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):"
            "n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);"
            "t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script',"
            f"'https://connect.facebook.net/en_US/fbevents.js');fbq('init','{pid}');fbq('track','PageView');</script>")


def cabeca(titulo: str, desc: str, raiz: str) -> str:
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(titulo)}</title>'
            f'<meta name="description" content="{E(desc)}"><meta property="og:title" content="{E(titulo)}">'
            f'<meta property="og:description" content="{E(desc)}"><meta name="theme-color" content="#07090f">'
            f'{FONTES}<link rel="stylesheet" href="{raiz}style.css">{pixel()}</head>')


def topo(raiz: str) -> str:
    return (f'<header class="wrap topo"><a class="marca" href="{raiz}"><i></i>{E(CFG["marca"])} · Guias</a>'
            f'<small>@{E(CFG["instagram"])}</small></header>')


def rodape(raiz: str) -> str:
    return (f'<footer class="wrap rodape">© 2026 {E(CFG["marca"])} · Conteúdo gratuito e independente. '
            f'Nomes e marcas pertencem aos respectivos donos. · <a href="{raiz}privacidade/">Privacidade</a></footer>')


def oferta(guia: dict) -> str:
    o = CFG["oferta"]
    num = "".join(c for c in CFG.get("whatsapp", "") if c.isdigit())
    msg = o["mensagem_wa"].replace("{guia}", guia["codigo"])
    href = f"https://wa.me/{num}?text={quote(msg)}" if num else f"https://ig.me/m/{CFG['instagram']}"
    itens = "".join(f"<li>{E(b)}</li>" for b in o["bullets"])
    return (f'<aside id="oferta" class="cartao oferta oculto"><span class="selo">Próximo passo</span>'
            f'<h2>{E(o["titulo"])}</h2><p id="ponte"></p><p>{E(o["texto"])}</p><ul>{itens}</ul>'
            f'<a id="cta-oferta" class="btn verde" href="{E(href)}" target="_blank" rel="noopener">{E(o["cta"])} →</a>'
            + (f'<a class="btn" style="background:transparent;border:1px solid var(--line);box-shadow:none;margin-top:10px" '
               f'href="{E(href)}" target="_blank" rel="noopener">{E(o["cta2"])}</a>' if o.get("cta2") else "")
            + '<p class="seguro">Abre uma conversa direta comigo no Instagram.</p></aside>')


def pagina_guia(g: dict) -> str:
    raiz = "../"
    return (cabeca(g["titulo"], g["sub"], raiz) + f'<body data-slug="{E(g["slug"])}">' + topo(raiz) +
            f'<main class="wrap"><span class="selo">Material gratuito · código {E(g["codigo"])}</span>'
            f'<h1>{E(g["destaque"])}</h1><p class="sub">{E(g["sub"])}</p>'
            '<form id="form-lead" class="cartao" novalidate><div id="captura">'
            '<h2>Onde a gente te manda o guia?</h2><p>Preencha e o guia completo abre na hora, aqui mesmo.</p>'
            '<label for="nome">Nome</label><input id="nome" autocomplete="given-name" placeholder="Seu nome" required>'
            '<label for="email">E-mail</label><input id="email" type="email" autocomplete="email" placeholder="seu@email.com" required>'
            '<label for="tel">WhatsApp</label><div class="tel"><select id="ddi" aria-label="Código do país"></select>'
            '<input id="tel" type="tel" inputmode="numeric" autocomplete="tel-national" placeholder="(11) 99999-9999" required></div>'
            '<input id="site" name="site" tabindex="-1" autocomplete="off" class="oculto" aria-hidden="true">'
            '<label class="consent"><input id="consent" type="checkbox"> Aceito receber este guia e novidades por e-mail e WhatsApp. '
            'Posso sair quando quiser. <a href="../privacidade/" target="_blank">Privacidade</a></label>'
            '<button id="bt-lead" class="btn" type="submit">Acessar o guia completo</button>'
            '<div id="erro-lead" class="erro" role="alert"></div><p class="seguro">🔒 Seus dados ficam com a gente e não são vendidos.</p>'
            '</div></form><article id="guia" class="guia oculto"></article>' + oferta(g) + '</main>' + rodape(raiz) +
            f'<script id="cfg" type="application/json">{cfg_publico()}</script><script src="../app.js" defer></script></body></html>')


def pagina_inicio(guias: list[dict]) -> str:
    raiz = "./"
    codigos = json.dumps({g["codigo"].upper(): g["slug"] for g in guias})
    lista = "".join(f'<a href="{E(g["slug"])}/"><b>{E(g["destaque"])}</b><span>{E(g["sub"])}</span><small>{E(g["codigo"])}</small></a>'
                    for g in guias)
    return (cabeca(f'Guias gratuitos de IA | {CFG["marca"]}', "Os materiais dos vídeos: links, comandos e passo a passo.", raiz) +
            '<body>' + topo(raiz) + '<main class="wrap"><span class="selo">Guias gratuitos</span>'
            '<h1>Digite o <em>código</em> do vídeo</h1><p class="sub">Cada vídeo tem um código (aparece no final e na legenda). '
            'Coloca ele aqui pra liberar o material completo: links, comandos e passo a passo.</p>'
            '<form id="form-codigo" class="cartao"><label for="codigo">Código do vídeo</label><div class="codigo">'
            '<input id="codigo" placeholder="ex: APAGAR" autocomplete="off" autocapitalize="characters" required>'
            '<button class="btn" type="submit">Abrir</button></div><div id="erro-codigo" class="erro" role="alert"></div></form>'
            f'<h2 style="font:600 22px var(--font-display);margin:44px 0 14px">Todos os guias</h2><div class="ferr">{lista}</div></main>'
            + rodape(raiz) + f'<script id="codigos" type="application/json">{codigos}</script>'
            f'<script id="cfg" type="application/json">{cfg_publico()}</script><script src="app.js" defer></script></body></html>')


def pagina_privacidade() -> str:
    raiz = "../"
    return (cabeca("Privacidade", "Como tratamos os seus dados.", raiz) + '<body>' + topo(raiz) +
            '<main class="wrap guia"><h1>Privacidade</h1><div class="secao">'
            f'<p>Responsável: {E(CFG["marca"])} (Instagram @{E(CFG["instagram"])}).</p>'
            '<p>Recolhemos nome, e-mail e WhatsApp quando você pede um guia, pra te enviar o material e novidades sobre IA e sobre os '
            'nossos serviços. Base legal: o seu consentimento (LGPD art. 7º, I; RGPD art. 6.º, 1, a).</p>'
            '<p>Os dados ficam guardados num servidor seguro (Supabase, UE) e não são vendidos nem cedidos a terceiros.</p>'
            '<p>Você pode pedir acesso, correção ou exclusão a qualquer momento mandando uma mensagem no Instagram, ou responder '
            '"SAIR" em qualquer mensagem pra não receber mais nada.</p>'
            '<p>Se o Pixel da Meta estiver ativo, ele mede visitas e cadastros pra melhorar os anúncios.</p></div></main>'
            + rodape(raiz) + '</body></html>')


def main() -> None:
    guias = []
    for f in sorted((AQUI / "guias").glob("*.json")):
        g = json.loads(f.read_text(encoding="utf-8"))
        for k in ("slug", "codigo", "titulo", "destaque", "sub", "secoes"):
            if not g.get(k):
                raise SystemExit(f"{f.name}: falta '{k}'")
        guias.append(g)
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "guias").mkdir(parents=True)
    for nome in ("style.css", "app.js"):
        shutil.copy(AQUI / "src" / nome, DIST / nome)
    (DIST / "index.html").write_text(pagina_inicio(guias), encoding="utf-8")
    (DIST / "privacidade").mkdir()
    (DIST / "privacidade" / "index.html").write_text(pagina_privacidade(), encoding="utf-8")
    for g in guias:
        (DIST / g["slug"]).mkdir()
        (DIST / g["slug"] / "index.html").write_text(pagina_guia(g), encoding="utf-8")
        shutil.copy(AQUI / "guias" / f"{g['slug']}.json", DIST / "guias" / f"{g['slug']}.json")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"ok: {len(guias)} guias → {DIST}")


if __name__ == "__main__":
    main()
