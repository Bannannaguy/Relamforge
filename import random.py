import random
import json
import os
import math
import re
import builtins
import pygame

# =====================================================================
# GAME REGISTRIES
# =====================================================================

RAW_MATERIALS = ["dirt", "iron", "wood", "stone", "copper", "gunpowder", "sand", "blood", "herb", "crystal"]
EXCLUSIVE_MATERIALS = ["ancient_relic", "dragon_scale", "enchanted_wood", "shadow_core"]

SPECIES_REGISTRY = {
    "a": {
        "name": "Human",
        "base_hp": 80,
        "base_power": 8,
        "base_defence": 1,
        "buff": "Tactical Mastery: +20% XP bonus and access to advanced firearms.",
        "weakness": "Fragile Frame: Takes +15% damage from heavy physical attacks.",
        "attacks": {
            "punch": {"dmg": 25, "cd": 0, "max_cd": 0, "status": None},
            "kick": {"dmg": 45, "cd": 0, "max_cd": 1, "status": None}
        },
        "unlockables": {
            "shoot": {"dmg": 40, "cd": 0, "max_cd": 1, "status": None},
            "grenade": {"dmg": 75, "cd": 0, "max_cd": 2, "status": "burn"},
            "sniper": {"dmg": 110, "cd": 0, "max_cd": 3, "status": None}
        }
    },
    "b": {
        "name": "Vampire",
        "base_hp": 95,
        "base_power": 12,
        "base_defence": 0,
        "buff": "Sanguine Drain: Natural life-steal on dark abilities and high base HP.",
        "weakness": "Sunlight Vulnerability: Reduced natural defense regeneration.",
        "attacks": {
            "blood_sucker": {"dmg": 30, "cd": 0, "max_cd": 0, "status": "drain"},
            "bat_bite": {"dmg": 50, "cd": 0, "max_cd": 2, "status": None}
        },
        "unlockables": {
            "hypnotize": {"dmg": 10, "cd": 0, "max_cd": 3, "status": "stun"},
            "mist_form": {"dmg": -30, "cd": 0, "max_cd": 3, "status": None},
            "blood_drain": {"dmg": 85, "cd": 0, "max_cd": 3, "status": "drain"}
        }
    },
    "c": {
        "name": "Cyborg",
        "base_hp": 120,
        "base_power": 9,
        "base_defence": 3,
        "buff": "Nanite Plating: Starts with highest Defense (+3) and health pool.",
        "weakness": "Overclock Strain: Abilities have slightly longer cooldowns.",
        "attacks": {
            "laser_blast": {"dmg": 22, "cd": 0, "max_cd": 0, "status": None},
            "rocket_punch": {"dmg": 52, "cd": 0, "max_cd": 1, "status": None}
        },
        "unlockables": {
            "emp_wave": {"dmg": 65, "cd": 0, "max_cd": 2, "status": "stun"},
            "self_repair": {"dmg": -40, "cd": 0, "max_cd": 3, "status": None},
            "overclock": {"dmg": 120, "cd": 0, "max_cd": 4, "status": "burn"}
        }
    },
    "d": {
        "name": "Elf",
        "base_hp": 65,
        "base_power": 10,
        "base_defence": 0,
        "buff": "Nature's Precision: Attacks inflict lingering Poison and high critical burst.",
        "weakness": "Fragile Constitution: Lowest starting health pool.",
        "attacks": {
            "bow_shot": {"dmg": 35, "cd": 0, "max_cd": 0, "status": None},
            "dagger_slash": {"dmg": 55, "cd": 0, "max_cd": 1, "status": None}
        },
        "unlockables": {
            "poison_arrow": {"dmg": 70, "cd": 0, "max_cd": 2, "status": "poison"},
            "stealth": {"dmg": 0, "cd": 0, "max_cd": 3, "status": "stealth"},
            "nature_heal": {"dmg": -35, "cd": 0, "max_cd": 3, "status": None}
        }
    }
}

# Recipe Registry: Crafting recipes for equipment, abilities, AND exclusive materials
RECIPES = {
    # Exclusive Material Synthesis Recipes (Transmuting raw materials into rare materials)
    "ancient_relic": {"req": {"stone": 10, "crystal": 2}, "def_bonus": 0, "atk_bonus": 0, "qty": 1, "species": "Universal"},
    "enchanted_wood": {"req": {"wood": 10, "herb": 4}, "def_bonus": 0, "atk_bonus": 0, "qty": 1, "species": "Universal"},
    "shadow_core": {"req": {"blood": 8, "crystal": 3}, "def_bonus": 0, "atk_bonus": 0, "qty": 1, "species": "Universal"},
    "dragon_scale": {"req": {"copper": 10, "iron": 10, "crystal": 4}, "def_bonus": 0, "atk_bonus": 0, "qty": 1, "species": "Universal"},

    # Standard & High-Tier Equipment Crafted using Exclusive Materials
    "brick_wall": {"req": {"stone": 3, "dirt": 2}, "def_bonus": 2, "atk_bonus": 0, "qty": 1, "species": "Universal"},
    "barrier": {"req": {"iron": 3, "wood": 2}, "def_bonus": 4, "atk_bonus": 0, "qty": 1, "species": "Universal"},
    "shadow_cloak": {"req": {"shadow_core": 2, "blood": 5}, "def_bonus": 8, "atk_bonus": 5, "qty": 1, "species": "Universal"},
    "enchanted_staff": {"req": {"enchanted_wood": 3, "crystal": 5}, "def_bonus": 3, "atk_bonus": 18, "qty": 1, "species": "Universal"},
    "dragon_armor": {"req": {"dragon_scale": 3, "iron": 8}, "def_bonus": 15, "atk_bonus": 2, "qty": 1, "species": "Universal"},
    "relic_blade": {"req": {"ancient_relic": 2, "iron": 6}, "def_bonus": 2, "atk_bonus": 25, "qty": 1, "species": "Universal"},
    "rifle": {"req": {"iron": 4, "wood": 2, "gunpowder": 2}, "def_bonus": 0, "atk_bonus": 15, "qty": 1, "species": "Human", "unlock": "sniper"},
    "coffin": {"req": {"wood": 8, "blood": 3}, "def_bonus": 3, "atk_bonus": 5, "qty": 1, "species": "Vampire", "unlock": "blood_drain"},
    "wire": {"req": {"copper": 2, "iron": 2}, "def_bonus": 1, "atk_bonus": 2, "qty": 2, "species": "Cyborg", "unlock": "emp_wave"},
    "arrow": {"req": {"wood": 2, "stone": 2}, "def_bonus": 0, "atk_bonus": 0, "qty": 10, "species": "Elf", "unlock": "poison_arrow"}
}

# Market Buy/Sell Rates
BUY_PRICES = {
    "dirt": 5, "wood": 8, "stone": 10, "iron": 20, "copper": 25, 
    "gunpowder": 30, "blood": 35, "herb": 15, "crystal": 50,
    "ancient_relic": 150, "enchanted_wood": 200, "shadow_core": 300, "dragon_scale": 450
}

SELL_PRICES = {item: int(price * 0.6) for item, price in BUY_PRICES.items()}
SELL_PRICES.update({
    "brick_wall": 25, "barrier": 40, "shadow_cloak": 250, 
    "enchanted_staff": 320, "dragon_armor": 500, "relic_blade": 420,
    "rifle": 120, "coffin": 100, "wire": 30, "arrow": 15
})

SKILL_TRAINER_CATALOG = {
    "berserk_strike": {
        "cost_gold": 250, "req_mat": "ancient_relic", "req_qty": 1,
        "atk": {"dmg": 95, "cd": 0, "max_cd": 3, "status": None},
        "desc": "A reckless heavy strike dealing huge damage."
    },
    "divine_shield": {
        "cost_gold": 300, "req_mat": "enchanted_wood", "req_qty": 2,
        "atk": {"dmg": -50, "cd": 0, "max_cd": 4, "status": None},
        "desc": "Channel divine magic to restore 50+ HP."
    },
    "shadow_strike": {
        "cost_gold": 450, "req_mat": "shadow_core", "req_qty": 2,
        "atk": {"dmg": 130, "cd": 0, "max_cd": 4, "status": "drain"},
        "desc": "Strike from the shadows, stealing health."
    },
    "dragon_breath": {
        "cost_gold": 600, "req_mat": "dragon_scale", "req_qty": 2,
        "atk": {"dmg": 160, "cd": 0, "max_cd": 5, "status": "burn"},
        "desc": "Unleash devastating dragon fire that burns enemies."
    }
}

ENEMY_REGISTRY = {
    "Goblin Scout": {"hp": 50, "power": 6, "exp": 25, "gold": (15, 30), "drop": "wood", "attacks": {"slash": 8, "stab": 12}},
    "Bandit Marauder": {"hp": 80, "power": 9, "exp": 45, "gold": (30, 60), "drop": "iron", "attacks": {"heavy_strike": 16, "cleave": 20}},
    "Corrupted Cyborg": {"hp": 120, "power": 12, "exp": 75, "gold": (50, 90), "drop": "copper", "attacks": {"overcharge": 22, "plasma_cut": 28}},
    "Vampire Lord": {"hp": 160, "power": 15, "exp": 110, "gold": (80, 140), "drop": "blood", "attacks": {"dark_frenzy": 26, "shadow_bolt": 32}},
    "Elder Dragon": {"hp": 320, "power": 24, "exp": 280, "gold": (300, 600), "drop": "dragon_scale", "attacks": {"inferno": 40, "tail_slam": 32}}
}

# =====================================================================
# CLAN & BANK SYSTEM
# =====================================================================

class AdvancedClan:
    def __init__(self):
        self.tier = 1
        self.tier_names = {1: "Outpost", 2: "Fortress", 3: "Citadel"}
        self.members = 1
        self.max_members = 5
        self.armory_lvl = 0   # +2 ATK / +1 DEF per level
        self.treasury_lvl = 0 # +25 Gold per action per level
        self.quarry_lvl = 0   # Generates passive raw & rare materials
        self.barracks_lvl = 0
        self.infirmary_lvl = 0
        self.library_lvl = 0
        self.watchtower_lvl = 0

    def upgrade_tier(self, player) -> bool:
        costs = {1: (500, "stone", 10), 2: (1500, "iron", 15)}
        if self.tier >= 3:
            print("\n[CLAN] Your Clan Citadel is already at maximum tier!")
            return False

        gold_req, mat_req, qty_req = costs[self.tier]
        if player.gold >= gold_req and player.inventory.get(mat_req, 0) >= qty_req:
            player.gold -= gold_req
            player.inventory[mat_req] -= qty_req
            self.tier += 1
            self.max_members += 5
            print(f"\n*** CLAN UPGRADED! Your Clan is now a Level {self.tier} {self.tier_names[self.tier]}! ***")
            print(f"Max Member Capacity increased to {self.max_members}.")
            return True
        else:
            print(f"\n[ERROR] Tier upgrade requires {gold_req} Gold and {qty_req}x {mat_req.capitalize()}!")
            return False

    def build_structure(self, player, structure: str):
        costs = {
            "armory": (200, "iron", 5),
            "treasury": (250, "copper", 5),
            "quarry": (150, "stone", 10),
            "barracks": (300, "wood", 5),
            "infirmary": (250, "herb", 5),
            "library": (350, "crystal", 2),
            "watchtower": (300, "iron", 8),
        }
        if structure not in costs:
            print(f"\n[ERROR] Unknown clan structure: {structure}.")
            return False

        gold_req, mat_req, qty_req = costs[structure]
        if player.gold >= gold_req and player.inventory.get(mat_req, 0) >= qty_req:
            player.gold -= gold_req
            player.inventory[mat_req] -= qty_req
            if structure == "armory":
                self.armory_lvl += 1
                player.bonus_power += 2
                player.bonus_defence += 1
                print(f"\n[CLAN BUILD] Armory upgraded to Lvl {self.armory_lvl}! (+2 ATK / +1 DEF)")
            elif structure == "treasury":
                self.treasury_lvl += 1
                print(f"\n[CLAN BUILD] Treasury upgraded to Lvl {self.treasury_lvl}! (+25 Gold passive yield)")
            elif structure == "quarry":
                self.quarry_lvl += 1
                print(f"\n[CLAN BUILD] Clan Quarry upgraded to Lvl {self.quarry_lvl}! (Generates materials passively)")
            elif structure == "barracks":
                self.barracks_lvl += 1
                self.max_members += 2
                print(f"\n[CLAN BUILD] Barracks upgraded to Lvl {self.barracks_lvl}! (+2 member capacity)")
            elif structure == "infirmary":
                self.infirmary_lvl += 1
                print(f"\n[CLAN BUILD] Infirmary upgraded to Lvl {self.infirmary_lvl}! (Restores {self.infirmary_lvl * 5} HP per action)")
            elif structure == "library":
                self.library_lvl += 1
                print(f"\n[CLAN BUILD] Library upgraded to Lvl {self.library_lvl}! (+{self.library_lvl * 10}% XP)")
            elif structure == "watchtower":
                self.watchtower_lvl += 1
                player.bonus_defence += 1
                print(f"\n[CLAN BUILD] Watchtower upgraded to Lvl {self.watchtower_lvl}! (+1 DEF)")
            return True
        else:
            print(f"\n[ERROR] Building {structure.capitalize()} requires {gold_req} Gold and {qty_req}x {mat_req.capitalize()}!")
            return False

    def process_passive_yields(self, player):
        if self.treasury_lvl > 0:
            passive_gold = self.treasury_lvl * 25
            player.gold += passive_gold
        if self.quarry_lvl > 0:
            pool = RAW_MATERIALS + EXCLUSIVE_MATERIALS
            random_mat = random.choice(pool)
            player.add_material(random_mat, self.quarry_lvl)
        if self.infirmary_lvl > 0:
            player.heal(self.infirmary_lvl * 5)

    def to_dict(self):
        return {
            "tier": self.tier,
            "members": self.members,
            "max_members": self.max_members,
            "armory_lvl": self.armory_lvl,
            "treasury_lvl": self.treasury_lvl,
            "quarry_lvl": self.quarry_lvl,
            "barracks_lvl": self.barracks_lvl,
            "infirmary_lvl": self.infirmary_lvl,
            "library_lvl": self.library_lvl,
            "watchtower_lvl": self.watchtower_lvl,
        }

    @classmethod
    def from_dict(cls, data):
        clan = cls()
        clan.tier = data.get("tier", 1)
        clan.members = data.get("members", 1)
        clan.max_members = data.get("max_members", 5)
        clan.armory_lvl = data.get("armory_lvl", 0)
        clan.treasury_lvl = data.get("treasury_lvl", 0)
        clan.quarry_lvl = data.get("quarry_lvl", 0)
        clan.barracks_lvl = data.get("barracks_lvl", 0)
        clan.infirmary_lvl = data.get("infirmary_lvl", 0)
        clan.library_lvl = data.get("library_lvl", 0)
        clan.watchtower_lvl = data.get("watchtower_lvl", 0)
        return clan

# =====================================================================
# PLAYER CLASS
# =====================================================================

class Player:
    def __init__(self, name: str, species_key: str):
        data = SPECIES_REGISTRY.get(species_key, SPECIES_REGISTRY["a"])
        self.name = name
        self.species = data["name"]
        self.level = 1
        self.exp = 0
        self.exp_needed = 100
        self.gold = 150
        self.bank_gold = 0  # Money stored in bank earning 2% interest per action
        
        self.base_max_hp = data["base_hp"]
        self.hp = data["base_hp"]
        self.base_power = data["base_power"]
        self.bonus_power = 0
        self.base_defence = data["base_defence"]
        self.bonus_defence = 0
        
        self.buff = data["buff"]
        self.weakness = data["weakness"]
        
        self.attacks = json.loads(json.dumps(data["attacks"]))
        self.unlockables = json.loads(json.dumps(data["unlockables"]))
        
        self.clan = AdvancedClan()
        self.mining_cooldown = 0
        self.status_effects = {}

        self.inventory = {mat: 5 for mat in RAW_MATERIALS}
        for ex in EXCLUSIVE_MATERIALS:
            self.inventory[ex] = 0
        for recipe in RECIPES:
            self.inventory[recipe] = 0

    @property
    def total_power(self) -> int:
        return self.base_power + self.bonus_power + (self.level * 2)

    @property
    def total_defence(self) -> int:
        return self.base_defence + self.bonus_defence

    def add_exp(self, amount: int):
        if self.species == "Human":
            amount = int(amount * 1.2)
        if self.clan.library_lvl > 0:
            amount = int(amount * (100 + 10 * self.clan.library_lvl) / 100)
            
        self.exp += amount
        print(f"\n+ {amount} XP earned!")
        
        while self.exp >= self.exp_needed:
            self.exp -= self.exp_needed
            self.level += 1
            self.exp_needed = int(self.exp_needed * 1.5)
            self.base_max_hp += 15
            self.base_power += 2
            self.hp = self.base_max_hp
            print(f"\n*** LEVEL UP! Reached Level {self.level}! ***")
            print(f"Max HP: {self.base_max_hp} | Total Power: {self.total_power}")

    def heal(self, amount: int):
        self.hp = min(self.base_max_hp, self.hp + amount)

    def add_material(self, item_name: str, qty: int = 1):
        self.inventory[item_name] = self.inventory.get(item_name, 0) + qty

    def has_materials(self, req_dict: dict) -> bool:
        return all(self.inventory.get(mat, 0) >= count for mat, count in req_dict.items())

    def consume_materials(self, req_dict: dict):
        for mat, count in req_dict.items():
            self.inventory[mat] -= count

    def tick_cooldowns(self):
        for atk in self.attacks:
            if self.attacks[atk]["cd"] > 0:
                self.attacks[atk]["cd"] -= 1
        if self.mining_cooldown > 0:
            self.mining_cooldown -= 1
            
        # Process Bank Interest (2% per action)
        if self.bank_gold > 0:
            interest = int(self.bank_gold * 0.02)
            self.bank_gold += interest

        self.clan.process_passive_yields(self)

    def reset_combat_state(self):
        for atk in self.attacks:
            self.attacks[atk]["cd"] = 0
        self.status_effects.clear()

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "species": self.species,
            "level": self.level,
            "exp": self.exp,
            "exp_needed": self.exp_needed,
            "gold": self.gold,
            "bank_gold": self.bank_gold,
            "base_max_hp": self.base_max_hp,
            "hp": self.hp,
            "base_power": self.base_power,
            "bonus_power": self.bonus_power,
            "base_defence": self.base_defence,
            "bonus_defence": self.bonus_defence,
            "buff": self.buff,
            "weakness": self.weakness,
            "attacks": self.attacks,
            "unlockables": self.unlockables,
            "clan": self.clan.to_dict(),
            "inventory": self.inventory
        }

    @classmethod
    def from_dict(cls, data: dict):
        player = cls.__new__(cls)
        player.name = data["name"]
        player.species = data["species"]
        player.level = data["level"]
        player.exp = data["exp"]
        player.exp_needed = data["exp_needed"]
        player.gold = data["gold"]
        player.bank_gold = data.get("bank_gold", 0)
        player.base_max_hp = data["base_max_hp"]
        player.hp = data["hp"]
        player.base_power = data["base_power"]
        player.bonus_power = data["bonus_power"]
        player.base_defence = data["base_defence"]
        player.bonus_defence = data["bonus_defence"]
        player.buff = data["buff"]
        player.weakness = data["weakness"]
        player.attacks = data["attacks"]
        player.unlockables = data["unlockables"]
        player.clan = AdvancedClan.from_dict(data.get("clan", {}))
        player.inventory = data["inventory"]
        player.mining_cooldown = 0
        player.status_effects = {}
        return player

# =====================================================================
# MONEY, BANKING & SHOPS
# =====================================================================

def merchant_marketplace(player: Player):
    """General Marketplace for Buying and Selling goods for Money/Gold."""
    while True:
        print("\n================ GRAND MARKETPLACE ================")
        print(f"Purse: {player.gold} Gold | Bank Account: {player.bank_gold} Gold")
        print("1. Buy Materials")
        print("2. Sell Items/Materials for Gold")
        print("3. Access Kingdom Bank (Deposit/Withdraw Money)")
        print("0. Back to Main Dashboard")
        
        ch = input("\nSelect Option #: ").strip()
        if ch == "0":
            break
        elif ch == "1":
            print("\n--- BUY MATERIALS ---")
            items = list(BUY_PRICES.keys())
            for idx, item in enumerate(items, 1):
                print(f"  {idx}. {item.replace('_', ' ').capitalize()} - {BUY_PRICES[item]} Gold")
            sel = input("Select item # (0 to cancel): ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(items):
                item_selected = items[int(sel) - 1]
                qty = input(f"How many {item_selected.capitalize()}? ").strip()
                if qty.isdigit() and int(qty) > 0:
                    cost = BUY_PRICES[item_selected] * int(qty)
                    if player.gold >= cost:
                        player.gold -= cost
                        player.add_material(item_selected, int(qty))
                        print(f"\n[BOUGHT] {qty}x {item_selected.capitalize()} for {cost} Gold!")
                    else:
                        print("\n[ERROR] Not enough Gold!")
        elif ch == "2":
            print("\n--- SELL ITEMS FOR GOLD ---")
            sellable = [k for k, v in player.inventory.items() if v > 0 and k in SELL_PRICES]
            if not sellable:
                print("You have no sellable items in your inventory!")
                continue
                
            for idx, item in enumerate(sellable, 1):
                unit_price = SELL_PRICES[item]
                count = player.inventory[item]
                print(f"  {idx}. {item.replace('_', ' ').capitalize()} (Have: {count}) - Sell Price: {unit_price} Gold each")
                
            sel = input("Select item # to sell (0 to cancel): ").strip()
            if sel.isdigit() and 1 <= int(sel) <= len(sellable):
                item_selected = sellable[int(sel) - 1]
                qty_str = input(f"Quantity of {item_selected.capitalize()} to sell (Max {player.inventory[item_selected]}): ").strip()
                if qty_str.isdigit() and 0 < int(qty_str) <= player.inventory[item_selected]:
                    qty = int(qty_str)
                    earnings = SELL_PRICES[item_selected] * qty
                    player.inventory[item_selected] -= qty
                    player.gold += earnings
                    recipe = RECIPES.get(item_selected, {})
                    player.bonus_defence -= recipe.get("def_bonus", 0) * qty
                    player.bonus_power -= recipe.get("atk_bonus", 0) * qty
                    print(f"\n[SOLD] {qty}x {item_selected.capitalize()} for {earnings} Gold!")
        elif ch == "3":
            kingdom_bank(player)

def kingdom_bank(player: Player):
    """Bank system earning compound interest on stored money."""
    while True:
        print("\n================ KINGDOM BANK ==================")
        print(f"Wallet Gold: {player.gold} Gold")
        print(f"Vault Balance: {player.bank_gold} Gold (Earns +2% interest per action)")
        print("1. Deposit Money")
        print("2. Withdraw Money")
        print("0. Leave Bank")
        
        ch = input("\nAction #: ").strip()
        if ch == "0":
            break
        elif ch == "1":
            amt = input("Deposit Amount: ").strip()
            if amt.isdigit() and 0 < int(amt) <= player.gold:
                val = int(amt)
                player.gold -= val
                player.bank_gold += val
                print(f"\n[DEPOSITED] {val} Gold into vault.")
            else:
                print("\n[ERROR] Invalid deposit amount!")
        elif ch == "2":
            amt = input("Withdraw Amount: ").strip()
            if amt.isdigit() and 0 < int(amt) <= player.bank_gold:
                val = int(amt)
                player.bank_gold -= val
                player.gold += val
                print(f"\n[WITHDRAWN] {val} Gold from vault.")
            else:
                print("\n[ERROR] Invalid withdrawal amount!")

def skill_trainer_shop(player: Player):
    while True:
        print("\n================ ACADEMY SKILL TRAINER ================")
        print(f"Gold: {player.gold} | Unlock new attacks for combat!")
        skills = list(SKILL_TRAINER_CATALOG.keys())
        for idx, sk in enumerate(skills, 1):
            info = SKILL_TRAINER_CATALOG[sk]
            status = "[OWNED]" if sk in player.attacks else f"Cost: {info['cost_gold']} Gold + {info['req_qty']}x {info['req_mat'].capitalize()}"
            print(f"  {idx}. {sk.replace('_', ' ').capitalize()} - {status}")
            print(f"     -> DMG: {info['atk']['dmg']} | Cooldown: {info['atk']['max_cd']} Turns | {info['desc']}")

        print("  0. Leave Trainer")
        choice = input("\nSelect skill # (0 to exit): ").strip()
        if choice == "0":
            break

        if choice.isdigit() and 1 <= int(choice) <= len(skills):
            sk_name = skills[int(choice) - 1]
            info = SKILL_TRAINER_CATALOG[sk_name]

            if sk_name in player.attacks:
                print("\n[TRAINER] You already know this skill!")
                continue

            if player.gold >= info["cost_gold"] and player.inventory.get(info["req_mat"], 0) >= info["req_qty"]:
                player.gold -= info["cost_gold"]
                player.inventory[info["req_mat"]] -= info["req_qty"]
                player.attacks[sk_name] = dict(info["atk"])
                print(f"\n*** SKILL UNLOCKED! Learned {sk_name.replace('_', ' ').capitalize()}! ***")
            else:
                print(f"\n[ERROR] Requires {info['cost_gold']} Gold and {info['req_qty']}x {info['req_mat'].capitalize()}!")

def clan_management_dashboard(player: Player):
    clan = player.clan
    while True:
        print("\n================ CLAN HEADQUARTERS ================")
        print(f"Clan Tier: Lvl {clan.tier} ({clan.tier_names[clan.tier]})")
        print(f"Warriors Recrypted: {clan.members}/{clan.max_members}")
        print(f"Structures: Armory {clan.armory_lvl} | Treasury {clan.treasury_lvl} | Quarry {clan.quarry_lvl}")
        print(f"Barracks {clan.barracks_lvl} | Infirmary {clan.infirmary_lvl} | Library {clan.library_lvl} | Watchtower {clan.watchtower_lvl}")
        print("\nClan Commands:")
        print("  1. Recruit Clan Warrior (+2 Power Bonus per warrior)")
        print("  2. Upgrade Clan Tier (Increases Member Limit)")
        print("  3. Build/Upgrade Armory (+2 ATK / +1 DEF)")
        print("  4. Build/Upgrade Treasury (+25 Passive Gold per action)")
        print("  5. Build/Upgrade Clan Quarry (Generates passive materials)")
        print("  6. Build Barracks (+2 member capacity)")
        print("  7. Build Infirmary (restores 5 HP per action per level)")
        print("  8. Build Library (+10% XP per level)")
        print("  9. Build Watchtower (+1 DEF per level)")
        print("  0. Back to Dashboard")

        choice = input("\nSelect Action #: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            if clan.members < clan.max_members:
                cost = clan.members * 100
                if player.gold >= cost:
                    player.gold -= cost
                    clan.members += 1
                    player.bonus_power += 2
                    print(f"\n[RECRUITED] New warrior joined your clan! Total Warriors: {clan.members}/{clan.max_members}.")
                else:
                    print(f"\n[ERROR] Recruiting next warrior costs {cost} Gold!")
            else:
                print("\n[CLAN FULL] Upgrade Clan Tier to recruit more warriors!")
        elif choice == "2":
            clan.upgrade_tier(player)
        elif choice == "3":
            clan.build_structure(player, "armory")
        elif choice == "4":
            clan.build_structure(player, "treasury")
        elif choice == "5":
            clan.build_structure(player, "quarry")
        elif choice == "6":
            clan.build_structure(player, "barracks")
        elif choice == "7":
            clan.build_structure(player, "infirmary")
        elif choice == "8":
            clan.build_structure(player, "library")
        elif choice == "9":
            clan.build_structure(player, "watchtower")

# =====================================================================
# ACTIVITIES & COMBAT
# =====================================================================

def explore(player: Player):
    print("\n--- WILDERNESS EXPLORATION ---")
    found_mat = random.choice(RAW_MATERIALS)
    amount = random.randint(2, 4)
    found_gold = random.randint(15, 40)
    
    player.add_material(found_mat, amount)
    player.gold += found_gold
    player.tick_cooldowns()
    
    print(f"Collected {amount}x [{found_mat.capitalize()}] and discovered {found_gold} Gold.")

def mine(player: Player):
    if player.mining_cooldown > 0:
        print(f"\n[QUARRY COOLDOWN] Mining team exhausted! Wait {player.mining_cooldown} turns.")
        return

    print("\n--- DEEP MINING QUARRY ---")
    minable = ["stone", "iron", "copper", "crystal"]
    extracted = random.choice(minable)
    amount = random.randint(3, 6)
    
    player.add_material(extracted, amount)
    player.tick_cooldowns()
    player.mining_cooldown = 3
    print(f"Mined {amount}x [{extracted.capitalize()}]! Quarry cooling down for 3 turns.")

def _finish_enemy_victory(player: Player, enemy_name: str, enemy_info: dict):
    gold_drop = random.randint(enemy_info["gold"][0], enemy_info["gold"][1])
    material_drop = enemy_info["drop"]
    print(f"\nVICTORY! Defeated {enemy_name}!")
    print(f"Loot: {gold_drop} Gold, 2x [{material_drop.capitalize()}]")
    player.gold += gold_drop
    player.add_material(material_drop, 2)
    player.add_exp(enemy_info["exp"])
    player.reset_combat_state()


def fight_an_enemy(player: Player):
    enemy_name, e_info = random.choice(list(ENEMY_REGISTRY.items()))
    e_hp = e_info["hp"] + (player.level * 10)
    e_max_hp = e_hp
    e_pow = e_info["power"]
    e_attacks = e_info["attacks"]
    enemy_effects = {}
    
    player.reset_combat_state()
    print(f"\n========== COMBAT ENGAGED: {enemy_name.upper()} ==========")

    while player.hp > 0 and e_hp > 0:
        print(f"\n{player.name} (Lvl {player.level}): [{player.hp}/{player.base_max_hp} HP] | DEF: {player.total_defence}")
        print(f"{enemy_name}: [{e_hp}/{e_max_hp} HP]")

        print("\nCombat Moves:")
        attack_keys = list(player.attacks.keys())
        for idx, atk in enumerate(attack_keys, 1):
            atk_data = player.attacks[atk]
            dmg = atk_data["dmg"]
            curr_cd = atk_data["cd"]
            effective_cooldown = atk_data["max_cd"] + (1 if player.species == "Cyborg" else 0)
            cd_str = (
                f"[READY | {effective_cooldown}-turn cooldown]"
                if curr_cd == 0 else f"[COOLDOWN: {curr_cd} turns]"
            )
            if dmg < 0:
                dmg_str = f"Heal {abs(dmg) + player.total_power}"
            elif dmg == 0:
                dmg_str = "Evade next attack"
            else:
                base_preview = dmg + (player.total_power // 2)
                dmg_str = f"{base_preview} DMG"
                if player.species == "Elf":
                    dmg_str += " + Poison / crit chance"
                elif atk_data.get("status"):
                    dmg_str += f" + {atk_data['status'].capitalize()}"
                if player.species == "Vampire" and atk_data.get("status") == "drain":
                    dmg_str += " / life-steal"
            print(f"  {idx}. {atk.replace('_', ' ').capitalize()} - {dmg_str} {cd_str}")
            
        print(f"  {len(attack_keys) + 1}. Emergency Shelter (1 Dirt & 1 Stone -> Absorb 15 DMG)")

        choice = input("\nExecute Command #: ").strip()
        shelter_active = False

        if choice.isdigit() and 1 <= int(choice) <= len(attack_keys):
            chosen_atk = attack_keys[int(choice) - 1]
            atk_data = player.attacks[chosen_atk]

            if atk_data["cd"] > 0:
                print(f"\n[CD ERROR] {chosen_atk.capitalize()} is cooling down ({atk_data['cd']} turns left)!")
                continue

            base_dmg = atk_data["dmg"]
            max_cd = atk_data["max_cd"] + (1 if player.species == "Cyborg" else 0)
            if base_dmg < 0:
                heal_val = abs(base_dmg) + player.total_power
                player.heal(heal_val)
                print(f"\nExecuted {chosen_atk.replace('_', ' ').capitalize()} and restored {heal_val} HP!")
            else:
                total_dmg = base_dmg + (player.total_power // 2) if base_dmg > 0 else 0
                is_critical = player.species == "Elf" and total_dmg > 0 and random.random() < 0.2
                if is_critical:
                    total_dmg = int(total_dmg * 1.5)
                    print("\nCRITICAL HIT! The Elf's precision increases the damage!")
                e_hp -= total_dmg
                print(f"\nExecuted {chosen_atk.replace('_', ' ').capitalize()} dealing {total_dmg} damage!")

                status = atk_data.get("status")
                if player.species == "Elf" and total_dmg > 0:
                    status = "poison"
                if status == "drain" and total_dmg > 0:
                    heal_val = max(1, total_dmg // 3)
                    player.heal(heal_val)
                    print(f"Life-steal restored {heal_val} HP!")
                elif status in ("burn", "poison") and total_dmg > 0:
                    duration = 2 if status == "burn" else 3
                    damage_per_turn = max(2, total_dmg // 6)
                    previous = enemy_effects.get(status, {})
                    enemy_effects[status] = {
                        "turns": max(duration, previous.get("turns", 0)),
                        "damage": max(damage_per_turn, previous.get("damage", 0)),
                    }
                    print(f"{enemy_name} is afflicted with {status}!")
                elif status == "stun":
                    enemy_effects["stun"] = max(1, enemy_effects.get("stun", 0))
                    print(f"{enemy_name} is stunned!")
                elif status == "stealth":
                    player.status_effects["stealth"] = True
                    print("You vanish into the shadows and evade the next attack!")

            player.tick_cooldowns()
            player.attacks[chosen_atk]["cd"] = max_cd
        elif choice == str(len(attack_keys) + 1):
            if player.inventory.get("dirt", 0) < 1 or player.inventory.get("stone", 0) < 1:
                print("\n[ERROR] Need 1 Dirt and 1 Stone!")
                continue
            player.inventory["dirt"] -= 1
            player.inventory["stone"] -= 1
            shelter_active = True
            player.tick_cooldowns()
            print("\nConstructed emergency cover! Reduced incoming damage.")
        else:
            print("\n[ERROR] Invalid move!")
            continue

        if e_hp <= 0:
            _finish_enemy_victory(player, enemy_name, e_info)
            break

        defeated_by_status = False
        for effect in ("burn", "poison"):
            effect_data = enemy_effects.get(effect)
            if not effect_data:
                continue
            effect_damage = effect_data["damage"]
            e_hp -= effect_damage
            effect_data["turns"] -= 1
            print(f"{enemy_name} takes {effect_damage} {effect} damage!")
            if effect_data["turns"] <= 0:
                del enemy_effects[effect]
            if e_hp <= 0:
                _finish_enemy_victory(player, enemy_name, e_info)
                defeated_by_status = True
                break
        if defeated_by_status:
            break

        if enemy_effects.pop("stun", 0):
            print(f"{enemy_name} is stunned and loses its turn!")
            continue
        if player.status_effects.pop("stealth", False):
            print(f"{enemy_name} cannot find you and misses its turn!")
            continue

        e_atk_name, e_raw_dmg = random.choice(list(e_attacks.items()))
        total_e_dmg = e_raw_dmg + (e_pow // 2)
        final_dmg = max(2, total_e_dmg - player.total_defence - (15 if shelter_active else 0))

        player.hp -= final_dmg
        print(f"The {enemy_name} used {e_atk_name.capitalize()} dealing {final_dmg} damage!")

        if player.hp <= 0:
            print("\nDEFEAT! Restoring HP to 50%...")
            player.hp = player.base_max_hp // 2
            player.reset_combat_state()
            break

def craft_something(player: Player):
    print("\n================ CRAFTING BENCH ================")
    print("Crafting Recipes (Includes Exclusive Material Refining):")
    available_recipes = []
    for item_name, recipe_info in RECIPES.items():
        if recipe_info["species"] in ["Universal", player.species]:
            available_recipes.append((item_name, recipe_info))

    for idx, (item_name, info) in enumerate(available_recipes, 1):
        req_str = ", ".join([f"{qty} {mat.capitalize()}" for mat, qty in info["req"].items()])
        stats = ""
        if info["def_bonus"] > 0: stats += f" [+{info['def_bonus']} DEF]"
        if info["atk_bonus"] > 0: stats += f" [+{info['atk_bonus']} ATK]"
        print(f"  {idx}. {item_name.replace('_', ' ').capitalize()} (Req: {req_str}){stats}")

    choice = input("\nSelect recipe # to craft (0 to exit): ").strip()
    if choice == "0":
        return

    if choice.isdigit() and 1 <= int(choice) <= len(available_recipes):
        item_name, info = available_recipes[int(choice) - 1]
        if player.has_materials(info["req"]):
            player.consume_materials(info["req"])
            player.add_material(item_name, info.get("qty", 1))
            player.bonus_defence += info.get("def_bonus", 0)
            player.bonus_power += info.get("atk_bonus", 0)
            
            print(f"\n[CRAFT SUCCESS] Crafted {info.get('qty', 1)}x {item_name.replace('_', ' ').capitalize()}!")
            
            unlock_key = info.get("unlock")
            if unlock_key and unlock_key in player.unlockables:
                player.attacks[unlock_key] = dict(player.unlockables.pop(unlock_key))
                print(f"*** UNLOCKED ABILITY: {unlock_key.upper()}! ***")
            
            player.tick_cooldowns()
        else:
            print("\n[ERROR] Missing required crafting materials!")

def view_inventory(player: Player):
    print("\n================ INVENTORY & STATS ================")
    print(f"Name: {player.name} | Species: {player.species} | Lvl: {player.level}")
    print(f"Purse: {player.gold} Gold | Bank Vault: {player.bank_gold} Gold")
    print(f"HP: {player.hp}/{player.base_max_hp} | ATK: {player.total_power} | DEF: {player.total_defence}")
    
    print("\n--- Standard Materials ---")
    print(" | ".join([f"{m.capitalize()}: {player.inventory.get(m, 0)}" for m in RAW_MATERIALS]))

    print("\n--- Exclusive / Rare Materials ---")
    print(" | ".join([f"{m.replace('_', ' ').capitalize()}: {player.inventory.get(m, 0)}" for m in EXCLUSIVE_MATERIALS]))

    print("\n--- Crafted Items & Equipment ---")
    crafted = [f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in player.inventory.items() if k not in RAW_MATERIALS and k not in EXCLUSIVE_MATERIALS and v > 0]
    print(" | ".join(crafted) if crafted else "None")

def save_game(player: Player):
    filename = f"{player.name.lower()}_rpg_save.json"
    with open(filename, "w") as f:
        json.dump(player.to_dict(), f, indent=4)
    print(f"\n[SAVED] Progress saved to '{filename}'.")

def load_game() -> Player:
    saves = [f for f in os.listdir() if f.endswith("_rpg_save.json")]
    if not saves:
        return None

    print("\nFound Saved Characters:")
    for idx, save_file in enumerate(saves, 1):
        print(f"  {idx}. {save_file}")

    choice = input("\nSelect slot # (or Enter for New Game): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(saves):
        with open(saves[int(choice) - 1], "r") as f:
            return Player.from_dict(json.load(f))
    return None

# =====================================================================
# MAIN ENGINE DASHBOARD
# =====================================================================

GAME_PLAYER = None


class GameExit(Exception):
    pass


class GameWindow:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1120, 760))
        pygame.display.set_caption("Realmforge - Text RPG")
        self.clock = pygame.time.Clock()
        self.title_font = pygame.font.Font(None, 38)
        self.body_font = pygame.font.Font(None, 25)
        self.log_font = pygame.font.Font(None, 22)
        self.small_font = pygame.font.Font(None, 20)
        self.output_lines = []
        self.menu_start = 0
        self.menu_page = 0
        self.history_page = 0
        self.page_size = 7
        self.click_regions = []
        self.page_regions = []
        self.prompt = ""
        self.input_text = ""
        self.input_rect = pygame.Rect(34, 677, 1052, 48)
        self.running = True
        self.combat_enemy = None
        self.combat_hp = 0
        self.combat_max_hp = 0
        self.hero_action_until = 0
        self.enemy_action_until = 0
        self.damage_effect = None
        self.colors = {
            "background": (12, 18, 31),
            "panel": (21, 31, 49),
            "panel_light": (29, 43, 65),
            "border": (55, 76, 99),
            "text": (225, 233, 242),
            "muted": (142, 161, 184),
            "accent": (83, 220, 187),
            "gold": (247, 193, 81),
            "red": (245, 103, 104),
            "blue": (112, 169, 255),
        }
        self.draw()

    def print_text(self, *values, sep=" ", end="\n"):
        text = sep.join(str(value) for value in values) + end
        self.output_lines.extend(text.splitlines())
        self.history_page = 0
        combat_start = re.search(r"COMBAT ENGAGED:\s*(.+)", text, re.IGNORECASE)
        if combat_start:
            name = combat_start.group(1).strip().rstrip("= ")
            self.combat_enemy = next(
                (enemy for enemy in ENEMY_REGISTRY if enemy.casefold() in name.casefold()),
                name.title(),
            )
            self.combat_max_hp = ENEMY_REGISTRY.get(self.combat_enemy, {}).get("hp", 0)
            if GAME_PLAYER is not None:
                self.combat_max_hp += GAME_PLAYER.level * 10
            self.combat_hp = self.combat_max_hp

        if self.combat_enemy and self.combat_enemy.casefold() in text.casefold():
            enemy_health = re.search(r"\[(\d+)/(\d+) HP\]", text)
            if enemy_health:
                self.combat_hp, self.combat_max_hp = map(int, enemy_health.groups())

        now = pygame.time.get_ticks()
        player_hit = re.search(r"Executed .+ dealing (\d+) damage", text, re.IGNORECASE)
        enemy_hit = re.search(r"The .+ used .+ dealing (\d+) damage", text, re.IGNORECASE)
        heal = re.search(r"restored (\d+) HP", text, re.IGNORECASE)
        if player_hit:
            self.hero_action_until = now + 460
            self.damage_effect = (player_hit.group(1), 705, now + 850, self.colors["gold"])
        elif enemy_hit:
            self.enemy_action_until = now + 460
            self.damage_effect = (enemy_hit.group(1), 420, now + 850, self.colors["red"])
        elif heal:
            self.damage_effect = (f"+{heal.group(1)} HP", 420, now + 1000, self.colors["accent"])

        if re.search(r"\b(VICTORY|DEFEAT)!", text, re.IGNORECASE):
            self.combat_enemy = None
            self.combat_hp = 0
            self.combat_max_hp = 0
            self.damage_effect = None
            self.hero_action_until = 0
            self.enemy_action_until = 0
        self.draw()

    def _draw_wrapped(self, text, font, color, x, y, max_width):
        words = text.split()
        if not words:
            return y + font.get_linesize()

        line = ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if line and font.size(candidate)[0] > max_width:
                self.screen.blit(font.render(line, True, color), (x, y))
                y += font.get_linesize()
                line = word
            else:
                line = candidate
        if line:
            self.screen.blit(font.render(line, True, color), (x, y))
            y += font.get_linesize()
        return y

    def _get_menu_pages(self):
        groups = []
        current_group = []
        for index in range(self.menu_start, len(self.output_lines)):
            line = self.output_lines[index]
            if re.match(r"^\s*\d+[.)]\s+", line):
                if current_group:
                    groups.append(current_group)
                current_group = [(index, line)]
            elif current_group:
                current_group.append((index, line))
        if current_group:
            groups.append(current_group)

        pages = []
        page = []
        row_count = 0
        for group in groups:
            group_rows = max(1, len(group))
            if page and row_count + group_rows > self.page_size:
                pages.append(page)
                page = []
                row_count = 0
            page.extend(group)
            row_count += group_rows
        if page:
            pages.append(page)
        return pages

    def _draw_battle_sprite(self, center, species, now, scale=2, action_until=0, enemy=False):
        cx, cy = center
        elapsed = max(0, action_until - now)
        lunge = math.sin((460 - elapsed) / 460 * math.pi) * 18 if elapsed else 0
        cx += int(-lunge if enemy else lunge)
        unit = scale
        cy += int(math.sin(now / 230) * unit)

        def rect(x, y, width, height):
            return pygame.Rect(
                int(cx + x * unit), int(cy + y * unit),
                max(1, int(width * unit)), max(1, int(height * unit)),
            )

        if enemy:
            palette = {
                "goblin scout": ((104, 176, 99), (60, 111, 73), (65, 104, 73), (225, 106, 78)),
                "bandit marauder": ((199, 153, 113), (92, 70, 70), (71, 91, 116), (223, 179, 97)),
                "corrupted cyborg": ((155, 185, 200), (65, 86, 103), (109, 135, 152), (94, 204, 224)),
                "vampire lord": ((200, 203, 216), (54, 43, 76), (94, 50, 75), (206, 91, 118)),
                "elder dragon": ((220, 132, 91), (101, 48, 54), (169, 73, 50), (255, 196, 102)),
            }
            skin, hair, outfit, accent = palette.get(species.casefold(), palette["goblin scout"])
        else:
            palette = {
                "Human": ((236, 184, 137), (95, 65, 49), (54, 93, 146), (87, 213, 192)),
                "Vampire": ((216, 214, 229), (54, 43, 76), (88, 47, 86), (204, 82, 131)),
                "Cyborg": ((179, 200, 215), (65, 84, 102), (70, 108, 131), (72, 220, 235)),
                "Elf": ((222, 185, 139), (74, 132, 91), (52, 112, 78), (157, 222, 117)),
            }
            skin, hair, outfit, accent = palette.get(species, palette["Human"])

        outline = (27, 34, 49)
        is_dragon = enemy and species.casefold() == "elder dragon"
        pygame.draw.ellipse(self.screen, (9, 14, 24), rect(-7, 14, 14, 2))
        if species == "Vampire" and not enemy:
            pygame.draw.polygon(
                self.screen, (69, 36, 77),
                [(int(cx - 6 * unit), int(cy - 8 * unit)),
                 (int(cx - 10 * unit), int(cy + 11 * unit)),
                 (cx, int(cy + 8 * unit)),
                 (int(cx + 10 * unit), int(cy + 11 * unit)),
                 (int(cx + 6 * unit), int(cy - 8 * unit))],
            )
        if is_dragon:
            wing = (117, 49, 53)
            pygame.draw.polygon(
                self.screen, wing,
                [(int(cx - 5 * unit), int(cy - 5 * unit)),
                 (int(cx - 15 * unit), int(cy - 14 * unit)),
                 (int(cx - 12 * unit), int(cy - 2 * unit)),
                 (int(cx - 9 * unit), int(cy + 4 * unit))],
            )
            pygame.draw.polygon(
                self.screen, wing,
                [(int(cx + 5 * unit), int(cy - 5 * unit)),
                 (int(cx + 15 * unit), int(cy - 14 * unit)),
                 (int(cx + 12 * unit), int(cy - 2 * unit)),
                 (int(cx + 9 * unit), int(cy + 4 * unit))],
            )
            pygame.draw.line(self.screen, accent, (int(cx - 5 * unit), int(cy + 7 * unit)),
                             (int(cx - 13 * unit), int(cy + 12 * unit)), max(2, int(unit * 2)))
        if enemy and species.casefold() == "goblin scout" or not enemy and species == "Elf":
            pygame.draw.polygon(self.screen, skin,
                                [(int(cx - 4 * unit), int(cy - 11 * unit)),
                                 (int(cx - 9 * unit), int(cy - 14 * unit)),
                                 (int(cx - 7 * unit), int(cy - 7 * unit))])
            pygame.draw.polygon(self.screen, skin,
                                [(int(cx + 4 * unit), int(cy - 11 * unit)),
                                 (int(cx + 9 * unit), int(cy - 14 * unit)),
                                 (int(cx + 7 * unit), int(cy - 7 * unit))])

        pygame.draw.rect(self.screen, outline, rect(-6, 5, 5, 10), border_radius=max(1, int(unit)))
        pygame.draw.rect(self.screen, outline, rect(1, 5, 5, 10), border_radius=max(1, int(unit)))
        pygame.draw.rect(self.screen, accent, rect(-5, 6, 3, 8), border_radius=max(1, int(unit)))
        pygame.draw.rect(self.screen, accent, rect(2, 6, 3, 8), border_radius=max(1, int(unit)))
        pygame.draw.rect(self.screen, outline, rect(-7, -5, 14, 12), border_radius=max(1, int(unit * 2)))
        pygame.draw.polygon(
            self.screen, outfit,
            [(int(cx - 6 * unit), int(cy - 4 * unit)),
             (int(cx + 6 * unit), int(cy - 4 * unit)),
             (int(cx + 5 * unit), int(cy + 6 * unit)),
             (int(cx - 5 * unit), int(cy + 6 * unit))],
        )
        if species == "Cyborg" or enemy and species.casefold() == "corrupted cyborg":
            pygame.draw.rect(self.screen, (90, 115, 132), rect(-7, -4, 3, 7))
            pygame.draw.rect(self.screen, (90, 115, 132), rect(4, -4, 3, 7))
            pygame.draw.circle(self.screen, accent, (int(cx), int(cy)), max(1, int(unit)))
        pygame.draw.rect(self.screen, accent, rect(-1, -3, 2, 8))

        arm_swing = 2 if elapsed > 170 else 0
        for side, swing in ((-1, -arm_swing), (1, 0)):
            start = (int(cx + side * 5 * unit), int(cy - 2 * unit))
            finish = (int(cx + side * (8 - swing) * unit), int(cy + 3 * unit))
            pygame.draw.line(self.screen, outline, start, finish, max(2, int(unit * 3)))
            pygame.draw.line(self.screen, skin, start, finish, max(1, int(unit * 2)))

        pygame.draw.rect(self.screen, outline, rect(-5, -14, 10, 10), border_radius=max(1, int(unit * 2)))
        pygame.draw.rect(self.screen, skin, rect(-4, -13, 8, 8), border_radius=max(1, int(unit * 2)))
        pygame.draw.rect(self.screen, hair, rect(-5, -15, 10, 4), border_radius=max(1, int(unit * 2)))
        pygame.draw.rect(self.screen, hair, rect(-5, -12, 2, 4))
        pygame.draw.rect(self.screen, hair, rect(3, -12, 2, 4))
        if is_dragon:
            pygame.draw.polygon(self.screen, accent,
                                [(int(cx - 4 * unit), int(cy - 12 * unit)),
                                 (int(cx - 6 * unit), int(cy - 18 * unit)),
                                 (int(cx - unit), int(cy - 13 * unit))])
            pygame.draw.polygon(self.screen, accent,
                                [(int(cx + 4 * unit), int(cy - 12 * unit)),
                                 (int(cx + 6 * unit), int(cy - 18 * unit)),
                                 (int(cx + unit), int(cy - 13 * unit))])
        pygame.draw.rect(self.screen, outline, rect(-2, -10, 1, 1))
        pygame.draw.rect(self.screen, outline, rect(2, -10, 1, 1))

        if (enemy and not is_dragon) or (not enemy and species in ("Human", "Elf")):
            sword_x, sword_y = cx + 9 * unit, cy + unit
            sword_end = (int(sword_x + 3 * unit), int(sword_y - 9 * unit))
            pygame.draw.line(self.screen, outline, (int(sword_x), int(sword_y)), sword_end, max(2, int(unit * 2)))
            pygame.draw.line(self.screen, (211, 224, 235), (int(sword_x), int(sword_y)), sword_end, max(1, int(unit)))
            pygame.draw.line(self.screen, accent, (int(sword_x - 2 * unit), int(sword_y)),
                             (int(sword_x + 2 * unit), int(sword_y + 2 * unit)), max(2, int(unit)))

        if elapsed:
            slash_color = (255, 239, 170) if not enemy else (255, 130, 133)
            slash_rect = pygame.Rect(int(cx + (8 if not enemy else -23) * unit), int(cy - 14 * unit),
                                     int(16 * unit), int(17 * unit))
            start, stop = (205, 345) if not enemy else (335, 475)
            pygame.draw.arc(self.screen, slash_color, slash_rect, math.radians(start),
                            math.radians(stop), max(1, int(unit)))

    def _draw_battle_scene(self, player, now):
        colors = self.colors
        scene = pygame.Rect(28, 91, 1064, 318)
        self.screen.set_clip(scene)
        for row in range(226):
            blend = row / 225
            sky = (int(15 + blend * 38), int(24 + blend * 48), int(49 + blend * 52))
            pygame.draw.line(self.screen, sky, (scene.left, scene.top + row), (scene.right, scene.top + row))

        for index, (sx, sy, phase) in enumerate((
            (70, 40, 0), (155, 91, 1), (256, 33, 2), (363, 79, 3), (493, 42, 4),
            (607, 103, 5), (704, 37, 6), (821, 76, 7), (1004, 48, 8),
        )):
            twinkle = int(40 + 45 * (0.5 + 0.5 * math.sin(now / 370 + phase)))
            pygame.draw.circle(self.screen, (twinkle, twinkle + 12, min(255, twinkle + 32)),
                               (scene.left + sx, scene.top + sy), 1 if index % 3 else 2)

        moon_center = (scene.right - 177, scene.top + 67)
        pygame.draw.circle(self.screen, (101, 133, 167), moon_center, 35)
        pygame.draw.circle(self.screen, (227, 218, 185), moon_center, 28)
        pygame.draw.circle(self.screen, (203, 199, 177), (moon_center[0] - 11, moon_center[1] - 9), 3)
        pygame.draw.circle(self.screen, (203, 199, 177), (moon_center[0] + 12, moon_center[1] + 5), 4)

        pygame.draw.polygon(self.screen, (37, 52, 78), [
            (scene.left, scene.top + 231), (scene.left + 183, scene.top + 109),
            (scene.left + 297, scene.top + 224), (scene.left + 450, scene.top + 105),
            (scene.left + 619, scene.top + 234), (scene.left + 774, scene.top + 121),
            (scene.left + 945, scene.top + 232), (scene.right, scene.top + 157),
            (scene.right, scene.top + 258), (scene.left, scene.top + 258),
        ])
        pygame.draw.polygon(self.screen, (50, 66, 84), [
            (scene.left, scene.top + 259), (scene.left + 232, scene.top + 178),
            (scene.left + 383, scene.top + 267), (scene.left + 576, scene.top + 164),
            (scene.left + 765, scene.top + 259), (scene.left + 945, scene.top + 181),
            (scene.right, scene.top + 246), (scene.right, scene.bottom),
            (scene.left, scene.bottom),
        ])

        ground_top = scene.top + 224
        for row in range(scene.bottom - ground_top):
            shade = min(45, row // 3)
            pygame.draw.line(self.screen, (22 + shade // 3, 39 + shade, 40 + shade // 2),
                             (scene.left, ground_top + row), (scene.right, ground_top + row))
        pygame.draw.line(self.screen, (103, 127, 116), (scene.left, ground_top),
                         (scene.right, ground_top), 2)

        for ruin_x, ruin_scale in ((scene.left + 69, 1.0), (scene.right - 108, 0.84)):
            base_y = ground_top + 29
            pygame.draw.rect(self.screen, (44, 58, 69),
                             (int(ruin_x), int(base_y - 83 * ruin_scale),
                              int(17 * ruin_scale), int(83 * ruin_scale)))
            pygame.draw.rect(self.screen, (61, 75, 82),
                             (int(ruin_x - 5 * ruin_scale), int(base_y - 88 * ruin_scale),
                              int(27 * ruin_scale), int(8 * ruin_scale)))
            pygame.draw.rect(self.screen, (40, 55, 65),
                             (int(ruin_x + 31 * ruin_scale), int(base_y - 56 * ruin_scale),
                              int(13 * ruin_scale), int(56 * ruin_scale)))
            pygame.draw.rect(self.screen, (61, 75, 82),
                             (int(ruin_x + 28 * ruin_scale), int(base_y - 61 * ruin_scale),
                              int(19 * ruin_scale), int(7 * ruin_scale)))

        for index in range(17):
            blade_x = scene.left + ((index * 67 + 24) % scene.width)
            blade_y = ground_top + 35 + (index * 29) % 43
            pygame.draw.line(self.screen, (42, 81, 64), (blade_x, blade_y),
                             (blade_x + (index % 5) - 2, blade_y - 7 - (index % 6)), 2)

        for peak_x, peak_y, width in (
            (scene.left + 183, scene.top + 109, 30),
            (scene.left + 450, scene.top + 105, 34),
            (scene.left + 774, scene.top + 121, 28),
        ):
            pygame.draw.polygon(self.screen, (108, 129, 151), [
                (peak_x - width // 2, peak_y + 20),
                (peak_x, peak_y),
                (peak_x + width // 2, peak_y + 20),
                (peak_x + width // 4, peak_y + 15),
                (peak_x, peak_y + 8),
                (peak_x - width // 5, peak_y + 16),
            ])

        for torch_x in (scene.left + 119, scene.right - 144):
            torch_y = ground_top + 8
            pygame.draw.rect(self.screen, (81, 56, 48), (torch_x, torch_y, 4, 21))
            flame_offset = int(now / 100) % 2
            pygame.draw.rect(self.screen, (229, 113, 63), (torch_x - 2, torch_y - 7 - flame_offset, 8, 8))
            pygame.draw.rect(self.screen, (255, 208, 111), (torch_x, torch_y - 5 - flame_offset, 4, 4))

        for stone_x, stone_y, stone_width in (
            (scene.left + 274, ground_top + 35, 18),
            (scene.left + 290, ground_top + 32, 13),
            (scene.left + 791, ground_top + 47, 22),
            (scene.left + 811, ground_top + 43, 14),
            (scene.left + 517, ground_top + 58, 16),
        ):
            pygame.draw.rect(self.screen, (76, 83, 77), (stone_x, stone_y, stone_width, 6))
            pygame.draw.rect(self.screen, (105, 111, 97), (stone_x + 2, stone_y, stone_width // 2, 2))

        if self.combat_enemy:
            hero_x, enemy_x = scene.left + 366, scene.left + 735
            hero_y = ground_top + 32
            enemy_y = ground_top + 32
            ring_y = ground_top + 29
            pygame.draw.ellipse(self.screen, (54, 114, 107), (hero_x - 64, ring_y - 6, 128, 18), 2)
            pygame.draw.ellipse(self.screen, (144, 81, 90), (enemy_x - 70, ring_y - 5, 140, 17), 2)

            self._draw_battle_sprite((hero_x, hero_y), player.species, now, scale=3.6,
                                     action_until=self.hero_action_until)
            enemy_scale = 4.05 if self.combat_enemy == "Elder Dragon" else 3.6
            self._draw_battle_sprite((enemy_x, enemy_y), self.combat_enemy, now, scale=enemy_scale,
                                     action_until=self.enemy_action_until, enemy=True)
        elif player is not None:
            center = (scene.centerx, ground_top + 29)
            pulse = int(2 * math.sin(now / 340))
            pygame.draw.ellipse(self.screen, (47, 91, 94), (center[0] - 99 - pulse, center[1] + 42, 198 + pulse * 2, 26), 2)
            pygame.draw.ellipse(self.screen, (76, 135, 118), (center[0] - 77, center[1] + 47, 154, 15), 1)
            self._draw_battle_sprite(center, player.species, now, scale=4.5,
                                     action_until=self.hero_action_until)

        scene_pixels = self.screen.subsurface(scene).copy()
        pixel_size = (max(1, scene.width // 2), max(1, scene.height // 2))
        pixel_art = pygame.transform.scale(
            pygame.transform.scale(scene_pixels, pixel_size),
            scene.size,
        )
        self.screen.blit(pixel_art, scene.topleft)
        self.screen.set_clip(None)
        pygame.draw.rect(self.screen, (91, 119, 137), scene, width=2)
        pygame.draw.rect(self.screen, colors["border"], scene.inflate(-6, -6), width=1)
        for x, y in ((scene.left + 9, scene.top + 9), (scene.right - 9, scene.top + 9),
                     (scene.left + 9, scene.bottom - 9), (scene.right - 9, scene.bottom - 9)):
            pygame.draw.rect(self.screen, colors["gold"], (x - 2, y - 2, 4, 4))

        if player is not None:
            self.screen.blit(self.small_font.render(
                f"{player.name}  ·  LEVEL {player.level}", True, colors["text"]),
                (scene.left + 34, scene.top + 79))
            pygame.draw.rect(self.screen, (12, 20, 30), (scene.left + 34, scene.top + 101, 188, 9))
            hp_fraction = max(0, min(1, player.hp / max(1, player.base_max_hp)))
            pygame.draw.rect(self.screen, colors["red"],
                             (scene.left + 34, scene.top + 101, int(188 * hp_fraction), 9))
            pygame.draw.rect(self.screen, (12, 20, 30), (scene.left + 34, scene.top + 116, 188, 5))
            xp_fraction = max(0, min(1, player.exp / max(1, player.exp_needed)))
            pygame.draw.rect(self.screen, colors["blue"],
                             (scene.left + 34, scene.top + 116, int(188 * xp_fraction), 5))
            self.screen.blit(self.small_font.render(
                f"ATK {player.total_power}   DEF {player.total_defence}", True, colors["text"]),
                (scene.left + 34, scene.top + 129))

            if self.combat_enemy:
                hero_x, enemy_x = scene.left + 366, scene.left + 735
                self.screen.blit(self.small_font.render(player.name, True, colors["text"]),
                                 (hero_x - 84, scene.top + 112))
                self.screen.blit(self.small_font.render(self.combat_enemy, True, colors["text"]),
                                 (enemy_x - 88, scene.top + 112))
                pygame.draw.rect(self.screen, (12, 20, 30), (hero_x - 84, scene.top + 140, 168, 11))
                pygame.draw.rect(self.screen, colors["red"],
                                 (hero_x - 84, scene.top + 140,
                                  int(168 * max(0, min(1, player.hp / max(1, player.base_max_hp)))), 11))
                pygame.draw.rect(self.screen, (12, 20, 30), (enemy_x - 88, scene.top + 140, 176, 11))
                enemy_fraction = max(0, min(1, self.combat_hp / max(1, self.combat_max_hp)))
                pygame.draw.rect(self.screen, (202, 82, 99),
                                 (enemy_x - 88, scene.top + 140, int(176 * enemy_fraction), 11))
            else:
                self.screen.blit(self.small_font.render(
                    "THE SHATTERED FRONTIER", True, (144, 225, 202)),
                    (scene.left + 34, scene.top + 23))
                self.screen.blit(self.small_font.render(
                    "Moonlit ruins  /  The wilds", True, (178, 193, 207)),
                    (scene.left + 34, scene.top + 42))

        if self.damage_effect and now < self.damage_effect[2]:
            label, x, expires, color = self.damage_effect
            progress = 1 - (expires - now) / 850
            popup = self.body_font.render(label, True, color)
            self.screen.blit(popup, (x - popup.get_width() // 2,
                                     int(scene.top + 181 - progress * 34)))
        elif self.damage_effect:
            self.damage_effect = None

    def draw(self):
        now = pygame.time.get_ticks()
        colors = self.colors
        self.screen.fill(colors["background"])

        pygame.draw.rect(self.screen, colors["panel"], (0, 0, 1120, 72))
        pygame.draw.line(self.screen, colors["border"], (0, 71), (1120, 71), 1)
        pygame.draw.polygon(self.screen, colors["accent"], [(29, 19), (43, 12), (57, 19), (57, 39), (43, 48), (29, 39)])
        pygame.draw.polygon(self.screen, colors["panel_light"], [(36, 22), (43, 18), (50, 22), (50, 36), (43, 41), (36, 36)])
        pygame.draw.circle(self.screen, colors["gold"], (43, 29), 3)
        self.screen.blit(self.title_font.render("REALMFORGE", True, colors["text"]), (70, 14))
        self.screen.blit(self.small_font.render("A TEXT RPG ADVENTURE", True, colors["muted"]), (72, 48))

        player = GAME_PLAYER
        if player is not None:
            summary = f"{player.name}   |   {player.species}  •  LEVEL {player.level}"
            self.screen.blit(self.body_font.render(summary, True, colors["text"]), (650, 25))
            self.screen.blit(self.small_font.render(f"{player.gold:,} GOLD", True, colors["gold"]), (985, 28))

        self._draw_battle_scene(player, now)

        output_rect = pygame.Rect(28, 424, 1064, 233)
        pygame.draw.rect(self.screen, colors["panel"], output_rect)
        pygame.draw.rect(self.screen, colors["border"], output_rect, width=1)
        menu_pages = self._get_menu_pages() if self.prompt else []
        menu_mode = bool(menu_pages)
        if menu_mode:
            page_count = len(menu_pages)
            page_index = min(self.menu_page, page_count - 1)
            visible_lines = menu_pages[page_index]
            page_label = f"Menu page {page_index + 1}/{page_count}"
        else:
            page_count = max(1, (len(self.output_lines) + self.page_size - 1) // self.page_size)
            page_index = max(0, page_count - 1 - min(self.history_page, page_count - 1))
            start_index = page_index * self.page_size
            visible_lines = [
                (index, self.output_lines[index])
                for index in range(start_index, min(start_index + self.page_size, len(self.output_lines)))
            ]
            page_label = f"Log page {page_index + 1}/{page_count}"

        if menu_mode:
            log_title = "CHOOSE AN OPTION"
        else:
            log_title = "BATTLE LOG" if self.combat_enemy else "ADVENTURE LOG"
        self.screen.blit(self.small_font.render(log_title, True, colors["accent"]), (48, 438))
        self.screen.blit(self.small_font.render(page_label, True, colors["muted"]), (889, 438))
        previous_rect = pygame.Rect(1010, 435, 26, 22)
        next_rect = pygame.Rect(1042, 435, 26, 22)
        self.page_regions = []
        can_go_previous = page_index > 0 if menu_mode else self.history_page < page_count - 1
        can_go_next = page_index < page_count - 1 if menu_mode else self.history_page > 0
        for rect, label, enabled, direction in (
            (previous_rect, "<", can_go_previous, -1),
            (next_rect, ">", can_go_next, 1),
        ):
            fill = colors["panel_light"] if enabled else colors["panel"]
            text_color = colors["accent"] if enabled else colors["muted"]
            pygame.draw.rect(self.screen, fill, rect)
            pygame.draw.rect(self.screen, colors["border"], rect, width=1)
            rendered = self.small_font.render(label, True, text_color)
            self.screen.blit(rendered, rendered.get_rect(center=rect.center))
            if enabled:
                self.page_regions.append((rect, direction, menu_mode))
        pygame.draw.line(self.screen, colors["border"], (48, 463), (1072, 463), 1)

        line_height = self.log_font.get_linesize()
        self.click_regions = []
        y = 469 + max(0, (self.page_size - len(visible_lines)) // 2) * line_height
        log_clip = pygame.Rect(44, 467, 1032, 184)
        self.screen.set_clip(log_clip)
        for index, line in visible_lines:
            color = colors["text"]
            match = re.match(r"^\s*(\d+)[.)]\s+", line)
            if match and menu_mode:
                color = colors["accent"]
            line_top = y
            y = self._draw_wrapped(line, self.log_font, color, 48, y, 1018)
            if match and menu_mode and line_top < log_clip.bottom and y > log_clip.top:
                option_rect = pygame.Rect(40, line_top, 1035, max(line_height, y - line_top))
                self.click_regions.append((option_rect, match.group(1)))
        self.screen.set_clip(None)

        pygame.draw.rect(self.screen, colors["panel_light"], self.input_rect)
        pygame.draw.rect(self.screen, colors["accent"] if self.prompt else colors["border"], self.input_rect, width=1)
        prompt = self.prompt or "Waiting for the next adventure..."
        prompt_color = colors["accent"] if self.prompt else colors["muted"]
        self.screen.blit(self.small_font.render(prompt[:90], True, prompt_color), (48, 683))
        available_width = 1010
        input_display = self.input_text
        while input_display and self.body_font.size(input_display)[0] > available_width:
            input_display = input_display[1:]
        self.screen.blit(self.body_font.render(input_display, True, colors["text"]), (48, 702))
        if self.prompt and now % 1000 < 500:
            cursor_x = 50 + self.body_font.size(input_display)[0]
            pygame.draw.line(self.screen, colors["accent"], (cursor_x, 703), (cursor_x, 722), 2)

        pygame.display.flip()

    def get_input(self, prompt=""):
        self.prompt = str(prompt)
        self.input_text = ""
        first_option = next(
            (index for index, line in enumerate(self.output_lines[self.menu_start:], self.menu_start)
             if re.match(r"^\s*\d+[.)]\s+", line)),
            None,
        )
        if first_option is not None:
            self.menu_start = first_option
            self.menu_page = 0
            self.history_page = 0
        else:
            self.history_page = 0
        pygame.key.start_text_input()
        self.draw()
        try:
            while self.running:
                self.clock.tick(30)
                self.draw()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        raise GameExit
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        page_clicked = False
                        for rect, direction, is_menu in self.page_regions:
                            if rect.collidepoint(event.pos):
                                if is_menu:
                                    self.menu_page += direction
                                else:
                                    self.history_page -= direction
                                page_clicked = True
                                self.draw()
                                break
                        if page_clicked:
                            continue
                        for rect, option in self.click_regions:
                            if rect.collidepoint(event.pos):
                                self.output_lines.append(f"> {option}")
                                self.prompt = ""
                                self.input_text = ""
                                self.menu_start = len(self.output_lines)
                                self.menu_page = 0
                                self.history_page = 0
                                self.draw()
                                return option
                    if event.type == pygame.TEXTINPUT:
                        self.input_text += event.text
                        self.draw()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            value = self.input_text
                            self.output_lines.append(f"> {value}")
                            self.prompt = ""
                            self.input_text = ""
                            self.menu_start = len(self.output_lines)
                            self.menu_page = 0
                            self.history_page = 0
                            self.draw()
                            return value
                        if event.key == pygame.K_BACKSPACE:
                            self.input_text = self.input_text[:-1]
                            self.draw()
                        elif event.key == pygame.K_PAGEUP:
                            if self.prompt and self._get_menu_pages():
                                self.menu_page = max(0, self.menu_page - 1)
                            else:
                                page_count = max(1, (len(self.output_lines) + self.page_size - 1) // self.page_size)
                                self.history_page = min(page_count - 1, self.history_page + 1)
                            self.draw()
                        elif event.key == pygame.K_PAGEDOWN:
                            if self.prompt and self._get_menu_pages():
                                self.menu_page = min(len(self._get_menu_pages()) - 1, self.menu_page + 1)
                            else:
                                self.history_page = max(0, self.history_page - 1)
                            self.draw()
            raise GameExit
        finally:
            pygame.key.stop_text_input()


def main():
    global GAME_PLAYER

    print("=========================================================")
    print("        REALMFORGE: A GRAPHICAL RPG ADVENTURE           ")
    print("=========================================================")
    
    player = load_game()
    if not player:
        print("\nSelect Species:")
        print("  A. Human   (XP Bonus & Firearms)")
        print("  B. Vampire (Life-Drain & High HP)")
        print("  C. Cyborg  (High Natural Defense)")
        print("  D. Elf     (Poison & Critical Burst)")
        
        sp = input("Choice (A/B/C/D): ").strip().lower()
        nm = input("Player Name: ").strip()
        player = Player(nm, sp)

    GAME_PLAYER = player
    while True:
        cd_str = f" [CD: {player.mining_cooldown}]" if player.mining_cooldown > 0 else " [READY]"
        print("\n================ MAIN MENU ================")
        print(f"{player.name} ({player.species}) | Lvl {player.level} | Gold: {player.gold} | HP: {player.hp}/{player.base_max_hp}")
        print("  1. Explore Wilderness")
        print(f"  2. Mine Resources{cd_str}")
        print("  3. Hunt for Food & Heal")
        print("  4. Arena Combat")
        print("  5. Manage Clan Headquarters")
        print("  6. Crafting Bench & Material Refining")
        print("  7. Skill Trainer Academy (Unlock New Attacks)")
        print("  8. Marketplace & Kingdom Bank (Buy/Sell Goods)")
        print("  9. View Inventory & Stats")
        print("  10. Save Game Progress")
        print("  0. Exit")

        ch = input("\nChoice #: ").strip()

        if ch == "1": explore(player)
        elif ch == "2": mine(player)
        elif ch == "3":
            player.heal(35)
            player.tick_cooldowns()
            print(f"\nRested and ate food! HP restored to {player.hp}/{player.base_max_hp}.")
        elif ch == "4": fight_an_enemy(player)
        elif ch == "5": clan_management_dashboard(player)
        elif ch == "6": craft_something(player)
        elif ch == "7": skill_trainer_shop(player)
        elif ch == "8": merchant_marketplace(player)
        elif ch == "9": view_inventory(player)
        elif ch == "10": save_game(player)
        elif ch == "0":
            print("\nExiting game...")
            break
        else:
            print("\n[ERROR] Invalid option!")

if __name__ == "__main__":
    window = GameWindow()
    original_input = builtins.input
    original_print = builtins.print
    builtins.input = window.get_input
    builtins.print = window.print_text
    try:
        main()
    except GameExit:
        pass
    finally:
        builtins.input = original_input
        builtins.print = original_print
        pygame.quit()