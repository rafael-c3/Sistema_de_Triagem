document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. LÓGICA DAS ABAS (existente) ---
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => item.classList.remove('active'));
            contents.forEach(item => item.classList.remove('active'));
            tab.classList.add('active');
            const targetId = tab.getAttribute('data-tab');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });

    // --- 2. NOVA LÓGICA DE UPLOAD AJAX ---
    
    // Seletores
    const uploadContainer = document.querySelector('.avatar-upload-container');
    const photoInput = document.getElementById('id_foto_perfil'); // O <input type="file"> real
    const uploadForm = document.getElementById('avatar-upload-form');
    const profilePicDisplay = document.getElementById('profile-pic-display');
    
    // Verifica se os elementos existem (só para quem está vendo o próprio perfil)
    if (uploadContainer && photoInput && uploadForm && profilePicDisplay) {
        
        // 1. Clicar no container "clica" no input de arquivo escondido
        uploadContainer.addEventListener('click', function() {
            photoInput.click();
        });

        // 2. Quando o usuário escolhe um arquivo (evento 'change')
        photoInput.addEventListener('change', function() {
            if (photoInput.files && photoInput.files.length > 0) {
                // Arquivo foi selecionado, vamos enviá-lo
                
                // Pega o token CSRF do formulário
                const csrfToken = uploadForm.querySelector('input[name="csrfmiddlewaretoken"]').value;
                
                // Cria o FormData para enviar o arquivo
                const formData = new FormData(uploadForm);
                
                // Mostra um "carregando" (deixando a foto opaca)
                profilePicDisplay.style.opacity = '0.5';

                // Usamos fetch() para enviar o formulário via AJAX
                fetch(uploadForm.action, { // A action do form é a própria URL (hosp:perfil)
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrfToken, // Token de segurança do Django
                        'X-Requested-With': 'XMLHttpRequest' // Para a view saber que é AJAX
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Sucesso! Atualiza a imagem na tela.
                        // Adicionamos um "?t=" para evitar cache do navegador
                        profilePicDisplay.src = data.new_photo_url + '?t=' + new Date().getTime();
                        
                        // Recarrega a página para que o botão "Remover Foto" apareça
                        // É a forma mais simples de atualizar o estado
                        location.reload(); 
                    } else {
                        console.error('Upload falhou:', data.error);
                        alert('Houve um erro ao enviar a foto.');
                    }
                })
                .catch(error => {
                    console.error('Fetch error:', error);
                    alert('Houve um erro de conexão.');
                })
                .finally(() => {
                    // Tira o "carregando"
                    profilePicDisplay.style.opacity = '1';
                    // Limpa o input de arquivo para poder enviar o mesmo arquivo de novo
                    photoInput.value = ''; 
                });
            }
        });
    }

    // --- 3. NOVA LÓGICA DE REMOVER FOTO AJAX ---
    const clearBtn = document.getElementById('clear-photo-ajax-btn');
    
    if (clearBtn) {
        clearBtn.addEventListener('click', function() {
            if (!confirm('Tem certeza que deseja remover sua foto de perfil?')) {
                return; // Cancela se o usuário clicar em "Não"
            }

            const clearUrl = clearBtn.dataset.url; // Pega a URL do 'data-url'
            const csrfToken = uploadForm ? uploadForm.querySelector('input[name="csrfmiddlewaretoken"]').value : document.querySelector('input[name="csrfmiddlewaretoken"]').value;

            profilePicDisplay.style.opacity = '0.5'; // "Carregando"

            fetch(clearUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Atualiza a foto para a padrão
                    profilePicDisplay.src = data.new_photo_url + '?t=' + new Date().getTime();
                    // Remove o botão "Remover Foto" da tela
                    clearBtn.remove();
                } else {
                    console.error('Erro ao remover foto:', data.error);
                    alert('Houve um erro ao remover a foto.');
                }
            })
            .catch(error => console.error('Fetch error:', error))
            .finally(() => {
                profilePicDisplay.style.opacity = '1';
            });
        });
    }
});