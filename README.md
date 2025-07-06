# 🤖 DeepSeek Discord Bot (Termux Optimized)

Bot Discord yang menggunakan DeepSeek API untuk percakapan AI. Dioptimalkan untuk dijalankan di Termux (Android).

## 🔥 Fitur Utama
- Perintah `!ai [pertanyaan]` untuk bertanya ke DeepSeek AI
- Sistem cooldown untuk mencegah spam
- Logging error otomatis
- Optimasi RAM & CPU untuk Android
- Perintah bantuan lengkap

## ⚙️ Instalasi di Termux

```bash
# Update package
pkg update && pkg upgrade -y

# Install Python & Git
pkg install python git -y

# Clone repo
git clone https://github.com/username/deepseek-discord-bot-termux.git
cd deepseek-discord-bot-termux

# Install dependencies
pip install -r requirements.txt

# Salin contoh .env
cp .env.example .env

# Edit .env dengan token Anda
nano .env
