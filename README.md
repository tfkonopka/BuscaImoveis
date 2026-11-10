# 🏘️ Visualizador de Preços ITBI - Rio de Janeiro

Uma ferramenta completa para visualizar, analisar e comparar preços de imóveis baseado em dados públicos de transações ITBI (Imposto sobre Transmissão de Bens Imóveis) do Rio de Janeiro.

## ✨ Funcionalidades

### 1. **Mapa Interativo com Clustering**
- Visualização de todas as transações em mapa Leaflet
- Clustering automático para melhor performance
- Cores por faixa de preço/m²
- Clique em marcador para detalhes
- Integração com Google Maps

### 2. **Filtros Avançados**
- 💰 Filtro por preço (mín/máx)
- 📏 Filtro por área em m² (mín/máx)
- 📊 Filtro por preço/m² (mín/máx)
- 📅 Filtro por período de data
- 🏘️ Filtro por bairro
- 🗺️ Filtro por zona (Sul, Norte, Oeste, Centro)
- 🏠 Busca por endereço e número

### 3. **Análise de Dados**
- **Estatísticas**: Preço médio, mediana, mín/máx
- **Gráficos**: Distribuição de preços, série temporal
- **Comparação**: Compare 2 regiões lado-a-lado
- **Rankings**: Top 10 ruas por preço/m²

### 4. **Visualizações Interativas**
- Tabela com resultados (até 100 por página)
- Gráficos em tempo real com Chart.js
- Cards informativos com dados por zona
- Exportação de resultados

## 🚀 Como Usar

### Opção 1: Com Dados de Exemplo (Rápido)
1. Abra `itbi_visualizer.html` no navegador
2. A aplicação carrega com 500 imóveis fictícios para demonstração
3. Todos os recursos funcionam normalmente

```bash
# No terminal
open itbi_visualizer.html
# ou
firefox itbi_visualizer.html
# ou
chrome itbi_visualizer.html
```

### Opção 2: Com Dados Reais ITBI
1. **Baixar dados da Prefeitura RJ**
   - Acesse: https://fazenda.prefeitura.rio/itbi-valores-medios-por-m2-de-transacoes-imobiliarias-por-trecho-de-logradouro/
   - Baixe um dos arquivos Excel com dados ITBI
   - Salve como `itbi_data.xlsx` na mesma pasta

2. **Processar dados**
   ```bash
   # Instalar dependências
   npm install xlsx

   # Executar script
   node process_itbi_data.js
   ```
   - Isso gera um arquivo `itbi_data.json` com ~25k-80k transações

3. **Abrir visualizador**
   - Reabra `itbi_visualizer.html`
   - Dados reais serão carregados automaticamente

## 📋 Interface

### Painel Esquerdo - Filtros
- Configure seus critérios de busca
- Clique em "Aplicar Filtros" para atualizar resultados
- "Limpar" reseta todos os filtros

### Centro - Mapa
- Visualiza todas as transações
- Clique em um marcador para ver detalhes
- Zoom automático ao filtrar

### Direita - Abas de Resultados

#### 📋 **Resultados**
- Tabela com até 100 transações
- Clique em coluna para ordenar
- Clique em linha para centralizar no mapa

#### 📊 **Gráficos**
- Distribuição de preços/m² (histograma)
- Série temporal de transações (linha)

#### 📈 **Estatísticas**
- Cards com resumo dos dados filtrados
- Gráfico comparativo por zona
- Top 10 ruas mais caras

#### ⚖️ **Comparação**
- Selecione 2 bairros
- Veja comparação em gráfico radar
- Analise diferenças de preço e volume

## 🛠️ Stack Técnico

### Frontend
- **HTML5/CSS3**: Layout responsivo e moderno
- **JavaScript vanilla**: Sem dependências externas (executa tudo localmente)
- **Leaflet.js**: Mapa interativo
- **Chart.js**: Gráficos e visualizações
- **Bootstrap 5**: UI components

### Dados
- **Papa Parse**: Leitura de CSV/Excel
- **IndexedDB/LocalStorage**: Cache local
- **Arquivos JSON**: Armazenamento estruturado

### APIs (Opcional)
- **Google Maps**: Botão "Ver no Google Maps" (requer chave)
- **OpenStreetMap**: Tiles do mapa (gratuito)

## 📊 Estrutura de Dados

Cada transação contém:
```json
{
  "id": 0,
  "logradouro": "Rua das Flores",
  "numero": "42",
  "bairro": "Copacabana",
  "zona": "Zona Sul",
  "cep": "20000-000",
  "preco": 500000,
  "m2": 120,
  "valor_m2": 4166.67,
  "data_transacao": "2026-10-15",
  "volume_transacoes": 1,
  "latitude": -23.5506,
  "longitude": -43.1762
}
```

## 🎯 Casos de Uso

### Para Compradores
- Pesquisar preços médios de imóveis em suas regiões de interesse
- Comparar valores entre bairros
- Analisar tendências de preço ao longo do tempo
- Identificar ruas mais caras e mais baratas

### Para Vendedores
- Descobrir preço justo para seu imóvel
- Comparar com transações similares na região
- Análise de mercado local
- Benchmarking contra concorrência

### Para Investidores
- Análise de mercado por região/bairro
- Identificar oportunidades de investimento
- Acompanhar tendências de preço
- Comparação de ROI entre regiões

### Para Pesquisadores
- Dados públicos de transações imobiliárias
- Análise geoespacial de preços
- Estudos de mercado imobiliário
- Dados para pesquisa acadêmica

## ⚙️ Configuração

### Alterar Dados de Exemplo
Edite a função `generateSampleData()` em `itbi_visualizer.html`:

```javascript
const bairros = [
    { name: 'Copacabana', zone: 'Zona Sul', lat: -23.5506, lng: -43.1762 },
    // Adicione seus bairros aqui
];
```

### Integrar Google Maps (Opcional)
1. Obtenha uma chave API em https://cloud.google.com/maps-platform
2. Abra o arquivo HTML e procure por "maps.googleapis.com"
3. Substitua `YOUR_KEY` pela sua chave

### Customizar Cores
Edite as variáveis CSS no `<style>`:
```css
/* Cores principais */
--primary: #667eea;
--secondary: #764ba2;
/* etc */
```

## 📈 Performance

- **Dados até 50MB**: Carrega diretamente no browser
- **Dados > 50MB**: Considere dividir por bairro ou zona
- **100k+ marcadores**: Use clustering (já implementado)
- **Totalmente offline**: Funciona 100% local após carregamento

## 🐛 Troubleshooting

### "itbi_data.json não encontrado"
- ✅ Use dados de exemplo ou processe Excel com `process_itbi_data.js`

### Mapa não aparece
- ✅ Verifique conexão internet (precisa carregar tiles do OpenStreetMap)
- ✅ Abra console (F12) e procure por erros

### Performance lenta com muitos dados
- ✅ O clustering já está ativado por padrão
- ✅ Reduza intervalo de datas nos filtros
- ✅ Filtre por bairro específico

### Gráficos não aparecem
- ✅ Clique na aba "Gráficos" para atualizar
- ✅ Certifique-se que há dados filtrados

## 📝 Arquivos

```
projeto/
├── itbi_visualizer.html      # 🎯 Arquivo principal (abra no navegador)
├── process_itbi_data.js      # Script para processar Excel
├── itbi_data.json            # Dados processados (gerado automaticamente)
├── itbi_data.xlsx            # Seus dados brutos ITBI
└── README.md                 # Este arquivo
```

## 🔒 Privacidade

- ✅ Totalmente offline - nenhum dado é enviado a servidores
- ✅ Sem cookies ou rastreamento
- ✅ Sem login necessário
- ✅ Dados armazenados apenas localmente

## 📄 Licença

Este projeto usa dados públicos da Prefeitura do Rio de Janeiro e bibliotecas de código aberto:
- OpenStreetMap (tiles)
- Leaflet.js (mapa)
- Chart.js (gráficos)
- Bootstrap (UI)

## 🚀 Roadmap Futuro

- [ ] Exportar dados em Excel/PDF
- [ ] Alertas de preço por email
- [ ] Integração com APIs de imobiliárias
- [ ] Histórico de preços por imóvel
- [ ] Previsão de preços com ML
- [ ] App mobile React Native
- [ ] Suporte a outras cidades (SP, BH, etc)

## 📧 Contato & Suporte

Para dúvidas sobre dados ITBI RJ, consulte:
- Portal: https://data.rio/
- Prefeitura: https://fazenda.prefeitura.rio/

## 🙏 Agradecimentos

- Prefeitura da Cidade do Rio de Janeiro pelos dados públicos
- OpenStreetMap e comunidade de open-source
- Inspiração em Bel Radar, ITBI Map e Atlas Dados

---

**Desenvolvido com ❤️ para análise de mercado imobiliário do Rio de Janeiro**
