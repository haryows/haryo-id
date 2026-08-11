# haryo.id — Astro + Cloudflare Pages + R2

Situs statis untuk haryo.id, dibangun dengan [Astro](https://astro.build).

## Struktur

```
src/
  content/blog/       ← file .md untuk tiap tulisan (ini yang kamu edit tiap nulis post baru)
  pages/               ← halaman: index, blog, category, about, contact
  layouts/             ← BaseLayout.astro (header, footer, dark mode)
  styles/global.css    ← semua styling & design tokens
```

## 1. Jalankan di lokal

```bash
npm install
npm run dev
```

Buka http://localhost:4321

## 2. Menulis post baru

Buat file baru di `src/content/blog/nama-slug-kamu.md`:

```markdown
---
title: "Judul Post"
description: "Ringkasan singkat untuk SEO/preview."
date: 2026-08-01
category: "Linux Server"
image: "https://media.haryo.id/posts/nama-gambar.png"   # opsional
---

Isi tulisan pakai Markdown biasa.
```

Nama file jadi bagian dari URL: `nama-slug-kamu.md` → `/blog/nama-slug-kamu/`

## 3. Setup Cloudflare R2 untuk gambar

1. Di dashboard Cloudflare → **R2** → **Create bucket**, misal nama `haryo-media`.
2. Di tab **Settings** bucket → **Public access** → aktifkan lewat **custom domain**, contoh: `media.haryo.id` (karena domain haryo.id sudah ada di akun Cloudflare-mu, ini tinggal beberapa klik, tanpa perlu ubah nameserver lagi).
3. Upload gambar ke bucket (lewat dashboard, atau nanti pakai `wrangler` CLI / rclone kalau mau otomatis).
4. Pakai URL `https://media.haryo.id/nama-file.png` di frontmatter `image:` atau langsung di isi Markdown post.

Free tier R2: 10 GB storage/bulan, dan **tidak ada biaya egress** — jauh cukup untuk gambar blog personal.

## 4. Deploy ke Cloudflare Pages

1. Push folder ini ke repo GitHub kamu.
2. Di dashboard Cloudflare → **Workers & Pages** → **Create application** → **Pages** → **Connect to Git**, pilih repo ini.
3. Build settings:
   - Framework preset: **Astro**
   - Build command: `npm run build`
   - Output directory: `dist`
4. Deploy. Setelah berhasil, buka tab **Custom domains** project ini → tambahkan `haryo.id` dan `www.haryo.id`.
   Karena domain sudah dikelola Cloudflare, verifikasinya otomatis.

## 5. Pindahkan DNS dari cPanel lama

Setelah custom domain di Pages aktif, cek record DNS zone `haryo.id` di Cloudflare:
- Hapus/ubah **A record** lama yang mengarah ke IP hosting cPanel.
- Cloudflare Pages akan otomatis membuat/menyesuaikan record yang dibutuhkan saat kamu menambahkan custom domain di langkah 4.
- Tunggu propagasi (biasanya cepat karena DNS sudah di Cloudflare).

## 6. (Opsional) Headless CMS

Kalau nanti ingin dashboard mirip WordPress di atas struktur ini, bisa tambahkan **Decap CMS** — cukup mengarah ke folder `src/content/blog/` sebagai koleksi.
