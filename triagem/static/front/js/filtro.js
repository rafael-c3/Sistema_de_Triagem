// Versão Atualizada com Menu de Filtros

document.addEventListener('DOMContentLoaded', () => {

    // --- CÓDIGO NOVO PARA O MENU DE FILTROS ---
    const toggleFiltrosBtn = document.getElementById('toggle-filtros');
    const filtrosAvancadosDiv = document.getElementById('filtros-avancados');

    if (toggleFiltrosBtn && filtrosAvancadosDiv) {
        // Evento para MOSTRAR/ESCONDER o menu ao clicar no botão
        toggleFiltrosBtn.addEventListener('click', (event) => {
            // event.stopPropagation() impede que o clique no botão feche o menu imediatamente
            event.stopPropagation(); 
            filtrosAvancadosDiv.classList.toggle('visivel');
        });

        // Evento para FECHAR o menu se o usuário clicar em qualquer lugar fora dele
        document.addEventListener('click', (event) => {
            const isClickInsideMenu = filtrosAvancadosDiv.contains(event.target);
            const isClickOnToggleButton = toggleFiltrosBtn.contains(event.target);

            if (!isClickInsideMenu && !isClickOnToggleButton) {
                filtrosAvancadosDiv.classList.remove('visivel');
            }
        });
    }
    // --- FIM DO CÓDIGO NOVO ---


    // --- SEU CÓDIGO ANTIGO E FUNCIONAL (inicia aqui) ---

    // Seleciona todos os elementos necessários da página
    const buscaInput = document.getElementById('busca-input');
    const filtroStatusBtns = document.querySelectorAll('.filtro-status');
    const filtroCorBtns = document.querySelectorAll('.filtro-cor');
    const cardsPacientes = document.querySelectorAll('.card-paciente');
    const btnsAtender = document.querySelectorAll('.btn-atender');

    // Objeto para guardar os filtros ativos
    let filtrosAtivos = {
        busca: '',
        status: 'todos',
        cor: 'todos'
    };

    // Função principal que aplica os filtros
    const aplicarFiltros = () => {
        cardsPacientes.forEach(card => {
            const nomePaciente = card.querySelector('strong').textContent.toLowerCase();
            const idPaciente = card.querySelector('small').textContent.toLowerCase();
            const statusCard = card.dataset.status;
            const corCard = card.dataset.cor;

            const matchBusca = nomePaciente.includes(filtrosAtivos.busca) || idPaciente.includes(filtrosAtivos.busca);
            const matchStatus = filtrosAtivos.status === 'todos' || filtrosAtivos.status === statusCard;
            const matchCor = filtrosAtivos.cor === 'todos' || filtrosAtivos.cor === corCard;

            if (matchBusca && matchStatus && matchCor) {
                card.style.display = 'block'; // Mostra o card
            } else {
                card.style.display = 'none'; // Esconde o card
            }
        });
    };

    // Adiciona o evento de 'input' para a barra de busca
    if (buscaInput) {
        buscaInput.addEventListener('input', (e) => {
            filtrosAtivos.busca = e.target.value.toLowerCase();
            aplicarFiltros();
        });
    }

    // Adiciona o evento de 'click' para os botões de filtro de STATUS
    filtroStatusBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filtroStatusBtns.forEach(b => b.classList.remove('ativo'));
            btn.classList.add('ativo');
            filtrosAtivos.status = btn.dataset.status;
            aplicarFiltros();
        });
    });

    // Adiciona o evento de 'click' para os botões de filtro de COR
    filtroCorBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filtroCorBtns.forEach(b => b.classList.remove('ativo'));
            btn.classList.add('ativo');
            filtrosAtivos.cor = btn.dataset.cor;
            aplicarFiltros();
        });
    });

});