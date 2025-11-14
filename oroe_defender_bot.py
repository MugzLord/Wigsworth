import os
import random
import json
import discord
from discord.ext import commands

# --------------- CONFIG ---------------

TOKEN = os.getenv("DISCORD_TOKEN")  # or paste token directly (not recommended)

# 👉 REPLACE THIS with Oroe's real Discord user ID
OROE_ID = 123456789012345678

# How often the bot should respond (0.0 = never, 1.0 = always)
RESPONSE_CHANCE = 0.7

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# --------------- DEFAULT LINES (fallback) ---------------

DEFAULT_DEFENCE_LINES = [
    "Oi, leave Oroe alone — man’s already hanging on by a prayer and a half-charged phone.",
    "Before you speak on Oroe, please remember he’s on someone’s prayer request list.",
    "Objection! My client Oroe is guilty only of being adorable and mildly inconvenient.",
    "Stop slandering Oroe — he’s fragile. He bruises like a Tesco peach.",
    "Let’s not attack Oroe today, he woke up with 2% battery and zero emotional stability.",
    "God forgives everything… except the slander you lot throw at Oroe.",
    "Your Honour, the hate towards Oroe is outrageous, biased, and honestly a bit jealous.",
    "Don’t bully Oroe. He cries in 1080p HD with immersive surround sound.",
    "Even when Oroe is wrong, he’s right. That’s the rule. I don’t make them, I just enforce them.",
    "Not too loud please — Oroe is sensitive, like Wi-Fi in a storm.",
]

DEFAULT_REPLY_LINES = [
    "Arguing with a bot about Oroe? Yeah, you’re in too deep.",
    "You’re replying to me instead of apologising to Oroe, interesting.",
    "Imagine backchatting Oroe’s lawyer bot. Extremely brave.",
    "I see you replying — just say you love Oroe and go.",
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
    print(f"Logged in as {bot.user} (Oroe Defence Bot active)")


@bot.event
async def on_message(message: discord.Message):
    # Ignore all bot messages (including itself)
    if message.author.bot:
        return

    content = message.content.lower()

    # 1) Did they tag Oroe directly?
    mentioned_oroe = any(user.id == OROE_ID for user in message.mentions)

    # 2) Did they say his name/word?
    said_oroe_word = ("oroe" in content) or ("oreo" in content)

    # 3) Are they replying to this bot?
    replying_to_bot = False
    if message.reference and isinstance(message.reference.resolved, discord.Message):
        parent: discord.Message = message.reference.resolved
        if parent.author.id == bot.user.id:
            replying_to_bot = True

    should_respond = mentioned_oroe or said_oroe_word or replying_to_bot

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
