# 13 — Testing
Pemilik strategi tes. Perintah: docs/11_COMMANDS.md. Kriteria per fitur: docs/23_ACCEPTANCE_CRITERIA.md.

## Jenis & cakupan
| Jenis | Alat | Lingkup | Target |
|---|---|---|---|
| Unit logika | pytest | `conversation/`, `engine/permissions.py`, `engine/narrator.py`, `voice/splitter.py`, `conversation/turn_detection.py`, `engine/model_policy.py` | ≥ 90% baris di modul ini |
| Integrasi `jarvisd` | pytest-asyncio + `FakeSDKClient` (stream berskrip `ToolUseBlock`/`ResultMessage`/interrupt) + klien WS uji | alur docs/06 A–E end-to-end tanpa model nyata | semua alur + cabang gagal |
| Protokol | pytest (skema pydantic) + XCTest (decode Codable) dari fixture JSON bersama `jarvisd/tests/fixtures/protocol/*.json` | tiap jenis pesan docs/27 | 100% jenis pesan |
| `stt-server` | pytest + `TestClient` FastAPI; transcriber dipalsukan kecuali tes bertanda `slow` | auth, batas ukuran, format galat | semua cabang |
| App | XCTest | `AppState` reduksi pesan → status UI, `TTSPlayer` posisi baca, `LocalVAD` ambang | logika non-UI |
| Pengukuran | `jarvisd.bench`, `stt_server.bench` | latensi barge-in, akhir-ucapan→suara, RTF STT | metrik docs/00 |
| Manual berskrip | daftar AC-90 di docs/23 | gema speaker, kipas, jaringan putus | tiap gerbang |

## Wajib dites (alur kritikal)
- Klasifikasi tingkat persetujuan: tiap baris docs/05 + kasus "tak dikenali → Frasa aksi"; "ya" ditolak untuk Frasa aksi; habis waktu → `deny`.
- Pembatalan: `cancelled` hanya setelah stream berhenti; `git status --short` dipanggil.
- Backchannel saat `speaking` tidak menjadi persetujuan.
- Transkrip sementara tidak pernah memicu `query`.
- Idempotency: `transcript.final` / `text.input` ganda dengan key sama → satu `query`.
- Pemisah lisan/layar: penanda `---layar---`, penjaga panjang (> 2 kalimat dipotong + "Detail lengkap ada di layar.").
- Pertanyaan status tidak memanggil model (assert `FakeSDKClient.query` tak dipanggil).
- `ANTHROPIC_API_KEY` dibuang dari env subprocess SDK.

## Aturan
- Tes tidak memanggil Claude asli maupun VPS asli; tes jaringan nyata bertanda `@pytest.mark.live`, tidak jalan di `pytest -q` bawaan.
- Bug yang diperbaiki → tes regresi dulu (docs/18).
