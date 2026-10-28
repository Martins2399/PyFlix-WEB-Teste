# PyFlix Web

PyFlix é uma aplicação web com cadastro e login reais, catálogo carregado do banco de dados e reprodução dos vídeos de demonstração. A interface continua sendo HTML/CSS/JavaScript; o Flask entrega a página e a API.

## O que já funciona

- Cadastro com nome, e-mail, senha e confirmação de senha.
- Validação no navegador e no servidor; e-mails são normalizados e não podem se repetir.
- Senhas novas são armazenadas com hash. Contas antigas com senha em texto puro são convertidas para hash no próximo login bem-sucedido.
- Sessão de login segura e opção de sair.
- Exploração do catálogo sem conta.
- Busca por título, descrição e categoria.
- Filmes, descrições, categorias e caminhos de imagem/vídeo vêm da tabela `filmes`, não de uma lista fixa no JavaScript.
- Reprodução dos vídeos incluídos no projeto.
- Catálogo inicial adicionado ao banco somente se a tabela estiver vazia e os arquivos de mídia correspondentes existirem.

## Executar no Replit

O workflow **Start PyFlix** executa o servidor Flask na porta 5000 e abre o site na visualização Web.

O projeto usa `SESSION_SECRET` para assinar as sessões. No Replit, mantenha esse valor em Secrets; nunca o coloque no código ou no GitHub. Em desenvolvimento, o banco SQLite padrão fica em `PyFlix - WEB/usuarios.db`. Se `DATABASE_URL` estiver configurada, o app usa PostgreSQL.

Para executar manualmente:

```bash
./.pythonlibs/bin/python server.py
```

## Banco de dados e arquivos

- `usuarios`: contas e hashes de senha.
- `filmes`: título, descrição, categoria, caminhos relativos dos arquivos, ordem, destaque e estado ativo.
- Imagens e vídeos ficam em `static/images/` e `static/videos/`. O banco guarda somente caminhos relativos, não os arquivos de vídeo.
- Em produção, o servidor exige `DATABASE_URL` para evitar salvar contas em um disco temporário. Não use SQLite em hospedagem com sistema de arquivos efêmero.

O banco SQLite local foi mantido no computador e removido do rastreamento do Git. A tabela de usuários estava sem contas quando preparei este projeto; o app agora preenche a tabela de filmes com os sete vídeos de demonstração. O `.gitignore` evita adicionar o banco novamente. Se versões anteriores do banco com contas já tiverem sido enviadas a um repositório remoto, apagar o arquivo em um commit novo não remove esses dados do histórico.

## Testar

```bash
./.pythonlibs/bin/python -m unittest discover -s tests -v
```

Os testes usam bancos SQLite temporários e não alteram o banco local.

Rotas principais:

- `GET /api/filmes` — catálogo público.
- `POST /api/registar` — criar conta e iniciar sessão.
- `POST /api/login` — autenticar.
- `GET /api/me` — consultar a sessão atual.
- `POST /api/logout` — encerrar sessão.
- `GET /health` — verificação do servidor e do banco.

## Roteiro de prática do áudio

1. **Visualizar a página web:** o HTML e o CSS formam a interface; a visualização usa o workflow do Flask na porta 5000.
2. **Usar vídeos pequenos:** os trailers de demonstração ficam nos arquivos estáticos do projeto. Para produção, evite colocar vídeos grandes no repositório; use armazenamento de mídia apropriado.
3. **Ligar tela e banco:** a página busca `/api/filmes`. O Flask lê os registros e só permite caminhos de mídia dentro das pastas estáticas previstas.
4. **Praticar cadastro e login:** crie uma conta, saia, entre novamente, teste senha incorreta e tente cadastrar o mesmo e-mail.
5. **Executar os testes:** os testes exercitam cadastro, hash, sessão, login, logout, migração de senha antiga e catálogo.
6. **Praticar GitHub:** revise os arquivos antes de enviar. O banco local e Secrets não devem entrar no repositório. O projeto não foi enviado ao GitHub por este trabalho.
7. **Praticar Render:** `render.yaml` descreve um serviço web Flask e um PostgreSQL de demonstração. Conecte o repositório manualmente no Render para praticar a criação dos recursos.
8. **Migrar SQLite para PostgreSQL:** configure `DATABASE_URL` para o banco de destino, rode primeiro a prévia abaixo e só então use `--apply`:

   ```bash
   ./.pythonlibs/bin/python scripts/migrate_sqlite_to_postgres.py
   ./.pythonlibs/bin/python scripts/migrate_sqlite_to_postgres.py --apply
   ```

   A migração não apaga a origem, converte senhas antigas para hash e ignora contas e filmes que já existam no destino. Faça uma cópia de segurança antes de migrar dados reais.

### Limites importantes do plano gratuito do Render

O arquivo `render.yaml` usa os planos gratuitos para permitir a prática sem configurar cobrança. Conforme a documentação atual do Render, o PostgreSQL gratuito tem limite de 1 GB, não oferece backups e expira 30 dias após a criação; após o período de carência, os dados são apagados. O serviço web gratuito também pode dormir quando fica ocioso e perde arquivos locais em reinícios. Use esses recursos somente para testes. Para manter contas e dados reais, escolha um banco persistente sem esse prazo e configure backups.

## Implantação

O projeto inclui `render.yaml`, `requirements.txt`, comando Gunicorn e rota de saúde para a prática de publicação. Nenhum serviço foi criado, nenhum banco externo foi provisionado e nenhum deploy foi executado.
