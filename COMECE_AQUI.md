# 🚀 COMECE AQUI - Guia de Primeiros Passos

## ⏱️ 2 Minutos: Executar com Dados de Exemplo

### Passo 1: Abrir o visualizador
Abra o arquivo `itbi_visualizer.html` diretamente no seu navegador:

```bash
# No macOS
open itbi_visualizer.html

# No Windows
start itbi_visualizer.html

# No Linux
xdg-open itbi_visualizer.html

# Ou simplesmente: clique duplo no arquivo
```

### Passo 2: Explore os dados
- 🗺️ Veja o **mapa** com 500 imóveis de exemplo no Rio
- 🔍 Use os **filtros** na esquerda
- 📊 Veja **gráficos** e **estatísticas**
- ⚖️ **Compare** 2 bairros

**É só isso!** A ferramenta já tem dados fictícios carregados.

---

## 🎯 15 Minutos: Usar com Seus Dados Reais ITBI

### Passo 1: Baixar dados da Prefeitura RJ

1. Acesse: https://fazenda.prefeitura.rio/itbi-valores-medios-por-m2-de-transacoes-imobiliarias-por-trecho-de-logradouro/

2. Baixe um dos arquivos Excel (escolha um):
   - `ITBI 2011-2018.xlsx` (histórico antigo)
   - `ITBI 2019-2024.xlsx` (recomendado)
   - `ITBI 2025 em diante.xlsx` (mais recente)

### Passo 2: Preparar os dados

1. **Renomeie** o arquivo que baixou para `itbi_data.xlsx`

2. **Coloque na mesma pasta** onde está `itbi_visualizer.html`

3. **Instale dependências** (primeira vez apenas):
   ```bash
   npm install
   ```

4. **Processe os dados**:
   ```bash
   npm run process-data
   ```
   
   Você verá:
   ```
   📂 Lendo arquivo ITBI...
   ✅ Lido 80234 registros
   🔄 Processando dados...
   ✅ Processado 78901 registros válidos
   💾 Salvando JSON...
   ✅ Salvo em: itbi_data.json
   ```

### Passo 3: Abrir visualizador com seus dados

Reabra `itbi_visualizer.html` no navegador - ele carregará seus dados reais automaticamente!

---

## 📁 Estrutura de Pastas

Após os passos acima, sua pasta ficará assim:

```
ITBI/
├── itbi_visualizer.html      ← Abra este no navegador
├── process_itbi_data.js
├── README.md
├── COMECE_AQUI.md           ← Você está aqui
├── package.json
├── itbi_data.xlsx           ← Arquivo que você baixou
├── itbi_data.json           ← Gerado automaticamente
└── node_modules/            ← Criado automaticamente
```

---

## 🎮 Como Usar - Guia Rápido

### Filtrar Dados
1. Preencha os filtros na esquerda
2. Clique em **"✓ Aplicar Filtros"**
3. Mapa e gráficos atualizam automaticamente

### Exemplos de Filtros

**Encontrar imóveis em Copacabana entre R$ 300k e R$ 500k:**
```
Bairro: Copacabana
Preço Min: 300000
Preço Max: 500000
→ Clique em Aplicar Filtros
```

**Encontrar apartamentos grandes (100-150m²) na Zona Sul:**
```
Zona: Zona Sul
Área Min: 100
Área Max: 150
→ Clique em Aplicar Filtros
```

**Comparar preços entre Ipanema e Leblon:**
```
Aba: ⚖️ Comparação
Região 1: Ipanema
Região 2: Leblon
→ Clique em Comparar
```

### Navegar pelas Abas

| Aba | O que faz |
|-----|-----------|
| 📋 **Resultados** | Lista de 100 transações com detalhes |
| 📊 **Gráficos** | Distribuição de preços e série temporal |
| 📈 **Estatísticas** | Resumo geral, preços por zona, top ruas |
| ⚖️ **Comparação** | Compare 2 bairros lado-a-lado |

### Clicar no Mapa
- **Clique em um marcador** → vê endereço, preço, data
- **Botão "Google Maps"** → abre o local no Google Maps
- **Clique em uma linha da tabela** → centraliza no mapa

---

## 🆘 Troubleshooting

### ❌ Problema: "Arquivo itbi_data.json não encontrado"
**Solução:**
- [ ] Verifique se procesou os dados com `npm run process-data`
- [ ] Ou simplesmente use os dados de exemplo (já carregam automaticamente)

### ❌ Problema: Erro ao rodar `npm run process-data`
**Solução:**
```bash
# Reinstale dependências
rm -rf node_modules package-lock.json
npm install
npm run process-data
```

### ❌ Problema: Mapa não aparece / branco
**Solução:**
- [ ] Verifique sua conexão internet (precisa carregar o mapa do OpenStreetMap)
- [ ] Abra o Console (F12 ou Cmd+Shift+I)
- [ ] Procure por mensagens de erro em vermelho

### ❌ Problema: Muito lento com muitos dados
**Solução:**
- [ ] Use os filtros para reduzir para um bairro específico
- [ ] Reduza a faixa de datas
- [ ] O clustering automático já está ativado

### ❌ Problema: Dados não aparecem após processar
**Solução:**
- [ ] Verifique que o arquivo gerado `itbi_data.json` existe na pasta
- [ ] Recarregue a página do navegador (Ctrl+Shift+R ou Cmd+Shift+R)

---

## 💡 Dicas Úteis

### 📌 Dica 1: Estatísticas Rápidas
Filtre por um bairro e vá para a aba **📈 Estatísticas** para ver:
- Preço médio, mínimo e máximo
- Preço/m² médio
- Ruas mais caras
- Comparação entre zonas

### 📌 Dica 2: Encontrar Oportunidades
1. Vá para **📊 Gráficos**
2. Procure por **"picos"** (valores muito baixos ou altos)
3. Filtre por essas faixas para investigar

### 📌 Dica 3: Analisar Tendências
1. Use filtro de **data** para ver evolução
2. Vá para **📊 Gráficos** → "Transações por Mês"
3. Observe padrões sazonais

### 📌 Dica 4: Salvar Filtros
Não há função de "salvar filtro", mas você pode:
- Usar a URL com parâmetros (implementar em versão futura)
- Tirar screenshots dos resultados
- Copiar dados da tabela para Excel

### 📌 Dica 5: Exportar Dados
Seleção da tabela com Ctrl+A (Cmd+A), copie com Ctrl+C, cole em Excel!

---

## 🔄 Atualizar Dados

Quando novos dados ITBI forem disponibilizados:

1. Baixe o novo arquivo Excel
2. Renomeie para `itbi_data.xlsx`
3. Execute `npm run process-data`
4. Recarregue o navegador

---

## 📚 Próximos Passos

Após dominar o básico:

### Nível 1: Customização
- Editar cores e design (CSS no arquivo HTML)
- Adicionar seus bairros/zonas
- Alterar fonte de dados

### Nível 2: Expansão
- Adicionar suporte a outras cidades (SP, BH, etc)
- Conectar com API de imobiliárias reais
- Criar alertas de preço

### Nível 3: Análise Avançada
- Usar Python + Jupyter para análise ML
- Exportar para Tableau/Power BI
- Integrar com CRM imobiliário

---

## 📞 Suporte

**Dúvidas sobre os dados ITBI?**
- Prefeitura RJ: https://fazenda.prefeitura.rio/
- Portal de dados: https://data.rio/

**Dúvidas sobre a ferramenta?**
- Verifique o [README.md](README.md) completo
- Abra o Console (F12) para ver erros
- Inspecione o código HTML (está bem comentado!)

---

## ✅ Checklist de Primeiros Passos

- [ ] Abri `itbi_visualizer.html` no navegador
- [ ] Explorei o mapa e os filtros
- [ ] Baixei dados reais ITBI
- [ ] Renomeei para `itbi_data.xlsx`
- [ ] Executei `npm run process-data`
- [ ] Reabri o visualizador com dados reais
- [ ] Fiz alguns filtros de teste
- [ ] Consultei as abas: Resultados, Gráficos, Estatísticas, Comparação

**Pronto! Você está com domínio completo da ferramenta!** 🎉

---

**Bom uso! Se gostou, compartilhe com amigos imobiliários!**
