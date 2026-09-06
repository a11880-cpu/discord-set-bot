import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Configurar o bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# IDs dos canais
CANAL_SET_ID = int(os.getenv("CANAL_SET_ID"))
CANAL_ACEITO_ID = int(os.getenv("CANAL_ACEITO_ID"))
CANAL_NEGADO_ID = int(os.getenv("CANAL_NEGADO_ID"))

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} comando(s) sincronizado(s)")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

@bot.tree.command(name="set", description="Submeter um novo set")
@app_commands.describe(descricao="Descrição do seu set")
async def set_command(interaction: discord.Interaction, descricao: str):
    """Comando para submeter um set"""
    
    # Criar embed
    embed = discord.Embed(
        title="📝 Novo Set Submetido",
        description=descricao,
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Autor", value=interaction.user.mention, inline=False)
    embed.set_footer(text=f"ID do Usuário: {interaction.user.id}")
    
    # Enviar para canal de sets pendentes
    canal = bot.get_channel(CANAL_SET_ID)
    if canal:
        # Criar botões
        view = discord.ui.View()
        view.add_item(BotaoAceitar())
        view.add_item(BotaoNegar())
        
        mensagem = await canal.send(embed=embed, view=view)
        await interaction.response.send_message(
            f"✅ Seu set foi enviado para análise! ID: {mensagem.id}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ Erro: Canal não encontrado!",
            ephemeral=True
        )

class BotaoAceitar(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.green, label="✅ Aceitar", emoji="✅")
    
    async def callback(self, interaction: discord.Interaction):
        # Copiar a mensagem para o canal aceito
        embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if embed:
            embed.color = discord.Color.green()
            embed.title = "✅ Set Aceito"
            
            canal_aceito = interaction.client.get_channel(CANAL_ACEITO_ID)
            if canal_aceito:
                await canal_aceito.send(embed=embed)
                await interaction.message.delete()
                await interaction.response.send_message("✅ Set aceito com sucesso!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Canal aceito não encontrado!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erro ao processar set!", ephemeral=True)

class BotaoNegar(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.red, label="❌ Negar", emoji="❌")
    
    async def callback(self, interaction: discord.Interaction):
        # Copiar a mensagem para o canal negado
        embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if embed:
            embed.color = discord.Color.red()
            embed.title = "❌ Set Negado"
            
            canal_negado = interaction.client.get_channel(CANAL_NEGADO_ID)
            if canal_negado:
                await canal_negado.send(embed=embed)
                await interaction.message.delete()
                await interaction.response.send_message("❌ Set negado com sucesso!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Canal negado não encontrado!", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Erro ao processar set!", ephemeral=True)

# Conectar o bot
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ Erro: Token não encontrado no arquivo .env!")
