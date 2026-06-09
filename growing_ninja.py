#!/usr/bin/env python3
"""
GROWING NINJA - Terminal Prototype
Gamification-Lernspiel für Grundschule (Deutsch, Mathe, Sachunterricht)
Mit Schülern gemeinsam erweiterbar!

Alle Mechaniken enthalten:
- Hub/Regal
- Wachstum + Transformationen (Genin → Kage)
- Jump & Run (Wortarten)
- Katana Komposita-Slice
- Ninja-Stern Shooter (mit Schrumpf-Strafe)
- Mystery Fässer (Gold vs Challenge)
- Boss-Kämpfe
- Shop mit Gold
- Speichern/Laden
"""

import json
import random
import os
import time
from datetime import datetime

# ====================== FARBCODES (ANSI) ======================
class C:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    CYAN = '\033[96m'

def print_header(text):
    print(f"\n{C.HEADER}{C.BOLD}{'='*60}{C.ENDC}")
    print(f"{C.HEADER}{C.BOLD}{text.center(60)}{C.ENDC}")
    print(f"{C.HEADER}{C.BOLD}{'='*60}{C.ENDC}\n")

def print_success(text):
    print(f"{C.GREEN}✅ {text}{C.ENDC}")

def print_warning(text):
    print(f"{C.YELLOW}⚠️  {text}{C.ENDC}")

def print_fail(text):
    print(f"{C.RED}❌ {text}{C.ENDC}")

# ====================== SPIELER-DATEN ======================
player = {
    "name": "Ninja-Schüler",
    "xp": 0,
    "gold": 40,
    "level": 1,
    "stage": "Genin",
    "upgrades": {"jump": 1, "star": 1, "strength": 1},
    "unlocked_stages": ["Genin"],
    "last_boss_xp": 0,
    "total_levels_played": 0
}

QUESTIONS_DB = {
    "wortarten": [
        {"q": "Welche Wortart ist 'Hund'?", "options": ["Nomen (Dingworts)", "Verb (Tuworts)", "Adjektiv (Wieworts)"], "correct": 0, "xp": 12},
        {"q": "Welche Wortart ist 'schnell'?", "options": ["Nomen", "Verb", "Adjektiv (Wieworts)"], "correct": 2, "xp": 12},
        {"q": "Welche Wortart ist 'laufen'?", "options": ["Nomen", "Verb (Tuworts)", "Adjektiv"], "correct": 1, "xp": 12},
        {"q": "Welche Wortart ist 'Schule'?", "options": ["Nomen (Dingworts)", "Verb", "Adjektiv"], "correct": 0, "xp": 12},
        {"q": "Welche Wortart ist 'schön'?", "options": ["Nomen", "Verb", "Adjektiv (Wieworts)"], "correct": 2, "xp": 12},
        {"q": "Welche Wortart ist 'lesen'?", "options": ["Nomen", "Verb (Tuworts)", "Adjektiv"], "correct": 1, "xp": 12},
    ],
    "komposita": [
        {"word": "Apfelbaum", "parts": ["Apfel", "Baum"], "xp": 15},
        {"word": "Schulranzen", "parts": ["Schul", "Ranzen"], "xp": 15},
        {"word": "Fußballplatz", "parts": ["Fußball", "Platz"], "xp": 15},
        {"word": "Hausaufgabe", "parts": ["Haus", "Aufgabe"], "xp": 15},
        {"word": "Eisenbahn", "parts": ["Eisen", "Bahn"], "xp": 15},
        {"word": "Regenbogen", "parts": ["Regen", "Bogen"], "xp": 15},
    ],
    "mathe": [
        {"q": "Was ist 7 + 8?", "answer": 15, "xp": 10},
        {"q": "Was ist 12 - 5?", "answer": 7, "xp": 10},
        {"q": "Was ist 6 × 4?", "answer": 24, "xp": 12},
        {"q": "Ein Ninja hat 9 Sterne. Er wirft 4 weg. Wie viele bleiben?", "answer": 5, "xp": 12},
        {"q": "Was ist 20 ÷ 4?", "answer": 5, "xp": 12},
    ],
    "sachkunde": [
        {"q": "Welches Tier ist ein Säugetier?", "options": ["Fisch", "Vogel", "Hund"], "correct": 2, "xp": 14},
        {"q": "Wie viele Beine hat eine Spinne?", "options": ["6", "8", "10"], "correct": 1, "xp": 14},
        {"q": "Was braucht eine Pflanze zum Wachsen?", "options": ["Nur Wasser", "Wasser + Licht + Luft", "Nur Erde"], "correct": 1, "xp": 14},
        {"q": "Welche Jahreszeit kommt nach dem Winter?", "options": ["Herbst", "Frühling", "Sommer"], "correct": 1, "xp": 12},
        {"q": "Wo sitzt das Herz im Körper?", "options": ["Links", "Rechts", "Mitte"], "correct": 0, "xp": 14},
    ]
}

def save_game():
    with open("growing_ninja_save.json", "w", encoding="utf-8") as f:
        json.dump(player, f, indent=2, ensure_ascii=False)
    print_success("Fortschritt gespeichert!")

def load_game():
    global player
    if os.path.exists("growing_ninja_save.json"):
        with open("growing_ninja_save.json", "r", encoding="utf-8") as f:
            loaded = json.load(f)
            player.update(loaded)
        print(f"{C.CYAN}Willkommen zurück, {player['name']}!{C.ENDC}")

def calculate_stage(xp):
    if xp >= 900: return "Kage (Legendär)"
    elif xp >= 600: return "Elite Super Ninja"
    elif xp >= 350: return "Jonin"
    elif xp >= 180: return "Chunin"
    else: return "Genin"

def apply_transformation():
    new_stage = calculate_stage(player["xp"])
    if new_stage != player["stage"]:
        old_stage = player["stage"]
        player["stage"] = new_stage
        if new_stage not in player["unlocked_stages"]:
            player["unlocked_stages"].append(new_stage)
        
        print_header("🌟🌟🌟 VERWANDLUNG! 🌟🌟🌟")
        print(f"{C.BOLD}{C.HEADER}Dein Ninja entwickelt sich weiter!{C.ENDC}")
        print(f"  {old_stage}  →  {C.BOLD}{new_stage}{C.ENDC}")
        
        if "Super" in new_stage or "Kage" in new_stage:
            print(f"{C.YELLOW}💥 Neue Kräfte freigeschaltet! Höhere Sprünge, stärkere Sterne, mehr Ausdauer!{C.ENDC}")
        print(f"{C.GREEN}Du bist jetzt deutlich stärker und schneller!{C.ENDC}")
        time.sleep(2.2)

def show_status():
    stage = player["stage"]
    size = min(5, 1 + player["level"] // 2)
    bar = "█" * size + "░" * (6 - size)
    
    # Small visual ninja that "grows"
    ninja_art = {
        "Genin": "🥷",
        "Chunin": "🥷",
        "Jonin": "🗡️🥷",
        "Elite Super Ninja": "🔥🥷",
        "Kage (Legendär)": "👑🥷"
    }.get(stage, "🥷")
    
    print(f"\n{C.BOLD}{ninja_art} {player['name']}  |  Stufe: {C.HEADER}{stage}{C.ENDC}  |  Level {player['level']}")
    print(f"XP: {player['xp']}   Gold: {player['gold']}   Größe & Kraft: [{bar}]")
    print(f"Upgrades → Sprung: {player['upgrades']['jump']}  |  Sterne: {player['upgrades']['star']}  |  Kraft: {player['upgrades']['strength']}")

# ====================== MINI-SPIELE ======================
def play_wortarten_jump():
    print_header("🦘 JUMP & RUN - Wortarten-Plattformen")
    print("Springe nur auf die richtige Wortart! Falsch = Stolpern.")
    
    q = random.choice(QUESTIONS_DB["wortarten"])
    print(f"\n{C.BLUE}Aufgabe: {q['q']}{C.ENDC}")
    for i, opt in enumerate(q["options"], 1):
        print(f"  {i}. {opt}")
    
    try:
        choice = int(input("\nAuf welche Plattform springst du? (Nummer): "))
        if choice == q["correct"] + 1:
            xp = q["xp"] + (player["upgrades"]["jump"] * 3)
            player["xp"] += xp
            print_success(f"Perfekter Sprung! Der Ninja wird stärker. +{xp} XP")
        else:
            correct_answer = q["options"][q["correct"]]
            print_warning(f"Fast! Der Ninja stolpert. Richtige Antwort: {correct_answer}")
            player["xp"] += 4
    except ValueError:
        print_warning("Ungültige Eingabe. Der Ninja zögert...")

def play_katana_split():
    print_header("⚔️ KATANA - Komposita trennen")
    print("Schlage mit der Katana das zusammengesetzte Wort in zwei Teile!")
    
    comp = random.choice(QUESTIONS_DB["komposita"])
    print(f"\n{C.YELLOW}Wort: {comp['word']}{C.ENDC}")
    print("Schreibe die beiden Teile getrennt durch ein Leerzeichen oder |")
    
    answer = input("Dein Schnitt: ").strip().lower()
    parts_lower = [p.lower() for p in comp["parts"]]
    
    if answer.replace("|", " ").replace("-", " ") == " ".join(parts_lower):
        xp = comp["xp"] + (player["upgrades"]["strength"] * 2)
        player["xp"] += xp
        print_success(f"Sauberer Schnitt! Du siehst die einzelnen Wörter. +{xp} XP")
    else:
        print_warning(f"Noch nicht ganz perfekt. Richtig wäre: {' + '.join(comp['parts'])}")
        player["xp"] += 5

def play_shooter():
    print_header("🎯 NINJA-STERN SHOOTER (Ego-Shooter Style)")
    print("Wörter fliegen auf dich zu! Wirf den Stern auf die richtige Kategorie.")
    print("Zu viele Fehler = Der Ninja schrumpft ein bisschen vor Scham...\n")
    
    mistakes = 0
    objective = random.choice(["Nomen", "Verb", "Adjektiv"])
    print(f"{C.CYAN}Ziel dieses Levels: Triff möglichst viele {objective}!{C.ENDC}")
    
    for i in range(6):
        pool = QUESTIONS_DB["wortarten"]
        q = random.choice(pool)
        word = q["q"].split("'")[1] if "'" in q["q"] else "Wort"
        cat = q["options"][q["correct"]].split()[0]
        
        print(f"\nEs fliegt: {C.BOLD}{word}{C.ENDC}   (Kategorie: {cat})")
        ans = input("Wirf Stern auf diese Kategorie? (ja/nein oder Kategorie-Name): ").strip().lower()
        
        is_correct_category = (objective.lower() in cat.lower()) or (ans.startswith("j") and objective.lower() in cat.lower())
        
        if is_correct_category or ans == objective.lower()[:3]:
            xp = 8 + (player["upgrades"]["star"] * 2)
            player["xp"] += xp
            print_success(f"Treffer! Guter Wurf. +{xp} XP")
        else:
            mistakes += 1
            print_fail(f"Verfehlt! Das Wort verwandelt sich... ({mistakes}/3 Fehler)")
            if mistakes >= 3:
                print_warning("Der Ninja schrumpft etwas... aber er wird klüger!")
                break
    
    if mistakes < 3:
        print_success("Gute Reflexe, Ninja!")

def play_math_or_sach():
    print_header("🧠 MATHE oder SACHUNTERRICHT Challenge")
    category = random.choice(["mathe", "sachkunde"])
    q = random.choice(QUESTIONS_DB[category])
    
    print(f"\n{C.BLUE}{q['q']}{C.ENDC}")
    
    if category == "mathe":
        try:
            ans = int(input("Deine Antwort: "))
            if ans == q["answer"]:
                xp = q["xp"] + (player["upgrades"]["strength"] * 2)
                player["xp"] += xp
                print_success(f"Richtig gerechnet! +{xp} XP")
            else:
                print_warning(f"Falsch. Die richtige Antwort war {q['answer']}")
                player["xp"] += 5
        except:
            print_warning("Das war keine Zahl...")
    else:
        for i, opt in enumerate(q["options"], 1):
            print(f"  {i}. {opt}")
        try:
            choice = int(input("Deine Wahl: "))
            if choice == q["correct"] + 1:
                xp = q["xp"] + (player["upgrades"]["jump"] * 2)
                player["xp"] += xp
                print_success(f"Super! +{xp} XP")
            else:
                print_warning(f"Richtige Antwort: {q['options'][q['correct']]}")
                player["xp"] += 5
        except:
            print_warning("Ungültige Eingabe.")

def open_mystery_barrel():
    print_header("🛢️  MYSTERY FASS")
    print("Du trittst das Fass auf... Was ist drin?")
    time.sleep(1.2)
    
    if random.random() < 0.62:
        gold = random.randint(18, 55)
        player["gold"] += gold
        print_success(f"Gold! Du findest {gold} Goldstücke.")
    else:
        print_warning("Eine Checkbalt-Herausforderung erscheint!")
        play_quick_challenge()

def play_quick_challenge():
    print("\nSchnelle Bonus-Challenge für Extra-XP!")
    play_wortarten_jump()  # oder eine andere kurze Mechanik

def play_boss():
    print_header("👹 BOSS-KAMPF!")
    print(f"{C.RED}{C.BOLD}Der große Wissens-Boss erscheint!{C.ENDC}")
    print("Zeige, was du gelernt hast – 5 Runden!")
    
    wins = 0
    for i in range(5):
        cat = random.choice(list(QUESTIONS_DB.keys()))
        q = random.choice(QUESTIONS_DB[cat])
        print(f"\nRunde {i+1}: {q.get('q', q.get('word', 'Aufgabe'))}")
        
        correct = False
        if cat == "mathe":
            try:
                ans = int(input("Antwort: "))
                correct = (ans == q["answer"])
            except:
                pass
        elif cat == "komposita":
            ans = input("Trennung: ").strip().lower()
            parts = [p.lower() for p in q["parts"]]
            correct = ans.replace("|"," ").replace("-"," ") == " ".join(parts)
        else:
            for j, opt in enumerate(q.get("options", []), 1):
                print(f"  {j}. {opt}")
            try:
                choice = int(input("Wahl: "))
                correct = (choice == q["correct"] + 1)
            except:
                pass
        
        if correct:
            wins += 1
            print_success("Treffer!")
        else:
            print_fail("Der Boss wehrt ab...")
    
    if wins >= 4:
        reward_xp = 70 + (player["level"] * 5)
        reward_gold = 80
        player["xp"] += reward_xp
        player["gold"] += reward_gold
        print_success(f"BOOOOOOSSS BESIEGT! +{reward_xp} XP  +{reward_gold} Gold")
        print(f"{C.YELLOW}Du erhältst eine mächtige Belohnung!{C.ENDC}")
    else:
        print_warning("Der Boss war stark... aber du hast viel gelernt. Nächstes Mal!")

def growing_ninja_session():
    print_header("🥷 GROWING NINJA - TRAINING BEGINNT")
    print("Du startest eine Trainingseinheit. Erledige Aufgaben, wachse und werde stärker!")
    
    for i in range(5):  # 5 Mini-Level pro Session
        print(f"\n--- Level {player['total_levels_played'] + 1} ---")
        mechanic = random.choice([
            play_wortarten_jump,
            play_katana_split,
            play_shooter,
            play_math_or_sach
        ])
        mechanic()
        
        player["total_levels_played"] += 1
        
        # Barrel Chance
        if random.random() < 0.55:
            open_mystery_barrel()
        
        apply_transformation()
        
        # Boss Check (alle ~120 XP oder nach 5 Levels)
        if (player["xp"] - player["last_boss_xp"] > 120) or (player["total_levels_played"] % 7 == 0 and player["total_levels_played"] > 3):
            play_boss()
            player["last_boss_xp"] = player["xp"]
        
        show_status()
        time.sleep(0.6)
    
    print_header("SESSION BEENDET")
    print(f"Du hast {player['total_levels_played']} Level gemeistert. Der Ninja ist gewachsen!")

def shop():
    print_header("🛍️ NINJA-SHOP")
    print(f"Dein Gold: {player['gold']}")
    print("\n1. Bessere Sprungkraft (+1)          - 45 Gold")
    print("2. Stärkere Ninja-Sterne (+1)       - 40 Gold")
    print("3. Mehr Kraft & Ausdauer (+1)       - 50 Gold")
    print("0. Zurück zum Hub")
    
    choice = input("\nWas möchtest du kaufen? ").strip()
    
    if choice == "1" and player["gold"] >= 45:
        player["gold"] -= 45
        player["upgrades"]["jump"] += 1
        print_success("Sprungkraft verbessert! Deine Sprünge sind jetzt höher.")
    elif choice == "2" and player["gold"] >= 40:
        player["gold"] -= 40
        player["upgrades"]["star"] += 1
        print_success("Sterne sind jetzt schneller und stärker!")
    elif choice == "3" and player["gold"] >= 50:
        player["gold"] -= 50
        player["upgrades"]["strength"] += 1
        print_success("Deine Angriffe und Ausdauer steigen!")
    elif choice == "0":
        return
    else:
        print_warning("Nicht genug Gold oder ungültige Wahl.")

def main():
    load_game()
    
    if player["name"] == "Ninja-Schüler":
        name = input("Wie heißt dein Ninja-Schüler? (oder Enter für Standard): ").strip()
        if name:
            player["name"] = name
    
    while True:
        show_status()
        print_header("🏯 GROWING NINJA HUB - DAS REGAL")
        print("1. Growing Ninja Session starten (trainieren & wachsen)")
        print("2. Shop besuchen (Gold für Upgrades ausgeben)")
        print("3. Ein freies Mystery-Fass öffnen")
        print("4. Status & Fortschritt detailliert ansehen")
        print("5. Andere Spiele vom Regal auswählen (kommt bald)")
        print("0. Speichern & Beenden")
        
        choice = input("\nDeine Wahl: ").strip()
        
        if choice == "1":
            growing_ninja_session()
        elif choice == "2":
            shop()
        elif choice == "3":
            open_mystery_barrel()
        elif choice == "4":
            show_status()
            print(f"\nFreigeschaltete Stufen: {', '.join(player['unlocked_stages'])}")
            print(f"Gesamt gespielte Level: {player['total_levels_played']}")
        elif choice == "0":
            save_game()
            print(f"\n{C.HEADER}Bis bald, {player['name']}! Der Ninja wartet auf dich.{C.ENDC}")
            break
        else:
            print_warning("Ungültige Eingabe.")

if __name__ == "__main__":
    main()
