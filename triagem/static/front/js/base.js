document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. Lógica para pegar o nome e gerar as iniciais ---
    const fullNameInput = document.getElementById('user-full-name');
    const initialsSpan = document.getElementById('user-initials');

    if (fullNameInput && initialsSpan) {
        const fullName = fullNameInput.value;
        const nameParts = fullName.split(' ').filter(part => part);
        let initials = '';

        if (nameParts.length > 0) {
            initials += nameParts[0].charAt(0);
            if (nameParts.length > 1) {
                initials += nameParts[nameParts.length - 1].charAt(0);
            }
        }
        initialsSpan.textContent = initials.toUpperCase();
    }

    // --- 2. Lógica para abrir e fechar o menu dropdown ---
    const avatarButton = document.getElementById('avatar-button');
    const dropdownMenu = document.getElementById('dropdown-menu');

    if (avatarButton && dropdownMenu) {
        avatarButton.addEventListener('click', function(event) {
            event.stopPropagation();
            dropdownMenu.classList.toggle('show');
        });

        window.addEventListener('click', function(event) {
            if (dropdownMenu.classList.contains('show')) {
                dropdownMenu.classList.remove('show');
            }
        });

        dropdownMenu.addEventListener('click', function(event) {
            event.stopPropagation();
        });
    }
});