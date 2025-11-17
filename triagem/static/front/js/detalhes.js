/* Arquivo: static/front/js/detalhes.js
   Funções específicas para a página de detalhes do prontuário
*/

// --- 1. Função para mostrar o nome do arquivo no upload de anexos ---
// Esta função é chamada diretamente pelo onchange="" no HTML
function mostrarNomeArquivo(input) {
    const display = document.getElementById('file-name-display');
    
    if (input.files && input.files.length > 0) {
        const nome = input.files[0].name;
        // Exibe o nome com uma cor de destaque
        display.innerHTML = `<span style="color: #0d6efd;">Arquivo selecionado: <strong>${nome}</strong></span>`;
    } else {
        display.textContent = '';
    }
}

// --- 2. Lógica do botão "Adicionar Observação" ---
// O 'DOMContentLoaded' garante que o HTML carregou antes de rodar o script
document.addEventListener('DOMContentLoaded', function() {
    
    const toggleBtn = document.getElementById('toggle-form-btn');
    const formContainer = document.getElementById('nova-observacao-form');

    // Só adiciona o evento se os elementos existirem na página (evita erros)
    if (toggleBtn && formContainer) {
        toggleBtn.addEventListener('click', () => {
            // Quando o botão for clicado...
            formContainer.style.display = 'block'; // Mostra o formulário
            toggleBtn.style.display = 'none';      // Esconde o próprio botão
        });
    }

});