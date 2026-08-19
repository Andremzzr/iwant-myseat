# iwant-myseat

Um script em Python para monitorar sessões de cinema IMAX e enviar notificações automaticamente via Telegram quando houver cadeiras disponíveis.

## Pré-requisitos

- Python 3 instalado no sistema.

## Configuração do Telegram

Para que o script consiga enviar mensagens para você, é necessário criar um bot no Telegram e obter as chaves de acesso.

1. Criando o bot:
   - Abra o Telegram e busque por @BotFather.
   - Inicie a conversa e envie o comando /newbot. Siga as instruções na tela para escolher um nome e um username para o seu bot.
   - Ao final, o BotFather fornecerá um token de acesso (parecido com 123456789:ABCdefGHI). Guarde este token.
   - Busque o bot que você acabou de criar no Telegram e inicie a conversa clicando em "Start" ou enviando uma mensagem. Isso é obrigatório, pois bots não podem iniciar conversas com usuários.

2. Obtendo o seu Chat ID:
   - No Telegram, busque pelo bot @userinfobot.
   - Inicie a conversa com ele. Ele responderá imediatamente com uma mensagem contendo o seu "Id" (um número grande). Guarde este número.

## Configuração do Projeto

1. Crie e ative um ambiente virtual (recomendado) dentro da pasta do projeto:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows, utilize: venv\Scripts\activate
   ```

2. Instale as bibliotecas necessárias:
   ```bash
   pip install -r requirements.txt
   ```
   Caso prefira instalar manualmente, execute: `pip install curl_cffi python-dotenv`

3. Configure o arquivo de variáveis:
   - Crie um arquivo chamado `.env` na mesma pasta do script.
   - Adicione o seu token do bot e o seu ID de usuário, respeitando o seguinte formato:

   ```env
   TELEGRAM_TOKEN=cole_seu_token_aqui
   TELEGRAM_CHAT_ID=cole_seu_id_aqui
   ```

## Como Executar

Com o ambiente virtual ativado e o arquivo .env configurado, execute o script no terminal informando o nome do filme e a quantidade mínima de cadeiras que você precisa.

Sintaxe:
```bash
python fetch_sessions.py "Título do Filme" <quantidade_de_cadeiras>
```

Exemplo:
```bash
python fetch_sessions.py "A Odisseia" 2
```

O script fará a busca nas APIs do cinema pelas sessões do filme especificado. Caso encontre sessões IMAX com a quantidade de cadeiras solicitada, uma mensagem contendo os detalhes (horários, salas e preços) será enviada automaticamente para o seu Telegram.
