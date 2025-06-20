# 📱 SMS Spam Tool (Indonesia Targeted)

**Disclaimer: This tool is provided for educational and security testing purposes only. Do not use this tool for illegal activities or without proper authorization.**

## 📌 Deskripsi

Tool ini mengirimkan permintaan OTP (One-Time Password) secara berulang ke nomor ponsel yang ditargetkan, menggunakan berbagai layanan populer di Indonesia seperti Tokopedia, Grab, Matahari, Blibli, dan lainnya.

Tool ini dirancang untuk mendemonstrasikan bagaimana API abuse bisa terjadi jika tidak ada rate limiting atau verifikasi tambahan di sisi server.

## ⚙️ Fitur

- Mengirim spam OTP ke berbagai layanan.
- Dukungan multi-platform (API Tokopedia, Grab, Matahari, dll).
- Rotasi User-Agent otomatis dari file eksternal (`ua.txt`).
- Opsi untuk mengulangi proses spam.
- Efek pengetikan dan countdown visual di terminal.

## 🧾 Dependensi

Install dependensi yang diperlukan menggunakan:

```bash
pip install -r requirements.txt
```

File `requirements.txt`:

```
certifi==2025.4.26
charset-normalizer==3.4.2
idna==3.10
requests==2.32.4
urllib3==2.4.0
```

## 🚀 Cara Penggunaan

1. Siapkan file `ua.txt` berisi daftar User-Agent (satu per baris).
2. Jalankan script:

```bash
python main.py
```

3. Masukkan nomor HP target (format: 08xxxxxxxxxx).
4. Pilih apakah ingin mengulangi proses spam (opsional).

## 🛠 Struktur Proyek

- `main.py`: File utama yang berisi logic eksekusi dan konfigurasi API.
- `requirements.txt`: Dependensi Python.
- `ua.txt`: Daftar User-Agent yang digunakan secara acak (wajib disediakan).

## ⚠️ Peringatan

> Menggunakan tool ini untuk menyerang, melecehkan, atau mengganggu orang lain adalah **melanggar hukum** dan **tidak etis**. Selalu gunakan untuk pembelajaran, riset keamanan, atau pengujian atas izin yang sah.

## 👨‍💻 Author

- **Linctonnn**
