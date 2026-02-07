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
    // --- 1.5. MÁSCARA AUTOMÁTICA PARA O CAMPO CPF (RESPONSÁVEL) ---
    // AQUI ESTÁ A PARTE NOVA QUE VOCÊ PEDIU
    const cpfRespInput = document.getElementById('id_cpf_responsavel');

    if (cpfRespInput) {
        cpfRespInput.addEventListener('input', () => {
            // Remove tudo que não for dígito
            let value = cpfRespInput.value.replace(/\D/g, '');
            
            // Limita o tamanho para 11 dígitos
            value = value.substring(0, 11);

            // Aplica a formatação do CPF (###.###.###-##)
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d)/, '$1.$2');
            value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
            
            cpfRespInput.value = value;
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

    const campoCep = document.getElementById('id_cep');

        // Se o campo não existir (ex: está em outra aba), o script para aqui pra não dar erro
        if (!campoCep) return;

        // 2. Adiciona o evento "blur" (quando o usuário clica fora do campo)
        campoCep.addEventListener('blur', function() {
            
            // Remove tudo que não é número para validar
            let cep = this.value.replace(/\D/g, '');

            // Verifica se o CEP tem tamanho válido (8 dígitos)
            if (cep.length === 8) {
                
                // Mostra pro usuário que está carregando (opcional, mas elegante)
                document.getElementById('id_logradouro').value = "...";
                document.getElementById('id_bairro').value = "...";
                document.getElementById('id_cidade').value = "...";

                // 3. Chama a API do ViaCEP
                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            // 4. Preenche os campos automaticamente
                            // AJUSTE OS IDs ABAIXO SE OS SEUS FOREM DIFERENTES
                            if(document.getElementById('id_endereco')) 
                                document.getElementById('id_endereco').value = data.logradouro;
                            
                            if(document.getElementById('id_bairro')) 
                                document.getElementById('id_bairro').value = data.bairro;
                            
                            if(document.getElementById('id_cidade')) 
                                document.getElementById('id_cidade').value = data.localidade;
                            
                            if(document.getElementById('id_uf')) 
                                document.getElementById('id_uf').value = data.uf;
                            
                            // Foca no campo de número para agilizar
                            if(document.getElementById('id_numero'))
                                document.getElementById('id_numero').focus();

                        } else {
                            alert("CEP não encontrado.");
                            limparFormularioCep();
                        }
                    })
                    .catch(error => {
                        console.error("Erro na requisição ViaCEP:", error);
                        alert("Erro ao buscar CEP. Verifique sua conexão.");
                        limparFormularioCep();
                    });
            } else {
                // Se o CEP for inválido, limpa
                limparFormularioCep();
            }
        });

        function limparFormularioCep() {
            // Função auxiliar para limpar se der erro
            if(document.getElementById('id_logradouro')) document.getElementById('id_logradouro').value = "";
            if(document.getElementById('id_bairro')) document.getElementById('id_bairro').value = "";
            if(document.getElementById('id_cidade')) document.getElementById('id_cidade').value = "";
            if(document.getElementById('id_uf')) document.getElementById('id_uf').value = "";
        }
    

});