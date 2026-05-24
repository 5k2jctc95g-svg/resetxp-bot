import discord
from discord.ext import commands
from discord import option
from openai import OpenAI
from dotenv import load_dotenv
from discord.ext import tasks
import os
import json
import time
import random
import datetime
import requests
import base64

# Charger variables .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
RENDER_API_KEY = os.getenv("RENDER_API_KEY")

# Client OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Permissions Discord
intents = discord.Intents.default()
intents.message_content = True

# Création bot
bot = discord.Bot(intents=intents)
cooldowns = {}
CHANNEL_ID = 1508142974716870737

challenges = [
    "20 squats",
    "15 pompes",
    "10 minutes de cardio",
    "5 minutes de gainage",
    "30 jumping jacks",
    "15 minutes de marche",
    "10 minutes de corde à sauter"
]

# Base données
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "users.json")

# Charger données
def load_data():

    try:

        with open(DATA_FILE, "r") as f:

            return json.load(f)

    except Exception as e:

        print(f"ERREUR JSON : {e}")

        backup_file = os.path.join(
            os.path.dirname(__file__),
            "users_backup.json"
        )

        try:

            with open(backup_file, "r") as f:

                print("✅ Backup chargé")

                data = json.load(f)

                with open(DATA_FILE, "w") as repaired_file:

                    json.dump(data, repaired_file, indent=4)

                print("✅ users.json réparé")
                
                return data

        except:

            print("❌ Aucun backup valide")

            return {}

# Sauvegarder données
def save_data(data):

    # Sauvegarde principale
    with open(DATA_FILE, "w") as f:

        json.dump(data, f, indent=4)

    # Backup automatique
    backup_file = os.path.join(
        os.path.dirname(__file__),
        "users_backup.json"
    )

    with open(backup_file, "w") as f:

        json.dump(data, f, indent=4)

# Créer utilisateur
def create_user(user_id):

    data = load_data()

    if str(user_id) not in data:

        data[str(user_id)] = {
            "xp": 0,
            "pv": 100,
            "level": 1,
            "challenge": None,
            "weights": [],
            "last_gym": None,
            "gym_sessions": 0
        }

        save_data(data)

    else:

        updated = False

        if "challenge" not in data[str(user_id)]:

            data[str(user_id)]["challenge"] = None
            updated = True
        
        if "weights" not in data[str(user_id)]:

            data[str(user_id)]["weights"] = []
            updated = True

        if "last_gym" not in data[str(user_id)]:

            data[str(user_id)]["last_gym"] = None

            updated = True

        if "gym_sessions" not in data[str(user_id)]:

            data[str(user_id)]["gym_sessions"] = 0

            updated = True

        if updated:

            save_data(data)

def get_user(user_id):

    create_user(user_id)

    data = load_data()

    return data, data[str(user_id)]


# Ajouter XP
def add_xp(user, amount):

    print(f"AJOUT XP -> {amount}")

    user["xp"] += amount

    xp = user["xp"]

    old_level = user["level"]

    level = int((xp / 50) ** 0.5) + 1

    user["level"] = level

    if level > old_level:

        print(f"🎉 Niveau {level} atteint !")

# Modifier PV
def add_pv(user, amount):

    user["pv"] += amount

    if user["pv"] > 100:
        user["pv"] = 100

    if user["pv"] < 0:
        user["pv"] = 0

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

    await ctx.defer()

    data, user = get_user(ctx.author.id)

    # Création embed
    print(data)
    print(user)
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
    await ctx.followup.send(embed=embed)
# Repas healthy
@bot.command()
async def healthymeal(ctx):

    data, user = get_user(ctx.author.id)

    add_xp(user, 15)

    save_data(data)


# Analyse image
@bot.slash_command(
    name="analyze",
    description="Analyser un repas"
)
async def analyze(ctx, image: discord.Attachment):

    user_id = str(ctx.author.id)
    current_time = time.time()

    if user_id in cooldowns:

        last_use = cooldowns[user_id]

        if current_time - last_use < 30:

            remaining = int(30 - (current_time - last_use))

            await ctx.send(
                f"⏳ Attends encore {remaining}s avant une nouvelle analyse."
            )

            return

    cooldowns[user_id] = current_time

    # Vérifier image
    
    # Vérifier état joueur

    # Vérifier état joueur
    create_user(ctx.author.id)

    data = load_data()

    user = data[str(ctx.author.id)]

    if user["pv"] <= 0:

        await ctx.send(
            "☠️ Tu es KO.\nUtilise /challenge pour recevoir un défi sportif."
        )

        return

    await ctx.defer()
        

    try:

        # URL image
        image_url = image.url

        
        
        cooldowns[user_id] = current_time

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
    Tu es un juge nutrition RPG brutal et réaliste.

    Tu analyses UNIQUEMENT la nourriture visible sur l'image.

    IMPORTANT :

    Un fast-food, burger, tacos, friture, nuggets, soda, nourriture grasse ou ultra transformée est MAUVAIS pour la santé.

    RÈGLES STRICTES :

    - Un fast-food doit TOUJOURS avoir des PV négatifs.
    - Un fast-food doit souvent faire perdre de l'XP.
    - Un fast-food ne peut JAMAIS dépasser 10 XP.
    - Plus la nourriture semble grasse, frite ou industrielle, plus les PV doivent être négatifs.
    - Les aliments healthy donnent beaucoup de XP et PV.
    - Les légumes, fruits, protéines propres et repas équilibrés sont récompensés.
    - Tu dois être sévère avec la junk food.
    - La malbouffe doit faire régresser le joueur.
    - Tu ne dois PAS encourager la malbouffe.
    - Si l'image montre principalement de la junk food, donne un mauvais score.

    EXEMPLES OBLIGATOIRES :

    Burger/frites/nuggets :
    XP entre -80 et 10
    PV entre -120 et -20

    Salade/repas healthy :
    XP entre 70 et 100
    PV entre 20 et 50

    Réponds EXACTEMENT dans ce format :

    XP: nombre
    PV: nombre
    MESSAGE: analyse RPG immersive
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

                    xp_text = line.replace("XP:", "").strip()
                    xp_text = xp_text.replace("+", "")
                    xp_text = xp_text.replace("XP", "")

                    xp_gain = int(xp_text)

                elif line.startswith("PV:"):

                    pv_text = line.replace("PV:", "").strip()
                    pv_text = pv_text.replace("+", "")
                    pv_text = pv_text.replace("PV", "")

                    pv_change = int(pv_text)

                elif line.startswith("MESSAGE:"):

                    message = line.replace(
                        "MESSAGE:",
                        ""
                    ).strip()
                        
        # Ajouter XP/PV
        data, user = get_user(ctx.author.id)

        add_xp(user, xp_gain)
        print("XP AJOUTÉ")

        add_pv(user, pv_change)
        print("PV AJOUTÉ")

        save_data(data)
        
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

        await ctx.followup.send(embed=embed)

    except Exception as e:

        print(f"Erreur : {e}")


# Lancer bot
@bot.event
async def on_ready():

    print(f"✅ {bot.user} connecté")

    weekly_weight_reminder.start()

@bot.slash_command()
async def leaderboard(ctx):

    data = load_data()

    sorted_users = sorted(
        data.items(),
        key=lambda x: x[1]["xp"],
        reverse=True
    )

    leaderboard_text = ""

    for i, (user_id, user_data) in enumerate(sorted_users[:10], start=1):

        xp = user_data["xp"]

        leaderboard_text += (
            f"{i}. <@{user_id}> — {xp} XP\n"
        )

    embed = discord.Embed(
        title="🏆 Leaderboard",
        description=leaderboard_text,
        color=discord.Color.gold()
    )

    await ctx.respond(embed=embed)

@bot.slash_command()
async def challenge(ctx):

    data, user = get_user(ctx.author.id)

    if user["pv"] > 0:

        await ctx.respond(
            "💪 Tu n'es pas KO.\nLes défis sportifs sont réservés aux joueurs à 0 PV."
        )

        return

    if data[str(ctx.author.id)]["challenge"] is None:

        data[str(ctx.author.id)]["challenge"] = random.choice(challenges)

        save_data(data)

    challenge = data[str(ctx.author.id)]["challenge"]

    embed = discord.Embed(
        title="🏃 Défi Sportif",
        description=(
            f"☠️ Tu es KO.\n\n"
            f"🎯 Défi : **{challenge}**\n\n"
            f"📸 Utilise bientôt `/proof` pour envoyer ta preuve."
        ),
        color=discord.Color.red()
    )

    await ctx.respond(embed=embed)

@bot.slash_command()
async def proof(ctx, image: discord.Attachment):

    data, user = get_user(ctx.author.id)

    if user["challenge"] is None:

        await ctx.respond(
            "❌ Tu n'as aucun défi actif."
        )

        return

    await ctx.defer()

    try:

        image_url = image.url

        challenge = user["challenge"]

        response = client.responses.create(
            model="gpt-4.1-mini",

            input=[{
                "role": "user",
                "content": [

                    {
                        "type": "input_text",
                        "text": f"""

Tu es un système de validation de défi sportif
pour un RPG motivation/santé.

Le but est d'encourager le joueur,
pas d'être ultra strict.

Tu dois vérifier si la photo semble être
une preuve PLAUSIBLE que le joueur
a probablement réalisé son défi.

Le joueur n'a PAS besoin d'être photographié
pendant l'exercice exact.

Tu peux accepter :
- selfie après effort
- environnement extérieur
- salle de sport
- tapis de course
- équipement de sport
- baskets dehors
- montre connectée
- transpiration
- environnement cohérent avec le défi
- preuve crédible et logique

Une simple photo cohérente après le sport
peut être acceptée.

Tu ne dois PAS exiger :
- exercice visible
- transpiration visible
- matériel visible
- effort évident

Le but est d'encourager le joueur,
pas de faire une enquête policière.

Tu dois refuser :
- memes
- nourriture
- images absurdes
- dessins
- animaux
- photos sans rapport
- images internet évidentes
- captures d'écran absurdes

Le joueur affirme avoir réalisé une activité sportive.

La photo n'a PAS besoin de prouver
le défi exact.

Tu dois simplement vérifier si :
- la photo semble honnête
- sportive
- cohérente
- crédible

Une simple preuve lifestyle/sport suffit.

Si la preuve semble raisonnablement crédible :
réponds VALID

Sinon :
réponds INVALID

Donne un score de crédibilité de 0 à 100.

0 = totalement faux ou sans rapport
100 = preuve très crédible

Réponds EXACTEMENT sous ce format :

SCORE: nombre
MESSAGE: courte explication
"""
                    },

                    {
                        "type": "input_image",
                        "image_url": image_url
                    }

                ]
            }]
        )

        result = response.output_text.strip()

        print(result)

        score = 0

        lines = result.split("\n")

        for line in lines:

            if line.startswith("SCORE:"):

                try:

                    score = int(
                        line.replace("SCORE:", "").strip()
                    )

                except:

                    score = 0

        if score >= 60:

            data[str(ctx.author.id)]["pv"] = 50

            data[str(ctx.author.id)]["xp"] += 50

            data[str(ctx.author.id)]["challenge"] = None

            save_data(data)

            embed = discord.Embed(
                title="✅ Défi validé",
                description=(
                    "🔥 Preuve acceptée.\n\n"
                    "❤️ +50 PV\n"
                    "⭐ +50 XP\n\n"
                    "Tu peux repartir à l'aventure."
                ),
                color=discord.Color.green()
            )

            await ctx.followup.send(embed=embed)

        else:

            await ctx.followup.send(
                "❌ Preuve refusée.\nLe défi ne semble pas réalisé."
            )

    except Exception as e:

        print(f"Erreur proof : {e}")

@bot.slash_command(
    name="weight",
    description="Enregistrer ton poids"
)
async def weight(ctx, poids: float):

    data, user = get_user(ctx.author.id)

    today = str(datetime.date.today())

    # Ajouter historique
    for entry in user["weights"]:

        if entry["date"] == today:

            await ctx.respond(
                "⚠️ Tu as déjà enregistré ton poids aujourd'hui."
            )

            return

    user["weights"].append({
        "date": today,
        "weight": poids
    })

    save_data(data)

    difference_text = "Première pesée enregistrée."

    # Comparaison semaine précédente
    if len(user["weights"]) >= 2:

        old_weight = user["weights"][-2]["weight"]

        diff = round(poids - old_weight, 1)

        if diff < 0:

            difference_text = f"📉 {abs(diff)} kg depuis la dernière pesée"

        elif diff > 0:

            difference_text = f"📈 +{diff} kg depuis la dernière pesée"

        else:

            difference_text = "⚖️ Poids stable"

    embed = discord.Embed(
        title="⚖️ Pesée enregistrée",
        description=(
            f"Poids actuel : {poids} kg\n\n"
            f"{difference_text}"
        ),
        color=discord.Color.blue()
    )

    await ctx.respond(embed=embed)

@tasks.loop(minutes=1)
async def weekly_weight_reminder():

    now = datetime.datetime.now()

    # Dimanche = 6
    if now.weekday() == 6 and now.hour == 9 and now.minute == 0:

        channel = bot.get_channel(CHANNEL_ID)

        if channel:

            embed = discord.Embed(
                title="⚖️ Pesée Hebdomadaire",
                description=(
                    "🔥 Il est temps de faire votre pesée !\n\n"
                    "Utilisez : `/weight votre_poids`\n\n"
                    "📉 Comparez votre progression avec la semaine dernière."
                ),
                color=discord.Color.blue()
            )

            await channel.send(embed=embed)

@bot.slash_command(
    name="renderstatus",
    description="Voir le statut du serveur Render"
)
async def renderstatus(ctx):

    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}"
    }

    response = requests.get(
        "https://api.render.com/v1/services",
        headers=headers
    )

    if response.status_code != 200:

        await ctx.respond("❌ Impossible de contacter Render.")
        return

    services = response.json()

    if not services:

        await ctx.respond("❌ Aucun service trouvé.")
        return

    service = services[0]
    print(service)

    name = service.get("service", {}).get("name", "Inconnu")

    suspended = service.get("suspended")

    status_text = "🟢 Online"

    if suspended == True:
        status_text = "🔴 Offline"

    embed = discord.Embed(
        title="📡 Render Status",
        color=discord.Color.green()
    )

    embed.add_field(
        name="Service",
        value=name,
        inline=False
    )

    embed.add_field(
        name="Statut",
        value=status_text,
        inline=False
    )

    embed.set_footer(
        text="ResetXP Monitoring"
    )

    await ctx.respond(embed=embed)

@bot.slash_command(
    name="gymproof",
    description="Valider une séance de salle"
)
async def gymproof(
    ctx,
    image: discord.Attachment
):

    data, user = get_user(ctx.author.id)

    today = str(datetime.date.today())

    # Anti spam journalier
    if user["last_gym"] == today:

        await ctx.respond(
            "⚠️ Tu as déjà validé une séance aujourd'hui."
        )

        return

    await ctx.defer()

    image_bytes = await image.read()

    response = client.chat.completions.create(

        model="gpt-4o-mini",

        messages=[

            {
                "role": "system",
                "content": (
                    "Tu analyses des preuves de salle de sport.\n"
                    "Réponds STRICTEMENT sous ce format :\n\n"
                    "SCORE: nombre entre 0 et 100\n"
                    "MESSAGE: courte explication\n\n"
                    "Une vraie salle : machines, haltères, tapis, vestiaire, logo salle, environnement fitness.\n"
                    "Un selfie seul ou une photo floue = score faible."
                )
            },

            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyse cette preuve de salle."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
                        }
                    }
                ]
            }
        ]
    )

    result = response.choices[0].message.content

    score = 0
    message = "Analyse impossible."

    for line in result.splitlines():

        if line.startswith("SCORE:"):

            try:

                score = int(
                    line.replace("SCORE:", "").strip()
                )

            except:

                score = 0

        if line.startswith("MESSAGE:"):

            message = line.replace(
                "MESSAGE:",
                ""
            ).strip()

    if score >= 50:

        xp_gain = 25

        user["xp"] += xp_gain

        user["last_gym"] = today

        user["gym_sessions"] += 1

        save_data(data)

        embed = discord.Embed(
            title="🏋️ Séance validée !",
            description=(
                f"🔥 +{xp_gain} XP\n\n"
                f"{message}"
            ),
            color=discord.Color.green()
        )

    else:

        embed = discord.Embed(
            title="❌ Séance refusée",
            description=message,
            color=discord.Color.red()
        )

    await ctx.followup.send(embed=embed)

bot.run(DISCORD_TOKEN)