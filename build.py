"""Gera o site estático em docs/ a partir de config.json + guias/*.json.
    python build.py
Estrutura: docs/index.html (código do vídeo) · docs/<slug>/index.html (captura + guia) · docs/guias/<slug>.json
Identidade visual: a mesma do Kit Edição com IA (roxo/lima/tinta/papel, Big Shoulders + Schibsted + Martian Mono).
"""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

AQUI = Path(__file__).resolve().parent
DIST = AQUI / "docs"  # o GitHub Pages serve /docs
CFG = json.loads((AQUI / "config.json").read_text(encoding="utf-8"))
E = html.escape
FONTES = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
          '<link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@700;800;900'
          '&family=Schibsted+Grotesk:wght@400;500;600;700&family=Martian+Mono:wght@400;500&display=swap" rel="stylesheet">')
ICONE_WA = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 '
            '1.17-.17.2-.35.22-.64.07-.3-.15-1.26-.46-2.39-1.47-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.62-.92-2.22-.24-.58-.49-.5-.67-.51h-.57c-.2 '
            '0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.21 3.08c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.19 1.87.12.57-.09 '
            '1.76-.72 2.01-1.41.25-.7.25-1.29.17-1.41-.07-.13-.27-.2-.57-.35zM12.05 21.5h-.01a9.4 9.4 0 0 1-4.8-1.31l-.34-.2-3.57.93.95-3.48-.22-.36a9.42 '
            '9.42 0 0 1-1.45-5.02c0-5.2 4.24-9.44 9.45-9.44 2.52 0 4.89.99 6.67 2.77a9.37 9.37 0 0 1 2.76 6.68c0 5.2-4.24 9.43-9.44 9.43zm8.03-17.47A11.3 '
            '11.3 0 0 0 12.05.7C5.79.7.7 5.79.7 12.04c0 2 .52 3.95 1.52 5.67L.6 23.6l6.04-1.58a11.33 11.33 0 0 0 5.41 1.38h.01c6.25 0 11.34-5.09 11.35-11.34a11.27 '
            '11.27 0 0 0-3.33-8.03z"/></svg>')
TICKER = ["Links oficiais", "Comandos prontos", "Passo a passo", "Grátis", "Verificado"]


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


def wa_link(msg: str) -> str:
    num = "".join(c for c in CFG.get("whatsapp", "") if c.isdigit())
    return f"https://wa.me/{num}?text={quote(msg)}" if num else f"https://ig.me/m/{CFG['instagram']}"


def cabeca(titulo: str, desc: str, raiz: str) -> str:
    return (f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(titulo)}</title>'
            f'<meta name="description" content="{E(desc)}"><meta property="og:title" content="{E(titulo)}">'
            f'<meta property="og:description" content="{E(desc)}"><meta name="theme-color" content="#100b1c">'
            f'{FONTES}<link rel="stylesheet" href="{raiz}style.css">{pixel()}</head>')


def topo(raiz: str) -> str:
    return (f'<header class="topo-band"><div class="wrap topo"><a class="marca" href="{raiz}"><i>▶</i>Guias/IA</a>'
            f'<small>@{E(CFG["instagram"])}</small></div></header>')


def ticker() -> str:
    itens = "".join(f"<span>{E(t)}</span>" for t in TICKER) * 2
    return f'<div class="ticker" aria-hidden="true"><div class="ticker-track">{itens}</div></div>'


def rodape(raiz: str) -> str:
    return (f'<footer class="rodape"><div class="wrap">© 2026 {E(CFG["marca"])} · Conteúdo gratuito e independente. '
            f'Nomes e marcas pertencem aos respectivos donos. · <a href="{raiz}privacidade/">Privacidade</a></div></footer>')


def oferta(guia: dict) -> str:
    o = CFG["oferta"]
    itens = "".join(f"<li>{E(b)}</li>" for b in o["bullets"])
    msg = o["mensagem_wa"].replace("{guia}", guia["codigo"])
    seg = (f'<a class="btn sec" href="{E(wa_link(o["mensagem_wa2"].replace("{guia}", guia["codigo"])))}" target="_blank" '
           f'rel="noopener">{E(o["cta2"])}</a>' if o.get("cta2") else "")
    return (f'<aside id="oferta" class="oferta oculto"><span class="selo"><span class="dot"></span><b>Próximo passo</b></span>'
            f'<h2>{E(o["titulo"])}</h2><p id="ponte"></p><p>{E(o["texto"])}</p><ul>{itens}</ul>'
            + (f'<a id="cta-oferta" class="btn" href="{E(o["cta_link"])}">{E(o["cta"])} →</a>' if o.get("cta_link") else
               f'<a id="cta-oferta" class="btn" href="{E(wa_link(msg))}" target="_blank" rel="noopener">{ICONE_WA}{E(o["cta"])}</a>')
            + f'{seg}<p class="seguro">O segundo botão abre o WhatsApp com a mensagem pronta</p></aside>')


def pagina_guia(g: dict) -> str:
    raiz = "../"
    return (cabeca(g["titulo"], g["sub"], raiz) + f'<body data-slug="{E(g["slug"])}">' + topo(raiz) +
            '<main><section class="hero"><div class="wrap">'
            f'<span class="selo"><span class="dot"></span><b>Código {E(g["codigo"])}</b>Material gratuito</span>'
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
            '<button id="bt-lead" class="btn" type="submit">Acessar o guia completo →</button>'
            '<div id="erro-lead" class="erro" role="alert"></div><p class="seguro">🔒 Seus dados não são vendidos</p>'
            '</div></form></div></section>' + ticker() +
            '<section class="guia-banda"><div class="wrap"><article id="guia" class="guia oculto"></article>' + oferta(g) +
            '</div></section></main>' + rodape(raiz) +
            f'<script id="cfg" type="application/json">{cfg_publico()}</script><script src="../app.js" defer></script></body></html>')


def pagina_inicio(guias: list[dict]) -> str:
    raiz = "./"
    codigos = json.dumps({g["codigo"].upper(): g["slug"] for g in guias})
    lista = "".join(f'<a href="{E(g["slug"])}/"><b>{E(g["destaque"])}</b><span>{E(g["sub"])}</span><small>{E(g["codigo"])}</small></a>'
                    for g in guias)
    return (cabeca(f'Guias gratuitos de IA | {CFG["marca"]}', "Os materiais dos vídeos: links, comandos e passo a passo.", raiz) +
            '<body>' + topo(raiz) + '<main><section class="hero"><div class="wrap">'
            '<span class="selo"><span class="dot"></span><b>Guias grátis</b>Dos vídeos do Instagram</span>'
            '<h1>Digite o <em>código</em> do vídeo.</h1><p class="sub">Cada vídeo tem um código: é a palavra que você comenta. '
            'Coloca ele aqui pra liberar o material completo: links, comandos e passo a passo.</p>'
            '<form id="form-codigo" class="cartao"><label for="codigo">Código do vídeo</label><div class="codigo">'
            '<input id="codigo" placeholder="EX: APAGAR" autocomplete="off" autocapitalize="characters" required>'
            '<button class="btn" type="submit">Abrir →</button></div><div id="erro-codigo" class="erro" role="alert"></div></form>'
            '</div></section>' + ticker() +
            f'<section class="banda"><div class="wrap"><h2 class="grande">Todos os <span class="lime">guias.</span></h2>'
            f'<div class="ferr">{lista}</div></div></section></main>'
            + rodape(raiz) + f'<script id="codigos" type="application/json">{codigos}</script>'
            f'<script id="cfg" type="application/json">{cfg_publico()}</script><script src="app.js" defer></script></body></html>')


def pagina_privacidade() -> str:
    raiz = "../"
    return (cabeca("Privacidade", "Como tratamos os seus dados.", raiz) + '<body>' + topo(raiz) +
            '<main><section class="banda"><div class="wrap guia"><h1>Privacidade</h1><div class="secao">'
            f'<p>Responsável: {E(CFG["marca"])} (Instagram @{E(CFG["instagram"])}).</p>'
            '<p>Coletamos nome, e-mail e WhatsApp quando você pede um guia, pra te enviar o material e novidades sobre IA e sobre os '
            'nossos serviços. Base legal: o seu consentimento (LGPD art. 7º, I; RGPD art. 6.º, 1, a).</p>'
            '<p>Os dados ficam guardados num servidor seguro (Supabase, UE) e não são vendidos nem cedidos a terceiros.</p>'
            '<p>Você pode pedir acesso, correção ou exclusão a qualquer momento pelo WhatsApp ou pelo Instagram, ou responder '
            '"SAIR" em qualquer mensagem pra não receber mais nada.</p>'
            '<p>Se o Pixel da Meta estiver ativo, ele mede visitas e cadastros pra melhorar os anúncios.</p></div></div></section></main>'
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
    kit = (AQUI / CFG["kit_origem"]).resolve()  # página de venda do Kit Edição com IA (projeto edicao-ia-site)
    if kit.exists():
        (DIST / "kit").mkdir()
        shutil.copy(kit, DIST / "kit" / "index.html")
        if (kit.parent / "estilos").exists():
            shutil.copytree(kit.parent / "estilos", DIST / "kit" / "estilos")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    print(f"ok: {len(guias)} guias → {DIST}")


if __name__ == "__main__":
    main()
