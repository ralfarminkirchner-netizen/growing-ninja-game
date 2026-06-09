#!/usr/bin/env python3
"""
GROWING NINJA - Web Version (Flask)
Für Railway / Browser spielbar.
Wiederverwendet die gleichen Fragen und Mechaniken wie die Terminal-Version.
"""

from flask import Flask, render_template_string, request, session, redirect, url_for, flash
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "growing-ninja-secret-for-schools-2026")

# ====================== SPIEL-DATEN (aus Terminal-Version) ======================
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

STAGES = [
    (0, "Genin"),
    (180, "Chunin"),
    (350, "Jonin"),
    (600, "Elite Super Ninja"),
    (900, "Kage (Legendär)"),
]

UPGRADE_COSTS = {
    "jump": 45,
    "star": 40,
    "strength": 50,
}

def get_stage(xp):
    for threshold, name in reversed(STAGES):
        if xp >= threshold:
            return name
    return "Genin"

def get_player():
    if "player" not in session:
        session["player"] = {
            "name": "Web-Ninja",
            "xp": 0,
            "gold": 40,
            "upgrades": {"jump": 1, "star": 1, "strength": 1},
            "total_levels_played": 0,
        }
    return session["player"]

def save_player(p):
    session["player"] = p
    session.modified = True

def apply_transformation(p):
    new_stage = get_stage(p["xp"])
    old_stage = p.get("stage", "Genin")
    if new_stage != old_stage:
        p["stage"] = new_stage
        flash(f"🌟 VERWANDLUNG! {old_stage} → {new_stage}!", "success")
        if "Super" in new_stage or "Kage" in new_stage:
            flash("💥 Neue Kräfte freigeschaltet!", "success")
        return True
    return False

# ====================== HTML TEMPLATE (schön & kindgerecht) ======================
BASE_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🥷 Growing Ninja • Web</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;display=swap');
    .ninja-font { font-family: "Press Start 2P", system-ui; }
    .game-card { transition: transform .1s ease, box-shadow .1s ease; }
    .game-card:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); }
    .ninja-green { color: #22c55e; }
    .stage-badge {
      background: linear-gradient(90deg, #166534, #4ade80);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      font-weight: 700;
    }
    .feedback { animation: pop 0.3s ease; }
    @keyframes pop { 0% {transform:scale(0.8);opacity:0} 100%{transform:scale(1);opacity:1} }
  </style>
</head>
<body class="bg-zinc-950 text-zinc-200">
  <div class="max-w-5xl mx-auto p-4 md:p-8">
    <!-- HEADER -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-x-3">
        <div class="text-5xl">🥷</div>
        <div>
          <h1 class="text-4xl font-bold tracking-tighter ninja-font">GROWING NINJA</h1>
          <p class="text-emerald-400 text-sm -mt-1">Lernen • Wachsen • Kämpfen</p>
        </div>
      </div>
      <div class="flex items-center gap-x-2 text-sm">
        <a href="https://github.com/ralfarminkirchner-netizen/growing-ninja-game" target="_blank"
           class="px-3 py-1.5 rounded-xl bg-zinc-900 hover:bg-zinc-800 flex items-center gap-x-2 text-xs">
          <i class="fa-brands fa-github"></i>
          <span>GitHub</span>
        </a>
        <a href="/" class="px-4 py-1.5 rounded-2xl bg-emerald-600 hover:bg-emerald-500 font-semibold text-sm flex items-center gap-x-2">
          <i class="fa-solid fa-home"></i>
          <span>Hub</span>
        </a>
      </div>
    </div>

    <!-- STATUS BAR -->
    {% set p = player %}
    <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-5 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-y-4">
        <div>
          <div class="flex items-center gap-x-3">
            <span class="text-3xl">🥷</span>
            <div>
              <div class="font-bold text-2xl">{{ p.name }}</div>
              <div class="text-emerald-400 text-lg font-semibold stage-badge">{{ p.get('stage', 'Genin') }}</div>
            </div>
          </div>
        </div>

        <div class="flex-1 max-w-md">
          <div class="flex justify-between text-xs mb-1.5 text-zinc-400">
            <div>XP: <span class="font-mono text-emerald-400">{{ p.xp }}</span></div>
            <div>Gold: <span class="font-mono text-yellow-400">{{ p.gold }}</span></div>
          </div>
          <div class="h-3 bg-zinc-800 rounded-full overflow-hidden border border-zinc-700">
            {% set progress = min( (p.xp % 180) / 180 * 100, 100) %}
            <div class="h-3 bg-gradient-to-r from-emerald-400 to-lime-400 rounded-full transition-all"
                 style="width: {{ progress }}%"></div>
          </div>
          <div class="text-[10px] text-zinc-500 mt-1 flex justify-between">
            <div>Level {{ (p.total_levels_played // 3) + 1 }}</div>
            <div>Upgrades: Sprung {{ p.upgrades.jump }} • Sterne {{ p.upgrades.star }} • Kraft {{ p.upgrades.strength }}</div>
          </div>
        </div>

        <div class="flex gap-x-2">
          <form method="post" action="{{ url_for('reset') }}">
            <button type="submit" class="text-xs px-3 py-2 rounded-2xl bg-zinc-800 hover:bg-red-950 text-zinc-400 hover:text-red-400 border border-zinc-700">
              <i class="fa-solid fa-undo mr-1"></i> Reset
            </button>
          </form>
        </div>
      </div>
    </div>

    <!-- FLASH MESSAGES -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="mb-4 px-5 py-3 rounded-2xl text-sm feedback
            {% if category == 'success' %} bg-emerald-900/70 border border-emerald-700 text-emerald-300
            {% elif category == 'warning' %} bg-yellow-900/70 border border-yellow-700 text-yellow-300
            {% else %} bg-zinc-800 border border-zinc-700 {% endif %}">
            {{ message }}
          </div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}

    <div class="mt-10 text-center text-[10px] text-zinc-500">
      Terminal-Version verfügbar auf GitHub • Mit ❤️ für Grundschulkinder gemacht
    </div>
  </div>
</body>
</html>
"""

HUB_TEMPLATE = """
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

  <!-- Play Challenge -->
  <a href="{{ url_for('challenge') }}" 
     class="game-card group block bg-zinc-900 border border-emerald-800 hover:border-emerald-500 rounded-3xl p-6">
    <div class="flex items-start gap-x-4">
      <div class="text-4xl group-hover:scale-110 transition">🎯</div>
      <div class="flex-1">
        <div class="font-bold text-xl">Nächste Challenge</div>
        <div class="text-emerald-400 text-sm mt-1">Spring, schneide, rechne oder beantworte – werde stärker!</div>
        <div class="mt-4 inline-flex items-center text-xs px-3 py-1 rounded-full bg-emerald-900 text-emerald-300">
          <i class="fa-solid fa-play mr-2"></i> JETZT SPIELEN
        </div>
      </div>
    </div>
  </a>

  <!-- Mystery Barrel -->
  <form method="post" action="{{ url_for('barrel') }}" class="game-card block">
    <button type="submit" class="w-full text-left bg-zinc-900 border border-yellow-800 hover:border-yellow-500 rounded-3xl p-6">
      <div class="flex items-start gap-x-4">
        <div class="text-4xl">🛢️</div>
        <div>
          <div class="font-bold text-xl">Mystery Fass</div>
          <div class="text-yellow-400 text-sm mt-1">Tritt es auf! Gold oder eine schnelle Challenge?</div>
          <div class="mt-3 text-xs text-yellow-300">62% Chance auf 18–55 Gold</div>
        </div>
      </div>
    </button>
  </form>

  <!-- Shop -->
  <a href="{{ url_for('shop') }}" 
     class="game-card block bg-zinc-900 border border-sky-800 hover:border-sky-500 rounded-3xl p-6">
    <div class="flex items-start gap-x-4">
      <div class="text-4xl">🛍️</div>
      <div>
        <div class="font-bold text-xl">Ninja-Shop</div>
        <div class="text-sky-400 text-sm mt-1">Gold gegen dauerhafte Upgrades eintauschen</div>
        <div class="mt-4 text-xs">Sprungkraft • Sterne • Kraft</div>
      </div>
    </div>
  </a>

  <!-- Boss -->
  <form method="post" action="{{ url_for('boss') }}" class="game-card block">
    <button type="submit" class="w-full text-left bg-zinc-900 border border-red-800 hover:border-red-500 rounded-3xl p-6">
      <div class="flex items-start gap-x-4">
        <div class="text-4xl">👹</div>
        <div>
          <div class="font-bold text-xl">Boss-Kampf</div>
          <div class="text-red-400 text-sm mt-1">5 Runden. Nur die Stärksten gewinnen große Belohnungen!</div>
          <div class="mt-3 text-xs text-red-300">Mind. 4 von 5 richtig = Sieg</div>
        </div>
      </div>
    </button>
  </form>

</div>

<div class="mt-8 bg-zinc-900 border border-zinc-800 rounded-3xl p-5 text-sm">
  <div class="font-semibold mb-2 flex items-center gap-x-2">
    <i class="fa-solid fa-info-circle text-emerald-400"></i>
    <span>So funktioniert's</span>
  </div>
  <ul class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1 text-zinc-400 text-xs">
    <li>• Jede Challenge bringt XP und macht dich stärker</li>
    <li>• Mystery Fässer können Gold oder Extra-Aufgaben enthalten</li>
    <li>• Im Shop kaufst du dauerhafte Verbesserungen</li>
    <li>• Bei genug XP verwandelt sich dein Ninja (Genin → Kage)</li>
    <li>• Boss-Kämpfe geben große Belohnungen</li>
    <li>• Alles wird automatisch gespeichert (im Browser)</li>
  </ul>
</div>

<div class="mt-4 text-center">
  <a href="https://github.com/ralfarminkirchner-netizen/growing-ninja-game" target="_blank"
     class="text-xs text-zinc-400 hover:text-zinc-300 inline-flex items-center gap-x-1.5">
    <i class="fa-solid fa-terminal"></i>
    <span>Auch als richtiges Terminal-Spiel verfügbar (Python)</span>
  </a>
</div>
"""

CHALLENGE_TEMPLATE = """
<div class="max-w-2xl mx-auto">
  <div class="mb-4 flex items-center justify-between">
    <a href="{{ url_for('hub') }}" class="text-emerald-400 hover:text-emerald-300 text-sm flex items-center gap-x-1">
      <i class="fa-solid fa-arrow-left"></i> zurück zum Hub
    </a>
    <div class="text-xs px-3 py-1 bg-zinc-900 rounded-full border border-zinc-700">{{ challenge_type.upper() }}</div>
  </div>

  <div class="bg-zinc-900 border border-emerald-700 rounded-3xl p-7">
    <div class="text-2xl font-bold mb-6">{{ challenge.q if challenge.q else challenge.word }}</div>

    <form method="post" action="{{ url_for('submit') }}">
      <input type="hidden" name="type" value="{{ challenge_type }}">

      {% if challenge_type in ['wortarten', 'sachkunde'] %}
        <div class="space-y-3">
          {% for i, opt in enumerate(challenge.options) %}
          <button type="submit" name="choice" value="{{ i }}"
                  class="w-full text-left px-5 py-4 rounded-2xl border border-zinc-700 hover:border-emerald-500 bg-zinc-950 hover:bg-zinc-800 flex items-center gap-x-3 transition">
            <span class="font-mono w-6 text-emerald-400">{{ i+1 }}.</span>
            <span>{{ opt }}</span>
          </button>
          {% endfor %}
        </div>

      {% elif challenge_type == 'komposita' %}
        <div class="space-y-4">
          <div class="text-sm text-zinc-400">Schreibe die beiden Teile getrennt durch ein Leerzeichen oder |</div>
          <input type="text" name="answer" placeholder="z.B. Apfel Baum" required
                 class="w-full bg-black border border-zinc-700 focus:border-emerald-500 rounded-2xl px-5 py-3 text-lg font-medium">
          <button type="submit" 
                  class="mt-2 w-full py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 font-bold tracking-wider">
            KATANA-SCHNITT AUSFÜHREN ⚔️
          </button>
        </div>

      {% elif challenge_type == 'mathe' %}
        <div>
          <input type="number" name="answer" placeholder="Deine Antwort" required
                 class="w-full bg-black border border-zinc-700 focus:border-emerald-500 rounded-2xl px-5 py-3 text-3xl font-mono text-center">
          <button type="submit" 
                  class="mt-3 w-full py-4 rounded-2xl bg-emerald-600 hover:bg-emerald-500 font-bold">
            ANTWORT ABSCHICKEN
          </button>
        </div>
      {% endif %}
    </form>
  </div>

  <div class="text-center mt-4 text-xs text-zinc-500">Falsch antworten gibt trotzdem etwas XP. Weitermachen!</div>
</div>
"""

SHOP_TEMPLATE = """
<div class="max-w-xl mx-auto">
  <h2 class="text-2xl font-bold mb-6 flex items-center gap-x-3"><span>🛍️</span> Ninja-Shop</h2>

  <div class="bg-zinc-900 border border-zinc-800 rounded-3xl divide-y divide-zinc-800">
    {% for key, label, cost, desc in [
      ('jump', 'Bessere Sprungkraft (+1)', 45, 'Höhere Sprünge in Wortarten-Jump & Run'),
      ('star', 'Stärkere Ninja-Sterne (+1)', 40, 'Mehr Schaden und XP im Shooter'),
      ('strength', 'Mehr Kraft & Ausdauer (+1)', 50, 'Bessere Ergebnisse bei Katana + Mathe')
    ] %}
    <form method="post" action="{{ url_for('buy') }}" class="p-5 flex items-center justify-between gap-x-4">
      <input type="hidden" name="item" value="{{ key }}">
      <div>
        <div class="font-semibold">{{ label }}</div>
        <div class="text-xs text-zinc-400">{{ desc }}</div>
      </div>
      <button type="submit" class="shrink-0 px-6 py-2.5 rounded-2xl bg-sky-600 hover:bg-sky-500 font-medium text-sm disabled:opacity-40"
              {% if player.gold < cost %}disabled{% endif %}>
        {{ cost }} Gold
      </button>
    </form>
    {% endfor %}
  </div>

  <div class="mt-6 text-center">
    <a href="{{ url_for('hub') }}" class="text-emerald-400 hover:text-emerald-300 text-sm">← zurück zum Hub</a>
  </div>
</div>
"""

@app.route("/")
def hub():
    player = get_player()
    if "stage" not in player:
        player["stage"] = get_stage(player["xp"])
    full = BASE_HTML.replace("{% block content %}{% endblock %}", HUB_TEMPLATE)
    return render_template_string(full, player=player)

@app.route("/challenge")
def challenge():
    p = get_player()
    ctype = random.choice(list(QUESTIONS_DB.keys()))
    q = random.choice(QUESTIONS_DB[ctype])

    # Store the current challenge in session so we can validate later
    session["pending"] = {"type": ctype, "data": q}
    session.modified = True

    full = BASE_HTML.replace("{% block content %}{% endblock %}", CHALLENGE_TEMPLATE)
    return render_template_string(
        full,
        player=p,
        challenge=q,
        challenge_type=ctype
    )

@app.route("/submit", methods=["POST"])
def submit():
    p = get_player()
    pending = session.pop("pending", None)
    if not pending:
        flash("Keine offene Challenge gefunden.", "warning")
        return redirect(url_for("hub"))

    ctype = pending["type"]
    q = pending["data"]
    correct = False
    xp_gain = 4

    if ctype in ("wortarten", "sachkunde"):
        try:
            choice = int(request.form.get("choice", -1))
            if choice == q["correct"]:
                correct = True
                xp_gain = q["xp"] + (p["upgrades"].get("jump", 1) * 2)
        except:
            pass

    elif ctype == "komposita":
        ans = request.form.get("answer", "").strip().lower().replace("|", " ").replace("-", " ")
        parts = " ".join([x.lower() for x in q["parts"]])
        if ans == parts:
            correct = True
            xp_gain = q["xp"] + (p["upgrades"].get("strength", 1) * 2)

    elif ctype == "mathe":
        try:
            ans = int(request.form.get("answer", ""))
            if ans == q["answer"]:
                correct = True
                xp_gain = q["xp"] + (p["upgrades"].get("strength", 1) * 2)
        except:
            pass

    p["xp"] += xp_gain
    p["total_levels_played"] += 1

    if correct:
        flash(f"✅ Richtig! +{xp_gain} XP", "success")
    else:
        flash(f"⚠️ Fast geschafft. +{xp_gain} XP (Richtige Antwort: {q.get('answer') or q.get('parts') or q['options'][q['correct']]}) ", "warning")

    apply_transformation(p)
    save_player(p)
    return redirect(url_for("hub"))

@app.route("/barrel", methods=["POST"])
def barrel():
    p = get_player()
    if random.random() < 0.62:
        gold = random.randint(18, 55)
        p["gold"] += gold
        flash(f"✅ Gold! Du findest {gold} Goldstücke.", "success")
    else:
        flash("🛢️ Das Fass enthielt eine Challenge!", "warning")
        # Give a free quick challenge
        return redirect(url_for("challenge"))

    p["total_levels_played"] += 1
    apply_transformation(p)
    save_player(p)
    return redirect(url_for("hub"))

@app.route("/shop")
def shop():
    p = get_player()
    full = BASE_HTML.replace("{% block content %}{% endblock %}", SHOP_TEMPLATE)
    return render_template_string(full, player=p)

@app.route("/buy", methods=["POST"])
def buy():
    p = get_player()
    item = request.form.get("item")
    cost = UPGRADE_COSTS.get(item, 999)

    if p["gold"] >= cost:
        p["gold"] -= cost
        p["upgrades"][item] = p["upgrades"].get(item, 1) + 1
        flash(f"✅ Upgrade gekauft: {item} +1!", "success")
    else:
        flash("Nicht genug Gold!", "warning")

    save_player(p)
    return redirect(url_for("shop"))

@app.route("/boss", methods=["POST"])
def boss():
    p = get_player()
    wins = 0
    rounds = 4

    for _ in range(rounds):
        cat = random.choice(list(QUESTIONS_DB.keys()))
        q = random.choice(QUESTIONS_DB[cat])

        # Very simplified auto-check for demo purposes in web boss
        # In real version we could do sequential forms, but for now we simulate strong performance
        if random.random() > 0.35:   # slightly easier than pure random for kids
            wins += 1

    if wins >= 3:
        reward_xp = 65 + (p.get("total_levels_played", 0) // 2)
        reward_gold = 70
        p["xp"] += reward_xp
        p["gold"] += reward_gold
        flash(f"👹 BOOOOOOSSS BESIEGT! +{reward_xp} XP  +{reward_gold} Gold", "success")
    else:
        flash(f"Der Boss war stark... {wins}/{rounds} gewonnen. Du hast trotzdem viel gelernt!", "warning")

    apply_transformation(p)
    save_player(p)
    return redirect(url_for("hub"))

@app.route("/reset", methods=["POST"])
def reset():
    session.pop("player", None)
    session.pop("pending", None)
    flash("Fortschritt zurückgesetzt. Neuer Ninja bereit!", "success")
    return redirect(url_for("hub"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
