/* Site de guias — captura (Supabase, só INSERT) + libertação do guia + oferta. Sem dependências. */
(() => {
  const CFG = JSON.parse(document.getElementById("cfg").textContent);
  const $ = (s, el = document) => el.querySelector(s);
  const PAISES = [["+55", "🇧🇷 +55"], ["+351", "🇵🇹 +351"], ["+1", "🇺🇸 +1"], ["+34", "🇪🇸 +34"], ["+44", "🇬🇧 +44"],
    ["+33", "🇫🇷 +33"], ["+39", "🇮🇹 +39"], ["+49", "🇩🇪 +49"], ["+244", "🇦🇴 +244"], ["+258", "🇲🇿 +258"],
    ["+238", "🇨🇻 +238"], ["+54", "🇦🇷 +54"], ["+56", "🇨🇱 +56"], ["+57", "🇨🇴 +57"], ["+52", "🇲🇽 +52"],
    ["+595", "🇵🇾 +595"], ["+598", "🇺🇾 +598"], ["+41", "🇨🇭 +41"], ["+353", "🇮🇪 +353"], ["+31", "🇳🇱 +31"]];
  const CHAVE = "guias_lead_v1";

  const guardar = (k, v) => { try { localStorage.setItem(k, v); } catch (_) { /* modo privado */ } };
  const ler = (k) => { try { return localStorage.getItem(k); } catch (_) { return null; } };
  const utm = () => {
    const q = new URLSearchParams(location.search), o = {};
    ["utm_source", "utm_medium", "utm_campaign", "utm_content"].forEach((k) => { if (q.get(k)) o[k] = q.get(k).slice(0, 110); });
    return o;
  };
  const pixel = (ev, dados) => { if (window.fbq) window.fbq("track", ev, dados || {}); };

  function el(tag, attrs = {}, ...filhos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) {
      if (k === "class") e.className = v; else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v);
    }
    filhos.flat().forEach((f) => e.append(f instanceof Node ? f : document.createTextNode(String(f ?? ""))));
    return e;
  }

  /* ---------- página inicial: código do vídeo ---------- */
  const formCod = $("#form-codigo");
  if (formCod) {
    const codigos = JSON.parse($("#codigos").textContent);
    formCod.addEventListener("submit", (e) => {
      e.preventDefault();
      const c = $("#codigo").value.trim().toUpperCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
      const slug = codigos[c];
      if (!slug) { $("#erro-codigo").textContent = "Código não encontrado. Confira no vídeo (aparece no final) ou na legenda."; return; }
      location.href = `${slug}/${location.search}`;
    });
  }

  /* ---------- hub: lista de espera do clone (mesma tabela guia_leads, guia "clone") ---------- */
  const formEsp = $("#form-espera");
  if (formEsp) {
    const ddi = $("#e-ddi");
    PAISES.forEach(([v, t]) => ddi.append(el("option", { value: v }, t)));
    formEsp.addEventListener("submit", async (e) => {
      e.preventDefault();
      const erro = $("#e-erro"), bt = $("#e-bt");
      erro.textContent = "";
      const nome = $("#e-nome").value.trim(), email = $("#e-email").value.trim().toLowerCase();
      const whatsapp = ddi.value + $("#e-tel").value.replace(/\D/g, "");
      if (nome.length < 2) return (erro.textContent = "Escreva o seu nome.");
      if (!/^\+[0-9]{8,16}$/.test(whatsapp)) return (erro.textContent = "WhatsApp inválido: só números, com DDD.");
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return (erro.textContent = "E-mail inválido.");
      if (!$("#e-consent").checked) return (erro.textContent = "Marque a caixa para entrar na lista.");
      if ($("#e-site").value) return; // honeypot
      bt.disabled = true; bt.textContent = "Entrando…";
      try {
        const r = await fetch(`${CFG.supabase_url}/rest/v1/guia_leads`, {
          method: "POST",
          headers: { apikey: CFG.supabase_key, "Content-Type": "application/json", Prefer: "return=minimal" },
          body: JSON.stringify({ guia: "clone", interesse: "lista_espera_clone", nome, email, whatsapp, consentimento: true,
            utm_source: "hub", ...utm() }),
        });
        if (!r.ok) throw new Error(await r.text());
        guardar(CHAVE, "1");
        pixel("Lead", { content_name: "lista_espera_clone" });
        $("#fe-campos").classList.add("oculto");
        $("#fe-feito").classList.remove("oculto");
      } catch (err) {
        erro.textContent = "Não foi possível entrar na lista agora. Confira os dados e tente de novo.";
        bt.disabled = false; bt.textContent = "Entrar na lista de espera";
      }
    });
  }
  document.querySelectorAll("[data-ev]").forEach((a) =>
    a.addEventListener("click", () => pixel("Contact", { content_name: a.dataset.ev })));

  /* ---------- página de guia ---------- */
  const formLead = $("#form-lead");
  if (!formLead) return;
  const slug = document.body.dataset.slug;
  const sel = $("#ddi");
  PAISES.forEach(([v, t]) => sel.append(el("option", { value: v }, t)));

  async function mostrarGuia() {
    $("#captura").classList.add("oculto");
    const alvo = $("#guia");
    alvo.classList.remove("oculto");
    try {
      const r = await fetch(`../guias/${slug}.json`, { cache: "no-cache" });
      if (!r.ok) throw new Error(r.status);
      renderGuia(await r.json(), alvo);
    } catch (err) {
      alvo.append(el("p", { class: "erro" }, "Não consegui carregar o guia agora. Atualize a página em alguns segundos."));
    }
    alvo.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function bloco(b) {
    switch (b.tipo) {
      case "passos": return el("ol", {}, (b.itens || []).map((i) => el("li", {}, i)));
      case "codigo": {
        const pre = el("pre", {}, b.texto);
        const bt = el("button", { type: "button", onclick: async () => {
          try { await navigator.clipboard.writeText(b.texto); bt.textContent = "Copiado ✓"; } catch (_) { bt.textContent = "Selecione e copie"; }
          setTimeout(() => (bt.textContent = "Copiar"), 1800);
        } }, "Copiar");
        return el("div", { class: "cod" }, b.rotulo ? el("div", { class: "rot" }, b.rotulo) : "", pre, bt);
      }
      case "tabela": return el("div", { class: "tab" }, el("table", {},
        el("thead", {}, el("tr", {}, (b.colunas || []).map((c) => el("th", {}, c)))),
        el("tbody", {}, (b.linhas || []).map((l) => el("tr", {}, l.map((c) => el("td", {}, c)))))));
      case "dica": return el("div", { class: "caixa dica" }, "💡 ", b.texto);
      case "aviso": return el("div", { class: "caixa aviso" }, "⚠️ ", b.texto);
      default: return el("p", {}, b.texto);
    }
  }

  function renderGuia(g, alvo) {
    alvo.append(el("div", { class: "meta" }, el("span", {}, `⏱ ${g.tempo_leitura_min || 5} min de leitura`),
      el("span", {}, `✔ Verificado em ${(g.verificado_em || "").split("-").reverse().join("/")}`)));
    if (g.ferramentas?.length) {
      alvo.append(el("div", { class: "ferr" }, g.ferramentas.map((f) =>
        el("a", { href: f.link, target: "_blank", rel: "noopener" }, el("b", {}, f.nome), el("span", {}, f.para_que), el("small", {}, "abrir ↗")))));
    }
    (g.secoes || []).forEach((s, i) => alvo.append(el("section", { class: "secao entra" },
      el("h2", {}, el("span", { class: "n" }, String(i + 1).padStart(2, "0")), s.titulo), (s.blocos || []).map(bloco))));
    if (g.fontes?.length) {
      alvo.append(el("details", { class: "fontes" }, el("summary", {}, "Fontes oficiais"),
        el("ul", {}, g.fontes.map((u) => el("li", {}, el("a", { href: u, target: "_blank", rel: "noopener" }, u))))));
    }
    const of = $("#oferta");
    if (of) { if (g.proximo_passo) $("#ponte").textContent = g.proximo_passo; of.classList.remove("oculto"); }
  }

  if (ler(CHAVE)) mostrarGuia();

  formLead.addEventListener("submit", async (e) => {
    e.preventDefault();
    const erro = $("#erro-lead"), bt = $("#bt-lead");
    erro.textContent = "";
    const nome = $("#nome").value.trim(), email = $("#email").value.trim().toLowerCase();
    const num = $("#tel").value.replace(/\D/g, ""), whatsapp = sel.value + num;
    if (nome.length < 2) return (erro.textContent = "Escreva seu nome.");
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return (erro.textContent = "E-mail inválido.");
    if (!/^\+[0-9]{8,16}$/.test(whatsapp)) return (erro.textContent = "WhatsApp inválido (só números, com DDD).");
    if (!$("#consent").checked) return (erro.textContent = "Marque a caixa pra receber o material.");
    if ($("#site").value) return; // honeypot
    bt.disabled = true; bt.textContent = "Liberando…";
    try {
      const r = await fetch(`${CFG.supabase_url}/rest/v1/guia_leads`, {
        method: "POST",
        headers: { apikey: CFG.supabase_key, "Content-Type": "application/json", Prefer: "return=minimal" },
        body: JSON.stringify({ guia: slug, nome, email, whatsapp, consentimento: true, ...utm() }),
      });
      if (!r.ok) throw new Error(await r.text());
      guardar(CHAVE, "1");
      pixel("Lead", { content_name: slug });
      mostrarGuia();
    } catch (err) {
      erro.textContent = "Não deu pra enviar agora. Confira os dados e tente de novo.";
      bt.disabled = false; bt.textContent = "Acessar o guia completo";
    }
  });

  const cta = $("#cta-oferta");
  if (cta) cta.addEventListener("click", () => pixel("Contact", { content_name: slug }));
})();
