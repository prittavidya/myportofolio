Nama : Joanna Prittavidya Putri Arianto
NPM : 2506539265
Kelas : PBP A

### Tugas 1

1. Saya menggunakan elemen semantik <section> agar struktur HTML lebih terorganisisir dan mudah dipahami. Penggunaan elemen semantik juga membantu saya mengelompokkan bagian portofolio berdasarkan konten dan fungsinya sehingga lebih mudah ketika distyling menggunakan CSS.
2. Tantangan tata letak yang saya temukan adalah menyesuaikan ukuran dan posisi beberapa elemen agar tetap terlihat rapi saat layar dikecilkan. Awalnya, saya ingin menempatkan elemen secara berdampingan tetapi ketika dikecilkan elemen tersebut menjadi lebih sempit, sehingga saya tempatkan menjadi vertikal. Saya mengevaluasinya dengan melihat apakah suatu elemen masih memiliki ruang yang cukup dan apakah informasi utamanya tetap mudah dibaca.
3. Karena website yang saya buat masih berupa static web, informasi pada portofolio masih harus ditulis dan diubah secara langsung melalui kode HTML. Hal ini membuat proses pembaruan informasi menjadi kurang praktis, terutama jika jumlah project, pengalaman, atau data lainnya semakin banyak. Pada iterasi berikutnya, saya ingin menambahkan fungsionalitas dinamis menggunakan Django dan database, sehingga data seperti certificates dapat dikelola melalui backend tanpa harus mengubah struktur HTML secara manual. Saya juga ingin mempersiapkan fitur seperti penambahan dan pengeditan project secara dinamis agar website portofolio lebih mudah diperbarui.

AI DISCLOSURE
Saya menggunakan Gemini untuk membantu saya dalam pengerjaan melanjutkan website portofolio. Saya meminta AI untuk menjelaskan logika pembuatan suatu tata letak visual (misalnya menanyakan konsep pembuatan vertical timeline pada HTML/CSS). Saya juga meminta penjelasan untuk sintaks yang saya kurang pahami. Ada kalanya perubahan CSS tidak muncul di browser, saya memberikan tangkapan layar dan bertanya mengapa kode tidak ter-render.


### Tugas 2
1. Browser mengirimkan HTTP request ke server Django. File konfigurasi URL utama (myportfolio/urls.py) menerima request ini, melihat awalan path URL, lalu meneruskannya (menggunakan include()) ke file routing spesifik milik aplikasi main. Di dalam main/urls.py, Django mencocokkan path achievements/ dengan path yang sudah didaftarkan. Ketika cocok, Django akan memanggil fungsi view yang terhubung dengan path tersebut, yaitu show_achievements. Fungsi view show_achievements menerima request dan membutuhkan data untuk ditampilkan. View ini memanggil model Achievements (yang bertugas berkomunikasi dengan database) melalui QuerySet Achievements.objects.all() untuk mengambil semua data pencapaian dari database. View memasukkan data yang diambil dari model ke dalam sebuah variabel context (dictionary). Kemudian, view memanggil fungsi render() dengan menyertakan request, file achievements.html (Template), dan context tersebut. Template memproses struktur HTML-nya dan menggabungkannya secara dinamis dengan data dari context menggunakan Django Template Language (DTL). Setelah HTML final terbentuk, Django mengembalikannya ke browser pengguna sebagai HTTP response, dan browser menampilkan halaman portofolio yang berisi data pencapaian.
2. Data portofolio sebaiknya disimpan di model (database) karena memisahkan antara struktur presentasi (HTML/Template) dengan isi data (Content). Jika data di-hardcode langsung di HTML, kita harus membongkar kode sumber aplikasi setiap kali ada penambahan atau perubahan pencapaian baru, yang mana sangat tidak efisien dan berisiko merusak struktur kode. Menyimpan data di model membuat pemeliharaan aplikasi jauh lebih mudah, dengan menambah, mengedit, atau menghapus data langsung lewat Django Admin Panel tanpa perlu menyentuh baris kode HTML (seperti halnya sistem CMS). Dari sisi pengembangan aplikasi, pemisahan ini memungkinkan kita untuk mengolah data secara dinamis (misalnya melakukan filtering, sorting berdasarkan tahun, atau pagination) dengan mudah di dalam fungsi view sebelum ditampilkan.
3. makemigrations berfungsi sebagai perintah untuk mendeteksi perubahan yang kita buat pada file models.py dan membuat file "cetak biru" (file migrasi) yang berisi instruksi bagaimana struktur database harus diubah. migrate berfungsi untuk mengeksekusi file cetak biru tersebut (file migrasi) dan secara nyata menerapkan/menulis perubahan struktur tabel ke dalam sistem database (misalnya menambah tabel, menambah kolom, dll).

AI DISCLOSURE
Saya menggunakan Gemini untuk membantu saya dalam pengerjaan tugas individu 2. Saya meminta AI untuk menjelaskan alur tugas secara step by step, bertanya ketika ada bagian yang saya tidak mengerti.
Link chatlog: https://share.gemini.google/MGvFROVvAh8X

### Tugas 3

1. **ModelForm** menghubungkan form langsung dengan model (`Achievement`), sehingga field, tipe input, `max_length`, dan aturan validasi (misalnya `year` harus angka, `name` wajib diisi) diturunkan otomatis dari definisi model. Jika membuat form HTML manual, saya harus menulis ulang setiap field, validasi, dan proses konversi tipe data di dua tempat (HTML dan view), yang mudah tidak sinkron ketika model berubah. ModelForm juga menyediakan `form.is_valid()` untuk validasi di sisi server, `form.errors` untuk pesan kesalahan, `form.save()` untuk menyimpan data, dan `instance=` untuk mengisi form dengan data lama saat update, sehingga kode lebih ringkas dan konsisten. `{% csrf_token %}` wajib ada karena form dengan method POST mengubah data di server. Tanpa token tersebut, situs lain dapat membuat browser pengguna yang sedang login mengirim request POST palsu ke aplikasi kita (serangan *Cross-Site Request Forgery*), karena browser otomatis menyertakan cookie sesi. Token CSRF adalah nilai acak unik per sesi yang hanya diketahui halaman kita; Django menolak request POST (403) yang tidak membawa token yang cocok, sehingga hanya form yang benar-benar berasal dari situs kita yang diterima.
2. JSON lebih disukai karena lebih ringkas dan lebih mudah dibaca dibandingkan XML yang memerlukan tag pembuka dan penutup untuk setiap elemen, sehingga ukuran data lebih kecil dan transfer lebih cepat. JSON juga merupakan subset dari sintaks objek JavaScript, sehingga di browser dapat langsung diubah menjadi objek dengan `JSON.parse()` / `response.json()` tanpa parser XML/DOM yang lebih rumit. Selain itu, JSON mendukung tipe data dasar (string, angka, boolean, null, array, object) secara native, dan didukung hampir semua bahasa pemrograman serta framework modern (termasuk REST API dan framework frontend seperti React), sehingga menjadi format standar pertukaran data antara frontend dan backend. XML masih dipakai untuk kasus tertentu (dokumen dengan atribut/namespace, sistem lama), tetapi untuk aplikasi web modern JSON lebih praktis.
3. Ketika browser meminta `/api/achievements/`, Django mencocokkan URL tersebut di `main/urls.py` dan memanggil view `get_achievements_json`. View mengambil data dari database dengan `Achievement.objects.all()` (opsional difilter dengan parameter `?name=`), lalu mengubahnya menjadi string JSON dengan `serializers.serialize("json", queryset)`, dan mengembalikannya lewat `HttpResponse(..., content_type="application/json")`. Pada halaman `/achievements/`, view `show_achievements` memakai JSON tersebut, lalu mendeserialisasinya kembali dengan `serializers.deserialize("json", ...)` menjadi objek model untuk dirender di template. Serialization diperlukan karena QuerySet dan instance model adalah objek Python yang tidak dapat dikirim melalui HTTP; HTTP hanya mengirim teks/byte. Serializer mengubah objek tersebut menjadi format teks yang standar dan dapat dibaca oleh klien mana pun (termasuk yang tidak memakai Python), serta menangani tipe data khusus seperti UUID dan tanggal yang bukan tipe bawaan JSON.

**Fitur Tugas 3:**
- Semua template (`index.html`, `experience.html`, `achievements.html`, `achievement_form.html`) memakai `{% extends "base.html" %}`.
- Achievement: create (`/achievements/add/`), update (`/achievements/<id>/edit/`), delete (tombol dengan konfirmasi modal, method POST), dan JSON (`/api/achievements/`, mendukung filter `?name=`).
- Experience juga tersedia dalam JSON di `/api/experience/`.
- `AchievementForm` (`main/forms.py`) memiliki field `name`, `issuer` (teks), `year` (angka), dan `description` (teks panjang, opsional).
- Setelah menambah/mengubah/menghapus data, muncul pesan sukses di bagian atas halaman.

**Cara menjalankan:**
```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python manage.py test
```

AI DISCLOSURE
Saya menggunakan Gemini untuk membantu saya dalam pengerjaan Tugas Individu 3. Saya meminta AI untuk menjelaskan alur tugas secara step-by-step dan bertanya ketika ada bagian materi Form & Data Delivery yang saya tidak mengerti. Secara spesifik, saya menggunakan AI untuk memahami cara kerja `ModelForm` di Django, alur serialization dan deserialization data ke format JSON, serta logika di dalam views untuk fungsi Create, Update, dan Delete.

### Tugas 4

**Hak akses yang diterapkan (bagian Achievements):**

| Peran | Baca daftar & detail | Star / Unstar | Ubah | Tambah & Hapus |
|---|---|---|---|---|
| Pengunjung (belum login) | ✅ | ➡️ diarahkan ke login | ➡️ diarahkan ke login | ➡️ diarahkan ke login |
| Pengguna biasa | ✅ | ✅ | ❌ 403 | ❌ 403 |
| Editor (grup `Editor`) | ✅ | ✅ | ✅ | ❌ 403 |
| Pemilik (superuser) | ✅ | ✅ | ✅ | ✅ |

**Fitur Tugas 4:**
- **Autentikasi:** register, login, dan logout memakai `UserCreationForm`, `AuthenticationForm`, `login()`, dan `logout()` bawaan Django. Saat login, cookie `last_login` disimpan dan ditampilkan di halaman utama; saat logout cookie dihapus. Setelah login, pengguna dikembalikan ke halaman asal (`?next=`), dengan pengecekan `url_has_allowed_host_and_scheme` untuk mencegah *open redirect*.
- **Peran Editor:** migrasi `0007_create_editor_group` otomatis membuat grup `Editor` yang hanya punya permission `view_achievement` dan `change_achievement`. Anggota grup ditetapkan lewat Django Admin (`/admin` → Users → pilih user → Groups → `Editor`).
- **Pemeriksaan di sisi server:** aturan peran dikumpulkan di `main/roles.py`. Decorator `role_required(...)` memakai `@login_required` (redirect ke `/login/`) lalu memunculkan `PermissionDenied` (HTTP 403) jika peran tidak cukup. `create_achievement` dan `delete_achievement` hanya untuk superuser, sedangkan `edit_achievement` untuk superuser atau Editor.
- **Menyembunyikan kontrol di template:** context processor `main.context_processors.user_roles` mengirim `can_edit_achievement`, `can_manage_achievement`, `is_editor`, dan `user_role` ke semua template. Tombol *Tambah*, *Edit*, dan *Hapus* hanya muncul untuk peran yang berhak. Navbar juga menampilkan badge peran pengguna.
- **Star:** `Achievement.starred_by = ManyToManyField(User)`. View `toggle_star` hanya menerima POST (`@require_POST`, GET → 405) dengan `{% csrf_token %}`. Relasi M2M menjamin satu pengguna maksimal memberi satu star. Jumlah star dihitung dengan `annotate(Count("starred_by"))` dalam satu query. Status star pengguna ditampilkan sebagai tombol *Star*/*Unstar*, sedangkan pengunjung melihat tombol *Login untuk Star*.
- **Halaman detail publik:** `/achievements/<id>/`.
- **Keamanan API:** `/api/achievements/` hanya menyerialisasi field `name`, `issuer`, `year`, dan `description`. Field `starred_by` tidak disertakan agar username pemberi star tidak bocor. Tooltip tombol star juga tidak lagi menampilkan daftar username.

**Cara mencoba peran:**
```
python manage.py migrate            # membuat tabel + grup Editor
python manage.py createsuperuser    # akun pemilik portofolio
python manage.py runserver
```
1. Daftar dua akun lewat `/register/`.
2. Login ke `/admin` dengan superuser, lalu masukkan salah satu akun ke grup **Editor**.
3. Login dengan setiap akun dan bandingkan tombol yang muncul di `/achievements/`.

Semua skenario di atas juga dicakup oleh unit test (`python manage.py test`, 43 test), termasuk kelas `AuthAndAuthorizationTest` dan `EditorRoleTest`.

AI DISCLOSURE
Saya menggunakan Claude Code (Claude) untuk membantu melengkapi Tugas Individu 4. Saya memberikan deskripsi tugas lengkap dan meminta AI mengecek bagian yang belum terpenuhi dari kode yang sudah saya buat (autentikasi, cookie `last_login`, dan star). AI membantu pada bagian berikut:
- menambahkan peran Editor (migrasi grup, `main/roles.py`, dan context processor),
- memperbaiki endpoint JSON yang sebelumnya ikut mengirim username pemberi star,
- membuat `toggle_star` hanya menerima POST dan menambahkan redirect `next` yang aman,
- membuat halaman detail, serta menambah dan memperbarui unit test.

Catatan: test lama (`test_json_uses_usernames_for_stars`) justru mengharapkan username ada di JSON. Test ini saya ganti dengan `test_json_does_not_leak_starring_users` karena bertentangan dengan syarat tidak membocorkan informasi sensitif. Hasil dari AI tidak langsung saya terima begitu saja. Saya juga tetap perlu memeriksa sendiri alur login, star, dan pembagian peran di browser.
