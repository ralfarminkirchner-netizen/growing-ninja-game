#!/usr/bin/env python3
"""
Demo driver for Growing Ninja (as-is prototype).
Plays a short automated session by feeding scripted answers.
Run this to see the game in action without manual input.
"""

import growing_ninja as gn
import builtins
import random
import sys

# Make runs reproducible but still feel random-ish
random.seed(42)

# Scripted answers for this demo run.
# We will play:
# - 1 full growing_ninja_session (it does 5 mini-games + possible barrels + boss)
# But sessions have many prompts, so we pre-supply a long enough list of reasonable answers.

# Reasonable answers for the various minigames:
# - wortarten_jump: a number 1-3
# - katana: something like "Apfel Baum" or "Haus Aufgabe" etc.
# - shooter: "ja", "nein", "nomen", "verb" etc.
# - math/sach: numbers or 1-3
# - shop / hub: mostly 0 to back out, or numbers
# - boss: similar

# We'll supply a generous pool of answers. The game will consume what it needs.
ANSWERS = [
    # For the initial name prompt (if it triggers)
    "",

    # We'll mostly let the session run and give decent answers
    "1", "2", "3",          # wordart / multiple choice
    "Apfel Baum", "Haus Aufgabe", "Regen Bogen", "Eisen Bahn",
    "ja", "nein", "nomen", "verb", "adjektiv", "nom", "ver", "adj",
    "1", "2", "3",
    "15", "7", "24", "5", "9", "4", "20",   # math answers, some right some wrong
    "0",                                    # often back out of shop / menus
    "1", "2", "3",
]

_answer_iter = iter(ANSWERS)

def scripted_input(prompt=""):
    try:
        ans = next(_answer_iter)
    except StopIteration:
        ans = "0"  # safe fallback to exit loops
    # Print what the game asked + what we answered (so you can follow along)
    if prompt:
        sys.stdout.write(f"{prompt}{ans}\n")
    else:
        sys.stdout.write(f"{ans}\n")
    sys.stdout.flush()
    return ans

def run_demo():
    print("\n" + "="*62)
    print("🥷 GROWING NINJA - AUTOMATED DEMO RUN (prototype as-is)")
    print("="*62 + "\n")

    # Fresh player for the demo
    gn.player.update({
        "name": "Demo-Ninja",
        "xp": 0,
        "gold": 40,
        "level": 1,
        "stage": "Genin",
        "upgrades": {"jump": 1, "star": 1, "strength": 1},
        "unlocked_stages": ["Genin"],
        "last_boss_xp": 0,
        "total_levels_played": 0
    })

    # Patch input for the whole run
    orig_input = builtins.input
    builtins.input = scripted_input

    try:
        # Simulate entering the main loop and choosing option 1 (start session) once
        # Then let one full session run (it will do 5 levels + barrels + possible boss)
        print(">>> Player starts at the HUB and chooses: Start Training Session\n")

        # We can't easily drive the full while-True main() without lots of menu answers.
        # Instead we directly call the core "play a session" function that the user would reach.
        gn.growing_ninja_session()

        print("\n" + "="*62)
        print("SESSION COMPLETE - Demo run finished.")
        print("="*62)
        gn.show_status()
        print(f"\nUnlocked stages: {', '.join(gn.player['unlocked_stages'])}")
        print(f"Total levels played this demo: {gn.player['total_levels_played']}")

    finally:
        builtins.input = orig_input

if __name__ == "__main__":
    run_demo()
