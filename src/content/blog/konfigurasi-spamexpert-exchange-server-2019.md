---
title: "Konfigurasi SpamExperts x Exchange Server 2019"
description: "Cara menyambungkan SpamExperts dengan Exchange Server 2019 — dari send connector outgoing, autentikasi smart host, sampai MX record incoming dan whitelist IP. Catatan pengalaman pribadi, lengkap dengan screenshot."
date: 2026-10-03
category: "Microsoft"
image: "/images/spamexpert-exchange-cover.png"
---

Waktu pertama kali disuruh "nyambungin SpamExperts ke Exchange", kelihatannya cuma soal ganti MX record. Praktiknya ada dua jalur yang harus diatur dan kalau salah satu kelewat, hasilnya lucu-lucu: email masuk tapi email keluar nyangkut, atau sebaliknya — email keluar lancar tapi semuanya mendarat di folder spam penerima.

Di artikel ini saya catat alur konfigurasi SpamExperts (sekarang bagian dari SolarWinds Mail Protect) dengan Exchange Server 2019 via Exchange Admin Center (EAC), berdasarkan yang saya kerjakan sendiri. Ada dua bagian: **outgoing** (Exchange → SpamExperts → internet) dan **incoming** (internet → SpamExperts → Exchange).

## Konsep Dasarnya

SpamExperts bekerja sebagai **cloud filter** yang duduk di depan mail server kita:

```
Outgoing:  Exchange ──► SpamExperts (smtp.antispamcloud.com) ──► internet
Incoming:  internet ──► SpamExperts (MX record) ──► Exchange
```

- **Outgoing**: semua email keluar dari Exchange di-relay ke smart host SpamExperts. Fungsinya scan spam/malware keluar dan — yang sering dilupakan — menjaga reputasi pengiriman.
- **Incoming**: MX record domain diarahkan ke SpamExperts. Email masuk difilter dulu, baru diteruskan ke Exchange.

Syarat awal: domain yang dipakai di Exchange **sudah ditambahkan di dashboard SpamExperts**, baik dengan autentikasi domain maupun IP. Kalau belum, semua langkah di bawah tidak akan jalan.

## Bagian 1: Konfigurasi Outgoing Mail

Semua langkah ini dilakukan di **Exchange Admin Center (EAC)** — biasanya di `https://<server-exchange>/ecp/`.

### Langkah 1: Buka menu Send Connector

Masuk ke EAC → **Mail Flow → Send Connectors**, lalu klik tanda **+** untuk membuat connector baru.

![Daftar send connector di Exchange Admin Center](/images/spamexpert/step1.png)

### Langkah 2: Beri nama dan pilih tipe Internet

Isikan nama connector di kolom **Name** — saya pakai nama yang jelas seperti `SpamExpert Outgoing` supaya gampang dikenali nanti. Pada bagian **Type**, pilih **Internet**, lalu klik **Next**.

![Pemilihan tipe send connector: Internet](/images/spamexpert/step2.png)

### Langkah 3: Arahkan ke smart host SpamExperts

Pada bagian **Network settings**, pilih **Route mail through smart hosts**, klik **+** untuk menambahkan smart host, lalu masukkan smart host SpamExperts. Untuk layanan cloud standar:

```
smtp.antispamcloud.com
```

Biarkan port pada **25** (default), lalu klik **Next**.

![Network settings: route mail through smart host](/images/spamexpert/step3.png)

### Langkah 4: Pilih metode autentikasi smart host

Ada dua skenario, tergantung konfigurasi outgoing di dashboard SpamExperts:

- **Basic authentication** — isi **User name** dan **Password** outgoing yang dibuat di dashboard SpamExperts.
- **None** — dipakai kalau autentikasi outgoing di SpamExperts berbasis **IP** (IP publik server Exchange kita sudah didaftarkan di dashboard).

Setelah dipilih, klik **Next**.

![Smart host authentication: basic authentication atau none](/images/spamexpert/step4.png)

### Langkah 5: Set address space ke `*`

Klik **+** pada bagian **Address Space**, lalu di kolom **FQDN** isikan `*` (tanda bintang). Artinya: **semua** domain tujuan akan di-relay melalui connector ini — bukan cuma domain internal kita. Biarkan **Cost** di angka 1, lalu klik **Next**.

### Langkah 6: Pilih source server

Pilih server Exchange yang akan memakai connector ini (server dengan role Mailbox/Transport), klik **+**, lalu **Finish**.

![Pemilihan source server untuk send connector](/images/spamexpert/step5.png)

### Langkah 7: Pastikan connector aktif

Terakhir, cek di daftar send connectors bahwa status connector yang baru dibuat **Enabled**. Kalau masih *Disabled*, klik connector-nya lalu centang **Enable**.

![Send connector SpamExpert berstatus Enabled](/images/spamexpert/step6.png)

Sampai di sini jalur outgoing sudah jadi. Tes kirim email ke alamat eksternal (misalnya Gmail) dan cek *header*-nya — harusnya terlihat lewat `antispamcloud.com`.

## Bagian 2: Konfigurasi Incoming Mail

### Langkah 1: Arahkan MX record ke SpamExperts

Di DNS management domain, ubah MX record agar mengarah ke SpamExperts. Untuk layanan cloud standar, record-nya seperti ini:

```
10  MX  mx.spamexperts.com
20  MX  fallbackmx.spamexperts.eu
30  MX  lastmx.spamexperts.net
```

![MX record SpamExperts di DNS management](/images/spamexpert/step7.png)

> **Catatan:** nilai persisnya cek di dashboard SpamExperts masing-masing, karena bisa berbeda tergantung paket/region.

### Langkah 2: Whitelist IP SpamExperts di Exchange

Setelah MX diarahkan, semua email masuk akan datang **dari IP SpamExperts** — bukan lagi dari pengirim aslinya. Kalau di Exchange (atau firewall di depannya) ada pemblokiran koneksi, email masuk bisa ditolak. Whitelist IP range SpamExperts berikut:

```
IP range:
185.201.16.0/22

Sub-ranges:
185.201.16.0/24
185.201.17.0/24
185.201.18.0/24
185.201.19.0/24
```

Whitelist ini bisa dipasang di firewall, connection filtering, atau Receive Connector Exchange. Contoh menambahkan IP allow list via **Exchange Management Shell**:

```powershell
Set-ReceiveConnector "DefaultFrontend<NAMASERVER>" -RemoteIPRanges @{Add="185.201.16.0/22"}
```

Sesuaikan `<NAMASERVER>` dengan nama server Exchange kita (`Get-ReceiveConnector` untuk melihat daftarnya).

### Jangan Lupa: SPF Record

Ini bagian yang paling sering kelewat. Karena outgoing sekarang lewat SpamExperts, SPF record domain **wajib** menyertakan SpamExperts, supaya email kita tidak dianggap palsu oleh penerima:

```
v=spf1 include:spf.antispamcloud.com ~all
```

Kalau sebelumnya sudah ada SPF (misalnya `include:_spf.google.com`), tambahkan `include`-nya — jangan buat record SPF kedua. Tanpa langkah ini, konfigurasi bisa "berhasil" tapi email keluar tetap mendarat di spam penerima.

## Verifikasi

Setelah semuanya dipasang, ceklist sederhana yang biasa saya lakukan:

- **Outgoing**: kirim email ke Gmail → cek *Show original* → pastikan ada jejak relay `antispamcloud.com` dan SPF **PASS**.
- **Incoming**: kirim email dari akun eksternal → pastikan lewat filter SpamExperts (cek log delivery di dashboard) sebelum masuk mailbox.
- **Queue**: di EAC → Mail Flow, pastikan tidak ada email yang menumpuk di queue.

Kalau incoming tersendat, tersangka utamanya biasanya dua: MX belum propagasi (`dig MX namadomain.com` untuk cek), atau IP SpamExperts belum di-whitelist.

## Penutup

Konfigurasinya sebenarnya tidak rumit — yang bikin pusing biasanya cuma dua hal: lupa whitelist IP di sisi incoming, dan lupa update SPF di sisi outgoing. Sisanya tinggal klik-klik di EAC.

Kalau ada yang mau didiskusikan soal setup SpamExperts + Exchange, atau ketemu kasus error yang aneh-aneh, silakan hubungi saya lewat [halaman kontak](/contact). Senang kalau catatan ini membantu.

> **Disclaimer:** Tutorial di blog ini adalah catatan pengalaman pribadi, bukan dokumentasi resmi. Konfigurasi dan penggunaannya cukup ikuti dengan kesadaran penuh — *do it with your own risk* — karena setiap lingkungan server bisa berbeda. Backup konfigurasi (export connector, catat DNS record lama) sebelum mulai mengutak-atik mail flow produksi.
