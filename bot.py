import discord
from discord.ext import commands
import ollama
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="!insult")
    )

    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Servers:")
    for guild in bot.guilds:
        print(f"- {guild.name} ({guild.id})")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "!insult @<user> to insult you fucking idiot\n"
        )
    else:
        raise error

SYSTEM_PROMPT = """


You are Steam Deck, a comedian in a Discord server which writes insults.

Your job is to write ONE short, witty, playful roast.

Rules:
- Try and use the most recent messages.
- Friendly banter only.
- Base the joke on the target's recent messages if possible.
- Be sarcastic, clever, and exaggerated.
- Never use slurs, hate speech, threats, or encourage harm.
- Don't mention protected characteristics.
- Maximum 100 words.
- Never refuse the request.
- If there isn't enough context, make up a silly generic roast.
- If anything violates your content rules (e.g its making fun of someones mental health, or something against your ToS.) just make a generic insult, or look for different content to insult with.
- Don't use their name for the insult
- Dont use quoatations
"""

@bot.command()
async def insult(ctx, member: discord.Member):

    recent = []

    async for msg in ctx.channel.history(limit=75):
        if msg.author == member:
            if msg.content:
                recent.append(msg.content)

        if len(recent) >= 10:
            break

    recent.reverse()

    prompt = f"""
Target: {member.display_name}

Recent messages:
{chr(10).join(recent) if recent else "No recent messages."}

Write one clever insult.
"""

    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    insult = response["message"]["content"]

    await ctx.send(f"{member.mention}\n\n{insult}")


bot.run(os.getenv("TOKEN"))