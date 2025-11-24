document.addEventListener('DOMContentLoaded', function() {

    // 1. Tenta esconder opções vazias (seu código original)
    try {
        const emptyRadio = document.querySelector('.custom-radio-item input[value=""]');
        if (emptyRadio) {
            emptyRadio.closest('.custom-radio-item').style.display = 'none';
        }
    } catch (e) {
        // Ignora erros
    }

    // --- ELEMENTOS DA PÁGINA ---
    const placeholder = document.getElementById('placeholder-detalhe');
    const formDetalhe = document.getElementById('form-detalhe');
    const btnCancelar = document.getElementById('btn-cancelar');
    const listaTriagens = document.getElementById('lista-triagens');

    // Campos visuais do formulário
    const campoIdPaciente = document.getElementById('detalhe-id-paciente');
    const campoNome = document.getElementById('detalhe-nome');
    const campoHora = document.getElementById('detalhe-hora');
    const campoSugestaoIA = document.getElementById('detalhe-sugestao-ia');

    // --- NOVOS ELEMENTOS (SIM/NÃO) ---
    const radioSim = document.getElementById('radio-sim');
    const radioNao = document.getElementById('radio-nao');
    const containerReclassificacao = document.getElementById('container-reclassificacao');

    let itemAtivo = null;
    // Verifica se a lista existe para evitar erros em outras páginas
    if (!listaTriagens) return;
    
    const urlTemplate = listaTriagens.getAttribute('data-url-template');

    // ============================================================
    // FUNÇÕES AUXILIARES (LÓGICA NOVA)
    // ============================================================

    // 1. Controla visibilidade da lista baseada no Sim/Não
    function toggleReclassificacao() {
        if (!radioSim || !radioNao) return;

        if (radioNao.checked) {
            containerReclassificacao.style.display = 'block';
            
            // --- MUDANÇA AQUI: LIMPAR SELEÇÃO ---
            // Se o usuário disse "Não", limpamos tudo para forçar ele a escolher
            const radios = document.querySelectorAll('input[name="classificacao"]');
            radios.forEach(radio => {
                radio.checked = false;
            });

        } else {
            containerReclassificacao.style.display = 'none';
            // Se voltou para SIM, seleciona a opção da IA automaticamente de novo
            // para garantir que o formulário envie o dado certo
            matchIaClassification(); 
        }
    }

    // 2. Marca o radio button da lista que corresponde ao texto da IA
    function matchIaClassification() {
        // Pega o texto visual do badge (ex: "Muito Urgente")
        const textoIA = campoSugestaoIA.textContent.trim();
        
        // Função para limpar texto (tira acentos e minúsculas) para comparação
        const normalize = str => str.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
        const targetText = normalize(textoIA);

        const radios = document.querySelectorAll('input[name="classificacao"]');
        
        radios.forEach(radio => {
            // Procura o label associado ao radio
            const label = document.querySelector(`label[for="${radio.id}"]`);
            if (label) {
                const labelText = normalize(label.textContent.trim());
                // Compara se o texto do label bate com o texto da IA
                if (labelText === targetText || targetText.includes(labelText) || labelText.includes(targetText)) {
                    radio.checked = true;
                }
            }
        });
    }

    // Adiciona os eventos de clique no Sim/Não
    if (radioSim && radioNao) {
        radioSim.addEventListener('change', toggleReclassificacao);
        radioNao.addEventListener('change', toggleReclassificacao);
    }

    // ============================================================
    // EVENTO PRINCIPAL: CLIQUE NA LISTA DE PACIENTES
    // ============================================================
    listaTriagens.addEventListener('click', function(e) {
        e.preventDefault();
        const item = e.target.closest('.item-triagem');
        if (!item) return;

        // Pega os dados dos atributos data-*
        const pk = item.getAttribute('data-triagem-pk');
        const nome = item.getAttribute('data-nome');
        const hora = item.getAttribute('data-hora');
        
        // DICA: O atributo data-sugestao traz o slug (ex: muito-urgente).
        // Mas para exibir bonito, vamos pegar o texto que já está dentro do span do card.
        const badgeOriginal = item.querySelector('.classificacao-badge');
        const textoSugestaoBonito = badgeOriginal ? badgeOriginal.textContent.trim() : item.getAttribute('data-sugestao');
        const slugSugestao = item.getAttribute('data-sugestao'); // ex: muito-urgente

        // (Estilo) Marca o item como ativo
        if (itemAtivo) {
            itemAtivo.classList.remove('active');
        }
        item.classList.add('active');
        itemAtivo = item;

        // Troca a visualização
        placeholder.style.display = 'none';
        formDetalhe.style.display = 'block';

        // 1. Preenche os dados visuais
        campoIdPaciente.textContent = pk; 
        campoNome.textContent = nome;
        campoHora.textContent = hora;
        
        // 2. Preenche o badge da sugestão da IA
        campoSugestaoIA.textContent = textoSugestaoBonito;
        campoSugestaoIA.className = 'classificacao-badge'; // Reseta classes
        campoSugestaoIA.classList.add(slugSugestao); // Adiciona a cor correta

        // 3. Define o 'action' do formulário para salvar neste ID
        formDetalhe.action = urlTemplate.replace('9999', pk); 

        // 4. Limpa justificativa
        const campoJustificativa = document.getElementById('id_justificativa'); 
        if (campoJustificativa) campoJustificativa.value = '';

        // --- LÓGICA NOVA: RESETAR ESTADO ---
        if (radioSim) {
            radioSim.checked = true; // Reseta para "Sim"
            toggleReclassificacao(); // Esconde a lista
            matchIaClassification(); // Marca a opção certa no formulário oculto
        }
    });

    // Lógica do botão "Cancelar"
    if (btnCancelar) {
        btnCancelar.addEventListener('click', function(e) {
            e.preventDefault();
            
            formDetalhe.style.display = 'none';
            placeholder.style.display = 'flex'; // Use flex para centralizar o ícone

            if (itemAtivo) {
                itemAtivo.classList.remove('active');
                itemAtivo = null;
            }
        });
    }
});