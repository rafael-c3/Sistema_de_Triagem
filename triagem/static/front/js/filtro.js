document.addEventListener('DOMContentLoaded', () => {

    // --- 1. SELEÇÃO DE TODOS OS ELEMENTOS ---
    const cardsPacientes = document.querySelectorAll('.card-paciente');
    const buscaInput = document.getElementById('busca-input');
    const filtroDataBtns = document.querySelectorAll('.btn-filtro-data');
    
    // Pega a data de hoje e formata como AAAA-MM-DD para a comparação
    const hoje = new Date();
    const hojeFormatado = `${hoje.getFullYear()}-${String(hoje.getMonth() + 1).padStart(2, '0')}-${String(hoje.getDate()).padStart(2, '0')}`;

    // Objeto que guarda o estado de TODOS os filtros
    let filtrosAtivos = { 
        busca: '', 
        status: 'todos', 
        cor: 'todos',
        periodo: 'todos'
    };

    // --- 2. FUNÇÃO PRINCIPAL DE FILTRAGEM ---
    const aplicarFiltros = () => {
        cardsPacientes.forEach(card => {
            const nomePaciente = card.querySelector('strong').textContent.toLowerCase();
            const idPaciente = card.querySelector('small').textContent.toLowerCase();
            const statusCard = card.dataset.status;
            const corCard = card.dataset.cor;
            const dataCadastroCard = card.dataset.cadastro;

            // Verificação de cada filtro
            const matchBusca = nomePaciente.includes(filtrosAtivos.busca) || idPaciente.includes(filtrosAtivos.busca);
            const matchStatus = filtrosAtivos.status === 'todos' || filtrosAtivos.status.toLowerCase() === statusCard.toLowerCase();
            const matchCor = filtrosAtivos.cor === 'todos' || filtrosAtivos.cor.toLowerCase() === corCard.toLowerCase();
            const matchPeriodo = filtrosAtivos.periodo === 'todos' || dataCadastroCard === hojeFormatado;

            if (matchBusca && matchStatus && matchCor && matchPeriodo) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    };
    
    // --- 3. LÓGICA PARA CADA TIPO DE FILTRO ---

    // Filtro de Busca por texto
    if (buscaInput) {
        buscaInput.addEventListener('input', (e) => {
            filtrosAtivos.busca = e.target.value.toLowerCase();
            aplicarFiltros();
        });
    }

    // Filtros de Menu Dropdown (Status e Risco)
    function setupDropdown(btnId, menuId, filterType, filterClass, filterPrefix) {
        const triggerBtn = document.getElementById(btnId);
        const menu = document.getElementById(menuId);
        if (!triggerBtn || !menu) return;

        const filterButtons = menu.querySelectorAll(filterClass);
        const triggerBtnSpan = triggerBtn.querySelector('span');

        triggerBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            document.querySelectorAll('.filtro-dropdown-menu.visivel').forEach(m => {
                if (m !== menu) m.classList.remove('visivel');
            });
            menu.classList.toggle('visivel');
        });

        filterButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                filtrosAtivos[filterType] = btn.dataset[filterType];
                aplicarFiltros();
                triggerBtnSpan.textContent = `${filterPrefix}: ${btn.textContent}`;
                filterButtons.forEach(b => b.classList.remove('ativo'));
                btn.classList.add('ativo');
                menu.classList.remove('visivel');
            });
        });
    }

    // Configura os dois menus
    setupDropdown('status-filtro-btn', 'status-filtro-menu', 'status', '.filtro-status', 'Status');
    setupDropdown('risco-filtro-btn', 'risco-filtro-menu', 'cor', '.filtro-cor', 'Risco');

    // Novo Filtro de Data
    filtroDataBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filtroDataBtns.forEach(b => b.classList.remove('ativo'));
            btn.classList.add('ativo');
            filtrosAtivos.periodo = btn.dataset.periodo;
            aplicarFiltros();
        });
    });

    // --- 4. AÇÕES FINAIS ---

    // Fecha os menus dropdown se clicar fora
    document.addEventListener('click', () => {
        document.querySelectorAll('.filtro-dropdown-menu.visivel').forEach(m => m.classList.remove('visivel'));
    });

    // Aplica os filtros uma vez no carregamento da página para corrigir o layout
    aplicarFiltros();
});