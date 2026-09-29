---
title: "Cara Menambahkan Security Headers di Cloudflare (Gratis, Tanpa Ubah Kode)"
description: "Panduan lengkap menambahkan security headers seperti CSP, HSTS, dan X-Frame-Options lewat Cloudflare Transform Rules — tanpa menyentuh kode server sama sekali."
date: 2026-06-02
category: "Cloudflare"
image: "/images/security-headers-cover.png"
---

Pernah cek website sendiri di [securityheaders.com](https://securityheaders.com) dan dapat nilai **F**? Tenang, saya juga pernah. Kabar baiknya: kalau domain kamu sudah lewat Cloudflare, kamu bisa naik ke grade A tanpa menyentuh satu baris kode pun di server.

Di artikel ini saya tunjukkan cara menambahkan security headers penting hanya menggunakan fitur gratis Cloudflare.

## Apa Itu Security Header, dan Kenapa Penting?

Security header adalah instruksi kecil yang dikirim server (atau dalam kasus ini, Cloudflare) bersama respons website. Browser yang menerimanya jadi tahu apa yang boleh dan tidak boleh dilakukan terhadap halaman kamu — misalnya, apakah boleh di-embed di situs orang lain, atau apakah boleh menjalankan script dari domain asing.

Beberapa header yang paling berpengaruh:

- **Strict-Transport-Security (HSTS)** — memaksa browser selalu pakai HTTPS. Tanpa ini, pengunjung yang mengetik `haryo.id` bisa saja pertama kali masuk lewat HTTP dan rentan serangan *downgrade*.
- **X-Frame-Options / frame-ancestors** — mencegah website kamu di-embed dalam iframe di situs lain. Ini pertahanan utama dari serangan *clickjacking*.
- **X-Content-Type-Options** — melarang browser "menebak-nebak" tipe file. Mencegah serangan berbasis MIME-sniffing.
- **Referrer-Policy** — mengatur seberapa banyak informasi halaman asal bocor ke website tujuan saat ada link keluar.
- **Content-Security-Policy (CSP)** — yang paling kuat sekaligus paling rumit: menentukan sumber mana saja yang boleh memuat script, style, dan gambar. Ini pertahanan lapis tambahan dari serangan XSS.

## Sekilas: Dua Cara di Cloudflare

Ada dua jalur untuk menambahkan header di Cloudflare:

1. **Transform Rules → Modify Response Header** — tersedia di **paket gratis**, tanpa batas praktis untuk kebutuhan semacam ini. *Inilah yang kita pakai.*
2. **Workers** — lebih fleksibel, tapi butuh sedikit kode JavaScript dan punya batas kuota harian di plan gratis.

Kalau kamu baru mulai, opsi pertama sudah lebih dari cukup.

## Langkah 1: Buka Transform Rules

1. Login ke dasbor Cloudflare, pilih domain kamu.
2. Di menu kiri, masuk ke **Rules → Transform Rules**.
3. Pilih tab **Modify Response Header**, lalu klik **Create rule**.

## Langkah 2: Buat Rule Utama

Beri nama rule-nya, misalnya `security-headers`.

Untuk bagian "jika request masuk", pilih **All incoming requests** — supaya header diterapkan ke seluruh halaman. Kalau kamu punya area statis seperti `asset` atau `cdn` yang tidak butuh, nanti bisa dikecualikan dengan ekspresi khusus, tapi untuk awal "semua" sudah aman.

Sekarang bagian pentingnya: tambahkan operasi **Set static header** untuk masing-masing header di bawah ini.

### HSTS

- **Header name:** `Strict-Transport-Security`
- **Value:** `max-age=31536000; includeSubDomains; preload`

Artinya: "ingat selama 1 tahun (31536000 detik) bahwa situs ini wajib HTTPS, berlaku juga untuk semua subdomain, dan boleh dimasukkan ke daftar preload browser".

⚠️ **Catatan sebelum copas:** jangan buru-buru menambahkan `preload` kalau subdomain kamu ada yang belum mendukung HTTPS — setelah masuk daftar preload, undo-nya butuh waktu berbulan-bulan. Pakai `max-age=31536000; includeSubDomains` dulu, naikkan ke `preload` kalau sudah yakin semua aman.

### X-Frame-Options

- **Header name:** `X-Frame-Options`
- **Value:** `DENY`

Sederhana: halaman kamu tidak boleh di-embed di mana pun, termasuk oleh situs kamu sendiri. Kalau kamu perlu meng-embed halaman sendiri di subdomain lain, ganti jadi `SAMEORIGIN`.

### X-Content-Type-Options

- **Header name:** `X-Content-Type-Options`
- **Value:** `nosniff`

Satu kata, tugas penting: browser dilarang menebak tipe konten.

### Referrer-Policy

- **Header name:** `Referrer-Policy`
- **Value:** `strict-origin-when-cross-origin`

Pengaturan yang seimbang: situs tujuan masih tahu domain asal link-nya, tapi tidak sampai URL lengkap beserta parameter sensitifnya.

### Permissions-Policy (opsional, tapi bagus)

- **Header name:** `Permissions-Policy`
- **Value:** `camera=(), microphone=(), geolocation=()`

Ini memberi tahu browser: website saya tidak butuh kamera, mikrofon, maupun lokasi — jangan kasih akses ke script mana pun. Nilai default yang aman untuk kebanyakan blog dan website company profile.

## Langkah 3: Deploy dan Uji

Klik **Deploy**. Perubahan biasanya aktif dalam hitungan detik sampai beberapa menit.

Cara paling cepat untuk memastikan semua terpasang — jalankan dari terminal:

```bash
curl -sI https://haryo.id | grep -iE 'strict-transport|x-frame|x-content|referrer|permissions'
```

Kalau kelima barisnya muncul, selamat — coba cek lagi di [securityheaders.com](https://securityheaders.com). Dari grade F tadi seharusnya sudah melompat ke **A**.

Di inspector browser (F12 → tab Network → klik request dokumen → bagian Response Headers) juga bisa dilihat langsung header-nya.

## Bonus: CSP — Kuat Tapi Butuh Pendekatan Berbeda

Content-Security-Policy layak dibahas terpisah karena sekali salah, website bisa "rusak" — gambar hilang, script tidak jalan, font tidak muncul.

Pengalaman saya, cara paling sehat adalah bertahap:

1. **Mulai dalam mode report-only** supaya browser hanya melapor tanpa memblokir apa pun:
   - **Header name:** `Content-Security-Policy-Report-Only`
   - **Value:** `default-src 'self'; report-uri /csp-report`
2. **Buka console browser** selama beberapa hari, catat semua pelanggaran yang muncul.
3. **Sesuaikan directive** sampai daftarnya bersih — misalnya tambah `img-src 'self' data:;` kalau ada gambar base64, atau domain CDN tertentu kalau kamu pakai font eksternal.
4. **Baru aktifkan versi final** dengan nama header `Content-Security-Policy`.

Dengan pola seperti ini, kamu mendapat proteksi XSS yang kuat tanpa drama "kok tiba-tiba websitenya aneh".

## Penutup

Enam header, satu rule Cloudflare, nol baris kode server — dan nilai securityheaders.com kamu naik dari F ke A. Perubahannya mungkin tidak terlihat mata, tapi jarak antara website yang "biasa jalan" dan website yang punya lapisan pertahanan dasar justru ada di detail seperti ini.

Kalau ada pertanyaan atau mau berdiskusi soal implementasi CSP yang lebih spesifik, silakan mampir ke [halaman kontak](/contact/) saya.

> **Disclaimer:** Tutorial di blog ini adalah catatan pengalaman pribadi, bukan dokumentasi resmi. Konfigurasi dan penggunaannya cukup ikuti dengan kesadaran penuh — *do it with your own risk* — karena setiap lingkungan server bisa berbeda.
