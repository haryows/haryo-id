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
image: "/images/nama-gambar.png"   # opsional
---

Isi tulisan pakai Markdown biasa.
```

Nama file jadi bagian dari URL: `nama-slug-kamu.md` → `/blog/nama-slug-kamu/`

## 3. Menambahkan gambar

Karena setup R2 butuh kartu debit/kredit terdaftar di Cloudflare, untuk sekarang gambar disimpan **langsung di dalam project ini** — gratis, tanpa kartu apa pun, dan otomatis ikut ter-deploy oleh Cloudflare Pages.

1. Taruh file gambar (jpg/png/webp) ke folder `public/images/`. Contoh: `public/images/security-headers-cover.png`
2. Pakai di frontmatter post: `image: "/images/security-headers-cover.png"`
3. Atau langsung di isi Markdown: `![Deskripsi gambar](/images/nama-file.png)`
4. `git add .`, `git commit -m "tambah gambar"`, `git push` seperti biasa — Cloudflare otomatis build ulang.

Batas: maksimal 25MB per file gambar, dan total 20.000 file di seluruh situs (paket Free Cloudflare Pages) — jauh lebih dari cukup untuk blog personal.

> Nanti kalau kamu sudah punya kartu debit/kredit dan mau pindah ke Cloudflare R2 (misalnya karena gambar/video makin banyak), cukup ganti path gambar dari `/images/nama-file.png` menjadi URL penuh seperti `https://media.haryo.id/nama-file.png` — tidak perlu ubah struktur project lainnya.

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
