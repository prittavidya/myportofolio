let toastTimer;

function showToast(title, message, type = 'normal', duration = 3000) {
    const toastComponent = document.getElementById('toast-component');
    const toastTitle = document.getElementById('toast-title');
    const toastMessage = document.getElementById('toast-message');

    if (!toastComponent) return;

    // Hapus class tipe sebelumnya
    toastComponent.classList.remove('toast-success', 'toast-error', 'toast-normal');

    // Terapkan class baru berdasarkan tipe
    if (type === 'success') {
        toastComponent.classList.add('toast-success');
    } else if (type === 'error') {
        toastComponent.classList.add('toast-error');
    } else {
        toastComponent.classList.add('toast-normal');
    }

    // textContent (bukan innerHTML) agar pesan tidak pernah dieksekusi sebagai HTML
    toastTitle.textContent = title;
    toastMessage.textContent = message;

    // Batalkan timer sebelumnya jika toast masih tampil
    clearTimeout(toastTimer);

    // Animasi muncul
    if (!toastComponent.matches(':popover-open')) {
        toastComponent.showPopover();
        void toastComponent.offsetHeight; // paksa browser menghitung style agar transisi berjalan
    }
    toastComponent.classList.remove('toast-hidden');
    toastComponent.classList.add('toast-show');

    // Animasi hilang otomatis
    toastTimer = setTimeout(() => {
        toastComponent.classList.remove('toast-show');
        toastComponent.classList.add('toast-hidden');
        toastTimer = setTimeout(() => toastComponent.hidePopover(), 300);
    }, duration);
}

// Tampilkan pesan flash Django (setelah redirect hapus/edit/register) sebagai toast
function showDjangoMessages() {
    const dataElement = document.getElementById('django-messages');
    if (!dataElement) return;

    let messages = [];
    try {
        messages = JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error('Gagal membaca pesan Django:', error);
        return;
    }
    if (messages.length === 0) return;

    const isError = messages.some(message => message.tags.includes('error'));
    showToast(
        isError ? 'Gagal' : 'Berhasil',
        messages.map(message => message.text).join(' '),
        isError ? 'error' : 'success',
    );
}

showDjangoMessages();
