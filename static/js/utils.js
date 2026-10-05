/**
 * Helper bersama untuk semua halaman yang memakai AJAX.
 * Dimuat lewat base.html sebelum skrip khusus halaman.
 */

/**
 * Mengubah karakter khusus HTML menjadi entity agar data dari server tampil
 * sebagai teks biasa, bukan dieksekusi sebagai HTML/JavaScript (mencegah XSS).
 * Wajib dipakai untuk setiap nilai yang disisipkan lewat innerHTML/template literal.
 */
function escapeHtml(value) {
    return String(value ?? '')
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}

/**
 * Membaca nilai cookie berdasarkan nama, misalnya getCookie('csrftoken')
 * untuk header X-CSRFToken pada permintaan POST.
 */
function getCookie(name) {
    const prefix = `${name}=`;
    const cookie = document.cookie
        .split(';')
        .map(part => part.trim())
        .find(part => part.startsWith(prefix));
    return cookie ? decodeURIComponent(cookie.slice(prefix.length)) : null;
}

/**
 * Mengganti UUID dummy pada URL hasil {% url %} dengan ID asli.
 */
const DUMMY_ID = '00000000-0000-0000-0000-000000000000';

function urlFor(template, id) {
    return template.replace(DUMMY_ID, encodeURIComponent(id));
}
