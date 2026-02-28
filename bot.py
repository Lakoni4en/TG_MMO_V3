#!/usr/bin/env python3
"""
ABYSS CHRONICLES - Telegram MMORPG Bot
All-in-one single file. Deploy to Railway by setting BOT_TOKEN env variable.
Promo code: Premak4 → 2x EXP for 24 hours
"""

import os
import sqlite3
import json
import time
import random
import logging
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, JobQueue
)
from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DATABASE_URL = os.getenv("DATABASE_URL", "game.db")

PROMO_CODES = {
    "Premak4": {
        "type": "exp_boost",
        "multiplier": 2.0,
        "duration_hours": 24,
        "description": "200% EXP for 24 hours!"
    }
}

MAX_LEVEL = 100
HARDCORE_EXP_MULTIPLIER = 2.5
BASE_EXP_PER_LEVEL = 100

CLASSES = {
    "warrior": {
        "name": "⚔️ Warrior",
        "description": "Strong melee fighter with high HP",
        "hp_bonus": 50, "atk_bonus": 10, "def_bonus": 15, "spd_bonus": 0, "mana_bonus": 0,
        "skills_start": ["power_strike", "shield_bash"]
    },
    "mage": {
        "name": "🔮 Mage",
        "description": "Master of spells with high damage",
        "hp_bonus": 0, "atk_bonus": 25, "def_bonus": 0, "spd_bonus": 5, "mana_bonus": 50,
        "skills_start": ["fireball", "mana_shield"]
    },
    "rogue": {
        "name": "🗡️ Rogue",
        "description": "Fast assassin with critical hits",
        "hp_bonus": 10, "atk_bonus": 15, "def_bonus": 5, "spd_bonus": 20, "mana_bonus": 10,
        "skills_start": ["backstab", "evasion"]
    },
    "paladin": {
        "name": "🛡️ Paladin",
        "description": "Holy warrior who can heal",
        "hp_bonus": 30, "atk_bonus": 8, "def_bonus": 20, "spd_bonus": 0, "mana_bonus": 20,
        "skills_start": ["holy_strike", "heal"]
    },
    "ranger": {
        "name": "🏹 Ranger",
        "description": "Swift archer with poison attacks",
        "hp_bonus": 15, "atk_bonus": 20, "def_bonus": 5, "spd_bonus": 10, "mana_bonus": 15,
        "skills_start": ["arrow_shot", "poison_arrow"]
    },
    "necromancer": {
        "name": "💀 Necromancer",
        "description": "Dark mage who controls undead",
        "hp_bonus": 5, "atk_bonus": 20, "def_bonus": 0, "spd_bonus": 0, "mana_bonus": 40,
        "skills_start": ["death_bolt", "raise_dead"]
    }
}

RACES = {
    "human": {
        "name": "👤 Human",
        "description": "+10% to all stats, bonus skill point",
        "hp_mult": 1.1, "atk_mult": 1.1, "def_mult": 1.1, "exp_mult": 1.15, "bonus_skill_points": 1
    },
    "elf": {
        "name": "🧝 Elf",
        "description": "+25% speed and mana, bonus dodge",
        "hp_mult": 0.9, "atk_mult": 1.15, "def_mult": 0.95, "exp_mult": 1.1, "bonus_skill_points": 0
    },
    "dwarf": {
        "name": "⛏️ Dwarf",
        "description": "+30% HP and defense, crafting bonus",
        "hp_mult": 1.3, "atk_mult": 0.9, "def_mult": 1.3, "exp_mult": 1.0, "bonus_skill_points": 0
    },
    "orc": {
        "name": "👹 Orc",
        "description": "+40% attack, double rage damage",
        "hp_mult": 1.2, "atk_mult": 1.4, "def_mult": 0.85, "exp_mult": 1.0, "bonus_skill_points": 0
    },
    "undead": {
        "name": "💀 Undead",
        "description": "Immune to poison, +20% dark magic",
        "hp_mult": 1.0, "atk_mult": 1.2, "def_mult": 1.0, "exp_mult": 1.2, "bonus_skill_points": 0
    },
    "demon": {
        "name": "😈 Demon",
        "description": "+30% fire damage, life steal",
        "hp_mult": 1.1, "atk_mult": 1.3, "def_mult": 0.9, "exp_mult": 1.1, "bonus_skill_points": 0
    }
}

DIFFICULTY = {
    "endless": {
        "name": "♾️ Endless Lives",
        "description": "Respawn on death, normal progression",
        "exp_mult": 1.0, "drop_mult": 1.0, "hardcore": False
    },
    "hardcore": {
        "name": "💀 Hardcore",
        "description": "1 life only! +150% EXP. Reach LVL 100 → Immortal title!",
        "exp_mult": 2.5, "drop_mult": 2.0, "hardcore": True
    }
}

# ═══════════════════════════════════════════════════════════
# SKILLS
# ═══════════════════════════════════════════════════════════

SKILLS = {
    # WARRIOR
    "power_strike": {"name": "⚔️ Power Strike", "description": "Deal 150% ATK damage",
                     "type": "active", "class": "warrior", "max_level": 5, "mana_cost": 10,
                     "damage_mult": [1.5, 1.7, 2.0, 2.3, 2.6], "requires": [], "hidden": False, "sp_cost": 1},
    "shield_bash": {"name": "🛡️ Shield Bash", "description": "Stun enemy for 1 turn",
                    "type": "active", "class": "warrior", "max_level": 3, "mana_cost": 15,
                    "stun_chance": [0.3, 0.5, 0.75], "requires": ["power_strike"], "hidden": False, "sp_cost": 1},
    "berserker_rage": {"name": "😡 Berserker Rage", "description": "+50% ATK, -20% DEF for 3 turns",
                       "type": "active", "class": "warrior", "max_level": 3, "mana_cost": 20,
                       "requires": ["power_strike"], "hidden": False, "sp_cost": 2},
    "war_cry": {"name": "📣 War Cry", "description": "Boost all stats by 20% for 2 turns",
                "type": "active", "class": "warrior", "max_level": 3, "mana_cost": 25,
                "requires": ["shield_bash"], "hidden": False, "sp_cost": 2},
    "whirlwind": {"name": "🌀 Whirlwind", "description": "Spin and deal 120% ATK",
                  "type": "active", "class": "warrior", "max_level": 5, "mana_cost": 30,
                  "requires": ["berserker_rage", "war_cry"], "hidden": False, "sp_cost": 3},
    "iron_skin": {"name": "🦾 Iron Skin", "description": "Passive +15% DEF per level",
                  "type": "passive", "class": "warrior", "max_level": 5,
                  "def_bonus": [0.15, 0.3, 0.45, 0.6, 0.75], "requires": ["shield_bash"], "hidden": False, "sp_cost": 2},
    "last_stand": {"name": "💪 Last Stand", "description": "Below 20% HP, ATK doubles",
                   "type": "passive", "class": "warrior", "max_level": 3,
                   "requires": ["whirlwind"], "hidden": False, "sp_cost": 3},
    "blade_storm": {"name": "⚡ Blade Storm", "description": "5 rapid strikes, 80% ATK each",
                    "type": "active", "class": "warrior", "max_level": 3, "mana_cost": 40,
                    "requires": ["whirlwind"], "hidden": False, "sp_cost": 4},
    "titan_strike": {"name": "🏔️ Titan Strike", "description": "Massive 400% ATK damage (LVL 50+)",
                     "type": "active", "class": "warrior", "max_level": 1, "mana_cost": 80, "level_req": 50,
                     "requires": ["blade_storm", "last_stand"], "hidden": True, "sp_cost": 5},
    "unbreakable": {"name": "🔩 Unbreakable", "description": "Passive: 10% chance to ignore damage",
                    "type": "passive", "class": "warrior", "max_level": 3,
                    "requires": ["iron_skin"], "hidden": False, "sp_cost": 3},

    # MAGE
    "fireball": {"name": "🔥 Fireball", "description": "Deal 180% ATK fire damage",
                 "type": "active", "class": "mage", "max_level": 5, "mana_cost": 15,
                 "damage_mult": [1.8, 2.1, 2.4, 2.8, 3.2], "requires": [], "hidden": False, "sp_cost": 1},
    "mana_shield": {"name": "🔵 Mana Shield", "description": "Absorb damage using mana",
                    "type": "active", "class": "mage", "max_level": 3, "mana_cost": 20,
                    "requires": [], "hidden": False, "sp_cost": 1},
    "ice_lance": {"name": "❄️ Ice Lance", "description": "Pierce and slow enemy, 160% ATK",
                  "type": "active", "class": "mage", "max_level": 5, "mana_cost": 18,
                  "requires": ["fireball"], "hidden": False, "sp_cost": 2},
    "thunder_bolt": {"name": "⚡ Thunder Bolt", "description": "Chain lightning, 140% ATK x3",
                     "type": "active", "class": "mage", "max_level": 5, "mana_cost": 25,
                     "requires": ["mana_shield"], "hidden": False, "sp_cost": 2},
    "mana_regen": {"name": "✨ Mana Regen", "description": "Passive +10% mana regen per level",
                   "type": "passive", "class": "mage", "max_level": 5,
                   "requires": ["mana_shield"], "hidden": False, "sp_cost": 1},
    "arcane_surge": {"name": "💜 Arcane Surge", "description": "+40% spell power for 3 turns",
                     "type": "active", "class": "mage", "max_level": 3, "mana_cost": 30,
                     "requires": ["ice_lance", "thunder_bolt"], "hidden": False, "sp_cost": 3},
    "frost_nova": {"name": "❄️ Frost Nova", "description": "Freeze enemy for 2 turns",
                   "type": "active", "class": "mage", "max_level": 3, "mana_cost": 35,
                   "requires": ["ice_lance"], "hidden": False, "sp_cost": 3},
    "meteor": {"name": "☄️ Meteor", "description": "Call a meteor, 500% ATK fire dmg",
               "type": "active", "class": "mage", "max_level": 1, "mana_cost": 80, "level_req": 40,
               "requires": ["arcane_surge"], "hidden": True, "sp_cost": 5},
    "time_warp": {"name": "⏱️ Time Warp", "description": "Take 2 actions this turn",
                  "type": "active", "class": "mage", "max_level": 1, "mana_cost": 60, "level_req": 60,
                  "requires": ["arcane_surge"], "hidden": True, "sp_cost": 5},
    "spell_echo": {"name": "🔄 Spell Echo", "description": "20% chance to cast spell twice",
                   "type": "passive", "class": "mage", "max_level": 3,
                   "requires": ["arcane_surge"], "hidden": False, "sp_cost": 4},

    # ROGUE
    "backstab": {"name": "🗡️ Backstab", "description": "200% ATK if enemy stunned",
                 "type": "active", "class": "rogue", "max_level": 5, "mana_cost": 10,
                 "damage_mult": [2.0, 2.5, 3.0, 3.5, 4.0], "requires": [], "hidden": False, "sp_cost": 1},
    "evasion": {"name": "💨 Evasion", "description": "Dodge next 2 attacks",
                "type": "active", "class": "rogue", "max_level": 3, "mana_cost": 15,
                "requires": [], "hidden": False, "sp_cost": 1},
    "poison_blade": {"name": "🐍 Poison Blade", "description": "Coat blade in poison, DOT 3 turns",
                     "type": "active", "class": "rogue", "max_level": 5, "mana_cost": 12,
                     "requires": ["backstab"], "hidden": False, "sp_cost": 2},
    "smoke_bomb": {"name": "💣 Smoke Bomb", "description": "Reduce enemy accuracy by 50%",
                   "type": "active", "class": "rogue", "max_level": 3, "mana_cost": 20,
                   "requires": ["evasion"], "hidden": False, "sp_cost": 2},
    "shadow_step": {"name": "🌑 Shadow Step", "description": "Teleport behind enemy, +100% crit",
                    "type": "active", "class": "rogue", "max_level": 3, "mana_cost": 25,
                    "requires": ["poison_blade", "smoke_bomb"], "hidden": False, "sp_cost": 3},
    "crit_mastery": {"name": "🎯 Crit Mastery", "description": "Passive +10% crit chance per level",
                     "type": "passive", "class": "rogue", "max_level": 5,
                     "requires": ["backstab"], "hidden": False, "sp_cost": 2},
    "fan_of_blades": {"name": "🌪️ Fan of Blades", "description": "Throw 4 blades, 70% ATK each",
                      "type": "active", "class": "rogue", "max_level": 3, "mana_cost": 30,
                      "requires": ["shadow_step"], "hidden": False, "sp_cost": 3},
    "death_mark": {"name": "💀 Death Mark", "description": "Mark target, +80% dmg from all attacks",
                   "type": "active", "class": "rogue", "max_level": 1, "mana_cost": 50, "level_req": 45,
                   "requires": ["shadow_step"], "hidden": True, "sp_cost": 5},
    "hemorrhage": {"name": "🩸 Hemorrhage", "description": "Bleed DOT: 15% ATK/turn for 5 turns",
                   "type": "active", "class": "rogue", "max_level": 3, "mana_cost": 18,
                   "requires": ["poison_blade"], "hidden": False, "sp_cost": 3},

    # PALADIN
    "holy_strike": {"name": "✨ Holy Strike", "description": "Deal 140% ATK holy damage",
                    "type": "active", "class": "paladin", "max_level": 5, "mana_cost": 12,
                    "damage_mult": [1.4, 1.65, 1.9, 2.2, 2.5], "requires": [], "hidden": False, "sp_cost": 1},
    "heal": {"name": "💚 Heal", "description": "Restore 30% max HP",
             "type": "active", "class": "paladin", "max_level": 5, "mana_cost": 20,
             "heal_pct": [0.3, 0.4, 0.5, 0.6, 0.75], "requires": [], "hidden": False, "sp_cost": 1},
    "divine_shield": {"name": "🛡️ Divine Shield", "description": "Immune to damage for 1 turn",
                      "type": "active", "class": "paladin", "max_level": 3, "mana_cost": 35,
                      "requires": ["holy_strike"], "hidden": False, "sp_cost": 3},
    "consecration": {"name": "🔆 Consecration", "description": "Holy ground, 80% ATK/turn for 3 turns",
                     "type": "active", "class": "paladin", "max_level": 3, "mana_cost": 30,
                     "requires": ["heal"], "hidden": False, "sp_cost": 2},
    "aura_of_light": {"name": "🌟 Aura of Light", "description": "Passive: Regen 5% HP each turn",
                      "type": "passive", "class": "paladin", "max_level": 5,
                      "requires": ["consecration"], "hidden": False, "sp_cost": 2},
    "holy_nova": {"name": "💥 Holy Nova", "description": "Burst of holy light, 200% ATK AoE",
                  "type": "active", "class": "paladin", "max_level": 3, "mana_cost": 45,
                  "requires": ["divine_shield", "aura_of_light"], "hidden": False, "sp_cost": 4},
    "smite": {"name": "⚡ Smite", "description": "Smite undead for 300% bonus damage",
              "type": "active", "class": "paladin", "max_level": 3, "mana_cost": 25,
              "requires": ["holy_strike"], "hidden": False, "sp_cost": 2},
    "resurrection": {"name": "💫 Resurrection", "description": "Revive with 50% HP (once per battle)",
                     "type": "active", "class": "paladin", "max_level": 1, "mana_cost": 100, "level_req": 50,
                     "requires": ["divine_shield", "aura_of_light"], "hidden": True, "sp_cost": 5},
    "guardian_angel": {"name": "👼 Guardian Angel", "description": "Passive: 15% chance to block lethal hit",
                       "type": "passive", "class": "paladin", "max_level": 3,
                       "requires": ["resurrection"], "hidden": True, "sp_cost": 5},

    # RANGER
    "arrow_shot": {"name": "🏹 Arrow Shot", "description": "Precise shot, 130% ATK damage",
                   "type": "active", "class": "ranger", "max_level": 5, "mana_cost": 8,
                   "damage_mult": [1.3, 1.55, 1.8, 2.1, 2.4], "requires": [], "hidden": False, "sp_cost": 1},
    "poison_arrow": {"name": "🐍 Poison Arrow", "description": "Poison for 40% ATK/turn, 4 turns",
                     "type": "active", "class": "ranger", "max_level": 5, "mana_cost": 12,
                     "requires": [], "hidden": False, "sp_cost": 1},
    "multi_shot": {"name": "🎯 Multi Shot", "description": "Fire 3 arrows, 90% ATK each",
                   "type": "active", "class": "ranger", "max_level": 5, "mana_cost": 20,
                   "requires": ["arrow_shot"], "hidden": False, "sp_cost": 2},
    "eagle_eye": {"name": "🦅 Eagle Eye", "description": "Passive +15% ATK and crit range",
                  "type": "passive", "class": "ranger", "max_level": 5,
                  "requires": ["arrow_shot"], "hidden": False, "sp_cost": 2},
    "rain_of_arrows": {"name": "🌧️ Rain of Arrows", "description": "100% ATK x5 random hits",
                       "type": "active", "class": "ranger", "max_level": 3, "mana_cost": 40,
                       "requires": ["multi_shot"], "hidden": False, "sp_cost": 3},
    "natures_ally": {"name": "🌿 Nature's Ally", "description": "Summon wolf companion for 3 turns",
                     "type": "active", "class": "ranger", "max_level": 3, "mana_cost": 35,
                     "requires": ["poison_arrow"], "hidden": False, "sp_cost": 3},
    "trueshot": {"name": "🎯 Trueshot", "description": "Ignores 50% of enemy DEF",
                 "type": "passive", "class": "ranger", "max_level": 3,
                 "requires": ["eagle_eye"], "hidden": False, "sp_cost": 3},
    "arrow_of_doom": {"name": "☠️ Arrow of Doom", "description": "Charged shot: 600% ATK pierce dmg",
                      "type": "active", "class": "ranger", "max_level": 1, "mana_cost": 90, "level_req": 55,
                      "requires": ["rain_of_arrows"], "hidden": True, "sp_cost": 5},
    "beast_tamer": {"name": "🐾 Beast Tamer", "description": "Beasts deal 50% less damage to you",
                    "type": "passive", "class": "ranger", "max_level": 3,
                    "requires": ["natures_ally"], "hidden": False, "sp_cost": 3},

    # NECROMANCER
    "death_bolt": {"name": "💀 Death Bolt", "description": "Dark bolt, 170% ATK shadow dmg",
                   "type": "active", "class": "necromancer", "max_level": 5, "mana_cost": 15,
                   "damage_mult": [1.7, 2.0, 2.3, 2.7, 3.1], "requires": [], "hidden": False, "sp_cost": 1},
    "raise_dead": {"name": "🧟 Raise Dead", "description": "Summon undead minion from dead mob",
                   "type": "active", "class": "necromancer", "max_level": 3, "mana_cost": 30,
                   "requires": [], "hidden": False, "sp_cost": 2},
    "life_drain": {"name": "🩸 Life Drain", "description": "Steal 25% of damage dealt as HP",
                   "type": "active", "class": "necromancer", "max_level": 5, "mana_cost": 20,
                   "requires": ["death_bolt"], "hidden": False, "sp_cost": 2},
    "bone_armor": {"name": "🦴 Bone Armor", "description": "+30% DEF from bones for 3 turns",
                   "type": "active", "class": "necromancer", "max_level": 3, "mana_cost": 25,
                   "requires": ["raise_dead"], "hidden": False, "sp_cost": 2},
    "plague": {"name": "☣️ Plague", "description": "Curse enemy: -50% stats for 3 turns",
               "type": "active", "class": "necromancer", "max_level": 3, "mana_cost": 35,
               "requires": ["life_drain", "bone_armor"], "hidden": False, "sp_cost": 3},
    "death_pact": {"name": "📜 Death Pact", "description": "Sacrifice 30% HP for 200% ATK boost",
                   "type": "active", "class": "necromancer", "max_level": 3, "mana_cost": 10,
                   "requires": ["life_drain"], "hidden": False, "sp_cost": 3},
    "soul_harvest": {"name": "💀 Soul Harvest", "description": "Gain mana from each kill",
                     "type": "passive", "class": "necromancer", "max_level": 3,
                     "requires": ["raise_dead"], "hidden": False, "sp_cost": 2},
    "lich_form": {"name": "👑 Lich Form", "description": "Transform: +100% all stats for 5 turns",
                  "type": "active", "class": "necromancer", "max_level": 1, "mana_cost": 100, "level_req": 60,
                  "requires": ["plague", "death_pact"], "hidden": True, "sp_cost": 5},
    "undead_army": {"name": "🧟 Undead Army", "description": "Raise 3 undead at once",
                    "type": "active", "class": "necromancer", "max_level": 1, "mana_cost": 80, "level_req": 70,
                    "requires": ["lich_form"], "hidden": True, "sp_cost": 5},

    # UNIVERSAL
    "meditation": {"name": "🧘 Meditation", "description": "Restore 40% mana",
                   "type": "active", "class": "universal", "max_level": 3, "mana_cost": 0,
                   "requires": [], "hidden": False, "sp_cost": 2},
    "first_aid": {"name": "🩹 First Aid", "description": "Heal 20% HP in battle",
                  "type": "active", "class": "universal", "max_level": 3, "mana_cost": 5,
                  "requires": [], "hidden": False, "sp_cost": 2},
    "treasure_hunter": {"name": "💰 Treasure Hunter", "description": "Passive +20% coin drops",
                         "type": "passive", "class": "universal", "max_level": 5,
                         "requires": [], "hidden": False, "sp_cost": 1},
    "luck": {"name": "🍀 Luck", "description": "Passive +10% rare item chance",
             "type": "passive", "class": "universal", "max_level": 5,
             "requires": ["treasure_hunter"], "hidden": False, "sp_cost": 2},
    "endurance": {"name": "💪 Endurance", "description": "Passive +10% max HP per level",
                  "type": "passive", "class": "universal", "max_level": 5,
                  "requires": [], "hidden": False, "sp_cost": 2},
    "swift_learner": {"name": "📚 Swift Learner", "description": "Passive +10% EXP gain per level",
                      "type": "passive", "class": "universal", "max_level": 3,
                      "requires": [], "hidden": False, "sp_cost": 2},
    "battle_hardened": {"name": "🛡️ Battle Hardened", "description": "Passive +5% DEF per level",
                         "type": "passive", "class": "universal", "max_level": 5,
                         "requires": ["endurance"], "hidden": False, "sp_cost": 2},
    "killing_blow": {"name": "💥 Killing Blow", "description": "+25% DMG when enemy <30% HP",
                     "type": "passive", "class": "universal", "max_level": 3,
                     "requires": [], "hidden": False, "sp_cost": 3},
    "survivor": {"name": "🌿 Survivor", "description": "Passive: Regen 2% HP after each battle",
                 "type": "passive", "class": "universal", "max_level": 5,
                 "requires": ["endurance"], "hidden": False, "sp_cost": 2},
    "berserker": {"name": "🔥 Berserker", "description": "+5% ATK for each 10% HP lost",
                  "type": "passive", "class": "universal", "max_level": 3,
                  "requires": ["killing_blow"], "hidden": True, "sp_cost": 3},

    # SECRET SKILLS (unlocked by achievements/kills)
    "slime_mastery": {
        "name": "🟢 Slime Mastery", "description": "SECRET: Kill 1000 Slimes → +50% DEF aura",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"mob_kills": {"slime": 1000}}, "sp_cost": 0
    },
    "wolf_bond": {
        "name": "🐺 Wolf Bond", "description": "SECRET: Kill 1000 Wolves → Summon wolf aura",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"mob_kills": {"wolf": 1000}}, "sp_cost": 0
    },
    "dragon_slayer": {
        "name": "🐉 Dragon Slayer", "description": "SECRET: Kill 100 Dragons → +100% vs bosses",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"mob_kills": {"dragon": 100}}, "sp_cost": 0
    },
    "undying_will": {
        "name": "💀 Undying Will", "description": "SECRET: Die 50 times → +30% HP on respawn",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"deaths": 50}, "sp_cost": 0
    },
    "shadow_dancer": {
        "name": "🌑 Shadow Dancer", "description": "SECRET: Kill 500 Shadows → Phase through attacks",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"mob_kills": {"shadow": 500}}, "sp_cost": 0
    },
    "void_walker": {
        "name": "🌌 Void Walker", "description": "SECRET: Kill 200 Demons → Void step ability",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"mob_kills": {"demon": 200}}, "sp_cost": 0
    },
    "ancient_knowledge": {
        "name": "📜 Ancient Knowledge", "description": "SECRET: Explore all 8 maps → +25% all stats",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"explore_all": True}, "sp_cost": 0
    },
    "immortal_soul": {
        "name": "✨ Immortal Soul", "description": "SECRET: Reach LVL 100 Hardcore → Legendary aura",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"immortal": True}, "sp_cost": 0
    },
    "coin_emperor": {
        "name": "👑 Coin Emperor", "description": "SECRET: Earn 1M coins total → +100% drops",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"total_coins": 1000000}, "sp_cost": 0
    },
    "golem_breaker": {
        "name": "🪨 Golem Breaker", "description": "SECRET: Kill 300 Golems → Armor pierce",
        "type": "passive", "class": "universal", "max_level": 1, "hidden": True, "secret": True,
        "unlock_condition": {"mob_kills": {"stone_golem": 300}}, "sp_cost": 0
    },
}


def get_available_skills(player_class, player_skills_dict):
    available = []
    for skill_id, skill in SKILLS.items():
        if skill.get("secret"):
            continue
        if skill["class"] not in [player_class, "universal"]:
            continue
        if skill_id in player_skills_dict:
            continue
        reqs = skill.get("requires", [])
        if all(r in player_skills_dict for r in reqs):
            available.append((skill_id, skill))
    return available


def check_secret_skill_unlocks(player, player_skills, mob_kills):
    newly_unlocked = []
    for skill_id, skill in SKILLS.items():
        if not skill.get("secret"):
            continue
        if skill_id in player_skills:
            continue
        cond = skill.get("unlock_condition", {})
        unlocked = True
        for cond_key, cond_val in cond.items():
            if cond_key == "mob_kills":
                for mob, needed in cond_val.items():
                    if mob_kills.get(mob, 0) < needed:
                        unlocked = False
            elif cond_key == "deaths":
                if player.get("deaths", 0) < cond_val:
                    unlocked = False
            elif cond_key == "immortal":
                if not player.get("immortal"):
                    unlocked = False
            elif cond_key == "explore_all":
                pass  # handled separately
        if unlocked:
            newly_unlocked.append(skill_id)
    return newly_unlocked


# ═══════════════════════════════════════════════════════════
# MAPS & MOBS & ITEMS
# ═══════════════════════════════════════════════════════════

MAPS = {
    "forest": {
        "name": "🌲 Whispering Forest", "description": "A dense forest full of wildlife",
        "level_req": 1, "mobs": ["slime", "wolf", "goblin", "forest_sprite"], "boss": "forest_king",
        "loot_table": ["wood", "herb", "mushroom", "wolf_pelt", "goblin_ear"],
        "hidden_items": ["ancient_seed", "mystic_flower"], "connections": ["cave", "plains"],
        "bg_emoji": "🌲🌿🍄"
    },
    "plains": {
        "name": "🌾 Golden Plains", "description": "Vast open fields with roaming beasts",
        "level_req": 5, "mobs": ["bandit", "wild_boar", "giant_bee", "scarecrow"], "boss": "plains_warlord",
        "loot_table": ["grain", "honey", "iron_ore", "leather"],
        "hidden_items": ["plains_crystal", "old_coin_bag"], "connections": ["forest", "dungeon", "swamp"],
        "bg_emoji": "🌾🌼🐝"
    },
    "cave": {
        "name": "🕳️ Dark Caverns", "description": "Treacherous underground tunnels",
        "level_req": 10, "mobs": ["bat", "cave_spider", "stone_golem", "dark_dwarf"], "boss": "cave_titan",
        "loot_table": ["crystal", "iron_ore", "gold_nugget", "spider_silk"],
        "hidden_items": ["glowing_crystal", "ancient_coin"], "connections": ["forest", "dungeon"],
        "bg_emoji": "🕳️💎🦇"
    },
    "dungeon": {
        "name": "⚰️ Ancient Dungeon", "description": "Ruins filled with undead horrors",
        "level_req": 20, "mobs": ["skeleton", "zombie", "ghost", "dark_mage"], "boss": "dungeon_overlord",
        "loot_table": ["bone", "cursed_gem", "ancient_scroll", "dark_essence"],
        "hidden_items": ["lich_fragment", "soul_crystal"], "connections": ["plains", "cave", "volcano"],
        "bg_emoji": "⚰️💀🕯️"
    },
    "swamp": {
        "name": "🌊 Cursed Swamp", "description": "Toxic marshlands with vile creatures",
        "level_req": 25, "mobs": ["swamp_toad", "leech", "shadow", "bog_witch"], "boss": "swamp_hydra",
        "loot_table": ["swamp_moss", "toxic_venom", "shadow_dust", "witch_brew"],
        "hidden_items": ["shadow_stone", "cursed_relic"], "connections": ["plains", "volcano"],
        "bg_emoji": "🌊☠️🐸"
    },
    "volcano": {
        "name": "🌋 Inferno Volcano", "description": "Scorching lands of fire and magma",
        "level_req": 40, "mobs": ["fire_elemental", "lava_golem", "demon", "fire_dragon"], "boss": "volcanic_overlord",
        "loot_table": ["magma_stone", "fire_essence", "demon_horn", "dragon_scale"],
        "hidden_items": ["phoenix_feather", "lava_core"], "connections": ["dungeon", "swamp", "frozen_tundra"],
        "bg_emoji": "🌋🔥😈"
    },
    "frozen_tundra": {
        "name": "❄️ Frozen Tundra", "description": "A freezing wasteland of ice and snow",
        "level_req": 60, "mobs": ["ice_elemental", "frost_wolf", "yeti", "ice_witch"], "boss": "frost_titan",
        "loot_table": ["ice_crystal", "frost_essence", "yeti_fur", "frozen_gem"],
        "hidden_items": ["frozen_heart", "ancient_ice_rune"], "connections": ["volcano", "void_realm"],
        "bg_emoji": "❄️🐺🏔️"
    },
    "void_realm": {
        "name": "🌌 Void Realm", "description": "A dimension beyond reality. Max danger!",
        "level_req": 80, "mobs": ["void_shade", "chaos_beast", "void_dragon", "ancient_horror"], "boss": "void_emperor",
        "loot_table": ["void_shard", "chaos_essence", "dark_crystal", "ancient_relic"],
        "hidden_items": ["void_core", "cosmic_fragment"], "connections": ["frozen_tundra"],
        "bg_emoji": "🌌👾🌀"
    }
}

MOBS = {
    "slime": {"name": "🟢 Slime", "hp": 30, "atk": 5, "def": 2, "exp": 8, "coins": (2, 6), "level": 1,
              "drops": [("slime_jelly", 0.8), ("mystic_flower", 0.01)]},
    "wolf": {"name": "🐺 Wolf", "hp": 60, "atk": 12, "def": 5, "exp": 18, "coins": (5, 12), "level": 3,
             "drops": [("wolf_pelt", 0.7), ("wolf_fang", 0.4)]},
    "goblin": {"name": "👺 Goblin", "hp": 45, "atk": 9, "def": 3, "exp": 14, "coins": (8, 18), "level": 2,
               "drops": [("goblin_ear", 0.6), ("rusty_dagger", 0.2)]},
    "forest_sprite": {"name": "🧚 Forest Sprite", "hp": 35, "atk": 8, "def": 6, "exp": 20, "coins": (4, 10), "level": 3,
                      "drops": [("sprite_dust", 0.9), ("ancient_seed", 0.05)]},
    "forest_king": {"name": "👑 Forest King", "hp": 500, "atk": 35, "def": 20, "exp": 200, "coins": (80, 150), "level": 10,
                    "drops": [("kings_crown", 0.5), ("forest_amulet", 0.3)], "boss": True},
    "bandit": {"name": "🦹 Bandit", "hp": 80, "atk": 15, "def": 8, "exp": 25, "coins": (15, 30), "level": 5,
               "drops": [("stolen_goods", 0.6), ("iron_sword", 0.15)]},
    "wild_boar": {"name": "🐗 Wild Boar", "hp": 100, "atk": 18, "def": 12, "exp": 30, "coins": (8, 15), "level": 7,
                  "drops": [("leather", 0.7), ("boar_tusk", 0.4)]},
    "giant_bee": {"name": "🐝 Giant Bee", "hp": 55, "atk": 14, "def": 6, "exp": 22, "coins": (5, 12), "level": 6,
                  "drops": [("honey", 0.8), ("stinger", 0.5)]},
    "scarecrow": {"name": "🎃 Scarecrow", "hp": 90, "atk": 16, "def": 14, "exp": 28, "coins": (10, 20), "level": 8,
                  "drops": [("stuffing", 0.5), ("cursed_hat", 0.1)]},
    "plains_warlord": {"name": "⚔️ Plains Warlord", "hp": 800, "atk": 50, "def": 30, "exp": 350, "coins": (150, 250), "level": 20,
                       "drops": [("warlord_blade", 0.4), ("warlord_armor", 0.3)], "boss": True},
    "bat": {"name": "🦇 Bat", "hp": 40, "atk": 10, "def": 4, "exp": 20, "coins": (3, 8), "level": 10,
            "drops": [("bat_wing", 0.7), ("crystal", 0.2)]},
    "cave_spider": {"name": "🕷️ Cave Spider", "hp": 70, "atk": 16, "def": 8, "exp": 30, "coins": (8, 18), "level": 12,
                    "drops": [("spider_silk", 0.8), ("spider_fang", 0.5)]},
    "stone_golem": {"name": "🪨 Stone Golem", "hp": 150, "atk": 22, "def": 30, "exp": 50, "coins": (20, 40), "level": 15,
                    "drops": [("stone_heart", 0.4), ("iron_ore", 0.9)]},
    "dark_dwarf": {"name": "⛏️ Dark Dwarf", "hp": 110, "atk": 20, "def": 18, "exp": 40, "coins": (25, 50), "level": 14,
                   "drops": [("dwarf_axe", 0.2), ("gold_nugget", 0.6)]},
    "cave_titan": {"name": "🗿 Cave Titan", "hp": 1200, "atk": 65, "def": 50, "exp": 500, "coins": (200, 380), "level": 30,
                   "drops": [("titan_fist", 0.3), ("ancient_gem", 0.4)], "boss": True},
    "skeleton": {"name": "💀 Skeleton", "hp": 90, "atk": 24, "def": 10, "exp": 45, "coins": (15, 30), "level": 20,
                 "drops": [("bone", 0.9), ("cursed_gem", 0.2)]},
    "zombie": {"name": "🧟 Zombie", "hp": 130, "atk": 20, "def": 15, "exp": 40, "coins": (12, 25), "level": 20,
               "drops": [("rotten_flesh", 0.8), ("dark_essence", 0.3)]},
    "ghost": {"name": "👻 Ghost", "hp": 80, "atk": 30, "def": 5, "exp": 55, "coins": (20, 40), "level": 22,
              "drops": [("ectoplasm", 0.7), ("soul_crystal", 0.1)]},
    "dark_mage": {"name": "🧙 Dark Mage", "hp": 100, "atk": 35, "def": 8, "exp": 65, "coins": (30, 60), "level": 25,
                  "drops": [("ancient_scroll", 0.5), ("dark_staff", 0.15)]},
    "dungeon_overlord": {"name": "💀 Dungeon Overlord", "hp": 2000, "atk": 80, "def": 60, "exp": 800, "coins": (350, 600), "level": 40,
                         "drops": [("overlord_robe", 0.3), ("lich_staff", 0.2)], "boss": True},
    "swamp_toad": {"name": "🐸 Swamp Toad", "hp": 120, "atk": 22, "def": 12, "exp": 50, "coins": (18, 35), "level": 25,
                   "drops": [("toad_gland", 0.7), ("swamp_moss", 0.8)]},
    "leech": {"name": "🐛 Giant Leech", "hp": 95, "atk": 28, "def": 6, "exp": 48, "coins": (15, 28), "level": 26,
              "drops": [("leech_venom", 0.8), ("toxic_venom", 0.5)]},
    "shadow": {"name": "🌑 Shadow", "hp": 110, "atk": 34, "def": 8, "exp": 60, "coins": (22, 45), "level": 28,
               "drops": [("shadow_dust", 0.9), ("shadow_stone", 0.05)]},
    "bog_witch": {"name": "🧙‍♀️ Bog Witch", "hp": 140, "atk": 38, "def": 12, "exp": 75, "coins": (35, 70), "level": 30,
                  "drops": [("witch_brew", 0.6), ("cursed_relic", 0.1)]},
    "swamp_hydra": {"name": "🐍 Swamp Hydra", "hp": 3000, "atk": 95, "def": 65, "exp": 1200, "coins": (500, 900), "level": 50,
                    "drops": [("hydra_scale", 0.4), ("hydra_poison", 0.5)], "boss": True},
    "fire_elemental": {"name": "🔥 Fire Elemental", "hp": 160, "atk": 45, "def": 15, "exp": 90, "coins": (30, 60), "level": 40,
                       "drops": [("fire_essence", 0.8), ("magma_stone", 0.5)]},
    "lava_golem": {"name": "🌋 Lava Golem", "hp": 220, "atk": 40, "def": 40, "exp": 100, "coins": (40, 80), "level": 42,
                   "drops": [("lava_core", 0.3), ("magma_stone", 0.9)]},
    "demon": {"name": "😈 Demon", "hp": 180, "atk": 55, "def": 20, "exp": 110, "coins": (50, 100), "level": 45,
              "drops": [("demon_horn", 0.6), ("dark_essence", 0.7)]},
    "fire_dragon": {"name": "🐉 Fire Dragon", "hp": 280, "atk": 65, "def": 35, "exp": 150, "coins": (80, 160), "level": 48,
                    "drops": [("dragon_scale", 0.7), ("dragon_claw", 0.4)]},
    "volcanic_overlord": {"name": "🌋 Volcanic Overlord", "hp": 5000, "atk": 130, "def": 90, "exp": 2000, "coins": (1000, 2000), "level": 65,
                          "drops": [("volcanic_heart", 0.3), ("inferno_blade", 0.2)], "boss": True},
    "ice_elemental": {"name": "❄️ Ice Elemental", "hp": 200, "atk": 55, "def": 30, "exp": 130, "coins": (50, 100), "level": 60,
                      "drops": [("frost_essence", 0.8), ("ice_crystal", 0.7)]},
    "frost_wolf": {"name": "🐺 Frost Wolf", "hp": 240, "atk": 60, "def": 25, "exp": 140, "coins": (55, 110), "level": 62,
                   "drops": [("yeti_fur", 0.6), ("frozen_gem", 0.4)]},
    "yeti": {"name": "❄️ Yeti", "hp": 350, "atk": 70, "def": 40, "exp": 170, "coins": (70, 140), "level": 65,
             "drops": [("yeti_fur", 0.9), ("frozen_heart", 0.15)]},
    "ice_witch": {"name": "🧊 Ice Witch", "hp": 250, "atk": 75, "def": 25, "exp": 180, "coins": (80, 160), "level": 68,
                  "drops": [("ancient_ice_rune", 0.2), ("ice_staff", 0.15)]},
    "frost_titan": {"name": "🧊 Frost Titan", "hp": 8000, "atk": 180, "def": 130, "exp": 3500, "coins": (2000, 4000), "level": 80,
                    "drops": [("frost_crown", 0.25), ("titan_ice_blade", 0.2)], "boss": True},
    "void_shade": {"name": "🌌 Void Shade", "hp": 280, "atk": 90, "def": 35, "exp": 200, "coins": (100, 200), "level": 80,
                   "drops": [("void_shard", 0.8), ("dark_crystal", 0.6)]},
    "chaos_beast": {"name": "👾 Chaos Beast", "hp": 350, "atk": 100, "def": 45, "exp": 230, "coins": (120, 240), "level": 83,
                    "drops": [("chaos_essence", 0.7), ("void_shard", 0.5)]},
    "void_dragon": {"name": "🌌 Void Dragon", "hp": 500, "atk": 120, "def": 60, "exp": 300, "coins": (180, 360), "level": 87,
                    "drops": [("ancient_relic", 0.4), ("void_core", 0.1)]},
    "ancient_horror": {"name": "👁️ Ancient Horror", "hp": 450, "atk": 130, "def": 50, "exp": 280, "coins": (160, 320), "level": 90,
                       "drops": [("cosmic_fragment", 0.1), ("void_shard", 0.9)]},
    "void_emperor": {"name": "🌌 Void Emperor", "hp": 20000, "atk": 300, "def": 200, "exp": 8000, "coins": (5000, 10000), "level": 100,
                     "drops": [("void_emperor_crown", 0.5), ("cosmic_core", 0.3)], "boss": True},
}

ITEMS = {
    "wood": {"name": "🪵 Wood", "type": "material", "desc": "Common crafting wood"},
    "herb": {"name": "🌿 Herb", "type": "material", "desc": "Useful for potions"},
    "mushroom": {"name": "🍄 Mushroom", "type": "material", "desc": "Strange fungi"},
    "wolf_pelt": {"name": "🐺 Wolf Pelt", "type": "material", "desc": "Warm fur"},
    "goblin_ear": {"name": "👺 Goblin Ear", "type": "material", "desc": "Proof of kill"},
    "iron_ore": {"name": "⛏️ Iron Ore", "type": "material", "desc": "Raw iron"},
    "gold_nugget": {"name": "💛 Gold Nugget", "type": "material", "desc": "Shiny gold"},
    "crystal": {"name": "💎 Crystal", "type": "material", "desc": "Magic crystal"},
    "bone": {"name": "🦴 Bone", "type": "material", "desc": "Old bones"},
    "dragon_scale": {"name": "🐉 Dragon Scale", "type": "material", "desc": "Fireproof scale"},
    "spider_silk": {"name": "🕷️ Spider Silk", "type": "material", "desc": "Strong silk"},
    "void_shard": {"name": "🌌 Void Shard", "type": "material", "desc": "Void matter"},
    "sprite_dust": {"name": "✨ Sprite Dust", "type": "material", "desc": "Magical fairy dust"},
    "slime_jelly": {"name": "🟢 Slime Jelly", "type": "material", "desc": "Gooey slime extract"},
    "wolf_fang": {"name": "🐺 Wolf Fang", "type": "material", "desc": "Sharp wolf tooth"},
    "health_potion": {"name": "🧪 Health Potion", "type": "consumable", "desc": "Restore 50 HP",
                      "effect": {"heal": 50}, "buy": 30, "sell": 10},
    "mega_potion": {"name": "🧪 Mega Potion", "type": "consumable", "desc": "Restore 200 HP",
                    "effect": {"heal": 200}, "buy": 100, "sell": 35},
    "mana_potion": {"name": "💧 Mana Potion", "type": "consumable", "desc": "Restore 50 mana",
                    "effect": {"mana": 50}, "buy": 30, "sell": 10},
    "elixir": {"name": "✨ Elixir", "type": "consumable", "desc": "Restore 50% HP + mana",
               "effect": {"heal_pct": 0.5, "mana_pct": 0.5}, "buy": 200, "sell": 70},
    "strength_brew": {"name": "💪 Strength Brew", "type": "consumable", "desc": "+30% ATK boost",
                      "effect": {"atk_boost": 0.3}, "buy": 150, "sell": 50},
    "iron_skin_brew": {"name": "🛡️ Iron Skin Brew", "type": "consumable", "desc": "+30% DEF boost",
                       "effect": {"def_boost": 0.3}, "buy": 150, "sell": 50},
    "rusty_sword": {"name": "⚔️ Rusty Sword", "type": "weapon", "desc": "+5 ATK", "atk": 5, "buy": 50, "sell": 15},
    "iron_sword": {"name": "⚔️ Iron Sword", "type": "weapon", "desc": "+12 ATK", "atk": 12, "buy": 150, "sell": 50},
    "steel_blade": {"name": "⚔️ Steel Blade", "type": "weapon", "desc": "+25 ATK", "atk": 25, "buy": 400, "sell": 140},
    "inferno_blade": {"name": "🔥 Inferno Blade", "type": "weapon", "desc": "+60 ATK +Fire", "atk": 60, "buy": 2000, "sell": 700},
    "rusty_shield": {"name": "🛡️ Rusty Shield", "type": "armor", "desc": "+5 DEF", "def": 5, "buy": 50, "sell": 15},
    "iron_armor": {"name": "🛡️ Iron Armor", "type": "armor", "desc": "+15 DEF", "def": 15, "buy": 200, "sell": 70},
    "dragon_armor": {"name": "🐉 Dragon Armor", "type": "armor", "desc": "+50 DEF +Resist", "def": 50, "buy": 3000, "sell": 1000},
    "ancient_seed": {"name": "🌱 Ancient Seed", "type": "material", "desc": "A rare seed of unknown origin"},
    "mystic_flower": {"name": "🌸 Mystic Flower", "type": "material", "desc": "Glows faintly"},
    "shadow_stone": {"name": "🌑 Shadow Stone", "type": "material", "desc": "Absorbs light"},
    "void_core": {"name": "🌌 Void Core", "type": "material", "desc": "Pure void energy"},
    "phoenix_feather": {"name": "🦅 Phoenix Feather", "type": "material", "desc": "Legendary firebird feather"},
    "cosmic_fragment": {"name": "🌠 Cosmic Fragment", "type": "material", "desc": "A piece of a star"},
    "autobattle_chip": {"name": "🤖 Autobattle Chip", "type": "special", "desc": "Enables auto-battle feature",
                        "buy": 500, "sell": 0},
    "skill_scroll": {"name": "📜 Skill Scroll", "type": "special", "desc": "Reveals a random hidden skill",
                     "buy": 300, "sell": 50},
    "exp_tome": {"name": "📗 EXP Tome", "type": "special", "desc": "+500 EXP instantly",
                 "buy": 200, "sell": 60, "effect": {"exp": 500}},
}

CRAFTING_RECIPES = {
    "craft_health_potion": {"materials": {"herb": 2, "mushroom": 1}, "result": "health_potion", "qty": 3},
    "craft_mega_potion": {"materials": {"herb": 5, "crystal": 1}, "result": "mega_potion", "qty": 2},
    "craft_mana_potion": {"materials": {"mushroom": 2, "sprite_dust": 1}, "result": "mana_potion", "qty": 3},
    "craft_iron_sword": {"materials": {"iron_ore": 3, "wood": 1}, "result": "iron_sword", "qty": 1},
    "craft_iron_armor": {"materials": {"iron_ore": 5}, "result": "iron_armor", "qty": 1},
    "craft_steel_blade": {"materials": {"iron_ore": 8, "gold_nugget": 2}, "result": "steel_blade", "qty": 1},
    "craft_strength_brew": {"materials": {"wolf_pelt": 2, "herb": 3}, "result": "strength_brew", "qty": 1},
    "craft_elixir": {"materials": {"crystal": 2, "herb": 3, "gold_nugget": 1}, "result": "elixir", "qty": 1},
}

# ═══════════════════════════════════════════════════════════
# ACHIEVEMENTS
# ═══════════════════════════════════════════════════════════

ACHIEVEMENTS = {
    "first_kill": {"name": "🗡️ First Blood", "desc": "Kill your first enemy", "secret": False},
    "hundred_kills": {"name": "💀 Serial Slayer", "desc": "Kill 100 enemies", "secret": False},
    "thousand_kills": {"name": "⚔️ Warlord", "desc": "Kill 1,000 enemies", "secret": False},
    "ten_deaths": {"name": "💀 Persistent", "desc": "Die 10 times and keep going", "secret": False},
    "level_10": {"name": "📈 Rising Power", "desc": "Reach Level 10", "secret": False},
    "level_50": {"name": "⭐ Half-Century", "desc": "Reach Level 50", "secret": False},
    "level_100": {"name": "👑 Legendary", "desc": "Reach Level 100", "secret": False},
    "void_slayer": {"name": "🌌 Void Slayer", "desc": "Defeat the Void Emperor", "secret": True},
    "undying_will": {"name": "💀 Undying Will", "desc": "Die 50 times (secret skill unlocked!)", "secret": True},
    "immortal": {"name": "✨ Immortal", "desc": "Complete Hardcore mode at LVL 100", "secret": False},
    "rich": {"name": "💰 Millionaire", "desc": "Accumulate 100,000 coins", "secret": False},
    "explorer": {"name": "🗺️ Explorer", "desc": "Visit all 8 maps", "secret": True},
    "crafter": {"name": "⚒️ Master Crafter", "desc": "Craft 50 items", "secret": False},
    "skill_master": {"name": "📚 Skill Master", "desc": "Unlock 20 skills", "secret": False},
    "boss_slayer": {"name": "🏆 Boss Slayer", "desc": "Defeat all 8 map bosses", "secret": True},
}

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════

def get_conn():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS players (
        user_id INTEGER PRIMARY KEY, username TEXT, class TEXT, race TEXT, difficulty TEXT,
        level INTEGER DEFAULT 1, exp INTEGER DEFAULT 0, hp INTEGER DEFAULT 100,
        max_hp INTEGER DEFAULT 100, mana INTEGER DEFAULT 50, max_mana INTEGER DEFAULT 50,
        atk INTEGER DEFAULT 10, def INTEGER DEFAULT 5, spd INTEGER DEFAULT 10,
        coins INTEGER DEFAULT 100, gems INTEGER DEFAULT 0, deaths INTEGER DEFAULT 0,
        kills INTEGER DEFAULT 0, skill_points INTEGER DEFAULT 0,
        map_id TEXT DEFAULT 'forest', is_dead INTEGER DEFAULT 0, immortal INTEGER DEFAULT 0,
        autobattle INTEGER DEFAULT 0, autobattle_purchased INTEGER DEFAULT 0,
        created_at INTEGER DEFAULT 0, last_active INTEGER DEFAULT 0,
        exp_boost_until INTEGER DEFAULT 0, exp_boost_mult REAL DEFAULT 1.0,
        promo_used TEXT DEFAULT '[]'
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS player_skills (
        user_id INTEGER, skill_id TEXT, level INTEGER DEFAULT 1,
        PRIMARY KEY (user_id, skill_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS player_inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, item_id TEXT,
        quantity INTEGER DEFAULT 1, equipped INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS player_achievements (
        user_id INTEGER, achievement_id TEXT, unlocked_at INTEGER,
        PRIMARY KEY (user_id, achievement_id)
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS player_mob_kills (
        user_id INTEGER, mob_id TEXT, count INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, mob_id)
    )""")
    conn.commit()
    conn.close()


def get_player(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM players WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def create_player(user_id, username, cls, race, difficulty):
    conn = get_conn()
    c = conn.cursor()
    now = int(time.time())
    cls_data = CLASSES[cls]
    race_data = RACES[race]
    base_hp = int((100 + cls_data["hp_bonus"]) * race_data["hp_mult"])
    base_atk = int((10 + cls_data["atk_bonus"]) * race_data["atk_mult"])
    base_def = int((5 + cls_data["def_bonus"]) * race_data["def_mult"])
    base_spd = 10 + cls_data["spd_bonus"]
    base_mana = 50 + cls_data["mana_bonus"]
    c.execute("""INSERT OR REPLACE INTO players
        (user_id, username, class, race, difficulty, hp, max_hp, mana, max_mana, atk, def, spd, coins, created_at, last_active)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,100,?,?)""",
        (user_id, username, cls, race, difficulty, base_hp, base_hp, base_mana, base_mana, base_atk, base_def, base_spd, now, now))
    for skill_id in cls_data["skills_start"]:
        c.execute("INSERT OR IGNORE INTO player_skills (user_id, skill_id, level) VALUES (?,?,1)", (user_id, skill_id))
    conn.commit()
    conn.close()


def update_player(user_id, **kwargs):
    if not kwargs:
        return
    conn = get_conn()
    c = conn.cursor()
    sets = ", ".join(f"{k}=?" for k in kwargs)
    vals = list(kwargs.values()) + [user_id]
    c.execute(f"UPDATE players SET {sets} WHERE user_id=?", vals)
    conn.commit()
    conn.close()


def get_player_skills(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT skill_id, level FROM player_skills WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return {r["skill_id"]: r["level"] for r in rows}


def unlock_skill(user_id, skill_id, level=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO player_skills (user_id, skill_id, level) VALUES (?,?,?)", (user_id, skill_id, level))
    conn.commit()
    conn.close()


def upgrade_skill_db(user_id, skill_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE player_skills SET level=level+1 WHERE user_id=? AND skill_id=?", (user_id, skill_id))
    conn.commit()
    conn.close()


def get_inventory(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM player_inventory WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_item(user_id, item_id, qty=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, quantity FROM player_inventory WHERE user_id=? AND item_id=?", (user_id, item_id))
    row = c.fetchone()
    if row:
        c.execute("UPDATE player_inventory SET quantity=quantity+? WHERE id=?", (qty, row["id"]))
    else:
        c.execute("INSERT INTO player_inventory (user_id, item_id, quantity) VALUES (?,?,?)", (user_id, item_id, qty))
    conn.commit()
    conn.close()


def remove_item(user_id, item_id, qty=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, quantity FROM player_inventory WHERE user_id=? AND item_id=?", (user_id, item_id))
    row = c.fetchone()
    if row:
        new_qty = row["quantity"] - qty
        if new_qty <= 0:
            c.execute("DELETE FROM player_inventory WHERE id=?", (row["id"],))
        else:
            c.execute("UPDATE player_inventory SET quantity=? WHERE id=?", (new_qty, row["id"]))
    conn.commit()
    conn.close()


def has_item(user_id, item_id, qty=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT quantity FROM player_inventory WHERE user_id=? AND item_id=?", (user_id, item_id))
    row = c.fetchone()
    conn.close()
    return row and row["quantity"] >= qty


def get_achievements_list(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT achievement_id FROM player_achievements WHERE user_id=?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [r["achievement_id"] for r in rows]


def unlock_achievement(user_id, ach_id):
    conn = get_conn()
    c = conn.cursor()
    now = int(time.time())
    c.execute("INSERT OR IGNORE INTO player_achievements (user_id, achievement_id, unlocked_at) VALUES (?,?,?)",
              (user_id, ach_id, now))
    conn.commit()
    conn.close()


def has_achievement(user_id, ach_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM player_achievements WHERE user_id=? AND achievement_id=?", (user_id, ach_id))
    row = c.fetchone()
    conn.close()
    return row is not None


def get_mob_kills(user_id, mob_id=None):
    conn = get_conn()
    c = conn.cursor()
    if mob_id:
        c.execute("SELECT count FROM player_mob_kills WHERE user_id=? AND mob_id=?", (user_id, mob_id))
        row = c.fetchone()
        conn.close()
        return row["count"] if row else 0
    else:
        c.execute("SELECT mob_id, count FROM player_mob_kills WHERE user_id=?", (user_id,))
        rows = c.fetchall()
        conn.close()
        return {r["mob_id"]: r["count"] for r in rows}


def add_mob_kill(user_id, mob_id, count=1):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO player_mob_kills (user_id, mob_id, count) VALUES (?,?,0)", (user_id, mob_id))
    c.execute("UPDATE player_mob_kills SET count=count+? WHERE user_id=? AND mob_id=?", (count, user_id, mob_id))
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════════════
# BATTLE ENGINE
# ═══════════════════════════════════════════════════════════

def exp_to_next_level(level):
    return int(BASE_EXP_PER_LEVEL * (level ** 1.5))


def get_exp_multiplier(player):
    mult = 1.0
    diff = DIFFICULTY.get(player.get("difficulty", "endless"), {})
    mult *= diff.get("exp_mult", 1.0)
    race = RACES.get(player.get("race", "human"), {})
    mult *= race.get("exp_mult", 1.0)
    now = int(time.time())
    if player.get("exp_boost_until", 0) > now:
        mult *= player.get("exp_boost_mult", 1.0)
    skills = get_player_skills(player["user_id"])
    if "swift_learner" in skills:
        mult *= (1 + 0.1 * skills["swift_learner"])
    return mult


def scale_mob(mob_data, player_level):
    scale = 1.0 + (player_level - mob_data["level"]) * 0.05
    scale = max(0.5, min(scale, 3.0))
    mob = dict(mob_data)
    mob["hp"] = int(mob["hp"] * scale)
    mob["atk"] = int(mob["atk"] * scale)
    mob["def"] = int(mob["def"] * scale)
    mob["exp"] = int(mob["exp"] * scale)
    mob["coins_roll"] = (int(mob_data["coins"][0] * scale), int(mob_data["coins"][1] * scale))
    return mob


def calculate_damage(atk, enemy_def, crit_chance=0.1, crit_mult=2.0):
    base = max(1, atk - int(enemy_def * 0.5))
    variance = random.uniform(0.85, 1.15)
    dmg = int(base * variance)
    crit = random.random() < crit_chance
    if crit:
        dmg = int(dmg * crit_mult)
    return dmg, crit


def do_battle(player, mob_id):
    mob_data = MOBS.get(mob_id)
    if not mob_data:
        return {"error": "Unknown mob"}

    mob = scale_mob(mob_data, player["level"])
    p_skills = get_player_skills(player["user_id"])

    p_hp = player["hp"]
    p_max_hp = player["max_hp"]
    p_atk = player["atk"]
    p_def = player["def"]
    crit_chance = 0.1

    if "iron_skin" in p_skills:
        p_def = int(p_def * (1 + 0.15 * p_skills["iron_skin"]))
    if "endurance" in p_skills:
        p_max_hp = int(p_max_hp * (1 + 0.1 * p_skills["endurance"]))
        p_hp = min(p_hp, p_max_hp)
    if "crit_mastery" in p_skills:
        crit_chance += 0.1 * p_skills["crit_mastery"]
    if "eagle_eye" in p_skills:
        p_atk = int(p_atk * (1 + 0.15 * p_skills["eagle_eye"]))

    last_stand = "last_stand" in p_skills
    m_hp = mob["hp"]
    turns = 0
    battle_log = []
    player_used_resurrection = False

    while p_hp > 0 and m_hp > 0 and turns < 30:
        turns += 1
        current_atk = p_atk
        if last_stand and p_hp < p_max_hp * 0.2:
            current_atk = int(current_atk * 2)
        if "killing_blow" in p_skills and m_hp < mob["hp"] * 0.3:
            current_atk = int(current_atk * (1 + 0.25 * p_skills["killing_blow"]))

        p_dmg, p_crit = calculate_damage(current_atk, mob["def"], crit_chance)
        m_hp -= p_dmg
        crit_str = " 💥CRIT!" if p_crit else ""
        battle_log.append(f"T{turns}: You deal {p_dmg}{crit_str} | Enemy HP: {max(0, m_hp)}")
        if m_hp <= 0:
            break

        e_dmg, _ = calculate_damage(mob["atk"], p_def)
        p_hp -= e_dmg
        battle_log.append(f"T{turns}: Enemy deals {e_dmg} | Your HP: {max(0, p_hp)}")

        if p_hp <= 0 and "resurrection" in p_skills and not player_used_resurrection:
            p_hp = int(p_max_hp * 0.5)
            player_used_resurrection = True
            battle_log.append("💫 RESURRECTION! Revived with 50% HP!")

        if "aura_of_light" in p_skills and p_hp > 0:
            regen = int(p_max_hp * 0.05)
            p_hp = min(p_max_hp, p_hp + regen)

        if "life_drain" in p_skills and p_hp > 0:
            drain = int(p_dmg * 0.25)
            p_hp = min(p_max_hp, p_hp + drain)

    won = m_hp <= 0
    result = {
        "won": won, "mob_name": mob_data["name"], "mob_id": mob_id,
        "turns": turns, "remaining_hp": max(0, p_hp),
        "battle_log": battle_log[-6:],
        "exp": 0, "coins": 0, "drops": [], "level_up": False,
        "new_level": player["level"], "secret_skills": [], "achievements": []
    }

    if won:
        exp_gain = int(mob["exp"] * get_exp_multiplier(player))
        coin_gain = random.randint(mob["coins_roll"][0], mob["coins_roll"][1])

        if "treasure_hunter" in p_skills:
            coin_gain = int(coin_gain * (1 + 0.2 * p_skills["treasure_hunter"]))

        drops = []
        for item_id, drop_chance in mob_data["drops"]:
            luck_bonus = 0.1 * p_skills.get("luck", 0) if "luck" in p_skills else 0
            if random.random() < drop_chance + luck_bonus:
                drops.append(item_id)
                add_item(player["user_id"], item_id, 1)

        new_exp = player["exp"] + exp_gain
        new_coins = player["coins"] + coin_gain
        new_kills = player["kills"] + 1
        new_level = player["level"]
        leveled_up = False

        while new_exp >= exp_to_next_level(new_level) and new_level < MAX_LEVEL:
            new_exp -= exp_to_next_level(new_level)
            new_level += 1
            leveled_up = True

        new_immortal = player.get("immortal", 0)
        if new_level >= MAX_LEVEL and player.get("difficulty") == "hardcore" and not new_immortal:
            new_immortal = 1
            result["achievements"].append("🏆 IMMORTAL ACHIEVED! You are now a Legend!")

        sp_gain = (new_level - player["level"]) if leveled_up else 0
        race = RACES.get(player.get("race", "human"), {})
        if leveled_up and race.get("bonus_skill_points"):
            sp_gain += race["bonus_skill_points"] * (new_level - player["level"])

        remaining_hp_val = max(1, result["remaining_hp"])

        update_player(player["user_id"],
            exp=new_exp, coins=new_coins, kills=new_kills, level=new_level,
            hp=remaining_hp_val,
            skill_points=player["skill_points"] + sp_gain,
            immortal=new_immortal,
            last_active=int(time.time())
        )

        add_mob_kill(player["user_id"], mob_id)
        mob_kills = get_mob_kills(player["user_id"])

        player_updated = get_player(player["user_id"])
        p_skills_updated = get_player_skills(player["user_id"])
        new_secrets = check_secret_skill_unlocks(player_updated, p_skills_updated, mob_kills)
        for sk in new_secrets:
            unlock_skill(player["user_id"], sk)
            result["secret_skills"].append(SKILLS[sk]["name"])

        ach_checks = [
            (new_kills >= 1, "first_kill", "🗡️ First Blood! Killed your first enemy!"),
            (new_kills >= 100, "hundred_kills", "💀 Serial Slayer! 100 kills!"),
            (new_kills >= 1000, "thousand_kills", "⚔️ Warlord! 1000 kills!"),
            (new_level >= 10, "level_10", "📈 Rising Power! Reached Level 10!"),
            (new_level >= 50, "level_50", "⭐ Half-Century! Reached Level 50!"),
            (new_level >= 100, "level_100", "👑 Legendary! Reached Level 100!"),
            (mob_id == "void_emperor" and won, "void_slayer", "🌌 Void Slayer! Defeated the Void Emperor!"),
        ]
        for condition, ach_id, msg in ach_checks:
            if condition and not has_achievement(player["user_id"], ach_id):
                unlock_achievement(player["user_id"], ach_id)
                result["achievements"].append(msg)

        result.update({"exp": exp_gain, "coins": coin_gain, "drops": drops,
                        "level_up": leveled_up, "new_level": new_level})
    else:
        new_deaths = player["deaths"] + 1
        if player.get("difficulty") == "hardcore":
            update_player(player["user_id"], is_dead=1, deaths=new_deaths, hp=0)
            result["hardcore_death"] = True
        else:
            respawn_hp = max(1, int(player["max_hp"] * 0.3))
            update_player(player["user_id"], hp=respawn_hp, deaths=new_deaths, last_active=int(time.time()))
            result["respawned"] = True
            result["respawn_hp"] = respawn_hp
            if new_deaths >= 50 and not has_achievement(player["user_id"], "undying_will"):
                unlock_achievement(player["user_id"], "undying_will")
                unlock_skill(player["user_id"], "undying_will")
                result["secret_skills"].append("💀 Undying Will")
            if new_deaths >= 10 and not has_achievement(player["user_id"], "ten_deaths"):
                unlock_achievement(player["user_id"], "ten_deaths")
                result["achievements"].append("💀 Persistent - Died 10 times!")
    return result


def format_battle_result(result):
    if result.get("error"):
        return f"❌ Error: {result['error']}"

    lines = [f"⚔️ **BATTLE vs {result['mob_name']}**\n"]
    if result["won"]:
        lines.append("🏆 **VICTORY!**")
        lines.append(f"⏱ Turns: {result['turns']} | ❤️ HP left: {result['remaining_hp']}")
        lines.append(f"✨ EXP: +{result['exp']} | 💰 Coins: +{result['coins']}")
        if result["drops"]:
            drop_names = [ITEMS.get(d, {}).get("name", d) for d in result["drops"]]
            lines.append(f"📦 Drops: {', '.join(drop_names)}")
        if result["level_up"]:
            lines.append(f"\n🎉 **LEVEL UP! → LVL {result['new_level']}!**")
        for sk in result.get("secret_skills", []):
            lines.append(f"\n🔓 **SECRET SKILL UNLOCKED: {sk}!**")
        for ach in result.get("achievements", []):
            lines.append(f"\n🏅 **ACHIEVEMENT: {ach}**")
    else:
        if result.get("hardcore_death"):
            lines.append("💀 **YOU DIED - HARDCORE MODE**")
            lines.append("Your hardcore run has ended. Use /reset to start over.")
        elif result.get("respawned"):
            lines.append(f"💀 You were defeated... but you respawn!")
            lines.append(f"❤️ Respawned with {result['respawn_hp']} HP")
        for ach in result.get("achievements", []):
            lines.append(f"\n🏅 {ach}")
        for sk in result.get("secret_skills", []):
            lines.append(f"\n🔓 **SECRET SKILL: {sk}!**")

    lines.append("\n📜 *Battle Log (last turns):*")
    for log in result["battle_log"]:
        lines.append(f"  {log}")
    return "\n".join(lines)


def auto_battle_tick(user_id):
    player = get_player(user_id)
    if not player or not player.get("autobattle"):
        return None
    if player.get("is_dead"):
        return None
    if player["hp"] <= int(player["max_hp"] * 0.15):
        return {"message": "⚠️ Auto-battle paused: HP too low! Use a potion first."}
    map_data = MAPS.get(player.get("map_id", "forest"), {})
    mobs = map_data.get("mobs", ["slime"])
    mob_id = random.choice(mobs)
    return do_battle(player, mob_id)


# ═══════════════════════════════════════════════════════════
# HANDLERS - HELPERS
# ═══════════════════════════════════════════════════════════

def make_bar(current, maximum, length=12):
    if maximum <= 0:
        return "▓" * length
    filled = int((current / maximum) * length)
    filled = max(0, min(filled, length))
    return "█" * filled + "░" * (length - filled)


def build_stats_text(player):
    race = RACES.get(player.get("race", "human"), {})
    cls = CLASSES.get(player.get("class", "warrior"), {})
    diff = DIFFICULTY.get(player.get("difficulty", "endless"), {})
    now = int(time.time())
    boost_active = player.get("exp_boost_until", 0) > now
    immortal_str = " ✨[IMMORTAL]" if player.get("immortal") else ""
    hardcore_str = " 💀[HARDCORE]" if player.get("difficulty") == "hardcore" else ""
    hp_bar = make_bar(player["hp"], player["max_hp"])
    exp_needed = exp_to_next_level(player["level"])
    exp_bar = make_bar(player["exp"], exp_needed)
    lines = [
        f"╔══ 🎮 **CHARACTER STATS** ══╗",
        f"👤 {player.get('username', 'Hero')}{immortal_str}{hardcore_str}",
        f"⚔️ {cls.get('name', '?')} | 🌍 {race.get('name', '?')} | 🎯 {diff.get('name', '?')}",
        f"",
        f"📊 **Level:** {player['level']} / {MAX_LEVEL}",
        f"✨ **EXP:** {player['exp']} / {exp_needed}",
        f"  {exp_bar}",
        f"",
        f"❤️ **HP:** {player['hp']} / {player['max_hp']}",
        f"  {hp_bar}",
        f"💧 **Mana:** {player['mana']} / {player['max_mana']}",
        f"",
        f"⚔️ ATK: {player['atk']}  🛡️ DEF: {player['def']}  💨 SPD: {player['spd']}",
        f"💰 Coins: {player['coins']}  💎 Gems: {player.get('gems', 0)}",
        f"💀 Deaths: {player.get('deaths', 0)}  🗡️ Kills: {player.get('kills', 0)}",
        f"🗺️ Map: {MAPS.get(player.get('map_id', 'forest'), {}).get('name', '?')}",
        f"🤖 Auto-battle: {'✅ ON' if player.get('autobattle') else '❌ OFF'}",
        f"🎫 Skill Points: {player.get('skill_points', 0)}",
    ]
    if boost_active:
        lines.append(f"⚡ 🚀 EXP x2 ACTIVE!")
    return "\n".join(lines)


def main_menu_keyboard(player):
    kb = [
        [InlineKeyboardButton("⚔️ Battle", callback_data="battle_menu"),
         InlineKeyboardButton("📊 Stats", callback_data="stats")],
        [InlineKeyboardButton("🗺️ Map", callback_data="map_menu"),
         InlineKeyboardButton("🎒 Inventory", callback_data="inventory")],
        [InlineKeyboardButton("📚 Skills", callback_data="skill_tree"),
         InlineKeyboardButton("🏪 Shop", callback_data="shop")],
        [InlineKeyboardButton("⚒️ Craft", callback_data="craft_menu"),
         InlineKeyboardButton("🏆 Achievements", callback_data="achievements")],
        [InlineKeyboardButton("🔍 Explore", callback_data="explore"),
         InlineKeyboardButton("🤖 Auto-Battle", callback_data="autobattle_toggle")],
    ]
    return InlineKeyboardMarkup(kb)


# ═══════════════════════════════════════════════════════════
# COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if player:
        text = (f"🎮 Welcome back, **{user.first_name}**!\n\n"
                f"{build_stats_text(player)}\n\nWhat would you like to do?")
        await update.message.reply_text(text, reply_markup=main_menu_keyboard(player), parse_mode=ParseMode.MARKDOWN)
    else:
        await show_class_selection(update, context)


async def show_class_selection(update, context):
    text = ("🎮 **Welcome to ABYSS CHRONICLES!**\n\n"
            "An epic MMORPG adventure awaits you.\n\n"
            "**Step 1: Choose your Class:**\n\n")
    for cls_id, cls in CLASSES.items():
        text += f"{cls['name']}\n_{cls['description']}_\n\n"
    kb = [[InlineKeyboardButton(cls["name"], callback_data=f"class_{cls_id}")]
          for cls_id, cls in CLASSES.items()]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎮 **ABYSS CHRONICLES - Help**\n\n"
        "**Commands:**\n"
        "/start - Start game / Main menu\n"
        "/stats - View your character\n"
        "/battle - Fight a monster\n"
        "/map - View & travel maps\n"
        "/skills - Skill tree\n"
        "/shop - Buy items\n"
        "/craft - Craft items\n"
        "/inventory or /inv - Your items\n"
        "/explore - Search the map\n"
        "/auto - Toggle auto-battle\n"
        "/promo <code> - Enter promo code\n"
        "/achievements - View achievements\n"
        "/reset - ⚠️ Reset character\n\n"
        "**Game Tips:**\n"
        "• Kill 1000 specific mobs for secret skills!\n"
        "• Explore maps to find hidden items\n"
        "• Hardcore mode = 2.5x EXP + Immortal title at LVL 100\n"
        "• Use code **Premak4** for 2x EXP for 24h!\n"
        "• Some skills are hidden in the skill tree 👀\n"
        "• Buy Auto-Battle Chip in shop for 500💰"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ You don't have a character yet! Use /start")
        return
    await update.message.reply_text(build_stats_text(player), reply_markup=main_menu_keyboard(player), parse_mode=ParseMode.MARKDOWN)


async def cmd_battle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    if player.get("is_dead"):
        await update.message.reply_text("💀 You are dead! Use /reset to restart your hardcore run.")
        return
    if player["hp"] <= int(player["max_hp"] * 0.1):
        await update.message.reply_text("❤️ HP critically low! Use a potion first. /inventory")
        return
    map_data = MAPS.get(player.get("map_id", "forest"), {})
    mobs = map_data.get("mobs", ["slime"])
    kb = []
    for mob_id in mobs:
        mob = MOBS.get(mob_id, {})
        kb.append([InlineKeyboardButton(f"{mob.get('name', mob_id)} (LVL {mob.get('level', '?')})", callback_data=f"fight_{mob_id}")])
    boss_id = map_data.get("boss")
    if boss_id and boss_id in MOBS:
        boss = MOBS[boss_id]
        kb.append([InlineKeyboardButton(f"🔴 BOSS: {boss['name']} (LVL {boss['level']})", callback_data=f"fight_{boss_id}")])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    text = (f"⚔️ **BATTLE MENU**\n📍 {map_data.get('name', '?')}\n"
            f"❤️ HP: {player['hp']}/{player['max_hp']}\n\nChoose your enemy:")
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_map(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    current_map = player.get("map_id", "forest")
    map_data = MAPS.get(current_map, {})
    connections = map_data.get("connections", [])
    text = (f"🗺️ **WORLD MAP**\n\n📍 **Current:** {map_data.get('name', '?')}\n"
            f"{map_data.get('bg_emoji', '')} _{map_data.get('description', '')}_\n"
            f"⚠️ Level Req: {map_data.get('level_req', 1)}\n\n"
            f"🧟 Monsters: {', '.join([MOBS.get(m, {}).get('name', m) for m in map_data.get('mobs', [])])}\n\n**Travel to:**")
    kb = []
    for conn_id in connections:
        conn = MAPS.get(conn_id, {})
        lock = "🔒 " if player["level"] < conn.get("level_req", 1) else ""
        kb.append([InlineKeyboardButton(f"{lock}{conn.get('name', conn_id)} (LVL {conn.get('level_req', 1)}+)", callback_data=f"travel_{conn_id}")])
    kb.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    await _show_skills(update.message, player)


async def _show_skills(message, player):
    p_skills = get_player_skills(player["user_id"])
    sp = player.get("skill_points", 0)
    p_class = player.get("class", "warrior")
    text = f"📚 **SKILL TREE**\n🎫 Skill Points: {sp}\n\n**Your Skills ({len(p_skills)}):**\n"
    for sk_id, sk_lvl in list(p_skills.items())[:10]:
        sk = SKILLS.get(sk_id, {})
        text += f"• {sk.get('name', sk_id)} Lv{sk_lvl}/{sk.get('max_level', 1)}\n"
    available = get_available_skills(p_class, p_skills)
    text += f"\n**Available to Learn ({len(available)}):**\n"
    kb = []
    for sk_id, sk in available[:8]:
        if not sk.get("secret"):
            cost = sk.get("sp_cost", 1)
            can = sp >= cost
            kb.append([InlineKeyboardButton(f"{'✅' if can else '❌'} {sk['name']} ({cost}SP)", callback_data=f"learn_skill_{sk_id}")])
            text += f"• {sk['name']} [{cost} SP] - {sk['description']}\n"
    for sk_id, sk_lvl in p_skills.items():
        sk = SKILLS.get(sk_id, {})
        if sk_lvl < sk.get("max_level", 1):
            cost = sk.get("sp_cost", 1)
            if sp >= cost:
                kb.append([InlineKeyboardButton(f"⬆️ Upgrade {sk.get('name', sk_id)} ({cost}SP)", callback_data=f"upgrade_skill_{sk_id}")])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    await _show_shop(update.message, player)


async def _show_shop(message, player):
    text = f"🏪 **SHOP**\n💰 Your coins: {player['coins']}\n\n"
    shop_items = ["health_potion", "mega_potion", "mana_potion", "elixir",
                  "strength_brew", "iron_skin_brew", "exp_tome", "skill_scroll", "autobattle_chip",
                  "iron_sword", "steel_blade", "iron_armor", "dragon_armor"]
    kb = []
    for item_id in shop_items:
        item = ITEMS.get(item_id, {})
        price = item.get("buy", 0)
        if price > 0:
            can_buy = "✅" if player["coins"] >= price else "❌"
            kb.append([InlineKeyboardButton(f"{can_buy} {item.get('name', item_id)} - {price}💰 | {item.get('desc', '')}", callback_data=f"buy_{item_id}")])
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_inventory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    await _show_inventory(update.message, player)


async def _show_inventory(message, player):
    inv = get_inventory(player["user_id"])
    text = f"🎒 **INVENTORY**\n💰 Coins: {player['coins']}\n\n"
    kb = []
    if inv:
        for item_entry in inv:
            item = ITEMS.get(item_entry["item_id"], {})
            name = item.get("name", item_entry["item_id"])
            qty = item_entry["quantity"]
            text += f"• {name} x{qty} - {item.get('desc', '')}\n"
            if item.get("type") == "consumable":
                kb.append([InlineKeyboardButton(f"💊 Use {name}", callback_data=f"use_{item_entry['item_id']}")])
    else:
        text += "_Empty inventory..._"
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_explore(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    await _do_explore(update.message, player)


async def _do_explore(message, player):
    map_data = MAPS.get(player.get("map_id", "forest"), {})
    loot = map_data.get("loot_table", [])
    hidden = map_data.get("hidden_items", [])
    result_text = f"🔍 **EXPLORING** {map_data.get('name', '?')}...\n\n"
    found = False
    for h_item in hidden:
        if random.random() < 0.08:
            add_item(player["user_id"], h_item, 1)
            item_name = ITEMS.get(h_item, {}).get("name", h_item)
            result_text += f"✨ **Rare Find!** You discovered a {item_name}!\n"
            found = True
    for l_item in loot:
        if random.random() < 0.35:
            qty = random.randint(1, 3)
            add_item(player["user_id"], l_item, qty)
            item_name = ITEMS.get(l_item, {}).get("name", l_item)
            result_text += f"📦 Found {qty}x {item_name}\n"
            found = True
    if not found:
        result_text += "😔 Nothing found this time. Try again!"
    if random.random() < 0.4:
        coins = random.randint(5, 30)
        update_player(player["user_id"], coins=player["coins"] + coins)
        result_text += f"\n💰 Found {coins} coins!"
    kb = [[InlineKeyboardButton("🔍 Explore Again", callback_data="explore"),
           InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
    await message.reply_text(result_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_craft(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    await _show_craft(update.message, player)


async def _show_craft(message, player):
    inv = {i["item_id"]: i["quantity"] for i in get_inventory(player["user_id"])}
    text = "⚒️ **CRAFTING MENU**\n\n"
    kb = []
    for recipe_id, recipe in CRAFTING_RECIPES.items():
        result_item = ITEMS.get(recipe["result"], {})
        mats = recipe["materials"]
        can_craft = all(inv.get(m, 0) >= qty for m, qty in mats.items())
        mat_text = ", ".join([f"{ITEMS.get(m,{}).get('name',m)} x{q}" for m, q in mats.items()])
        emoji = "✅" if can_craft else "❌"
        text += f"{emoji} **{result_item.get('name', recipe['result'])}** x{recipe['qty']}\n   {mat_text}\n\n"
        if can_craft:
            kb.append([InlineKeyboardButton(f"⚒️ Craft {result_item.get('name', '')}", callback_data=f"craft_{recipe_id}")])
    if not kb:
        text += "_No recipes available. Gather materials by exploring and fighting!_"
    kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    unlocked = get_achievements_list(player["user_id"])
    text = f"🏆 **ACHIEVEMENTS** ({len(unlocked)}/{len(ACHIEVEMENTS)})\n\n"
    for ach_id, ach in ACHIEVEMENTS.items():
        if ach_id in unlocked:
            text += f"✅ **{ach['name']}** - {ach['desc']}\n"
        elif not ach.get("secret"):
            text += f"🔒 {ach['name']} - {ach['desc']}\n"
        else:
            text += f"❓ ??? (Secret)\n"
    kb = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    if not context.args:
        await update.message.reply_text("Usage: /promo <code>\nExample: /promo Premak4")
        return
    code = context.args[0]
    promo_used = json.loads(player.get("promo_used", "[]"))
    if code in promo_used:
        await update.message.reply_text("❌ You already used this promo code!")
        return
    promo = PROMO_CODES.get(code)
    if not promo:
        await update.message.reply_text("❌ Invalid promo code!")
        return
    if promo["type"] == "exp_boost":
        duration = promo["duration_hours"] * 3600
        until = int(time.time()) + duration
        promo_used.append(code)
        update_player(player["user_id"], exp_boost_until=until, exp_boost_mult=promo["multiplier"],
                      promo_used=json.dumps(promo_used))
        await update.message.reply_text(
            f"🎉 **Promo Activated!**\n⚡ {promo['description']}\nValid for {promo['duration_hours']} hours!",
            parse_mode=ParseMode.MARKDOWN)


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("⚠️ YES, RESET", callback_data="confirm_reset"),
           InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]]
    await update.message.reply_text(
        "⚠️ **RESET CHARACTER?**\n\nThis will delete your character permanently!\nAre you sure?",
        reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)


async def cmd_auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user.id)
    if not player:
        await update.message.reply_text("❌ Use /start first!")
        return
    if not player.get("autobattle_purchased"):
        await update.message.reply_text(
            "🤖 **Auto-Battle**\n\nPurchase the Auto-Battle Chip in the shop for 500💰 first!\nUse /shop",
            parse_mode=ParseMode.MARKDOWN)
        return
    new_state = not player.get("autobattle", False)
    update_player(player["user_id"], autobattle=int(new_state))
    state_str = "✅ ENABLED" if new_state else "❌ DISABLED"
    await update.message.reply_text(
        f"🤖 **Auto-Battle {state_str}**\n\n"
        f"{'Auto-battle will fight for you every 30 seconds!' if new_state else 'Auto-battle stopped.'}",
        parse_mode=ParseMode.MARKDOWN)


# ═══════════════════════════════════════════════════════════
# CALLBACK HANDLER
# ═══════════════════════════════════════════════════════════

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    player = get_player(user.id)

    # Registration flow
    if data.startswith("class_"):
        cls_id = data.split("_", 1)[1]
        context.user_data["chosen_class"] = cls_id
        cls = CLASSES.get(cls_id, {})
        text = (f"⚔️ Class: {cls.get('name', cls_id)}\n\n**Step 2: Choose your Race:**\n\n")
        for race_id, race in RACES.items():
            text += f"{race['name']}\n_{race['description']}_\n\n"
        kb = [[InlineKeyboardButton(race["name"], callback_data=f"race_{race_id}")] for race_id, race in RACES.items()]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        return

    if data.startswith("race_"):
        race_id = data.split("_", 1)[1]
        context.user_data["chosen_race"] = race_id
        text = "**Step 3: Choose Difficulty:**\n\n"
        for diff_id, diff in DIFFICULTY.items():
            text += f"{diff['name']}\n_{diff['description']}_\n\n"
        kb = [[InlineKeyboardButton(diff["name"], callback_data=f"diff_{diff_id}")] for diff_id, diff in DIFFICULTY.items()]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        return

    if data.startswith("diff_"):
        diff_id = data.split("_", 1)[1]
        cls_id = context.user_data.get("chosen_class", "warrior")
        race_id = context.user_data.get("chosen_race", "human")
        create_player(user.id, user.first_name, cls_id, race_id, diff_id)
        player = get_player(user.id)
        text = (f"🎉 **Character Created!**\n\n{build_stats_text(player)}\n\n"
                f"🗡️ Your adventure begins in the Whispering Forest!\nUse the menu below to start playing!")
        await query.edit_message_text(text, reply_markup=main_menu_keyboard(player), parse_mode=ParseMode.MARKDOWN)
        return

    if not player:
        await query.edit_message_text("❌ No character found. Use /start")
        return

    if data == "main_menu" or data == "stats":
        player = get_player(user.id)
        await query.edit_message_text(build_stats_text(player), reply_markup=main_menu_keyboard(player), parse_mode=ParseMode.MARKDOWN)

    elif data == "battle_menu":
        if player.get("is_dead"):
            await query.edit_message_text("💀 You are dead! Use /reset to restart.")
            return
        map_data = MAPS.get(player.get("map_id", "forest"), {})
        mobs = map_data.get("mobs", ["slime"])
        kb = []
        for mob_id in mobs:
            mob = MOBS.get(mob_id, {})
            kb.append([InlineKeyboardButton(f"{mob.get('name', mob_id)} (LVL {mob.get('level', '?')})", callback_data=f"fight_{mob_id}")])
        boss_id = map_data.get("boss")
        if boss_id and boss_id in MOBS:
            boss = MOBS[boss_id]
            kb.append([InlineKeyboardButton(f"🔴 BOSS: {boss['name']}", callback_data=f"fight_{boss_id}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        text = (f"⚔️ **BATTLE**\n📍 {map_data.get('name','?')}\n"
                f"❤️ HP: {player['hp']}/{player['max_hp']}\n\nChoose enemy:")
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("fight_"):
        mob_id = data.split("_", 1)[1]
        if player.get("is_dead"):
            await query.edit_message_text("💀 You're dead! Use /reset")
            return
        result = do_battle(player, mob_id)
        text = format_battle_result(result)
        kb = [
            [InlineKeyboardButton("⚔️ Fight Again", callback_data=f"fight_{mob_id}"),
             InlineKeyboardButton("🔙 Menu", callback_data="battle_menu")],
            [InlineKeyboardButton("📊 Stats", callback_data="stats"),
             InlineKeyboardButton("🎒 Inventory", callback_data="inventory")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "map_menu":
        current_map = player.get("map_id", "forest")
        map_data = MAPS.get(current_map, {})
        connections = map_data.get("connections", [])
        text = (f"🗺️ **WORLD MAP**\n\n📍 **Current:** {map_data.get('name', '?')}\n"
                f"{map_data.get('bg_emoji', '')} _{map_data.get('description', '')}_\n\n**Travel to:**")
        kb = []
        for conn_id in connections:
            conn = MAPS.get(conn_id, {})
            lock = "🔒 " if player["level"] < conn.get("level_req", 1) else ""
            kb.append([InlineKeyboardButton(f"{lock}{conn.get('name', conn_id)} (LVL {conn.get('level_req', 1)}+)", callback_data=f"travel_{conn_id}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("travel_"):
        map_id = data.split("_", 1)[1]
        dest = MAPS.get(map_id, {})
        if player["level"] < dest.get("level_req", 1):
            await query.answer(f"❌ Need Level {dest.get('level_req', 1)}!", show_alert=True)
            return
        update_player(player["user_id"], map_id=map_id)
        await query.answer(f"✈️ Traveled to {dest.get('name', map_id)}!")
        player = get_player(user.id)
        map_data = dest
        connections = map_data.get("connections", [])
        text = (f"🗺️ **WORLD MAP**\n\n📍 **Current:** {map_data.get('name', '?')}\n"
                f"{map_data.get('bg_emoji', '')} _{map_data.get('description', '')}_\n\n**Travel to:**")
        kb = []
        for conn_id in connections:
            conn = MAPS.get(conn_id, {})
            lock = "🔒 " if player["level"] < conn.get("level_req", 1) else ""
            kb.append([InlineKeyboardButton(f"{lock}{conn.get('name', conn_id)} (LVL {conn.get('level_req', 1)}+)", callback_data=f"travel_{conn_id}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "skill_tree":
        p_skills = get_player_skills(player["user_id"])
        sp = player.get("skill_points", 0)
        p_class = player.get("class", "warrior")
        text = f"📚 **SKILL TREE**\n🎫 Skill Points: {sp}\n\n**Your Skills ({len(p_skills)}):**\n"
        for sk_id, sk_lvl in list(p_skills.items())[:10]:
            sk = SKILLS.get(sk_id, {})
            text += f"• {sk.get('name', sk_id)} Lv{sk_lvl}/{sk.get('max_level', 1)}\n"
        available = get_available_skills(p_class, p_skills)
        text += f"\n**Available ({len(available)}):**\n"
        kb = []
        for sk_id, sk in available[:6]:
            if not sk.get("secret"):
                cost = sk.get("sp_cost", 1)
                can = sp >= cost
                kb.append([InlineKeyboardButton(f"{'✅' if can else '❌'} {sk['name']} ({cost}SP) - {sk['description'][:25]}", callback_data=f"learn_skill_{sk_id}")])
                text += f"• {sk['name']} [{cost} SP]\n"
        for sk_id, sk_lvl in p_skills.items():
            sk = SKILLS.get(sk_id, {})
            if sk_lvl < sk.get("max_level", 1):
                cost = sk.get("sp_cost", 1)
                if sp >= cost:
                    kb.append([InlineKeyboardButton(f"⬆️ Upgrade {sk.get('name', sk_id)} ({cost}SP)", callback_data=f"upgrade_skill_{sk_id}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("learn_skill_"):
        sk_id = data.split("learn_skill_")[1]
        sk = SKILLS.get(sk_id)
        if not sk:
            await query.answer("Unknown skill!", show_alert=True)
            return
        sp = player.get("skill_points", 0)
        cost = sk.get("sp_cost", 1)
        p_skills = get_player_skills(player["user_id"])
        if sk_id in p_skills:
            await query.answer("Already learned!", show_alert=True)
            return
        if sp < cost:
            await query.answer(f"Need {cost} SP! You have {sp}.", show_alert=True)
            return
        unlock_skill(player["user_id"], sk_id)
        update_player(player["user_id"], skill_points=sp - cost)
        await query.answer(f"✅ Learned {sk['name']}!")
        player = get_player(user.id)
        p_skills = get_player_skills(player["user_id"])
        available = get_available_skills(player.get("class", "warrior"), p_skills)
        text = f"📚 **SKILL TREE**\n🎫 SP: {player['skill_points']}\n\n✅ Learned {sk['name']}!\n"
        kb = []
        for s_id, s in available[:6]:
            if not s.get("secret"):
                c = s.get("sp_cost", 1)
                kb.append([InlineKeyboardButton(f"{'✅' if player['skill_points']>=c else '❌'} {s['name']} ({c}SP)", callback_data=f"learn_skill_{s_id}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("upgrade_skill_"):
        sk_id = data.split("upgrade_skill_")[1]
        sk = SKILLS.get(sk_id)
        if not sk:
            await query.answer("Unknown skill!", show_alert=True)
            return
        p_skills = get_player_skills(player["user_id"])
        if sk_id not in p_skills:
            await query.answer("Don't have this skill!", show_alert=True)
            return
        current_lv = p_skills[sk_id]
        if current_lv >= sk.get("max_level", 1):
            await query.answer("Skill is max level!", show_alert=True)
            return
        sp = player.get("skill_points", 0)
        cost = sk.get("sp_cost", 1)
        if sp < cost:
            await query.answer(f"Need {cost} SP!", show_alert=True)
            return
        upgrade_skill_db(player["user_id"], sk_id)
        update_player(player["user_id"], skill_points=sp - cost)
        await query.answer(f"⬆️ {sk['name']} upgraded to LV{current_lv + 1}!")

    elif data == "shop":
        player = get_player(user.id)
        text = f"🏪 **SHOP**\n💰 Your coins: {player['coins']}\n\n"
        shop_items = ["health_potion", "mega_potion", "mana_potion", "elixir",
                      "strength_brew", "iron_skin_brew", "exp_tome", "skill_scroll", "autobattle_chip",
                      "iron_sword", "steel_blade", "iron_armor", "dragon_armor"]
        kb = []
        for item_id in shop_items:
            item = ITEMS.get(item_id, {})
            price = item.get("buy", 0)
            if price > 0:
                can_buy = "✅" if player["coins"] >= price else "❌"
                kb.append([InlineKeyboardButton(f"{can_buy} {item.get('name', item_id)} - {price}💰 | {item.get('desc', '')}", callback_data=f"buy_{item_id}")])
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("buy_"):
        item_id = data.split("buy_")[1]
        item = ITEMS.get(item_id, {})
        price = item.get("buy", 0)
        if player["coins"] < price:
            await query.answer(f"❌ Not enough coins! Need {price}.", show_alert=True)
            return
        if item_id == "autobattle_chip":
            if player.get("autobattle_purchased"):
                await query.answer("Already purchased!", show_alert=True)
                return
            update_player(player["user_id"], coins=player["coins"] - price, autobattle_purchased=1)
            await query.answer("🤖 Auto-Battle unlocked! Use /auto to enable it.")
        elif item_id == "skill_scroll":
            p_skills = get_player_skills(player["user_id"])
            p_class = player.get("class", "warrior")
            hidden_skills = [sid for sid, sk in SKILLS.items()
                             if sk.get("hidden") and not sk.get("secret")
                             and sk["class"] in [p_class, "universal"]
                             and sid not in p_skills]
            if hidden_skills:
                chosen = random.choice(hidden_skills)
                unlock_skill(player["user_id"], chosen)
                update_player(player["user_id"], coins=player["coins"] - price)
                await query.answer(f"📜 Revealed: {SKILLS[chosen]['name']}!", show_alert=True)
            else:
                await query.answer("No hidden skills left to reveal!", show_alert=True)
        elif item_id == "exp_tome":
            exp_gain = item.get("effect", {}).get("exp", 500)
            update_player(player["user_id"], coins=player["coins"] - price, exp=player["exp"] + exp_gain)
            await query.answer(f"📗 +{exp_gain} EXP gained!", show_alert=True)
        else:
            add_item(player["user_id"], item_id, 1)
            update_player(player["user_id"], coins=player["coins"] - price)
            await query.answer(f"✅ Bought {item.get('name', item_id)}!")

    elif data == "inventory":
        player = get_player(user.id)
        inv = get_inventory(player["user_id"])
        text = f"🎒 **INVENTORY**\n💰 Coins: {player['coins']}\n\n"
        kb = []
        if inv:
            for item_entry in inv:
                item = ITEMS.get(item_entry["item_id"], {})
                name = item.get("name", item_entry["item_id"])
                qty = item_entry["quantity"]
                text += f"• {name} x{qty} - {item.get('desc', '')}\n"
                if item.get("type") == "consumable":
                    kb.append([InlineKeyboardButton(f"💊 Use {name}", callback_data=f"use_{item_entry['item_id']}")])
        else:
            text += "_Empty!_"
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("use_"):
        item_id = data.split("use_")[1]
        item = ITEMS.get(item_id, {})
        if not has_item(player["user_id"], item_id):
            await query.answer("You don't have this!", show_alert=True)
            return
        effect = item.get("effect", {})
        msg = f"Used {item.get('name', item_id)}!\n"
        new_hp = player["hp"]
        new_mana = player["mana"]
        if "heal" in effect:
            new_hp = min(player["max_hp"], player["hp"] + effect["heal"])
            msg += f"❤️ +{effect['heal']} HP"
        if "heal_pct" in effect:
            heal = int(player["max_hp"] * effect["heal_pct"])
            new_hp = min(player["max_hp"], player["hp"] + heal)
            msg += f"❤️ +{heal} HP"
        if "mana" in effect:
            new_mana = min(player["max_mana"], player["mana"] + effect["mana"])
            msg += f" 💧+{effect['mana']} Mana"
        if "mana_pct" in effect:
            mp = int(player["max_mana"] * effect["mana_pct"])
            new_mana = min(player["max_mana"], player["mana"] + mp)
            msg += f" 💧+{mp} Mana"
        remove_item(player["user_id"], item_id, 1)
        update_player(player["user_id"], hp=new_hp, mana=new_mana)
        await query.answer(msg, show_alert=True)

    elif data == "explore":
        player = get_player(user.id)
        map_data = MAPS.get(player.get("map_id", "forest"), {})
        loot = map_data.get("loot_table", [])
        hidden = map_data.get("hidden_items", [])
        result_text = f"🔍 **EXPLORING** {map_data.get('name', '?')}...\n\n"
        found = False
        for h_item in hidden:
            if random.random() < 0.08:
                add_item(player["user_id"], h_item, 1)
                item_name = ITEMS.get(h_item, {}).get("name", h_item)
                result_text += f"✨ **Rare Find!** {item_name}!\n"
                found = True
        for l_item in loot:
            if random.random() < 0.35:
                qty = random.randint(1, 3)
                add_item(player["user_id"], l_item, qty)
                item_name = ITEMS.get(l_item, {}).get("name", l_item)
                result_text += f"📦 {qty}x {item_name}\n"
                found = True
        if not found:
            result_text += "😔 Nothing found this time."
        if random.random() < 0.4:
            coins = random.randint(5, 30)
            update_player(player["user_id"], coins=player["coins"] + coins)
            result_text += f"\n💰 Found {coins} coins!"
        kb = [[InlineKeyboardButton("🔍 Explore Again", callback_data="explore"),
               InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]]
        await query.edit_message_text(result_text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "autobattle_toggle":
        if not player.get("autobattle_purchased"):
            text = "🤖 **Auto-Battle**\n\nBuy the **Auto-Battle Chip** in the shop for 500💰 first!"
            kb = [[InlineKeyboardButton("🏪 Shop", callback_data="shop"),
                   InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
            await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)
        else:
            new_state = not player.get("autobattle", False)
            update_player(player["user_id"], autobattle=int(new_state))
            await query.answer(f"🤖 Auto-Battle: {'✅ ON' if new_state else '❌ OFF'}")
            player = get_player(user.id)
            await query.edit_message_text(build_stats_text(player), reply_markup=main_menu_keyboard(player), parse_mode=ParseMode.MARKDOWN)

    elif data == "achievements":
        unlocked = get_achievements_list(player["user_id"])
        text = f"🏆 **ACHIEVEMENTS** ({len(unlocked)}/{len(ACHIEVEMENTS)})\n\n"
        for ach_id, ach in ACHIEVEMENTS.items():
            if ach_id in unlocked:
                text += f"✅ **{ach['name']}** - {ach['desc']}\n"
            elif not ach.get("secret"):
                text += f"🔒 {ach['name']} - {ach['desc']}\n"
            else:
                text += f"❓ ??? (Secret)\n"
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="main_menu")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data == "craft_menu":
        inv = {i["item_id"]: i["quantity"] for i in get_inventory(player["user_id"])}
        text = "⚒️ **CRAFTING**\n\n"
        kb = []
        for recipe_id, recipe in CRAFTING_RECIPES.items():
            result_item = ITEMS.get(recipe["result"], {})
            mats = recipe["materials"]
            can_craft = all(inv.get(m, 0) >= qty for m, qty in mats.items())
            mat_text = ", ".join([f"{ITEMS.get(m,{}).get('name',m)} x{q}" for m, q in mats.items()])
            emoji = "✅" if can_craft else "❌"
            text += f"{emoji} **{result_item.get('name', recipe['result'])}** x{recipe['qty']}\n   {mat_text}\n\n"
            if can_craft:
                kb.append([InlineKeyboardButton(f"⚒️ Craft {result_item.get('name', '')}", callback_data=f"craft_{recipe_id}")])
        if not kb:
            text += "_No recipes available._"
        kb.append([InlineKeyboardButton("🔙 Back", callback_data="main_menu")])
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode=ParseMode.MARKDOWN)

    elif data.startswith("craft_"):
        recipe_id = data[6:]  # remove "craft_"
        recipe = CRAFTING_RECIPES.get(recipe_id)
        if not recipe:
            await query.answer("Unknown recipe!", show_alert=True)
            return
        inv = {i["item_id"]: i["quantity"] for i in get_inventory(player["user_id"])}
        if not all(inv.get(m, 0) >= qty for m, qty in recipe["materials"].items()):
            await query.answer("Not enough materials!", show_alert=True)
            return
        for mat, qty in recipe["materials"].items():
            remove_item(player["user_id"], mat, qty)
        add_item(player["user_id"], recipe["result"], recipe["qty"])
        result_name = ITEMS.get(recipe["result"], {}).get("name", recipe["result"])
        await query.answer(f"✅ Crafted {recipe['qty']}x {result_name}!", show_alert=True)

    elif data == "confirm_reset":
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM players WHERE user_id=?", (user.id,))
        c.execute("DELETE FROM player_skills WHERE user_id=?", (user.id,))
        c.execute("DELETE FROM player_inventory WHERE user_id=?", (user.id,))
        c.execute("DELETE FROM player_achievements WHERE user_id=?", (user.id,))
        c.execute("DELETE FROM player_mob_kills WHERE user_id=?", (user.id,))
        conn.commit()
        conn.close()
        await query.edit_message_text("🗑️ Character deleted. Use /start to create a new one!")


# ═══════════════════════════════════════════════════════════
# AUTO-BATTLE JOB
# ═══════════════════════════════════════════════════════════

async def auto_battle_job(context: ContextTypes.DEFAULT_TYPE):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT user_id FROM players WHERE autobattle=1 AND is_dead=0")
        rows = c.fetchall()
        conn.close()

        for row in rows:
            user_id = row["user_id"]
            player = get_player(user_id)
            if not player:
                continue
            if player["hp"] <= int(player["max_hp"] * 0.15):
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text="⚠️ **Auto-Battle Paused!**\nYour HP is critically low! Use a potion. (/inventory)",
                        parse_mode=ParseMode.MARKDOWN)
                except Exception:
                    pass
                continue

            result = auto_battle_tick(user_id)
            if result and not result.get("message"):
                text = f"🤖 **AUTO-BATTLE**\n\n{format_battle_result(result)}"
                try:
                    await context.bot.send_message(chat_id=user_id, text=text, parse_mode=ParseMode.MARKDOWN)
                except Exception as e:
                    logger.warning(f"Could not send auto-battle result to {user_id}: {e}")
    except Exception as e:
        logger.error(f"Auto-battle job error: {e}")


# ═══════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════

def main():
    init_db()
    logger.info("✅ Database initialized!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("battle", cmd_battle))
    app.add_handler(CommandHandler("map", cmd_map))
    app.add_handler(CommandHandler("skills", cmd_skills))
    app.add_handler(CommandHandler("shop", cmd_shop))
    app.add_handler(CommandHandler("inventory", cmd_inventory))
    app.add_handler(CommandHandler("inv", cmd_inventory))
    app.add_handler(CommandHandler("explore", cmd_explore))
    app.add_handler(CommandHandler("craft", cmd_craft))
    app.add_handler(CommandHandler("achievements", cmd_achievements))
    app.add_handler(CommandHandler("promo", cmd_promo))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("auto", cmd_auto))
    app.add_handler(CallbackQueryHandler(handle_callback))

    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(auto_battle_job, interval=30, first=10)
        logger.info("✅ Auto-battle job scheduled (every 30s)")

    logger.info("🎮 ABYSS CHRONICLES Bot is starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
