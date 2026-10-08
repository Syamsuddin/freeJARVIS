# 16 — Debugging Guide
Log: docs/15. Perintah: docs/11. Galat: docs/14.

## Gejala → diagnosa
| Gejala | Periksa |
|---|---|
| Tagihan masuk ke API, bukan langganan | `uv run python -m jarvisd.diag sdk`; `launchctl print gui/$UID/id.freejarvis.jarvisd \| grep ANTHROPIC` |
| Jarvis tak berhenti saat disela | log app kategori `audio`: VAD terpicu? `vad_to_stop_ms`? Headset vs speaker? |
| VAD terpicu sendiri | kipas/CPU sibuk; cek ambang `LocalVAD`; VPIO aktif (`isVoiceProcessingEnabled`) |
| Jawaban lambat | log `stt_ms` (VPS) vs `stt_to_first_tts_ms` (model); `stt_server.bench` untuk RTF |
| Salah dengar nama berkas | `projects.vocabulary` terisi? initial prompt terkirim? |
| Status "membatalkan" macet | stream SDK masih mengirim? log `engine` sejak `interrupt` |
| App "jarvisd terputus" | `launchctl print gui/$UID/id.freejarvis.jarvisd`; port 8764 dipakai proses lain (`lsof -i :8764`) |
| Viewer tak menampilkan diff | hook `PostToolUse` terpasang di opsi SDK? log `event=hook` |

## Jebakan proyek
- **`ANTHROPIC_API_KEY`** di env → SDK memakainya dan menagih API key. `engine/sdk_client.py` wajib `env.pop("ANTHROPIC_API_KEY", None)` untuk env subprocess; jangan "memperbaiki" galat login dengan menambahkan key.
- **`interrupt()` ≠ batal.** Stream bisa masih mengirim pesan; status `cancelled` hanya setelah stream berakhir.
- **Transkrip sementara** Whisper tidak stabil; jangan pernah memicu aksi darinya.
- **Backchannel** "iya"/"oke" saat Jarvis bicara terlihat seperti persetujuan. Bukan.
- **Kipas MacBook Intel** saat CPU sibuk (Claude Code + build) bisa memicu VAD; uji dengan beban CPU.
- **Hook SDK** dipasang lewat opsi `hooks` di `ClaudeAgentOptions`, bukan `.claude/settings.json`; mengubah settings proyek pengguna dilarang.
- **`AskUserQuestion`** perilakunya di `can_use_tool` belum diverifikasi; jangan berasumsi sebelum G0 (docs/03).
- **Voice Processing I/O** mengubah format/sample rate input; selalu konversi ke 16 kHz mono sebelum VAD/STT.
