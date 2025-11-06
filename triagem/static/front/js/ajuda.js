// Aguarda o documento carregar
document.addEventListener("DOMContentLoaded", function() {
    
    // Seleciona todos os cabeçalhos do accordion
    const accordionHeaders = document.querySelectorAll(".accordion-header");

    // Adiciona o "escutador" de clique para cada um
    accordionHeaders.forEach(header => {
        
        // Pega o conteúdo correspondente
        const content = header.nextElementSibling;
        
        // Pega o item-pai
        const item = header.parentElement;

        // Pré-configura o primeiro item para vir aberto (como no vídeo)
        if (header.getAttribute("aria-expanded") === "true") {
            item.classList.add("active");
            header.classList.add("active");
            content.classList.add("active");
            // Define a altura máxima inicial com base no conteúdo
            content.style.maxHeight = content.scrollHeight + "px";
        }

        // Adiciona o evento de clique
        header.addEventListener("click", () => {
            
            // Verifica se o item clicado já está ativo
            const isActive = item.classList.contains("active");

            // 1. Primeiro, fecha TODOS os itens
            closeAllItems();

            // 2. Se o item clicado NÃO estava ativo, abre ele
            if (!isActive) {
                item.classList.add("active");
                header.classList.add("active");
                content.classList.add("active");
                header.setAttribute("aria-expanded", "true");
                
                // Define a altura máxima com base no conteúdo
                content.style.maxHeight = content.scrollHeight + "px";
            }
            // Se ele já estava ativo, o closeAllItems() já cuidou de fechar ele.
        });
    });

    // Função auxiliar para fechar todos os itens
    function closeAllItems() {
        accordionHeaders.forEach(header => {
            const item = header.parentElement;
            const content = header.nextElementSibling;
            
            item.classList.remove("active");
            header.classList.remove("active");
            content.classList.remove("active");
            header.setAttribute("aria-expanded", "false");
            content.style.maxHeight = 0; // Fecha o item
        });
    }
});