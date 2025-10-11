document.addEventListener('DOMContentLoaded', function() {
    // Verifique se os seletores aqui correspondem EXATAMENTE aos IDs do HTML
    const tipoUsuarioSelect = document.querySelector('#id_tipo_usuario');
    const medicoFieldsWrapper = document.querySelector('#medico-fields-wrapper');

    const tipoUsuarioElement = document.querySelector('#id_tipo_usuario');
    if (tipoUsuarioElement) {
        const choices = new Choices(tipoUsuarioElement, {
            searchEnabled: false, // Desabilita a busca, já que são poucas opções
            itemSelectText: 'Pressionar para selecionar', // Melhora a acessibilidade
            shouldSort: false, // Garante que a ordem das opções seja a original
            allowHTML: true
        });
    }

    function toggleCamposMedico() {
        if (!tipoUsuarioSelect || !medicoFieldsWrapper) {
            // Se um dos elementos não for encontrado, o código para aqui.
            return; 
        }

        const shouldShow = tipoUsuarioSelect.value === 'MEDICO';
        medicoFieldsWrapper.classList.toggle('visible', shouldShow);
    }

    if (tipoUsuarioSelect) {
        tipoUsuarioSelect.addEventListener('change', toggleCamposMedico);
        toggleCamposMedico();
    }

    const cpfElement = document.querySelector('#id_cpf');
    if (cpfElement) {
        const cpfMaskOptions = {
            mask: '000.000.000-00'
        };
        const mask = IMask(cpfElement, cpfMaskOptions);
    }
});

    

   