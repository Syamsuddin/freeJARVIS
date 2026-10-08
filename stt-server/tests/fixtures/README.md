# Sampel audio bench (`id-*.wav`)

`stt_server.bench` butuh WAV Bahasa Indonesia 16 kHz mono s16, 2–8 detik. Berkas WAV tidak di-commit (privasi suara pengguna); buat sendiri di Mac:

```bash
# Suara sistem id-ID (cepat, untuk RTF):
say -v Damayanti -o /tmp/s.aiff "Jarvis, periksa modul login, fokus validasi SSO."
afconvert -f WAVE -d LEI16@16000 -c 1 /tmp/s.aiff stt-server/tests/fixtures/id-login.wav

# Suara sendiri (lebih realistis untuk akurasi): rekam di QuickTime, lalu
afconvert -f WAVE -d LEI16@16000 -c 1 rekaman.m4a stt-server/tests/fixtures/id-rekaman-1.wav
```

Minimal 5 sampel: perintah pendek, nama berkas (`LoginController.php`), istilah campuran, kalimat 6–8 detik, dan satu ucapan dengan jeda.
