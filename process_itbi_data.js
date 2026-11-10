#!/usr/bin/env node

/**
 * Script para processar dados ITBI Excel em JSON
 * Execução: node process_itbi_data.js
 *
 * 1. Baixe os arquivos Excel da Prefeitura RJ
 * 2. Renomeie como: itbi_data.xlsx
 * 3. Execute este script
 * 4. Resultado: itbi_data.json
 */

const XLSX = require('xlsx');
const fs = require('fs');
const path = require('path');

function processITBIData() {
  const inputFile = path.join(__dirname, 'itbi_data.xlsx');

  if (!fs.existsSync(inputFile)) {
    console.error('❌ Arquivo itbi_data.xlsx não encontrado!');
    console.error('Passos:');
    console.error('1. Baixe em: https://fazenda.prefeitura.rio/itbi-valores-medios-por-m2-de-transacoes-imobiliarias-por-trecho-de-logradouro/');
    console.error('2. Salve como: itbi_data.xlsx');
    console.error('3. Execute: node process_itbi_data.js');
    process.exit(1);
  }

  console.log('📂 Lendo arquivo ITBI...');
  const workbook = XLSX.readFile(inputFile);
  const sheetName = workbook.SheetNames[0];
  const worksheet = workbook.Sheets[sheetName];
  const rawData = XLSX.utils.sheet_to_json(worksheet);

  console.log(`✅ Lido ${rawData.length} registros`);
  console.log('🔄 Processando dados...');

  const processedData = rawData
    .filter(row => row.LOGRADOURO && row.NUMERO)
    .map((row, index) => ({
      id: index,
      logradouro: row.LOGRADOURO?.trim() || '',
      numero: String(row.NUMERO)?.trim() || '',
      bairro: row.BAIRRO?.trim() || 'Desconhecido',
      zona: inferZona(row.BAIRRO),
      cep: row.CEP?.trim() || '',
      preco: parseFloat(row['VALOR MÉDIO']) || 0,
      m2: parseFloat(row['M²']) || 0,
      data_transacao: row.DATA ? new Date(row.DATA).toISOString().split('T')[0] : '',
      valor_m2: parseFloat(row['VALOR M²']) || 0,
      volume_transacoes: parseInt(row['VOLUME']) || 1,
      latitude: null,
      longitude: null
    }))
    .filter(item => item.preco > 0 && item.m2 > 0);

  console.log(`✅ Processado ${processedData.length} registros válidos`);
  console.log('💾 Salvando JSON...');

  const outputFile = path.join(__dirname, 'itbi_data.json');
  fs.writeFileSync(outputFile, JSON.stringify(processedData, null, 2));

  console.log(`✅ Salvo em: ${outputFile}`);
  console.log(`📊 Estatísticas:`);
  console.log(`   - Total: ${processedData.length}`);
  console.log(`   - Preço médio: R$ ${(processedData.reduce((a, b) => a + b.preco, 0) / processedData.length).toLocaleString('pt-BR')}`);
  console.log(`   - Valor/m² médio: R$ ${(processedData.reduce((a, b) => a + b.valor_m2, 0) / processedData.length).toLocaleString('pt-BR')}`);
}

function inferZona(bairro) {
  const zonas = {
    'Zona Sul': ['Copacabana', 'Ipanema', 'Leblon', 'Lagoa', 'Botafogo', 'Flamengo', 'Leme', 'Vidigal', 'São Conrado'],
    'Zona Norte': ['Jacarepaguá', 'Barra da Tijuca', 'Recreio dos Bandeirantes', 'Vargem Pequena', 'Vargem Grande'],
    'Zona Oeste': ['Santa Cruz', 'Sepetiba', 'Inhaúma', 'Deodoro', 'Cidade Nova'],
    'Centro': ['Centro', 'Lapa', 'Gloria', 'Catete', 'Cinelândia', 'Saúde', 'Gamboa']
  };

  for (const [zona, bairros] of Object.entries(zonas)) {
    if (bairros.some(b => bairro?.includes(b))) return zona;
  }
  return 'Indefinida';
}

processITBIData();
