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
OREO_COMFORT_LINES = [


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
    "I've checked the statutes, the footnotes, and the fine print. Still lost."
    "Legally speaking, I must confess: huh?"
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
    "Let the record show: Emz and Oreo are complicated, but this is a courtroom, not a reality show."
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
    "I’m on your side, Oreo. The court recognises that you did not deserve those bad words."
    "Oreo, I’ve reviewed your emotional complaint. You are indeed suffering — mostly from your own behaviour.",
    "Oreo, I see you’re hurt again. The court gently reminds you that you are dramatic by nature.",
    "Noted, Oreo. You’ve been emotionally wounded… again… somehow… unsurprisingly.",
    "Oreo, your distress has been logged under: ‘he probably caused this but we still support him’.",
    "I hear you, Oreo. You are now officially the victim, as usual — congrats.",
    "Oreo, the court acknowledges your pain and also notes that you thrive on chaos.",
    "Understood, Oreo. Filing this under: ‘Main Character Syndrome – Chronic’",
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
    "Oreo, I'm here. I will comfort you. But please, for once, breathe normally."
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

    {
        "keywords": [
            "can you kill",
            "kill her",
            "kill him",
            "kill them",
            "kill lilith",
            "kill oreo"
        ],
        "answer": "Absolutely not. I’m a lawyer, not a hitman. We do de-escalation here, not murder requests."
    },
    {
        "keywords": [
            "hurt her",
            "hurt him",
            "hurt them"
        ],
        "answer": "No violence on the record, please. The worst I can do is file a very strongly worded complaint."
    },
    {
        "keywords": [
            "can you attack",
            "destroy her",
            "destroy him"
        ],
        "answer": "I only attack arguments, not people. Try therapy, not homicide."
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


import re  # make sure this is near the top of your file

def _norm(text: str) -> list[str]:
    # lower, remove punctuation, split into words
    cleaned = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return [w for w in cleaned.split() if w]

def find_qa_answer(text: str) -> str | None:
    text_words = set(_norm(text))
    if not text_words:
        return None

    best_answer = None
    best_score = 0.0

    for qa in QA_ANSWERS:
        for kw in qa["keywords"]:
            kw_words = set(_norm(kw))
            if not kw_words:
                continue
            overlap = len(text_words & kw_words)
            score = overlap / len(kw_words)  # how much of the keyword is covered

            if score > best_score:
                best_score = score
                best_answer = qa["answer"]

    # require at least half of the keyword words to match to avoid weird hits
    if best_score >= 0.5:
        return best_answer
    return None


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    content = message.content.lower()
    is_oreo = (message.author.id == OREO_ID)

    # Drama Queen Trigger
    drama_triggers = [
        "i'm sad", "im sad", "i’m hurt", "im hurt",
        "why me", "they hate me", "nobody likes me",
        "i’m done", "im done", "i give up", "i hate this server",
        "hurt", "sad", "cry", "crying",
    ]
    
    dramatic_emojis = ["😭", "😢", "🥺", "💔"]
    
    is_drama_message = (
        is_oreo and (
            any(phrase in content for phrase in drama_triggers) or
            any(emoji in content for emoji in dramatic_emojis)
        )
    )

    
    # ---- EMZ detection ----
    # Replace with Emz's real Discord ID
    EMZ_ID = 615268319972556808 
    
    EMZ_KEYWORDS = [
        "emz", "emzz", "emzy", "emzyy", "emzyyy",
        "emzzz", "emz.", "emz!", "emz?", " emz ", "emz "
    ]
    
    emz_by_name = any(k in content for k in EMZ_KEYWORDS)
    emz_by_id = (message.author.id == EMZ_ID)
    emz_by_mention = any(user.id == EMZ_ID for user in message.mentions)
    
    # TRUE if Emz is mentioned or talking
    emz_present = emz_by_name or emz_by_id or emz_by_mention
    
    # Emz talking about Oreo OR someone talking about Emz + Oreo
    emz_oreo_combo = (emz_present and "oreo" in content)

    # DEBUG: respond to "ping" so we know the bot is reading messages
    if content.strip() == "ping":
        try:
            await message.reply("pong (Oreo lawyer is alive)", mention_author=False)
        except Exception as e:
            print(f"Failed to send ping reply: {e}")
        await bot.process_commands(message)
        return

    # DRAMA QUEEN MODE
    if is_drama_message and DRAMA_QUEEN_LINES:
        try:
            line = random.choice(DRAMA_QUEEN_LINES)
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send drama queen line: {e}")
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

    # ---- Q&A: talking directly to Barrister ----
    talking_to_barrister = (
        replying_to_bot
        or "barrister" in content
        or "lawyer" in content
        or bot.user.mention.lower() in content
    )
    
    # --- If Oreo himself is talking to Barrister, comfort him ---
    if talking_to_barrister and is_oreo and OREO_COMFORT_LINES:
        try:
            line = random.choice(OREO_COMFORT_LINES)
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send Oreo comfort line: {e}")
        await bot.process_commands(message)
        return
    
    # --- Normal Q&A / confused answers for everyone else ---
    talking_to_barrister = (
        replying_to_bot
        or "barrister" in content
        or "lawyer" in content
        or bot.user.mention.lower() in content
    )
    
    # --- If Oreo himself is talking to Barrister, comfort him ---
    if talking_to_barrister and is_oreo and OREO_COMFORT_LINES:
        try:
            line = random.choice(OREO_COMFORT_LINES)
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send Oreo comfort line: {e}")
        await bot.process_commands(message)
        return
    
    # --- Normal Q&A / confused answers for everyone else ---
    if talking_to_barrister:
        qa_answer = find_qa_answer(content)
        if qa_answer:
            try:
                await message.reply(qa_answer, mention_author=False)
            except Exception as e:
                print(f"Failed to send Q&A reply: {e}")
            await bot.process_commands(message)
            return
    
        # fallback confused lines...
        try:
            line = random.choice(CONFUSED_LINES)
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send fallback reply: {e}")
        await bot.process_commands(message)
        return


    
    # ---- B) Others mention Oreo / say 'oreo' / argue with defence ----
    should_respond = mentioned_oreo or said_trigger_word or replying_to_bot

    # Special case: Emz + Oreo mentioned together -> mediator lines
    if emz_oreo_combo and EMZ_OREO_LINES and random.random() < RESPONSE_CHANCE:
        try:
            line = random.choice(EMZ_OREO_LINES)
            await message.reply(line, mention_author=False)
        except Exception as e:
            print(f"Failed to send Emz–Oreo mediator line: {e}")
        await bot.process_commands(message)
        return

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
        return


bot.run(TOKEN)
