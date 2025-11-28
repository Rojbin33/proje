import os
import random
import sqlite3
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv

# .env yükle
load_dotenv()
DISCORD_TOKEN="token"
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
        print("Hata: DISCORD_TOKEN bulunamadı. .env dosyası oluşturup DISCORD_TOKEN=your_token şeklinde ekleyin veya ortam değişkeni ayarlayın.")
        raise SystemExit(1)
# 
# intents ayarları (zorunlu)
intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# DB oluştur ve bağlan
conn = sqlite3.connect("games.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    description TEXT,
    genre TEXT,
    platform TEXT,
    popularity INTEGER DEFAULT 0
)
""")

# 50 oyun listesi
games = [
("Battlefield 1", "I. Dünya Savaşı temalı büyük ölçekli FPS.", "FPS", "PC/PS/Xbox", 5000),
("Battlefield 4", "Modern savaş FPS, araç ve harita çeşitliliği.", "FPS", "PC/PS/Xbox", 7000),
("Battlefield 5", "II. Dünya Savaşı, gerçekçi silah ve araçlar.", "FPS", "PC/PS/Xbox", 6000),
("Battlefield 2042", "Gelecek savaş, devasa haritalar ve araçlar.", "FPS", "PC/PS/Xbox", 5500),
("Call of Duty: Modern Warfare", "Modern çatışmalar, hızlı FPS aksiyonu.", "FPS", "PC/PS/Xbox", 9000),
("Call of Duty: Warzone", "Battle Royale modu ile popüler FPS.", "FPS", "PC/PS/Xbox", 9500),
("Call of Duty: Black Ops Cold War", "Soğuk Savaş döneminde aksiyon FPS.", "FPS", "PC/PS/Xbox", 8000),
("Escape from Tarkov", "Gerçekçi taktiksel shooter, hardcore deneyim.", "FPS", "PC", 4700),
("War Thunder", "Tank, uçak ve gemi savaşları simülasyonu.", "Simülasyon", "PC", 5200),
("World of Tanks", "Tank savaşları, stratejik MMO.", "MMO", "PC", 4800),
("World of Warships", "Gemi savaşları MMO simülasyonu.", "MMO", "PC", 4500),
("BattleBit Remastered", "Low-poly büyük ölçekli savaşlar.", "FPS", "PC", 3600),
("Arma 3", "Gerçekçi askeri simülasyon ve sandbox FPS.", "Simülasyon", "PC", 4200),
("Squad", "Takım tabanlı gerçekçi FPS.", "FPS", "PC", 3800),
("Verdun", "I. Dünya Savaşı FPS.", "FPS", "PC", 2500),
("Hell Let Loose", "II. Dünya Savaşı büyük haritalı FPS.", "FPS", "PC", 3000),
("Post Scriptum", "Tarihi savaş FPS simülasyonu.", "FPS", "PC", 2200),
("Company of Heroes 3", "Strateji tabanlı savaş oyunu.", "Strateji", "PC", 3200),
("Total War: WARHAMMER III", "Strateji ve fantastik savaş.", "Strateji", "PC", 2800),
("Total War: Three Kingdoms", "Stratejik Çin tarihi savaşları.", "Strateji", "PC", 2700),
("Hearts of Iron IV", "II. Dünya Savaşı strateji simülasyonu.", "Strateji", "PC", 3300),
("Men of War: Assault Squad 2", "Gerçekçi taktiksel savaş.", "Strateji", "PC", 2100),
("Company of Heroes 2", "II. Dünya Savaşı stratejik RTS.", "Strateji", "PC", 2600),
("Red Orchestra 2", "Gerçekçi I. ve II. Dünya Savaşı FPS.", "FPS", "PC", 2400),
("Insurgency: Sandstorm", "Modern taktiksel FPS.", "FPS", "PC", 4300),
("Far Cry 6", "Açık dünya savaş ve aksiyon.", "FPS", "PC/PS/Xbox", 5000),
("Tom Clancy's Ghost Recon Breakpoint", "Modern askeri taktik FPS.", "FPS", "PC/PS/Xbox", 4100),
("Tom Clancy's Ghost Recon Wildlands", "Büyük harita açık dünya taktik.", "FPS", "PC/PS/Xbox", 3900),
("Sniper Elite 4", "Taktiksel sniper ve stealth FPS.", "FPS", "PC/PS/Xbox", 3500),
("Sniper Elite 5", "Modern sniper deneyimi, geniş haritalar.", "FPS", "PC/PS/Xbox", 3700),
("Call of Duty: Vanguard", "II. Dünya Savaşı FPS.", "FPS", "PC/PS/Xbox", 4800),
("Call of Duty: Black Ops III", "Fütüristik savaş FPS.", "FPS", "PC/PS/Xbox", 4600),
("Call of Duty: Black Ops II", "Modern ve geçmiş savaş FPS.", "FPS", "PC/PS/Xbox", 4400),
("Medal of Honor: Above and Beyond", "VR destekli II. Dünya Savaşı FPS.", "FPS", "PC/VR", 2000),
("Battlefield: Bad Company 2", "Taktiksel büyük ölçekli FPS.", "FPS", "PC/PS/Xbox", 3500),
("Planetside 2", "Devasa MMO FPS, sürekli savaş.", "MMO", "PC", 4100),
("Warface", "Online FPS, PVP ve PVE.", "FPS", "PC/PS/Xbox", 3000),
("Enlisted", "II. Dünya Savaşı FPS simülasyonu.", "FPS", "PC", 2900),
("Warhammer 40,000: Space Marine", "Taktiksel aksiyon ve savaş.", "FPS", "PC/PS/Xbox", 2500),
("Iron Harvest", "Alternatif tarih strateji oyunu.", "Strateji", "PC", 2300),
("Supreme Commander: Forged Alliance", "Devasa harita strateji savaşı.", "Strateji", "PC", 2100),
("Battle Brothers", "Taktiksel RPG ve savaş simülasyonu.", "Strateji", "PC", 1800),
("Total War: Shogun 2", "Japonya döneminde strateji.", "Strateji", "PC", 2000),
("Total War: Rome II", "Antik Roma strateji oyunu.", "Strateji", "PC", 2200),
("Command & Conquer Remastered", "Klasik RTS savaş oyunu.", "Strateji", "PC", 1900),
("Age of Empires IV", "Tarihi strateji ve savaş.", "Strateji", "PC", 2500),
("Rise of Nations: Extended Edition", "Tarihi strateji ve savaş simülasyonu.", "Strateji", "PC", 1700),
("Commandos 2 HD Remaster", "Taktiksel askeri strateji.", "Strateji", "PC", 1600),
("Company of Heroes", "Klasik II. Dünya Savaşı RTS.", "Strateji", "PC", 2000)
]

for g in games:
    try:
        c.execute("INSERT INTO games (name, description, genre, platform, popularity) VALUES (?,?,?,?,?)", g)
    except:
        pass
conn.commit()

# AI tarzı cevap
def ai_style_reply(game):
    openings = ["Hımm… bunu düşündüm.", "Uzman modumu açtım 😎", "Savaş alanını tarıyorum…"]
    opinions = ["Bu oyun bana göre gerçekten öne çıkıyor çünkü", "Genelde oyuncuların en sevdiği yanı"]
    closings = ["İstersen benzer oyun da önerebilirim.", "Daha fazla detay istersen söyle."]
    
    name, desc, genre, platform, pop = game
    return f"{random.choice(openings)}\n{name} oyununa baktım. {random.choice(opinions)} {desc.lower()}.\nTürü: {genre}\nPlatform: {platform}\nPopülerlik: {pop}\n{random.choice(closings)}"

# !game komutu
@bot.command()
async def game(ctx, *, isim):
    row = c.execute("SELECT name, description, genre, platform, popularity FROM games WHERE LOWER(name)=LOWER(?)", (isim,)).fetchone()
    if not row:
        await ctx.send(f'"{isim}" veritabanında bulunamadı.')
    else:
        await ctx.send(ai_style_reply(row))
        c.execute("UPDATE games SET popularity = popularity + 1 WHERE name = ?", (isim,))
        conn.commit()

# !top komutu
@bot.command()
async def top(ctx, adet: int = 7):
    rows = c.execute("SELECT name, description, genre, platform, popularity FROM games ORDER BY popularity DESC LIMIT ?", (adet,)).fetchall()
    if not rows:
        await ctx.send("Veritabanında oyun yok.")
    else:
        msg = "**En Popüler Oyunlar:**\n"
        for i, r in enumerate(rows):
            msg += f"#{i+1} {r[0]} ({r[4]} oynanma)\n"
        await ctx.send(msg)

print("Bot hazır ✅")
bot.run(DISCORD_TOKEN)
