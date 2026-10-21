# Harmage Antigravity Improvement Pack

Tujuan: membantu Antigravity memakai Graphify dan skill secara terarah, menyimpan konteks proyek, serta melanjutkan pekerjaan tanpa audit berulang.

## Instalasi (Windows)

1. Tutup Antigravity atau tutup workspace Harmage terlebih dahulu.
2. Ekstrak folder `.agents` dan file `PROJECT_MEMORY.md` serta `TASK_STATE.md` ke **root repositori Harmage yang benar** (folder utama repo, bukan otomatis folder parent `E:\AI Agent`).
3. Jika `.agents` sudah ada, gabungkan isinya; jangan hapus skill/rule lama.
4. Jika `PROJECT_MEMORY.md` atau `TASK_STATE.md` sudah ada, jangan menimpanya. Gabungkan informasi baru dengan file lama.
5. Buka ulang workspace di Antigravity. Skills ada di `.agents/skills/`; rule ada di `.agents/rules/harmage-workflow.md`.
6. Di chat Antigravity, ketik `/graphify-workflow` untuk mencoba skill Graphify, atau `/project-memory` untuk memeriksa/menyegarkan memori. Ketersediaan slash command bergantung pada skill discovery versi yang digunakan.

## Graphify: verifikasi sebelum digunakan

Buka PowerShell di root proyek dan jalankan:

```powershell
graphify --help
graphify --version
```

Jika perintah tidak ditemukan, periksa instalasi resmi Graphify: https://github.com/Graphify-Labs/graphify

Dokumentasi upstream saat pack ini dibuat menyebut paket PyPI resmi `graphifyy` dan perintah CLI `graphify`. Jangan menginstal paket bernama mirip dari sumber tidak terverifikasi. Ikuti README resmi terbaru dan periksa opsi yang tersedia pada versi terpasang.

Jangan menganggap graph tersedia atau terbaru hanya karena paket terinstal. Skill Graphify meminta Antigravity memeriksa perintah, lokasi graph, status freshness, dan bukti eksekusi sebelum menyatakan berhasil.

## Isi pack

- `.agents/rules/harmage-workflow.md`: aturan workspace yang otomatis ditemukan.
- `graphify-workflow`: prosedur penggunaan Graphify secara terverifikasi.
- `project-memory`: cara menyimpan dan memakai pengetahuan proyek.
- `skill-auditor`: mengecek skill/tool yang tersedia tanpa mengarang kemampuan.
- `verify-before-done`: verifikasi perubahan, tes, dan bukti.
- `PROJECT_MEMORY.md`: template memori proyek.
- `TASK_STATE.md`: status tugas untuk melanjutkan pekerjaan.

## Batasan

File ini tidak melatih ulang model dan tidak bisa memaksa model menggunakan tool yang tidak tersedia. Ia membuat prosedur, memori, dan bukti kerja lebih konsisten. Setelah instalasi, verifikasi skill benar-benar terdeteksi oleh Antigravity.
