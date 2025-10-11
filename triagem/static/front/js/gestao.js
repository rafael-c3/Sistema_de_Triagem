document.addEventListener('DOMContentLoaded', function () {
    // --- CÓDIGO DAS ABAS (Existente) ---
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            button.classList.add('active');
            const tabId = button.getAttribute('data-tab');
            const activeTabContent = document.getElementById(tabId);
            if (activeTabContent) {
                activeTabContent.classList.add('active');
            }
        });
    });

    // --- CÓDIGO PARA FILTROS COMBINADOS (BUSCA + GÊNERO) ---

    // 1. Seleciona todos os elementos necessários
    const searchInput = document.querySelector('#pacientes .search-box input');
    const tableRows = document.querySelectorAll('#pacientes tbody tr');
    const filterBtn = document.getElementById('filter-btn');
    const filterMenu = document.getElementById('filter-menu');
    const filterOptions = document.querySelectorAll('.filter-option');
    const filterBtnText = document.getElementById('filter-btn-text'); // NOVO: Seleciona o span do texto do botão

    // 2. Variáveis para guardar o estado atual dos filtros
    let currentSearchTerm = '';
    let currentGenderFilter = 'todos';

    // 3. Função principal que aplica AMBOS os filtros
    function applyFilters() {
        tableRows.forEach(row => {
            const nomeCell = row.querySelector('td:nth-child(2)');
            const cpfCell = row.querySelector('td:nth-child(3)');
            const genderCell = row.querySelector('td:nth-child(4)');

            if (nomeCell && cpfCell && genderCell) {
                const cpfText = cpfCell.textContent.replace(/[.\-]/g, '');
                const nomeText = nomeCell.textContent.toLowerCase();
                const genderText = genderCell.textContent.trim().toLowerCase();
                const searchMatch = nomeText.includes(currentSearchTerm) || cpfText.includes(currentSearchTerm);
                const genderMatch = (currentGenderFilter === 'todos') || (genderText === currentGenderFilter);

                if (searchMatch && genderMatch) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            }
        });
    }

    // 4. Evento para a barra de busca
    searchInput.addEventListener('keyup', function() {
        currentSearchTerm = searchInput.value.toLowerCase();
        applyFilters();
    });

    // 5. Evento para o botão de filtro (abrir/fechar menu)
    filterBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        filterMenu.classList.toggle('show');
    });

    // 6. Evento para as opções de filtro de gênero
    filterOptions.forEach(option => {
        option.addEventListener('click', function(event) {
            event.preventDefault();
            currentGenderFilter = this.getAttribute('data-gender');
            
            filterBtnText.textContent = this.textContent; // NOVO: Atualiza o texto do botão com o texto da opção clicada

            applyFilters();
            filterMenu.classList.remove('show');
        });
    });

    // 7. Evento para fechar o menu se clicar fora dele
    window.addEventListener('click', function(event) {
        if (!filterMenu.contains(event.target) && !filterBtn.contains(event.target)) {
            filterMenu.classList.remove('show');
        }
    });
});