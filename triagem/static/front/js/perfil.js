// static/front/js/perfil.js

document.addEventListener('DOMContentLoaded', function() {
    // Seleciona todos os botões de aba e todos os painéis de conteúdo
    const tabs = document.querySelectorAll('.tab-button');
    const contents = document.querySelectorAll('.tab-content');

    // Adiciona um evento de clique para cada botão de aba
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // 1. Remove a classe 'active' de todos os botões e conteúdos
            tabs.forEach(item => item.classList.remove('active'));
            contents.forEach(item => item.classList.remove('active'));

            // 2. Adiciona a classe 'active' ao botão que foi clicado
            tab.classList.add('active');

            // 3. Adiciona a classe 'active' ao conteúdo correspondente
            const targetId = tab.getAttribute('data-tab');
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
});