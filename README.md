# AlgoTN — Un « Thonny pour les algorithmes »

## Présentation

Bonjour ! Je m'appelle **Youssef Halim Ajmi**, je suis élève au **Lycée Pilote de Béja**, en Tunisie, et je fais partie de la **promotion du baccalauréat 2027**.

J'ai créé **AlgoTN**, un environnement permettant d'écrire et d'exécuter les algorithmes étudiés dans les lycées tunisiens. L'idée est simple : proposer **une sorte de « Thonny pour les algorithmes »**. Au lieu d'exécuter chaque instruction à la main, on peut écrire son algorithme, le lancer et observer son résultat.

AlgoTN permet également de **repérer des erreurs** (syntaxe, variables non définies, division par zéro, etc.) et, lorsque l'information est disponible, **d'indiquer la ligne concernée**. Le projet est conçu pour l'apprentissage de l'algorithmique au lycée, et non pour remplacer un langage généraliste comme Python.

## 1. Les différences avec l'écriture habituelle en classe

La syntaxe d'AlgoTN est très proche de celle utilisée dans les cours d'algorithmique en Tunisie. Quelques adaptations facilitent cependant la saisie au clavier :

| Écriture habituelle | Écriture dans AlgoTN |
| --- | --- |
| `a ≠ b` | `a != b` |
| `a ≥ b` | `a >= b` |
| `a ≤ b` | `a <= b` |
| `PAS = 2` | `PAS 2` |

Par exemple :

```text
POUR i DE 1 à 9 PAS 2 FAIRE
    ECRIRE(i)
FIN POUR
```

Ce programme affiche les nombres impairs de 1 à 9.

### Noms des fonctions sans accents

**Les noms de fonctions ne doivent pas contenir d'accents.** On écrira, par exemple :

- `RACINE_CARREE(25)` et non `RACINE_CARRÉE(25)` ;
- `ALEA(1, 10)` et non `ALÉA(1, 10)` ;
- `EFFACER(...)` et non `ÉFFACER(...)`.

Cette règle concerne les **noms de fonctions**. Elle n'interdit pas nécessairement les accents ailleurs dans le programme, notamment dans les chaînes de caractères.

## 2. Variables, affichage et lecture

### Utilisation des variables

Dans AlgoTN, on peut affecter directement une valeur à une variable :

```text
age <- 17
nom <- "Youssef"
ECRIRE(nom)
ECRIRE(age)
```

### La lecture précise le type après un trait de soulignement

Au lieu de préciser le type d'une variable dans le **tableau de déclaration des objets globaux**, on utilise la forme :

```text
LIRE_TYPE(nom_variable)
```

Dans cette notation, `TYPE` est remplacé par le type souhaité :

| Instruction | Valeur demandée |
| --- | --- |
| `LIRE_ENTIER(n)` | Un entier |
| `LIRE_REEL(x)` | Un nombre réel |
| `LIRE_CHAINE(nom)` | Une chaîne de caractères |
| `LIRE_BOOLEEN(reponse)` | Une valeur logique (`VRAI` ou `FAUX`) |

Exemple :

```text
ECRIRE("Entrez votre âge :")
LIRE_ENTIER(age)
ECRIRE("Votre âge est : ", age)
```

Il n'est donc pas nécessaire d'ajouter une déclaration de type dans un tableau des objets globaux pour cette variable lue de cette manière.

### Afficher un message et lire une valeur

**On ne peut pas placer `ECRIRE(...)` et `LIRE(...)` comme deux instructions séparées sur une même ligne de code.** Par exemple, cette écriture n'est pas acceptée :

```text
ECRIRE("Entrez votre âge :") LIRE_ENTIER(age)
```

La forme classique est :

```text
ECRIRE("Entrez votre âge :")
LIRE_ENTIER(age)
```

La forme souhaitée pour regrouper le message et la lecture dans **un seul appel** est :

```text
LIRE_ENTIER(age, "Entrez votre âge : ")
LIRE_REEL(moyenne, "Entrez votre moyenne : ")
LIRE_CHAINE(nom, "Quel est votre nom ? ")
```

**Compatibilité importante :** cette syntaxe à **deux arguments** doit être prise en charge par la version de `interpreter.py` utilisée. Dans la dernière version du code examinée pour ce README, les fonctions `LIRE_*` acceptaient encore **un seul argument**. Tant que le deuxième argument n'est pas implémenté, utilisez `ECRIRE(...)` et `LIRE_TYPE(...)` sur deux lignes distinctes.

## 3. Définir un nouveau type de tableau

AlgoTN permet de définir un type de tableau à l'aide de `NOUVEAU_TYPE` :

```text
NOUVEAU_TYPE NOM_DU_TYPE : TABLEAU DE taille TYPE
```

Exemples de définitions :

```text
NOUVEAU_TYPE TAB3 : TABLEAU DE 3 ENTIER
NOUVEAU_TYPE NOTES : TABLEAU DE 5 REEL
NOUVEAU_TYPE PRENOMS : TABLEAU DE 4 CHAINE
```

Ces instructions définissent des **types**. Pour créer un tableau contenant des valeurs, on peut écrire :

```text
NOUVEAU_TYPE TAB3 : TABLEAU DE 3 ENTIER

A <- [10, 20, 30]
ECRIRE(A[0])
A[1] <- 50
ECRIRE(A[1])
```

**Attention :** les indices des tableaux commencent à **0**. Dans cet exemple, `A[0]` est le premier élément et `A[2]` le troisième.

### Exemple avec une procédure et un paramètre par référence

```text
NOUVEAU_TYPE TAB3 : TABLEAU DE 3 ENTIER

PROCEDURE MODIFIER(@T : TAB3)
DEBUT
    T[0] <- T[0] + 5
FIN

A <- [10, 20, 30]
MODIFIER(A)
ECRIRE(A[0])
```

Le résultat attendu est `15`. Le symbole `@` indique que le tableau est passé en paramètre **par référence**, afin que les modifications soient répercutées sur le tableau d'origine.

## 4. Installer et exécuter AlgoTN

Pour utiliser AlgoTN, téléchargez ou copiez les fichiers du projet dans un même dossier :

```text
AlgoTN/
├── lexer.py
├── parser.py
├── interpreter.py
├── errors.py
├── programme.mini.txt
├── gui.py
└── index.html
```

Il existe **trois méthodes d'utilisation**. Les fichiers `gui.py` et `index.html` correspondent à deux interfaces différentes ; ils ne sont pas nécessaires pour la méthode en ligne de commande.

### Méthode 1 — Avec `interpreter.py` (terminal)

**Prérequis :** installer Python 3 sur l'ordinateur.

1. Placez `lexer.py`, `parser.py`, `interpreter.py` et `errors.py` dans le même dossier.
2. Écrivez votre algorithme dans le fichier **`programme.mini.txt`**.
3. Ouvrez un terminal dans ce dossier.
4. Exécutez :

```powershell
python interpreter.py
```

Sous Windows, vous pouvez également essayer :

```powershell
py interpreter.py
```

Le résultat (ou le message d'erreur) apparaît directement dans le terminal. **Dans l'organisation actuelle, l'interpréteur lit `programme.mini.txt` par défaut.**

### Méthode 2 — Avec `gui.py` (application de bureau)

**Prérequis :** Python 3 et Tkinter (généralement inclus avec les installations classiques de Python sur Windows).

1. Placez `gui.py` dans le même dossier que les fichiers Python de l'interpréteur.
2. Ouvrez un terminal dans ce dossier.
3. Exécutez :

```powershell
python gui.py
```

4. Dans la fenêtre AlgoTN, saisissez ou ouvrez un algorithme.
5. Cliquez sur **Exécuter** pour afficher le résultat dans la console de l'application.

Selon l'interface utilisée, vous pouvez aussi disposer d'options pour ouvrir et enregistrer vos fichiers ainsi que de raccourcis clavier.

### Méthode 3 — Avec `index.html` (navigateur web)

**Prérequis :** un navigateur moderne. L'interface web utilise **Pyodide** pour exécuter les fichiers Python directement dans le navigateur. Elle nécessite normalement une connexion Internet pour charger Pyodide depuis son CDN.

1. Conservez `index.html`, `lexer.py`, `parser.py`, `interpreter.py` et `errors.py` dans un même dossier.
2. Si Python est installé, ouvrez un terminal dans ce dossier et démarrez un serveur local :

```powershell
python -m http.server 8000
```

3. Ouvrez cette adresse dans le navigateur :

```text
http://localhost:8000
```

4. Attendez le message **« AlgoTN prêt ! »**.
5. Saisissez l'algorithme dans l'éditeur et cliquez sur **Exécuter**.

> **Important :** n'ouvrez pas simplement `index.html` avec une adresse `file://` : le chargement des fichiers Python avec `fetch()` peut être bloqué. Utilisez un serveur local ou un hébergement web statique. Une fois le site hébergé, les élèves peuvent l'utiliser dans leur navigateur, sans installer Python sur leur ordinateur.

## 5. Pourquoi utiliser AlgoTN ?

- **Détecter les erreurs :** repérer des problèmes de syntaxe et certaines erreurs d'exécution, avec des messages explicatifs en français et, lorsque possible, un numéro de ligne.
- **Exécuter les algorithmes plus facilement :** obtenir rapidement le résultat d'un algorithme sans devoir simuler chaque instruction à la main.
- **Vérifier ses raisonnements :** comparer le résultat obtenu avec celui attendu après une exécution manuelle.
- **Faciliter l'apprentissage :** disposer d'un environnement proche des notations enseignées dans les lycées tunisiens.

AlgoTN est un **outil pédagogique** : il aide à comprendre et à vérifier un algorithme, mais ne remplace pas l'apprentissage du raisonnement algorithmique.

---

**Auteur : Youssef Halim Ajmi**  
**Établissement : Lycée Pilote de Béja — Tunisie**  
**Promotion : Baccalauréat 2027**
