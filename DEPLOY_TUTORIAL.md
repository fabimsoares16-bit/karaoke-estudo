# 📚 Tutorial de Deploy na Vercel — Karaokê de Estudo

> Este documento registra **exatamente** como foi feito o deploy desta aplicação na Vercel,
> passo a passo, para referência e aprendizado futuro.

---

## 🧩 Entendendo a Estrutura do Projeto

Antes de subir qualquer coisa, é importante entender **o que cada arquivo faz** e
**o que a Vercel espera receber**.

### Arquivos do projeto

```
app de ingles/
├── index.html              ← Frontend (HTML + CSS + JS, tudo num arquivo só)
├── api/                    ← 🔑 Pasta mágica! A Vercel transforma cada arquivo aqui
│   ├── search_yt.py        │     em um endpoint serverless automático
│   ├── search_lrc.py       │     /api/search_yt  →  search_yt.py
│   └── lyrics_fallback.py  │     /api/search_lrc →  search_lrc.py
│                           │     /api/lyrics_fallback → lyrics_fallback.py
├── vercel.json             ← Configurações do deploy
├── .vercelignore           ← Arquivos que NÃO devem subir para a Vercel
├── server.py               ← Servidor LOCAL (não vai para a Vercel)
├── test_yt.js              ← Teste local (não vai para a Vercel)
└── documento.txt           ← Anotações (não vai para a Vercel)
```

### O que é a pasta `api/`?

A Vercel tem uma convenção: **qualquer arquivo Python (ou Node.js, Go, Ruby) dentro
da pasta `api/` na raiz do projeto é automaticamente transformado em uma Serverless
Function**.

Isso significa que:
- `api/search_yt.py` → vira o endpoint `https://seusite.vercel.app/api/search_yt`
- `api/search_lrc.py` → vira o endpoint `https://seusite.vercel.app/api/search_lrc`
- `api/lyrics_fallback.py` → vira o endpoint `https://seusite.vercel.app/api/lyrics_fallback`

**Não precisa configurar rotas, nem instalar frameworks.** A Vercel faz tudo sozinha.

### Requisito das Serverless Functions em Python

Cada arquivo `.py` na pasta `api/` precisa seguir este formato:

```python
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):    # ← O nome DEVE ser "handler" (minúsculo)
    def do_GET(self):                      # ← Método HTTP que ele responde
        # sua lógica aqui
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok": true}')
```

> ⚠️ **Importante**: A classe DEVE se chamar `handler` (com h minúsculo). Se usar outro
> nome, a Vercel não vai encontrar o ponto de entrada da função.

---

## 📁 Arquivos de Configuração

### `vercel.json` — Configurações do deploy

```json
{
  "cleanUrls": true
}
```

Este arquivo é **minimalista** porque a Vercel já faz o resto automaticamente:
- `cleanUrls: true` → remove a extensão `.html` das URLs (acessa `/` em vez de `/index.html`)
- A Vercel já serve arquivos estáticos (HTML, CSS, JS) da raiz
- A Vercel já detecta a pasta `api/` e cria as Serverless Functions

### `.vercelignore` — O que NÃO subir

```
# Arquivos que NÃO devem ir para a Vercel (são só para desenvolvimento local)
server.py
test_yt.js
documento.txt
__pycache__
.claude
```

Funciona igual ao `.gitignore`: lista arquivos/pastas que devem ser ignorados no deploy.
O `server.py` é o servidor local de desenvolvimento — na Vercel, as Serverless Functions
na pasta `api/` substituem ele.

---

## 🚀 O Deploy Passo a Passo

### Passo 1 — Verificar pré-requisitos

Abri o terminal (PowerShell) e verifiquei se tudo estava instalado:

```powershell
node --version     # → v24.12.0  ✅
npm --version      # → 11.6.2    ✅
vercel --version   # → 54.18.4   ✅
```

> 💡 Se o Node.js não estivesse instalado, bastaria baixar em https://nodejs.org
> Se a Vercel CLI não estivesse instalada: `npm install -g vercel`

### Passo 2 — Verificar login na Vercel

```powershell
vercel whoami
# → fabimsoares16-bit  ✅ (já estava logado)
```

> 💡 Se não estivesse logado, rodaria `vercel login` (abre o navegador para autenticar).

### Passo 3 — Ver projetos existentes

```powershell
vercel ls
```

Isso mostrou 3 projetos na minha conta:
- `app-do-ingles` (deploy anterior, só com HTML)
- `project-il797`
- `sistema-materiais`

Decidi **criar um projeto novo** em vez de atualizar o antigo.

### Passo 4 — Vincular a pasta a um novo projeto

```powershell
vercel link --yes --scope fabio-soares-projects1 --project karaoke-estudo
```

**O que cada flag faz:**
| Flag | Significado |
|---|---|
| `--yes` | Aceita tudo automaticamente (modo não-interativo) |
| `--scope fabio-soares-projects1` | Especifica o "time"/conta na Vercel |
| `--project karaoke-estudo` | Nome do novo projeto |

**Saída:**
```
✓ Created  fabio-soares-projects1/karaoke-estudo
```

Isso criou:
- O projeto `karaoke-estudo` no painel da Vercel
- Uma pasta `.vercel/` local com o ID do projeto (para os deploys futuros saberem
  pra onde enviar)

### Passo 5 — Fazer o deploy

```powershell
vercel --yes
```

**O que aconteceu nos bastidores:**

```
1. Upload dos arquivos (72KB total)
   - index.html
   - api/search_yt.py
   - api/search_lrc.py
   - api/lyrics_fallback.py
   - vercel.json
   (os arquivos do .vercelignore foram ignorados ✅)

2. Build na região iad1 (Washington, D.C.)
   - Detectou Python → provisionou Python 3.12
   - Criou ambiente virtual (.venv)
   - Compilou bytecode Python
   - Build completo em 5 segundos

3. Deploy dos outputs
   - index.html → servido como arquivo estático
   - api/*.py → criou 3 Serverless Functions

4. Alias
   - URL de produção: https://karaoke-estudo.vercel.app
```

---

## 🌐 Resultado Final

| Recurso | URL |
|---|---|
| **Site** | https://karaoke-estudo.vercel.app |
| **API: Busca YouTube** | https://karaoke-estudo.vercel.app/api/search_yt?q=... |
| **API: Busca Letras** | https://karaoke-estudo.vercel.app/api/search_lrc?q=... |
| **API: Fallback Letras** | https://karaoke-estudo.vercel.app/api/lyrics_fallback?q=... |
| **Painel do Deploy** | https://vercel.com/fabio-soares-projects1/karaoke-estudo |

---

## 🔄 Como Atualizar no Futuro

Sempre que fizer mudanças no código, basta rodar na pasta do projeto:

```powershell
# Deploy de preview (para testar antes)
vercel --yes

# OU deploy direto em produção
vercel --prod --yes
```

Não precisa vincular de novo — a pasta `.vercel/` já sabe qual projeto atualizar.

---

## 🧠 Conceitos Importantes Aprendidos

### 1. Diferença entre Local e Vercel

```
┌─────────────── LOCAL ───────────────┐    ┌─────────────── VERCEL ──────────────┐
│                                     │    │                                      │
│  server.py (roda com python)        │    │  index.html → arquivo estático       │
│  ├── serve index.html               │    │                                      │
│  ├── /api/search_yt (proxy)         │    │  api/search_yt.py → Serverless Fn    │
│  ├── /api/search_lrc (proxy)        │    │  api/search_lrc.py → Serverless Fn   │
│  └── /api/lyrics_fallback (proxy)   │    │  api/lyrics_fallback.py → Serverless │
│                                     │    │                                      │
│  Tudo roda num processo só          │    │  Cada função roda independente       │
│  Porta: localhost:8000              │    │  URL: karaoke-estudo.vercel.app      │
└─────────────────────────────────────┘    └──────────────────────────────────────┘
```

### 2. Serverless Functions

- **Não ficam rodando 24h** — só executam quando alguém faz uma requisição
- **Cada chamada é independente** — não compartilham memória entre si
- **Timeout padrão: 10 segundos** (plano gratuito) — por isso os timeouts no código
  são de 4-9 segundos
- **Escalam automaticamente** — se 100 pessoas acessarem ao mesmo tempo, a Vercel
  cria 100 instâncias

### 3. Por que a pasta `api/` funciona

A Vercel usa um sistema de **convenção sobre configuração**:
- Colocou na pasta `api/`? → vira Serverless Function
- É arquivo `.py`? → usa Python Runtime
- É arquivo `.js` ou `.ts`? → usa Node.js Runtime
- Tem `handler` exportado? → esse é o ponto de entrada

### 4. O `.vercelignore` é essencial

Sem ele, o `server.py` seria enviado para a Vercel desnecessariamente. Apesar de
não causar erro (a Vercel ignora arquivos Python fora da pasta `api/`), é boa prática
enviar apenas o necessário.

### 5. O `vercel.json` pode ser expandido

Exemplo de configurações mais avançadas que poderiam ser adicionadas:

```json
{
  "cleanUrls": true,
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "s-maxage=60" }
      ]
    }
  ],
  "redirects": [
    { "source": "/old-page", "destination": "/", "permanent": true }
  ]
}
```

---

## 📋 Checklist Rápido para Deploys Futuros

- [ ] Código testado localmente (`python server.py` + abrir no navegador)
- [ ] `.vercelignore` atualizado (se adicionou novos arquivos de dev)
- [ ] `vercel.json` atualizado (se precisa de novas configurações)
- [ ] Novas funções Python em `api/` seguem o padrão `class handler(BaseHTTPRequestHandler)`
- [ ] Rodar `vercel --yes` para preview
- [ ] Testar na URL de preview
- [ ] Rodar `vercel --prod --yes` para produção

---

*Documento gerado em 22/07/2026 após deploy bem-sucedido.*
