import discord
import os
import requests
import asyncio
import traceback
from discord.ext import commands
from datetime import datetime

# ===== KONFIGURASI =====
PREFIX = "!"  # Prefix perintah
MAX_RESPONSE_LENGTH = 1800  # Batas karakter respons
REQUEST_TIMEOUT = 30  # Timeout request API (detik)
COOLDOWN_TIME = 10  # Cooldown antar perintah (detik)

# ===== SETUP LOGGING =====
def setup_logger():
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        filename='bot.log',
        level=logging.INFO,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('DeepSeekBot')

logger = setup_logger()

# ===== LOAD ENVIRONMENT =====
DISCORD_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
API_URL = "https://api.deepseek.com/chat/completions"

# ===== VALIDASI TOKEN =====
if not DISCORD_TOKEN:
    logger.error("DISCORD_BOT_TOKEN tidak ditemukan di .env!")
    exit(1)

if not DEEPSEEK_API_KEY:
    logger.error("DEEPSEEK_API_KEY tidak ditemukan di .env!")
    exit(1)

# ===== SETUP BOT =====
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# ===== COOLDOWN SYSTEM =====
user_cooldowns = {}

def check_cooldown(user_id):
    current_time = datetime.now().timestamp()
    last_time = user_cooldowns.get(user_id, 0)
    
    if current_time - last_time < COOLDOWN_TIME:
        return COOLDOWN_TIME - int(current_time - last_time)
    
    user_cooldowns[user_id] = current_time
    return 0

# ===== DEEPSEEK API HANDLER =====
def query_deepseek(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 1
        }
        
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code != 200:
            error_msg = f"API Error {response.status_code}: {response.text}"
            logger.error(error_msg)
            return f"⚠️ Error API: {response.status_code}"
        
        data = response.json()
        return data['choices'][0]['message']['content']
    
    except requests.exceptions.Timeout:
        logger.error("API Timeout")
        return "⏳ Waktu permintaan habis, coba lagi nanti"
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}\n{traceback.format_exc()}")
        return "❌ Error tak terduga, coba lagi nanti"

# ===== BOT EVENTS & COMMANDS =====
@bot.event
async def on_ready():
    logger.info(f'Bot {bot.user.name} berhasil login!')
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{PREFIX}ai | DeepSeek"
        )
    )

@bot.command(name='ai')
async def ai_command(ctx, *, prompt: str):
    """Tanya apapun ke DeepSeek AI"""
    # Cek cooldown
    cooldown = check_cooldown(ctx.author.id)
    if cooldown > 0:
        await ctx.reply(f"⏳ Tunggu {cooldown} detik sebelum bertanya lagi", delete_after=5)
        return
    
    # Proses permintaan
    async with ctx.typing():
        # Jeda untuk mengurangi beban CPU
        await asyncio.sleep(1.5)
        
        try:
            response = query_deepseek(prompt)
            
            # Potong jika terlalu panjang
            if len(response) > MAX_RESPONSE_LENGTH:
                response = response[:MAX_RESPONSE_LENGTH] + " [...]"
                
            await ctx.reply(f"🤖 **DeepSeek AI:**\n{response}")
            logger.info(f"Question from {ctx.author}: {prompt[:50]}...")
            
        except Exception as e:
            await ctx.reply(f"🔥 Error: {str(e)}")
            logger.error(f"Command error: {str(e)}")

@bot.command(name='ping')
async def ping_command(ctx):
    """Cek status bot"""
    latency = round(bot.latency * 1000)
    await ctx.reply(f"🏓 Pong! Latensi: `{latency}ms`")

@bot.command(name='help')
async def help_command(ctx):
    """Tampilkan bantuan"""
    help_msg = f"""
**📖 Bantuan Bot DeepSeek**:
`{PREFIX}ai [pertanyaan]` - Tanyakan apapun ke AI
`{PREFIX}ping` - Cek status bot
`{PREFIX}help` - Tampilkan pesan ini

Bot ini menggunakan model **deepseek-chat** dari DeepSeek.
Jeda antar perintah: {COOLDOWN_TIME} detik
    """
    await ctx.reply(help_msg)

# ===== RUN BOT =====
if __name__ == "__main__":
    logger.info("Starting DeepSeek Discord Bot...")
    try:
        bot.run(DISCORD_TOKEN)
    except discord.LoginFailure:
        logger.error("Token Discord tidak valid!")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}\n{traceback.format_exc()}")