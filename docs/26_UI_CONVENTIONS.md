# 26 — UI Conventions
Rumah tunggal fakta antarmuka `FreeJarvis.app`. Nilai di luar tabel token TERLARANG; di kode hanya lewat `app/FreeJarvis/Design/Tokens.swift`.

## Jangkar
Prototipe tiga keadaan + lembar logo yang disepakati 8 Okt 2026: `docs/_design/keadaan-1-siap.png`, `keadaan-2-bekerja.png`, `keadaan-3-menunggu-izin.png`, `logo.png` (kanvas sumber: artifact "Prototipe UI FreeJarvis", claude.ai/artifact/Pg7DDVzj4uxepauPinCuoe). Bila gambar dan dokumen ini berbeda, dokumen ini menang.

## Token
| Kategori | Nama | Nilai |
|---|---|---|
| Warna latar | `bg` | `#0B1220` |
| | `surface` (kartu, kolom, panel transkrip) | `#111A2B` |
| | `surfaceRaised` (tombol sekunder, pil) | `#162236` |
| | `border` | `#1E293B` |
| Teks | `text` | `#E6EDF7` |
| | `textMuted` (label, sekunder, ucapan sementara) | `#8A9BB5` |
| | `textOnAccent` | `#0B1220` |
| Aksen | `accent` (sian; orb, tombol utama, tab aktif, titik status) | `#38BDF8` |
| | `accentLight` (sian tua, khusus latar terang/logo terang) | `#0284C7` |
| Semantik | `warning` (menunggu izin, frasa aksi) | `#F59E0B` |
| | `danger` (Batalkan, kode layar, destruktif) | `#F87171` |
| | `success` (mic aktif, tes lolos) | `#34D399` |
| Tint (latar 12% dari semantik di atas `surface`) | `accentTint` / `warningTint` / `dangerTint` / `successTint` | `#38BDF8` / `#F59E0B` / `#F87171` / `#34D399` @ opacity 0.12 |
| Diff | `diffAddBg` / `diffAddText` | `#34D399`@0.14 / `#86EFAC` |
| | `diffDelBg` / `diffDelText` | `#F87171`@0.14 / `#FCA5A5` |
| Huruf | `fontUI` | Manrope (400, 600, 700, 800) — dibundel di `Resources/Fonts` |
| | `fontMono` | JetBrains Mono (400, 500) — kode, path, diff, perintah |
| Skala (pt, ukuran/tinggi baris) | `display` | 22/28 Manrope 700 (judul status orb) |
| | `title` | 16/22 Manrope 700 (judul kartu, nama berkas) |
| | `body` | 14/20 Manrope 400–600 |
| | `small` | 12/16 Manrope 400 (keterangan, footer) |
| | `label` | 11/14 Manrope 700, huruf kapital, tracking 0.08em |
| | `mono` | 13/20 JetBrains Mono 400 |
| Wordmark | "free" / "JARVIS" | Manrope 400 `textMuted` / Manrope 800 `text`, tracking 0.06em |
| Jarak | `space` | 4, 8, 12, 16, 24, 32 (hanya nilai ini) |
| Radius | `radiusCard` / `radiusButton` / `radiusPill` | 12 / 10 / tinggi penuh |
| Ukuran | `buttonHeight` / `pillHeight` / `orbDiameter` / `orbRing` | 44 / 32 / 152 / 2 |
| Efek | `orbGlow` | bayangan `accent`@0.35 radius 24 (amber `warning` saat menunggu izin); satu-satunya bayangan di UI |
| Gerak | `motionFast` / `motionOrb` | 150 ms ease-out (transisi status) / amplitudo orb mengikuti RMS mic/TTS, tanpa animasi dekoratif |
| Tata letak | jendela bawaan / rasio panel / Viewer min | 1280×800 / 40:60 dapat digeser / 360; di bawah 900 lebar Viewer dilipat menjadi ikon |

Tema: gelap saja di MVP. Gradien hanya pada ikon aplikasi (`#163A52` → `#0B1220`).

## Logo & ikon
| Aset | Aturan |
|---|---|
| Tanda | kanvas 100×100: cincin `r=41` tebal 7, celah 40 unit kanan atas (`rotate(-68)`); lima batang lebar 6 tinggi 14–26–40–26–14; batang tengah lanjut kait J (`a9.5 9.5 0 0 1 -19 0`) |
| Warna gelap / terang | cincin `accent`, batang `text`, latar `bg` / cincin `accentLight`, batang `bg`, latar `#F5F7FB`, wordmark terang `#5B6B85` / `#0B1220` |
| Ikon aplikasi | persegi radius 23% sisi, gradien di atas, tanda 68% sisi, tanpa wordmark; `AppIcon.appiconset` 16–1024 |
| Ikon menu bar | template monokrom 18/36 px, versi tiga elemen (cincin, kait J, satu batang kanan); berdenyut saat Jarvis bicara |
| Minimum | tanda penuh 28 px; di bawahnya versi tiga elemen. Ruang aman = tinggi satu batang pendek |
| Ekspor | `mark-dark.svg`, `mark-light.svg`, `mark-mono.svg` di `app/FreeJarvis/Resources/` |

## Tata letak & halaman
Satu jendela, dua panel tetap (bukan halaman berpindah). Pola: dasbor dua panel.
| Area | Isi (urutan atas→bawah) |
|---|---|
| Header | wordmark + "Panggil "Jarvis" · satu suara untuk Claude Code" |
| Panel kiri | pemilih Proyek + path · dua pil status (Percakapan, Claude Code) · orb + judul status + petunjuk · Transkrip · bar kontrol (Bicara, Sela, Batalkan, Bisu) · kolom ketik · footer (mikrofon/AEC, jatah) |
| Panel kanan | label VIEWER + tab Jawaban · Perubahan · Log · Pertanyaan (lencana jumlah / titik baru) · isi tab |
| Menu bar | ikon + menu: Tampilkan jendela, Bisukan, Proyek, Keluar |

## Inventaris komponen
| Komponen | Varian | Berkas |
|---|---|---|
| `OrbView` | siap/mendengar/bicara (`accent`), menunggu izin (`warning` + ikon gembok), terputus (`textMuted`) | `UI/Conversation/OrbView.swift` |
| `StatusPill` | netral, aktif (`accentTint` + border `accent`), peringatan (`warningTint` + border `warning`) | `UI/Components/Pill.swift` |
| `TranscriptView` | baris pengguna/Jarvis (label `small` `textMuted`/`accent` + waktu), ucapan sementara miring `textMuted`, kartu persetujuan sebaris | `UI/Conversation/TranscriptView.swift` |
| `JButton` | utama (isi `accent`), sekunder (`surfaceRaised`), destruktif (border+teks `danger`, isi `dangerTint`), ikon | `UI/Components/Button.swift` |
| `ViewerTabs` | aktif (garis bawah `accent`), lencana jumlah (`accent`/`warning`), titik baru | `UI/Viewer/ViewerView.swift` |
| `DiffBlock` | header berkas `mono` + "+n −m" + status "sedang ditulis"; aksi Bacakan/Salin/Buka di editor | `UI/Components/DiffBlock.swift` |
| `CodeBlock` / `LogBlock` | log dilipat, 50 baris terakhir | `UI/Components/CodeBlock.swift` |
| `ApprovalCard` | tingkat Kata singkat/Frasa aksi (`warning`)/Kode layar (`danger`); baris detail (Perintah, Direktori, Commit, Berkas berubah, Tingkat); baris "Mendengar frasa" + teks terdengar `mono`; hitung mundur; tombol Izinkan/Tolak/Lihat diff dulu | `UI/Components/ApprovalCard.swift` |
| `TierTable` | tabel tingkat persetujuan di bawah kartu | `UI/Viewer/QuestionsTab.swift` |
| `ProjectSummary` | kartu Proyek, Sesi, Model + daftar berkas terakhir | `UI/Viewer/ProjectSummary.swift` |
| `NarratorBar` | titik `accent` + kalimat narator + "pembaruan berikutnya paling cepat 10 detik lagi" | `UI/Viewer/ChangesTab.swift` |

## Empat state wajib
| Area | Kosong | Memuat | Gagal | Sukses |
|---|---|---|---|---|
| Viewer (semua tab) | ringkasan proyek (Keadaan 1) + contoh perintah suara Viewer | blok "sedang ditulis" | blok galat `dangerTint` + "detail di Log" | blok terisi + lampu tab |
| Transkrip | "Belum ada percakapan di sesi ini. Contoh: "Jarvis, periksa modul login."" | ucapan sementara | — (galat via `error` ke Log) | baris final |
| Tab Perubahan | "Belum ada perubahan di sesi ini." | diff "sedang ditulis" | "Diff tak bisa dibaca" | diff |
| Tab Pertanyaan | "Tidak ada pertanyaan tertunda." | — | "Izin kedaluwarsa" | kartu |
| Pemilih proyek | "Belum ada proyek. Ucapkan "tambah proyek" atau pilih folder." | — | "Folder tidak ditemukan" | nama + path |
| Panel jatah | "Jatah belum diketahui" | — | "Jatah habis · tersedia lagi {jam}" (`danger`) | "Jatah Max: 5 jam tersisa 72% · kredit API 91%" |
| Koneksi `jarvisd` | — | "Menyambung ke jarvisd…" | "jarvisd terputus · menyambung ulang" + orb `textMuted` | normal |

## Mikroteks
Bahasa Indonesia, nada netral-sopan, tanpa slang. Waktu `HH:mm` 24 jam zona lokal. Persen tanpa desimal. Kata kerja tombol tetap: **Bicara, Sela, Batalkan, Izinkan, Tolak, Bacakan, Salin, Buka di editor, Lihat diff dulu**. Status sesuai label docs/06. Petunjuk hotkey: "Tahan ⌥ Space lalu bicara, atau ketik di bawah."

## Larangan UI
Nilai di luar token · pustaka UI pihak ketiga · gradien/glassmorphism (kecuali ikon aplikasi) · emoji · teks placeholder tersisa · ikon selain SF Symbols · animasi dekoratif · menampilkan kode layar di luar Viewer · tombol klik sebagai satu-satunya jalur persetujuan.
