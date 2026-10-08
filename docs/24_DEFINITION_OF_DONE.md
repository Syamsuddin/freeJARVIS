# 24 — Definition of Done
Berlaku untuk semua task.

- [ ] Kriteria terima fitur di docs/23 terpenuhi, blok verifikasinya dijalankan dan hasilnya dicantumkan.
- [ ] Tes paket yang disentuh hijau (`jarvisd`, `stt-server`, dan/atau `app`; perintah docs/11), termasuk tes baru untuk perilaku baru.
- [ ] Lint + mypy bersih untuk Python; build Xcode tanpa warning baru.
- [ ] Tanpa regresi: suite penuh paket terkait hijau, bukan hanya tes baru.
- [ ] Bila menyentuh audio/barge-in/STT/TTS: angka latensi sebelum/sesudah dari `jarvisd.bench`.
- [ ] Struktur & penamaan sesuai docs/12; nilai UI hanya dari token docs/26.
- [ ] Protokol berubah → docs/27 + `messages.py` + `Messages.swift` + fixture diperbarui di commit yang sama.
- [ ] Tidak melanggar docs/20 & docs/21.
- [ ] Fakta blueprint berubah → dokumen pemilik + `_MANIFEST.json` diperbarui, `bash scripts/validate.sh` tanpa `[FAIL]`.
