# Dosir Desain FreeJarvis (bahan vcbd)

Oct 8, 2026 · @Syamsuddin Ideris

## 1. Ringkasan dan keputusan terkunci

FreeJarvis adalah aplikasi percakapan suara full-duplex di macOS yang mengendalikan Claude Code lewat Claude Agent SDK, dengan MCP sebagai ekstensi tahap 2 untuk sesi terminal. Semua keputusan di bawah sudah diambil Pak Syams dalam diskusi 8 Oktober 2026 dan menjadi masukan tetap untuk skill `vcbd`.

| Keputusan | Nilai | Alasan singkat |
| --- | --- | --- |
| Platform | macOS, MacBook Pro 2019 Intel | Laptop kerja Pak Syams; tidak ada Neural Engine, STT berat dipindah ke VPS |
| Langganan | Claude Max | Agent SDK dan `claude -p` ditarik dari batas langganan; Max punya kredit API bulanan |
| Inti integrasi | Claude Agent SDK (Python) | Satu-satunya jalur dengan `interrupt()`, `resume`, `can_use_tool` |
| MCP | Tahap 2, bukan fondasi | Hanya dibutuhkan bila sesi `claude` di terminal ikut bersuara |
| Channels | Eksperimen tahap 2 | Masih research preview; belum terbukti bisa mengendalikan eksekusi |
| Topologi | Dua proses lokal + STT di VPS | `FreeJarvis.app` (Swift) + `jarvisd` (Python); transkripsi di VPS agar CPU Intel lega |
| Barge-in | Diputuskan di laptop oleh VAD, target < 300 ms terukur | Tidak boleh bergantung jaringan |
| Pemakaian | Pribadi, satu pengguna | OAuth langganan hanya untuk pemakaian pribadi; bila dibagikan, tiap pengguna login sendiri |
| Bahasa | Antarmuka dan suara Bahasa Indonesia; kode dan identifier Inggris | Konvensi kerja Pak Syams |
| Nama | FreeJarvis, kata panggil bawaan "Jarvis" (bisa diganti) | Dari dokumen desain awal |

Dokumen desain awal (versi VPS, lima layanan, enam alat MCP) tetap menjadi referensi konsep; dosir ini menggantikannya sebagai sumber kebenaran untuk `vcbd`.

## 2. Konsep produk dan pengalaman pengguna

Satu identitas suara, satu aplikasi menu bar, dan Claude Code sebagai pelaksana; pengguna bicara dengan Jarvis tanpa membuka terminal. Mikrofon tetap aktif saat Jarvis berbicara, sehingga pengguna bisa menyela, mengoreksi, dan membatalkan kapan saja.

Contoh percakapan yang menjadi acuan uji:

1. Pengguna: "Jarvis, buka proyek SIPADI." → Jarvis: "Proyek SIPADI terbuka, sesi kemarin dilanjutkan."
2. Pengguna: "Periksa modul login." → Jarvis: "Baik, saya periksa." (status di layar: membaca `LoginController.php`)
3. Pengguna menyela: "Sebentar, bagian validasi saja." → audio berhenti < 300 ms, Jarvis: "Baik, fokus validasi."
4. Claude bertanya lewat `AskUserQuestion` → Jarvis membacakan pertanyaan, menunggu jawaban suara.
5. Pengguna: "Batalkan pekerjaan." → `interrupt()`, Jarvis: "Dibatalkan. Ada dua berkas berubah, lihat di layar."

Antarmuka `FreeJarvis.app` (menu bar, jendela kecil yang bisa dilepas):

| Elemen | Isi |
| --- | --- |
| Orb suara | Visualisasi amplitudo; warna mengikuti status percakapan |
| Baris status | Status percakapan dan status pekerjaan ditampilkan terpisah |
| Transkrip | Transkrip final per giliran; transkrip sementara tampil pudar |
| Panel layar | Panel kanan tetap (Viewer): kode, diff, tabel, log, pertanyaan, dan teks di bawah penanda `---layar---` |
| Proyek dan sesi | Proyek aktif (`cwd`), id sesi, tombol lanjutkan sesi |
| Jatah | Sisa jendela langganan dan kredit API bulanan dari respons SDK |
| Kontrol | Push-to-talk (hotkey global), bisukan, sela, batalkan, pilih proyek, pilih model |

Jawaban lisan dibatasi dua kalimat. Semua yang panjang atau berbentuk kode masuk panel layar, tidak dibacakan.

### Mode layar: ketika Jarvis perlu menampilkan teks

Jendela FreeJarvis terbagi dua panel tetap: panel kiri adalah antarmuka percakapan (orb, status, transkrip, kontrol), panel kanan adalah Viewer tempat Jarvis menampilkan sesuatu atas inisiatifnya sendiri atau atas perintah pengguna. Viewer selalu terlihat; saat kosong ia menampilkan ringkasan proyek dan sesi aktif, bukan panel abu-abu. Jarvis mengumumkan isi baru dengan satu kalimat ("Detail ada di Viewer") dan lampu pada tab yang terisi.

| Pemicu | Yang ditampilkan | Perilaku suara |
| --- | --- | --- |
| Teks model setelah `---layar---` | Markdown dirender: heading, daftar, kode dengan highlight | Jarvis hanya membacakan bagian lisan |
| `PostToolUse` pada `Edit`/`Write` | Diff per berkas dengan nama berkas dan tombol "Buka di editor" | "Mengubah `LoginController.php`", maksimal 1×/10 detik |
| `Bash` selesai | Log perintah, dilipat, 50 baris terakhir | Hanya ringkasan: "tes lolos, 3 gagal" |
| `AskUserQuestion` dengan pilihan | Kartu pertanyaan dengan tombol pilihan; bisa dijawab suara atau klik | Pertanyaan dibacakan utuh, pilihan dibacakan bila ≤ 3 |
| Permintaan izin tingkat layar | Kartu persetujuan dengan perintah lengkap, tombol Izinkan/Tolak | "Perlu persetujuan di layar" |
| Perintah suara "tampilkan", "baca bagian kedua", "tutup layar" | Mengganti tab Viewer, membacakan blok yang ditunjuk, mengosongkan Viewer | Mengikuti perintah |

Viewer memiliki empat tab: Jawaban, Perubahan, Log, Pertanyaan. Setiap blok punya tombol salin dan "Bacakan". Lebar panel bisa digeser, dengan rasio bawaan 40:60 (percakapan : Viewer) karena diff dan log butuh lebar; di layar sempit Viewer bisa dilipat menjadi ikon. Panel kiri juga menyediakan kolom ketik di bawah transkrip untuk masukan campuran suara dan teks, misalnya menempelkan path atau pesan galat yang sulit diucapkan.

### Prototipe antarmuka (acuan `26_UI_CONVENTIONS`)

Tiga keadaan di bawah adalah acuan visual yang disepakati 8 Oktober 2026; kanvas yang bisa disunting ada di [Prototipe UI FreeJarvis](https://claude.ai/artifact/Pg7DDVzj4uxepauPinCuoe). Rasio panel 40:60, tema gelap, aksen sian `#38BDF8`, peringatan amber `#F59E0B`, destruktif merah `#F87171`, huruf Manrope untuk antarmuka dan JetBrains Mono untuk kode.

**Keadaan 1 · Siap.** Viewer kosong menampilkan ringkasan proyek, sesi, model, dan berkas terakhir disentuh.

&#91;image: Keadaan 1: siap, Viewer kosong\]

**Keadaan 2 · Claude bekerja.** Dua pil status terpisah, transkrip bergiliran dengan ucapan sementara yang pudar, Viewer membuka tab Perubahan dengan diff dan tombol Bacakan / Salin / Buka di editor.

&#91;image: Keadaan 2: Claude bekerja, diff di Viewer\]

**Keadaan 3 · Menunggu izin (frasa aksi).** Orb amber, kartu persetujuan di dalam transkrip menyebut frasa yang diterima, Viewer membuka tab Pertanyaan dengan detail perintah, baris "Mendengar frasa", dan tombol klik sebagai cadangan.

&#91;image: Keadaan 3: menunggu izin lewat frasa aksi\]

### Identitas visual: logo freeJARVIS

Tanda terdiri dari cincin terbuka, gelombang suara lima batang, dan kait J; wordmark menulis "free" tipis dan "JARVIS" tebal. Berkas sumber ada di artboard "Logo" pada kanvas prototipe; untuk `26_UI_CONVENTIONS` dan aset Xcode, aturan di bawah mengikat.

&#91;image: Logo freeJARVIS: lockup utama, varian terang, ikon aplikasi, ikon menu bar, warna dan huruf\]

| Unsur | Spesifikasi |
| --- | --- |
| Tanda (mark) | Kanvas 100×100: cincin `r=41`, tebal 7, celah 40 unit di kanan atas (`rotate(-68)`); lima batang lebar 6, tinggi 14–26–40–26–14; batang tengah dilanjutkan kait J (`a9.5 9.5 0 0 1 -19 0`) |
| Makna | Cincin terbuka = percakapan full-duplex dan "free"; batang = gelombang suara, sama dengan orb aplikasi; kait J = nama panggil "Jarvis" |
| Warna latar gelap | Cincin sian `#38BDF8`, batang putih `#E6EDF7`, latar navy `#0B1220` |
| Warna latar terang | Cincin sian tua `#0284C7`, batang navy `#0B1220`, latar `#F5F7FB` |
| Wordmark | Manrope: "free" 400 warna `#8A9BB5`, "JARVIS" 800 warna `#E6EDF7` (terang: `#5B6B85` / `#0B1220`), letter-spacing 0.06em |
| Ikon aplikasi macOS | Persegi sudut membulat (radius 23% sisi), gradien `#163A52` → `#0B1220`, tanda 68% sisi, tanpa wordmark |
| Ikon menu bar | Template monokrom 18 px; versi ringkas tiga elemen (cincin, kait J, satu batang kanan); berdenyut saat Jarvis bicara |
| Ukuran minimum | Tanda penuh 28 px; di bawah itu pakai versi tiga elemen. Ruang aman = tinggi satu batang pendek |
| Ekspor untuk Xcode | `mark-dark.svg`, `mark-light.svg`, `mark-mono.svg`, `AppIcon.appiconset` 16–1024 px, `MenuBarIcon` 18/36 px template |

## 3. Arsitektur

Dua proses di laptop dan dua layanan di luar: `FreeJarvis.app` memegang audio dan layar, `jarvisd` memegang seluruh logika, VPS memegang transkripsi, dan Claude Code dijalankan `jarvisd` lewat Agent SDK.

&#91;embedded content: arsitektur FreeJarvis · 2 proses lokal, 2 layanan luar\]

Keputusan "berhenti bicara" diambil di `FreeJarvis.app` begitu VAD lokal mendeteksi suara pengguna; `jarvisd` baru menafsirkan maksud selaan setelah audio sudah berhenti. Kotak MCP bergaris putus karena baru dibangun di tahap 2.

| Komponen | Tanggung jawab | Tidak bertanggung jawab atas |
| --- | --- | --- |
| `FreeJarvis.app` | Mic dan speaker lewat `AVAudioEngine` Voice Processing I/O, VAD lokal untuk barge-in, pemutar TTS dan posisi baca, orb, transkrip, panel layar, hotkey | Logika percakapan, panggilan model, STT |
| `jarvisd` | Mesin status percakapan dan pekerjaan, Agent SDK, `can_use_tool`, hook, narator status, pemisah lisan/layar, klien STT, TTS router, SQLite | Audio mentah, rendering UI |
| VPS STT | Menerima potongan audio pasca-VAD (2–8 detik), mengembalikan transkrip; `faster-whisper` int8 | Deteksi giliran, barge-in |
| Claude Code | Pelaksana kerja di `cwd` proyek, bertanya lewat `AskUserQuestion`, mengirim hook | Pengelolaan suara |

## 4. Integrasi Claude Code

Agent SDK adalah inti; MCP, hook, dan Channels adalah pelengkap dengan prioritas menurun. Kebijakan Anthropic per 8 Oktober 2026: Agent SDK, `claude -p`, dan aplikasi pihak ketiga ditarik dari batas langganan, dan Max mendapat kredit API bulanan ([sumber](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)); OAuth langganan hanya untuk pemakaian pribadi ([sumber](https://code.claude.com/docs/en/legal-and-compliance)).

| Jalur | Peran di FreeJarvis | Tahap | Kemampuan kunci |
| --- | --- | --- | --- |
| Agent SDK (Python, `ClaudeSDKClient`) | Mode percakapan: sesi dijalankan `jarvisd` | 1 | `query`, stream `ToolUseBlock`/`ResultMessage`, `interrupt()`, `resume=<session_id>`, `cwd` per proyek, `can_use_tool`, pilih model per giliran |
| `AskUserQuestion` (alat bawaan Claude Code) | Pengganti `jarvis_ask`: Claude bertanya, Jarvis membacakan, jawaban suara dikembalikan via `can_use_tool` | 1 | Perlu verifikasi: alat ini muncul di `can_use_tool` pada versi SDK terpasang |
| Hook SDK (`PostToolUse`, `Stop`, `Notification`) | Narator status dan tampil diff tanpa token model | 1 | Dipasang lewat opsi hooks SDK, bukan `settings.json` |
| Hook Claude Code CLI (`Stop`, `Notification`) | Pengumuman satu arah dari sesi terminal: "Claude selesai, tiga berkas berubah" | 2 | `curl` ke `jarvisd` di `127.0.0.1` |
| MCP Streamable HTTP `:8765` | Sesi `claude` di terminal bisa bicara dan bertanya | 2 | `jarvis_speak`, `jarvis_ask` (memblokir), `jarvis_show`, `jarvis_stop_speaking`; fungsi sama dengan in-process `create_sdk_mcp_server` |
| Channels | Menyuntik ucapan ke sesi terminal yang terbuka | 2, eksperimen | Research preview sejak Claude Code v2.1.80; butuh login claude.ai dan flag `--channels`; belum terbukti bisa menginterupsi |

Aturan tetap untuk Engine:

- Lingkungan `jarvisd` tidak boleh memuat `ANTHROPIC_API_KEY`; kalau ada, SDK memilihnya dan menagih ke API key, bukan langganan. Kode melakukan `env.pop("ANTHROPIC_API_KEY", None)`.
- Pertanyaan status ("sudah sampai mana?") dijawab `jarvisd` dari peristiwa stream yang tersimpan, tidak diteruskan ke model.
- Sesi suara memakai system prompt tambahan: jawaban lisan maksimal dua kalimat Bahasa Indonesia; kode, tabel, log, dan penjelasan panjang ditulis setelah penanda `---layar---`.
- Koreksi saat Claude bekerja: `interrupt()`, lalu kirim giliran baru berawalan "Koreksi dari pengguna: …". Pembatalan dinyatakan berhasil hanya setelah stream benar-benar berhenti.
- Setelah pembatalan, `jarvisd` menjalankan `git status --short` di `cwd` dan menampilkannya di panel layar.

## 5. Pipeline suara

Urutan tetap: mic → AEC macOS → VAD lokal → potong per ucapan → STT di VPS → turn detection → Engine → pemisah lisan/layar → TTS → speaker, dengan mic tetap aktif selama TTS berbunyi.

| Tahap | Komponen awal | Opsi naik kelas | Catatan untuk Intel 2019 |
| --- | --- | --- | --- |
| AEC, noise, AGC | `AVAudioEngine` dengan `setVoiceProcessingEnabled(true)` | — | Tersedia di Intel; tahap 0–1 diuji dengan headset dulu |
| VAD | Silero VAD di `FreeJarvis.app` (untuk barge-in) dan `jarvisd` (untuk pemotongan) | — | Ringan, aman di CPU |
| STT | `faster-whisper` int8 di VPS, model `large-v3-turbo`; fallback `medium` bila CPU VPS 4 inti | Penyedia streaming cloud id-ID (Azure, Deepgram) lewat `STTProvider` | Tidak ada MLX atau CoreML; `whisper.cpp small` lokal hanya cadangan offline |
| Initial prompt STT | Kosakata proyek: nama kelas, tabel, berkas dari `cwd` | — | Mengurangi salah dengar istilah teknis campuran |
| Turn detection | Jeda adaptif \~700 ms; lebih lama bila ucapan menggantung ("terus…", "dan…") | Klasifikator semantik ringan | Tidak bersandar pada transkrip sementara Whisper |
| TTS | `AVSpeechSynthesizer` suara sistem id-ID (offline, instan) | Azure Neural id-ID / ElevenLabs lewat `TTSProvider` | — |
| Kata panggil | openWakeWord, model "Jarvis" | — | Tahap 3 |

Pemisah lisan/layar bekerja berlapis: (1) system prompt membatasi jawaban lisan dua kalimat; (2) narator di `jarvisd` mengubah peristiwa alat jadi kalimat pendek, maksimal satu kali per 10 detik; (3) penjaga panjang memotong teks lisan di batas kalimat dan menutup dengan "Detail lengkap ada di layar."

Transkrip sementara hanya untuk indikator di layar; perintah dikirim ke Engine setelah giliran dinyatakan selesai oleh turn detection.

## 6. Interupsi, koreksi, dan dua mesin status

"Sebentar" menjeda suara tanpa menyentuh pekerjaan; "batalkan" menghentikan pekerjaan lewat `interrupt()` tanpa mematikan percakapan. Keduanya hidup di mesin status yang berbeda, dan pengguna selalu mendapat prioritas saat terjadi bicara bersamaan.

&#91;embedded content: dua mesin status · percakapan dan pekerjaan\]

Target respons selaan: audio berhenti 150–300 ms setelah VAD lokal mendeteksi suara pengguna, diukur pada tahap 1. `FreeJarvis.app` melaporkan posisi baca saat disela; `jarvisd` membuang antrean audio lama dan menandai kalimat mana yang sudah terdengar.

| Ucapan selaan | Tafsiran | Aksi |
| --- | --- | --- |
| "Sebentar", "tunggu" | Jeda | Percakapan → dijeda; pekerjaan tetap berjalan |
| "Ringkas saja", "intinya" | Ubah bentuk jawaban | Potong jawaban lisan, sisanya ke layar |
| "Bukan itu, maksud saya …" | Koreksi instruksi | `interrupt()`, giliran baru berawalan "Koreksi dari pengguna: …" |
| "Batalkan pekerjaan" | Pembatalan | `interrupt()`; status batal setelah stream berhenti; `git status --short` ke layar |
| "Iya", "hmm", "oke" saat Jarvis bicara | Backchannel | Tidak mengakhiri giliran Jarvis |
| "Iya" saat status menunggu izin atau jawaban | Persetujuan atau jawaban | Dikembalikan ke `can_use_tool` atau `AskUserQuestion` |

Status pekerjaan hanya bersumber dari peristiwa SDK. Bila belum ada peristiwa, Jarvis berkata "masih menunggu laporan", bukan mengarang kemajuan.

## 7. Persetujuan berjenjang, privasi, batas penggunaan

Semua tingkat persetujuan bisa dilakukan lewat suara; yang berbeda adalah seberapa mahal ucapannya: kata singkat untuk tindakan di dalam proyek, frasa yang menyebut nama tindakan untuk jaringan dan penghapusan, dan kode dua kata yang hanya tampil di layar untuk tindakan tak terbalikkan. Klik dan Touch ID tetap tersedia sebagai cadangan, bukan keharusan. Persetujuan terikat pada satu tindakan, satu sesi, dan batas waktu.

| Tingkat | Contoh alat | Cara setuju (suara adalah jalur utama; klik hanya cadangan) | Batas waktu |
| --- | --- | --- | --- |
| Otomatis | `Read`, `Grep`, `Glob`, menjalankan tes | Tanpa tanya; dicatat di log | — |
| Kata singkat | `Edit`, `Write` di dalam `cwd` proyek | "Ya" / "lanjut" lewat `can_use_tool`; backchannel saat Jarvis masih bicara diabaikan | 60 detik, lalu dianggap ditolak |
| Frasa aksi | `git push`, akses jaringan, `Bash` dengan `rm`, berkas di luar `cwd` | Mengucapkan nama tindakannya: "izinkan push", "izinkan hapus"; "ya" saja diabaikan. Jarvis menyebut frasa yang diharapkan dan Viewer menampilkannya | 120 detik |
| Kode layar | `rm -rf`, `push --force`, drop tabel, menyentuh kunci API atau `.env` | Mengucapkan kode dua kata acak yang hanya tampil di Viewer (mis. "merpati tujuh"), bukti pengguna melihat layar; Touch ID opsional sebagai pengganti | 120 detik |

Privasi dan akses:

- Indikator mikrofon selalu terlihat di menu bar; tombol bisu memutus tangkapan audio di tingkat `AVAudioEngine`, bukan hanya di UI.
- Audio mentah tidak disimpan. Potongan audio ke VPS dihapus setelah transkrip kembali; VPS tidak menyimpan audio.
- Transkrip final disimpan di SQLite lokal dengan retensi yang bisa diatur (bawaan 30 hari).
- `jarvisd` hanya mendengarkan di `127.0.0.1`; koneksi ke VPS memakai TLS dan token.
- Satu pengguna, satu akun Max. Bila FreeJarvis dibagikan, tiap pemakai login Claude Code sendiri; token OAuth Pak Syams tidak pernah disalin ke mesin lain.

## 8. Kebijakan model dan jatah Max

Model dipilih per jenis giliran agar Jarvis bisa cerewet tanpa menghabiskan jatah: giliran ringan memakai Sonnet, pekerjaan kode memakai Opus, dan status tidak memakai model sama sekali.

| Jenis giliran | Model | Catatan |
| --- | --- | --- |
| Status, kemajuan, "sudah sampai mana" | Tidak ada; dari peristiwa SDK | Nol token |
| Klarifikasi, konfirmasi, obrolan ringan | Sonnet | Dipilih per giliran lewat opsi SDK |
| Pekerjaan kode, review, refactor | Opus | Bawaan untuk instruksi kerja |
| Perintah "pakai model X" | Sesuai permintaan | Diumumkan Jarvis |

Panel jatah membaca sisa jendela langganan dan kredit API bulanan dari respons SDK (field batas laju pada `ResultMessage`) dan memperingatkan lewat suara saat tersisa 10%. Kehabisan jatah ditampilkan sebagai status `gagal` dengan alasan, bukan sebagai bug.

## 9. Stack teknologi dan struktur repo

Satu monorepo `freejarvis` dengan tiga paket: `app` (Swift), `jarvisd` (Python), dan `stt-server` (Python, dipasang di VPS). Python memegang seluruh logika agar sesuai keahlian utama; Swift hanya kulit audio dan UI.

| Lapisan | Pilihan | Versi minimum | Alasan |
| --- | --- | --- | --- |
| macOS | 13 Ventura atau lebih baru | sesuai dukungan MacBook Pro 2019 | Voice Processing I/O dan `AVSpeechSynthesizer` id-ID tersedia |
| `app` | Swift 5.9, SwiftUI, `MenuBarExtra`, `AVAudioEngine`, `AVSpeechSynthesizer`, `URLSessionWebSocketTask` | Xcode 15 | Akses langsung ke AEC sistem; Flutter desktop tetap butuh kode Swift untuk ini |
| `jarvisd` | Python 3.12, `claude-agent-sdk`, `asyncio`, `websockets`, `silero-vad`, `aiosqlite`, `pydantic` | — | Dijalankan `launchd` sebagai LaunchAgent pengguna |
| MCP (tahap 2) | `mcp` Python SDK, Streamable HTTP di `127.0.0.1:8765` | — | Alat yang sama dengan in-process `create_sdk_mcp_server` |
| `stt-server` | FastAPI, `faster-whisper` int8 `large-v3-turbo` (fallback `medium`), antrean satu pekerja | — | Endpoint `POST /transcribe` menerima WAV 16 kHz mono + initial prompt |
| Penyimpanan | SQLite: sesi, proyek, transkrip, pertanyaan tertunda, status pekerjaan | — | Satu berkas di `~/Library/Application Support/FreeJarvis/` |
| Kata panggil (tahap 3) | openWakeWord model "Jarvis" | — | Berjalan di `jarvisd` |

Struktur repo yang diusulkan:

```
freejarvis/
  app/            # Xcode project: FreeJarvis.app
  jarvisd/
    jarvisd/
      engine/     # Agent SDK client, can_use_tool, hooks, narator
      voice/      # VAD, klien STT, TTS router, pemisah lisan|layar
      conversation/ # mesin status percakapan & pekerjaan, interupsi
      mcp/        # tahap 2: server HTTP + definisi alat
      store/      # SQLite
      ws/         # protokol ke app
    tests/
  stt-server/     # FastAPI + faster-whisper, dipasang di VPS
  docs/           # paket blueprint vcbd (00–27)
```

Protokol `app` ↔ `jarvisd` (WebSocket, JSON): `audio.chunk`, `audio.vad` (mulai/berhenti bicara), `tts.play`, `tts.position`, `tts.stop`, `state.conversation`, `state.job`, `transcript.partial`, `transcript.final`, `screen.show`, `approval.request`, `approval.reply`, `quota.update`.

## 10. Tahapan pembangunan dan kriteria terima

Tahap 0 dikerjakan tanpa UI dan tanpa MCP agar dalam 1–2 minggu sudah terbukti apakah mode percakapan lewat Agent SDK terasa enak; UI, full-duplex, dan MCP menyusul setelah gerbangnya lolos.

&#91;embedded content: tahapan pembangunan · 4 tahap, 3 gerbang\]

Pengujian lintas tahap yang wajib ada di `23_ACCEPTANCE`: interupsi saat audio diputar, gema speaker, jeda berpikir pengguna, koreksi instruksi di tengah pekerjaan, pembatalan tugas, pergantian proyek, jaringan ke VPS terputus (STT fallback lokal `whisper.cpp small`), dan pencegahan perintah ganda setelah koneksi pulih (idempotency key per giliran).

## 11. Risiko, asumsi, dan verifikasi sebelum coding

Tiga hal wajib diverifikasi di tahap 0 sebelum `vcbd` mengunci kontrak: perilaku `AskUserQuestion` di `can_use_tool`, kecepatan STT di VPS, dan ketersediaan suara sistem id-ID di macOS laptop.

| Risiko / asumsi | Dampak bila salah | Mitigasi | Status |
| --- | --- | --- | --- |
| `AskUserQuestion` tidak lewat `can_use_tool` di versi SDK terpasang | `jarvis_ask` harus dibangun sebagai alat MCP in-process sejak tahap 0 | Uji di hari pertama tahap 0 | Belum diverifikasi |
| STT di VPS lebih lambat dari 1× realtime | Percakapan terasa lamban | Turun ke `medium` int8; opsi cloud lewat `STTProvider` | Belum diukur |
| Suara sistem id-ID tidak terpasang / kualitas rendah | TTS terdengar kaku | Unduh suara di System Settings; TTS cloud di tahap 3 | Belum dicek |
| Kebijakan Agent SDK pada langganan berubah lagi | Biaya harian berubah | Panel jatah; `ANTHROPIC_API_KEY` sebagai jalur cadangan yang sadar biaya | Dipantau; artikel diperbarui 7 Okt 2026 |
| Channels tetap preview atau dihapus | Mode "ikut sesi terminal" hanya lewat MCP + hook | Channels tidak pernah jadi fondasi | Diterima |
| Whisper salah dengar istilah teknis campuran | Nama berkas meleset | Initial prompt kosakata proyek; konfirmasi nama berkas lewat layar | Diterima |
| Interupsi meninggalkan berkas setengah jadi | Kode rusak tanpa disadari | `git status --short` ke layar setelah `interrupt()` | Diterima |
| Kipas MacBook Intel masuk mikrofon saat CPU sibuk | VAD salah picu | STT di VPS; noise suppression Voice Processing I/O; uji dengan speaker di tahap 2 | Diterima |
| macOS di laptop tidak lagi mendapat pembaruan Apple | API baru (SpeechAnalyzer) tidak tersedia | Tidak memakai API yang butuh macOS 26 | Diterima |

## 12. Jawaban awal wawancara vcbd (K1–K10)

Jawaban di bawah mengisi wawancara `vcbd` lebih dulu; skill tetap menyajikan Ringkasan Kebutuhan untuk dikonfirmasi sebelum menulis 28 dokumen.

| K | Pertanyaan | Jawaban |
| --- | --- | --- |
| K1 | Nama, tujuan, pengguna | FreeJarvis; percakapan suara full-duplex untuk mengendalikan Claude Code; satu pengguna (Pak Syams), pemakaian pribadi |
| K2 | Platform dan bentuk | Aplikasi menu bar macOS (Intel 2019) + daemon Python; bukan web, bukan mobile |
| K3 | Stack | Swift/SwiftUI untuk `app`; Python 3.12 + `claude-agent-sdk` untuk `jarvisd`; FastAPI + `faster-whisper` untuk `stt-server` di VPS; SQLite |
| K4 | Mode repo | Monorepo tiga paket; tanpa SPLIT backend/frontend; kontrak WebSocket `app`↔`jarvisd` dan HTTP `jarvisd`↔`stt-server` didokumentasikan di `27_API_CONTRACT` |
| K5 | Fitur inti MVP (tahap 0–1) | Push-to-talk, STT, jawaban suara, pemisah lisan/layar, interupsi, pembatalan, resume sesi, pilih proyek, persetujuan berjenjang, panel layar, panel jatah |
| K6 | Di luar cakupan MVP | MCP server, Channels, kata panggil, multi-proyek paralel, agen selain Claude Code (Hermes, OpenClaw, Codex), TTS cloud, mobile |
| K7 | Integrasi eksternal | Claude Agent SDK (login Max), VPS STT milik sendiri, hook Claude Code; tidak ada layanan pihak ketiga lain di MVP |
| K8 | Keamanan dan privasi | Lihat bagian 7: `127.0.0.1` saja, TLS + token ke VPS, audio tidak disimpan, retensi transkrip 30 hari, `ANTHROPIC_API_KEY` dibuang dari lingkungan |
| K9 | UI dan token desain | Dua panel tetap (kiri percakapan, kanan Viewer, rasio 40:60, bisa digeser); tema gelap, satu aksen biru-sian, orb sebagai elemen utama; status percakapan dan pekerjaan selalu dua baris terpisah; Bahasa Indonesia; `26_UI_CONVENTIONS` wajib |
| K10 | Kriteria selesai | Gerbang per tahap di bagian 10; MVP dinyatakan selesai saat gerbang tahap 1 lolos dengan pengukuran, bukan asumsi |
