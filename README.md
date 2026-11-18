# Visual Recommender

**Visual Recommender** est une application web de recherche d’articles vestimentaires visuellement similaires. L’utilisateur télécharge une photographie de produit, puis l’application analyse son contenu et propose les résultats les plus proches issus d’un catalogue local.

Le projet utilise **ResNet50**, pré-entraîné sur ImageNet, pour transformer chaque image en vecteur de caractéristiques. Les vecteurs sont stockés dans **ChromaDB** et recherchés grâce à la similarité cosinus. L’interface web est construite avec **FastAPI**, **Jinja2**, **HTMX** et **Tailwind CSS**.

## Fonctionnalités

- Téléversement d’une image depuis le navigateur.
- Extraction des caractéristiques visuelles avec ResNet50.
- Recherche des 5 articles les plus proches.
- Filtrage par département : Men, Women, Boys, Girls ou Unisex.
- Affichage de l’image référence, des recommandations et de leur distance.
- Recherche locale sans service externe après l’installation.
- Base vectorielle persistante avec ChromaDB.

## Aperçu du fonctionnement

1. Les métadonnées du catalogue sont lues depuis `dataset/styles.csv`.
2. Chaque image disponible est transformée en vecteur de 2048 nombres.
3. Les vecteurs et métadonnées sont enregistrés dans ChromaDB.
4. L’image téléversée est transformée dans le même espace vectoriel.
5. ChromaDB retourne les articles ayant la plus petite distance cosinus.

## Structure du projet

```text
visual-recommender/
├── api/
│   ├── main.py                 # Application FastAPI
│   ├── static/                 # Ressources statiques
│   └── templates/
│       ├── index.html          # Page d’envoi de l’image
│       └── results.html        # Affichage des recommandations
├── core/
│   ├── feature_extractor.py    # Extraction ResNet50
│   └── chroma_manager.py       # Construction de la base ChromaDB
├── dataset/
│   ├── styles.csv              # Métadonnées du catalogue
│   └── images/                 # Images du catalogue
├── temp_uploads/               # Images téléversées temporairement
├── vector_db/                  # Base ChromaDB générée automatiquement
├── requirements.txt
└── README.md
```

## Prérequis

- Windows 10 ou Windows 11.
- Python 3.10, 3.11 ou 3.12 recommandé.
- `pip` et `venv`.
- Au minimum 8 Go de RAM recommandés.
- Une connexion Internet lors de la première utilisation afin que TensorFlow puisse télécharger les poids ResNet50.

> **Remarque :** TensorFlow 2.15 n’est pas compatible avec les dernières versions de Python. Python 3.11 est conseillé.

## Installation étape par étape

### 1. Télécharger le projet

```powershell
git clone https://github.com/<UTILISATEUR>/<DEPOT>.git
cd <DEPOT>
```

Le dépôt peut aussi être ouvert directement dans VS Code avec le dossier du projet.

### 2. Créer l’environnement virtuel

Depuis PowerShell, à la racine du projet :

```powershell
py -3.11 -m venv venv
```

Si cette commande échoue, vérifiez que Python 3.11 est installé :

```powershell
py -0p
```

### 3. Activer l’environnement virtuel

```powershell
.\venv\Scripts\Activate.ps1
```

Si PowerShell bloque les scripts, autorisez temporairement l’exécution :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Une fois activé, le terminal affiche normalement `(venv)` au début de la ligne.

### 4. Mettre à niveau pip

```powershell
python -m pip install --upgrade pip
```

### 5. Installer les dépendances

```powershell
python -m pip install -r requirements.txt
```

L’installation peut prendre plusieurs minutes selon la vitesse de téléchargement.

## Construire la base vectorielle

Avant la première recherche, la base ChromaDB doit être créée.

À la racine du projet, avec l’environnement virtuel activé :

```powershell
python -m core.chroma_manager
```

Cette commande :

- charge jusqu’aux 2 000 premières lignes du catalogue ;
- ignore les articles dont l’image manque ;
- extrait les caractéristiques avec ResNet50 sur le processeur ;
- crée les fichiers dans `vector_db/`.

Le traitement peut prendre une durée significative. À la fin, le message suivant doit apparaître :

```text
Vector database population complete! You can now query similar items.
```

Pour reconstruire complètement la base après une modification du catalogue, supprimez le dossier `vector_db/` puis relancez la commande précédente.

## Lancer l’application

Depuis la racine du projet :

```powershell
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Puis ouvrez cette adresse dans un navigateur :

```text
http://127.0.0.1:8000
```

L’arrêt du serveur s’effectue avec `Ctrl+C` dans le terminal.

## Utiliser l’application

1. Ouvrez `http://127.0.0.1:8000`.
2. Cliquez sur **Choose File** ou sur le sélecteur du formulaire.
3. Sélectionnez une image au format JPG, PNG ou autre format lisible.
4. Facultatif : choisissez un département afin de limiter les résultats.
5. Cliquez sur **Search**.
6. Consultez l’image téléversée et les cinq articles similaires.

La distance affichée mesure l’écart avec l’image recherchée. Une valeur plus faible indique généralement une meilleure proximité visuelle.

## Commandes utiles

### Activer l’environnement

```powershell
.\venv\Scripts\Activate.ps1
```

### Désactiver l’environnement

```powershell
deactivate
```

### Reconstruire les caractéristiques

```powershell
python -m core.chroma_manager
```

### Vérifier les dépendances installées

```powershell
python -m pip freeze
```

## Dépendances principales

| Dépendance | Rôle |
|---|---|
| TensorFlow | Chargement du modèle ResNet50 |
| ChromaDB | Stockage et recherche vectorielle |
| FastAPI | API web et routes HTTP |
| Uvicorn | Serveur ASGI |
| Jinja2 | Rendu des pages HTML |
| Pandas | Lecture du catalogue CSV |
| Pillow | Chargement et préparation des images |

## Dépannage

### Le serveur indique que la collection `fashion_products` n’existe pas

Arrêtez le serveur, construisez la base puis relancez l’application :

```powershell
python -m core.chroma_manager
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

### Une image ne produit aucun résultat

- Vérifiez que l’image n’est pas corrompue.
- Essayez avec une autre photographie au format JPG ou PNG.
- Vérifiez que `vector_db/` contient une base construite.
- Essayez avec le filtre département réglé sur **All Departments**.

### `No module named tensorflow`

L’environnement virtuel n’est probablement pas activé ou les dépendances n’ont pas été installées :

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Téléchargement ou chargement de ResNet50 échoue

- Vérifiez la connexion Internet.
- Réessayez après quelques instants.
- Assurez-vous d’utiliser une version Python compatible recommandée ci-dessus.

### Erreur lors de l’exécution sous PowerShell

Autorisez les scripts uniquement pour le processus courant :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## Jeu de données

Le jeu de données est composé de métadonnées produits dans `dataset/styles.csv` et d’images dans `dataset/images/`. Le champ `id` du fichier CSV correspond au nom de l’image, par exemple :

```text
15970 -> dataset/images/15970.jpg
```

Le gestionnaire vectoriel indexe les premiers articles disponibles, mais les utilisateurs peuvent adapter ce comportement dans `core/chroma_manager.py`.

## Conception technique

- Le modèle `ResNet50(weights="imagenet", include_top=False, pooling="avg")` génère un vecteur.
- Les images sont redimensionnées en 224 × 224 pixels avant l’extraction.
- ChromaDB utilise la distance cosinus.
- Les filtres sont appliqués avec le champ `gender` des métadonnées.
- La génération TensorFlow est limitée au CPU afin d’éviter les problèmes liés aux pilotes CUDA sur Windows.

## Licence

Ajoutez ici la licence choisie pour le projet avant une diffusion publique. Les images et données du catalogue peuvent être soumises à leurs propres licences ou conditions d’utilisation.
