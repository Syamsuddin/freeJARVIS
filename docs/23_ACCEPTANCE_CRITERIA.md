# 23 — Acceptance Criteria
Per fitur aktif (docs/01). Patokan selesai = kriteria di sini + DoD (docs/24). Fitur yang diterima diarsipkan ke `docs/_archive/23-{fitur}.md`.

## G0 — Verifikasi tahap 0
| Cek | Perintah | Lulus |
|---|---|---|
| `AskUserQuestion` lewat `can_use_tool` | `cd jarvisd && uv run python -m jarvisd.diag ask` | mencetak `ask_via_can_use_tool=yes` + `answer_roundtrip=yes` (bila `no` → `jarvis_ask` in-process, docs/03). **LULUS 8 Okt 2026** (SDK 0.2.164, haiku & sonnet); ulangi di laptop bila SDK naik versi |
| Kecepatan STT | `cd stt-server && uv run python -m stt_server.bench --samples tests/fixtures/id-*.wav` | RTF ≤ 1,0 untuk `large-v3-turbo`, atau `medium` dipilih dan dicatat di docs/09 |
| Suara id-ID | `say -v '?' \| grep id_ID` | ≥ 1 suara; pengguna menyatakan layak |
| SDK tanpa API key | `cd jarvisd && uv run python -m jarvisd.diag sdk` | `auth=subscription`, `anthropic_api_key=absent` |

## AC-00 — Lima skenario acuan (gerbang G1, manual berskrip)
1. "Jarvis, buka proyek SIPADI." → "Proyek SIPADI terbuka, sesi kemarin dilanjutkan."; Viewer: ringkasan proyek.
2. "Periksa modul login." → "Baik, saya periksa."; pil kedua: "bekerja · membaca LoginController.php".
3. Menyela "Sebentar, bagian validasi saja." → audio berhenti < 300 ms (log `vad_to_stop_ms`) → "Baik, fokus validasi."
4. Claude memanggil `AskUserQuestion` → pertanyaan dibacakan → dijawab suara → pekerjaan berlanjut.
5. "Batalkan pekerjaan." → status `membatalkan` → `dibatalkan` → "Dibatalkan. Ada dua berkas berubah, lihat di layar." + `git status --short` di tab Perubahan.
Lulus: kelima skenario tanpa menyentuh terminal, direkam di `docs/_archive/g1-run-{tanggal}.md`.

## F02 — STT + fallback
- Given VPS hidup, When ucapan 4 s, Then `transcript.final` dalam ≤ 1,5 s setelah akhir ucapan.
- Given VPS mati, When pengguna bicara, Then fallback `whisper.cpp` dipakai + diumumkan sekali per putus.
- Given ucapan sementara, Then tak ada `query` yang dikirim.
```bash
cd jarvisd && uv run pytest -q tests/voice/test_stt_client.py tests/conversation/test_turn_detection.py
cd stt-server && uv run pytest -q
```
Lulus: semua passed.

## F04 — Pemisah lisan/layar
- Given teks model berisi `---layar---`, Then hanya bagian sebelum penanda yang masuk `tts.play`; sisanya `screen.show` tab Jawaban.
- Given lisan > 2 kalimat tanpa penanda, Then dipotong di batas kalimat ke-2 + "Detail lengkap ada di layar."; sisanya ke Viewer.
- Given 3 peristiwa `Edit` dalam 10 s, Then narator mengucap ≤ 1 kalimat.
```bash
cd jarvisd && uv run pytest -q tests/voice/test_splitter.py tests/engine/test_narrator.py
```

## F05/F06 — Interupsi, koreksi, pembatalan
- Given `speaking`, When `audio.vad{start, during_tts}`, Then antrean TTS dibuang dan `turns.heard_until` terisi.
- Given "sebentar", Then percakapan `paused` dan job tetap `running`.
- Given "bukan itu, maksud saya X" saat job `running`, Then `interrupt()` → tunggu stream berhenti → `query` baru berawalan "Koreksi dari pengguna: ".
- Given "batalkan pekerjaan", Then `cancelling` → (stream berhenti) `cancelled` → `git status --short` dikirim `screen.show{kind: git_status}`. Tidak ada `cancelled` sebelum stream berhenti.
- Given backchannel "iya" saat `speaking`, Then TTS berlanjut dan tak ada persetujuan.
```bash
cd jarvisd && uv run pytest -q tests/conversation/test_interruption.py tests/conversation/test_job_state.py
cd jarvisd && uv run python -m jarvisd.bench latency --runs 50
```
Lulus: tes passed; bench `barge_in_p95_ms < 300`.

## F07 — Proyek & sesi
- Given proyek "sipadi" punya `last_session_id`, When "buka proyek sipadi", Then `ClaudeSDKClient` dibuat dengan `cwd`=path dan `resume`=id sesi.
- Given nama tak cocok, Then kandidat tampil di Viewer, tak ada `cwd` berubah.
- Given job `running`, When ganti proyek, Then Jarvis bertanya dulu.
```bash
cd jarvisd && uv run pytest -q tests/engine/test_sdk_client.py tests/conversation/test_project_switch.py
```

## F08 — Persetujuan berjenjang
- Tiap baris matriks docs/05 punya kasus tes klasifikasi; `Bash` tak dikenal → Frasa aksi.
- Given Frasa aksi "izinkan push", When pengguna berkata "ya", Then ditolak sebagai jawaban dan Jarvis mengulang frasa.
- Given Kode layar, Then `screen_code` tak muncul di `tts.play` maupun log.
- Given batas waktu lewat, Then `deny` + `pending_prompts.resolution='expired'`.
```bash
cd jarvisd && uv run pytest -q tests/engine/test_permissions.py tests/conversation/test_approval_flow.py
```

## F09/F10/F12 — Viewer, narator status, kolom ketik
- Given `PostToolUse` `Edit`, Then `screen.show{tab: changes, kind: diff}` dengan path, +/−.
- Given `Bash` selesai, Then tab Log berisi 50 baris terakhir; suara hanya ringkasan.
- Given "sudah sampai mana?", Then dijawab dari `tool_events` tanpa memanggil model; tanpa peristiwa → "Masih menunggu laporan."
- Given perintah "tampilkan perubahan" / "baca bagian kedua" / "kosongkan layar", Then tab berganti / blok ke-2 dibacakan / `screen.clear`.
- Given `text.input` dengan key yang sama dua kali, Then satu `query`.
```bash
cd jarvisd && uv run pytest -q tests/engine/test_hooks.py tests/conversation/test_status_query.py tests/ws/test_protocol.py
xcodebuild -project app/FreeJarvis.xcodeproj -scheme FreeJarvis -destination 'platform=macOS' test
```

## F11/F13 — Jatah & model
- Given `ResultMessage` membawa batas laju, Then `quota_snapshots` bertambah + `quota.update`; ≤ 10% → peringatan suara sekali per jendela.
- Given giliran klarifikasi, Then model `sonnet`; instruksi kerja → `opus`; status → tanpa model; "pakai model X" → diumumkan.
```bash
cd jarvisd && uv run pytest -q tests/engine/test_quota.py tests/engine/test_model_policy.py
```

## AC-90 — Skenario lintas tahap (manual berskrip tiap gerbang)
| Skenario | Lulus |
|---|---|
| Interupsi saat audio diputar | AC-00 #3 |
| Gema speaker (tanpa headset, tahap 2) | Jarvis tidak menyela dirinya sendiri 10 giliran berturut |
| Jeda berpikir ("terus…" lalu diam 1,2 s) | giliran tak dipotong |
| Koreksi di tengah pekerjaan | F05 koreksi |
| Pembatalan | AC-00 #5 |
| Pergantian proyek | F07 |
| VPS putus di tengah ucapan | fallback lokal, ucapan tidak hilang |
| Koneksi pulih → pesan diulang | tidak ada perintah ganda (idempotency) |
| Beban CPU tinggi (build berjalan) | tak ada VAD salah picu dalam 5 menit diam |
