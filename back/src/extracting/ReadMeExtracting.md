# 📖 Pipeline d'extraction — Documentation complète

---

## 🗺️ Vue d'ensemble

```
Excel (.xlsx)  +  PDF (.pdf)
       ↓               ↓
  extract_traits   extract_pdf_to_dict
       ↓               ↓
    [traits]        {page: content}
            ↘       ↙
          run_pipeline
               ↓
        Pour chaque page :
          build_prompt
               ↓
       query_lm_studio_with_text
               ↓
           parse_json
               ↓
             merge
               ↓
          result.json
```

---

## 📂 Fichiers impliqués

```
back/
├── src/extracting/
│   ├── __init__.py           # Expose les fonctions publiques
│   ├── Extraction_excel.py   # Étape 1 : lire l'Excel
│   ├── pdf_to_text.py        # Étape 2 : lire le PDF (CLI standalone)
│   ├── lm_studio_client.py   # Étape 3 : appeler le LLM
│   └── main.py               # Étape 4 : orchestrer tout
├── prompts/v2/
│   └── prompt_targeted_extraction.txt  # Template du prompt
├── scripts/
│   └── run_extraction.sh     # Point d'entrée CLI
└── outputs/
    └── result.json           # Résultat final
```

---

## 🔢 Étape 1 — `Extraction_excel.py` : Lire les traits

### Rôle
Lire le fichier Excel fourni par l'utilisateur et extraire la liste des traits agronomiques à rechercher dans le PDF.

### Input
```
SI25BT006IGS_Olive_Nursery-20260224111539.xlsx
```

### Ce que fait le code
```python
traits = extract_traits(excel_source)
```

1. Ouvre le fichier `.xlsx` avec `openpyxl` ou `pandas`
2. Lit chaque ligne du tableau
3. Extrait pour chaque ligne :
   - `trait_id` : identifiant technique (ex: `Shoot_Lenght`)
   - `description` : libellé humain (ex: `Shoot Length`)

### Output
```python
[
  {"trait_id": "Shoot_Lenght",        "description": "Shoot Lenght"},
  {"trait_id": "VIGOUR",              "description": "VIGOUR"},
  {"trait_id": "Leaf_Area",           "description": "Leaf Area"},
  {"trait_id": "Fresh_Aerial_Weight", "description": "Fresh Aerial Weight"},
  {"trait_id": "Fresh_Root_Weight",   "description": "Fresh Root Weight"}
]
```

### Pourquoi c'est important
Cette liste est **la référence** de tout ce qu'on cherche dans le PDF. Le LLM ne cherchera **que** ces traits, rien d'autre.

---

## 🔢 Étape 2 — `extract_pdf_to_dict` dans `main.py` : Lire le PDF

### Rôle
Convertir chaque page du PDF en texte Markdown structuré.

### Input
```
FINAL_REPORT_SI25BT006IGS.pdf  (ex: 72 pages)
```

### Ce que fait le code
```python
pages = extract_pdf_to_dict(pdf_source)
```

1. Ouvre le PDF avec `pymupdf`
   - Si c'est un chemin → `pymupdf.open(str(pdf_source))`
   - Si c'est des bytes (API) → `pymupdf.open(stream=pdf_source, filetype="pdf")`
2. Pour **chaque page** (0 à N-1) :
   - Appelle `pymupdf4llm.to_markdown(doc, pages=[page_num])`
   - `pymupdf4llm` extrait :
     - Le texte brut
     - Les tableaux (détectés automatiquement → convertis en Markdown)
     - La structure (titres, paragraphes)
3. Stocke le résultat dans un dict avec la page comme clé

### Output
```python
{
  1:  "# FINAL REPORT\n\nClient: GAIA...",
  2:  "## Table of Contents\n- Introduction\n...",
  15: "## ARM Ratings\n| Variable | Method | Unit |\n|----------|--------|------|\n| HEIGHT | ruler | cm |",
  72: "## Accreditation\n..."
}
```

### Pourquoi `pymupdf4llm` ?
Contrairement à un simple `page.get_text()`, `pymupdf4llm` :
- ✅ Détecte et formate les **tableaux** en Markdown
- ✅ Préserve la **hiérarchie** (titres H1, H2...)
- ✅ Produit un texte plus facile à lire pour le LLM

---

## 🔢 Étape 3 — `build_prompt` : Construire le prompt dynamiquement

### Rôle
Assembler le prompt envoyé au LLM pour **chaque page**.

### Input
```python
traits       = [{"trait_id": "VIGOUR", "description": "VIGOUR"}, ...]
page_content = "## ARM Ratings\n| Variable | Method |..."
template     = contenu de prompt_targeted_extraction.txt
```

### Ce que fait le code
```python
prompt = build_prompt(traits, content, template)
```

1. Construit la liste des traits :
```
- Shoot_Lenght: Shoot Lenght
- VIGOUR: VIGOUR
- Leaf_Area: Leaf Area
- Fresh_Aerial_Weight: Fresh Aerial Weight
- Fresh_Root_Weight: Fresh Root Weight
```
2. Remplace `{trait_list}` dans le template par cette liste
3. Remplace `{page_content}` par le texte Markdown de la page courante

### Output (exemple pour la page 15)
```
You are an expert agronomist...

TRAITS TO FIND:
- Shoot_Lenght: Shoot Lenght
- VIGOUR: VIGOUR
...

PAGE CONTENT:
## ARM Ratings
| Variable | Method | Unit |
|----------|--------|------|
| HEIGHT   | ruler  | cm   |
...
```

### Pourquoi c'est dynamique ?
- Le prompt est **reconstruit à chaque page** avec le contenu exact de cette page
- Les traits viennent de l'Excel → **aucun hardcoding**
- Fonctionne pour **n'importe quel PDF ou Excel**

---

## 🔢 Étape 4 — `query_lm_studio_with_text` : Appeler le LLM

### Rôle
Envoyer le prompt à LM Studio (serveur local) et récupérer la réponse.

### Input
```python
response = query_lm_studio_with_text(prompt)
```

### Ce que fait le code
1. Envoie une requête HTTP POST à `http://localhost:1234/v1/chat/completions`
2. Payload :
```json
{
  "model": "...",
  "messages": [{"role": "user", "content": "<prompt>"}],
  "temperature": 0.1,
  "max_tokens": 2000
}
```
3. Récupère la réponse texte du LLM

### Output (exemple)
```
[
  {
    "trait_id": "Shoot_Lenght",
    "description": "Shoot length measurement",
    "trait": "Length of the main shoot from base to apex",
    "method": "Manual measurement with ruler",
    "unit": "cm"
  }
]
```

### Pourquoi `temperature: 0.1` ?
Valeur basse = réponses **déterministes et précises**, pas créatives. Idéal pour extraction de données structurées.

---

## 🔢 Étape 5 — `parse_json` : Parser la réponse

### Rôle
Nettoyer et parser la réponse brute du LLM en liste Python.

### Problème à résoudre
Le LLM retourne parfois :
```
```json          ← markdown parasite
[{"trait_id":... ← JSON valide
```              ← markdown parasite
```

Ou pire, un JSON tronqué :
```
[{"trait_id": "VIGOUR", "trait": "Plant vig   ← coupé !
```

### Ce que fait le code
```python
parsed = parse_json(response)
```

1. **Supprime le Markdown** : retire les ` ```json ` et ` ``` `
2. **Répare le JSON tronqué** : si le JSON commence par `[` mais ne finit pas par `]`, cherche le dernier `}` valide et ferme le tableau
3. **Parse** avec `json.loads()`
4. **Normalise** : si le LLM retourne un dict au lieu d'une liste, l'encapsule dans une liste

### Exemples de cas gérés
```python
# Cas 1 : réponse propre
"[{...}]"  →  [{...}]

# Cas 2 : markdown
"```json\n[{...}]\n```"  →  [{...}]

# Cas 3 : JSON tronqué
"[{...}, {\"trait_id\": \"VIGOUR\", \"trait\": \"Plan"  →  [{...}]

# Cas 4 : dict seul
"{...}"  →  [{...}]

# Cas 5 : erreur totale
"Sorry I cannot..."  →  []
```

---

## 🔢 Étape 6 — `merge` : Fusionner les résultats

### Rôle
Intégrer les résultats d'une page dans le dictionnaire consolidé **sans écraser ce qui a déjà été trouvé**.

### Input
```python
# Ce qu'on a déjà (consolidated)
results = {
  "VIGOUR": {"trait_id": "VIGOUR", "trait": "Plant vigor", "method": None, "unit": None},
  "Shoot_Lenght": {"trait_id": "Shoot_Lenght", "trait": None, "method": None, "unit": None}
}

# Ce qu'on vient de trouver sur cette page
new_items = [
  {"trait_id": "VIGOUR", "trait": None, "method": "NDVI sensor", "unit": "%"},
  {"trait_id": "Shoot_Lenght", "trait": "Main shoot length", "method": "ruler", "unit": "cm"}
]
```

### Ce que fait le code
```python
merge(results, parsed)
```

Pour chaque trait trouvé :
- Compare les champs `trait`, `method`, `unit`
- **Règle** : ne remplace que si l'ancien est vide (`None`, `""`, `"null"`) ET le nouveau ne l'est pas

### Output après merge
```python
{
  "VIGOUR": {
    "trait_id": "VIGOUR",
    "trait": "Plant vigor",     # ← conservé (déjà rempli)
    "method": "NDVI sensor",    # ← ajouté (était None)
    "unit": "%"                 # ← ajouté (était None)
  },
  "Shoot_Lenght": {
    "trait_id": "Shoot_Lenght",
    "trait": "Main shoot length", # ← ajouté
    "method": "ruler",            # ← ajouté
    "unit": "cm"                  # ← ajouté
  }
}
```

### Pourquoi cette logique ?
Un trait peut être mentionné **sur plusieurs pages** :
- Page 5 → définition du trait
- Page 15 → méthode de mesure
- Page 32 → unité

Le merge accumule les infos **au fil des pages** sans perdre ce qui a été trouvé.

---

## 🔢 Étape 7 — Sauvegarde : `result.json`

### Ce que fait le code
```python
final = list(results.values())
with open(output_path, "w") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)
```

Convertit le dictionnaire en liste et sauvegarde en JSON formaté.

### Output final
```json
[
  {
    "trait_id": "Shoot_Lenght",
    "description": "Shoot Lenght",
    "trait": "Length of the main shoot from the base to the apex",
    "method": "Manual measurement with a graduated ruler",
    "unit": "cm"
  },
  {
    "trait_id": "VIGOUR",
    "description": "VIGOUR",
    "trait": "Overall plant vigor assessed by NDVI imaging",
    "method": "NDVI drone sensor",
    "unit": "%"
  },
  {
    "trait_id": "Leaf_Area",
    "description": "Leaf Area",
    "trait": null,
    "method": null,
    "unit": "cm2"
  }
]
```

---

## 🔄 Boucle complète — Récapitulatif page par page

```
PDF (72 pages)
    │
    ├── Page 1  → prompt → LLM → [] (rien trouvé)
    ├── Page 2  → prompt → LLM → [] (rien trouvé)
    ├── ...
    ├── Page 15 → prompt → LLM → [VIGOUR, Shoot_Lenght] → merge
    ├── Page 16 → prompt → LLM → [Leaf_Area] → merge
    ├── ...
    ├── Page 32 → prompt → LLM → [VIGOUR (method)] → merge
    ├── ...
    └── Page 72 → prompt → LLM → [] (rien trouvé)
                                        │
                                   result.json
```

---

## 🚀 Point d'entrée CLI

```bash
./scripts/run_extraction.sh \
  data/raw/excel/traits.xlsx \
  data/raw/pdf/report.pdf
```

### Ce que fait le script shell
1. `cd "$(dirname Hackathon_GAIA"` → se place dans `back/`
2. Vérifie que les 2 arguments sont fournis
3. Lance `uv run python -m src.extracting.main excel pdf output`

### Pourquoi `-m src.extracting.main` ?
Exécuter en tant que **module** (`-m`) plutôt que script (`python src/extracting/main.py`) permet :
- Les imports relatifs (`from src.extracting.X import Y`) de fonctionner
- Python ajoute `back/` au `sys.path` automatiquement

---

## 📊 Statistiques de sortie

```
Traits: 5
Extracting PDF...
Pages: 72

Page 1... nothing
Page 2... nothing
Page 15... ['VIGOUR', 'Shoot_Lenght']
Page 16... ['Leaf_Area']
Page 32... ['VIGOUR']
...
Page 72... nothing

Done: 4/5 traits found
Saved: outputs/result.json
``````