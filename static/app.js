document.addEventListener("DOMContentLoaded", () => {
    let filmesData = [];
    let destaques = [];
    let currentHeroIndex = 0;
    let selectedFilm = null;

    // Elementos DOM de Telas
    const views = {
        login: document.getElementById("login-view"),
        register: document.getElementById("register-view"),
        catalog: document.getElementById("catalog-view"),
        player: document.getElementById("player-view")
    };

    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");
    const loginError = document.getElementById("login-error");
    const registerError = document.getElementById("register-error");

    const heroSection = document.getElementById("hero-section");
    const heroTitle = document.getElementById("hero-title");
    const heroDesc = document.getElementById("hero-desc");
    const heroIndexCurrent = document.getElementById("hero-index-current");
    const heroIndexTotal = document.getElementById("hero-index-total");
    const btnHeroWatch = document.getElementById("btn-hero-watch");
    const heroPrev = document.getElementById("hero-prev");
    const heroNext = document.getElementById("hero-next");

    const rows = {
        acao: document.getElementById("row-acao"),
        terror: document.getElementById("row-terror"),
        documentarios: document.getElementById("row-documentarios"),
        outros: document.getElementById("row-outros")
    };

    const searchInput = document.getElementById("search-input");
    const emptySearch = document.getElementById("empty-search");
    const userGreeting = document.getElementById("user-greeting");
    const btnLogout = document.getElementById("btn-logout");

    const movieModal = document.getElementById("movie-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalCategory = document.getElementById("modal-category");
    const modalDesc = document.getElementById("modal-desc");
    const modalBtnPlay = document.getElementById("modal-btn-play");
    const modalClose = document.getElementById("modal-close");

    const logoutModal = document.getElementById("logout-modal");
    const btnLogoutConfirm = document.getElementById("btn-logout-confirm");
    const btnLogoutCancel = document.getElementById("btn-logout-cancel");

    const btnBackCatalog = document.getElementById("btn-back-catalog");
    const videoPlayer = document.getElementById("video-player");
    const videoSource = document.getElementById("video-source");
    const videoEmbed = document.getElementById("video-embed");
    const playerMovieTitle = document.getElementById("player-movie-title");
    const playerMovieDesc = document.getElementById("player-movie-desc");

    // Função de Troca de Telas
    function switchView(target) {
        Object.values(views).forEach(v => v.classList.remove("active"));
        if (views[target]) {
            views[target].classList.add("active");
            window.scrollTo(0, 0);
        }
    }

    // Verificar Sessão Atual
    async function checkSession() {
        try {
            const res = await fetch("/api/me");
            const data = await res.json();
            if (data.autenticado && data.utilizador) {
                userGreeting.textContent = `Olá, ${data.utilizador.nome}`;
            } else {
                userGreeting.textContent = "Olá, visitante";
            }
        } catch {
            userGreeting.textContent = "Olá, visitante";
        }
    }

    // Buscar Filmes do Catálogo
    async function fetchFilmes() {
        try {
            const res = await fetch("/api/filmes");
            const data = await res.json();
            filmesData = data.filmes || [];
            destaques = filmesData.filter(f => f.destaque);
            if (destaques.length === 0 && filmesData.length > 0) destaques = [filmesData[0]];

            renderHero();
            renderCatalog(filmesData);
        } catch {
            const errEl = document.getElementById("catalog-error");
            if (errEl) errEl.hidden = false;
        }
    }

    // Renderizar Hero (Destaque)
    function renderHero() {
        if (!destaques.length) return;
        const current = destaques[currentHeroIndex];
        if (heroTitle) heroTitle.textContent = current.titulo;
        if (heroDesc) heroDesc.textContent = current.descricao;
        if (heroSection) heroSection.style.backgroundImage = `url('/static/${current.imagem}')`;
        if (heroIndexCurrent) heroIndexCurrent.textContent = String(currentHeroIndex + 1).padStart(2, '0');
        if (heroIndexTotal) heroIndexTotal.textContent = String(destaques.length).padStart(2, '0');
    }

    if (heroPrev && heroNext) {
        heroPrev.addEventListener("click", () => {
            currentHeroIndex = (currentHeroIndex - 1 + destaques.length) % destaques.length;
            renderHero();
        });
        heroNext.addEventListener("click", () => {
            currentHeroIndex = (currentHeroIndex + 1) % destaques.length;
            renderHero();
        });
    }

    if (btnHeroWatch) {
        btnHeroWatch.addEventListener("click", () => {
            if (destaques[currentHeroIndex]) playMovie(destaques[currentHeroIndex]);
        });
    }

    // Renderizar Catálogo nas Fileiras
    function renderCatalog(filmes) {
        Object.values(rows).forEach(r => { if (r) r.innerHTML = ""; });

        let hasVisible = false;
        filmes.forEach(filme => {
            const card = document.createElement("div");
            card.className = "card";
            card.innerHTML = `
                <img src="/static/${filme.imagem}" alt="${filme.titulo}" loading="lazy">
                <div class="card-info">
                    <div class="card-title">${filme.titulo}</div>
                </div>
            `;
            card.addEventListener("click", () => openModal(filme));

            const cat = (filme.categoria || "").toLowerCase();
            if (cat.includes("ação") || cat.includes("acao")) {
                if (rows.acao) rows.acao.appendChild(card);
            } else if (cat.includes("terror")) {
                if (rows.terror) rows.terror.appendChild(card);
            } else if (cat.includes("documentário") || cat.includes("documentario")) {
                if (rows.documentarios) rows.documentarios.appendChild(card);
            } else {
                if (rows.outros) rows.outros.appendChild(card);
            }

            hasVisible = true;
        });

        if (emptySearch) emptySearch.hidden = hasVisible;
    }

    // Rolagem Lateral das Fileiras (< e >)
    document.querySelectorAll('.row-container').forEach(container => {
        const row = container.querySelector('.cards-row');
        const leftBtn = container.querySelector('.scroll-left');
        const rightBtn = container.querySelector('.scroll-right');

        if (leftBtn && rightBtn && row) {
            leftBtn.addEventListener('click', () => row.scrollBy({ left: -500, behavior: 'smooth' }));
            rightBtn.addEventListener('click', () => row.scrollBy({ left: 500, behavior: 'smooth' }));
        }
    });

    // Barra de Pesquisa
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const term = e.target.value.toLowerCase().trim();
            const filtered = filmesData.filter(f => 
                f.titulo.toLowerCase().includes(term) || 
                f.categoria.toLowerCase().includes(term) ||
                f.descricao.toLowerCase().includes(term)
            );
            renderCatalog(filtered);
        });
    }

    // Modal de Detalhes
    function openModal(filme) {
        selectedFilm = filme;
        if (modalTitle) modalTitle.textContent = filme.titulo;
        if (modalCategory) modalCategory.textContent = filme.categoria;
        if (modalDesc) modalDesc.textContent = filme.descricao;
        if (movieModal) {
            movieModal.classList.add("active");
            movieModal.setAttribute("aria-hidden", "false");
        }
    }

    if (modalClose) {
        modalClose.addEventListener("click", () => {
            movieModal.classList.remove("active");
            movieModal.setAttribute("aria-hidden", "true");
        });
    }

    if (modalBtnPlay) {
        modalBtnPlay.addEventListener("click", () => {
            movieModal.classList.remove("active");
            if (selectedFilm) playMovie(selectedFilm);
        });
    }

    // Player de Vídeo
    function playMovie(filme) {
        if (playerMovieTitle) playerMovieTitle.textContent = filme.titulo;
        if (playerMovieDesc) playerMovieDesc.textContent = filme.descricao;

        if (filme.video_tipo === "youtube") {
            if (videoPlayer) {
                videoPlayer.hidden = true;
                videoPlayer.pause();
            }
            if (videoEmbed) {
                videoEmbed.hidden = false;
                videoEmbed.src = filme.video_url;
            }
        } else {
            if (videoEmbed) {
                videoEmbed.hidden = true;
                videoEmbed.src = "";
            }
            if (videoPlayer) {
                videoPlayer.hidden = false;
                if (videoSource) videoSource.src = `/static/${filme.video}`;
                videoPlayer.load();
                videoPlayer.play().catch(() => {});
            }
        }

        switchView("player");
    }

    if (btnBackCatalog) {
        btnBackCatalog.addEventListener("click", () => {
            if (videoPlayer) videoPlayer.pause();
            if (videoEmbed) videoEmbed.src = "";
            switchView("catalog");
        });
    }

    // Formulário de Login
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (loginError) loginError.textContent = "";
            const email = document.getElementById("login-email").value;
            const senha = document.getElementById("login-senha").value;

            try {
                const res = await fetch("/api/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, senha })
                });
                const data = await res.json();
                if (res.ok) {
                    if (userGreeting) userGreeting.textContent = `Olá, ${data.utilizador.nome}`;
                    switchView("catalog");
                } else {
                    if (loginError) loginError.textContent = data.mensagem || "E-mail ou senha incorretos.";
                }
            } catch {
                if (loginError) loginError.textContent = "Erro de conexão com o servidor.";
            }
        });
    }

    // Formulário de Cadastro
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            if (registerError) registerError.textContent = "";
            const nome = document.getElementById("reg-nome").value;
            const email = document.getElementById("reg-email").value;
            const senha = document.getElementById("reg-senha").value;
            const confirmacao = document.getElementById("reg-senha-confirmacao").value;

            if (senha !== confirmacao) {
                if (registerError) registerError.textContent = "As senhas não coincidem.";
                return;
            }

            try {
                const res = await fetch("/api/registar", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ nome, email, senha })
                });
                const data = await res.json();
                if (res.ok) {
                    if (userGreeting) userGreeting.textContent = `Olá, ${data.utilizador.nome}`;
                    switchView("catalog");
                } else {
                    if (registerError) registerError.textContent = data.mensagem || "Erro ao criar conta.";
                }
            } catch {
                if (registerError) registerError.textContent = "Erro de conexão com o servidor.";
            }
        });
    }

    // Botões de Alternância de Telas (Visitante, Criar Conta, Voltar)
    const btnGuest = document.getElementById("btn-guest");
    if (btnGuest) {
        btnGuest.addEventListener("click", () => {
            if (userGreeting) userGreeting.textContent = "Olá, visitante";
            switchView("catalog");
        });
    }

    const linkToRegister = document.getElementById("link-to-register");
    if (linkToRegister) {
        linkToRegister.addEventListener("click", (e) => {
            e.preventDefault();
            switchView("register");
        });
    }

    const linkToLogin = document.getElementById("link-to-login");
    if (linkToLogin) {
    linkToLogin.addEventListener("click", (e) => {
        e.preventDefault();
        switchView("login");
    });
}

    // Logout
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            if (logoutModal) logoutModal.classList.add("active");
        });
    }
    if (btnLogoutCancel) {
        btnLogoutCancel.addEventListener("click", () => {
            if (logoutModal) logoutModal.classList.remove("active");
        });
    }
    if (btnLogoutConfirm) {
        btnLogoutConfirm.addEventListener("click", async () => {
            await fetch("/api/logout", { method: "POST" });
            if (logoutModal) logoutModal.classList.remove("active");
            if (userGreeting) userGreeting.textContent = "Olá, visitante";
            switchView("login");
        });
    }

    // Inicialização da Aplicação
    checkSession();
    fetchFilmes();
});