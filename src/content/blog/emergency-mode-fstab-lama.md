---
title: "Cara Mengatasi Emergency Mode Linux karena Entry fstab Lama"
description: "VM Linux nyangkut di emergency mode setelah detach disk? Penyebabnya entry fstab lama yang lupa dihapus. Ini cara identifikasi, fix, dan pencegahan dengan nofail."
date: 2026-10-04
category: "Linux"
image: "/images/fstab-emergency-mode-cover.png"
---

Case ini sebenarnya simpel banget penyebabnya, tapi efeknya bisa bikin panik: **VM/server Linux gagal boot dan nyangkut di "emergency mode"**. Bukan karena disk rusak, bukan karena update kernel gagal — cuma karena satu baris di `/etc/fstab` yang lupa dihapus setelah disk/volume-nya kita detach dari platform virtualisasi.

Ceritanya begini: ada volume LVM lama di sebuah VM Ubuntu yang sudah tidak dipakai, lalu di-detach dari sisi platform. Tapi entry mounting-nya di `/etc/fstab` masih ada. Waktu VM di-reboot, systemd berusaha mencari device itu... dan karena device-nya sudah tidak ada, systemd menunggu sampai **timeout**, lalu memutuskan boot gagal dan masuk ke emergency mode.

## Berlaku untuk OS apa saja?

Mekanisme ini adalah perilaku **systemd**, jadi berlaku untuk semua distro yang boot pakai systemd:

- **Ubuntu** 16.04 ke atas (case saya ini Ubuntu 22.04)
- **Debian** 8 ke atas
- **CentOS/RHEL/Rocky/AlmaLinux** 7 ke atas
- **openSUSE/SLES**, Fedora, Arch, dll

Yang TIDAK kena pola ini: distro tanpa systemd (Alpine/OpenRC, Gentoo default, Devuan). Mereka punya mekanisme sendiri (misal OpenRC drop ke shell kalau mount gagal), tapi konsepnya mirip: fstab yang menunjuk device yang tidak ada = boot bermasalah.

## Tanda-tandanya

Waktu VM boot, layar berhenti di pesan seperti ini:

![Tampilan emergency mode saat boot](/images/fstab-emergency/step1.png)

Perhatikan baris kuncinya:

```
You are in emergency mode. After logging in, type "journalctl -xb" to view
system logs, "systemctl reboot" to reboot, "systemctl default" or "exit"
to boot into default mode.

Give root password for maintenance
(or press Control-D to continue):
```

Masukkan password root untuk masuk ke maintenance shell.

## Langkah identifikasi

### 1. Pastikan dulu resource VM-nya aman

Sebelum menyalahkan fstab, cek dulu dari sisi platform: disk masih ter-attach sesuai konfigurasi? Network aman? CPU/memory cukup? Di case saya semuanya sesuai — artinya masalahnya ada di dalam OS.

Setelah login maintenance, cek filesystem yang ter-mount saat ini:

```bash
df -h
```

![Hasil df -h di emergency mode](/images/fstab-emergency/step2.png)

Terlihat hanya filesystem utama yang ke-mount — volume yang "hilang" jelas tidak muncul.

### 2. Baca log dengan journalctl

Sesuai petunjuk di layar, jalankan:

```bash
journalctl -xb
```

Lalu cari error yang merujuk ke device yang gagal. Di case saya ketemu ini:

```
systemd[1]: dev-mapper-vg\x2d\x2dvol\x2d\x2dold.device: Job ... start timed out.
systemd[1]: Timed out waiting for device /dev/mapper/vg--vol--old.
systemd[1]: dev-mapper-vg\x2d\x2dvol\x2d\x2dold.device: Job ... failed with result 'timeout'.
```

*(nama device di screenshot saya samarkan jadi generik — di case asli namanya berbeda)*

![Error journalctl merujuk ke device lama](/images/fstab-emergency/step3.png)

Nah, device `vol--old` ini nama volume LVM lama yang sudah di-detach. `\x2d` itu cuma escape systemd untuk karakter `-` (tanda hubung), jadi jangan bingung bacanya.

### 3. Konfirmasi bahwa device-nya memang sudah tidak ada

Cek fstab dan bandingkan dengan device yang benar-benar ada:

```bash
cat /etc/fstab
lvdisplay        # untuk volume LVM
lsblk            # untuk melihat semua block device
```

Di case saya, fstab masih memuat baris:

```
/dev/mapper/vg--vol--old    /datalama    ext4    rw,relatime    0    0
```

...tapi `lvdisplay` dan `lsblk` tidak lagi menunjukkan volume tersebut. Valid — ini memang sisa konfigurasi lama.

![Entry fstab yang menunjuk volume lama](/images/fstab-emergency/step4.png)

### 4. Komentari atau hapus entry-nya, lalu reboot

Edit fstab (di emergency mode biasanya masih bisa pakai `vi`/`nano`; kalau root filesystem read-only, remount dulu dengan `mount -o remount,rw /`):

```bash
vi /etc/fstab
```

Tambahkan `#` di depan baris entry lama (saya lebih suka komen dulu daripada langsung hapus — kalau nanti ternyata salah analisa, gampang dibalikkan), lalu reboot:

```bash
systemctl reboot
```

VM boot normal lagi. Selesai.

## Biar tidak kejadian lagi: pakai nofail

Ini bagian yang menurut saya paling penting. Kita tidak selalu ingat untuk bersih-bersih fstab setelah detach disk — apalagi kalau pekerjaan dilakukan buru-buru atau oleh orang lain. Solusinya: tambahkan opsi `nofail` pada entry disk yang sifatnya "boleh tidak ada":

```
/dev/mapper/vg--data-vol--data    /data    ext4    rw,relatime,nofail    0    0
```

Dengan `nofail`, systemd tidak akan menganggap boot gagal kalau device-nya tidak ditemukan — sistem tetap lanjut boot normal. Bisa dikombinasikan dengan batas waktu tunggu:

```
/dev/mapper/vg--data-vol--data    /data    ext4    rw,relatime,nofail,x-systemd.device-timeout=10s    0    0
```

Catatan: untuk disk **sistem** (root, /boot) opsi `nofail` tentu tidak masuk akal — ini untuk disk data/tambahan saja. Dan kalau disk data penting sampai hilang, kamu tetap mau tahu — `nofail` cuma mencegah server tidak bisa boot, bukan menghilangkan alert. Cek `lsblk`/`df -h` tetap jadi kebiasaan baik setelah reboot.

### Alternatif lain yang lebih rapi

- **Gunakan UUID/label** alih-alih nama device (`/dev/sdb1`, `/dev/mapper/...`). Nama device bisa berubah urutan setelah detach/attach, UUID tidak. Ambil UUID dengan `blkid`, lalu tulis di fstab: `UUID=xxxx-xxxx /data ext4 defaults,nofail 0 2`
- **Hapus entry fstab-nya** setiap kali detach disk — jadikan satu paket dengan prosedur detach itu sendiri
- **Backup fstab sebelum diubah**: `cp /etc/fstab /etc/fstab.bak-$(date +%F)`

## Kesimpulan

Emergency mode karena fstab basi itu masalah 5 menit — asal tahu jalurnya: login maintenance → `journalctl -xb` → temukan device yang timeout → bandingkan dengan fstab → komen/hapus → reboot. Yang bikin lama biasanya cuma paniknya 😄

Kebiasaan kecil yang menyelamatkan: **detach disk = update fstab**, dan pasang `nofail` untuk disk data. Dua hal itu saja sudah cukup untuk tidak pernah ketemu layar emergency mode karena kasus ini lagi.

> **Disclaimer**: langkah-langkah di artikel ini berdasarkan pengalaman pribadi saya menangani server production. Kondisi setiap sistem bisa berbeda — selalu backup konfigurasi (`/etc/fstab`) sebelum mengubahnya, dan do it with your own risk ya.

Kalau ada pertanyaan atau mau diskusi soal case serupa, silakan hubungi saya lewat [halaman kontak](/contact).
