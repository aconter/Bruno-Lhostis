"""
Génère les pages locales « Cours de maths et physique-chimie à [commune] ».

Une page par commune desservie à domicile (hors Lannilis, traitée par l'accueil).
Le style est repris tel quel de index.html, pour que les pages suivent le site.

Chaque commune a ses propres textes (présentation, école, FAQ) dans COMMUNES :
ne pas recopier le même paragraphe d'une commune à l'autre.

Usage : python scripts/generer_pages_locales.py
Écrit les fichiers cours-maths-physique-[commune].html à la racine et met à jour sitemap.xml.
"""
import datetime as dt
import html
import json
import math
import os
import re

SITE = "https://bruno-lhostis.fr/"
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCUEIL = os.path.join(RACINE, "index.html")
ORG_ID = SITE + "#organisation"
TEL = "+33646538697"
TEL_AFF = "06 46 53 86 97"
LANNILIS = (48.5719, -4.5244)

# Coordonnées et codes postaux : repris des pages du site Antoine Conter Informatique.
# Populations : ordres de grandeur INSEE arrondis.
COMMUNES = [
    {
        "slug": "plouguerneau", "nom": "Plouguerneau", "cp": "29880",
        "geo": (48.6046, -4.5104), "wiki": "Plouguerneau",
        "lieux": ["le bourg", "Lilia", "Le Grouanec", "Koréjou", "Saint-Michel", "Saint-Cava", "les hameaux"],
        "accroche": "Juste de l'autre côté du pont de Paluden, Plouguerneau est la commune la plus proche de ma base de Lannilis.",
        "presentation": (
            "Plouguerneau compte environ 6 700 habitants, de la côte des Abers jusqu'au Grouanec. "
            "La commune est grande et très étalée : entre Lilia, Saint-Michel et les hameaux de l'intérieur, "
            "un trajet vers un cours en ville prend vite du temps. C'est justement pour ça que je viens à domicile : "
            "l'élève travaille chez lui, à sa table, avec ses cahiers sous la main."
        ),
        "ecole": (
            "Plouguerneau n'a pas de collège : les collégiens sont scolarisés à Lannilis, dans les mêmes "
            "établissements que mes élèves lannilisiens. Je connais donc le rythme des contrôles et la façon "
            "dont les cours de maths et de physique-chimie y sont menés. Au lycée, la plupart partent à Brest "
            "chaque jour : les cours ont alors lieu le soir, le mercredi ou le week-end."
        ),
        "faq": [
            ("Venez-vous jusqu'à Lilia ou au Grouanec ?",
             "Oui. Je me déplace dans toute la commune de Plouguerneau, du bourg à Lilia, au Grouanec, à Koréjou et dans les hameaux, sans supplément."),
            ("Mon enfant est au collège à Lannilis, est-ce que vous connaissez ses professeurs ?",
             "Je ne travaille pas avec le collège, mais je suis plusieurs élèves scolarisés à Lannilis. Je pars des cahiers, des devoirs et des derniers contrôles de votre enfant pour coller exactement à ce qui est fait en classe."),
        ],
    },
    {
        "slug": "landeda", "nom": "Landéda", "cp": "29870",
        "geo": (48.5944, -4.5826), "wiki": "Landéda",
        "lieux": ["le bourg", "L'Aber Wrac'h", "Sainte-Marguerite", "les hameaux"],
        "accroche": "Landéda est au bout de la presqu'île, à quelques minutes de Lannilis par la route de l'Aber Wrac'h.",
        "presentation": (
            "Landéda occupe l'extrémité de la presqu'île entre l'Aber Wrac'h et l'Aber Benoît, avec le port de "
            "l'Aber Wrac'h et les dunes de Sainte-Marguerite. Pour une famille landédaenne, Lannilis est le passage "
            "obligé vers tout le reste : je fais le trajet dans l'autre sens et je viens chez vous."
        ),
        "ecole": (
            "Les collégiens de Landéda sont rattachés au collège Pays des Abers, à Lannilis. Je suis des élèves "
            "de ce collège de la 6e à la 3e, en maths comme en physique-chimie. Pour les lycéens, qui partent "
            "en général à Brest, je propose des créneaux en fin de journée et le week-end."
        ),
        "faq": [
            ("Vous déplacez-vous jusqu'au port de l'Aber Wrac'h ?",
             "Oui, je viens dans toute la commune de Landéda : le bourg, L'Aber Wrac'h, Sainte-Marguerite et les hameaux."),
            ("Pendant l'été, faites-vous des révisions avant la rentrée ?",
             "Oui, sur demande. Quelques séances fin août permettent de reprendre les bases avant l'entrée en 6e, en 4e ou en seconde."),
        ],
    },
    {
        "slug": "treglonou", "nom": "Tréglonou", "cp": "29870",
        "geo": (48.5442, -4.5440), "wiki": "Tréglonou",
        "lieux": ["le bourg", "les bords de l'Aber Benoît", "les hameaux vers Plouguin"],
        "accroche": "Tréglonou est à 3 km de Lannilis, de l'autre côté de l'Aber Benoît.",
        "presentation": (
            "Tréglonou est une petite commune d'environ 700 habitants, au bord de l'Aber Benoît. Le bourg ancien "
            "est près de l'aber, et l'habitat s'est étendu sur le plateau, en hameaux et fermes. Pour un élève de "
            "Tréglonou, un cours particulier en ville veut souvent dire un parent qui conduit : à domicile, ce trajet disparaît."
        ),
        "ecole": (
            "Que votre enfant soit au collège à Lannilis ou ailleurs, je travaille à partir de ce qu'il fait en classe : "
            "ses cahiers, ses exercices, ses contrôles. Les lycéens de Tréglonou partent en majorité à Brest ; "
            "les séances se calent alors le soir ou le mercredi après-midi."
        ),
        "faq": [
            ("Tréglonou est petit, vous venez quand même pour une seule heure ?",
             "Oui. Tréglonou est à 3 km de Lannilis, je viens pour un cours d'une heure, au bourg comme dans les hameaux."),
            ("Pouvez-vous suivre un élève de seconde en maths et en physique-chimie ?",
             "Oui, c'est même fréquent : la seconde demande beaucoup de calcul en physique-chimie, et travailler les deux matières ensemble fait gagner du temps."),
        ],
    },
    {
        "slug": "saint-pabu", "nom": "Saint-Pabu", "cp": "29830",
        "geo": (48.5671, -4.6203), "wiki": "Saint-Pabu",
        "lieux": ["le bourg", "Corn ar Gazel", "les bords de l'Aber Benoît"],
        "accroche": "Saint-Pabu, sur la rive gauche de l'Aber Benoît, fait partie des communes où je me déplace à domicile.",
        "presentation": (
            "Saint-Pabu compte environ 2 100 habitants, à l'embouchure de l'Aber Benoît, face à Landéda. "
            "La commune regarde à la fois vers les Abers et vers Ploudalmézeau. Pour les familles, les distances "
            "vers Brest sont longues : le cours à domicile permet de garder les soirées pour les devoirs plutôt que pour la route."
        ),
        "ecole": (
            "Les élèves de Saint-Pabu ne vont pas tous au même collège ni au même lycée. Peu importe : "
            "je construis les séances à partir des documents de votre enfant, quel que soit son établissement. "
            "Pour les lycéens, les cours peuvent aussi se faire en visio entre deux séances à domicile."
        ),
        "faq": [
            ("Saint-Pabu est un peu à l'écart, vous venez quand même ?",
             "Oui, Saint-Pabu fait partie de ma zone de déplacement à domicile. Pour une révision ponctuelle, la visio est aussi possible."),
            ("Mon enfant n'est pas au collège à Lannilis, est-ce un problème ?",
             "Non. Je travaille avec les cours, les exercices et les contrôles de l'élève, quel que soit son collège ou son lycée."),
        ],
    },
    {
        "slug": "plouguin", "nom": "Plouguin", "cp": "29830",
        "geo": (48.5291, -4.5931), "wiki": "Plouguin",
        "lieux": ["le bourg", "les hameaux vers Tréglonou", "les hameaux vers Saint-Pabu", "les hameaux vers Ploudalmézeau"],
        "accroche": "Plouguin est à environ 7 km de Lannilis, en passant par Tréglonou.",
        "presentation": (
            "Plouguin compte environ 2 300 habitants sur 30 km², bordée au nord par l'Aber Benoît et traversée "
            "par le Garo. C'est une commune rurale, avec un bourg et beaucoup de hameaux. Les familles y font "
            "beaucoup de route ; un professeur qui vient à la maison, c'est un trajet de moins dans la semaine."
        ),
        "ecole": (
            "Selon les familles, les collégiens de Plouguin vont dans différents établissements du secteur. "
            "Je m'adapte au programme et au rythme de chacun en partant de ses contrôles. "
            "Au lycée, je suis les élèves en spécialité maths et physique-chimie jusqu'au bac."
        ),
        "faq": [
            ("Combien de temps faut-il pour que vous veniez à Plouguin ?",
             "Plouguin est à environ 7 km de Lannilis. Je fixe avec vous un créneau régulier, en général le même chaque semaine."),
            ("Faites-vous des cours en petit groupe à Plouguin ?",
             "Oui, pour deux ou trois élèves du même niveau, par exemple des frères et sœurs ou des amis, si leurs besoins sont proches."),
        ],
    },
    {
        "slug": "coat-meal", "nom": "Coat-Méal", "cp": "29870",
        "geo": (48.5077, -4.5431), "wiki": "Coat-Méal",
        "lieux": ["le bourg", "les hameaux"],
        "accroche": "Coat-Méal, au sud de l'Aber Benoît, est entre Lannilis et Bourg-Blanc.",
        "presentation": (
            "Coat-Méal est une commune rurale d'environ 1 100 habitants, entourée de Bourg-Blanc, Plouvien, "
            "Tréglonou, Plouguin et Milizac-Guipronvel. Autour de l'enclos paroissial du bourg, l'habitat est "
            "dispersé en hameaux. Ici, presque tout se fait en voiture : je viens à l'élève plutôt que l'inverse."
        ),
        "ecole": (
            "Les collégiens de Coat-Méal sont répartis entre plusieurs collèges du secteur. "
            "Je travaille à partir de leurs cours, quel que soit l'établissement. Pour les lycéens qui partent "
            "à Brest, les séances ont lieu en fin de journée ou le week-end."
        ),
        "faq": [
            ("Vous venez dans les hameaux de Coat-Méal ?",
             "Oui, au bourg comme dans les hameaux. Il suffit de me donner l'adresse au premier appel."),
            ("Mon enfant décroche en maths en 4e, est-il trop tard ?",
             "Non. La 4e est souvent l'année où les lacunes se voient, avec le calcul littéral. On reprend les bases qui manquent, puis on avance avec le programme."),
        ],
    },
    {
        "slug": "plouvien", "nom": "Plouvien", "cp": "29860",
        "geo": (48.5331, -4.4686), "wiki": "Plouvien",
        "lieux": ["le bourg", "Saint-Jaoua", "les hameaux"],
        "accroche": "Plouvien est sur la route entre Lannilis et Plabennec, à environ 6 km de Lannilis.",
        "presentation": (
            "Plouvien compte près de 4 000 habitants sur 34 km², avec le bourg et plusieurs villages comme "
            "Saint-Jaoua. Placée entre Lannilis et Plabennec, la commune regarde vers les deux pôles scolaires "
            "du Pays des Abers, ce qui se ressent dans les profils des élèves."
        ),
        "ecole": (
            "Les collégiens de Plouvien vont à Plabennec ou à Lannilis, selon le secteur et le choix des familles. "
            "Je suis des élèves des collèges des deux communes, ce qui me permet de m'adapter au rythme de chacun. "
            "Pour Plouvien, je propose des créneaux en fin de journée et le mercredi."
        ),
        "faq": [
            ("Vous déplacez-vous jusqu'à Saint-Jaoua ?",
             "Oui, je viens au bourg de Plouvien, à Saint-Jaoua et dans tous les hameaux de la commune."),
            ("Mon enfant est au collège à Plabennec, pouvez-vous le suivre ?",
             "Oui. Je suis des élèves des collèges Nelson Mandela et Saint-Joseph de Plabennec, comme des collèges de Lannilis."),
        ],
    },
    {
        "slug": "plabennec", "nom": "Plabennec", "cp": "29860",
        "geo": (48.5012, -4.4254), "wiki": "Plabennec",
        "lieux": ["le centre", "les quartiers résidentiels", "les hameaux"],
        "accroche": "Plabennec est la commune la plus peuplée du Pays des Abers, et le second pôle scolaire après Lannilis.",
        "presentation": (
            "Avec près de 8 700 habitants et plus de 50 km², Plabennec est la plus grande commune du Pays des Abers. "
            "Son centre concentre commerces, services et établissements scolaires, et beaucoup de familles qui "
            "travaillent à Brest. Les élèves ont des emplois du temps chargés : le cours à domicile, le soir ou le "
            "mercredi, évite un trajet supplémentaire."
        ),
        "ecole": (
            "Plabennec a deux collèges, Nelson Mandela (public) et Saint-Joseph (privé). Je suis des élèves des "
            "deux, de la 6e à la 3e, en maths et en physique-chimie, avec la préparation du brevet en fin de "
            "collège. Les lycéens plabennecois partent ensuite à Brest : je les accompagne en spécialité jusqu'au bac."
        ),
        "faq": [
            ("Vous suivez des élèves de Nelson Mandela et de Saint-Joseph ?",
             "Oui, des deux collèges. Je pars des cahiers et des contrôles de l'élève, donc je m'adapte à chaque professeur et à chaque progression."),
            ("Quels créneaux proposez-vous à Plabennec ?",
             "Surtout en fin de journée et le mercredi, ainsi que le week-end. On fixe un créneau régulier au premier appel."),
        ],
    },
    {
        "slug": "bourg-blanc", "nom": "Bourg-Blanc", "cp": "29860",
        "geo": (48.4933, -4.4968), "wiki": "Bourg-Blanc",
        "lieux": ["le bourg", "les abords du lac", "les hameaux vers Coat-Méal", "les hameaux vers Milizac"],
        "accroche": "Bourg-Blanc, entre Plabennec, Plouvien et Coat-Méal, fait partie de ma zone de déplacement.",
        "presentation": (
            "Bourg-Blanc rassemble environ 3 600 habitants sur près de 29 km², autour du bourg et du lac. "
            "La commune a accueilli ces dernières années beaucoup de jeunes familles qui travaillent à Brest. "
            "Résultat : des parents qui rentrent tard et des enfants qui ont besoin d'un appui régulier pour les devoirs de maths."
        ),
        "ecole": (
            "Les collégiens de Bourg-Blanc vont dans différents collèges du secteur, souvent vers Plabennec. "
            "Je suis des élèves des collèges de Plabennec et de Lannilis, et je m'adapte à n'importe quel établissement "
            "à partir des documents de l'élève. Pour les lycéens, je propose aussi la visio entre deux séances."
        ),
        "faq": [
            ("Pouvez-vous venir après 18 h à Bourg-Blanc ?",
             "Oui, sur rendez-vous. Les créneaux du soir sont les plus demandés : réservez tôt dans l'année."),
            ("Faites-vous de l'aide aux devoirs ?",
             "Je fais du soutien en maths et en physique-chimie, avec de la méthode et de l'organisation du travail. Je ne fais pas d'aide aux devoirs toutes matières."),
        ],
    },
    {
        "slug": "le-drennec", "nom": "Le Drennec", "cp": "29860",
        "geo": (48.5340, -4.3825), "wiki": "Le_Drennec",
        "lieux": ["le bourg", "les hameaux"],
        "accroche": "Le Drennec est entre Plabennec et Ploudaniel, à 5 km de Plabennec.",
        "presentation": (
            "Le Drennec rassemble environ 1 900 habitants sur le plateau du Léon, traversé par la RD 788. "
            "L'habitat y est dispersé entre de nombreux hameaux et fermes. La commune est à 5 km de Plabennec "
            "comme de Lesneven, ce qui fait que les élèves y suivent des parcours scolaires variés."
        ),
        "ecole": (
            "Selon les familles, les collégiens et lycéens du Drennec vont vers Plabennec, Lesneven ou Brest. "
            "Je m'adapte à l'établissement de l'élève en partant de ses cours et de ses contrôles. "
            "Pour les révisions ponctuelles, la visio permet d'ajouter une séance sans déplacement."
        ),
        "faq": [
            ("Votre enfant est au lycée à Lesneven, pouvez-vous le suivre ?",
             "Oui. Je suis des lycéens de Brest et de Lesneven, en spécialité maths et physique-chimie."),
            ("Le Drennec est à la limite de votre zone ?",
             "Le Drennec fait partie des communes où je viens à domicile. Selon les créneaux, on peut alterner domicile et visio."),
        ],
    },
    {
        "slug": "kersaint-plabennec", "nom": "Kersaint-Plabennec", "cp": "29860",
        "geo": (48.4844, -4.3639), "wiki": "Kersaint-Plabennec",
        "lieux": ["le bourg", "les hameaux"],
        "accroche": "Kersaint-Plabennec, à 5 km de Plabennec, est la commune la plus au sud de ma zone de déplacement.",
        "presentation": (
            "Kersaint-Plabennec compte environ 1 600 habitants sur le plateau du Léon, traversée par la RN 12, "
            "juste au nord-est de l'aéroport de Brest. Beaucoup de parents y travaillent à Brest ou à Landerneau. "
            "Un cours à domicile en fin de journée évite de rajouter un trajet à des journées déjà longues."
        ),
        "ecole": (
            "Les élèves de Kersaint-Plabennec sont scolarisés dans plusieurs établissements, vers Plabennec, "
            "Landerneau ou Brest. Je travaille avec les cours et les contrôles de chaque élève, "
            "quel que soit son collège ou son lycée."
        ),
        "faq": [
            ("Kersaint-Plabennec est loin de Lannilis, vous venez vraiment ?",
             "Oui, Kersaint-Plabennec fait partie de ma zone de déplacement à domicile. Les créneaux sont à fixer ensemble, et la visio reste possible en complément."),
            ("Pouvez-vous aider un adulte qui reprend des études ?",
             "Oui. J'accompagne aussi des adultes en remise à niveau en maths, pour une reprise d'études ou un concours."),
        ],
    },
]


def km(a, b):
    """Distance à vol d'oiseau en km."""
    r = 6371.0
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 2 * r * math.asin(math.sqrt(h))


def style_accueil():
    with open(ACCUEIL, encoding="utf-8") as f:
        m = re.search(r"<style>(.*?)</style>", f.read(), re.S)
    return m.group(1).rstrip()


STYLE_LOCAL = """
    /* Pages locales */
    .crumb { font-size: 14px; color: var(--ink-soft); margin: 0 0 18px; }
    .crumb a { text-decoration: none; }
    .crumb a:hover { text-decoration: underline; }
    .facts { list-style: none; padding: 0; margin: 0; }
    .facts li { padding: 12px 0; border-top: 1px solid var(--grid); display: grid; grid-template-columns: 140px 1fr; gap: 12px; font-size: 16px; }
    .facts li:first-child { border-top: 0; }
    .facts b { color: var(--ink-soft); font-weight: 600; }
    .prose p { max-width: 40em; margin: 0 0 18px; }
    .places { display: flex; flex-wrap: wrap; gap: 8px; list-style: none; padding: 0; margin: 8px 0 0; }
    .places li { border: 1px solid var(--grid-strong); border-radius: 999px; padding: 4px 12px; font-size: 15px; background: #fff; }
    .near { display: flex; flex-wrap: wrap; gap: 10px; list-style: none; padding: 0; margin: 0; }
    .near a { display: inline-block; padding: 10px 16px; border: 1.5px solid var(--ink); border-radius: 8px; text-decoration: none; font-weight: 600; }
    .near a:hover { background: #eef3f9; }
    .near small { color: var(--ink-soft); font-weight: 500; }
    @media (max-width: 720px) { .facts li { grid-template-columns: 1fr; gap: 2px; } }"""


def esc(s):
    return html.escape(s, quote=True)


def url_page(c):
    return f"{SITE}cours-maths-physique-{c['slug']}.html"


def voisines(c, n=5):
    autres = [o for o in COMMUNES if o is not c]
    autres.sort(key=lambda o: km(c["geo"], o["geo"]))
    return autres[:n]


def jsonld(c):
    url = url_page(c)
    service = {
        "@context": "https://schema.org",
        "@type": "Service",
        "@id": url + "#service",
        "name": f"Cours de maths et physique-chimie à domicile à {c['nom']}",
        "serviceType": "Cours particuliers de mathématiques et de physique-chimie",
        "url": url,
        "provider": {"@id": ORG_ID},
        "areaServed": {
            "@type": "City",
            "name": c["nom"],
            "postalCode": c["cp"],
            "sameAs": f"https://fr.wikipedia.org/wiki/{c['wiki']}",
            "geo": {"@type": "GeoCoordinates", "latitude": c["geo"][0], "longitude": c["geo"][1]},
            "containedInPlace": {"@type": "AdministrativeArea", "name": "Pays des Abers"},
        },
        "audience": {"@type": "EducationalAudience", "educationalRole": "student"},
        "offers": {"@type": "Offer", "price": "27", "priceCurrency": "EUR",
                   "description": "Tarif horaire du cours à domicile"},
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in faqs(c)],
    }
    fil = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": "Communes desservies", "item": SITE + "#communes"},
            {"@type": "ListItem", "position": 3, "name": c["nom"], "item": url},
        ],
    }
    return "\n".join(
        f'  <script type="application/ld+json">{json.dumps(d, ensure_ascii=False)}</script>'
        for d in (service, faq, fil))


def faqs(c):
    """FAQ propre à la commune, puis deux questions communes reformulées pour elle."""
    return c["faq"] + [
        (f"Combien coûte un cours de maths à domicile à {c['nom']} ?",
         f"27 € de l'heure, déplacement à {c['nom']} compris, sans frais d'inscription ni engagement. "
         "Les cours donnés à domicile ouvrent droit à un crédit d'impôt de 50 %, soit 13,50 € l'heure après crédit."),
        (f"Les cours peuvent-ils se faire en visio depuis {c['nom']} ?",
         "Oui, avec un tableau partagé à l'écran. C'est pratique pour une révision avant un contrôle, "
         "en complément des séances à domicile."),
    ]


def page(c, style):
    url = url_page(c)
    nom, cp = esc(c["nom"]), c["cp"]
    dist = round(km(LANNILIS, c["geo"]))
    titre = f"Cours de maths et physique-chimie à {c['nom']} ({cp}) | Bruno L'Hostis"
    desc = (f"Professeur particulier de maths et physique-chimie à {c['nom']} ({cp}) : collège, lycée, "
            f"brevet, bac. Cours à domicile, 27 €/h, 13,50 € après crédit d'impôt.")
    lieux = "".join(f"<li>{esc(l[0].upper() + l[1:])}</li>" for l in c["lieux"])
    proches = "".join(
        f'<li><a href="cours-maths-physique-{o["slug"]}.html">{esc(o["nom"])} <small>{o["cp"]}</small></a></li>'
        for o in voisines(c))
    faq_html = "".join(
        f"\n        <details><summary>{esc(q)}</summary><p>{esc(r)}</p></details>" for q, r in faqs(c))

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="format-detection" content="telephone=no">
  <meta name="theme-color" content="#14284b">

  <title>{esc(titre)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="{url}">
  <meta name="geo.region" content="FR-29">
  <meta name="geo.placename" content="{nom}, Finistère">
  <meta name="geo.position" content="{c['geo'][0]};{c['geo'][1]}">
  <meta name="ICBM" content="{c['geo'][0]}, {c['geo'][1]}">

  <meta property="og:locale" content="fr_FR">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{url}">
  <meta property="og:title" content="{esc(titre)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:image" content="{SITE}Bruno-LHOSTIS-logo.png">
  <meta property="og:site_name" content="Bruno L'Hostis">

  <link rel="icon" href="Bruno-LHOSTIS-logo.avif" type="image/avif">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;700&family=Schibsted+Grotesk:wght@400;500;600;700;800&display=swap" rel="stylesheet">

{jsonld(c)}

  <style>{style}
{STYLE_LOCAL}
  </style>
</head>
<body>

<header class="site-header">
  <div class="wrap">
    <a href="./" class="brand" aria-label="Bruno L'Hostis, accueil">
      <img src="Bruno-LHOSTIS-logo.avif" alt="" width="44" height="44">
      <div><strong>Bruno L'Hostis</strong><span>Maths et physique-chimie, Lannilis</span></div>
    </a>
    <nav class="nav" aria-label="Navigation principale">
      <a href="./#niveaux">Niveaux</a>
      <a href="./#tarifs">Tarifs</a>
      <a href="./#bruno">Qui suis-je</a>
      <a href="./#communes">Communes</a>
      <a href="tel:{TEL}" class="btn btn-ink">{TEL_AFF}</a>
    </nav>
  </div>
</header>

<main id="top">

  <div class="hero squared">
    <div class="wrap">
      <div>
        <nav class="crumb" aria-label="Fil d'Ariane"><a href="./">Accueil</a> › <a href="./#communes">Communes</a> › {nom}</nav>
        <h1>Cours de maths et physique-chimie à {nom}</h1>
        <p class="lead">{esc(c['accroche'])} Je viens chez vous, du collège à la terminale, et on reprend les bases là où ça coince.</p>
        <div class="hero-actions">
          <a href="tel:{TEL}" class="btn btn-pen">Appeler le {TEL_AFF}</a>
          <a href="./#contact" class="btn btn-line">Écrire un message</a>
        </div>
        <ul class="hero-facts">
          <li>27 €/h, 13,50 € après crédit d'impôt</li>
          <li>À domicile à {nom}</li>
          <li>Sans engagement</li>
        </ul>
      </div>
      <div class="calc">
        <h3>{nom} en bref</h3>
        <ul class="facts">
          <li><b>Code postal</b><span>{cp}</span></li>
          <li><b>Depuis Lannilis</b><span>environ {dist} km à vol d'oiseau</span></li>
          <li><b>Matières</b><span>Maths et physique-chimie</span></li>
          <li><b>Niveaux</b><span>6e à terminale, adultes</span></li>
          <li><b>Lieu</b><span>À domicile, ou en visio</span></li>
          <li><b>Tarif</b><span>27 €/h, déplacement compris</span></li>
        </ul>
      </div>
    </div>
  </div>

  <section>
    <div class="wrap prose">
      <h2>Le collège et le lycée, vus de {nom}</h2>
      <p>{esc(c['ecole'])}</p>
      <p>Je me déplace partout sur la commune, sans supplément :</p>
      <ul class="places">{lieux}</ul>
    </div>
  </section>

  <section class="alt">
    <div class="wrap">
      <h2>Ce que je propose aux élèves de {nom}</h2>
      <p class="intro">Des cours construits à partir des contrôles et des devoirs de l'élève, pas d'un programme tout fait.</p>
      <div class="levels">
        <div class="level">
          <span class="tag">6e à 3e</span>
          <h3>Collégiens</h3>
          <ul>
            <li>Combler les lacunes avant qu'elles s'installent</li>
            <li>Méthode et organisation du travail</li>
            <li>Préparation du brevet en maths et sciences</li>
          </ul>
        </div>
        <div class="level">
          <span class="tag">2nde à terminale</span>
          <h3>Lycéens</h3>
          <ul>
            <li>Spécialité maths et physique-chimie</li>
            <li>Maths complémentaires et expertes</li>
            <li>Préparation du bac et des épreuves écrites</li>
          </ul>
        </div>
        <div class="level">
          <span class="tag">adultes</span>
          <h3>Adultes</h3>
          <ul>
            <li>Remise à niveau en maths</li>
            <li>Reprise d'études, concours</li>
            <li>Cours à domicile ou en visio</li>
          </ul>
        </div>
      </div>
    </div>
  </section>

  <section>
    <div class="wrap prose">
      <h2>{nom}, côté commune</h2>
      <p>{esc(c['presentation'])}</p>
      <p>Je m'appelle Bruno L'Hostis. Depuis 12 ans, j'accompagne des élèves en maths et en physique-chimie, en cours individuels ou en petits groupes. <a href="./#bruno">En savoir plus sur mon parcours</a>.</p>
    </div>
  </section>

  <section id="faq" class="alt">
    <div class="wrap">
      <h2>Questions fréquentes à {nom}</h2>
      <div class="faq">{faq_html}
      </div>
    </div>
  </section>

  <section>
    <div class="wrap">
      <h2>Je me déplace aussi autour de {nom}</h2>
      <p class="intro">Même tarif, même façon de travailler. Lannilis, ma base, est sur <a href="./">la page d'accueil</a>.</p>
      <ul class="near">{proches}</ul>
    </div>
  </section>

  <div class="strip">
    <div class="wrap">
      <span>Un cours à {nom} ?</span>
      <a href="tel:{TEL}">Appeler le {TEL_AFF}</a>
      <a href="./#contact">Laisser un message</a>
    </div>
  </div>

</main>

<footer>
  <div class="wrap">
    <div>
      <strong style="color:#fff">Bruno L'Hostis</strong><br>
      Cours de maths et physique-chimie, Lannilis (29870)<br>
      <a href="tel:{TEL}">{TEL_AFF}</a>
    </div>
    <a class="credit" href="https://informatique-plouguerneau-antoine-conter.fr/" target="_blank" rel="noopener">
      <img src="Antoine-CONTER-informatique-Logo.avif" alt="" width="44" height="44" loading="lazy">
      <span>Site réalisé par Antoine Conter Informatique</span>
    </a>
  </div>
</footer>

<a href="tel:{TEL}" class="btn btn-pen call-fab">Appeler Bruno</a>

</body>
</html>
"""


def sitemap():
    jour = dt.date.today().isoformat()
    urls = [(SITE, "1.0")] + [(url_page(c), "0.8") for c in COMMUNES]
    corps = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{jour}</lastmod>\n    <priority>{p}</priority>\n  </url>\n"
        for u, p in urls)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + corps + "</urlset>\n")


def main():
    style = style_accueil()
    for c in COMMUNES:
        chemin = os.path.join(RACINE, f"cours-maths-physique-{c['slug']}.html")
        with open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(page(c, style))
        print(f"{os.path.basename(chemin)}  ({round(km(LANNILIS, c['geo']))} km de Lannilis)")
    with open(os.path.join(RACINE, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
        f.write(sitemap())
    print(f"sitemap.xml : {len(COMMUNES) + 1} URL")


if __name__ == "__main__":
    main()
