"""
Rapport des positions Google par commune et par thème, depuis Search Console (28 derniers jours).

Pour chaque commune et chaque thème (maths, physique-chimie, brevet, bac...) :
impressions, clics, position moyenne, meilleure requête et page du site qui ressort.
Les tableaux s'affichent dans le résumé du workflow GitHub.

Usage : python scripts/rapport_positions.py [nb_jours]
Nécessite la clé du compte de service dans GSC_SERVICE_ACCOUNT_JSON.
Propriété Search Console : variable GSC_SITE (par défaut le préfixe d'URL du site).
"""
import datetime as dt
import json
import os
import sys
import unicodedata
import urllib.parse

PREFIXE = "https://bruno-lhostis.fr/"
SITE = os.environ.get("GSC_SITE", "").strip() or PREFIXE
COMMUNES = [
    # Base et communes desservies à domicile
    "Lannilis", "Plouguerneau", "Landéda", "Tréglonou", "Saint-Pabu", "Plouguin",
    "Coat-Méal", "Plouvien", "Plabennec", "Bourg-Blanc", "Le Drennec", "Kersaint-Plabennec",
    # Secteur, et villes des lycées (cours en visio)
    "Abers", "Lesneven", "Brest",
]
# Mots cherchés dans la requête, sans accents et en minuscules.
THEMES = {
    "Maths": ["math"],
    "Physique-chimie": ["physique", "chimie"],
    "Brevet": ["brevet"],
    "Bac": ["bac "],
    "Collège": ["college", "6e", "5e", "4e", "3e"],
    "Lycée": ["lycee", "seconde", "premiere", "terminale", "specialite"],
    "Adultes": ["adulte", "remise a niveau", "concours"],
    "Soutien, cours particuliers": ["soutien", "cours particulier", "prof"],
}


def norm(s):
    s = unicodedata.normalize("NFKD", s.lower()).encode("ascii", "ignore").decode()
    return s.replace("-", " ").replace("'", " ") + " "


def bilan(nom, sel):
    imp = sum(x["impressions"] for x in sel)
    clics = sum(x["clicks"] for x in sel)
    pos = (sum(x["position"] * x["impressions"] for x in sel) / imp) if imp else None
    best = max(sel, key=lambda x: x["impressions"]) if sel else None
    return (nom, imp, clics, pos,
            best["keys"][0] if best else "",
            best["keys"][1].replace(PREFIXE, "/") if best else "")


def tableau(titre_col, lignes):
    md = [f"| {titre_col} | Impressions | Clics | Position moyenne | Requête principale | Page |",
          "|---|---:|---:|---:|---|---|"]
    for c, imp, clics, pos, q, p in lignes:
        md.append(f"| {c} | {imp} | {clics} | {pos:.1f} | {q} | {p} |" if imp
                  else f"| {c} | 0 | 0 | non classé | | |")
    return md


def main():
    jours = int(sys.argv[1]) if len(sys.argv) > 1 else 28
    from google.oauth2 import service_account
    from google.auth.transport.requests import AuthorizedSession

    creds = service_account.Credentials.from_service_account_info(
        json.loads(os.environ["GSC_SERVICE_ACCOUNT_JSON"]),
        scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    s = AuthorizedSession(creds)
    fin = dt.date.today() - dt.timedelta(days=2)  # Search Console a ~2 jours de retard
    debut = fin - dt.timedelta(days=jours)
    url = ("https://www.googleapis.com/webmasters/v3/sites/"
           f"{urllib.parse.quote(SITE, safe='')}/searchAnalytics/query")
    r = s.post(url, json={"startDate": str(debut), "endDate": str(fin),
                          "dimensions": ["query", "page"], "rowLimit": 25000})
    r.raise_for_status()
    rows = r.json().get("rows", [])

    par_commune = [bilan(c, [x for x in rows if norm(c) in norm(x["keys"][0])]) for c in COMMUNES]
    par_theme = [bilan(t, [x for x in rows if any(m in norm(x["keys"][0]) for m in mots)])
                 for t, mots in THEMES.items()]
    imp_tot = sum(x["impressions"] for x in rows)
    clics_tot = sum(x["clicks"] for x in rows)

    md = [f"## Positions Google du {debut:%d/%m/%Y} au {fin:%d/%m/%Y}", "",
          f"Total : {imp_tot} impressions, {clics_tot} clics"
          + (f", CTR {100 * clics_tot / imp_tot:.1f} %" if imp_tot else ""), "",
          "### Par commune", ""] + tableau("Commune", par_commune)
    md += ["", "### Par thème", ""] + tableau("Thème", par_theme)
    md += ["", "Position moyenne : 1 à 10 = première page Google, 11 à 20 = deuxième page.",
           "« non classé » : aucune recherche contenant ce mot n'a encore affiché le site."]
    texte = "\n".join(md)
    print(texte)
    resume = os.environ.get("GITHUB_STEP_SUMMARY")
    if resume:
        with open(resume, "a", encoding="utf-8") as f:
            f.write(texte + "\n")


if __name__ == "__main__":
    main()
