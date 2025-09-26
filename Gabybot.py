import discord
from gtts import gTTS
from PIL import Image
import random
import os, unidecode
from io import BytesIO
import asyncio
import aiohttp

import nest_asyncio
nest_asyncio.apply()
import json

TOKEN = os.getenv("DISCORD_TOKEN")

with open("clusters_visuels.json", "r", encoding="utf-8") as f:
    clusters = json.load(f)

champions = {'annie': 1, 'olaf': 2, 'galio': 3, 'twisted fate': 4, 'xin zhao': 5, 'urgot': 6, 'leblanc': 7, 'vladimir': 8, 'fiddlesticks': 9, 'kayle': 10, 'master yi': 11, 'alistar': 12, 'ryze': 13, 'sion': 14, 'sivir': 15, 'soraka': 16, 'teemo': 17, 'tristana': 18, 'warwick': 19, 'nunu & willump': 20, 'miss fortune': 21, 'ashe': 22, 'tryndamere': 23, 'jax': 24, 'morgana': 25, 'zilean': 26, 'singed': 27, 'evelynn': 28, 'twitch': 29, 'karthus': 30, "cho'gath": 31, 'amumu': 32, 'rammus': 33, 'anivia': 34, 'shaco': 35, 'dr. mundo': 36, 'sona': 37, 'kassadin': 38, 'irelia': 39, 'janna': 40, 'gangplank': 41, 'corki': 42, 'karma': 43, 'taric': 44, 'veigar': 45, 'trundle': 48, 'swain': 50, 'caitlyn': 51, 'blitzcrank': 53, 'malphite': 54, 'katarina': 55, 'nocturne': 56, 'maokai': 57, 'renekton': 58, 'jarvan iv': 59, 'elise': 60, 'orianna': 61, 'wukong': 62, 'brand': 63, 'lee sin': 64, 'vayne': 67, 'rumble': 68, 'cassiopeia': 69, 'skarner': 72, 'heimerdinger': 74, 'nasus': 75, 'nidalee': 76, 'udyr': 77, 'poppy': 78, 'gragas': 79, 'pantheon': 80, 'ezreal': 81, 'mordekaiser': 82, 'yorick': 83, 'akali': 84, 'kennen': 85, 'garen': 86, 'leona': 89, 'malzahar': 90, 'talon': 91, 'riven': 92, "kog'maw": 96, 'shen': 98, 'lux': 99, 'xerath': 101, 'shyvana': 102, 'ahri': 103, 'graves': 104, 'fizz': 105, 'volibear': 106, 'rengar': 107, 'varus': 110, 'nautilus': 111, 'viktor': 112, 'sejuani': 113, 'fiora': 114, 'ziggs': 115, 'lulu': 117, 'draven': 119, 'hecarim': 120, "kha'zix": 121, 'darius': 122, 'jayce': 126, 'lissandra': 127, 'diana': 131, 'quinn': 133, 'syndra': 134, 'aurelion sol': 136, 'kayn': 141, 'zoe': 142, 'zyra': 143, "kai'sa": 145, 'seraphine': 147, 'gnar': 150, 'zac': 154, 'yasuo': 157, "vel'koz": 161, 'taliyah': 163, 'camille': 164, 'akshan': 166, "bel'veth": 200, 'braum': 201, 'jhin': 202, 'kindred': 203, 'zeri': 221, 'jinx': 222, 'tahm kench': 223, 'briar': 233, 'viego': 234, 'senna': 235, 'lucian': 236, 'zed': 238, 'kled': 240, 'ekko': 245, 'qiyana': 246, 'vi': 254, 'aatrox': 266, 'nami': 267, 'azir': 268, 'yuumi': 350, 'samira': 360, 'thresh': 412, 'illaoi': 420, "rek'sai": 421, 'ivern': 427, 'kalista': 429, 'bard': 432, 'rakan': 497, 'xayah': 498, 'ornn': 516, 'sylas': 517, 'neeko': 518, 'aphelios': 523, 'rell': 526, 'pyke': 555, 'vex': 711, 'yone': 777, 'ambessa': 799, 'mel': 800, 'sett': 875, 'lillia': 876, 'gwen': 887, 'renata glasc': 888, 'aurora': 893, 'nilah': 895, "k'sante": 897, 'smolder': 901, 'milio': 902, 'hwei': 910, 'naafiri': 950}

score = {}

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
parler=False
jeu=False
sol=False
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_cluster_for_skin(skin_id: int, champion: str, clusters: list) -> list:
    for cluster in clusters:
        for skin in cluster:
            if skin["skin_id"] == skin_id and skin["champion"].lower() == champion.lower():
                return cluster
    return []

async def get_random_skin_splash_with_cluster_info(champion_name: str, clusters: list):
    champ_id = champions.get(champion_name.lower())
    if champ_id is None:
        raise ValueError("Champion inconnu ou non mappé.")

    url = f"https://raw.communitydragon.org/15.9/plugins/rcp-be-lol-game-data/global/default/v1/champions/{champ_id}.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Erreur HTTP {resp.status} pour {champion_name}")
            data = await resp.json()

    skins = data.get("skins", [])
    if not skins:
        raise Exception(f"Aucun skin trouvé pour {champion_name}")

    # Choisir un skin aléatoire
    chosen_skin = random.choice(skins)
    skin_id = chosen_skin["id"]

    # Construire l’URL du splashart
    path = chosen_skin.get("uncenteredSplashPath")
    if not path:
        raise Exception("Champ 'uncenteredSplashPath' manquant.")

    trimmed = path.replace("/lol-game-data/assets/ASSETS/", "")
    splash_url = "https://raw.communitydragon.org/15.9/plugins/rcp-be-lol-game-data/global/default/assets/" + trimmed.lower()

    # Récupérer les champions du même cluster
    cluster = find_cluster_for_skin(skin_id, champion_name, clusters)
    related_champions = list(set(s["champion"].lower() for s in cluster))

    return {
        "splash_url": splash_url,
        "related_champions": related_champions
    }


@client.event
async def on_message(message):
    global parler,jeu,champ,img,soluce

    if message.author.bot:
        return
    
    
    m=message.content.lower()
    if " tg " in (" " + m + " "):
        await message.channel.send("fdp")
        return

    if message.content == "!reset":
        score.clear()
        await message.channel.send("Score réinitialisé !")
        return
    
    if message.content == "!scores":
        if not score:
            await message.channel.send("Aucun score enregistré.")
            return
        scores_message = "Scores actuels :\n"
        for name, points in score.items():
            scores_message += f"{name}: {points} points\n"
        await message.channel.send(scores_message)
        return

    if message.content == "!jeu" and message.channel.name=="jeu-image" and not jeu:
        jeu=True
        sol=False
        champ = random.choice(list(champions.keys()))
        infos = await get_random_skin_splash_with_cluster_info(champ, clusters)
        print(infos["splash_url"])
        soluce = infos["related_champions"]

        async with aiohttp.ClientSession() as session:
            async with session.get(infos["splash_url"]) as resp:
                if resp.status != 200:
                    return None
                content = await resp.read()
                img = Image.open(BytesIO(content))
        
        for k in reversed(range(1, 12)):
            imgSmall = img.resize((int(1215 / (k * k)), int(717 / (k * k))), resample=Image.Resampling.BILINEAR)
            result = imgSmall.resize(img.size, Image.Resampling.NEAREST)

            with BytesIO() as image_binary:
                if not jeu:
                    break
                result.save(image_binary, 'PNG')
                image_binary.seek(0)
                if not jeu:
                    break
                await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
                if not jeu:
                    break
                await asyncio.sleep(5)
                if not jeu:
                    break



    if jeu:
        if unidecode.unidecode(message.content.lower()) in soluce:
            jeu=False
            sol=True
            messages_construire = ""
            for champ in soluce:
                messages_construire += champ + ", "
            messages_construire = messages_construire[:-2]
            print(messages_construire)
            await message.channel.send("Bien joué tu as trouvé " + message.author.mention + " c'etait " + messages_construire)
            
            name = message.author.name
            if name in score:
                score[name] += 1
            else:
                score[name] = 1

            await message.channel.send("Tu as  " + str(score[name]) + " points !")

            imgSmall = img.resize((int(1215 / 3), int(717 / 3)), resample=Image.Resampling.BILINEAR)
            result = imgSmall.resize(img.size, Image.Resampling.NEAREST)
            with BytesIO() as image_binary:
                result.save(image_binary, 'PNG')
                image_binary.seek(0)
                await message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))
            
            
            return




client.run(TOKEN)