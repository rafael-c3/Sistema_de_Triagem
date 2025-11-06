document.addEventListener('DOMContentLoaded', function() {

    try {
        document.querySelector('.custom-radio-item input[value=""]').closest('.custom-radio-item').style.display = 'none';
    } catch (e) {
        // Não faz nada se não encontrar, evita quebrar o script
    }
    // Elementos da página
    const placeholder = document.getElementById('placeholder-detalhe');
    const formDetalhe = document.getElementById('form-detalhe');
    const btnCancelar = document.getElementById('btn-cancelar');
    const listaTriagens = document.getElementById('lista-triagens');

    // --- (INÍCIO DA MUDANÇA) ---
    // Campos do formulário que o JS vai preencher
    const campoIdPaciente = document.getElementById('detalhe-id-paciente');
    const campoNome = document.getElementById('detalhe-nome');
    const campoHora = document.getElementById('detalhe-hora');
    const campoSugestaoIA = document.getElementById('detalhe-sugestao-ia');
    // --- (FIM DA MUDANÇA) ---
    
    let itemAtivo = null;
    const urlTemplate = listaTriagens.getAttribute('data-url-template');

    listaTriagens.addEventListener('click', function(e) {
        e.preventDefault();
        const item = e.target.closest('.item-triagem');
        if (!item) return;

        // Pega os dados que guardamos nos atributos 'data-*'
        const pk = item.getAttribute('data-triagem-pk');
        const nome = item.getAttribute('data-nome');
        const sugestao = item.getAttribute('data-sugestao');
        const hora = item.getAttribute('data-hora');
        
        // (Estilo) Marca o item como ativo
        if (itemAtivo) {
            itemAtivo.classList.remove('active');
        }
        item.classList.add('active');
        itemAtivo = item;

        placeholder.style.display = 'none';
        formDetalhe.style.display = 'block';

        // --- (INÍCIO DA MUDANÇA) ---
        // 1. Preenche os dados no formulário
        // (Vamos usar o PK do paciente como ID, adapte se tiver outro)
        campoIdPaciente.textContent = `P-${pk}`; 
        campoNome.textContent = nome;
        campoHora.textContent = hora;
        
        // 2. Preenche o badge da sugestão da IA
        campoSugestaoIA.textContent = sugestao;
        // Limpa classes de cor antigas e adiciona a nova
        campoSugestaoIA.className = 'classificacao-badge'; 
        campoSugestaoIA.classList.add(sugestao.toLowerCase().replace(/ /g, '-')); // ex: "muito-urgente"
        // --- (FIM DA MUDANÇA) ---


        // 3. Define o 'action' do formulário
        formDetalhe.action = urlTemplate.replace('9999', pk); 

        // 4. Pré-seleciona o radio button
        // Esta lógica funciona perfeitamente com os novos radio buttons
        const radioSugerido = document.querySelector(`input[name="classificacao"][value="${sugestao}"]`);
        if (radioSugerido) {
            radioSugerido.checked = true;
        }
        
        // 5. Limpa o campo de justificativa
        const campoJustificativa = document.getElementById('id_justificativa'); 
        if (campoJustificativa) {
            campoJustificativa.value = '';
        }
    });

    // Lógica do botão "Cancelar"
    btnCancelar.addEventListener('click', function(e) {
        e.preventDefault();
        
        formDetalhe.style.display = 'none';
        placeholder.style.display = 'block';

        if (itemAtivo) {
            itemAtivo.classList.remove('active');
            itemAtivo = null;
        }
    });
});