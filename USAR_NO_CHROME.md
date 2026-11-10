# 🌐 Como Usar no Google Chrome (Passo-a-Passo)

## ✅ Solução Rápida (Teste Agora)

### Para macOS/Linux:

```bash
cd ~/Documents/ITBI
python3 -m http.server 8888
```

Cole no Chrome:
```
http://localhost:8888/itbi_visualizer.html
```

### Para Windows:

1. Clique duplo em **`iniciar.bat`**
2. Navegador abre automaticamente ✅

---

## 📋 Por Que o Mapa Não Rendeu?

O Chrome (e outros navegadores) **bloqueiam** arquivos HTML acessados diretamente:

```
❌ ERRADO: file:///C:/Users/você/Documents/ITBI/itbi_visualizer.html
✅ CERTO: http://localhost:8888/itbi_visualizer.html
```

**Por quê?** Segurança! Arquivo local pode acessar seu disco rigidamente.

---

## 🚀 Opção 1: Servidor Local (Recomendado)

### Passo 1: Abrir Terminal
**macOS:** Cmd + Espaço → "Terminal" → Enter

**Windows:** Clique em `iniciar.bat` (feito!)

**Linux:** Abra terminal (Ctrl + Alt + T)

### Passo 2: Navegar até a Pasta
```bash
cd ~/Documents/ITBI
```

(ou `cd C:\Users\SeuUsuario\Documents\ITBI` no Windows)

### Passo 3: Iniciar Servidor
```bash
python3 -m http.server 8888
```

Você verá:
```
Serving HTTP on 0.0.0.0 port 8888 (http://0.0.0.0:8888/) ...
```

### Passo 4: Abrir no Chrome
Copie e cole na barra de endereço:
```
http://localhost:8888/itbi_visualizer.html
```

### Resultado:
✅ Mapa carrega perfeitamente!

---

## 🎯 Opção 2: Script Automático

Se você tiver Python:

### macOS/Linux:
```bash
cd ~/Documents/ITBI
chmod +x iniciar.sh
./iniciar.sh
```

Browser abre automaticamente! ✅

### Windows:
Clique duplo: **`iniciar.bat`** ✅

---

## 💡 Dicas de Uso no Chrome

### Atalhos Úteis:
- `Ctrl + Shift + I` (ou F12) = Abrir Console (vê erros)
- `Ctrl + L` = Selecionar barra de endereço
- `Ctrl + R` = Recarregar página
- `Ctrl + Shift + R` = Recarregar sem cache

### Modo Fullscreen:
- `F11` = Tela cheia (depois F11 novamente sai)

### Devtools (Se tiver problemas):
1. Aperte `F12`
2. Vá para aba **Console**
3. Procure por erros em vermelho
4. Se tiver erro, mande print para suporte

---

## 🔍 Como Saber se Está Funcionando

✅ **Sinais de sucesso:**
- Mapa do Rio aparece (verde/azul)
- Marker clusters aparecem (bolinhas laranja com números)
- Filtros na esquerda funcionam
- Tabela de direita mostra dados

❌ **Sinais de erro:**
- Página branca
- "Cannot GET /itbi_visualizer.html"
- Mapa cinza (pode ser internet)
- Console cheio de erros vermelhos

---

## 🆘 Troubleshooting no Chrome

### ❌ "Falha ao conectar a localhost:8888"

**Solução:**
```bash
# Terminal: verifique se servidor está rodando
# Viu "Serving HTTP"? Está bom!
# Senão, execute novamente:
python3 -m http.server 8888
```

### ❌ "Cannot GET /itbi_visualizer.html"

**Solução:**
```bash
# Verifique que está na pasta certa:
ls itbi_visualizer.html

# Se não aparecer, você está em pasta errada:
cd ~/Documents/ITBI
python3 -m http.server 8888
```

### ❌ Mapa fica cinza / não carrega

**Solução:**
- Verifique internet (precisa carregar mapa do OpenStreetMap)
- Aguarde 3-5 segundos
- Recarregue (Ctrl+R)
- Se continuar: abra Console (F12) procure erros

### ❌ "Esta página é inacessível"

**Solução:**
```bash
# Terminal pode estar fechado! Abra novamente e rode:
python3 -m http.server 8888

# Depois acesse Chrome com a URL correta:
http://localhost:8888/itbi_visualizer.html
```

---

## 🎓 Entender o que Está Acontecendo

```
Seu Computador:
┌─────────────────────────────────┐
│  Chrome                         │
│  └─ Acessa localhost:8888       │
│     └─ Pede itbi_visualizer.html
│                                 │
│  Python http.server             │
│  └─ Ouve na porta 8888          │
│     └─ Envia arquivo HTML/JS    │
│                                 │
│  Arquivo:                       │
│  └─ itbi_visualizer.html        │
└─────────────────────────────────┘

                 ↕
         Comunicação Local
         (sem internet)
```

---

## 🎬 Demonstração Visual

### Antes (Não funciona):
```
Chrome → arquivo.html (no disco)
  ❌ Bloqueado por CORS
  ❌ Mapa não carrega
  ❌ JavaScript restrito
```

### Depois (Funciona!):
```
Chrome → localhost:8888 (servidor)
  ✅ Liberado por HTTP
  ✅ Mapa renderiza
  ✅ Tudo funciona
```

---

## 🔐 É Seguro?

✅ **SIM! Porque:**
- Conexão é local (não sai do seu PC)
- Sem dados sendo enviados
- Sem internet necessária
- Sem login/senha

---

## 🎯 Próximos Passos

1. **Agora:** Inicie o servidor e abra no Chrome
2. **Explore:** Teste filtros, mapa, gráficos
3. **Customize:** Leia `EXTENSOES.md` para personalizar
4. **Compartilhe:** Todos podem usar da mesma forma!

---

## 📞 Se Continuar com Problema

1. Abra o Console (F12)
2. Tire screenshot dos erros
3. Verifique que está na pasta correta: `ls itbi_visualizer.html`
4. Reinicie o servidor: `Ctrl+C` depois `python3 -m http.server 8888`

---

**Pronto! Seu visualizador ITBI está funcionando no Chrome! 🎉**
