import discord
from discord.ext import commands
from discord import option
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Charger variables .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Permissions Discord
intents = discord.Intents.default()
intents.message_content = True

# Création bot
bot = commands.Bot(command_prefix="/", intents=intents)

# Base données
DATA_FILE = "users.json"

# Charger données
def load_data():
    try:
        with open("users.json", "r") as f:
            content = f.read().strip()

            if not content:
                return {}

            return json.loads(content)

    except:
        return {}

# Sauvegarder données
def save_data(data):

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Créer utilisateur
def create_user(user_id):

    data = load_data()

    if str(user_id) not in data:

        data[str(user_id)] = {
            "xp": 0,
            "level": 1,
            "pv": 100
        }

    save_data(data)

# Ajouter XP
def add_xp(user_id, amount):

    create_user(user_id)

    data = load_data()

    data[str(user_id)]["xp"] += amount

    xp = data[str(user_id)]["xp"]

    level = xp // 100 + 1

    data[str(user_id)]["level"] = level

    save_data(data)

# Modifier PV
def add_pv(user_id, amount):

    create_user(user_id)

    data = load_data()

    data[str(user_id)]["pv"] += amount

    save_data(data)

# Bot connecté
@bot.event
async def on_ready():

    print(f"✅ Connecté comme {bot.user}")

# Profil
@bot.slash_command(
    name="profile",
    description="Afficher ton profil"
)
async def profile(ctx):

    create_user(ctx.author.id)

    data = load_data()

    if str(ctx.author.id) not in data:

        data[str(ctx.author.id)] = {
            "xp": 0,
            "pv": 100,
            "level": 1
        }

        save_data(data)

    user = data[str(ctx.author.id)]

    # Création embed
    embed = discord.Embed(
        title=f"⚔️ Profil de {ctx.author.name}",
        color=discord.Color.green()
    )

    embed.add_field(
        name="❤️ PV",
        value=user["pv"],
        inline=True
    )

    embed.add_field(
        name="⭐ XP",
        value=user["xp"],
        inline=True
    )

    embed.add_field(
        name="🏆 Niveau",
        value=user["level"],
        inline=True
    )

    embed.set_footer(
        text="ResetXP • Mange. Progresse. Devient légendaire."
    )


# Repas healthy
@bot.command()
async def healthymeal(ctx):

    add_xp(ctx.author.id, 15)


# Analyse image
@bot.slash_command(
    name="analyze",
    description="Analyser un repas"
)
async def analyze(ctx, image: discord.Attachment):

    await ctx.response.defer()
    # Vérifier image
    

    try:

        # URL image
        image_url = image.url

        
        
       

        # OpenAI
          # OpenAI

        response = client.responses.create(
            model="gpt-4.1-mini",

            input=[{
                "role": "user",
                "content": [

                    {
                        "type": "input_text",
                        "text": """
Analyse ce repas comme un système RPG nutrition.

IMPORTANT :
Tu dois répondre EXACTEMENT dans ce format :

XP: nombre
PV: nombre
MESSAGE: ton analyse fun
"""
                    },

                    {
                        "type": "input_image",
                        "image_url": image_url
                    }

                ]
            }]
        )

       
        result = response.output_text
        print(result)
        xp_gain = 0
        pv_change = 0
        message = "Analyse terminée."

        lines = result.split("\n")

        if "XP:" not in result or "PV:" not in result:
            await ctx.respond("❌ Réponse IA invalide")

        else:
            for line in lines:

            if line.startswith("XP:"):

                xp_gain = int(
                    line.replace("XP:", "").strip()
                )

            elif line.startswith("PV:"):

                pv_change = int(
                    line.replace("PV:", "").strip()
                )

            elif line.startswith("MESSAGE:"):

                message = line.replace(
                    "MESSAGE:",
                    ""
                ).strip()

        # Ajouter XP/PV
        add_xp(ctx.author.id, xp_gain)
        add_pv(ctx.author.id, pv_change)

        # Embed
        embed = discord.Embed(

            title="🎮 Analyse Nutrition",
            description=message,
            color=discord.Color.green()

        )

        embed.add_field(
            name="⭐ XP gagnés",
            value=xp_gain,
            inline=True
        )

        embed.add_field(
            name="❤️ PV",
            value=pv_change,
            inline=True
        )

        embed.set_footer(
            text="ResetXP • Nutrition RPG"
        )

        await ctx.respond(embed=embed)

    except Exception as e:

        print(f"Erreur : {e}")


# Lancer bot
@bot.event
async def on_ready():

    print(f"✅ {bot.user} connecté")

bot.remove_command("profile")

bot.run(DISCORD_TOKEN)