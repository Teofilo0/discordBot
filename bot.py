from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import os


intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs dos cargos principais
ROLE_ESPADACHIM_ID = 1386796444043968663
ROLE_DEMONIO_ID = 1386796534930341929

# Cargos de ranking - Espadachim
RANKS_ESPADACHIM = [
    1386432952895930529,
    1386433323458367690,
    1386433612731383918,
    1386433995897569280,
    1386434170598981854,
    1386434320373121094,
    1386434658262192330,
    1386435127969583155,
    1386435836014235709,
    1386436074288582736,
    1386792545354256434
]

# Cargos de ranking - Demônio
RANKS_DEMONIO = [
    1386436111186006136,
    1386436334469644441,
    1386436473263231117,
    1386436659243126895,
    1386436690192896012,
    1386436732538454257,
    1386435911604244480,
    1386437079692742777,
    1386437171849854976,
    1386437255077433514,
    1386437364724924516,
    1386437466122227942
]


LOG_CHANNEL_ID = 1383989829590585404

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')

@bot.event
async def on_member_update(before, after):
    added_roles = set(after.roles) - set(before.roles)
    current_role_ids = [r.id for r in after.roles]

    is_espadachim = ROLE_ESPADACHIM_ID in current_role_ids
    is_demonio = ROLE_DEMONIO_ID in current_role_ids

    if is_demonio:
        for role in added_roles:
            if role.id in RANKS_ESPADACHIM:
                index = RANKS_ESPADACHIM.index(role.id)
                rank_demonio_id = RANKS_DEMONIO[index]
                rank_demonio = discord.utils.get(after.guild.roles, id=rank_demonio_id)

                try:
                    await after.remove_roles(role, reason="Conversão automática para rank de Demônio")
                    await after.add_roles(rank_demonio, reason="Conversão automática de rank Espadachim → Demônio")
                    await after.send(
                        f"♻️ Você recebeu o cargo `{rank_demonio.name}` pois pertence à classe **Demônio**.\n"
                        f"O cargo `{role.name}` foi removido."
                    )
                    await log_event(after, role.name, f"removido (conversão para {rank_demonio.name})")
                except discord.Forbidden:
                    print(f"⚠️ Permissão insuficiente para modificar cargos de {after.display_name}")
                except Exception as e:
                    print(f"❌ Erro na conversão de cargo: {e}")
                return 
    if is_espadachim:
        for role in added_roles:
            if role.id in RANKS_DEMONIO:
                index = RANKS_DEMONIO.index(role.id)
                rank_espadachim_id = RANKS_ESPADACHIM[index]
                rank_espadachim = discord.utils.get(after.guild.roles, id=rank_espadachim_id)

                try:
                    await after.remove_roles(role, reason="Conversão automática para rank de Espadachim")
                    await after.add_roles(rank_espadachim, reason="Conversão automática de rank Demônio → Espadachim")
                    await after.send(
                        f"♻️ Você recebeu o cargo `{rank_espadachim.name}` pois pertence à classe **Espadachim**.\n"
                        f"O cargo `{role.name}` foi removido."
                    )
                    await log_event(after, role.name, f"removido (conversão para {rank_espadachim.name})")
                except discord.Forbidden:
                    print(f"⚠️ Permissão insuficiente para modificar cargos de {after.display_name}")
                except Exception as e:
                    print(f"❌ Erro na conversão de cargo: {e}")
                return
    if is_espadachim and is_demonio:
        cargo_dem = discord.utils.get(after.guild.roles, id=ROLE_DEMONIO_ID)
        if cargo_dem:
            await after.remove_roles(cargo_dem, reason="Conflito de classes")
            await after.send("⚠️ Você não pode ter Espadachim **e** Demônio ao mesmo tempo. O cargo `Demônio` foi removido.")
            await log_event(after, cargo_dem.name, "removido por conflito de classes")
        return

    for role in added_roles:
        if role.id in RANKS_ESPADACHIM and not is_espadachim:
            await remove_incompatible_role(after, role, "Espadachim")
        elif role.id in RANKS_DEMONIO and not is_demonio:
            await remove_incompatible_role(after, role, "Demônio")



async def remove_incompatible_role(member, role, required_class):
    try:
        await member.remove_roles(role, reason=f"Classe incorreta (não é {required_class})")
        await member.send(f"❌ Você não pode ter o cargo `{role.name}` sem ser da classe `{required_class}`.\nO cargo foi removido automaticamente.")
        await log_event(member, role.name, f"removido por não ser {required_class}")
    except discord.Forbidden:
        print(f"⚠️ Permissão insuficiente para remover {role.name} de {member.display_name}")
    except discord.HTTPException as e:
        print(f"Erro ao remover cargo: {e}")


async def log_event(member, role_name, reason):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            f"📢 **{member.display_name}** teve o cargo `{role_name}` **removido** — {reason}."
        )
bot.run(os.environ['TOKEN'])


