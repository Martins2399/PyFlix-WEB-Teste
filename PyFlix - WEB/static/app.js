// Garantir que o código corre apenas após o HTML carregar por completo
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

    // Processo de Registo
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

    // Processo de Login (Corrigido e Seguro)
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
            erroEl.textContent = resultado.mensagem;
        }
    } catch (erro) {
        erroEl.textContent = "Erro de conexão com o servidor.";
    }
});

function entrarNoCatalogo(utilizador) {
    document.getElementById('user-greeting').textContent = `Olá, ${utilizador.nome}`;
    carregarCatalogoFilmes(catalogoDados);
    mostrarEcra('catalog-view');
}

// Renderizar o catálogo dinamicamente
function carregarCatalogoFilmes(listaFilmes) {
    const rowAcao = document.getElementById('row-acao');
    const rowTerror = document.getElementById('row-terror');
    const rowOutros = document.getElementById('row-outros');

    if (!rowAcao) return;

    rowAcao.innerHTML = '';
    rowTerror.innerHTML = '';
    rowOutros.innerHTML = '';

    listaFilmes.forEach(filme => {
        const card = document.createElement('div');
        card.className = 'media-card';
        card.innerHTML = `
            <img src="/static/${filme.imagem}" alt="${filme.titulo}" onerror="this.src='https://picsum.photos/210/310?random=${filme.id}'">
            <div class="card-title">${filme.titulo}</div>
        `;

        // Variável global para armazenar o filme selecionado atualmente
let filmeSelecionadoAtual = null;

// Modificação: Ao clicar no card, abre o Modal de Detalhes em vez do vídeo direto
function abrirModalDetalhes(filme) {
    filmeSelecionadoAtual = filme;
    document.getElementById('modal-title').textContent = filme.titulo;
    document.getElementById('modal-category').textContent = filme.categoria;
    document.getElementById('modal-desc').textContent = filme.descricao;
    
    document.getElementById('movie-modal').classList.add('active');
}

// Fechar o Modal
document.getElementById('modal-close')?.addEventListener('click', () => {
    document.getElementById('movie-modal').classList.remove('active');
});

// Botão de Assistir dentro do Modal
document.getElementById('modal-btn-play')?.addEventListener('click', () => {
    document.getElementById('movie-modal').classList.remove('active');
    if (filmeSelecionadoAtual) {
        abrirPlayerDireto(filmeSelecionadoAtual);
    }
});

// Função para abrir o reprodutor de vídeo
function abrirPlayerDireto(filme) {
    document.getElementById('player-movie-title').textContent = filme.titulo;
    document.getElementById('player-movie-desc').textContent = filme.descricao;
    
    const videoPlayer = document.getElementById('video-player');
    const videoSource = document.getElementById('video-source');
    
    videoSource.src = `/static/${filme.video}`;
    videoPlayer.load();
    
    mostrarEcra('player-view');
}
    });
}

// Funcionalidade da Barra de Pesquisa em Tempo Real corrigida
document.getElementById('search-input')?.addEventListener('input', (e) => {
    const termo = e.target.value.toLowerCase().trim();
    const filmesFiltrados = catalogoDados.filter(filme => 
        filme.titulo.toLowerCase().includes(termo) || 
        filme.categoria.toLowerCase().includes(termo)
    );
    // Renderizar o catálogo dinamicamente e ocultar categorias vazias
function carregarCatalogoFilmes(listaFilmes) {
    const rowAcao = document.getElementById('row-acao');
    const rowTerror = document.getElementById('row-terror');
    const rowOutros = document.getElementById('row-outros');

    // Obtém o elemento pai (.category-section) de cada linha para poder ocultá-lo se estiver vazio
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

        // Distribui os filmes pelas categorias e conta quantos existem em cada uma
        if (filme.categoria === "Ação") {
            rowAcao.appendChild(card);
            countAcao++;
        } else if (filme.categoria === "Terror") {
            rowTerror.appendChild(card);
            countTerror++;
        } else {
            rowOutros.appendChild(card);
            countOutros++;
        }
    });

    // Oculta a secção inteira (incluindo o subtítulo) se não houver filmes correspondentes
    if (secaoAcao) secaoAcao.style.display = countAcao > 0 ? 'block' : 'none';
    if (secaoTerror) secaoTerror.style.display = countTerror > 0 ? 'block' : 'none';
    if (secaoOutros) secaoOutros.style.display = countOutros > 0 ? 'block' : 'none';
}

// Funcionalidade da Barra de Pesquisa em Tempo Real
document.getElementById('search-input')?.addEventListener('input', (e) => {
    const termo = e.target.value.toLowerCase().trim();
    const filmesFiltrados = catalogoDados.filter(filme => 
        filme.titulo.toLowerCase().includes(termo) || 
        filme.categoria.toLowerCase().includes(termo)
    );
    carregarCatalogoFilmes(filmesFiltrados);
});
});

// Abrir Player de Vídeo e forçar o carregamento correto
function abrirPlayer(filme) {
    document.getElementById('player-movie-title').textContent = filme.titulo;
    document.getElementById('player-movie-desc').textContent = filme.descricao;
    
    const videoPlayer = document.getElementById('video-player');
    const videoSource = document.getElementById('video-source');
    
    // Define o caminho correto servido pela pasta static do Flask
    videoSource.src = `/static/${filme.video}`;
    videoPlayer.load(); // Força o elemento a carregar o novo vídeo
    
    mostrarEcra('player-view');
}

// Botões de navegação secundários
document.getElementById('btn-back-catalog')?.addEventListener('click', () => {
    const videoPlayer = document.getElementById('video-player');
    videoPlayer.pause();
    mostrarEcra('catalog-view');
});

document.getElementById('btn-logout')?.addEventListener('click', () => {
    mostrarEcra('login-view');
});

document.getElementById('btn-hero-watch')?.addEventListener('click', () => {
    abrirPlayer(catalogoDados[0]);
});

// Efeito de scroll na Navbar
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (navbar && window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else if (navbar) {
        navbar.classList.remove('scrolled');
    }
});