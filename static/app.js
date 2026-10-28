const catalogoDados = [
    {
        id: 1,
        titulo: "Exterminador do Futuro 7",
        descricao: "O futuro é incerto, mas a luta pela sobrevivência é certa.",
        categoria: "Ação",
        imagem: "images/exterminador_7.webp",
        video: "videos/exterminador_7.mp4"
    },
    {
        id: 2,
        titulo: "A 5ª Onda",
        descricao: "Quando a humanidade enfrenta uma ameaça inesperada, a esperança transforma-se em luta.",
        categoria: "Ação",
        imagem: "images/a-5-onda.webp",
        video: "videos/a-5-onda.mp4"
    },
    {
        id: 3,
        titulo: "Minecraft: O Filme",
        descricao: "Uma aventura emocionante no mundo de blocos e criatividade.",
        categoria: "Comédia",
        imagem: "images/minecraft-o-filme.webp",
        video: "videos/minecraft-o-filme.mp4"
    },
    {
        id: 4,
        titulo: "Terror no Rio",
        descricao: "Uma história de terror que se desenrola nas águas turbulentas de um rio misterioso.",
        categoria: "Terror",
        imagem: "images/terror-rio.webp",
        video: "videos/terror-rio.mp4"
    },
    {
        id: 5,
        titulo: "Maldição da Múmia",
        descricao: "Uma antiga maldição desperta quando um arqueólogo desenterra um sarcófago.",
        categoria: "Terror",
        imagem: "images/maldicao-da-mumia.webp",
        video: "videos/maldicao-da-mumia.mp4"
    },
    {
        id: 6,
        titulo: "Sim Senhor",
        descricao: "Uma história de amor que transcende o tempo e as circunstâncias.",
        categoria: "Romance",
        imagem: "images/sim-senhor.webp",
        video: "videos/sim-senhor.mp4"
    },
    {
        id: 7,
        titulo: "Animais Fantásticos",
        descricao: "Uma aventura de criaturas mágicas e desafios intensos.",
        categoria: "Fantasia",
        imagem: "images/animais-fantasticos.webp",
        video: "videos/animais-fantasticos.mp4"
    }
];

let filmeSelecionadoAtual = null;

function mostrarEcra(idEcra) {
    document.querySelectorAll(".view").forEach((view) => {
        view.classList.toggle("active", view.id === idEcra);
    });
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function abrirModalDetalhes(filme) {
    filmeSelecionadoAtual = filme;
    document.getElementById("modal-title").textContent = filme.titulo;
    document.getElementById("modal-category").textContent = filme.categoria;
    document.getElementById("modal-desc").textContent = filme.descricao;
    const modal = document.getElementById("movie-modal");
    modal.classList.add("active");
    modal.setAttribute("aria-hidden", "false");
    document.getElementById("modal-close").focus();
}

function fecharModal() {
    const modal = document.getElementById("movie-modal");
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
}

function carregarCatalogoFilmes(listaFilmes) {
    const secoes = [
        { id: "row-acao", categoria: "Ação" },
        { id: "row-terror", categoria: "Terror" },
        { id: "row-outros", categoria: "outros" }
    ];
    let totalVisivel = 0;

    secoes.forEach(({ id, categoria }) => {
        const linha = document.getElementById(id);
        const secao = linha.closest(".category-section");
        const filmes = categoria === "outros"
            ? listaFilmes.filter((filme) => !["Ação", "Terror"].includes(filme.categoria))
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
            poster.src = `/static/${filme.imagem}`;
            poster.alt = "";
            poster.loading = "lazy";

            const title = document.createElement("span");
            title.className = "card-title";
            title.textContent = filme.titulo;

            const category = document.createElement("span");
            category.className = "card-category";
            category.textContent = filme.categoria;

            card.append(poster, title, category);
            card.addEventListener("click", () => abrirModalDetalhes(filme));
            linha.append(card);
        });
    });

    document.getElementById("empty-search").hidden = totalVisivel !== 0;
}

function entrarComoVisitante() {
    document.getElementById("user-greeting").textContent = "Olá, visitante";
    carregarCatalogoFilmes(catalogoDados);
    mostrarEcra("catalog-view");
}

function abrirPlayer(filme) {
    document.getElementById("player-movie-title").textContent = filme.titulo;
    document.getElementById("player-movie-desc").textContent = filme.descricao;

    const video = document.getElementById("video-player");
    const source = document.getElementById("video-source");
    source.src = `/static/${filme.video}`;
    video.load();
    mostrarEcra("player-view");
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("link-to-register").addEventListener("click", (event) => {
        event.preventDefault();
        mostrarEcra("register-view");
    });

    document.getElementById("link-to-login").addEventListener("click", (event) => {
        event.preventDefault();
        mostrarEcra("login-view");
    });

    document.getElementById("btn-guest").addEventListener("click", entrarComoVisitante);

    document.getElementById("login-form").addEventListener("submit", (event) => {
        event.preventDefault();
        document.getElementById("login-error").textContent =
            "A autenticação ainda não está conectada nesta pré-visualização. Explore como visitante.";
    });

    document.getElementById("register-form").addEventListener("submit", (event) => {
        event.preventDefault();
        document.getElementById("register-error").textContent =
            "O cadastro ficará disponível quando o servidor de autenticação estiver conectado.";
    });

    document.getElementById("search-input").addEventListener("input", (event) => {
        const termo = event.target.value.trim().toLocaleLowerCase("pt-BR");
        const resultados = catalogoDados.filter((filme) =>
            filme.titulo.toLocaleLowerCase("pt-BR").includes(termo)
            || filme.categoria.toLocaleLowerCase("pt-BR").includes(termo)
        );
        carregarCatalogoFilmes(resultados);
    });

    document.getElementById("btn-logout").addEventListener("click", () => {
        document.getElementById("search-input").value = "";
        fecharModal();
        mostrarEcra("login-view");
    });

    document.getElementById("btn-hero-watch").addEventListener("click", () => {
        abrirModalDetalhes(catalogoDados[0]);
    });

    document.getElementById("modal-close").addEventListener("click", fecharModal);
    document.getElementById("movie-modal").addEventListener("click", (event) => {
        if (event.target.id === "movie-modal") fecharModal();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") fecharModal();
    });

    document.getElementById("modal-btn-play").addEventListener("click", () => {
        if (!filmeSelecionadoAtual) return;
        fecharModal();
        abrirPlayer(filmeSelecionadoAtual);
    });

    document.getElementById("btn-back-catalog").addEventListener("click", () => {
        const video = document.getElementById("video-player");
        video.pause();
        mostrarEcra("catalog-view");
    });
});
