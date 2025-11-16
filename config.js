// Configuração da fonte de dados
// Modo: 'api' (desenvolvimento local) ou 'static' (GitHub Pages)
const CONFIG = {
  mode: 'api', // Modo API para desenvolvimento local
  apiUrl: 'http://127.0.0.1:5001',
  dataPath: 'data/' // Caminho relativo para os JSON
};

// Função helper para fazer fetch da fonte correta
async function fetchData(endpoint) {
  if (CONFIG.mode === 'static') {
    // Mapear endpoints da API para arquivos JSON
    const endpointMap = {
      '/deputados': 'deputados.json',
      '/sessoes': 'sessoes.json',
      '/estatisticas/sessoes': 'estatisticas_sessoes.json',
      '/atividade/deputados': 'atividades.json',
      '/atividade/agenda': 'agenda.json',
      '/atividade/estatisticas': 'atividades.json', // Usar mesmo arquivo
      '/substituicoes': 'substituicoes.json'
    };
    
    // Lidar com endpoint dinâmico de detalhes de deputado
    if (endpoint.startsWith('/deputados/') && endpoint.endsWith('/detalhes')) {
      const nomeDeputado = endpoint.split('/')[2]; // Extrair nome do deputado
      const response = await fetch(`${CONFIG.dataPath}deputados_detalhes.json`);
      const allData = await response.json();
      
      if (allData.ok && allData.deputados_detalhes[nomeDeputado]) {
        return { ok: true, ...allData.deputados_detalhes[nomeDeputado] };
      } else {
        return { ok: false, mensagem: "Deputado não encontrado" };
      }
    }
    
    const jsonFile = endpointMap[endpoint];
    if (!jsonFile) {
      console.warn(`Endpoint não mapeado: ${endpoint}`);
      return { ok: false };
    }
    
    const response = await fetch(`${CONFIG.dataPath}${jsonFile}`);
    return response.json();
  } else {
    // Modo API (desenvolvimento)
    const response = await fetch(`${CONFIG.apiUrl}${endpoint}`);
    return response.json();
  }
}
