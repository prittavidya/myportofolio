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