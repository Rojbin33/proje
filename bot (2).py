import os
import random
import sqlite3
import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from discord.ui import View, Button, Modal, TextInput

load_dotenv()
DISCORD_TOKEN = ""

intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------ VERİTABANI ------------------

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

c.execute("""
CREATE TABLE IF NOT EXISTS steam (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    steam_ad TEXT UNIQUE,
    aciklama TEXT
)
""")

conn.commit()

# ------------------ YAPAY ZEKA TARZI CEVAP ------------------

def ai_style_reply(game):
    openings = ["Hımm… bunu düşündüm.", "Uzman modumu açtım 😎", "Savaş alanını tarıyorum…"]
    opinions = ["Bu oyun öne çıkıyor çünkü", "Oyuncuların en sevdiği yanı"]
    closings = ["İstersen benzer oyun da önerebilirim.", "Daha fazla detay istersen söyle."]

    name, desc, genre, platform, pop = game
    return (
        f"{random.choice(openings)}\n"
        f"{name} oyununa baktım. {random.choice(opinions)} {desc.lower()}.\n"
        f"Türü: {genre}\n"
        f"Platform: {platform}\n"
        f"Popülerlik: {pop}\n"
        f"{random.choice(closings)}"
    )

# ------------------ KOMUTLAR ------------------

@bot.command()
async def game(ctx, *, isim):
    row = c.execute(
        "SELECT name, description, genre, platform, popularity FROM games WHERE LOWER(name)=LOWER(?)",
        (isim,)
    ).fetchone()
    if not row:
        await ctx.send(f'"{isim}" bulunamadı.')
        return

    await ctx.send(ai_style_reply(row))
    c.execute("UPDATE games SET popularity = popularity + 1 WHERE name = ?", (isim,))
    conn.commit()

@bot.command()
async def top(ctx, adet: int = 7):
    rows = c.execute(
        "SELECT name, description, genre, platform, popularity FROM games ORDER BY popularity DESC LIMIT ?",
        (adet,)
    ).fetchall()
    if not rows:
        await ctx.send("Veritabanında oyun yok.")
        return

    msg = "**En Popüler Oyunlar:**\n"
    for i, r in enumerate(rows):
        msg += f"#{i+1} {r[0]} ({r[4]} oynanma)\n"
    await ctx.send(msg)

@bot.command()
async def ara(ctx, *, kelime):
    kelime = f"%{kelime.lower()}%"
    rows = c.execute("SELECT name FROM games WHERE LOWER(name) LIKE ?", (kelime,)).fetchall()
    if not rows:
        await ctx.send("Benzer oyun bulunamadı.")
        return

    msg = "**Bulunan Oyunlar:**\n" + "\n".join([r[0] for r in rows])
    await ctx.send(msg)

@bot.command()
async def rastgele(ctx):
    row = c.execute(
        "SELECT name, description, genre, platform, popularity FROM games ORDER BY RANDOM() LIMIT 1"
    ).fetchone()
    if not row:
        await ctx.send("Veritabanında oyun yok.")
        return

    await ctx.send(ai_style_reply(row))

@bot.command()
async def bilgi(ctx):
    await ctx.send("🔥 GameFinder Bot v5.0\nKomutlar: !game, !top, !ara, !rastgele, !menu, !hesabımı_ekle")

# ------------------ MODAL (FORM) ------------------

class AddGameModal(Modal, title="Yeni Oyun Ekle"):
    isim = TextInput(label="Oyun Adı", placeholder="Örn: Valorant")
    genre = TextInput(label="Türü", placeholder="FPS, RPG, Strateji...")
    platform = TextInput(label="Platform", placeholder="PC, PS, Xbox...")
    description = TextInput(label="Açıklama", style=discord.TextStyle.long, placeholder="Oyun açıklaması...")

    async def on_submit(self, interaction: discord.Interaction):
        try:
            c.execute(
                "INSERT INTO games (name, description, genre, platform) VALUES (?,?,?,?)",
                (self.isim.value, self.description.value, self.genre.value, self.platform.value),
            )
            conn.commit()
            await interaction.response.send_message(f"✔ Oyun eklendi: **{self.isim.value}**", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Bu oyun zaten var veya hata oluştu.", ephemeral=True)

# ------------------ STEAM HESAP EKLE ------------------

@bot.command()
@commands.has_permissions(administrator=True)  # Yalnızca adminler kullanabilir
async def hesabımı_ekle(ctx, steam_ad, *, aciklama="Açıklama yok"):
    try:
        c.execute(
            "INSERT INTO steam (steam_ad, aciklama) VALUES (?, ?)",
            (steam_ad, aciklama)
        )
        conn.commit()
        await ctx.send(f"✔ Yeni hesap eklendi: **{steam_ad}**")
    except sqlite3.IntegrityError:
        await ctx.send("❌ Bu hesap zaten var.")
    except Exception as e:
        await ctx.send(f"❌ Hata oluştu: {e}")
@bot.command()
async def hesap_gor(ctx):
    try:
        c.execute("SELECT steam_ad, aciklama FROM steam")
        rows = c.fetchall()

        if not rows:
            await ctx.send("📭 Henüz hiç hesap eklenmemiş.")
            return

        embed = discord.Embed(
            title="👤 Eklenen Steam Hesapları",
            color=0x00ffcc
        )

        for steam_ad, aciklama in rows:
            embed.add_field(
                name=steam_ad,
                value=aciklama if aciklama else "Açıklama yok",
                inline=False
            )

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"❌ Hesapları çekerken hata oldu: {e}")

# ------------------ BUTTON MENU ------------------

class MenuButtons(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🎮 Rastgele Oyun", style=discord.ButtonStyle.green, custom_id="random_game"))
        self.add_item(Button(label="🔥 Popülerler", style=discord.ButtonStyle.blurple, custom_id="top_games"))
        self.add_item(Button(label="🔎 Oyun Arama", style=discord.ButtonStyle.gray, custom_id="search_game"))
        self.add_item(Button(label="➕ Oyun Ekle", style=discord.ButtonStyle.success, custom_id="add_game"))
        self.add_item(Button(label="ℹ️ Bilgi", style=discord.ButtonStyle.red, custom_id="bot_info"))
        # Yeni eklenenler:
        self.add_item(Button(label="➕ Hesap Ekle", style=discord.ButtonStyle.green, custom_id="add_account"))
        self.add_item(Button(label="👤 Hesap Gör", style=discord.ButtonStyle.blurple, custom_id="view_account"))

@bot.command()
async def menu(ctx):
    embed = discord.Embed(
        title="🎛️ Oyun ve Hesap Menüsü",
        description=(
            "Aşağıdaki butonlardan birini seç:\n\n"
            "🎮 Rastgele Oyun → Rastgele oyun önerisi\n"
            "🔥 Popülerler → En popüler oyunlar\n"
            "🔎 Oyun Arama → Oyun ara\n"
            "➕ Oyun Ekle → Yeni oyun ekle\n"
            "ℹ️ Bilgi → Bot hakkında bilgi\n"
            "➕ Hesap Ekle → Yeni Steam hesabı ekle\n"
            "👤 Hesap Gör → Eklenen hesapları listele"
        ),
        color=0x00ffcc
    )
    await ctx.send(embed=embed, view=MenuButtons())

# ------------------ INTERACTION HANDLER ------------------

@bot.event
async def on_interaction(interaction):
    cid = interaction.data.get("custom_id")

    if cid == "random_game":
        row = c.execute("SELECT name, description, genre, platform, popularity FROM games ORDER BY RANDOM() LIMIT 1").fetchone()
        await interaction.response.send_message(ai_style_reply(row), ephemeral=True)

    elif cid == "top_games":
        rows = c.execute("SELECT name, popularity FROM games ORDER BY popularity DESC LIMIT 5").fetchall()
        msg = "**🔥 En Popüler 5 Oyun:**\n"
        for i, r in enumerate(rows):
            msg += f"#{i+1} {r[0]} — {r[1]} görüntüleme\n"
        await interaction.response.send_message(msg, ephemeral=True)

    elif cid == "search_game":
        await interaction.response.send_message("🔎 Aramak için `!ara oyun_adı` yaz.", ephemeral=True)

    elif cid == "add_game":
        await interaction.response.send_modal(AddGameModal())

    elif cid == "bot_info":
        await interaction.response.send_message("🤖 GameFinder v5.0 | Menü + Form + Steam sistemi aktif!", ephemeral=True)

print("Bot Hazır!")
bot.run(DISCORD_TOKEN)