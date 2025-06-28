

import urllib.parse
import discord
import requests
import aiohttp
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()

import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
VALORANT_API_KEY = os.getenv("VALORANT_API_KEY")
BGMI_API_KEY = os.getenv("BGMI_API_KEY")
BGMI_DEV_UID = os.getenv("BGMI_DEV_UID")
FORTNITE_API_KEY = os.getenv("FORTNITE_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f"Bot is running as {bot.user}")

# --- Chess.com Command ---
@bot.command()
async def chess(ctx, username):
    username = username.lower()
    profile_url = f"https://api.chess.com/pub/player/{username}"
    stats_url = f"https://api.chess.com/pub/player/{username}/stats"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        profile_res = requests.get(profile_url, headers=headers)
        stats_res = requests.get(stats_url, headers=headers)

        if profile_res.status_code != 200:
            await ctx.send(f"❌ User `{username}` not found on Chess.com. (Status {profile_res.status_code})")
            return
        if stats_res.status_code != 200:
            await ctx.send(f"⚠️ Could not retrieve stats for `{username}`. (Status {stats_res.status_code})")
            return

        stats = stats_res.json()
        embed = discord.Embed(
            title=f"♟ Chess Stats for {username}",
            color=0x3498db
        )

        def add_game_mode(mode, name):
            if mode in stats:
                mode_data = stats[mode]
                rating = mode_data.get("last", {}).get("rating", "N/A")
                best = mode_data.get("best", {}).get("rating", "N/A")
                record = mode_data.get("record", {})
                wins = record.get("win", "N/A")
                losses = record.get("loss", "N/A")
                draws = record.get("draw", "N/A")

                embed.add_field(name=f"{name} Rating", value=f"{rating} (Best: {best})", inline=False)
                embed.add_field(name="W / L / D", value=f"{wins} / {losses} / {draws}", inline=True)
                embed.add_field(name="\u200b", value="\u200b", inline=True)  # spacing

        add_game_mode("chess_blitz", "Blitz")
        add_game_mode("chess_rapid", "Rapid")
        add_game_mode("chess_bullet", "Bullet")
        add_game_mode("chess_daily", "Daily")

        embed.set_footer(text="Data via Chess.com API")
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"[Error] Chess command failed: {e}")
        await ctx.send(f"⚠️ An error occurred while fetching stats.")





# --- Valorant Command ---

@bot.command()
async def valorant(ctx, tagline: str):
    await ctx.send("🔍 Fetching Valorant stats...")

    if "#" not in tagline:
        await ctx.send("⚠️ Please use the format: `!valorant username#tag`")
        return

    username, tag = tagline.split("#")
    encoded_username = urllib.parse.quote(username)
    encoded_tag = urllib.parse.quote(tag)

    headers = {
        "Authorization": VALORANT_API_KEY,
        "User-Agent": "DiscordBot (by Krishna)"
    }

    # Try each region until one works
    regions = ["na", "eu", "ap", "kr", "latam", "br"]
    mmr_data = None
    region_used = None

    async with aiohttp.ClientSession() as session:
        for region in regions:
            mmr_url = f"https://api.henrikdev.xyz/valorant/v2/mmr/{region}/{encoded_username}/{encoded_tag}"
            async with session.get(mmr_url, headers=headers) as mmr_response:
                if mmr_response.status == 200:
                    mmr_data = await mmr_response.json()
                    region_used = region
                    break
        if not mmr_data:
            await ctx.send("⚠️ MMR fetch failed for all regions.")
            return

        # Try to get summary
        summary_data = None
        summary_url = f"https://api.henrikdev.xyz/valorant/v2/summary/{region_used}/{encoded_username}/{encoded_tag}"
        async with session.get(summary_url, headers=headers) as summary_response:
            if summary_response.status == 200:
                summary_data = await summary_response.json()
            else:
                print(f"❌ Summary API Error {summary_response.status}: {await summary_response.text()}")

    # Prepare embed
    try:
        current = mmr_data["data"]["current_data"]
        rank = current.get("currenttierpatched", "Unranked")
        rr = current.get("ranking_in_tier", 0)
        elo = current.get("elo", "N/A")
        icon = current["images"]["small"]
        peak = mmr_data["data"]["highest_rank"]["patched_tier"]
        level = mmr_data["data"].get("account_level", "N/A")

        embed = discord.Embed(title=f"{username}#{tag} - Valorant Stats", color=discord.Color.purple())
        embed.set_thumbnail(url=icon)
        embed.add_field(name="Rank", value=f"{rank} ({rr} RR)", inline=True)
        embed.add_field(name="Peak Rank", value=str(peak), inline=True)
        embed.add_field(name="Account Level", value=str(level), inline=True)

        if summary_data:
            stats = summary_data["data"]["stats"]["all"]["overall"]
            kd = stats.get("kd", "N/A")
            win_pct = stats.get("win_percentage", "N/A")
            embed.add_field(name="K/D", value=str(kd), inline=True)
            embed.add_field(name="Win Rate", value=f"{win_pct}%", inline=True)
        else:
            embed.add_field(name="Note", value="No match data available (likely due to ranked reset).", inline=False)

        embed.set_footer(text=f"Region: {region_used.upper()} | Data via henrikdev.xyz")
        await ctx.send(embed=embed)

    except Exception as e:
        print("❌ Parsing error:", e)
        await ctx.send("⚠️ Could not parse Valorant data.")





# --- Fortnite Command ---
@bot.command()
async def fortnite(ctx, *, username):
    await ctx.send("🔍 Fetching Fortnite stats...")

    url = f"https://fortnite-api.com/v2/stats/br/v2?name={username}"

    headers = {
        "Authorization": FORTNITE_API_KEY,     
        "User-Agent": "Mozilla/5.0"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 403:
                    await ctx.send("🔒 This Fortnite account's stats are private.")
                    return
                elif response.status == 401:
                    await ctx.send("❌ Invalid or expired Fortnite API key.")
                    return
                elif response.status == 404:
                    await ctx.send(f"❌ User `{username}` not found.")
                    return

                data = await response.json()
                stats = data["data"]["stats"]["all"]["overall"]

                matches = stats.get("matches", "N/A")
                wins = stats.get("wins", "N/A")
                win_pct = stats.get("winRate", "N/A")
                kd = stats.get("kd", "N/A")
                kills = stats.get("kills", "N/A")

                embed = discord.Embed(title=f"🎮 Fortnite Stats for {username}", color=0x1abc9c)
                embed.add_field(name="Matches", value=str(matches), inline=True)
                embed.add_field(name="Wins", value=str(wins), inline=True)
                embed.add_field(name="Win Rate", value=f"{win_pct}%", inline=True)
                embed.add_field(name="Kills", value=str(kills), inline=True)
                embed.add_field(name="K/D Ratio", value=str(kd), inline=True)
                embed.set_footer(text="Data via fortnite-api.com")

                await ctx.send(embed=embed)

    except Exception as e:
        print(f"[Error] Fortnite command failed: {e}")
        await ctx.send("⚠️ Something went wrong while fetching Fortnite stats.")





@bot.command()
async def bgmi(ctx, uid: str):
    await ctx.send(f"🔍 Checking BGMI UID `{uid}`...")

    url = (
        "https://hl-gaming-official-main-v4-api.vercel.app/api"
        f"?sectionName=verify-bgmi&useruid={BGMI_DEV_UID}"
        f"&api={BGMI_API_KEY}&uid={uid}"
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 403:
                    await ctx.send("❌ Invalid credentials (developer UID or API key).")
                    return

                data = await resp.json()

        result = data.get("result", {})
        verified = result.get("verified", False)
        profile = result.get("official_response", {})

        if verified:
            username = profile.get("username", "Unknown")
            device = profile.get("device_bound", False)
            await ctx.send(
                f"✅ UID `{uid}` is valid!\n"
                f"• Username: `{username}`\n"
                f"• Device bound: {device}"
            )
        else:
            message = profile.get("message", "UID not found or not bound.")
            await ctx.send(f"❌ UID `{uid}` is invalid or not bound.\n• `{message}`")

    except Exception as e:
        print(f"[Error] BGMI command failed: {e}")
        await ctx.send("⚠️ Something went wrong while checking BGMI UID.")


bot.run(DISCORD_TOKEN)
