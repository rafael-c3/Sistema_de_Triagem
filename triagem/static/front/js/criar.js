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
    

});