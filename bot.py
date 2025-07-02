from keep_alive import keep_alive
keep_alive()

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# IDs dos cargos principais
ROLE_ESPADACHIM_ID = 1386796444043968663
ROLE_DEMONIO_ID = 1386796534930341929
ROLE_BBZ_ID = 1389812928282230887

# Ranks de cada classe
RANKS_ESPADACHIM = [
    1386432952895930529, 1386433323458367690, 1386433612731383918,
    1386433995897569280, 1386434170598981854, 1386434320373121094,
    1386434658262192330, 1386435127969583155, 1386435836014235709,
    1386436074288582736, 1386792545354256434
]

RANKS_DEMONIO = [
    1386436111186006136, 1386436334469644441, 1386436473263231117,
    1386436659243126895, 1386436690192896012, 1386436732538454257,
    1386435911604244480, 1386437079692742777, 1386437171849854976,
    1386437255077433514, 1386437364724924516, 1386437466122227942
]

RANKS_BBZ = [
    1390100232364359811, 1390100316678262854, 1390100414136844430,
    1390100468344164504, 1390100525722370058, 1390100637894705304
]

LOG_CHANNEL_ID = 1383989829590585404

@bot.event
async def on_ready():
    print(f'✅ Bot conectado como {bot.user.name}')

@bot.event
async def on_member_update(before, after):
    added_roles = set(after.roles) - set(before.roles)
    current_role_ids = [r.id for r in after.roles]

    # Classes
    is_espadachim = ROLE_ESPADACHIM_ID in current_role_ids
    is_demonio = ROLE_DEMONIO_ID in current_role_ids
    is_bbz = ROLE_BBZ_ID in current_role_ids

    class_roles = [ROLE_ESPADACHIM_ID, ROLE_DEMONIO_ID, ROLE_BBZ_ID]
    owned_classes = [r for r in after.roles if r.id in class_roles]

    # ❌ Impede múltiplas classes ao mesmo tempo
    if len(owned_classes) > 1:
        for r in owned_classes[1:]:
            try:
                await after.remove_roles(r, reason="Conflito de múltiplas classes")
                await after.send(f"⚠️ Você não pode ter múltiplas classes. O cargo `{r.name}` foi removido.")
                await log_event(after, r.name, "removido por conflito de classes")
            except discord.Forbidden:
                print(f"⚠️ Sem permissão para remover {r.name} de {after.display_name}")
            except Exception as e:
                print(f"❌ Erro ao remover classe em conflito: {e}")
        return

    # ♻️ Conversão de ranks (Espadachim ↔ Demônio)
    if is_demonio:
        for role in added_roles:
            if role.id in RANKS_ESPADACHIM:
                index = RANKS_ESPADACHIM.index(role.id)
                rank_demonio_id = RANKS_DEMONIO[index]
                rank_demonio = discord.utils.get(after.guild.roles, id=rank_demonio_id)
                try:
                    await after.remove_roles(role, reason="Conversão para Demônio")
                    await after.add_roles(rank_demonio, reason="Conversão automática Espadachim → Demônio")
                    await after.send(
                        f"♻️ Você recebeu `{rank_demonio.name}` pois é da classe **Demônio**.\n"
                        f"O cargo `{role.name}` foi removido."
                    )
                    await log_event(after, role.name, f"removido (conversão para {rank_demonio.name})")
                except Exception as e:
                    print(f"❌ Erro na conversão: {e}")
                return

    if is_espadachim:
        for role in added_roles:
            if role.id in RANKS_DEMONIO:
                index = RANKS_DEMONIO.index(role.id)
                rank_espadachim_id = RANKS_ESPADACHIM[index]
                rank_espadachim = discord.utils.get(after.guild.roles, id=rank_espadachim_id)
                try:
                    await after.remove_roles(role, reason="Conversão para Espadachim")
                    await after.add_roles(rank_espadachim, reason="Conversão automática Demônio → Espadachim")
                    await after.send(
                        f"♻️ Você recebeu `{rank_espadachim.name}` pois é da classe **Espadachim**.\n"
                        f"O cargo `{role.name}` foi removido."
                    )
                    await log_event(after, role.name, f"removido (conversão para {rank_espadachim.name})")
                except Exception as e:
                    print(f"❌ Erro na conversão: {e}")
                return

    # ❌ Bloqueia ranks fora da classe correspondente
    for role in added_roles:
        if role.id in RANKS_ESPADACHIM and not is_espadachim:
            await remove_incompatible_role(after, role, "Espadachim")
        elif role.id in RANKS_DEMONIO and not is_demonio:
            await remove_incompatible_role(after, role, "Demônio")
        elif role.id in RANKS_BBZ and not is_bbz:
            await remove_incompatible_role(after, role, "BBZ")

async def remove_incompatible_role(member, role, required_class):
    try:
        await member.remove_roles(role, reason=f"Classe incorreta (não é {required_class})")
        await member.send(f"❌ Você não pode ter o cargo `{role.name}` sem ser da classe `{required_class}`.\nO cargo foi removido automaticamente.")
        await log_event(member, role.name, f"removido por não ser {required_class}")
    except discord.Forbidden:
        print(f"⚠️ Sem permissão para remover {role.name} de {member.display_name}")
    except discord.HTTPException as e:
        print(f"❌ Erro ao remover cargo: {e}")

async def log_event(member, role_name, reason):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"📢 **{member.display_name}** teve o cargo `{role_name}` **removido** — {reason}.")

bot.run(os.environ['TOKEN'])
