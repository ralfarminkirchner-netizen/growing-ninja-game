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

# ====================== VISUALS FÜR BESSERE GRAFIK ======================
STAGE_VISUALS = {
    "Genin": {"emoji": "🥷", "color": "#4ade80", "aura": "emerald", "title": "Genin", "desc": "Der Weg beginnt"},
    "Chunin": {"emoji": "🥷", "color": "#22c55e", "aura": "emerald", "title": "Chunin", "desc": "Erste echte Kraft"},
    "Jonin": {"emoji": "🗡️", "color": "#16a34a", "aura": "green", "title": "Jonin", "desc": "Meister der Technik"},
    "Elite Super Ninja": {"emoji": "🔥🥷", "color": "#eab308", "aura": "yellow", "title": "Elite Super Ninja", "desc": "Übermenschlich"},
    "Kage (Legendär)": {"emoji": "👑🥷", "color": "#f59e0b", "aura": "amber", "title": "KAGE", "desc": "Legende der Ninja"},
}

def get_stage_visual(stage):
    return STAGE_VISUALS.get(stage, STAGE_VISUALS["Genin"])

# ====================== HTML TEMPLATE (verbesserte Grafik & Spielgefühl) ======================
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
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&amp;family=Inter:wght@400;600&amp;display=swap');
    
    :root {
      --ninja-green: #22c55e;
    }
    
    .ninja-font { font-family: "Press Start 2P", system-ui; }
    
    body {
      background: #0a0a0a;
      background-image: 
        linear-gradient(rgba(16, 185, 129, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(16, 185, 129, 0.03) 1px, transparent 1px);
      background-size: 32px 32px;
    }
    
    .game-card {
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: hidden;
    }
    .game-card::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 40%;
      height: 300%;
      background: linear-gradient(
        120deg,
        transparent,
        rgba(255,255,255,0.08),
        transparent
      );
      transform: skewX(-25deg);
      transition: left 0.7s;
    }
    .game-card:hover::before {
      left: 150%;
    }
    .game-card:hover {
      transform: translateY(-6px) scale(1.01);
      box-shadow: 0 25px 50px -12px rgb(0 0 0 / 0.4);
    }
    
    .ninja-shadow {
      filter: drop-shadow(0 10px 15px rgb(16 185 129 / 0.2));
    }
    
    .stage-badge {
      font-weight: 700;
      letter-spacing: 0.5px;
      background: linear-gradient(90deg, #166534, #4ade80, #86efac);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    
    .stat-bar {
      transition: width 600ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    .ninja-portrait {
      transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
      filter: drop-shadow(0 15px 25px rgb(0 0 0 / 0.5));
    }
    
    .feedback {
      animation: popIn 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    
    @keyframes popIn {
      0% { transform: scale(0.6) translateY(20px); opacity: 0; }
      60% { transform: scale(1.05) translateY(-4px); }
      100% { transform: scale(1) translateY(0); opacity: 1; }
    }
    
    .answer-btn {
      transition: all 0.15s ease;
      border: 2px solid #3f3f46;
    }
    .answer-btn:hover {
      border-color: #22c55e;
      background-color: #052e16;
      transform: translateX(4px);
    }
    
    .ninja-glow {
      box-shadow: 0 0 20px rgb(16 185 129 / 0.3),
                  0 0 40px rgb(16 185 129 / 0.15);
    }
    
    .section-title {
      font-size: 0.75rem;
      letter-spacing: 1.5px;
      font-weight: 600;
      text-transform: uppercase;
    }
    
    .growth-bar {
      height: 14px;
      background: #18181b;
      border-radius: 9999px;
      overflow: hidden;
      border: 1px solid #27272a;
    }
    
    .xp-text {
      font-family: ui-monospace, monospace;
    }
  </style>
</head>
<body class="bg-[#0a0a0a] text-zinc-200">
  <div class="max-w-6xl mx-auto p-4 md:p-8">
    <!-- HEADER -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-x-4">
        <div class="flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-900/30 border border-emerald-800 text-4xl ninja-shadow">🥷</div>
        <div>
          <h1 class="text-4xl md:text-5xl font-black tracking-[-2.5px] ninja-font text-white">GROWING NINJA</h1>
          <p class="text-emerald-400/90 text-sm md:text-base -mt-1 tracking-[1px]">LERNEN • WACHSEN • KÄMPFEN</p>
        </div>
      </div>
      
      <div class="flex items-center gap-x-3">
        <a href="https://github.com/ralfarminkirchner-netizen/growing-ninja-game" target="_blank"
           class="hidden sm:flex items-center gap-x-2 px-4 py-2 rounded-2xl bg-zinc-900 hover:bg-zinc-800 border border-zinc-800 text-sm font-medium transition">
          <i class="fa-brands fa-github text-lg"></i>
          <span class="hidden md:inline">GitHub</span>
        </a>
        
        <a href="/" 
           class="flex items-center gap-x-2 px-5 py-2.5 rounded-3xl bg-emerald-600 hover:bg-emerald-500 active:scale-[0.985] font-semibold text-sm transition shadow-inner">
          <i class="fa-solid fa-home"></i>
          <span class="hidden sm:inline">Zum Hub</span>
        </a>
      </div>
    </div>

    <!-- STATUS + NINJA VISUAL (stark verbesserte Grafik) -->
    {% set p = player %}
    {% set stage = p.get('stage', 'Genin') %}
    {% set visual = get_stage_visual(stage) %}
    <div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-2 md:p-3 mb-6 shadow-2xl">
      <div class="grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-3 items-stretch">
        
        <!-- NINJA PORTRAIT -->
        <div class="md:col-span-4 bg-zinc-950 border border-zinc-800 rounded-3xl p-5 flex flex-col items-center justify-center text-center">
          <div class="relative">
            <div class="text-[82px] md:text-[96px] leading-none ninja-portrait ninja-shadow select-none" 
                 style="color: {{ visual.color }}">
              {{ visual.emoji }}
            </div>
            {% if 'Kage' in stage or 'Elite' in stage %}
            <div class="absolute -top-1 -right-1 text-3xl animate-pulse">✨</div>
            {% endif %}
          </div>
          
          <div class="mt-1">
            <div class="stage-badge text-2xl tracking-[1.5px]">{{ visual.title }}</div>
            <div class="text-emerald-300/70 text-xs font-medium">{{ visual.desc }}</div>
          </div>
        </div>

        <!-- STATS + GROWTH -->
        <div class="md:col-span-8 bg-zinc-950 border border-zinc-800 rounded-3xl p-5 flex flex-col">
          <div class="flex items-start justify-between">
            <div>
              <div class="font-black text-3xl tracking-tighter">{{ p.name }}</div>
              <div class="flex items-center gap-x-2 text-sm">
                <span class="px-3 py-px rounded-full text-xs font-bold bg-emerald-900/70 text-emerald-300 border border-emerald-800">{{ stage }}</span>
                <span class="text-xs text-zinc-500">Level {{ (p.total_levels_played // 3) + 1 }}</span>
              </div>
            </div>
            
            <div class="text-right">
              <div class="flex items-center justify-end gap-x-1 text-xl font-bold">
                <span class="text-yellow-400"><i class="fa-solid fa-coins"></i></span>
                <span class="xp-text">{{ p.gold }}</span>
              </div>
              <div class="text-[10px] text-zinc-500 -mt-0.5">GOLD</div>
            </div>
          </div>

          <!-- XP + Growth Bar -->
          <div class="mt-4">
            <div class="flex justify-between items-baseline text-xs mb-1.5">
              <div class="flex items-center gap-x-1.5">
                <span class="font-semibold text-emerald-400">XP</span>
                <span class="font-mono text-lg font-bold text-white xp-text">{{ p.xp }}</span>
              </div>
              <div class="text-zinc-400 text-[11px]">
                Nächste Stufe bei {{ 180 if p.xp < 180 else (350 if p.xp < 350 else (600 if p.xp < 600 else 900)) }}
              </div>
            </div>
            
            <div class="growth-bar">
              {% set next_threshold = 180 if p.xp < 180 else (350 if p.xp < 350 else (600 if p.xp < 600 else 900)) %}
              {% set prev_threshold = 0 if p.xp < 180 else (180 if p.xp < 350 else (350 if p.xp < 600 else 600)) %}
              {% set segment = next_threshold - prev_threshold %}
              {% set progress = ((p.xp - prev_threshold) / segment * 100) if segment > 0 else 100 %}
              <div class="h-[14px] bg-gradient-to-r from-emerald-400 via-lime-400 to-emerald-300 rounded-full stat-bar"
                   style="width: {{ [progress, 100]|min }}%"></div>
            </div>
          </div>

          <!-- Upgrades as nice badges -->
          <div class="mt-auto pt-4 flex flex-wrap gap-2">
            <div class="flex-1 min-w-[92px] bg-zinc-900 border border-zinc-800 rounded-2xl px-3 py-1.5 text-xs flex items-center gap-x-2">
              <span class="text-lg">🦘</span>
              <div class="flex-1">
                <div class="text-emerald-300 font-semibold">Sprung</div>
                <div class="font-mono text-base leading-none font-bold">{{ p.upgrades.jump }}</div>
              </div>
            </div>
            <div class="flex-1 min-w-[92px] bg-zinc-900 border border-zinc-800 rounded-2xl px-3 py-1.5 text-xs flex items-center gap-x-2">
              <span class="text-lg">⭐</span>
              <div class="flex-1">
                <div class="text-emerald-300 font-semibold">Sterne</div>
                <div class="font-mono text-base leading-none font-bold">{{ p.upgrades.star }}</div>
              </div>
            </div>
            <div class="flex-1 min-w-[92px] bg-zinc-900 border border-zinc-800 rounded-2xl px-3 py-1.5 text-xs flex items-center gap-x-2">
              <span class="text-lg">💪</span>
              <div class="flex-1">
                <div class="text-emerald-300 font-semibold">Kraft</div>
                <div class="font-mono text-base leading-none font-bold">{{ p.upgrades.strength }}</div>
              </div>
            </div>
            
            <form method="post" action="{{ url_for('reset') }}" class="ml-auto">
              <button type="submit" 
                      class="h-full px-3.5 text-xs rounded-2xl border border-zinc-800 hover:bg-red-950/40 text-zinc-400 hover:text-red-400 transition flex items-center gap-x-1.5">
                <i class="fa-solid fa-undo text-[11px]"></i>
                <span class="hidden md:inline text-xs">Reset</span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- FLASH MESSAGES (besser sichtbar) -->
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <div class="mb-5 space-y-2">
        {% for category, message in messages %}
          <div class="px-5 py-3.5 rounded-3xl text-sm font-medium feedback flex items-center gap-x-3
            {% if category == 'success' %} bg-emerald-900/80 border border-emerald-700 text-emerald-200
            {% elif category == 'warning' %} bg-amber-900/80 border border-amber-700 text-amber-200
            {% else %} bg-zinc-800 border border-zinc-700 {% endif %}">
            <span class="text-lg">
              {% if category == 'success' %}✅{% elif category == 'warning' %}⚡{% else %}ℹ️{% endif %}
            </span>
            <span class="flex-1">{{ message }}</span>
          </div>
        {% endfor %}
        </div>
      {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}

    <div class="mt-8 text-center">
      <div class="inline-flex items-center gap-x-2 text-xs text-zinc-500 px-4 py-1.5 rounded-3xl bg-zinc-900 border border-zinc-800">
        <span>Terminal-Version auch verfügbar</span>
        <a href="https://github.com/ralfarminkirchner-netizen/growing-ninja-game" target="_blank" class="font-medium text-emerald-400 hover:text-emerald-300">GitHub →</a>
      </div>
    </div>
  </div>

  <script>
    // Simple but satisfying confetti for kids
    function launchConfetti(count = 42) {
      const colors = ['#22c55e', '#eab308', '#f59e0b', '#a3e635'];
      for (let i = 0; i < count; i++) {
        const particle = document.createElement('div');
        particle.textContent = ['🥷','⭐','🍃','✨','🪙'][Math.floor(Math.random()*5)];
        particle.style.position = 'fixed';
        particle.style.left = Math.random() * 100 + 'vw';
        particle.style.top = '-20px';
        particle.style.fontSize = (12 + Math.random() * 18) + 'px';
        particle.style.zIndex = '9999';
        particle.style.pointerEvents = 'none';
        particle.style.transition = `transform ${1.8 + Math.random()}s linear, opacity 1.8s linear`;
        document.body.appendChild(particle);

        const angle = Math.random() * 80 + 60;
        const distance = 300 + Math.random() * 420;

        requestAnimationFrame(() => {
          particle.style.transform = `translateY(${distance}px) rotate(${angle * 4}deg)`;
          particle.style.opacity = '0';
        });

        setTimeout(() => particle.remove(), 2800);
      }
    }

    // Auto-launch confetti on transformation or big success
    document.addEventListener('DOMContentLoaded', () => {
      const flashes = document.querySelectorAll('.feedback');
      flashes.forEach(el => {
        if (el.textContent.includes('VERWANDLUNG') || el.textContent.includes('BESIEGT') || el.textContent.includes('Richtig')) {
          setTimeout(() => launchConfetti(38), 180);
        }
      });

      // Subtle pulse on the ninja portrait when page loads
      const portrait = document.querySelector('.ninja-portrait');
      if (portrait) {
        setTimeout(() => {
          portrait.style.transform = 'scale(1.08)';
          setTimeout(() => { if (portrait) portrait.style.transform = 'scale(1)'; }, 420);
        }, 650);
      }
    });

    // Bonus: keyboard hint (kids love shortcuts)
    document.addEventListener('keydown', function(e) {
      if (e.key === "?" && document.activeElement.tagName === "BODY") {
        const challenge = document.querySelector('a[href*="challenge"]');
        if (challenge) challenge.click();
      }
    });
  </script>
</body>
</html>
"""

HUB_TEMPLATE = """
<!-- ACTION HUB - deutlich grafischer und ansprechender -->
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4 mb-4">

  <!-- Haupt-Action: Challenge -->
  <a href="{{ url_for('challenge') }}" 
     class="game-card group col-span-1 sm:col-span-2 lg:col-span-2 block bg-gradient-to-br from-emerald-900/40 to-zinc-900 border border-emerald-700 hover:border-emerald-400 rounded-3xl p-6 md:p-7 relative overflow-hidden">
    <div class="absolute top-4 right-4 text-6xl opacity-10 group-hover:opacity-20 transition">🎯</div>
    
    <div class="flex items-center gap-x-5">
      <div class="text-[52px] md:text-[60px] leading-none group-hover:scale-110 transition-transform">🎯</div>
      <div class="flex-1">
        <div class="uppercase tracking-[2px] text-xs font-bold text-emerald-400/90">TRAINING</div>
        <div class="font-black text-3xl md:text-4xl tracking-tighter mt-0.5">Nächste Challenge</div>
        <div class="mt-2 text-emerald-300/80 text-sm max-w-[260px]">
          Spring, schneide, rechne oder beantworte. Jede richtige Antwort macht deinen Ninja stärker!
        </div>
        
        <div class="mt-5 inline-flex items-center justify-center gap-x-2 px-5 h-11 rounded-2xl bg-emerald-600 group-hover:bg-emerald-500 font-bold text-sm shadow-inner active:scale-[0.985] transition">
          <i class="fa-solid fa-play"></i>
          <span>JETZT STARTEN</span>
        </div>
      </div>
    </div>
  </a>

  <!-- Mystery Barrel -->
  <form method="post" action="{{ url_for('barrel') }}" class="game-card block">
    <button type="submit" class="w-full h-full text-left bg-zinc-900 border border-yellow-700 hover:border-yellow-400 rounded-3xl p-6 flex flex-col">
      <div class="text-[46px] mb-2">🛢️</div>
      <div class="font-black text-2xl tracking-[-1px]">Mystery Fass</div>
      <div class="text-sm text-yellow-400/90 flex-1 mt-1">Tritt es auf! Entweder Gold oder eine schnelle Überraschungs-Challenge.</div>
      
      <div class="mt-4 text-xs bg-yellow-900/40 border border-yellow-800 rounded-2xl px-3 py-1 self-start font-medium">
        62% Chance auf 18–55 Gold
      </div>
    </button>
  </form>

  <!-- Shop -->
  <a href="{{ url_for('shop') }}" 
     class="game-card block bg-zinc-900 border border-sky-700 hover:border-sky-400 rounded-3xl p-6">
    <div class="text-[46px] mb-2">🛍️</div>
    <div class="font-black text-2xl tracking-[-1px]">Ninja Shop</div>
    <div class="text-sky-400/90 text-sm mt-1">Tausche dein Gold in dauerhafte Upgrades ein.</div>
    
    <div class="mt-4 flex gap-x-1.5 text-xs">
      <div class="bg-sky-900/40 text-sky-300 px-2.5 py-px rounded-lg">🦘 Sprung</div>
      <div class="bg-sky-900/40 text-sky-300 px-2.5 py-px rounded-lg">⭐ Sterne</div>
      <div class="bg-sky-900/40 text-sky-300 px-2.5 py-px rounded-lg">💪 Kraft</div>
    </div>
  </a>

  <!-- Boss Fight -->
  <form method="post" action="{{ url_for('boss') }}" class="game-card block">
    <button type="submit" class="w-full h-full text-left bg-zinc-900 border border-red-700 hover:border-red-400 rounded-3xl p-6 flex flex-col">
      <div class="text-[46px] mb-2">👹</div>
      <div class="font-black text-2xl tracking-[-1px]">Boss-Kampf</div>
      <div class="text-sm text-red-400/90 flex-1 mt-1 leading-snug">4 Runden. Zeige alles, was du gelernt hast und gewinne große Belohnungen!</div>
      
      <div class="mt-3 text-xs font-bold text-red-300">Nur die Besten gewinnen</div>
    </button>
  </form>
</div>

<!-- Info Footer -->
<div class="bg-zinc-900 border border-zinc-800 rounded-3xl p-4 md:p-5 text-sm">
  <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-400">
    <div class="font-semibold text-emerald-400/90">So wirst du stärker:</div>
    <div class="flex items-center gap-x-1"><span class="text-emerald-400">→</span> Challenges lösen = XP</div>
    <div class="flex items-center gap-x-1"><span class="text-emerald-400">→</span> Fässer öffnen = Gold</div>
    <div class="flex items-center gap-x-1"><span class="text-emerald-400">→</span> Shop = dauerhafte Power</div>
    <div class="flex items-center gap-x-1"><span class="text-emerald-400">→</span> Genug XP = Verwandlung!</div>
  </div>
</div>
"""

CHALLENGE_TEMPLATE = """
<div class="max-w-3xl mx-auto">
  <!-- Back + Type -->
  <div class="mb-3 flex items-center justify-between px-1">
    <a href="{{ url_for('hub') }}" class="flex items-center gap-x-2 text-emerald-400 hover:text-emerald-300 text-sm font-medium">
      <i class="fa-solid fa-chevron-left"></i> 
      <span>Zurück zum Hub</span>
    </a>
    <div class="px-4 py-1 text-xs font-bold tracking-widest rounded-full bg-zinc-900 border border-zinc-700">
      {{ challenge_type.upper() }}
    </div>
  </div>

  <div class="bg-zinc-900 border border-emerald-800 rounded-3xl p-7 md:p-8 shadow-xl">
    <!-- Question -->
    <div class="mb-6">
      <div class="uppercase text-xs tracking-[2px] text-emerald-400/80 mb-1">Deine Aufgabe</div>
      <div class="text-2xl md:text-3xl font-bold leading-tight">
        {{ challenge.q if challenge.q else challenge.word }}
      </div>
    </div>

    <form method="post" action="{{ url_for('submit') }}">
      <input type="hidden" name="type" value="{{ challenge_type }}">

      {% if challenge_type in ['wortarten', 'sachkunde'] %}
        <!-- Große, grafische Antwort-Buttons -->
        <div class="grid grid-cols-1 gap-3">
          {% for i, opt in enumerate(challenge.options) %}
          <button type="submit" name="choice" value="{{ i }}"
                  class="answer-btn group w-full text-left px-6 py-4 md:py-5 rounded-2xl bg-zinc-950 hover:bg-emerald-950/60 flex items-center gap-x-4 text-lg font-medium">
            <div class="w-9 h-9 flex-none rounded-2xl bg-emerald-900/50 text-emerald-400 flex items-center justify-center font-black group-hover:bg-emerald-500 group-hover:text-black transition">
              {{ i+1 }}
            </div>
            <span class="flex-1">{{ opt }}</span>
            <i class="fa-solid fa-arrow-right text-emerald-600 group-hover:text-emerald-400 transition"></i>
          </button>
          {% endfor %}
        </div>

      {% elif challenge_type == 'komposita' %}
        <div>
          <div class="text-sm text-zinc-400 mb-2 pl-1">Trenne das Wort mit einem Leerzeichen oder |</div>
          <div class="flex gap-x-3">
            <input type="text" name="answer" placeholder="Apfel Baum" required
                   class="flex-1 bg-black border-2 border-zinc-700 focus:border-emerald-500 rounded-3xl px-6 py-4 text-2xl font-medium placeholder:text-zinc-600">
            <button type="submit" 
                    class="px-8 py-4 rounded-3xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 font-bold text-sm tracking-wider flex items-center gap-x-2">
              <span class="hidden sm:inline">SCHNEIDEN</span>
              <span class="text-xl">⚔️</span>
            </button>
          </div>
        </div>

      {% elif challenge_type == 'mathe' %}
        <div>
          <div class="text-sm text-zinc-400 mb-2 pl-1">Gib die Antwort ein</div>
          <div class="flex gap-x-3">
            <input type="number" name="answer" placeholder="?" required
                   class="flex-1 bg-black border-2 border-zinc-700 focus:border-emerald-500 rounded-3xl px-6 py-4 text-4xl font-mono text-center placeholder:text-zinc-700">
            <button type="submit" 
                    class="px-10 py-4 rounded-3xl bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 font-bold text-base flex items-center gap-x-2">
              OK
            </button>
          </div>
        </div>
      {% endif %}
    </form>
  </div>

  <div class="text-center mt-4 text-xs text-zinc-500 px-2">
    Keine Sorge — auch bei Fehlern bekommst du etwas XP und wirst stärker.
  </div>
</div>
"""

SHOP_TEMPLATE = """
<div class="max-w-2xl mx-auto">
  <div class="mb-4 px-1 flex items-center gap-x-3">
    <span class="text-3xl">🛍️</span>
    <div>
      <div class="font-black text-3xl tracking-tighter">Ninja-Shop</div>
      <div class="text-xs text-sky-400/80">Dauerhafte Verbesserungen für deinen Ninja</div>
    </div>
  </div>

  <div class="grid grid-cols-1 gap-3">
    {% for key, label, cost, desc, icon in [
      ('jump', 'Bessere Sprungkraft', 45, 'Deutlich höhere Sprünge bei Wortarten-Plattformen', '🦘'),
      ('star', 'Stärkere Ninja-Sterne', 40, 'Mehr Treffer und XP im Shooter', '⭐'),
      ('strength', 'Mehr Kraft & Ausdauer', 50, 'Bessere Ergebnisse bei Katana + Mathe', '💪')
    ] %}
    <form method="post" action="{{ url_for('buy') }}" class="game-card bg-zinc-900 border border-sky-800 hover:border-sky-400 rounded-3xl p-4 md:p-5 flex items-center gap-x-4">
      <input type="hidden" name="item" value="{{ key }}">
      
      <div class="text-4xl w-12 text-center">{{ icon }}</div>
      
      <div class="flex-1 min-w-0">
        <div class="font-bold text-xl">{{ label }}</div>
        <div class="text-sm text-zinc-400">{{ desc }}</div>
      </div>
      
      <div class="text-right">
        <button type="submit" 
                class="px-6 py-2.5 text-sm rounded-2xl font-bold bg-sky-600 hover:bg-sky-500 disabled:bg-zinc-800 disabled:text-zinc-500 transition"
                {% if player.gold < cost %}disabled{% endif %}>
          {{ cost }} <span class="opacity-75">Gold</span>
        </button>
        <div class="text-[10px] text-sky-400/60 mt-0.5">Level {{ player.upgrades[key] }}</div>
      </div>
    </form>
    {% endfor %}
  </div>

  <div class="mt-5 text-center">
    <a href="{{ url_for('hub') }}" class="inline-block text-sm px-4 py-2 rounded-2xl bg-zinc-900 border border-zinc-700 hover:bg-zinc-800 text-emerald-400">← Zurück zum Hub</a>
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
