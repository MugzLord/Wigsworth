import os
import random
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN env var not set")

# 👉 REPLACE THIS via Railway env var OREO_ID
OREO_ID = int(os.getenv("OREO_ID", "0"))
if OREO_ID == 0:
    print("WARNING: OREO_ID not set or invalid. Bot will not know who Oreo is.")

# Chance to answer normal mentions
RESPONSE_CHANCE = float(os.getenv("RESPONSE_CHANCE", "0.7"))
# Chance to answer when Oreo himself talks
SELF_RESPONSE_CHANCE = float(os.getenv("SELF_RESPONSE_CHANCE", "0.3"))

TRIGGER_WORDS = ("oreo", "ore0", "oreoooo")  # add any spellings you like

# How often the bot should respond (0.0 = never, 1.0 = always)
RESPONSE_CHANCE = 0.7

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# How often the bot should reply when Oreo himself talks (0.0–1.0)
SELF_RESPONSE_CHANCE = 0.3  # 30%, adjust as you like

SELF_LINES = [
    "Relax, Oreo, the court still sides with you.",
    "Easy there, Oreo, you’re already the main case on the docket.",
    "Steady, Oreo. Your legal team has everything under control.",
    "Oreo, consider this a formal reminder that you’re legally unbothered.",
    "Client Oreo, please remain calm; the defence is airtight.",
    "Oreo, you are advised to ignore all haters on legal grounds.",
    "Counsel to Oreo: you’re still winning this case by a wide margin.",
    "Oreo, your only crime is existing too loudly in this server.",
    "Official notice to Oreo: you are cleared of all alleged nonsense.",
    "Oreo, on behalf of your defence, you may continue being dramatic.",
]


# --------------- DEFAULT LINES (fallback) ---------------

DEFAULT_DEFENCE_LINES = [
    "Oi, leave Oreo alone — man’s already hanging on by a prayer and a half-charged phone.",
    "Before you speak on Oreo, please remember he’s on someone’s prayer request list.",
    "Objection! My client Oreo is guilty only of being adorable and mildly inconvenient.",
    "Stop slandering Oreo — he’s fragile. He bruises like a Tesco peach.",
    "Let’s not attack Oreo today, he woke up with 2% battery and zero emotional stability.",
    "God forgives everything… except the slander you lot throw at Oreo.",
    "Your Honour, the hate towards Oreo is outrageous, biased, and honestly a bit jealous.",
    "Don’t bully Oreo. He cries in 1080p HD with immersive surround sound.",
    "Even when Oreo is wrong, he’s right. That’s the rule. I don’t make them, I just enforce them.",
    "Not too loud please — Oreo is sensitive, like Wi-Fi in a storm.",
]

DEFAULT_REPLY_LINES = [
    "Arguing with a bot about Oreo? Yeah, you’re in too deep.",
    "You’re replying to me instead of apologising to Oreo, interesting.",
    "Imagine backchatting Oreo’s lawyer bot. Extremely brave.",
    "I see you replying — just say you love Oreo and go.",
]

# These will be filled from JSON (or fall back to defaults)
DEFENCE_LINES: list[str] = []
REPLY_LINES: list[str] = []


def load_banter():
    """
    Load defence_lines and reply_lines from banter.json.
    If file missing or broken, use defaults.
    """
    global DEFENCE_LINES, REPLY_LINES

    try:
        with open("banter.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        defence = data.get("defence_lines", [])
        reply = data.get("reply_lines", [])

        # Use JSON values if present, otherwise fallback
        DEFENCE_LINES = defence if defence else DEFAULT_DEFENCE_LINES
        REPLY_LINES = reply if reply else DEFAULT_REPLY_LINES

        print(f"[BANTER] Loaded {len(DEFENCE_LINES)} defence lines and {len(REPLY_LINES)} reply lines from banter.json")

    except FileNotFoundError:
        print("[BANTER] banter.json not found, using default lines.")
        DEFENCE_LINES = DEFAULT_DEFENCE_LINES
        REPLY_LINES = DEFAULT_REPLY_LINES
    except Exception as e:
        print(f"[BANTER] Error loading banter.json: {e}")
        DEFENCE_LINES = DEFAULT_DEFENCE_LINES
        REPLY_LINES = DEFAULT_REPLY_LINES


# --------------- EVENTS ---------------

@bot.event
async def on_ready():
    load_banter()
    print(f"Logged in as {bot.user} (Oreo Defence Bot active)")


TRIGGER_WORDS = ("oroe", "oreo")  # words that trigger defence

TRIGGER_WORDS = tuple(w.lower() for w in TRIGGER_WORDS)

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.lower()

    # 0) Is this Oreo himself speaking?
    is_oreo = (OREO_ID != 0 and message.author.id == OREO_ID)

    # 1) Did someone tag Oreo?
    mentioned_oreo = any(user.id == OREO_ID for user in message.mentions) if OREO_ID != 0 else False

    # 2) Did they say “oreo” (or any word in TRIGGER_WORDS)?
    said_trigger_word = any(w in content for w in TRIGGER_WORDS)

    # 3) Are they replying to the defence message?
    replying_to_bot = False
    if message.reference and isinstance(message.reference.resolved, discord.Message):
        parent: discord.Message = message.reference.resolved
        if parent.author.id == bot.user.id:
            replying_to_bot = True

    # A) Oreo himself talks → sometimes reassure him
    if is_oreo and SELF_LINES and random.random() < SELF_RESPONSE_CHANCE:
        line = random.choice(SELF_LINES)
        try:
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to reply to Oreo: {e}")
        await bot.process_commands(message)
        return

    # B) Others mention Oreo / say oreo / argue with the defence
    should_respond = mentioned_oreo or said_trigger_word or replying_to_bot

    if should_respond and random.random() < RESPONSE_CHANCE:
        if replying_to_bot and REPLY_LINES:
            line = random.choice(REPLY_LINES)
        else:
            line = random.choice(DEFENCE_LINES)

        try:
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send reply: {e}")

    await bot.process_commands(message)


# --------------- RUN ---------------

if not TOKEN:
    raise RuntimeError("Set DISCORD_TOKEN env var or hardcode your token in the script.")

bot.run(TOKEN)
