/**
 * Halaman Achievements: daftar via AJAX, pencarian dengan debouncing,
 * tambah data lewat modal + Fetch API, serta star dan hapus tanpa reload.
 *
 * Konfigurasi (URL dan peran) dibaca dari atribut data-* pada #achievements-app
 * sehingga berkas ini tidak bergantung pada tag template Django.
 * Membutuhkan utils.js (escapeHtml, getCookie, urlFor) dan toast.js (showToast).
 */
(function () {
    const app = document.getElementById('achievements-app');
    if (!app) return;

    const config = {
        listUrl: app.dataset.listUrl,
        detailUrl: app.dataset.detailUrl,
        editUrl: app.dataset.editUrl,
        starUrl: app.dataset.starUrl,
        deleteUrl: app.dataset.deleteUrl,
        loginUrl: app.dataset.loginUrl,
        isAuthenticated: app.dataset.isAuthenticated === 'true',
        canEdit: app.dataset.canEdit === 'true',
        canManage: app.dataset.canManage === 'true',
    };

    const SEARCH_DEBOUNCE_DELAY = 300;
    let searchDebounceTimer;
    let achievementsAbortController;

    // Elemen DOM yang selalu ada untuk semua peran
    const loadingState = document.getElementById('loading');
    const errorState = document.getElementById('error');
    const emptyState = document.getElementById('empty');
    const emptyMessage = document.getElementById('empty-message');
    const gridContainer = document.getElementById('grid');
    const searchForm = document.getElementById('achievement-search-form');
    const searchInput = document.getElementById('search-input');

    function currentPageUrl() {
        return window.location.pathname + window.location.search;
    }

    // Menyembunyikan/Menampilkan section halaman
    function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) {
        loadingState.classList.toggle('hide', !showLoading);
        errorState.classList.toggle('hide', !showError);
        emptyState.classList.toggle('hide', !showEmpty);
        gridContainer.classList.toggle('hide', !showGrid);
    }

    // ---------- Render kartu ----------

    function buildStarHtml(id, achievement) {
        const count = Number(achievement.star_count) || 0;

        if (!config.isAuthenticated) {
            const loginUrl = `${config.loginUrl}?next=${encodeURIComponent(currentPageUrl())}`;
            return `
                <a href="${escapeHtml(loginUrl)}" class="button button-star" title="Login untuk memberi star">
                    <span aria-hidden="true">☆</span> Login untuk Star
                    <span class="star-count">${count}</span>
                </a>`;
        }

        const starred = achievement.is_starred === true;
        return `
            <form method="post" action="${escapeHtml(urlFor(config.starUrl, id))}"
                  class="star-form js-star-form" data-id="${escapeHtml(id)}">
                <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCookie('csrftoken'))}">
                <input type="hidden" name="next" value="${escapeHtml(currentPageUrl())}">
                <button type="submit"
                        class="button button-star${starred ? ' is-starred' : ''}"
                        aria-pressed="${starred}"
                        title="${starred ? 'Batalkan star' : 'Beri star'}">
                    <span aria-hidden="true">${starred ? '★' : '☆'}</span> ${starred ? 'Unstar' : 'Star'}
                    <span class="star-count">${count}</span>
                </button>
            </form>`;
    }

    function buildAchievementCardElement(item) {
        const achievement = item.fields;
        const id = item.pk;

        const articleElement = document.createElement('article');
        articleElement.className = 'experience-card';

        const descriptionHtml = achievement.description
            ? `<p class="experience-description">${escapeHtml(achievement.description)}</p>`
            : '';

        const editHtml = config.canEdit
            ? `<div class="project-actions">
                   <a href="${escapeHtml(urlFor(config.editUrl, id))}" class="button button-secondary">Edit Pencapaian</a>
               </div>`
            : '';

        const deleteHtml = config.canManage
            ? `<div class="project-actions">
                   <p class="experience-status">
                       <button type="button"
                               class="button button-danger js-delete-achievement"
                               popovertarget="delete-achievement-modal"
                               data-delete-url="${escapeHtml(urlFor(config.deleteUrl, id))}"
                               data-name="${escapeHtml(achievement.name)}"
                               aria-label="Hapus ${escapeHtml(achievement.name)}"
                               title="Hapus pencapaian">Hapus Pencapaian</button>
                   </p>
               </div>`
            : '';

        articleElement.innerHTML = `
            <span class="experience-category">${escapeHtml(achievement.year)}</span>
            <h2><a href="${escapeHtml(urlFor(config.detailUrl, id))}" class="card-title-link">${escapeHtml(achievement.name)}</a></h2>
            <p class="experience-description">Diberikan oleh: ${escapeHtml(achievement.issuer)}</p>
            ${descriptionHtml}
            <div class="project-card-actions">
                ${buildStarHtml(id, achievement)}
                ${editHtml}
                ${deleteHtml}
            </div>
        `;
        return articleElement;
    }

    // ---------- Ambil data ----------

    async function fetchAchievements(searchQuery = '') {
        // Batalkan permintaan lama agar hasil pencarian lama tidak menimpa yang terbaru
        if (achievementsAbortController) achievementsAbortController.abort();
        achievementsAbortController = new AbortController();

        try {
            displayPageSection({ showLoading: true });

            const url = searchQuery
                ? `${config.listUrl}?name=${encodeURIComponent(searchQuery)}`
                : config.listUrl;

            const response = await fetch(url, {
                headers: { 'Accept': 'application/json' },
                signal: achievementsAbortController.signal,
            });

            // fetch() tidak reject untuk status 4xx/5xx, jadi status dicek manual
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const achievementData = await response.json();

            if (achievementData.length === 0) {
                emptyMessage.textContent = searchQuery
                    ? 'Tidak ada pencapaian dengan nama tersebut.'
                    : 'Belum ada achievement yang ditambahkan.';
                displayPageSection({ showEmpty: true });
            } else {
                gridContainer.replaceChildren(...achievementData.map(buildAchievementCardElement));
                displayPageSection({ showGrid: true });
            }
        } catch (error) {
            if (error.name === 'AbortError') return;
            console.error('Error loading achievements:', error);
            displayPageSection({ showError: true });
        }
    }

    // ---------- Pencarian dengan debouncing ----------

    // Kata kunci disimpan di URL (?name=) agar bisa di-refresh/dibagikan
    function searchAchievements() {
        const query = searchInput.value.trim();
        const newUrl = query ? `?name=${encodeURIComponent(query)}` : window.location.pathname;
        history.replaceState(null, '', newUrl);
        fetchAchievements(query);
    }

    searchInput.addEventListener('input', function () {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(searchAchievements, SEARCH_DEBOUNCE_DELAY);
    });

    searchForm.addEventListener('submit', function (event) {
        event.preventDefault(); // Mencegah reload halaman
        clearTimeout(searchDebounceTimer);
        searchAchievements();
    });

    // ---------- Tambah data (hanya ada untuk pemilik) ----------

    // Modal hanya dirender untuk pemilik, jadi cek dulu keberadaannya
    // agar skrip tidak berhenti di halaman pengguna lain.
    const achievementForm = document.getElementById('achievement-form');
    const addModal = document.getElementById('add-achievement-modal');

    function fieldLabel(field) {
        const label = achievementForm.querySelector(`label[for="id_${CSS.escape(field)}"]`);
        return label ? label.textContent.trim() : field;
    }

    function clearFormErrors() {
        achievementForm.querySelectorAll('[data-errors-for]').forEach(el => el.replaceChildren());
    }

    // Tampilkan error validasi dari server di bawah field masing-masing (textContent, aman dari XSS)
    function showFormErrors(errors) {
        Object.entries(errors).forEach(([field, messages]) => {
            const container = achievementForm.querySelector(`[data-errors-for="${CSS.escape(field)}"]`);
            if (!container) return;
            messages.forEach(message => {
                const p = document.createElement('p');
                p.className = 'form-error';
                p.textContent = message;
                container.appendChild(p);
            });
        });
    }

    // Ringkasan error validasi untuk toast, misalnya "Tahun: Enter a whole number."
    function summarizeErrors(errors) {
        return Object.entries(errors)
            .map(([field, messages]) => {
                const text = messages.join(' ');
                return field === '__all__' ? text : `${fieldLabel(field)}: ${text}`;
            })
            .join(' ');
    }

    async function submitAchievementForm(event) {
        event.preventDefault();
        clearFormErrors();

        const submitButton = achievementForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            const { ok, data: result } = await postForm(
                achievementForm.dataset.ajaxUrl, new FormData(achievementForm),
            );

            if (!ok) {
                const errors = result.errors || {};
                showFormErrors(errors);
                const detail = summarizeErrors(errors);
                showToast(
                    'Gagal menyimpan',
                    detail || result.message || 'Terjadi kesalahan pada server.',
                    'error',
                    5000,
                );
                return;
            }

            achievementForm.reset();
            addModal.hidePopover();
            showToast('Berhasil', result.message, 'success');
            fetchAchievements(searchInput.value.trim()); // perbarui daftar tanpa reload
        } catch (error) {
            console.error('Error creating achievement:', error);
            showToast('Gagal menyimpan', 'Tidak dapat terhubung ke server.', 'error');
        } finally {
            submitButton.disabled = false;
        }
    }

    if (achievementForm && addModal) {
        achievementForm.addEventListener('submit', submitAchievementForm);
        // Error lama dibersihkan saat modal ditutup agar form bersih ketika dibuka lagi
        addModal.addEventListener('toggle', function (event) {
            if (event.newState === 'closed') clearFormErrors();
        });
    }

    // ---------- Star lewat AJAX (pengguna yang sudah login) ----------

    // Kartu dibuat ulang setiap fetch, jadi listener dipasang sekali di grid (event delegation)
    gridContainer.addEventListener('submit', async function (event) {
        const starForm = event.target.closest('.js-star-form');
        if (!starForm) return;
        event.preventDefault();

        const button = starForm.querySelector('button');
        button.disabled = true; // cegah klik ganda selagi permintaan berjalan

        try {
            const { ok, data } = await postForm(starForm.action, new FormData(starForm));
            if (!ok) {
                showToast('Gagal', data.message || 'Star gagal diperbarui.', 'error');
                button.disabled = false;
                return;
            }

            // Ganti hanya form star pada kartu ini, lalu kembalikan fokus ke tombolnya
            const wrapper = document.createElement('div');
            wrapper.innerHTML = buildStarHtml(starForm.dataset.id, data);
            const newForm = wrapper.firstElementChild;
            starForm.replaceWith(newForm);
            newForm.querySelector('button').focus();
            showToast(data.is_starred ? 'Star diberikan' : 'Star dibatalkan', data.message, 'normal');
        } catch (error) {
            console.error('Error toggling star:', error);
            showToast('Gagal', 'Tidak dapat terhubung ke server.', 'error');
            button.disabled = false;
        }
    });

    // ---------- Hapus lewat AJAX dengan modal bersama (hanya ada untuk pemilik) ----------

    const deleteModal = document.getElementById('delete-achievement-modal');
    const deleteForm = document.getElementById('delete-achievement-form');
    const deleteName = document.getElementById('delete-achievement-name');

    if (deleteModal && deleteForm && deleteName) {
        // Isi modal sesuai kartu yang tombol hapusnya diklik
        gridContainer.addEventListener('click', function (event) {
            const button = event.target.closest('.js-delete-achievement');
            if (!button) return;
            deleteForm.action = button.dataset.deleteUrl;
            deleteName.textContent = button.dataset.name;
        });

        deleteForm.addEventListener('submit', async function (event) {
            event.preventDefault();
            const submitButton = deleteForm.querySelector('button[type="submit"]');
            submitButton.disabled = true;

            try {
                const { ok, data } = await postForm(deleteForm.action, new FormData(deleteForm));
                if (!ok) {
                    showToast('Gagal menghapus', data.message || 'Terjadi kesalahan pada server.', 'error');
                    return;
                }
                deleteModal.hidePopover();
                showToast('Berhasil', data.message, 'success');
                // Muat ulang daftar agar kondisi kosong tampil jika kartu terakhir dihapus
                fetchAchievements(searchInput.value.trim());
            } catch (error) {
                console.error('Error deleting achievement:', error);
                showToast('Gagal menghapus', 'Tidak dapat terhubung ke server.', 'error');
            } finally {
                submitButton.disabled = false;
            }
        });
    }

    // Start application
    fetchAchievements(searchInput.value.trim());
})();
