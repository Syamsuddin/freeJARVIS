# 03 — Roadmap
Fase = vertical slice yang bisa didemokan. Gerbang = syarat masuk tahap berikut, diukur (bukan diasumsikan). Kriteria rinci: docs/23_ACCEPTANCE_CRITERIA.md.

| Tahap | Tujuan demoable | Fitur | Durasi target |
|---|---|---|---|
| 0 — Inti tanpa UI | `jarvisd` jalan dari terminal: PTT keyboard → STT VPS → Agent SDK → TTS `say`/stub → jawaban dua kalimat; batal & resume via perintah | F02, F04 (lapis 1+3), F06, F07, F13; `stt-server` terpasang | 1–2 minggu |
| **G0** · status: 1/4 cek lulus (`diag ask`); `diag sdk`, STT VPS, suara id-ID menunggu dijalankan di laptop/VPS | 3 verifikasi [TERBUKA] terjawab: `AskUserQuestion` lewat `can_use_tool`; STT VPS ≥ 1× realtime (atau turun ke `medium`); suara id-ID layak. Percakapan terasa enak menurut pengguna | — | — |
| 1 — App + full-duplex | `FreeJarvis.app` dua panel; mic aktif saat TTS; barge-in VAD lokal; Viewer 4 tab; persetujuan suara 4 tingkat; jatah | F01, F03, F05, F08–F12, narator F10 | 3–4 minggu |
| **G1 = MVP selesai** | Metrik docs/00_EXECUTIVE_SUMMARY.md terukur + skenario lintas tahap AC-90 lolos | — | — |
| 2 — Ikut sesi terminal | MCP Streamable HTTP `127.0.0.1:8765` (`jarvis_speak`, `jarvis_ask`, `jarvis_show`, `jarvis_stop_speaking`); hook CLI `Stop`/`Notification`; eksperimen Channels | F20, F21 | [TERBUKA] |
| **G2** | Sesi `claude` terminal bisa bicara & bertanya lewat Jarvis; uji speaker tanpa headset lolos | — | — |
| 3 — Kenyamanan | Kata panggil "Jarvis"; TTS cloud lewat `TTSProvider` | F30, F31 | [TERBUKA] |

Aturan: tahap berikut tidak dimulai sebelum gerbangnya lolos. Bila G0 menemukan `AskUserQuestion` tidak lewat `can_use_tool`, `jarvis_ask` dibangun sebagai alat MCP in-process (`create_sdk_mcp_server`) di tahap 0, bukan di tahap 2.
