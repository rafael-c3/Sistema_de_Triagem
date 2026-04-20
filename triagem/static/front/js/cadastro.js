document.addEventListener('DOMContentLoaded', function() {
    // 1. Seletores
    const tipoUsuarioSelect = document.querySelector('#id_tipo_usuario');
    const medicoFieldsWrapper = document.querySelector('#medico-fields-wrapper');
    const cpfElement = document.querySelector('#id_cpf');
    
    // Seletores dos campos específicos dentro do wrapper
    const campoCrm = document.querySelector('#id_crm')?.closest('.form-group');
    const campoCoren = document.querySelector('#id_coren')?.closest('.form-group');
    const campoEspecializacao = document.querySelector('#id_especializacao')?.closest('.form-group');

    // Seletores para os dropdowns
    const selectUF = document.querySelector('#id_uf_registro');
    const selectEsp = document.querySelector('#id_especializacao');

    // 2. Inicialização Única do Choices.js
    // Tipo de Usuário
    if (tipoUsuarioSelect) {
        new Choices(tipoUsuarioSelect, {
            searchEnabled: false,
            itemSelectText: 'Pressionar para selecionar',
            shouldSort: false,
            allowHTML: true,
            position: 'auto'
        });
    }

    // Registro Profissional (UF)
    if (selectUF) {
        new Choices(selectUF, {
            searchEnabled: true,
            itemSelectText: '',
            shouldSort: false,
            allowHTML: true,
            position: 'auto'
        });
    }

    // Especialização
    if (selectEsp) {
        new Choices(selectEsp, {
            searchEnabled: true,
            itemSelectText: '',
            allowHTML: true,
            position: 'bottom', // Força abrir para baixo agora que a lista é pequena
            shouldSort: false, // Evita que o menu seja cortado no fundo da tela
        });
    }

    // 3. Função de Lógica de Exibição
    function toggleCamposProfissional() {
        if (!tipoUsuarioSelect || !medicoFieldsWrapper) return;

        const valor = tipoUsuarioSelect.value.toUpperCase();
        
        // Controla a animação do container pai
        if (valor === 'MEDICO' || valor === 'ENFERMEIRO' || valor === 'TEC_ENFERMEIRO') {
            medicoFieldsWrapper.classList.add('visible');
        } else {
            medicoFieldsWrapper.classList.remove('visible');
        }

        // Reseta os campos internos
        if (campoCrm) campoCrm.style.display = 'none';
        if (campoCoren) campoCoren.style.display = 'none';
        if (campoEspecializacao) campoEspecializacao.style.display = 'none';

        // Mostra o campo correto baseado no Models.py
        if (valor === 'MEDICO') { 
            if (campoCrm) campoCrm.style.display = 'block';
            if (campoEspecializacao) campoEspecializacao.style.display = 'block'; 
        } else if (valor === 'ENFERMEIRO' || valor === 'TEC_ENFERMEIRO') {
            if (campoCoren) campoCoren.style.display = 'block';
        } 
    }

    // 4. Listeners
    if (tipoUsuarioSelect) {
        tipoUsuarioSelect.addEventListener('change', toggleCamposProfissional);
        toggleCamposProfissional(); // Executa ao carregar
    }

    // 5. Máscara de CPF
    if (cpfElement) {
        IMask(cpfElement, { mask: '000.000.000-00' });
    }
});