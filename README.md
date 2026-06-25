# Lazy-DursGo-XSS-Claude: Rantai Otomatisasi Bug Bounty Terpadu

Proyek ini menggabungkan lima alat bug bounty canggih—**LazyHunter**, **DursGo**, **XSS Scanner**, **DS_Store Explorer**, dan **Claude Bug Bounty**—ke dalam satu alur kerja yang terotomatisasi penuh. Hanya dengan satu perintah, Anda dapat melakukan pengintaian (reconnaissance), pemindaian kerentanan (vulnerability scanning), pemindaian XSS tingkat lanjut dengan AI, ekstraksi file sensitif via `.DS_Store`, dan analisis keamanan mendalam menggunakan kecerdasan buatan (AI) secara end-to-end.

## 🌟 Fitur Utama

- **Otomatisasi End-to-End**: Berjalan mulai dari pencarian subdomain hingga analisis kerentanan menggunakan AI.
- **Konfigurasi Satu Pintu**: Cukup berikan Cookie dan API Key Anda satu kali; skrip ini akan otomatis meneruskannya (inject) ke semua alat tersebut.
- **Integrasi Multi-AI**: Menggunakan DeepSeek (`deepseek-chat`) untuk memberikan kemampuan analisis keamanan pada DursGo dan Claude Bug Bounty, serta Gemini AI untuk analisis kerentanan XSS secara mendalam.
- **Injeksi Konteks Cerdas**: Skrip secara otomatis membimbing AI (Claude Bug Bounty) untuk memahami *tech stack* dari target dan menganalisa temuan DursGo agar relevan dengan lingkungan spesifik sistem.

## 🔄 Alur Kerja (Workflow)

1. **LazyHunter (Reconnaissance)**: Mencari subdomain, memeriksa host yang aktif, dan melakukan *crawling* pada endpoint. Cookie Anda akan otomatis digunakan jika alat ini mendukung fitur tersebut di *background*.
2. **DursGo (Vulnerability Scanner)**: Memindai kerentanan dengan cepat (berbasis Go) pada subdomain aktif yang telah ditemukan oleh LazyHunter. Otomatis menggunakan API Key DeepSeek dan Cookie Anda untuk *AI context* dan sesi terautentikasi.
3. **XSS Scanner (Advanced XSS Testing)**: Memindai seluruh endpoint yang ditemukan menggunakan metode berbasis navigasi dinamis (Playwright) dan mencocokkan pola DOM XSS menggunakan kecerdasan dari Gemini API. (Otomatis menggunakan Cookie dan Gemini API Key Anda).
4. **BackupFinder**: Mengecek dan menemukan keberadaan direktori serta file backup yang tertinggal pada subdomain aktif, mengompilasi polanya secara cermat untuk memastikan tidak ada arsip penting yang terlewat.
5. **DS_Store Explorer**: Secara otomatis akan memeriksa seluruh *endpoint* aktif untuk mencari tereksposnya file `.DS_Store` dan akan mengekstrak struktur folder sensitif jika direkitori tersebut rentan.
6. **Claude Bug Bounty (AI Agent)**: Menggunakan kecerdasan model DeepSeek untuk membuat *ReAct Agent* yang mencari celah lebih jauh dengan meneliti teknologi yang ada serta menganalisa dan merangkum temuan dari alat-alat sebelumnya.

## 📋 Prasyarat

Pastikan lingkungan kerja (environment) Anda sudah memiliki komponen berikut:
- Python 3.12+
- Go (diperlukan untuk melakukan build pada DursGo dan instalasi *tools*)
- Tool Go Security: `subfinder`, `httpx`, `nuclei`, `katana`, dan `gau` harus sudah ter-install dan tersedia di PATH.
- Playwright (diperlukan oleh XSS Scanner, dapat di-install lewat `playwright install`)
- Modul Python yang dibutuhkan untuk menjalankan `lazyhunter`, `xsscanner`, dan `claude-bug-bounty`. Disarankan meng-install dependencies lewat `requirements.txt` masing-masing repository.

Struktur direktori Anda seharusnya terlihat seperti ini:
```text
.
├── lazy_dursgo.py
├── lazyhunter-main/
├── dursgo-main/
└── cloned_repos/
    ├── BackupFinder/
    ├── claude-bug-bounty/
    ├── ds_store_exp/
    ├── nuclei-templates/
    └── xsscanner/
```

## 🚀 Cara Penggunaan

Jalankan skrip utama `lazy_dursgo.py`. Anda hanya perlu memasukkan target domain, beserta argumen opsional untuk *cookie* autentikasi dan API Key untuk masing-masing AI.

```bash
python lazy_dursgo.py -t <target.com> --cookie "session_id=cookie_anda_disini" --deepseek-api-key "sk-kunci_deepseek_anda" --gemini-api-key "AIzaSy_kunci_gemini_anda"
```

### Penjelasan Argumen

| Argumen | Deskripsi | Default |
| :--- | :--- | :--- |
| `-t`, `--target` | Target domain (contoh: example.com) | **Wajib** |
| `--scan-type` | Tipe pemindaian LazyHunter: `-lts` (Ringan/Light), `-dks` (Sedang/Dark), `-dps` (Mendalam/Deep) | `-lts` |
| `--speed` | Kecepatan pemindaian LazyHunter: `low`, `standard`, `fast` | `fast` |
| `--cookie` | Cookie yang digunakan untuk melakukan pemindaian terautentikasi pada seluruh rantai alat | `None` |
| `--deepseek-api-key` | API Key DeepSeek untuk analisis AI di DursGo & Claude Bug Bounty | `None` |
| `--gemini-api-key` | API Key Gemini khusus untuk fitur analisis AI pada XSS Scanner | `None` |
| `--update` | Melakukan update otomatis/tarik kode terbaru dari GitHub untuk semua tool & template | `None` |

## 💡 Contoh

Menjalankan pemindaian mendalam pada `example.com` dengan kecepatan standar (standard speed), menggunakan *cookies* untuk akses *endpoint* yang membutuhkan login, DeepSeek untuk Dursgo/CBB, dan Gemini untuk XSS Scanner:

```bash
python lazy_dursgo.py -t example.com --scan-type -dps --speed standard --cookie "PHPSESSID=123456789" --deepseek-api-key "sk-abcdef123456789" --gemini-api-key "AIzaSy_123456789"
```

## ⚠️ Catatan Penting

- Seluruh hasil laporan dari DursGo akan disimpan secara otomatis di dalam direktori `dursgo-main/reports/`.
- Claude Bug Bounty akan membuat sebuah folder *session* di dalam direktorinya sendiri yang berisi proses pertimbangan AI (*thought process*) dan hasil laporan akhir penganalisaan.
- XSS Scanner akan menampilkan hasilnya di log terminal atau menyimpannya di file logs jika dikonfigurasi di dalam `config.py` miliknya.
