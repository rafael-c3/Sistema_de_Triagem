// Garante que o script só vai rodar depois que a página inteira carregar
document.addEventListener('DOMContentLoaded', function() {

    // 1. Seleciona os elementos do DOM (incluindo os novos)
    const pacienteSearch = document.getElementById('paciente-search');
    const classificacaoFilter = document.getElementById('classificacao-filter');
    const avaliacaoFilter = document.getElementById('avaliacao-filter');
    const tipoUsuarioFilter = document.getElementById('tipo-usuario-filter');
    const feedbackTbody = document.getElementById('feedback-tbody');
    const tableRows = feedbackTbody.querySelectorAll('tr[data-paciente]'); // Seleciona apenas as linhas com dados
    
    // Novos elementos selecionados
    const noResultsRow = document.getElementById('no-results-row');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');

    // 2. Função principal que aplica os filtros
    function applyFilters() {
        const pacienteValue = pacienteSearch.value.toLowerCase().trim();
        const classificacaoValue = classificacaoFilter.value;
        const avaliacaoValue = avaliacaoFilter.value;
        const tipoUsuarioValue = tipoUsuarioFilter.value;
        
        let visibleRowsCount = 0;

        // 3. Percorre cada linha da tabela
        tableRows.forEach(row => {
            const rowPaciente = row.getAttribute('data-paciente');
            const rowClassificacao = row.getAttribute('data-classificacao');
            const rowAvaliacao = row.getAttribute('data-avaliacao');
            const rowTipoUsuario = row.getAttribute('data-tipo-usuario');

            const pacienteMatch = pacienteValue === '' || rowPaciente.includes(pacienteValue);
            const classificacaoMatch = classificacaoValue === '' || rowClassificacao === classificacaoValue;
            const avaliacaoMatch = avaliacaoValue === '' || rowAvaliacao === avaliacaoValue;
            const tipoUsuarioMatch = tipoUsuarioValue === '' || rowTipoUsuario === tipoUsuarioValue;

            if (pacienteMatch && classificacaoMatch && avaliacaoMatch && tipoUsuarioMatch) {
                row.style.display = ''; // Mostra a linha
                visibleRowsCount++;   // Incrementa o contador de linhas visíveis
            } else {
                row.style.display = 'none'; // Esconde a linha
            }
        });

        // NOVO: Lógica para mostrar a mensagem de "nenhum resultado"
        if (visibleRowsCount === 0) {
            noResultsRow.style.display = 'table-row'; // Mostra a mensagem
        } else {
            noResultsRow.style.display = 'none';      // Esconde a mensagem
        }
    }

    // NOVO: Função para limpar os filtros
    function clearFilters() {
        pacienteSearch.value = '';
        classificacaoFilter.selectedIndex = 0;
        avaliacaoFilter.selectedIndex = 0;
        tipoUsuarioFilter.selectedIndex = 0;
        
        // Aplica os filtros novamente (que agora estão limpos)
        applyFilters();
    }

    // 6. Adiciona os "escutadores" de eventos
    pacienteSearch.addEventListener('input', applyFilters);
    classificacaoFilter.addEventListener('change', applyFilters);
    avaliacaoFilter.addEventListener('change', applyFilters);
    tipoUsuarioFilter.addEventListener('change', applyFilters);
    
    // NOVO: Adiciona o evento de clique para o botão de limpar
    clearFiltersBtn.addEventListener('click', clearFilters);

    const modal = document.getElementById('feedback-modal');
    if (modal) {
        const closeModalBtn = document.getElementById('close-modal-btn');
        const viewButtons = document.querySelectorAll('.btn-ver');
        
        const modalPaciente = document.getElementById('modal-paciente');
        const modalFeedbackCount = document.getElementById('modal-feedback-count');
        const modalQueixa = document.getElementById('modal-queixa');
        const modalAvaliador = document.getElementById('modal-avaliador');
        const modalData = document.getElementById('modal-data');
        const modalClassificacaoOriginal = document.getElementById('modal-classificacao-original');
        const modalAvaliacao = document.getElementById('modal-avaliacao'); // <--- Nome correto
        const detalheIncorretoDiv = document.getElementById('detalhe-incorreto');
        const modalClassificacaoSugerida = document.getElementById('modal-classificacao-sugerida');
        const modalMotivo = document.getElementById('modal-motivo');

        function closeModal() {
            modal.classList.add('hidden');
        }

        function openModal(event) {
            const button = event.currentTarget;
            
            // Popula os dados no modal
            modalPaciente.textContent = button.dataset.pacienteNome;
            modalQueixa.textContent = button.dataset.queixaPrincipal;
            modalFeedbackCount.textContent = button.dataset.feedbackCount;
            modalAvaliador.textContent = button.dataset.avaliadorNome;
            modalData.textContent = button.dataset.data;
            modalAvaliacao.textContent = button.dataset.triagemCorreta; // <-- CORRIGIDO AQUI

            const classificacaoSlug = button.dataset.classificacaoSlug;
            modalClassificacaoOriginal.textContent = button.dataset.classificacaoOriginal;
            modalClassificacaoOriginal.className = '';
            modalClassificacaoOriginal.classList.add('tag', 'tag-' + classificacaoSlug);

            if (button.dataset.triagemCorreta === 'Incorreta') {
                modalAvaliacao.style.backgroundColor = '#dc3545'; // <-- CORRIGIDO AQUI
                detalheIncorretoDiv.classList.remove('hidden');
                modalClassificacaoSugerida.textContent = button.dataset.classificacaoSugerida;
                modalMotivo.textContent = button.dataset.motivo;
            } else {
                modalAvaliacao.style.backgroundColor = '#198754'; // <-- CORRIGIDO AQUI
                detalheIncorretoDiv.classList.add('hidden');
            }

            modal.classList.remove('hidden');
        }

        viewButtons.forEach(button => {
            button.addEventListener('click', openModal);
        });

        closeModalBtn.addEventListener('click', closeModal);
        
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeModal();
            }
        });
    }

});

