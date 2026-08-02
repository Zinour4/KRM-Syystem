from threading import Thread
from flask import Flask

app = Flask('')


@app.route('/')
def home():
  return "Bot is alive!"


def run():
  app.run(host='0.0.0.0', port=8080)


def keep_alive():
  t = Thread(target=run)
  t.daemon = True
  t.start()


import sys
keep_alive()
import sys
import asyncio
import traceback
import json
import os
import random
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

# ============ 🔑 التوكن ============
BOT_TOKEN = "MTUzMzIwMjc2NTQ2NjE3NzU4Ng.GLWEPa.jwUhdVbKyRwJCaoq1G27vGVH3yHX6Yr60e1VQk"
# ====================================

# ============ الإعدادات ============
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.reactions = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')

DEFAULT_IMAGE_INPUT = "1531696638408654879"
WARNS_FILE = 'data_warns.json'

# ============ دوال مساعدة ============
def parse_image_url(img_input: str) -> str:
    img_input = img_input.strip()
    if img_input.startswith("http://") or img_input.startswith("https://"):
        return img_input
    return f"https://cdn.discordapp.com/emojis/{img_input}.png?v=1"

def load_json(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            return json.load(f)
    return {}

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# ╔══════════════════════════════════════════════════════╗
# ║ 🏷️ القسم 1: نظام الرتب (Self-Roles)               ║
# ╚══════════════════════════════════════════════════════╝

FOOTBALL_ROLES_DATA = {
    "💛": {"name": "USMH", "color": discord.Color.from_rgb(255, 215, 0)},
    "🔴": {"name": "USMA", "color": discord.Color.from_rgb(220, 20, 60)},
    "🟢": {"name": "MCA",  "color": discord.Color.from_rgb(34, 139, 34)},
    "🔰": {"name": "JSK",  "color": discord.Color.from_rgb(255, 191, 0)},
    "⚪": {"name": "CRB",  "color": discord.Color.from_rgb(245, 245, 245)},
    "🖤": {"name": "ESS",  "color": discord.Color.from_rgb(30, 30, 30)},
}

GAMING_ROLES_DATA = {
    "👽": {"name": "Among Us",          "color": discord.Color.from_rgb(197, 17, 17)},
    "🔫": {"name": "Criminal",          "color": discord.Color.from_rgb(255, 140, 0)},
    "🪖": {"name": "PUBG",              "color": discord.Color.from_rgb(247, 202, 24)},
    "🏎️": {"name": "Forza Horizon",     "color": discord.Color.from_rgb(0, 120, 215)},
    "⚔️": {"name": "League of Legends", "color": discord.Color.from_rgb(200, 170, 110)},
}

GAMING1_ROLES_DATA = {
    "🕵️": {"name": "Spy",          "color": discord.Color.from_rgb(75, 0, 130)},
    "🎲": {"name": "Domino",       "color": discord.Color.from_rgb(255, 255, 255)},
    "🏃": {"name": "Stumble Guys", "color": discord.Color.from_rgb(255, 105, 180)},
    "🚗": {"name": "GTA V",        "color": discord.Color.from_rgb(0, 150, 60)},
}

ALL_ROLES_DATA = {**FOOTBALL_ROLES_DATA, **GAMING_ROLES_DATA, **GAMING1_ROLES_DATA}

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    if payload.user_id == bot.user.id:
        return
    emoji = str(payload.emoji)
    if emoji in ALL_ROLES_DATA:
        guild = bot.get_guild(payload.guild_id)
        if not guild: return
        member = guild.get_member(payload.user_id)
        if not member or member.bot: return
        
        role_info = ALL_ROLES_DATA[emoji]
        role = discord.utils.get(guild.roles, name=role_info["name"])
        if not role:
            try:
                role = await guild.create_role(name=role_info["name"], color=role_info["color"])
            except:
                return
        try:
            await member.add_roles(role)
        except:
            pass

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    emoji = str(payload.emoji)
    if emoji in ALL_ROLES_DATA:
        guild = bot.get_guild(payload.guild_id)
        if not guild: return
        member = guild.get_member(payload.user_id)
        if not member or member.bot: return
        
        role_info = ALL_ROLES_DATA[emoji]
        role = discord.utils.get(guild.roles, name=role_info["name"])
        if role and role in member.roles:
            try:
                await member.remove_roles(role)
            except:
                pass

async def send_panel(ctx_or_interaction, roles_data, title, description_intro, color, footer_text):
    guild = ctx_or_interaction.guild
    description_lines = []
    for emoji, data in roles_data.items():
        role = discord.utils.get(guild.roles, name=data["name"])
        if not role:
            try:
                role = await guild.create_role(name=data["name"], color=data["color"])
            except:
                pass
        role_mention = role.mention if role else f"@{data['name']}"
        description_lines.append(f"{emoji} **{data['name']}** ➔ {role_mention}")
    
    img_url = parse_image_url(DEFAULT_IMAGE_INPUT)
    embed = discord.Embed(
        title=title,
        description=description_intro + "\n\n" + "\n\n".join(description_lines),
        color=color
    )
    embed.set_image(url=img_url)
    embed.set_footer(text=f"{guild.name} • {footer_text}")
    
    if isinstance(ctx_or_interaction, discord.Interaction):
        await ctx_or_interaction.response.send_message(embed=embed)
        msg = await ctx_or_interaction.original_response()
    else:
        msg = await ctx_or_interaction.send(embed=embed)
    
    for emoji in roles_data.keys():
        try:
            await msg.add_reaction(emoji)
            await asyncio.sleep(0.3)
        except:
            pass

class SelfRolesGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="selfroles", description="أوامر أندية كرة القدم")
    
    @app_commands.command(name="panel", description="لوحة اختيار نادي كرة القدم المفضل")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        await send_panel(interaction, FOOTBALL_ROLES_DATA,
            "⚽ Choose Your Favorite Football Team",
            "اختر ناديك المفضل في البطولة الجزائرية:",
            discord.Color.gold(), "Football Club Roles")

class GamingGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="gaming", description="أوامر رتب الألعاب")
    
    @app_commands.command(name="roles", description="لوحة اختيار رتب الألعاب المفضلة")
    @app_commands.checks.has_permissions(administrator=True)
    async def roles(self, interaction: discord.Interaction):
        await send_panel(interaction, GAMING_ROLES_DATA,
            "🎮 Choose Your Favorite Games",
            "اختر ألعابك المفضلة بالضغط على التفاعلات:",
            discord.Color.purple(), "Gaming Roles")

class Gaming1Group(app_commands.Group):
    def __init__(self):
        super().__init__(name="gaming1", description="أوامر رتب الألعاب الجزء الثاني")
    
    @app_commands.command(name="roles", description="لوحة اختيار رتب الألعاب الجزء الثاني")
    @app_commands.checks.has_permissions(administrator=True)
    async def roles(self, interaction: discord.Interaction):
        await send_panel(interaction, GAMING1_ROLES_DATA,
            "🎲 Choose Your Favorite Games - Part 2",
            "اختر ألعابك المفضلة بالضغط على التفاعلات:",
            discord.Color.orange(), "Gaming Roles 2")

bot.tree.add_command(SelfRolesGroup())
bot.tree.add_command(GamingGroup())
bot.tree.add_command(Gaming1Group())

@bot.command(name="selfroles")
@commands.has_permissions(administrator=True)
async def selfroles_cmd(ctx):
    await send_panel(ctx, FOOTBALL_ROLES_DATA,
        "⚽ Choose Your Favorite Football Team",
        "اختر ناديك المفضل في البطولة الجزائرية:",
        discord.Color.gold(), "Football Club Roles")

@bot.command(name="gaming_roles")
@commands.has_permissions(administrator=True)
async def gaming_roles_cmd(ctx):
    await send_panel(ctx, GAMING_ROLES_DATA,
        "🎮 Choose Your Favorite Games",
        "اختر ألعابك المفضلة بالضغط على التفاعلات:",
        discord.Color.purple(), "Gaming Roles")

@bot.command(name="gaming1_roles")
@commands.has_permissions(administrator=True)
async def gaming1_roles_cmd(ctx):
    await send_panel(ctx, GAMING1_ROLES_DATA,
        "🎲 Choose Your Favorite Games - Part 2",
        "اختر ألعابك المفضلة بالضغط على التفاعلات:",
        discord.Color.orange(), "Gaming Roles 2")


# ╔══════════════════════════════════════════════════════╗
# ║ 🎫 القسم 2: نظام التكت (Tickets)                    ║
# ╚══════════════════════════════════════════════════════╝

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="إغلاق التكت", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 **سيتم إغلاق وحذف التكت خلال 5 ثوانٍ...**")
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Could not delete ticket channel: {e}")

class TicketMainView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, emoji: str):
        guild = interaction.guild
        user = interaction.user
        
        channel_name = f"ticket-{ticket_type.lower()}-{user.name.lower()}"
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        
        if existing_channel:
            return await interaction.response.send_message(f"⚠️ **لديك تكت مفتوح بالفعل!** {existing_channel.mention}", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
        }
        
        category = discord.utils.get(guild.categories, name="TICKETS")
        if not category:
            try:
                category = await guild.create_category("TICKETS")
            except:
                category = None
        
        ticket_channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites
        )
        
        welcome_embed = discord.Embed(
            title=f"{emoji} تكت جديد: {ticket_type}",
            description=(
                f"مرحباً بك {user.mention} في الدعم الفني!\n"
                "يرجى كتابة مشكلتك أو طلبك بالتفصيل وسيتم الرد عليك.\n\n"
                "اضغط على زر **🔒 إغلاق التكت** بالأسفل عند الانتهاء."
            ),
            color=discord.Color.blue()
        )
        welcome_embed.set_footer(text=f"{guild.name} Support System")
        
        await ticket_channel.send(content=f"{user.mention} مرحباً بك!", embed=welcome_embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ **تم إنشاء التكت بنجاح!** {ticket_channel.mention}", ephemeral=True)
    
    @discord.ui.button(label="Help", style=discord.ButtonStyle.success, emoji="💬", custom_id="ticket_help_btn")
    async def help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Help", "💬")
    
    @discord.ui.button(label="Report", style=discord.ButtonStyle.danger, emoji="⛔", custom_id="ticket_report_btn")
    async def report_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Report", "⛔")
    
    @discord.ui.button(label="Manager", style=discord.ButtonStyle.primary, emoji="👔", custom_id="ticket_manager_btn")
    async def manager_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Manager", "👔")
    
    @discord.ui.button(label="Staff Apply", style=discord.ButtonStyle.secondary, emoji="🟢", custom_id="ticket_staff_btn")
    async def staff_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Staff-Apply", "🟢")

class TicketGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="ticket", description="أوامر نظام التكت")
    
    @app_commands.command(name="panel", description="إرسال لوحة التكت والدعم الفني")
    @app_commands.checks.has_permissions(administrator=True)
    async def panel(self, interaction: discord.Interaction):
        img_url = parse_image_url(DEFAULT_IMAGE_INPUT)
        embed = discord.Embed(
            title=f"{interaction.guild.name.upper()} SUPPORT",
            description=(
                "Please choose according to your request and press the button below\n\n"
                "يرجى اختيار سبب التكت والضغط على الزر المناسب\n\n"
                "**Quick Guide:**\n"
                "💬 **Help:** استفسار أو مساعدة\n"
                "⛔ **Report:** الإبلاغ عن شخص\n"
                "👔 **Manager:** التواصل مع الإدارة العليا\n"
                "🟢 **Staff Apply:** الانضمام لفريق الإدارة"
            ),
            color=discord.Color.from_rgb(0, 150, 255)
        )
        embed.set_image(url=img_url)
        embed.set_footer(text=f"{interaction.guild.name} Community Support")
        await interaction.response.send_message(embed=embed, view=TicketMainView())

bot.tree.add_command(TicketGroup())

@bot.command(name="ticket_panel")
@commands.has_permissions(administrator=True)
async def ticket_panel_command(ctx):
    img_url = parse_image_url(DEFAULT_IMAGE_INPUT)
    embed = discord.Embed(
        title=f"{ctx.guild.name.upper()} SUPPORT",
        description=(
            "Please choose according to your request and press the button below\n\n"
            "يرجى اختيار سبب التكت والضغط على الزر المناسب\n\n"
            "**Quick Guide:**\n"
            "💬 **Help:** استفسار أو مساعدة\n"
            "⛔ **Report:** الإبلاغ عن شخص\n"
            "👔 **Manager:** التواصل مع الإدارة العليا\n"
            "🟢 **Staff Apply:** الانضمام لفريق الإدارة"
        ),
        color=discord.Color.from_rgb(0, 150, 255)
    )
    embed.set_image(url=img_url)
    embed.set_footer(text=f"{ctx.guild.name} Community Support")
    await ctx.send(embed=embed, view=TicketMainView())


# ╔══════════════════════════════════════════════════════╗
# ║ 🕵️ القسم 3: لعبة الجاسوس (Spy Game)                ║
# ╚══════════════════════════════════════════════════════╝

class SpyGameSession:
    def __init__(self, narra_user, voice_channel):
        self.narra = narra_user
        self.voice_channel = voice_channel
        self.players = [m for m in voice_channel.members if not m.bot]
        self.spy = None
        self.secret_word = None
        self.original_nicks = {}

active_sessions = {}

class SecretWordModal(discord.ui.Modal, title="اختيار الكلمة السرية للجولة"):
    word_input = discord.ui.TextInput(
        label="اكتب الكلمة السرية للجولة هنا:",
        placeholder="مثال: مطار، سيارة، سينما، هاتف...",
        required=True,
        max_length=50
    )
    
    def __init__(self, session, chosen_spy):
        super().__init__()
        self.session = session
        self.chosen_spy = chosen_spy
    
    async def on_submit(self, interaction: discord.Interaction):
        secret_word = self.word_input.value.strip()
        session = self.session
        session.secret_word = secret_word
        session.spy = self.chosen_spy
        
        await interaction.response.defer(ephemeral=True)
        
        for idx, player in enumerate(session.players):
            session.original_nicks[player.id] = player.nick
            num_name = f"{idx + 1}"
            try:
                await player.edit(nick=num_name)
            except Exception as e:
                print(f"لا يمكن تغيير اسم {player.display_name}: {e}")
        
        for player in session.players:
            if player == session.narra:
                continue
            try:
                if player == session.spy:
                    embed_spy = discord.Embed(
                        title="🕵️ أنت هو الجاسوس! (SPY)",
                        description="أنت الجاسوس! حاول معرفة الكلمة من النقاش دون أن يكشفوك!",
                        color=discord.Color.red()
                    )
                    await player.send(embed=embed_spy)
                else:
                    embed_word = discord.Embed(
                        title="🔍 الكلمة السرية للجولة:",
                        description=f"الكلمة التي اختارها الراوي هي: **{secret_word}**\n\nابحثوا عن الجاسوس بينكم!",
                        color=discord.Color.green()
                    )
                    await player.send(embed=embed_word)
            except Exception as e:
                print(f"Could not send DM to {player}: {e}")
        
        players_list_str = "\n".join([f"🔢 **لاعب {idx+1}:** {p.mention}" for idx, p in enumerate(session.players)])
        
        embed = discord.Embed(
            title="🎮 بدأت لعبة الجاسوس (Spy Game)!",
            description=(
                f"👑 **الراوي (Narra):** {session.narra.mention}\n"
                f"🔊 **الروم الصوتي:** `{session.voice_channel.name}`\n\n"
                f"👥 **اللاعبون بالأرقام ({len(session.players)}):**\n{players_list_str}\n\n"
                "📝 **تم اختيار الجاسوس والكلمة السرية وتغيير الأسماء!**\n"
                "اضغطوا **🛑 إنهاء اللعبة** لإعادة الأسماء الأصلية."
            ),
            color=discord.Color.gold()
        )
        embed.set_image(url=parse_image_url(DEFAULT_IMAGE_INPUT))
        embed.set_footer(text="Spy Game Panel - Active Round")
        
        await interaction.followup.send("✅ تم بدء الجولة!", ephemeral=True)
        await interaction.message.edit(embed=embed, view=SpyGameView())

class SelectSpyDropdown(discord.ui.Select):
    def __init__(self, session):
        options = [
            discord.SelectOption(
                label=f"لاعب: {p.display_name}",
                value=str(p.id),
                emoji="🕵️"
            ) for p in session.players
        ]
        super().__init__(
            placeholder="اختر اللاعب الذي سيكون الجاسوس (SPY)...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.session = session
    
    async def callback(self, interaction: discord.Interaction):
        spy_id = int(self.values[0])
        chosen_spy = interaction.guild.get_member(spy_id)
        await interaction.response.send_modal(SecretWordModal(self.session, chosen_spy))

class SelectSpyView(discord.ui.View):
    def __init__(self, session):
        super().__init__(timeout=60)
        self.add_item(SelectSpyDropdown(session))

class SpyGameView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="بدء اللعبة (Narra)", style=discord.ButtonStyle.success, emoji="🚀", custom_id="spy_narra_start_btn_v3")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = interaction.user
        
        if not user.voice or not user.voice.channel:
            return await interaction.response.send_message("⚠️ يجب أن تكون داخل روم صوتي لبدء اللعبة!", ephemeral=True)
        
        voice_channel = user.voice.channel
        session = SpyGameSession(user, voice_channel)
        
        if len(session.players) < 2:
            return await interaction.response.send_message(f"⚠️ يجب أن يكون هناك لاعبين على الأقل في `{voice_channel.name}`!", ephemeral=True)
        
        active_sessions[interaction.channel_id] = session
        
        view = SelectSpyView(session)
        await interaction.response.send_message("🕵️ **اختر الجاسوس (SPY) للجولة الحالية:**", view=view, ephemeral=True)
    
    @discord.ui.button(label="إنهاء اللعبة", style=discord.ButtonStyle.danger, emoji="🛑", custom_id="spy_end_game_btn_v3")
    async def end_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel_id = interaction.channel_id
        session = active_sessions.get(channel_id, None)
        
        if not session:
            return await interaction.response.send_message("⚠️ لا توجد لعبة جارية حالياً!", ephemeral=True)
        
        await interaction.response.defer()
        
        restored_count = 0
        for player_id, old_nick in session.original_nicks.items():
            member = interaction.guild.get_member(player_id)
            if member:
                try:
                    await member.edit(nick=old_nick)
                    restored_count += 1
                    await asyncio.sleep(0.15)
                except Exception as e:
                    print(f"Could not restore nick for {member}: {e}")
        
        del active_sessions[channel_id]
        
        embed = discord.Embed(
            title="🛑 تم إنهاء لعبة الجاسوس",
            description=(
                f"تم إنهاء الجولة بواسطة {interaction.user.mention}.\n"
                f"✅ **تمت إعادة أسماء السيرفر الأصلية لـ {restored_count} لاعب.**\n\n"
                "يمكن للراوي Narra بدء جولة جديدة!"
            ),
            color=discord.Color.red()
        )
        embed.set_image(url=parse_image_url(DEFAULT_IMAGE_INPUT))
        embed.set_footer(text="Spy Game Panel - Game Ended")
        
        await interaction.message.edit(embed=embed, view=self)
        await interaction.followup.send(embed=embed)

class SpyGroup(app_commands.Group):
    def __init__(self):
        super().__init__(name="spy", description="أوامر لعبة الجاسوس")
    
    @app_commands.command(name="game", description="فتح لوحة لعبة الجاسوس بالأرقام والراوي")
    async def game(self, interaction: discord.Interaction):
        img_url = parse_image_url(DEFAULT_IMAGE_INPUT)
        embed = discord.Embed(
            title="🕵️ لوحة لعبة الجاسوس (Spy Game)",
            description=(
                "ادخل إلى الروم الصوتي مع أصدقائك، ثم اضغط على **🚀 بدء اللعبة (Narra)** لاختيار الجاسوس والكلمة السرية!\n\n"
                "🛑 **اضغط زر إنهاء اللعبة بعد الانتهاء لإعادة الأسماء الأصلية.**"
            ),
            color=discord.Color.dark_embed()
        )
        embed.set_image(url=img_url)
        embed.set_footer(text="Spy Game Panel - persistent")
        await interaction.response.send_message(embed=embed, view=SpyGameView())

bot.tree.add_command(SpyGroup())

@bot.command(name="spy_game")
async def spy_game_command(ctx):
    img_url = parse_image_url(DEFAULT_IMAGE_INPUT)
    embed = discord.Embed(
        title="🕵️ لوحة لعبة الجاسوس (Spy Game)",
        description=(
            "ادخل إلى الروم الصوتي مع أصدقائك، ثم اضغط على **🚀 بدء اللعبة (Narra)** لاختيار الجاسوس والكلمة السرية!\n\n"
            "🛑 **اضغط زر إنهاء اللعبة بعد الانتهاء لإعادة الأسماء الأصلية.**"
        ),
        color=discord.Color.dark_embed()
    )
    embed.set_image(url=img_url)
    embed.set_footer(text="Spy Game Panel - persistent")
    await ctx.send(embed=embed, view=SpyGameView())


# ╔══════════════════════════════════════════════════════╗
# ║ 🛡️ القسم 4: الإشراف والحماية (Moderation)          ║
# ╚══════════════════════════════════════════════════════╝

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="📋 أوامر البوت الجامع",
        description=f"البادئة: `!`",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="🏷️ الرتب",
        value="`!selfroles` `!gaming_roles` `!gaming1_roles`",
        inline=False
    )
    embed.add_field(
        name="🎫 التكت",
        value="`!ticket_panel`",
        inline=False
    )
    embed.add_field(
        name="🕵️ الجاسوس",
        value="`!spy_game`",
        inline=False
    )
    embed.add_field(
        name="🔨 إشراف",
        value="`!ban` `!kick` `!mute` `!warn` `!purge` `!lock` `!unlock`",
        inline=False
    )
    embed.add_field(
        name="🔊 صوت",
        value="`!join` `!leave` `!muteall` `!unmuteall`",
        inline=False
    )
    embed.add_field(
        name="📊 معلومات",
        value="`!userinfo` `!serverinfo` `!avatar` `!ping`",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None, *, reason="بدون سبب"):
    if not member:
        return await ctx.send("❌ `!ban @user [السبب]`")
    if member == ctx.author:
        return await ctx.send("❌ ما تقدر تحظر نفسك!")
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ رتبته أعلى منك!")
    try:
        await member.ban(reason=f"[{ctx.author}] {reason}")
        embed = discord.Embed(title="🔨 تم الحظر", description=f"**العضو:** {member.mention}\n**السبب:** {reason}", color=discord.Color.red())
        await ctx.send(embed=embed)
    except:
        await ctx.send("❌ ما عندي صلاحية!")

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int = None):
    if not user_id:
        return await ctx.send("❌ `!unban ID`")
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)
        await ctx.send(f"✅ تم رفع الحظر عن **{user.name}**")
    except:
        await ctx.send("❌ ما لقيت العضو!")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member = None, *, reason="بدون سبب"):
    if not member:
        return await ctx.send("❌ `!kick @user`")
    if member.top_role >= ctx.author.top_role:
        return await ctx.send("❌ رتبته أعلى منك!")
    await member.kick(reason=f"[{ctx.author}] {reason}")
    embed = discord.Embed(title="👢 تم الطرد", description=f"**{member.mention}** - {reason}", color=discord.Color.orange())
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member = None, *, reason="بدون سبب"):
    if not member:
        return await ctx.send("❌ `!mute @user`")
    try:
        await member.edit(mute=True)
        await ctx.send(f"🔇 تم كتم {member.mention}")
    except:
        await ctx.send("❌ ما عندي صلاحية!")

@bot.command()
async def unmute(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("❌ `!unmute @user`")
    try:
        await member.edit(mute=False)
        await ctx.send(f"🔊 رفع كتم {member.mention}")
    except:
        await ctx.send("❌ ما عندي صلاحية!")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member = None, *, reason="بدون سبب"):
    if not member:
        return await ctx.send("❌ `!warn @user [السبب]`")
    warns = load_json(WARNS_FILE)
    warns.setdefault(str(ctx.guild.id), {}).setdefault(str(member.id), [])
    warns[str(ctx.guild.id)][str(member.id)].append({
        "reason": reason,
        "mod": ctx.author.id,
        "time": datetime.now().isoformat()
    })
    save_json(WARNS_FILE, warns)
    count = len(warns[str(ctx.guild.id)][str(member.id)])
    await ctx.send(f"⚠️ {member.mention} - تحذير #{count}\nالسبب: {reason}")

@bot.command()
async def warns(ctx, member: discord.Member = None):
    if not member:
        return await ctx.send("❌ `!warns @user`")
    warns = load_json(WARNS_FILE)
    user_warns = warns.get(str(ctx.guild.id), {}).get(str(member.id), [])
    if not user_warns:
        return await ctx.send(f"✅ {member.mention} نظيف!")
    embed = discord.Embed(title=f"⚠️ تحذيرات {member.display_name}", color=discord.Color.orange())
    for i, w in enumerate(user_warns[-5:], 1):
        embed.add_field(name=f"#{i}", value=f"**السبب:** {w['reason']}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def clearwarns(ctx, member: discord.Member):
    warns = load_json(WARNS_FILE)
    if str(ctx.guild.id) in warns and str(member.id) in warns[str(ctx.guild.id)]:
        del warns[str(ctx.guild.id)][str(member.id)]
        save_json(WARNS_FILE, warns)
    await ctx.send(f"🗑️ تم مسح تحذيرات {member.mention}")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = None):
    if not amount:
        return await ctx.send("❌ `!purge [عدد]`")
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ تم مسح {len(deleted)-1} رسالة")
    await asyncio.sleep(3)
    await msg.delete()

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 تم قفل القناة")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
    await ctx.send("🔓 تم فتح القناة")

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("❌ ادخل روم صوتي!")
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()
    await ctx.send(f"🔊 دخلت {channel.name}")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("👋 طلعت!")
    else:
        await ctx.send("❌ مو متصل!")

@bot.command()
@commands.has_permissions(mute_members=True)
async def muteall(ctx):
    if not ctx.voice_client:
        return await ctx.send("❌ البوت مو بصوت!")
    count = 0
    for m in ctx.voice_client.channel.members:
        if not m.bot and m.top_role < ctx.guild.me.top_role:
            try:
                await m.edit(mute=True, deafen=True)
                count += 1
            except:
                pass
    await ctx.send(f"🔇 كتم {count} شخص")

@bot.command()
@commands.has_permissions(mute_members=True)
async def unmuteall(ctx):
    if not ctx.voice_client:
        return await ctx.send("❌ البوت مو بصوت!")
    count = 0
    for m in ctx.voice_client.channel.members:
        if not m.bot:
            try:
                await m.edit(mute=False, deafen=False)
                count += 1
            except:
                pass
    await ctx.send(f"🔊 رفع كتم {count} شخص")

@bot.command()
async def ping(ctx):
    ms = round(bot.latency * 1000)
    await ctx.send(f"🏓 **{ms}ms** ⚡")

@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member.display_name}", color=member.color)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=f"`{member.id}`", inline=True)
    embed.add_field(name="📅 ديسكورد", value=member.created_at.strftime("%Y-%m-%d"), inline=True)
    embed.add_field(name="📅 السيرفر", value=member.joined_at.strftime("%Y-%m-%d"), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    g = ctx.guild
    embed = discord.Embed(title=f"📊 {g.name}", color=discord.Color.blue())
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="👑 المالك", value=f"<@{g.owner_id}>", inline=True)
    embed.add_field(name="👥 الأعضاء", value=g.member_count, inline=True)
    embed.add_field(name="💬 القنوات", value=len(g.text_channels) + len(g.voice_channels), inline=True)
    await ctx.send(embed=embed)

@bot.command()
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"🖼️ {member.display_name}")
    embed.set_image(url=member.display_avatar.url)
    await ctx.send(embed=embed)


# ============ معالجة الأخطاء ============
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ ما عندك صلاحية!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ ناقص معطيات! `!help`")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ خطأ: `{error}`")


# ============ 🚀 عند التشغيل ============
@bot.event
async def on_ready():
    bot.add_view(TicketMainView())
    bot.add_view(CloseTicketView())
    bot.add_view(SpyGameView())
    
    for guild in bot.guilds:
        try:
            bot.tree.copy_global_to(guild=guild)
            await bot.tree.sync(guild=guild)
        except:
            pass
    
    print("=" * 50)
    print(f"✅ البوت الجامع شغال!")
    print(f"📡 {bot.user}")
    print(f"🌐 {len(bot.guilds)} سيرفر")
    print(f"⚡ {len(bot.commands)} أمر")
    print("=" * 50)


# ============ تشغيل ============
if __name__ == "__main__":
    try:
        if BOT_TOKEN == "PUT_YOUR_TOKEN_HERE" or BOT_TOKEN.strip() == "":
            print("\n⚠️ ضع التوكن!")
            input("Enter...")
        else:
            bot.run(BOT_TOKEN)
    except Exception as e:
        traceback.print_exc()
    import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
