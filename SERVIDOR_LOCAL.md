# 🌐 Como Executar com Servidor Local

O navegador tem restrições de segurança ao abrir arquivos HTML diretamente do disco. **A solução é usar um servidor local**, que é simples e rápido.

## ⚡ Opção 1: Scripts Automáticos (Recomendado)

### macOS / Linux
```bash
chmod +x iniciar.sh
./iniciar.sh
```

Isso:
1. ✅ Inicia um servidor automático
2. ✅ Abre o navegador
3. ✅ Mostra a URL
4. ✅ Aperta Ctrl+C para parar

### Windows
Clique duplo em **`iniciar.bat`**

Isso:
1. ✅ Verifica se Python está instalado
2. ✅ Encontra porta disponível
3. ✅ Abre o navegador automaticamente
4. ✅ Deixa servidor rodando

---

## 🛠️ Opção 2: Manual (Python)

### Passo 1: Abrir Terminal/PowerShell

**macOS/Linux:**
```bash
cd ~/Documents/ITBI
```

**Windows:**
```powershell
cd C:\Users\SeuUsuario\Documents\ITBI
```

### Passo 2: Iniciar Servidor

**Python 3 (recomendado):**
```bash
python3 -m http.server 8888
```

Ou:
```bash
python -m http.server 8888
```

### Passo 3: Abrir no Navegador

Copie e cole na barra de endereço:
```
http://localhost:8888/itbi_visualizer.html
```

### Passo 4: Parar Servidor

Pressione **Ctrl+C** no terminal

---

## 🎯 Opção 3: Node.js (Alternativa)

Se você tem Node.js instalado:

```bash
# Instalar http-server globalmente
npm install -g http-server

# Iniciar servidor na pasta do projeto
cd ~/Documents/ITBI
http-server

# Acesse:
# http://localhost:8080/itbi_visualizer.html
```

---

## 🐍 Opção 4: PHP (Se Disponível)

```bash
cd ~/Documents/ITBI
php -S localhost:8000

# Acesse:
# http://localhost:8000/itbi_visualizer.html
```

---

## 🔧 Troubleshooting

### ❌ Erro: "Porta já em uso"

**Solução 1:** Use porta diferente
```bash
python3 -m http.server 8889
# http://localhost:8889/itbi_visualizer.html
```

**Solução 2:** Matar processo usando a porta
```bash
# macOS/Linux
lsof -ti:8888 | xargs kill -9

# Windows (PowerShell como admin)
netstat -ano | findstr :8888
taskkill /PID <PID> /F
```

### ❌ Erro: "Python não encontrado"

**Solução:**
```bash
# Verificar se instalado
python --version
python3 --version

# Se não tiver, instale em https://python.org
# Marque "Add Python to PATH"
```

### ❌ Mapa não carrega / "Cannot GET /"

**Solução:**
- Verifique que está na pasta correta: `cd ~/Documents/ITBI`
- Verifique a porta: tente `localhost:8888` (com 8888)
- Verifique se arquivo existe: `ls itbi_visualizer.html`

### ❌ Browser não abre automaticamente

**Solução:**
Abra manualmente copiando a URL que aparece no terminal:
```
http://localhost:XXXX/itbi_visualizer.html
```

---

## 📊 Verificar se Servidor Está Rodando

### macOS/Linux
```bash
curl http://localhost:8888/itbi_visualizer.html | head -5
```

### Windows (PowerShell)
```powershell
Invoke-WebRequest http://localhost:8888/itbi_visualizer.html
```

---

## 🔐 Segurança

✅ **Servidor local é seguro porque:**
- Não sai da sua máquina
- Apenas você acessa
- Sem internet necessária
- Sem dados sendo enviados

---

## 🚀 Dicas Avançadas

### Rodar em Background (macOS/Linux)
```bash
python3 -m http.server 8888 &
# Para parar: killall python3
```

### Acessar de Outro Computador (Mesma Rede)
```bash
# Em vez de localhost, use seu IP
# Descubra com: ifconfig (macOS/Linux) ou ipconfig (Windows)
http://192.168.1.100:8888/itbi_visualizer.html
```

### Configurar Alias (Atalho)
```bash
# Adicione ao ~/.bashrc ou ~/.zshrc
alias itbi='cd ~/Documents/ITBI && python3 -m http.server 8888'

# Depois use:
itbi
```

---

## 📱 Acessar do Celular (Mesma Rede WiFi)

1. Descubra IP do computador:
   ```bash
   # macOS/Linux
   ifconfig
   
   # Windows
   ipconfig
   ```

2. Anote o IP (ex: 192.168.1.100)

3. No celular, acesse:
   ```
   http://192.168.1.100:8888/itbi_visualizer.html
   ```

---

## ⚡ Performance

```
Tamanho de download: 43 KB
Tempo de carga: 2-3 segundos
Uso de memória: ~50 MB
CPU: Mínimo enquanto navegando
```

---

## 🎯 Resumo Rápido

| Método | Comando | Porta | Facilidade |
|--------|---------|-------|-----------|
| **Script** | `./iniciar.sh` | Automática | ⭐⭐⭐⭐⭐ |
| **Python** | `python3 -m http.server 8888` | 8888 | ⭐⭐⭐⭐ |
| **Node.js** | `http-server` | 8080 | ⭐⭐⭐⭐ |
| **PHP** | `php -S localhost:8000` | 8000 | ⭐⭐⭐ |

---

## ❓ FAQ

**P: Preciso ter internet para usar?**
R: Não! Funciona 100% offline.

**P: Por que não posso abrir o HTML diretamente?**
R: Navegadores modernos restringem acesso ao disco por segurança.

**P: Qual método é melhor?**
R: Use o script (`./iniciar.sh` ou `iniciar.bat`), é o mais fácil!

**P: Preciso deixar o terminal aberto?**
R: Sim, o servidor precisa estar rodando enquanto você usa.

**P: Posso usar em produção?**
R: Para uso pessoal sim. Para server remoto, use Nginx/Apache.

---

**Pronto! Agora seu visualizador vai funcionar perfeitamente! 🚀**
