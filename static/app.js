let catalogoDados = [];
let filmeSelecionadoAtual = null;
let usuarioAtual = null;

function mostrarEcra(idEcra) {
    document.querySelectorAll(".view").forEach((view) => {
        view.classList.toggle("active", view.id === idEcra);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function urlMidia(caminho) {
    return `/static/${caminho.split("/").map(encodeURIComponent).join("/")}`;
}

async function requisicaoJson(url, options = {}) {
    const headers = new Headers(options.headers || {});
    if (options.body && !headers.has("Content-Type")) {
        headers.set("Content-Type", "application/json");
    }

    const response = await fetch(url, {
        credentials: "same-origin",
        ...options,
        headers
    });
    const resultado = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(resultado.mensagem || "Não foi possível concluir a solicitação.");
    }
    return resultado;
}

function alternarCarregamento(form, carregando) {
    const botao = form.querySelector('button[type="submit"]');
    if (!botao) return;
    if (carregando) {
        botao.dataset.labelOriginal = botao.textContent;
        botao.disabled = true;
        botao.textContent = "Aguarde…";
    } else {
        botao.disabled = false;
        botao.textContent = botao.dataset.labelOriginal || botao.textContent;
    }
}

function abrirModalDetalhes(filme) {
    filmeSelecionadoAtual = filme;
    document.getElementById("modal-title").textContent = filme.titulo;
    document.getElementById("modal-category").textContent = filme.categoria;
    document.getElementById("modal-desc").textContent = filme.descricao;

    const modal = document.getElementById("movie-modal");
    modal.dataset.returnFocus = document.activeElement?.id || "";
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
    document.getElementById("modal-close").focus();
}

function fecharModal() {
    const modal = document.getElementById("movie-modal");
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");

    const returnFocus = modal.dataset.returnFocus
        ? document.getElementById(modal.dataset.returnFocus)
        : null;
    returnFocus?.focus();
}

function atualizarDestaque(filmes) {
    const hero = document.querySelector(".hero");
    const filme = filmes.find((item) => item.destaque) || filmes[0];
    if (!filme) {
        hero.hidden = true;
        return;
    }

    hero.hidden = false;
    hero.style.setProperty("--hero-image", `url("${urlMidia(filme.imagem)}")`);
    document.getElementById("hero-title").textContent = filme.titulo;
    document.getElementById("hero-desc").textContent = filme.descricao;
    document.getElementById("hero-index-current").textContent = "01";
    document.getElementById("hero-index-total").textContent = String(filmes.length).padStart(2, "0");
    document.getElementById("btn-hero-watch").setAttribute("aria-label", `Ver detalhes de ${filme.titulo}`);
}

function carregarCatalogoFilmes(listaFilmes) {
    const secoes = [
        { id: "row-acao", categoria: "Ação" },
        { id: "row-terror", categoria: "Terror" },
        { id: "row-documentarios", categoria: "Documentário" },
        { id: "row-outros", categoria: "outros" }
    ];
    let totalVisivel = 0;

    secoes.forEach(({ id, categoria }) => {
        const linha = document.getElementById(id);
        const secao = linha.closest(".category-section");
        const filmes = categoria === "outros"
            ? listaFilmes.filter((filme) => !["Ação", "Terror", "Documentário"].includes(filme.categoria))
            : listaFilmes.filter((filme) => filme.categoria === categoria);

        linha.replaceChildren();
        secao.hidden = filmes.length === 0;
        totalVisivel += filmes.length;

        filmes.forEach((filme) => {
            const card = document.createElement("button");
            card.className = "media-card";
            card.type = "button";
            card.setAttribute("aria-label", `Ver detalhes de ${filme.titulo}`);

            const poster = document.createElement("img");
            poster.src = urlMidia(filme.imagem);
            poster.alt = "";
            poster.loading = "lazy";

            const title = document.createElement("span");
            title.className = "card-title";
            title.textContent = filme.titulo;

            const categoryLabel = document.createElement("span");
            categoryLabel.className = "card-category";
            categoryLabel.textContent = filme.categoria;

            card.append(poster, title, categoryLabel);
            card.addEventListener("click", () => abrirModalDetalhes(filme));
            linha.append(card);
        });
    });

    document.getElementById("empty-search").hidden = totalVisivel !== 0;
}

async function carregarCatalogo() {
    const status = document.getElementById("catalog-status");
    const errorPanel = document.getElementById("catalog-error");
    status.hidden = false;
    status.textContent = "Carregando catálogo do banco de dados…";
    errorPanel.hidden = true;

    try {
        const resultado = await requisicaoJson("/api/filmes");
        if (!Array.isArray(resultado.filmes)) {
            throw new Error("O servidor retornou um catálogo inválido.");
        }
        catalogoDados = resultado.filmes;
        atualizarDestaque(catalogoDados);
        carregarCatalogoFilmes(catalogoDados);
        status.hidden = true;
    } catch (error) {
        catalogoDados = [];
        status.hidden = true;
        errorPanel.hidden = false;
        errorPanel.querySelector("p").textContent = error.message
            || "Não foi possível carregar o catálogo agora.";
    }
}

async function entrarNoCatalogo(utilizador = null) {
    usuarioAtual = utilizador;
    document.getElementById("user-greeting").textContent = utilizador
        ? `Olá, ${utilizador.nome}`
        : "Olá, visitante";
    document.getElementById("search-input").value = "";
    mostrarEcra("catalog-view");
    await carregarCatalogo();
}

function abrirPlayer(filme) {
    document.getElementById("player-movie-title").textContent = filme.titulo;
    document.getElementById("player-movie-desc").textContent = filme.descricao;

    const video = document.getElementById("video-player");
    const embed = document.getElementById("video-embed");
    if (filme.video_tipo === "youtube") {
        video.pause();
        video.hidden = true;
        embed.hidden = false;
        embed.title = `Trailer: ${filme.titulo}`;
        embed.src = filme.video_url;
    } else {
        embed.removeAttribute("src");
        embed.hidden = true;
        video.hidden = false;
        document.getElementById("video-source").src = urlMidia(filme.video_url || filme.video);
        video.load();
    }
    mostrarEcra("player-view");
}

function mostrarErro(idElemento, mensagem) {
    document.getElementById(idElemento).textContent = mensagem;
}

function abrirConfirmacaoLogout() {
    const modal = document.getElementById("logout-modal");
    modal.dataset.returnFocus = document.activeElement?.id || "";
    mostrarErro("logout-error", "");
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
    document.getElementById("btn-logout-cancel").focus();
}

function fecharConfirmacaoLogout(devolverFoco = true) {
    const modal = document.getElementById("logout-modal");
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
    mostrarErro("logout-error", "");

    if (devolverFoco && modal.dataset.returnFocus) {
        document.getElementById(modal.dataset.returnFocus)?.focus();
    }
}

async function confirmarLogout() {
    const confirmButton = document.getElementById("btn-logout-confirm");
    const cancelButton = document.getElementById("btn-logout-cancel");
    const error = document.getElementById("logout-error");
    error.textContent = "";
    confirmButton.disabled = true;
    cancelButton.disabled = true;
    confirmButton.textContent = "Encerrando…";

    try {
        await requisicaoJson("/api/logout", { method: "POST", body: "{}" });
        fecharConfirmacaoLogout(false);
        document.getElementById("video-player").pause();
        fecharModal();
        usuarioAtual = null;
        mostrarEcra("login-view");
        document.getElementById("login-email").focus();
    } catch {
        error.textContent = "Não foi possível encerrar a sessão. Tente novamente.";
        confirmButton.focus();
    } finally {
        confirmButton.disabled = false;
        cancelButton.disabled = false;
        confirmButton.textContent = "Sair da conta";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("link-to-register").addEventListener("click", (event) => {
        event.preventDefault();
        mostrarErro("login-error", "");
        mostrarEcra("register-view");
        document.getElementById("reg-nome").focus();
    });

    document.getElementById("link-to-login").addEventListener("click", (event) => {
        event.preventDefault();
        mostrarErro("register-error", "");
        mostrarEcra("login-view");
        document.getElementById("login-email").focus();
    });

    document.getElementById("btn-guest").addEventListener("click", () => entrarNoCatalogo());
    document.getElementById("catalog-retry").addEventListener("click", carregarCatalogo);

    document.getElementById("login-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.currentTarget;
        const error = document.getElementById("login-error");
        error.textContent = "";
        alternarCarregamento(form, true);

        try {
            const resultado = await requisicaoJson("/api/login", {
                method: "POST",
                body: JSON.stringify({
                    email: document.getElementById("login-email").value,
                    senha: document.getElementById("login-senha").value
                })
            });
            await entrarNoCatalogo(resultado.utilizador);
        } catch (requestError) {
            error.textContent = requestError.message;
        } finally {
            alternarCarregamento(form, false);
        }
    });

    document.getElementById("register-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.currentTarget;
        const error = document.getElementById("register-error");
        error.textContent = "";

        const senha = document.getElementById("reg-senha").value;
        const confirmacao = document.getElementById("reg-senha-confirmacao").value;
        if (senha !== confirmacao) {
            error.textContent = "As senhas não coincidem.";
            document.getElementById("reg-senha-confirmacao").focus();
            return;
        }

        alternarCarregamento(form, true);
        try {
            const resultado = await requisicaoJson("/api/registar", {
                method: "POST",
                body: JSON.stringify({
                    nome: document.getElementById("reg-nome").value,
                    email: document.getElementById("reg-email").value,
                    senha
                })
            });
            form.reset();
            await entrarNoCatalogo(resultado.utilizador);
        } catch (requestError) {
            error.textContent = requestError.message;
        } finally {
            alternarCarregamento(form, false);
        }
    });

    document.getElementById("search-input").addEventListener("input", (event) => {
        const termo = event.target.value.trim().toLocaleLowerCase("pt-BR");
        const resultados = catalogoDados.filter((filme) =>
            filme.titulo.toLocaleLowerCase("pt-BR").includes(termo)
            || filme.categoria.toLocaleLowerCase("pt-BR").includes(termo)
            || filme.descricao.toLocaleLowerCase("pt-BR").includes(termo)
        );
        carregarCatalogoFilmes(resultados);
    });

    document.getElementById("btn-logout").addEventListener("click", abrirConfirmacaoLogout);
    document.getElementById("btn-logout-cancel").addEventListener("click", () => fecharConfirmacaoLogout());
    document.getElementById("btn-logout-confirm").addEventListener("click", confirmarLogout);

    document.getElementById("btn-hero-watch").addEventListener("click", () => {
        const filme = catalogoDados.find((item) => item.destaque) || catalogoDados[0];
        if (filme) abrirModalDetalhes(filme);
    });

    document.getElementById("modal-close").addEventListener("click", fecharModal);
    document.getElementById("movie-modal").addEventListener("click", (event) => {
        if (event.target.id === "movie-modal") fecharModal();
    });
    document.getElementById("logout-modal").addEventListener("click", (event) => {
        if (event.target.id === "logout-modal") fecharConfirmacaoLogout();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && document.getElementById("movie-modal").classList.contains("active")) {
            fecharModal();
        }

        const logoutModal = document.getElementById("logout-modal");
        if (!logoutModal.classList.contains("active")) return;

        if (event.key === "Escape") {
            event.preventDefault();
            fecharConfirmacaoLogout();
            return;
        }

        if (event.key === "Tab") {
            const focusable = [...logoutModal.querySelectorAll("button:not(:disabled)")];
            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            if (!logoutModal.contains(document.activeElement)) {
                event.preventDefault();
                (event.shiftKey ? last : first)?.focus();
                return;
            }
            if (event.shiftKey && document.activeElement === first) {
                event.preventDefault();
                last.focus();
            } else if (!event.shiftKey && document.activeElement === last) {
                event.preventDefault();
                first.focus();
            }
        }
    });

    document.getElementById("modal-btn-play").addEventListener("click", () => {
        if (!filmeSelecionadoAtual) return;
        fecharModal();
        abrirPlayer(filmeSelecionadoAtual);
    });

    document.getElementById("btn-back-catalog").addEventListener("click", () => {
        const video = document.getElementById("video-player");
        video.pause();
        const embed = document.getElementById("video-embed");
        embed.removeAttribute("src");
        embed.hidden = true;
        video.hidden = false;
        mostrarEcra("catalog-view");
    });

    requisicaoJson("/api/me")
        .then((resultado) => {
            if (resultado.autenticado && resultado.utilizador) {
                return entrarNoCatalogo(resultado.utilizador);
            }
            return undefined;
        })
        .catch((error) => {
            mostrarErro("login-error", `Não foi possível conectar ao servidor: ${error.message}`);
        });
});
