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

    const telInput = document.getElementById('id_telefone');
    if (telInput) {
        telInput.addEventListener('input', function() {
            // Remove tudo que não for dígito
            let value = this.value.replace(/\D/g, '');
            
            // Limita a 11 caracteres (DDD + 9 dígitos)
            value = value.substring(0, 11);

            // Aplica a formatação (##) #####-#### ou (##) ####-####
            if (value.length > 10) {
                value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, '($1) $2-$3');
            } else if (value.length > 6) {
                value = value.replace(/^(\d{2})(\d{4})(\d{0,4}).*/, '($1) $2-$3');
            } else if (value.length > 2) {
                value = value.replace(/^(\d{2})(\d{0,5})/, '($1) $2');
            } else if (value.length > 0) {
                value = value.replace(/^(\d*)/, '($1');
            }
            this.value = value;
        });
    }




   // =========================================
    // MÁSCARA E BUSCA AUTOMÁTICA DE CEP
    // =========================================
    const campoCep = document.getElementById('id_cep');

    if (campoCep) {

        // 1. A MÁSCARA (Formata XXXXX-XXX enquanto o usuário digita)
        campoCep.addEventListener('input', function () {
            let value = this.value.replace(/\D/g, '');
            value = value.substring(0, 8);
            if (value.length > 5) {
                value = value.replace(/^(\d{5})(\d{1,3}).*/, '$1-$2');
            }
            this.value = value;
        });

        // 2. A BUSCA NA API (Puxa os dados quando ele clica fora do campo)
        campoCep.addEventListener('blur', function () {
            let cep = this.value.replace(/\D/g, '');

            if (cep.length === 8) {
                document.getElementById('id_logradouro') && (document.getElementById('id_logradouro').value = "...");
                document.getElementById('id_bairro') && (document.getElementById('id_bairro').value = "...");
                document.getElementById('id_cidade') && (document.getElementById('id_cidade').value = "...");

                fetch(`https://viacep.com.br/ws/${cep}/json/`)
                    .then(response => response.json())
                    .then(data => {
                        if (!data.erro) {
                            if (document.getElementById('id_endereco')) document.getElementById('id_endereco').value = data.logradouro;
                            if (document.getElementById('id_bairro')) document.getElementById('id_bairro').value = data.bairro;
                            if (document.getElementById('id_cidade')) document.getElementById('id_cidade').value = data.localidade;
                            if (document.getElementById('id_uf')) document.getElementById('id_uf').value = data.uf;
                            if (document.getElementById('id_numero')) document.getElementById('id_numero').focus();
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
                limparFormularioCep();
            }
        });
    }

    function limparFormularioCep() {
        if (document.getElementById('id_logradouro')) document.getElementById('id_logradouro').value = "";
        if (document.getElementById('id_bairro')) document.getElementById('id_bairro').value = "";
        if (document.getElementById('id_cidade')) document.getElementById('id_cidade').value = "";
        if (document.getElementById('id_uf')) document.getElementById('id_uf').value = "";
    }

    // =========================================
    // CONTROLE DINÂMICO DOS BOTÕES E VALIDAÇÃO
    // =========================================

    const camposObrigatoriosProximo = [
        'id_nome', 'id_data_nascimento', 'id_sexo', 'id_cpf',
        'id_temperatura', 'id_pressao_sistolica', 'id_pressao_diastolica',
        'id_pulso', 'id_frequenciaRespiratoria', 'id_saturacao'
    ];

    const camposObrigatoriosFinalizar = [
        ...camposObrigatoriosProximo,
        'id_telefone', 'id_cep', 'id_cidade', 'id_uf',
        'id_endereco', 'id_numero', 'id_bairro', 'id_queixa'
    ];

    window.validarCampos = function (validarTudo = false) {
        let formularioValido = true;
        const campos = validarTudo ? camposObrigatoriosFinalizar : camposObrigatoriosProximo;

        campos.forEach(id => {
            const campo = document.getElementById(id);
            if (campo) {
                if (!campo.value.trim()) {
                    formularioValido = false;
                    campo.classList.add('error');

                    const removerErro = function () { this.classList.remove('error'); };
                    campo.addEventListener('input', removerErro, { once: true });
                    campo.addEventListener('change', removerErro, { once: true });
                }
            }
        });

        if (!formularioValido) {
            const msg = validarTudo
                ? "⚠️ Por favor, preencha todos os campos obrigatórios (incluindo Endereço e Queixa) para finalizar."
                : "⚠️ Por favor, preencha os Dados Pessoais e Sinais Vitais antes de prosseguir.";
            alert(msg);
        }
        return formularioValido;
    };

    function verificarPreenchimento() {
        const botaoProximo = document.getElementById('btn-proximo');
        const botaoFinalizar = document.getElementById('btn-finalizar');

        const step1Ok = camposObrigatoriosProximo.every(id => {
            const campo = document.getElementById(id);
            return campo && campo.value.trim() !== "";
        });

        const step2Ok = camposObrigatoriosFinalizar.every(id => {
            const campo = document.getElementById(id);
            return campo && campo.value.trim() !== "";
        });

        if (botaoProximo) botaoProximo.disabled = !step1Ok;
        if (botaoFinalizar) botaoFinalizar.disabled = !step2Ok;
    }

    // --- LÓGICA DO BOTÃO PRÓXIMO ---
    const botaoProximoEl = document.getElementById('btn-proximo');
    if (botaoProximoEl) {
        botaoProximoEl.addEventListener('click', (e) => {
            e.preventDefault();
            if (window.validarCampos(false)) {
                const tabEndereco = document.querySelector('.tab-button-paciente[onclick*="endereco"]');
                const tabQueixaBtn = document.getElementById('tab-btn-queixa');
                if (tabEndereco) tabEndereco.click();
                if (tabQueixaBtn) tabQueixaBtn.click();
            }
        });
    }

    // --- BLOQUEIO FINAL DO FORMULÁRIO E VERIFICAÇÃO AO DIGITAR ---
    const formTriagem = document.querySelector('.form-triagem');
    if (formTriagem) {
        formTriagem.addEventListener('submit', (e) => {
            if (!window.validarCampos(true)) {
                e.preventDefault();
            }
        });

        // Essas duas linhas fazem a mágica de observar o usuário digitando
        formTriagem.addEventListener('input', verificarPreenchimento);
        formTriagem.addEventListener('change', verificarPreenchimento);

        // Roda uma vez quando a página abre para deixar o botão cinza de cara
        verificarPreenchimento();
    }

    
});