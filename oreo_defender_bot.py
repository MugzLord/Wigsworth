import os
import random
import json
import discord
from discord.ext import commands

# ---------------- CONFIG ----------------

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN env var not set")

# Oreo's Discord user ID from env (Railway)
OREO_ID = int(os.getenv("OREO_ID", "0"))
if OREO_ID == 0:
    print("WARNING: OREO_ID not set or invalid. Bot will not know who Oreo is.")

RESPONSE_CHANCE = float(os.getenv("RESPONSE_CHANCE", "0.7"))
SELF_RESPONSE_CHANCE = float(os.getenv("SELF_RESPONSE_CHANCE", "0.3"))

intents = discord.Intents.default()
intents.message_content = True
# intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# These will be filled from banter.json
DEFENCE_LINES: list[str] = []
REPLY_LINES: list[str] = []
SELF_LINES: list[str] = []
TRIGGER_WORDS: tuple[str, ...] = tuple()


def load_banter():
    """Load trigger_words, defence_lines, reply_lines, self_lines from banter.json."""
    global DEFENCE_LINES, REPLY_LINES, SELF_LINES, TRIGGER_WORDS

    try:
        with open("banter.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        defence = data.get("defence_lines", [])
        reply = data.get("reply_lines", [])
        self_lines = data.get("self_lines", [])
        triggers = data.get("trigger_words", ["oreo"])

        DEFENCE_LINES = defence
        REPLY_LINES = reply
        SELF_LINES = self_lines
        TRIGGER_WORDS = tuple(w.lower() for w in triggers)

        print(
            f"[BANTER] Loaded "
            f"{len(DEFENCE_LINES)} defence, "
            f"{len(REPLY_LINES)} reply, "
            f"{len(SELF_LINES)} self lines, "
            f"{len(TRIGGER_WORDS)} trigger words."
        )

        if not DEFENCE_LINES:
            print("[BANTER] WARNING: defence_lines is empty.")
        if not TRIGGER_WORDS:
            print("[BANTER] WARNING: trigger_words is empty.")

    except FileNotFoundError:
        print("[BANTER] ERROR: banter.json not found. Bot will run but say nothing.")
        DEFENCE_LINES = []
        REPLY_LINES = []
        SELF_LINES = []
        TRIGGER_WORDS = tuple()
    except Exception as e:
        print(f"[BANTER] ERROR loading banter.json: {e}")
        DEFENCE_LINES = []
        REPLY_LINES = []
        SELF_LINES = []
        TRIGGER_WORDS = tuple()


@bot.event
async def on_ready():
    load_banter()
    print(f"Logged in as {bot.user} | Oreo Defence Bot active")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.lower()

    # DEBUG: respond to "ping" so we know the bot is reading messages
    if content.strip() == "ping":
        try:
            await message.reply("pong (Oreo lawyer is alive)", mention_author=False)
        except Exception as e:
            print(f"Failed to send ping reply: {e}")
        await bot.process_commands(message)
        return


    # 0) Is this Oreo himself speaking?
    is_oreo = (OREO_ID != 0 and message.author.id == OREO_ID)

    # 1) Did someone tag Oreo?
    mentioned_oreo = any(user.id == OREO_ID for user in message.mentions) if OREO_ID != 0 else False

    # 2) Did they say any trigger word?
    said_trigger_word = bool(TRIGGER_WORDS) and any(w in content for w in TRIGGER_WORDS)

    # 3) Are they replying to this bot?
    replying_to_bot = False
    if message.reference and isinstance(message.reference.resolved, discord.Message):
        parent: discord.Message = message.reference.resolved
        if parent.author.id == bot.user.id:
            replying_to_bot = True

    # ---- A) Oreo himself talks ----
    if is_oreo and SELF_LINES and random.random() < SELF_RESPONSE_CHANCE:
        line = random.choice(SELF_LINES)
        try:
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to reply to Oreo: {e}")
        await bot.process_commands(message)
        return

    # ---- B) Others mention Oreo / say 'oreo' / argue with defence ----
    should_respond = mentioned_oreo or said_trigger_word or replying_to_bot

    if should_respond and DEFENCE_LINES and random.random() < RESPONSE_CHANCE:
        if replying_to_bot and REPLY_LINES:
            line = random.choice(REPLY_LINES)
        else:
            line = random.choice(DEFENCE_LINES)

        try:
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send reply: {e}")

    await bot.process_commands(message)


bot.run(TOKEN)
