#!/usr/bin/env python3
import json
import os
import re
import sys

# Paths
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "contributions.json")
DIST_DIR = os.path.join(ROOT, "dist")

def process_svg(file_path, score):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}", file=sys.stderr)
        return

    with open(file_path, "r", encoding="utf-8") as f:
        svg_text = f.read()

    # Find the animation duration in ms (usually in class definition like `.c { ... animation: ... 99300ms ... }`)
    m = re.search(r"animation\s*:\s*[^;]*?\b(\d+)ms\b", svg_text)
    if not m:
        # Fallback if pattern is slightly different
        m = re.search(r"\b(\d+)ms\b", svg_text)
    
    if m:
        duration_ms = int(m.group(1))
        print(f"Found animation duration: {duration_ms}ms in {os.path.basename(file_path)}")
    else:
        duration_ms = 90000  # Fallback 90 seconds
        print(f"Warning: could not find duration in {os.path.basename(file_path)}, using default 90000ms")

    # Define overlay display duration (e.g., 6 seconds at the end of the loop)
    show_duration_ms = 6000
    if show_duration_ms > duration_ms:
        show_duration_ms = duration_ms * 0.1

    show_percent = (show_duration_ms / duration_ms) * 100
    start_percent = 100 - show_percent
    pop_percent = start_percent + (show_percent * 0.1)
    hold_percent = start_percent + (show_percent * 0.9)

    # Style block content
    custom_style = f"""
@keyframes pop-animation {{
  0% {{ transform: scale(0); opacity: 0; }}
  {start_percent:.2f}% {{ transform: scale(0); opacity: 0; }}
  {pop_percent:.2f}% {{ transform: scale(1.1); opacity: 1; }}
  {pop_percent + 0.5:.2f}% {{ transform: scale(1); opacity: 1; }}
  {hold_percent:.2f}% {{ transform: scale(1); opacity: 1; }}
  100% {{ transform: scale(0); opacity: 0; }}
}}
@keyframes title-glow {{
  0%, 100% {{ fill: #A78BFA; }}
  50% {{ fill: #FBBF24; }}
}}
.winning-pop {{
  transform-origin: 440px 65px;
  animation: pop-animation {duration_ms}ms linear infinite;
  opacity: 0;
  pointer-events: none;
}}
.pop-title {{
  animation: title-glow 1.5s ease-in-out infinite;
}}
"""

    # Insert custom styles into the <style> block
    style_end_match = re.search(r"</style>", svg_text)
    if style_end_match:
        idx = style_end_match.start()
        svg_text = svg_text[:idx] + custom_style + svg_text[idx:]
    else:
        # Fallback if no style tag exists
        style_insert = f"<style>{custom_style}</style>"
        svg_text = svg_text.replace("<svg", f"<svg>{style_insert}", 1)

    # Generate custom SVG group for overlay
    formatted_score = f"{score:,}"
    winning_group = f"""  <g class="winning-pop">
    <!-- Semi-transparent backdrop -->
    <rect x="-16" y="-32" width="880" height="192" fill="rgba(13, 17, 23, 0.65)" rx="6"/>
    <!-- Popup window box -->
    <rect x="240" y="10" width="400" height="110" rx="8" fill="#161B22" stroke="#7C3AED" stroke-width="3"/>
    <!-- Winning title with retro glow -->
    <text x="440" y="45" font-family="'JetBrains Mono', ui-monospace, monospace" font-size="20" font-weight="bold" fill="#A78BFA" text-anchor="middle" class="pop-title">✨ YOU WON! ✨</text>
    <!-- Score info -->
    <text x="440" y="75" font-family="'JetBrains Mono', ui-monospace, monospace" font-size="14" font-weight="bold" fill="#FFFFFF" text-anchor="middle">TOTAL SCORE THIS YEAR: {formatted_score}</text>
    <text x="440" y="95" font-family="'JetBrains Mono', ui-monospace, monospace" font-size="11" fill="#8B949E" text-anchor="middle">GAMES COMPLETED: 1</text>
  </g>
"""

    # Insert group before </svg>
    svg_text = svg_text.replace("</svg>", winning_group + "</svg>")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg_text)
    print(f"Successfully added winning popup overlay to {os.path.basename(file_path)}!")

def main():
    # Load score
    score = 397
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                score = data.get("total_contributions", score)
        except Exception as e:
            print(f"Error loading contributions.json: {e}", file=sys.stderr)
    
    print(f"Using score: {score}")

    # Process files
    svg_light = os.path.join(DIST_DIR, "github-contribution-grid-snake.svg")
    svg_dark = os.path.join(DIST_DIR, "github-contribution-grid-snake-dark.svg")

    process_svg(svg_light, score)
    process_svg(svg_dark, score)

if __name__ == "__main__":
    main()
