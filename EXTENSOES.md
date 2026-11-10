# 🔧 Guia de Extensões e Customizações

Você pode expandir a ferramenta de várias formas. Aqui estão alguns exemplos:

## 1. 🎨 Alterar Cores e Design

### Editar a paleta de cores
Abra `itbi_visualizer.html` e procure por:

```css
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
```

Substitua por suas cores:
```css
.header {
    background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);
}
```

### Alterar cores de mapas (preço/m²)
Procure por esta seção:
```javascript
if (pricePerM2 > 6000) color = '#f5576c';      // Muito caro
else if (pricePerM2 > 4000) color = '#ffa502'; // Caro
else if (pricePerM2 > 2500) color = '#43e97b'; // Normal
```

## 2. 📍 Adicionar Novas Zonas

Na função `generateSampleData()`:

```javascript
const bairros = [
    { name: 'Niterói', zone: 'Grande Rio', lat: -22.9068, lng: -43.0929 },
    { name: 'Duque de Caxias', zone: 'Baixada', lat: -22.7847, lng: -43.3139 },
    // Adicione seus bairros aqui
];
```

Depois, adicione nas opções de zona em `populateFilters()`:
```javascript
<option value="Grande Rio">Grande Rio</option>
<option value="Baixada">Baixada</option>
```

## 3. 📊 Adicionar Novo Gráfico

Exemplo: Adicionar gráfico de "Preço por Ano"

### Passo 1: Criar tab no HTML
```html
<button class="tab-btn" onclick="app.switchTab('trends')">📈 Tendências</button>

<!-- Conteúdo -->
<div id="trends-tab" class="tab-content">
    <div class="chart-container">
        <h6>Evolução de Preços por Ano</h6>
        <canvas id="priceByYearChart"></canvas>
    </div>
</div>
```

### Passo 2: Criar função de gráfico
```javascript
updatePriceByYear() {
    const yearData = {};
    
    this.filteredData.forEach(item => {
        const year = item.data_transacao.substring(0, 4);
        if (!yearData[year]) {
            yearData[year] = { count: 0, totalPrice: 0 };
        }
        yearData[year].count++;
        yearData[year].totalPrice += item.preco;
    });

    const ctx = document.getElementById('priceByYearChart').getContext('2d');
    const years = Object.keys(yearData).sort();
    const avgPrices = years.map(y => yearData[y].totalPrice / yearData[y].count);

    if (this.charts.priceByYear) this.charts.priceByYear.destroy();

    this.charts.priceByYear = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Preço Médio',
                data: avgPrices,
                borderColor: '#667eea',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}
```

### Passo 3: Chamar no switchTab
```javascript
if (tab === 'trends') {
    this.updatePriceByYear();
}
```

## 4. 💾 Exportar Dados em Excel

Instale biblioteca:
```bash
npm install xlsx
```

Adicione função:
```javascript
exportToExcel() {
    const worksheet = XLSX.utils.json_to_sheet(this.filteredData);
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "ITBI");
    XLSX.writeFile(workbook, "itbi_dados.xlsx");
}
```

Adicione botão no HTML:
```html
<button class="btn btn-success btn-sm" onclick="app.exportToExcel()">
    ⬇️ Exportar Excel
</button>
```

## 5. 🔔 Sistema de Alertas

Salvar filtros e monitorar novos dados:

```javascript
saveAlert() {
    const alertName = prompt("Nome do alerta:");
    const alert = {
        name: alertName,
        filters: {
            bairro: document.getElementById('filterBairro').value,
            priceMin: parseFloat(document.getElementById('priceMin').value),
            priceMax: parseFloat(document.getElementById('priceMax').value)
        },
        createdAt: new Date().toISOString()
    };
    
    let alerts = JSON.parse(localStorage.getItem('itbi_alerts') || '[]');
    alerts.push(alert);
    localStorage.setItem('itbi_alerts', JSON.stringify(alerts));
    
    alert("✅ Alerta salvo!");
}
```

## 6. 🌐 Integrar com Google Maps Embed

No popup do marcador, em vez de apenas link:

```javascript
const popupContent = `
    <div class="popup-content">
        <h6>${item.logradouro}, ${item.numero}</h6>
        <p><strong>${item.bairro}</strong></p>
        <iframe 
            width="100%" 
            height="150" 
            style="border:0" 
            loading="lazy" 
            src="https://www.google.com/maps/embed/v1/place?key=YOUR_KEY&q=${item.latitude},${item.longitude}">
        </iframe>
    </div>
`;
```

## 7. 🤖 Adicionar Machine Learning (Previsão)

Use biblioteca TensorFlow.js:

```html
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@4.0.0"></script>
```

Exemplo simples de previsão:
```javascript
predictPrice(m2, zona) {
    const zoneMultiplier = {
        'Zona Sul': 1.5,
        'Zona Norte': 0.8,
        'Centro': 1.0
    };
    
    const basePrice = 2500; // R$/m² base
    const predicted = m2 * basePrice * zoneMultiplier[zona];
    return predicted;
}
```

## 8. 📱 Tornar Mobile-First

Remova o layout flex e use grid:

```css
@media (max-width: 768px) {
    .container-main {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        order: 2;
    }

    .map-container {
        width: 100%;
        height: 60vh;
        order: 1;
    }

    .results-container {
        width: 100%;
        height: 40vh;
        order: 3;
    }
}
```

## 9. 🔐 Adicionar Autenticação (Google)

Para versão web hospedada:

```html
<script src="https://accounts.google.com/gsi/client" async defer></script>
```

```javascript
function handleCredentialResponse(response) {
    console.log("Encoded JWT ID token: " + response.credential);
    app.init();
}

window.onload = function () {
    google.accounts.id.initialize({
        client_id: 'YOUR_CLIENT_ID',
        callback: handleCredentialResponse
    });
};
```

## 10. ☁️ Sincronizar com Nuvem

Exemplo com Firebase:

```html
<script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-database.js"></script>
```

```javascript
const db = firebase.database();

saveUserData() {
    const user = firebase.auth().currentUser;
    db.ref('users/' + user.uid).set({
        alerts: this.userAlerts,
        savedFilters: this.savedFilters,
        lastViewed: new Date().toISOString()
    });
}
```

## 11. 🎬 Adicionar GIF de Tutorial

```html
<button onclick="app.showTutorial()">🎥 Tutorial</button>

<div id="tutorialModal" class="modal">
    <img src="tutorial.gif" alt="Tutorial">
</div>
```

## 12. 📈 Adicionar Heatmap de Preços

Use Leaflet.heat:

```html
<script src="https://cdn.jsdelivr.net/npm/leaflet-heat@0.2.0/dist/leaflet-heat.js"></script>
```

```javascript
addHeatmap() {
    const heatData = this.filteredData.map(item => 
        [item.latitude, item.longitude, item.valor_m2 / 10000]
    );
    L.heatLayer(heatData, { radius: 25 }).addTo(this.map);
}
```

## 13. 🔗 Adicionar Share em Redes Sociais

```javascript
shareResults() {
    const url = window.location.href;
    const text = `Encontrei imóveis legais em ${this.filteredData.length} endereços no Rio!`;
    
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`);
}
```

## 14. 📸 Screenshot de Resultados

```html
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
```

```javascript
async takeScreenshot() {
    const canvas = await html2canvas(document.getElementById('results-container'));
    const image = canvas.toDataURL('image/png');
    
    const link = document.createElement('a');
    link.href = image;
    link.download = 'resultados_itbi.png';
    link.click();
}
```

## 15. 🌍 Adicionar Suporte a Outras Cidades

```javascript
const cities = {
    'rio': {
        name: 'Rio de Janeiro',
        defaultZoom: 11,
        center: [-23.5505, -43.2056],
        dataUrl: 'https://...'
    },
    'sp': {
        name: 'São Paulo',
        defaultZoom: 11,
        center: [-23.5505, -46.6333],
        dataUrl: 'https://...'
    }
};

switchCity(cityCode) {
    const city = cities[cityCode];
    this.map.setView(city.center, city.defaultZoom);
    this.loadDataForCity(city.dataUrl);
}
```

---

## 🚀 Próximas Ideias

- [ ] Integração com Stripe para versão paga
- [ ] Dashboard em tempo real com WebSocket
- [ ] AR (Realidade Aumentada) para visualizar imóveis
- [ ] IA para previsão de preços
- [ ] Integration com APIs de imobiliárias
- [ ] App PWA (Progressive Web App)
- [ ] Versão mobile nativa (React Native)
- [ ] Podcast/Vídeo automation

---

**Divirta-se expandindo! 🎉**
