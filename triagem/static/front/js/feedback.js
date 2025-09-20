// ==========================================================
// CÓDIGO JS CORRIGIDO - MOSTRAR/ESCONDER CAMPO
// (Substitua a versão anterior por esta)
// ==========================================================

// Encontra os elementos que vamos usar
const radiosAvaliacao = document.querySelectorAll('input[name="triagem_correta"]');
const grupoClassificacaoSugerida = document.getElementById('classificacao-sugerida-group');

// A função que decide se mostra ou esconde o campo
function toggleCampoDeSugestao() {
    // Encontra o radio que está selecionado
    const radioSelecionado = document.querySelector('input[name="triagem_correta"]:checked');

    // Se nenhum radio estiver selecionado (por segurança), esconde o campo
    if (!radioSelecionado) {
        if (grupoClassificacaoSugerida) {
            grupoClassificacaoSugerida.classList.add('hidden');
        }
        return; // Sai da função
    }

    // Pega o valor do radio que está selecionado
    const valorSelecionado = radioSelecionado.value;

    // Se o valor for 'False' (que corresponde ao "Não"), mostra o campo
    if (valorSelecionado === 'False') {
        grupoClassificacaoSugerida.classList.remove('hidden');
    } 
    // Senão (se for 'True' ou outro valor), esconde o campo
    else {
        grupoClassificacaoSugerida.classList.add('hidden');
    }
}

// Verifica se os elementos realmente existem na página antes de continuar
if (radiosAvaliacao.length > 0 && grupoClassificacaoSugerida) {
    // 1. Adiciona um "ouvinte" para cada botão de rádio
    radiosAvaliacao.forEach(radio => {
        radio.addEventListener('change', toggleCampoDeSugestao);
    });

    // 2. *** A CORREÇÃO PRINCIPAL ESTÁ AQUI ***
    // Executa a função uma vez assim que o script é carregado
    toggleCampoDeSugestao();
}