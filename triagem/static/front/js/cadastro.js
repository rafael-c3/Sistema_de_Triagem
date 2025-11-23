document.addEventListener('DOMContentLoaded', function() {
    // 1. Seletores
    const tipoUsuarioSelect = document.querySelector('#id_tipo_usuario');
    const medicoFieldsWrapper = document.querySelector('#medico-fields-wrapper');
    // Seletor para a Label do campo de registro (busca pelo atributo 'for')
    const labelRegistro = document.querySelector('label[for="id_registro_profissional"]');
    const cpfElement = document.querySelector('#id_cpf');

    // 2. Inicialização do Choices.js
    if (tipoUsuarioSelect) {
        const choices = new Choices(tipoUsuarioSelect, {
            searchEnabled: false,
            itemSelectText: 'Pressionar para selecionar',
            shouldSort: false,
            allowHTML: true
        });
    }

    // 3. Função Principal de Lógica
    function toggleCamposProfissional() {
        if (!tipoUsuarioSelect || !medicoFieldsWrapper) return;

        const valor = tipoUsuarioSelect.value;

        // VERIFIQUE SE OS VALORES ABAIXO BATEM COM SEU MODELS.PY
        if (valor === 'MEDICO') {
            // Mostra o campo
            medicoFieldsWrapper.classList.add('visible'); 
            // Muda o texto para CRM
            if (labelRegistro) labelRegistro.textContent = 'CRM'; 

        } else if (valor === 'ENFERMEIRO' || valor === 'TEC_ENFERMEIRO') {
            // Mostra o campo
            medicoFieldsWrapper.classList.add('visible'); 
            // Muda o texto para COREN
            if (labelRegistro) labelRegistro.textContent = 'COREN';

        } else {
            // Esconde o campo para outros tipos
            medicoFieldsWrapper.classList.remove('visible');
        }
    }

    // 4. Listeners (Ouvintes de eventos)
    if (tipoUsuarioSelect) {
        // O Choices.js geralmente propaga o evento 'change' para o select original
        tipoUsuarioSelect.addEventListener('change', toggleCamposProfissional);
        
        // Executa ao carregar a página (caso venha de um erro de validação)
        toggleCamposProfissional();
    }

    // 5. Máscara de CPF
    if (cpfElement) {
        const cpfMaskOptions = {
            mask: '000.000.000-00'
        };
        const mask = IMask(cpfElement, cpfMaskOptions);
    }
});

    

   