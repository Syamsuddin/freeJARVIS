# 27 — API Contract (antar-proses)
Rumah tunggal protokol `app` ↔ `jarvisd` (WebSocket) dan `jarvisd` ↔ `stt-server` (HTTP). Mode tunggal, bukan split: tak ada `kontrak/openapi.yaml`. Cermin kode: `jarvisd/jarvisd/ws/messages.py` (pydantic) dan `app/FreeJarvis/IPC/Messages.swift` (Codable). **Dokumen ini menang**: kode yang berbeda = bug; selisih → berhenti & lapor. Perubahan breaking = gerbang manusia (docs/22).

`protocol_version`: **1**

## WebSocket `ws://127.0.0.1:8764/v1`
Amplop tiap pesan teks: `{"type": "<jenis>", "id": "<uuid4>", "ts": "<ISO-8601 UTC>", ...field}`. Field `snake_case`. Audio dikirim sebagai **frame biner** (bukan JSON) agar tak membengkak base64.

Handshake: pesan pertama app = `hello`; `jarvisd` membalas `hello.ack` atau menutup 4401 (token salah) / 4426 (versi beda).

### App → jarvisd
| type | Field | Arti |
|---|---|---|
| `hello` | `token`, `protocol_version`, `app_version` | buka sesi; token dari `ws.token` (docs/21) |
| *(biner)* `audio.chunk` | PCM s16le 16 kHz mono, 20 ms/frame (640 byte) | dikirim hanya saat mic aktif & tak dibisukan |
| `audio.vad` | `event`: `start`\|`end`, `during_tts`: bool | VAD lokal; `start` saat `during_tts` = barge-in (app SUDAH menghentikan audio) |
| `tts.position` | `utterance_id`, `sentence_index`, `char_offset`, `reason`: `progress`\|`interrupted`\|`finished` | posisi baca |
| `text.input` | `text`, `idempotency_key` | kolom ketik |
| `approval.reply` | `prompt_id`, `decision`: `allow`\|`deny`\|`answer`, `answer?`, `via`: `click`\|`touch_id` | jawaban klik; jawaban suara diputuskan `jarvisd` |
| `ui.command` | `action`: `ptt_down`\|`ptt_up`\|`mute`\|`unmute`\|`pause`\|`cancel_job`\|`select_project`\|`select_model`\|`viewer_tab`\|`viewer_read`\|`viewer_clear`\|`resume_session`, `arg?` | tombol & hotkey; `arg` = nama proyek / model / tab / `block_id` |

### jarvisd → App
| type | Field | Arti |
|---|---|---|
| `hello.ack` | `protocol_version`, `project?`, `session?`, `conversation`, `job` | keadaan awal; app merender dari sini |
| `state.conversation` | `state` (docs/06), `detail?` | ganti pil + orb |
| `state.job` | `state` (docs/06), `activity?` (mis. "mengedit LoginController.php"), `tier?`, `fail_reason?` | ganti pil kedua |
| `transcript.partial` | `text` | ucapan sementara (pudar); tak pernah memicu aksi |
| `transcript.final` | `turn_id`, `speaker`: `user`\|`jarvis`, `text`, `channel` | baris transkrip |
| `tts.play` | `utterance_id`, `sentences`: [str], `voice` | app memutar berurutan, melapor `tts.position` |
| `tts.stop` | `utterance_id`, `reason` | hentikan sekarang |
| `screen.show` | `tab`: `answer`\|`changes`\|`log`\|`questions`, `block_id`, `kind`: `markdown`\|`diff`\|`log`\|`summary`\|`git_status`, `title`, `content`, `meta?` (`file_path`, `added`, `removed`, `writing`) , `mode`: `append`\|`replace` | isi Viewer; lampu tab |
| `screen.clear` | `tab?` | kosongkan Viewer (tanpa tab = semua → ringkasan proyek) |
| `approval.request` | `prompt_id`, `kind`: `approval`\|`question`, `tier?`, `tool?`, `command?`, `cwd?`, `details?` (commit, berkas, tes), `expected_phrase?`, `screen_code?`, `options?`, `expires_at` | kartu persetujuan/pertanyaan; `screen_code` hanya tampil di Viewer |
| `approval.resolved` | `prompt_id`, `resolution` | tutup kartu |
| `quota.update` | `window_remaining_pct?`, `window_resets_at?`, `credit_remaining_pct?` | panel jatah |
| `project.summary` | `project`, `path`, `branch`, `session_label`, `model_policy`, `recent_files`: [{`path`,`added`,`removed`}] | Viewer kosong (Keadaan 1) |
| `error` | `code`, `message`, `detail?` | docs/14; `message` Bahasa Indonesia untuk layar |

Kode `error.code`: `bad_message`, `unknown_type`, `stt_unavailable`, `sdk_failed`, `quota_exhausted`, `project_not_found`, `internal`.

## HTTP `stt-server`
| Metode & path | Request | Respons 200 | Galat |
|---|---|---|---|
| `POST /transcribe` | `multipart/form-data`: `audio` (WAV 16 kHz mono s16, ≤ 8 s), `prompt?` (initial prompt kosakata, ≤ 800 karakter), `language` (`id`); header `Authorization: Bearer`, `X-Request-Id` | `{"text": str, "duration_s": float, "infer_ms": int, "model": str}` | 400 format, 401 token, 411 tanpa Content-Length, 413 > 1 MB atau > `STT_MAX_AUDIO_S`, 429 rate limit, 503 model belum siap |
| `GET /healthz` | — | `{"status": "ok", "model": str}` | 503 |
Galat berbentuk `{"error": {"code": str, "message": str}}`.

## Aturan perubahan
- Additive (pesan/field opsional baru): perbarui tabel ini + `messages.py` + `Messages.swift` + fixture `jarvisd/tests/fixtures/protocol/` dalam satu commit; `protocol_version` tetap.
- Breaking: naikkan `protocol_version`, gerbang manusia (docs/22), app & `jarvisd` dirilis bersamaan.
- Tahap 2 (MCP `:8765`) menambah bagian baru di dokumen ini saat dibangun, bukan sebelumnya.
