document.addEventListener('DOMContentLoaded', () => {

    // --- 1. MÁSCARA AUTOMÁTICA PARA O CAMPO CPF ---
    const cpfInput = document.getElementById('id_cpf');

    if (cpfInput) {
        cpfInput.addEventListener('input', () => {
            // Remove tudo que não for dígito
            let value = cpfInput.value.replace(/\D/g, '');
            
            // Limita o tamanho para 11 dígitos
            value = value.substring(0, 11);

            // Aplica a formatação do CPF (###.###.###-##)
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            
            cpfInput.value = value;
        });
    }


    // Encontra os elementos do slider
    const painSlider = document.getElementById('id_dor');
    const painValueDisplay = document.getElementById('pain-value');

    // Função que atualiza tanto o texto quanto a cor da barra
    function updateSliderLook(value) {
        // 1. Atualiza o texto (ex: "7 / 10")
        if (painValueDisplay) {
            painValueDisplay.textContent = value + ' / 10';
        }

        // 2. Lógica para pintar a barra (A NOVIDADE ESTÁ AQUI)
        if (painSlider) {
            const min = painSlider.min;
            const max = painSlider.max;
            const percentage = ((value - min) / (max - min)) * 100;

            const fillColor = '#0d6efd'; // Cor do preenchimento (azul)
            const trackColor = '#e9ecef'; // Cor do trilho (cinza)

            // Aplica um gradiente linear que simula o preenchimento
            painSlider.style.background = `linear-gradient(to right, ${fillColor} ${percentage}%, ${trackColor} ${percentage}%)`;
        }
    }

    // Verifica se o slider existe na página
    if (painSlider) {
        // Define o visual inicial ao carregar a página
        updateSliderLook(painSlider.value);

        // Adiciona o "ouvinte" que chama a função toda vez que o slider se move
        painSlider.addEventListener('input', (event) => {
            updateSliderLook(event.target.value);
        });
    }
    

});