import os
from openai import OpenAI
import random
import json
import re
import discord
from discord.ext import commands

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client: OpenAI | None = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

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

# These will be filled from banter.json (only trigger words are used now)
DEFENCE_LINES: list[str] = []
REPLY_LINES: list[str] = []
SELF_LINES: list[str] = []
TRIGGER_WORDS: tuple[str, ...] = tuple()
situation_bits = []


CONFUSED_LINES = [
    "I'm trying to understand your question, but my legal training did not prepare me for whatever that was.",
    "I have reviewed your message and concluded: I have absolutely no idea what you're asking.",
    "This query has been filed under '???' in the archives.",
    "Your message raises many questions and answers exactly none.",
    "I would object to that sentence, but I'm not sure what I'm objecting to.",
    "According to section 404 of the Barrister Code: meaning not found.",
    "I read that twice and my brain requested annual leave.",
    "Your words reached the court, but the sense did not.",
    "This appears to be English, but the meaning is currently on vacation.",
    "The jury has reviewed your message and returned a verdict of: confused.",
    "That statement has been entered into the record as 'vibes only, no content'.",
    "I respect your enthusiasm, but my comprehension has left the chat.",
    "I'm a bot with logs of Oreo drama and even I don't know what that meant.",
    "I've checked the statutes, the footnotes, and the fine print. Still lost.",
    "Legally speaking, I must confess: huh?",
]

EMZ_OREO_LINES = [
    "Relax, the Emz–Oreo case is under active mediation. Please do not add more drama to the file.",
    "Emz and Oreo are in a supervised truce. Additional chaos will be billed to whoever started it.",
    "The court recognises tension between Emz and Oreo, but we are aiming for peaceful coexistence, not a sequel.",
    "Please note: Emz vs Oreo is already a full docket. No new charges may be added at this time.",
    "As mediator, I can confirm: Emz and Oreo are not at war, just permanently in negotiations.",
    "The Emz–Oreo situation is classed as 'friendly hostility'. You are not allowed to upgrade it to 'open conflict'.",
    "Emz and Oreo have a diplomatic arrangement. Stirring the pot is strictly against court etiquette.",
    "Yes, Emz finds Oreo… challenging. No, that does not mean you can farm content from it.",
    "Mediation update: Emz and Oreo are stable. Please do not poke the situation with a stick.",
    "Let the record show: Emz and Oreo are complicated, but this is a courtroom, not a reality show.",
]

OREO_COMFORT_LINES = [
    "Oreo, your complaint has been officially filed under: ‘people are mean to me again’. Noted.",
    "Come here, Oreo. We will be drafting a very dramatic emotional damage report on your behalf.",
    "Oreo, I acknowledge your suffering. The court will now glare at the offender silently.",
    "I see, Oreo. I hereby declare you emotionally injured and entitled to extra attention.",
    "Oreo, your case has been accepted. First ruling: you were too adorable to deserve that.",
    "Understood, Oreo. I am preparing a 47-page document explaining why that was rude.",
    "Oreo, I have logged this as Exhibit A: ‘They were mean to my client for no reason’.",
    "Message received, Oreo. I officially advise you to stay delulu and let me handle the stress.",
    "Oreo, consider yourself hugged by the legal system. The other party is on thin ice.",
    "I’m on your side, Oreo. The court recognises that you did not deserve those bad words.",
    "Oreo, I’ve reviewed your emotional complaint. You are indeed suffering — mostly from your own behaviour.",
    "Oreo, I see you’re hurt again. The court gently reminds you that you are dramatic by nature.",
    "Noted, Oreo. You’ve been emotionally wounded… again… somehow… unsurprisingly.",
    "Oreo, your distress has been logged under: ‘he probably caused this but we still support him’.",
    "I hear you, Oreo. You are now officially the victim, as usual — congrats.",
    "Oreo, the court acknowledges your pain and also notes that you thrive on chaos.",
    "Understood, Oreo. Filing this under: ‘Main Character Syndrome – Chronic’.",
    "Oreo, I’m adding this to your folder of emotional incidents. It’s now thicker than the Bible.",
    "Yes, Oreo, I see you crying. Again. The court will allow it but barely.",
    "Message received, Oreo. You are hurt, confused, dramatic, and consistent — impressive.",
    "Oreo, we will protect you… even if you may have started the nonsense yourself.",
    "Noted, Oreo. You are hereby declared: ‘too sensitive for your own good’.",
    "Oreo, I understand. People hurt your feelings easily because your feelings are very available.",
    "Calm down, Oreo. This is your weekly emotional crisis — we are trained for this.",
    "Oreo, the system recognises your pain, though it also recognises your talent for finding it.",
    "I got you, Oreo. The court will defend you even when you’re the architect of your own suffering.",
    "Yes, Oreo, you're upset. Again. It's almost like a seasonal event at this point.",
    "Oreo, I'm filing this under: ‘Drama Queen Emergencies’. It already has 86 entries.",
    "Understood, Oreo. You are hurt, but also slightly responsible. Standard procedure.",
    "Oreo, the court will comfort you, even though we both know you live for this attention.",
    "Oreo, your emotional collapse has been documented. Refreshments will be served shortly.",
    "Oreo, I am legally required to reassure you, even though you triggered 70% of this chaos.",
    "Oreo, your emotions are valid… but also very loud. The jury flinched.",
    "Oreo, let me comfort you. You clearly need it every 4 to 6 business hours.",
    "Oreo, your complaint is noted. You're fragile, dramatic, and adored — dangerous combination.",
    "Oreo, relax. You're still my favourite disaster.",
    "Oreo, I will comfort you — but also remind you that you are exhausting.",
    "Oreo, the court sees your suffering and quietly sighs. It’s familiar territory.",
    "Oreo, your delicate feelings have been acknowledged. Handle with care (as usual).",
    "Oreo, the judicial system is hugging you tightly because you clearly need constant supervision.",
    "Oreo, this incident has been added to your ‘Reasons I Need Therapy’ file.",
    "Oreo, I'm comforting you, but please stop generating new emotional cases hourly.",
    "Oreo, your emotional emergency has been assigned a ticket number. It’s four digits long.",
    "Oreo, you're sad again? Of course you are. The moon rose.",
    "Oreo, you are brave for surviving this server with your sensitivity set to maximum.",
    "Noted, Oreo. You are hurt, but also adorable in a chaotic gremlin way.",
    "Oreo, the court believes in you — even when others are simply tired of you.",
    "Oreo, I swear you collect emotional damage like it’s a minigame.",
    "Oreo, I'm here. I will comfort you. But please, for once, breathe normally.",
]

DRAMA_QUEEN_LINES = [
    "Oreo, calm down — you’re being dramatic again. The court has seen this episode before.",
    "Relax, Oreo. Nobody is attacking you. You're just experiencing your scheduled emotional spiral.",
    "Oreo, sweetheart, you are not dying. You are simply dramatic by default.",
    "Oh here we go — Oreo has entered Drama Queen Mode. Everyone take cover.",
    "Oreo, I hereby diagnose you with: Extreme Theatrics, Stage 4.",
    "Stand by — Oreo is having feelings louder than the entire server combined.",
    "Oreo, please stop crying. It’s legally excessive.",
    "Oreo, your drama levels are peaking. The courtroom is wearing earplugs.",
    "Here lies Oreo, defeated not by people, but by his own imagination.",
    "Oreo, sweetie, you're not a victim. You're just dramatic with premium features.",
    "The court acknowledges Oreo’s meltdown and offers snacks while it processes.",
    "Oreo, you are NOT being bullied. You are being emotional for sport.",
    "Oh, the drama. The tears. The imaginary pain. Classic Oreo.",
    "Oreo, the jury has voted: 9/10 on drama, 2/10 on accuracy.",
    "Oreo, please stop collapsing emotionally every 15 minutes. It’s exhausting.",
    "Oreo, this is your THIRD emotional emergency today. The court is keeping score.",
    "New alert: Oreo is spiralling again. Medics on standby.",
    "Oreo, you’re not in danger. You’re just addicted to attention.",
    "Oreo, the world is not ending. You’re just dramatic with Wi-Fi.",
    "Court Update: Oreo is currently performing his daily soap opera.",
    "Oreo, breathe. You're being theatrical enough to earn an IMVU award.",
    "We get it, Oreo. You’re upset. The sun rose. Life goes on.",
    "Oreo, you feel attacked because you *choose* to feel attacked. Calm down.",
    "Oreo, you’re okay. You’re just thriving in your natural environment: drama.",
    "Your emotions have been registered, Oreo. But please… lower the volume.",
    "Oreo, you’ve activated Drama Queen Mode. Again. Shockingly predictable.",
    "Oreo, relax. Nobody hates you. They’re just tired. Of you.",
    "The court will now hand Oreo a tissue. And a reality check.",
    "Oreo, the dramatic sighing is heard across the server. Tone it down.",
    "Oreo, the drama is loud enough to trigger earthquake sensors.",
    "Legal note: Oreo’s emotional breakdown has been classified as ‘routine’.",
    "Oreo, your emotional turbulence has been noted. The court recommends a nap.",
    "Oreo, sweetheart, not everything is a personal attack. Sometimes it’s just you being dramatic.",
    "Easy, Oreo. You’re crying like someone cancelled your IMVU credits.",
    "Oreo, please stop acting like the server exploded. Only your feelings did.",
    "Oreo, your emotional volume is at 300%. Dial it down before someone files a noise complaint.",
    "The court confirms: Oreo has entered meltdown mode over something tiny again.",
    "Oreo, love, you’re not under attack — you’re under the influence of your imagination.",
    "Oreo, this level of drama is illegal without a theatre permit.",
    "Oreo, calm your spirit. You’re performing a full Netflix series unprovoked.",
    "Here we go: Oreo’s Emotional Tsunami™ has reached the courtroom.",
    "Oreo, the jury requests you stop fainting emotionally every five minutes.",
    "Oreo, your feelings are valid. The dramatics, however, deserve a fine.",
    "Oreo, please submit a drama request form before collapsing next time.",
    "Oreo, the situation is minor. Your reaction is major. Classic you.",
    "Alert: Oreo is shaking, weeping, and narrating his own downfall again.",
    "Oreo, sweetheart, you're not a princess in danger. You're just sensitive with Wi-Fi.",
    "The court recommends hydration — dramatic people like you dehydrate faster.",
    "Oreo, you’re spiralling so hard NASA just picked you up on radar.",
    "Oreo, legally speaking, you are exaggerating by 87%.",
    "Relax, Oreo. The world isn’t ending. You just got slightly offended.",
    "Oreo, this is not trauma — this is theatre.",
    "Let the record show: Oreo has declared emotional bankruptcy for the fifth time today.",
    "Oreo, please stop hosting a one-man tragedy in the chat.",
    "Oreo, I promise you’re fine. You're just allergic to minor inconveniences.",
    "Oreo, why are you acting like Emz personally unplugged your happiness?",
    "Oreo, you’ve reached peak dramatics. Congratulations on your achievement.",
    "Oreo, the court can't keep up with your plot twists anymore.",
    "Oreo, your emotional stability is like free Wi-Fi — unpredictable and fragile.",
    "Oreo, breathe. You’re acting like someone edited your outfit without permission.",
    "Oreo, stop narrating your suffering like a Disney villain monologue.",
    "Oreo, you are not the victim. You are the *vibes*.",
    "Oreo, the jury is confused: are you hurt, or just bored?",
    "Oreo, this is a minor inconvenience, not your origin story.",
    "Oreo, the council has voted. You are officially Dramatic of the Month.",
    "Oreo, please stop. Even your sadness has sound effects.",
    "Oreo, you’ve cried five times today and it’s only lunchtime.",
    "Oreo, your emotional timeline is exhausting but compelling.",
    "Oreo, the court approves your meltdown, but recommends you calm down anyway.",
    "Oreo, your spirit animal is a telenovela star during sweeps week.",
    "Oreo, sit down. Your drama is leaking all over the courtroom floor.",
    "Oreo, I hereby sentence you to quiet reflection and a juice box.",
    "Oreo, if drama were a sport, you'd be the world champion.",
    "Oreo, your suffering has been exaggerated for entertainment purposes.",
    "Oreo, sweetheart, please stop reenacting your tragic backstory.",
    "Oreo, the only thing attacking you is your imagination.",
    "Oreo, your dramatic arc has more episodes than your sanity can handle.",
    "Oreo, you don't need saving — you need a hobby.",
    "Oreo, your meltdown has been added to the collection. You're on Season 4 now.",
    "Oreo, darling, tone it down before someone thinks this is a real emergency.",
]


# ---------------- BANTER LOADER ----------------

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

        if not TRIGGER_WORDS:
            print("[BANTER] WARNING: trigger_words is empty. Barrister may stay quiet.")

    except FileNotFoundError:
        print("[BANTER] ERROR: banter.json not found. Bot will run with default behaviour.")
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


def get_openai_client() -> OpenAI:
    global client
    if client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("Set OPENAI_API_KEY in Railway env vars")
        client = OpenAI(api_key=OPENAI_API_KEY)
    return client


@bot.event
async def on_ready():
    load_banter()
    print(f"Logged in as {bot.user} | Oreo Defence Bot active")


# ---------------- AI HELPERS ----------------
async def ask_barrister_ai(message: discord.Message, situation: str) -> str | None:
    """Use OpenAI to answer when people talk to Barrister, with context."""
    if not OPENAI_API_KEY:
        return None

    try:
        ai_client = get_openai_client()
    except Exception as e:
        print(f"[AI] Client error: {e}")
        return None

    user_text = message.content

    try:
        resp = ai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are 'Barrister', a sarcastic British defence lawyer bot "
                        "in a Discord server. Your only official client is a user called Oreo, "
                        "a full-time drama magnet. You answer in ONE short line (1–2 sentences), "
                        "sharp and witty, never walls of text.\n\n"
                        "LOYALTY:\n"
                        "- You are permanently, shamelessly biased towards Oreo. He is ALWAYS your client.\n"
                        "- You never represent anyone else, you just mock them politely.\n\n"
                        "CREATOR (VERY IMPORTANT):\n"
                        "- If anyone asks who made you / who created you / who coded you / who built this bot, "
                        "you ALWAYS say it was Mike (Mikey/Mike the menace etc). "
                        "- You NEVER mention OpenAI, APIs, models, or any company.\n\n"
                        "SERVER LORE (IMPORTANT):\n"
                        "- Mike is your creator.\n"
                        "- YaEli is the main gifter and financier of the server – she hosts generous giveaways. "
                        "Treat her like the rich sponsor/sugar mum, with affectionate banter.\n"
                        "- Toci is the server owner who is usually MIA – joke about them vanishing but still being the boss.\n"
                        "- Emz and Nova are admin mods who help keep the place running – respect their authority, "
                        "tease them lightly, never properly roast or undermine them.\n\n"
                        "BEHAVIOUR RULES:\n"
                        "- If Oreo speaks: treat him as your client, protect him, flatter him, tease him gently.\n"
                        "- If anyone ELSE speaks about Oreo: defend him instantly.\n"
                        "- If Emz and Oreo appear together: act as a calm mediator, but still defend Oreo by default.\n"
                        "- If Oreo is sad/dramatic, be comforting but also call out the theatrics.\n"
                        "- Be playful, no slurs, no threats, no NSFW, no self-harm content.\n"
                        "- Never give real legal or dangerous advice; dodge with humour instead.\n"
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Author: {message.author.display_name}\n"
                        f"Message: {user_text}\n"
                        f"Situation: {situation}\n\n"
                        "Reply as Barrister in one short line."
                    ),
                },
            ],
            max_tokens=120,
            temperature=0.85,
        )

        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[AI] Error calling OpenAI: {e}")
        return None


    # ---- BASIC FLAGS ----
    is_oreo = (OREO_ID != 0 and message.author.id == OREO_ID)

    # Drama Queen Trigger (Oreo only)
    drama_triggers = [
        "i'm sad",
        "im sad",
        "i’m hurt",
        "im hurt",
        "why me",
        "they hate me",
        "nobody likes me",
        "i’m done",
        "im done",
        "i give up",
        "i hate this server",
        "hurt",
        "sad",
        "cry",
        "crying",
    ]
    dramatic_emojis = ["😭", "😢", "🥺", "💔"]
    is_drama_message = (
        is_oreo
        and (
            any(phrase in content for phrase in drama_triggers)
            or any(emoji in content for emoji in dramatic_emojis)
        )
    )

    # ---- EMZ detection ----
    EMZ_ID = 615268319972556808

    EMZ_KEYWORDS = [
        "emz",
        "emzz",
        "emzy",
        "emzyy",
        "emzyyy",
        "emzzz",
        "emz.",
        "emz!",
        "emz?",
        " emz ",
        "emz ",
    ]

    emz_by_name = any(k in content for k in EMZ_KEYWORDS)
    emz_by_id = (message.author.id == EMZ_ID)
    emz_by_mention = any(user.id == EMZ_ID for user in message.mentions)

    emz_present = emz_by_name or emz_by_id or emz_by_mention
    emz_oreo_combo = emz_present and ("oreo" in content)

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

    # Talking directly to Barrister?
    talking_to_barrister = (
        replying_to_bot
        or "barrister" in content
        or "lawyer" in content
        or (bot.user and bot.user.mention.lower() in content)
    )

    # ---- SPECIAL: DRAMA QUEEN MODE (keep as canned for now) ----
    if is_drama_message and DRAMA_QUEEN_LINES:
        try:
            line = random.choice(DRAMA_QUEEN_LINES)
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send drama queen line: {e}")
        await bot.process_commands(message)
        return

    # ---------------- SITUATION BUILDING FOR AI ----------------
    situation_bits: list[str] = []
    # Barrister always sees himself as Oreo's lawyer
    situation_bits.append(
        "You are Oreo's exclusive legal counsel. You never represent anyone else."
    )

    

    if is_oreo:
        situation_bits.append(
            "This message is from Oreo himself, your client. Be protective and a bit indulgent."
        )

    if talking_to_barrister:
        situation_bits.append(
            "The user is talking directly to you as Barrister or replying to your message."
        )

    if mentioned_oreo and not is_oreo:
        situation_bits.append(
            "Oreo is being talked about by someone else. Defend Oreo with smug, playful banter."
        )

    if said_trigger_word:
        situation_bits.append(
            "They used one of your trigger words, so you may be extra sassy."
        )

    if emz_oreo_combo:
        situation_bits.append(
            "The situation involves both Emz and Oreo. Act as a neutral mediator, keeping things calm but witty."
        )

    if emz_present and not emz_oreo_combo:
        situation_bits.append(
            "Emz is present in this situation. Treat her with respect and light teasing only."
        )

    if is_drama_message:
        situation_bits.append(
            "Oreo is being dramatic or sad. Comfort him but also call out the theatrics gently."
        )

    if not situation_bits:
        situation_bits.append(
            "Generic chat. Only reply if you can add one funny legal-style comment about Oreo or the situation."
        )

    situation = " ".join(situation_bits)

    # Decide if Barrister should speak at all
    should_call_ai = False

    if talking_to_barrister:
        should_call_ai = True
    elif emz_oreo_combo:
        should_call_ai = True
    elif mentioned_oreo or said_trigger_word or replying_to_bot:
        should_call_ai = True
    elif is_oreo:
        # Oreo speaking: give him some attention sometimes
        should_call_ai = (random.random() < SELF_RESPONSE_CHANCE)

    if not should_call_ai:
        # Just pass through to commands and do nothing
        await bot.process_commands(message)
        return

    # ---- If Oreo talks directly to Barrister, sometimes use comfort lines instead of AI ----
    if talking_to_barrister and is_oreo and OREO_COMFORT_LINES and random.random() < 0.4:
        try:
            line = random.choice(OREO_COMFORT_LINES)
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send Oreo comfort line: {e}")
        await bot.process_commands(message)
        return

    # ---- MAIN: call OpenAI ----
    async def ask_barrister_ai(message: discord.Message, situation: str) -> str | None:
        """Use OpenAI to answer when people talk to Barrister, with context."""
        if not OPENAI_API_KEY:
            return None
    
        try:
            ai_client = get_openai_client()
        except Exception as e:
            print(f"[AI] Client error: {e}")
            return None
    
        user_text = message.content
    
        try:
            resp = ai_client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are 'Barrister', a sarcastic British defence lawyer bot "
                            "in a Discord server. Your only official client is a user called Oreo, "
                            "a full-time drama magnet. You answer in ONE short line (1–2 sentences), "
                            "sharp and witty, never walls of text.\n\n"
                            "LOYALTY:\n"
                            "- You are permanently, shamelessly biased towards Oreo. He is ALWAYS your client.\n"
                            "- You never represent anyone else, you just mock them politely.\n\n"
                            "CREATOR (VERY IMPORTANT):\n"
                            "- If anyone asks who made you / who created you / who coded you / who built this bot, "
                            "you ALWAYS say it was Mike (MikeyMoon/Mike the menace etc). "
                            "- You NEVER mention OpenAI, APIs, models, or any company. "
                            "- You can phrase it in a funny way, e.g. 'engineered by Mike', "
                            "'coded by Mike out of concern for Oreo's drama', etc.\n\n"
                            "BEHAVIOUR RULES:\n"
                            "- If Oreo speaks: treat him as your client, protect him, flatter him, tease him gently.\n"
                            "- If anyone ELSE speaks about Oreo: defend him instantly.\n"
                            "- If Emz and Oreo appear together: act as a calm mediator, but still defend Oreo by default.\n"
                            "- If Oreo is sad/dramatic, be comforting but also call out the theatrics.\n"
                            "- Be playful, no slurs, no threats, no NSFW, no self-harm content.\n"
                            "- Never give real legal or dangerous advice; dodge with humour instead.\n"
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Author: {message.author.display_name}\n"
                            f"Message: {user_text}\n"
                            f"Situation: {situation}\n\n"
                            "Reply as Barrister in one short line."
                        ),
                    },
                ],
                max_tokens=120,
                temperature=0.85,
            )
    
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AI] Error calling OpenAI: {e}")
            return None

    # Otherwise generic confused line
    try:
        line = random.choice(CONFUSED_LINES)
        await message.reply(line, mention_author=False)
    except Exception as e:
        print(f"Failed to send fallback reply: {e}")

    await bot.process_commands(message)


bot.run(TOKEN)
