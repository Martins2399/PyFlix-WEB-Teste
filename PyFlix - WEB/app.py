// Catálogo de filmes expandido com novas categorias, imagens e trailers
const catalogoDados = [
    { id: 1, titulo: "Exterminador do Futuro 7", descricao: "O futuro é incerto, mas a luta pela sobrevivência é certa.", categoria: "Ação", imagem: "images/exterminador_7.webp", video: "videos/exterminador_7.mp4" },
    { id: 2, titulo: "A 5° Onda", descricao: "Quando a humanidade enfrenta uma ameaça inesperada, a esperança transforma-se em luta.", categoria: "Ação", imagem: "images/a-5-onda.webp", video: "videos/a-5-onda.mp4" },
    { id: 3, titulo: "Minecraft: O Filme", descricao: "Uma aventura emocionante no mundo de blocos e criatividade.", categoria: "Comédia", imagem: "images/minecraft-o-filme.webp", video: "videos/minecraft-o-filme.mp4" },
    { id: 4, titulo: "Terror no rio", descricao: "Uma história de terror que se desenrola nas águas turbulentas de um rio misterioso.", categoria: "Terror", imagem: "images/terror-rio.webp", video: "videos/terror-rio.mp4" },
    { id: 5, titulo: "Maldição da múmia", descricao: "Uma antiga maldição desata-se quando um arqueólogo desenterra um sarcófago.", categoria: "Terror", imagem: "images/maldicao-da-mumia.webp", video: "videos/maldicao-da-mumia.mp4" },
    { id: 6, titulo: "Sim senhor", descricao: "Uma história de amor que transcende o tempo e as circunstâncias.", categoria: "Romance", imagem: "images/sim-senhor.webp", video: "videos/sim-senhor.mp4" },
    { id: 7, titulo: "Animais Fantásticos", descricao: "A continuação da saga de animais mágicos e desafios intensos.", categoria: "Ficção Científica", imagem: "images/animais-fantasticos.webp", video: "videos/animais-fantasticos.mp4" },
    // --- NOVOS FILMES ADICIONADOS EM CATEGORIAS DIFERENTES ---
    { id: 8, titulo: "O Segredo da Natureza", descricao: "Um documentário fascinante sobre os ecossistemas mais escondidos do planeta Terra.", categoria: "Documentário", imagem: "images/documentario.webp", video: "videos/documentario.mp4" },
    { id: 9, titulo: "Aventura na Floresta Mágica", descricao: "Uma animação cativante sobre amizade e coragem para salvar a floresta encantada.", categoria: "Animação", imagem: "images/animacao.webp", video: "videos/animacao.mp4" },
    { id: 10, titulo: "Silêncio Mortal", descricao: "Um suspense psicológico onde cada som pode ser o último para os sobreviventes.", categoria: "Suspense", imagem: "images/suspense.webp", video: "videos/suspense.mp4" }
];

// Variável global para armazenar o filme selecionado atualmente no modal
let filmeSelecionadoAtual = null;

// Alternar entre ecrãs (Views)
function mostrarEcra(idEcra) {
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    document.getElementById(idEcra).classList.add('active');
}

// Executar após o carregamento total do DOM
document.addEventListener('DOMContentLoaded', () => {

    // Navegação Login / Registo
    document.getElementById('link-to-register')?.addEventListener('click', (e) => {
        e.preventDefault();
        mostrarEcra('register-view');
    });

    document.getElementById('link-to-login')?.addEventListener('click', (e) => {
        e.preventDefault();
        mostrarEcra('login-view');
    });

    // Registo via API Flask
    document.getElementById('register-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const nome = document.getElementById('reg-nome').value;
        const email = document.getElementById('reg-email').value;
        const senha = document.getElementById('reg-senha').value;
        const erroEl = document.getElementById('register-error');

        try {
            const resposta = await fetch('/api/registar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome, email, senha })
            });
            const resultado = await resposta.json();

            if (resposta.ok) {
                alert("Conta criada com sucesso! Faça login.");
                mostrarEcra('login-view');
            } else {
                erroEl.textContent = resultado.mensagem || "Erro ao registar.";
            }
        } catch (erro) {
            erroEl.textContent = "Erro de conexão com o servidor.";
        }
    });

    // Login via API Flask
    document.getElementById('login-form')?.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const senha = document.getElementById('login-senha').value;
        const erroEl = document.getElementById('login-error');

        try {
            const resposta = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, senha })
            });
            const resultado = await resposta.json();

            if (resposta.ok) {
                erroEl.textContent = "";
                entrarNoCatalogo(resultado.utilizador);
            } else {
                erroEl.textContent = resultado.mensagem || "E-mail ou palavra-passe incorretos.";
            }
        } catch (erro) {
            erroEl.textContent = "Erro de conexão com o servidor.";
        }
    });

    // Fechar o Modal de Detalhes
    document.getElementById('modal-close')?.addEventListener('click', () => {
        document.getElementById('movie-modal')?.classList.remove('active');
    });

    // Botão de Assistir dentro do Modal de Detalhes
    document.getElementById('modal-btn-play')?.addEventListener('click', () => {
        document.getElementById('movie-modal')?.classList.remove('active');
        if (filmeSelecionadoAtual) {
            abrirPlayerDireto(filmeSelecionadoAtual);
        }
    });

    // Funcionalidade da Barra de Pesquisa em Tempo Real
    document.getElementById('search-input')?.addEventListener('input', (e) => {
        const termo = e.target.value.toLowerCase().trim();
        const filmesFiltrados = catalogoDados.filter(filme => 
            filme.titulo.toLowerCase().includes(termo) || 
            filme.categoria.toLowerCase().includes(termo)
        );
        carregarCatalogoFilmes(filmesFiltrados);
    });

    // Botão de Voltar ao Catálogo no Player
    document.getElementById('btn-back-catalog')?.addEventListener('click', () => {
        const videoPlayer = document.getElementById('video-player');
        videoPlayer.pause();
        mostrarEcra('catalog-view');
    });

    // Botão Sair / Logout com mensagem de confirmação
    document.getElementById('btn-logout')?.addEventListener('click', () => {
        const confirmarSaida = confirm("Realmente deseja sair ?");
        if (confirmarSaida) {
            mostrarEcra('login-view');
        }
    });

    // Botão Assistir Trailer no Destaque da Semana
    document.getElementById('btn-hero-watch')?.addEventListener('click', () => {
        abrirModalDetalhes(catalogoDados[0]);
    });
});

// Entrar no Catálogo após login
function entrarNoCatalogo(utilizador) {
    document.getElementById('user-greeting').textContent = `Olá, ${utilizador.nome}`;
    carregarCatalogoFilmes(catalogoDados);
    mostrarEcra('catalog-view');
}

// Renderizar o catálogo dinamicamente e suportar novas categorias/linhas
function carregarCatalogoFilmes(listaFilmes) {
    const rowAcao = document.getElementById('row-acao');
    const rowTerror = document.getElementById('row-terror');
    const rowOutros = document.getElementById('row-outros');

    const secaoAcao = rowAcao?.closest('.category-section');
    const secaoTerror = rowTerror?.closest('.category-section');
    const secaoOutros = rowOutros?.closest('.category-section');

    if (!rowAcao) return;

    rowAcao.innerHTML = '';
    rowTerror.innerHTML = '';
    rowOutros.innerHTML = '';

    let countAcao = 0;
    let countTerror = 0;
    let countOutros = 0;

    listaFilmes.forEach(filme => {
        const card = document.createElement('div');
        card.className = 'media-card';
        card.innerHTML = `
            <img src="/static/${filme.imagem}" alt="${filme.titulo}" onerror="this.src='https://picsum.photos/210/310?random=${filme.id}'">
            <div class="card-title">${filme.titulo}</div>
        `;

        card.addEventListener('click', () => abrirModalDetalhes(filme));

        // Direcciona os filmes para as linhas correspondentes
        if (filme.categoria === "Ação") {
            rowAcao.appendChild(card);
            countAcao++;
        } else if (filme.categoria === "Terror") {
            rowTerror.appendChild(card);
            countTerror++;
        } else {
            // As novas categorias (Documentário, Animação, Suspense, etc.) vão para a secção de Outros ou podem ser agrupadas
            rowOutros.appendChild(card);
            countOutros++;
        }
    });

    // Oculta a secção inteira se não houver filmes correspondentes na pesquisa
    if (secaoAcao) secaoAcao.style.display = countAcao > 0 ? 'block' : 'none';
    if (secaoTerror) secaoTerror.style.display = countTerror > 0 ? 'block' : 'none';
    if (secaoOutros) secaoOutros.style.display = countOutros > 0 ? 'block' : 'none';
}

// Abrir Modal de Detalhes
function abrirModalDetalhes(filme) {
    filmeSelecionadoAtual = filme;
    document.getElementById('modal-title').textContent = filme.titulo;
    document.getElementById('modal-category').textContent = filme.categoria;
    document.getElementById('modal-desc').textContent = filme.descricao;
    
    document.getElementById('movie-modal')?.classList.add('active');
}

// Função para abrir diretamente o reprodutor de vídeo
function abrirPlayerDireto(filme) {
    document.getElementById('player-movie-title').textContent = filme.titulo;
    document.getElementById('player-movie-desc').textContent = filme.descricao;
    
    const videoPlayer = document.getElementById('video-player');
    const videoSource = document.getElementById('video-source');
    
    videoSource.src = `/static/${filme.video}`;
    videoPlayer.load();
    
    mostrarEcra('player-view');
}

// Efeito de scroll na Navbar
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (navbar && window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else if (navbar) {
        navbar.classList.remove('scrolled');
    }
});