from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


# =========================
# Config
# =========================

OUTPUT_HTML = Path("web/rapport.html")

TITLE = "📸 Rapport TP2 - <votre nom>"
COURSE_FOOTER = "Photographie algorithmique — TP2 | Domaine fréquentiel"

# Ton layout a toi (comme tu l'as demandé)
IMG_IRIS = Path("web/images/data/Iris.png")
IMG_OPTIMUS = Path("web/images/data/Optimus.png")

IMG_IRIS_SHARP = Path("web/images/accentuation/Iris_sigma_2.5.png")  # extension potentiellement manquante
IMG_OPTIMUS_SHARP = Path("web/images/accentuation/Optimus_sigma_2.5.png")

IMG_IRIS_MONTAGE = Path("web/images/accentuation/montage_Iris.png")
IMG_OPTIMUS_MONTAGE = Path("web/images/accentuation/montage_Optimus.png")

# Partie 1 — T1 (Einstein/Marilyn)
IMG_EINSTEIN = Path("web/images/data/Albert_Einstein.png")
IMG_MARILYN = Path("web/images/data/Marilyn_Monroe.png")
IMG_HYBRID_T1 = Path("web/images/hybrid/T1/hybrid_cutoff5.0_5.0.png")

# Partie 1 — T2 (Cap/Thor)
IMG_CAP = Path("web/images/data/Capitaine.png")
IMG_THOR = Path("web/images/data/Thor.png")
IMG_HYBRID_T2 = Path("web/images/hybrid/T2/hybrid_cutoff3.0_3.5.png")

IMG_AMP_HIGH = Path("web/images/hybrid/T2/amplitude/amp_high_cutoff3.0_3.5.png")
IMG_AMP_LOW = Path("web/images/hybrid/T2/amplitude/amp_low_cutoff3.0_3.5.png")

# Partie 1 Bonus — couleur (tes photos)
IMG_TONY = Path("web/images/data/Tony.png")
IMG_PAT = Path("web/images/data/Pat.png")
IMG_HYBRID_T3 = Path("web/images/hybrid/T3/hybrid_cutoff10.0_10.0.png")  # extension potentiellement manquante

# Partie 2
IMG_PILE_MONTAGE = Path("web/images/pile/montage_gauss_lap.png")


# =========================
# Helpers HTML
# =========================

def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
    )

def pick_existing(p: Path) -> Path:
    """
    Si le path n'existe pas, et qu'il n'a pas d'extension, on essaie .png/.jpg/.jpeg.
    Sinon on retourne tel quel (même si manquant) -> ça évite de crasher ton script.
    """
    if p.exists():
        return p
    if p.suffix:
        return p
    for ext in [".png", ".jpg", ".jpeg"]:
        candidate = p.with_suffix(ext)
        if candidate.exists():
            return candidate
    return p

def rel_to_output(img_path: Path, output_html: Path) -> str:
    """
    Convertit un path en chemin relatif depuis le dossier du HTML.
    Ex: web/images/x.png vu depuis web/rapport.html => images/x.png
    """
    out_dir = output_html.parent
    try:
        return img_path.relative_to(out_dir).as_posix()
    except Exception:
        # fallback: relativize by commonpath if weird paths
        return img_path.as_posix()

def figure(img_path: Path, caption: str, output_html: Path, max_width: str = "70%") -> str:
    p = pick_existing(img_path)
    src = rel_to_output(p, output_html)
    cap = _escape(caption)
    return f"""
    <div class="figure-container">
        <img src="{src}" alt="{cap}" data-fullsize="{src}" onclick="openLightbox(this)" style="max-width:{max_width};" />
        <p class="figure-caption">{cap}</p>
    </div>
    """

def pair_two(img_a: Path, cap_a: str, img_b: Path, cap_b: str, output_html: Path) -> str:
    a = pick_existing(img_a)
    b = pick_existing(img_b)
    sa = rel_to_output(a, output_html)
    sb = rel_to_output(b, output_html)
    ca = _escape(cap_a)
    cb = _escape(cap_b)
    return f"""
    <div class="comparison-images">
        <div class="comparison-image-item" onclick="openLightbox(this.querySelector('img'))">
            <img src="{sa}" alt="{ca}" data-fullsize="{sa}">
            <div class="comparison-image-label">{ca}</div>
        </div>
        <div class="comparison-image-item" onclick="openLightbox(this.querySelector('img'))">
            <img src="{sb}" alt="{cb}" data-fullsize="{sb}">
            <div class="comparison-image-label">{cb}</div>
        </div>
    </div>
    """

def textarea_block(title: str, placeholder: str = "Écris ta réponse ici…") -> str:
    t = _escape(title)
    ph = _escape(placeholder)
    return f"""
    <div class="text-block">
        <div class="text-block-title">📝 {t}</div>
        <textarea class="text-area" placeholder="{ph}"></textarea>
    </div>
    """

def url_inputs_block(title: str, labels: Iterable[str]) -> str:
    t = _escape(title)
    inputs = []
    for lab in labels:
        l = _escape(lab)
        inputs.append(f"""
        <div class="url-row">
            <label>{l}</label>
            <input type="url" placeholder="https://..." />
        </div>
        """)
    return f"""
    <div class="text-block">
        <div class="text-block-title">🔗 {t}</div>
        {''.join(inputs)}
    </div>
    """

def section(title: str, inner: str) -> str:
    return f"""
    <section class="image-section">
        <h2>{_escape(title)}</h2>
        {inner}
    </section>
    """


# =========================
# HTML Template
# =========================

def build_html(output_html: Path) -> str:
    now = datetime.now().strftime("%d %B %Y à %H:%M")

    # ---- Partie 0
    p0 = ""
    p0 += "<h3>Images originales</h3>"
    p0 += f"""
    <div class="comparison-pair">
        <div class="comparison-pair-title">Iris vs Optimus</div>
        {pair_two(IMG_IRIS, "Iris (original)", IMG_OPTIMUS, "Optimus (original)", output_html)}
    </div>
    """

    p0 += "<h3>Sharpening (σ = 2.5)</h3>"
    p0 += f"""
    <div class="comparison-pair">
        <div class="comparison-pair-title">Sharpening σ=2.5</div>
        {pair_two(IMG_IRIS_SHARP, "Iris sharpened (σ=2.5)", IMG_OPTIMUS_SHARP, "Optimus sharpened (σ=2.5)", output_html)}
    </div>
    """

    p0 += "<h3>Montages des variations</h3>"
    p0 += f"""
    <div class="comparison-pair">
        <div class="comparison-pair-title">Montages</div>
        {pair_two(IMG_IRIS_MONTAGE, "Montage Iris", IMG_OPTIMUS_MONTAGE, "Montage Optimus", output_html)}
    </div>
    """
    p0 += textarea_block("Observations / réponses (Partie 0)")

    # ---- Partie 1
    p1 = ""
    p1 += "<h3>Hybride — Einstein / Marilyn</h3>"
    p1 += f"""
    <div class="comparison-pair">
        <div class="comparison-pair-title">Entrées</div>
        {pair_two(IMG_EINSTEIN, "Albert Einstein (input)", IMG_MARILYN, "Marilyn Monroe (input)", output_html)}
    </div>
    """
    p1 += "<h4>Résultat</h4>"
    p1 += figure(IMG_HYBRID_T1, "Image hybride (cutoff 5.0 / 5.0)", output_html, max_width="75%")

    p1 += "<hr class='soft-hr' />"

    p1 += "<h3>Hybride — Capitaine / Thor</h3>"
    p1 += f"""
    <div class="comparison-pair">
        <div class="comparison-pair-title">Entrées</div>
        {pair_two(IMG_CAP, "Capitaine (input)", IMG_THOR, "Thor (input)", output_html)}
    </div>
    """
    p1 += "<h4>Résultat</h4>"
    p1 += figure(IMG_HYBRID_T2, "Image hybride (cutoff 3.0 / 3.5)", output_html, max_width="75%")

    p1 += url_inputs_block(
        "Sources (si images prises sur Internet)",
        ["Lien source image 1", "Lien source image 2"],
    )
    p1 += textarea_block("Décrivez et commentez vos résultats (Partie 1)")

    p1 += "<hr class='soft-hr' />"
    p1 += "<h3>Analyse fréquentielle (résultat préféré)</h3>"
    p1 += f"""
    <div class="comparison-pair">
        <div class="comparison-pair-title">Amplitude (log) — composantes</div>
        {pair_two(IMG_AMP_HIGH, "Amplitude passe-haut", IMG_AMP_LOW, "Amplitude passe-bas", output_html)}
    </div>
    """
    p1 += textarea_block("Réponse: Illustration détaillée de l'analyse fréquentielle")

    # ---- Partie 1 Bonus
    p1b = ""
    p1b += "<h3>Hybride en couleur (mes propres photos)</h3>"
    p1b += f"""
    <div class="comparison-pair">
        <div class="comparison-pair-title">Entrées (mes photos)</div>
        {pair_two(IMG_TONY, "Tony (input) — MES PHOTOS", IMG_PAT, "Pat (input) — MES PHOTOS", output_html)}
    </div>
    """
    p1b += "<h4>Résultat</h4>"
    p1b += figure(IMG_HYBRID_T3, "Image hybride couleur (cutoff 10.0 / 10.0) — MES PHOTOS", output_html, max_width="75%")

    p1b += textarea_block(
        "Pour quelle(s) composantes la couleur améliore l'effet ? (passe-haut, passe-bas, les deux)",
        "Ex: La couleur aide surtout pour ____ parce que ____."
    )

    # ---- Partie 2
    p2 = ""
    p2 += "<h3>Piles gaussienne et laplacienne — « Lincoln et Gala » (Dali)</h3>"
    p2 += figure(IMG_PILE_MONTAGE, "Montage piles gaussienne + laplacienne", output_html, max_width="85%")
    p2 += textarea_block("Commentaires / observations (Partie 2)")

    # ---- Partie 3 (placeholder)
    p3 = ""
    p3 += "<h3>À compléter</h3>"
    p3 += textarea_block("Décrivez votre mélange multirésolution + résultats", "Ajoute tes images + ton texte quand tu les as.")

    # ---- Partie 4 (placeholder)
    p4 = ""
    p4 += "<h3>À compléter</h3>"
    p4 += textarea_block("Bonus / crédits supplémentaires / conclusion", "Checklist: ce que t'as fait + ce que ça change + mini bilan.")

    # Build full page
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{_escape(TITLE)}</title>

  <style>
    @import url('https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600;700&family=Fira+Code:wght@400;500&display=swap');
    * {{ box-sizing: border-box; }}

    body {{
      font-family: 'Source Sans Pro', -apple-system, BlinkMacSystemFont, sans-serif;
      margin: 0;
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
      color: #e8e8e8;
      min-height: 100vh;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 30px 20px;
    }}

    header {{
      text-align: center;
      padding: 40px 0;
      border-bottom: 2px solid rgba(255,255,255,0.1);
      margin-bottom: 40px;
    }}

    h1 {{
      font-size: 2.5em;
      font-weight: 700;
      margin: 0 0 10px 0;
      text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }}

    .date-badge {{
      display: inline-block;
      background: rgba(255,255,255,0.1);
      padding: 8px 20px;
      border-radius: 20px;
      margin-top: 12px;
      font-size: 0.9em;
      color: #b0b0b0;
    }}

    .image-section {{
      background: rgba(255,255,255,0.05);
      backdrop-filter: blur(10px);
      border-radius: 16px;
      padding: 30px;
      margin-bottom: 40px;
      border: 1px solid rgba(255,255,255,0.1);
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }}

    .image-section h2 {{
      color: #778da9;
      font-size: 1.6em;
      margin: 0 0 25px 0;
      padding-bottom: 15px;
      border-bottom: 2px solid rgba(119, 141, 169, 0.25);
    }}

    h3 {{
      color: #e0e1dd;
      font-size: 1.3em;
      margin: 26px 0 14px 0;
    }}

    h4 {{
      margin: 18px 0 10px 0;
      color: #dbe2ef;
    }}

    .figure-container {{
      text-align: center;
      margin: 15px 0;
      padding: 15px;
      background: rgba(0,0,0,0.2);
      border-radius: 12px;
    }}

    .figure-container img {{
      max-width: 100%;
      max-height: 520px;
      border-radius: 8px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.3);
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
    }}

    .figure-container img:hover {{
      transform: scale(1.015);
      box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    }}

    .figure-caption {{
      margin-top: 10px;
      font-style: italic;
      color: #a0a0a0;
      font-size: 0.9em;
    }}

    .comparison-pair {{
      background: rgba(0,0,0,0.25);
      border-radius: 12px;
      padding: 18px;
      border: 1px solid rgba(255,255,255,0.08);
      margin: 16px 0;
    }}

    .comparison-pair-title {{
      text-align: center;
      color: #fff;
      font-size: 1.05em;
      font-weight: 600;
      margin-bottom: 12px;
      padding-bottom: 10px;
      border-bottom: 2px solid rgba(255,255,255,0.15);
    }}

    .comparison-images {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
    }}

    .comparison-image-item {{
      position: relative;
      border-radius: 10px;
      overflow: hidden;
      background: rgba(0,0,0,0.2);
      cursor: pointer;
      transition: transform 0.15s, box-shadow 0.15s;
    }}

    .comparison-image-item:hover {{
      transform: translateY(-3px);
      box-shadow: 0 6px 20px rgba(0,0,0,0.5);
    }}

    .comparison-image-item img {{
      width: 100%;
      height: auto;
      display: block;
    }}

    .comparison-image-label {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);
      color: #fff;
      padding: 12px 8px 8px;
      font-size: 0.85em;
      text-align: center;
      font-weight: 500;
    }}

    .text-block {{
      background: rgba(0,0,0,0.25);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 12px;
      padding: 18px;
      margin: 18px 0 0 0;
    }}

    .text-block-title {{
      font-weight: 700;
      color: #cbd5e1;
      margin-bottom: 10px;
    }}

    .text-area {{
      width: 100%;
      min-height: 140px;
      resize: vertical;
      padding: 12px 14px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.15);
      background: rgba(0,0,0,0.35);
      color: #fff;
      font-family: 'Source Sans Pro', sans-serif;
      font-size: 1em;
      outline: none;
    }}

    .text-area:focus {{
      border-color: rgba(119,141,169,0.9);
      box-shadow: 0 0 0 2px rgba(119,141,169,0.25);
    }}

    .url-row {{
      display: grid;
      grid-template-columns: 180px 1fr;
      gap: 12px;
      align-items: center;
      margin: 10px 0;
    }}

    .url-row label {{
      color: #a0a0a0;
      font-size: 0.95em;
    }}

    .url-row input {{
      width: 100%;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.15);
      background: rgba(0,0,0,0.35);
      color: #fff;
      outline: none;
      font-family: 'Fira Code', monospace;
      font-size: 0.95em;
    }}

    .url-row input:focus {{
      border-color: rgba(119,141,169,0.9);
      box-shadow: 0 0 0 2px rgba(119,141,169,0.25);
    }}

    .soft-hr {{
      border: none;
      height: 1px;
      background: rgba(255,255,255,0.12);
      margin: 22px 0;
    }}

    footer {{
      text-align: center;
      padding: 30px;
      color: #777;
      font-size: 0.95em;
    }}

    /* Lightbox */
    .lightbox {{
      display: none;
      position: fixed;
      z-index: 9999;
      left: 0; top: 0;
      width: 100%; height: 100%;
      background-color: rgba(0,0,0,0.92);
      animation: fadeIn 0.2s;
    }}

    .lightbox.active {{
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .lightbox-content {{
      max-width: 95vw;
      max-height: 95vh;
      padding: 18px;
    }}

    .lightbox-content img {{
      max-width: 100%;
      max-height: 95vh;
      object-fit: contain;
      border-radius: 10px;
      box-shadow: 0 8px 40px rgba(0,0,0,0.8);
    }}

    .lightbox-close {{
      position: absolute;
      top: 16px;
      right: 30px;
      color: #fff;
      font-size: 44px;
      font-weight: bold;
      cursor: pointer;
      transition: color 0.2s;
      user-select: none;
    }}

    .lightbox-close:hover {{
      color: #ffc107;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; }}
      to {{ opacity: 1; }}
    }}

    @media (max-width: 900px) {{
      .comparison-images {{ grid-template-columns: 1fr; }}
      .url-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>

<body>
  <div id="lightbox" class="lightbox" onclick="closeLightbox(event)">
    <span class="lightbox-close">&times;</span>
    <div class="lightbox-content">
      <img id="lightbox-img" src="" alt="">
    </div>
  </div>

  <div class="container">
    <header>
      <h1>{_escape(TITLE)}</h1>
      <div class="date-badge">Généré le {now}</div>
    </header>

    {section("Partie 0 — Réchauffement (accentuation / sharpening)", p0)}
    {section("Partie 1 — Images hybrides", p1)}
    {section("Partie 1 Bonus — Hybride en couleur", p1b)}
    {section("Partie 2 — Piles gaussienne et laplacienne", p2)}
    {section("Partie 3 — Mélange multirésolution", p3)}
    {section("Partie 4 — Bonus / Conclusion", p4)}

    <footer>
      <p>{_escape(COURSE_FOOTER)}</p>
    </footer>
  </div>

  <script>
    function openLightbox(img) {{
      const lightbox = document.getElementById('lightbox');
      const lightboxImg = document.getElementById('lightbox-img');
      const fullSizeSrc = img.getAttribute('data-fullsize') || img.src;
      lightboxImg.src = fullSizeSrc;
      lightbox.classList.add('active');
      document.body.style.overflow = 'hidden';
    }}

    function closeLightbox(event) {{
      const lightbox = document.getElementById('lightbox');
      if (event.target === lightbox || event.target.classList.contains('lightbox-close')) {{
        lightbox.classList.remove('active');
        document.body.style.overflow = 'auto';
      }}
    }}

    document.addEventListener('keydown', function(event) {{
      if (event.key === 'Escape') {{
        const lightbox = document.getElementById('lightbox');
        lightbox.classList.remove('active');
        document.body.style.overflow = 'auto';
      }}
    }});
  </script>
</body>
</html>
"""
    return html


def main() -> None:
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(OUTPUT_HTML)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"[OK] Rapport généré: {OUTPUT_HTML.resolve()}")


if __name__ == "__main__":
    main()
