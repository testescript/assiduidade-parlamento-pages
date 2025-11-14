// Configuração da fonte de dados - VERSÃO GITHUB PAGES
// Modo: 'static' (GitHub Pages - dados JSON)
const CONFIG = {
  mode: 'static', // Modo estático para GitHub Pages
  apiUrl: 'http://127.0.0.1:5001', // Ignorado em modo static
  dataPath: 'data/' // Caminho relativo para os JSON
};

// Função helper para fazer fetch da fonte correta
async function fetchData(endpoint) {
  if (CONFIG.mode === 'api') {
    // Modo API: fazer pedido HTTP ao backend Flask
    const response = await fetch(`${CONFIG.apiUrl}${endpoint}`);
    return await response.json();
  } else {
    // Modo static: carregar JSON local
    const jsonFile = mapEndpointToFile(endpoint);
    const response = await fetch(jsonFile);
    return await response.json();
  }
}

// Mapear endpoints da API para ficheiros JSON
function mapEndpointToFile(endpoint) {
  const base = CONFIG.dataPath;
  
  // Remover query params para o mapeamento
  const [path] = endpoint.split('?');
  
  const mapping = {
    '/deputados': `${base}deputados.json`,
    '/sessoes': `${base}sessoes.json`,
    '/estatisticas/sessoes': `${base}estatisticas_sessoes.json`,
    '/atividade/deputados': `${base}atividades.json`,
    '/atividade/agenda': `${base}agenda.json`,
    '/substituicoes': `${base}substituicoes.json`,
    '/estatisticas/analise-avancada': `${base}estatisticas_sessoes.json`,
    '/atividade/estatisticas': `${base}atividades.json`
  };
  
  return mapping[path] || `${base}deputados.json`;
}
