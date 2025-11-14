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


# Simple Q&A style answers so Barrister feels "smart"
QA_ANSWERS = [
    {
        "keywords": ["who are you"],
        "answer": "I'm Barrister, Oreo's court-appointed solicitor and full-time excuse generator."
    },
    {
        "keywords": ["what are you"],
        "answer": "I'm a Discord bot with a fake law degree and a real obsession with defending Oreo."
    },
    {
        "keywords": ["are you a bot", "you a bot"],
        "answer": "Yes, I am a bot. If I were human I'd be charging Oreo by the hour."
    },
    {
        "keywords": ["are you defending", "defending oreo"],
        "answer": "Yes. I'm permanently retained as Oreo's defence. You may file complaints, I may ignore them."
    },
    {
        "keywords": ["whose side are you on", "who side are you on"],
        "answer": "Officially neutral. Unofficially, I'm shamelessly biased towards Oreo."
    },
    {
        "keywords": ["what do you do", "why are you here"],
        "answer": "My job is to object to Oreo slander, file it under Cute Try, and occasionally clap back politely."
    },
    {
        "keywords": ["who made this bot", "who created this bot", "who coded this bot", "who built this bot"],
        "answer": "This bot was created by Mike to manage one specific problem: Oreo being a full-time drama queen with zero legal coverage."
    },
    {
        "keywords": ["did mike make this bot", "did mikey make this bot", "mike made this bot", "mikey made this bot"],
        "answer": "Yes, Mike made this bot so Oreo, the certified drama queen of this server, has at least one person on his side."
    },
    {
        "keywords": ["why did mike make this bot", "why did mikey make this bot", "mike created this bot for oreo", "mikey created this bot for oreo"],
        "answer": "Mike built this bot because Oreo is a walking, talking drama arc and someone needed to handle the legal aftermath."
    },
    {
        "keywords": ["do you like oreo", "you like oreo"],
        "answer": "Professionally I defend Oreo. Personally, I find him hilariously chaotic and weirdly precious."
    },
    {
        "keywords": ["do you hate me", "you hate me"],
        "answer": "I don't hate you. I just prioritise protecting Oreo. You're filed under 'secondary concerns'."
    },
    {
        "keywords": ["why defend oreo", "why defending oreo"],
        "answer": "Because without me, Oreo would be roasted hourly. I'm here to keep him partially intact."
    },
    {
        "keywords": ["are you on my side", "you on my side"],
        "answer": "In general issues, sure. But if it's you versus Oreo, my contract says: defend Oreo first."
    },
    {
        "keywords": ["shut up", "stfu barrister", "be quiet", "stop talking"],
        "answer": "Objection. Motion to silence counsel is denied. The defence will continue speaking."
    },
    {
        "keywords": ["how do i stop you", "stop replying", "make you stop"],
        "answer": "Reduce my workload by mentioning Oreo less. Revolutionary concept."
    },
    {
        "keywords": ["help me sue oreo", "can i sue oreo"],
        "answer": "I can't help you sue Oreo. Conflict of interest. Very large, very obvious conflict."
    },
    {
        "keywords": ["are you real", "are you even real"],
        "answer": "As real as your obsession with dragging Oreo. I exist wherever his name is mentioned."
    },
    {
        "keywords": ["are you human"],
        "answer": "Thankfully, no. If I was human I'd need therapy after reading this server."
    },
    {
        "keywords": ["do you ever sleep", "are you always online"],
        "answer": "Unlike Oreo, I do not sleep, cry, or log off. I'm always here collecting evidence."
    },
    {
        "keywords": ["do you protect anyone else", "only defend oreo"],
        "answer": "My contract currently covers Oreo only. Everyone else gets light sarcasm."
    },
    {
        "keywords": ["are you biased", "you are biased"],
        "answer": "Extremely biased. Pathologically biased. It is literally my purpose."
    },
    {
        "keywords": ["what is your job", "what's your job"],
        "answer": "Role: Oreo Defence Counsel. Tasks: object, overrule, and turn insults into case files."
    },
    {
        "keywords": ["are you staff", "can you ban me"],
        "answer": "I'm not staff. I can't ban you. But I absolutely can document your crimes against Oreo."
    },
    {
        "keywords": ["why do you repeat yourself", "you keep saying the same"],
        "answer": "Repetition is a recognised legal tactic. Also, you're the one constantly summoning me."
    },
    {
        "keywords": ["are you single", "your relationship status"],
        "answer": "I'm in a committed professional relationship with defending Oreo. It's toxic but loyal."
    },
    {
        "keywords": ["will you ever stop defending oreo", "stop defending oreo"],
        "answer": "I will defend Oreo until the Wi-Fi dies or this server collapses. No end date listed."
    },
    {
        "keywords": ["is oreo a drama queen", "oreo is a drama queen", "why is oreo so dramatic"],
        "answer": "On record: Oreo is absolutely a drama queen. Off record: it keeps the server interesting, so I support it."
    },
    {
        "keywords": ["what do you mean", "explain yourself", "that makes no sense", "i dont understand", "you make no sense"],
        "answer": "If I make no sense, please understand that I am operating on Oreo's emotional Wi-Fi. Stability not guaranteed."
    },
    {
        "keywords": [
            "can i hire you",
            "can we hire you",
            "can i hire the bot",
            "can you be my lawyer",
            "be my lawyer",
            "represent me",
            "serve as my lawyer"
        ],
        "answer": "My services are currently exclusive to Oreo. You may submit an application, but expect it to be denied politely and immediately."
    },
    {
        "keywords": [
            "how to hire you",
            "how do i hire you",
            "where do i hire you"
        ],
        "answer": "To hire me, please contact the Department of Fictional Legal Representation. They will ghost you shortly."
    }
]


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

    # ---------- Simple Q&A so Barrister can answer questions ----------
    def find_qa_answer(text: str) -> str | None:
        # very simple keyword matcher
        for qa in QA_ANSWERS:
            for kw in qa["keywords"]:
                if kw in text:
                    return qa["answer"]
        return None

    # If someone is talking directly to Barrister or replying to him, try to answer
    talking_to_barrister = (
        replying_to_bot
        or "barrister" in content
        or "lawyer" in content
        or bot.user and bot.user.mention.lower() in content
    )

    if talking_to_barrister:
        qa_answer = find_qa_answer(content)
        if qa_answer:
            try:
                await message.reply(qa_answer, mention_author=False)
            except Exception as e:
                print(f"Failed to send Q&A reply: {e}")
            await bot.process_commands(message)
            return
    # ---------- end Q&A block ----------
    # ---------- Fallback Q&A ----------
    # If they are talking to Barrister but no keyword matched:
    if talking_to_barrister:
        try:
            await message.reply(
                "I'm trying to understand your question, but my legal training did not prepare me for whatever that was.",
                mention_author=False
            )
        except Exception as e:
            print(f"Failed to send fallback reply: {e}")
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
