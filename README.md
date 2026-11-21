# AlgoTN

AlgoTN est une application de bureau pour écrire, exécuter et tester les algorithmes étudiés dans les lycées tunisiens. Les résultats et les messages d’erreur s’affichent dans une console intégrée.

## Compatibilité

Cette version couvre l’intégralité du programme d’algorithmique de **2ᵉ année de l’enseignement secondaire tunisien**. Les programmes de **3ᵉ année** et de **4ᵉ année (baccalauréat)** restent hors du périmètre de cette version.

## Pourquoi utiliser AlgoTN ?

- Exécuter un algorithme et voir son résultat sans dérouler chaque instruction à la main.
- Repérer les erreurs de syntaxe et d’exécution, comme une variable non définie ou une division par zéro. Les messages sont en français et indiquent la ligne concernée lorsqu’elle est disponible.
- Comparer les résultats avec ceux d’une exécution manuelle pour vérifier son raisonnement.
- S’entraîner avec une notation proche de celle utilisée en classe.

## Lancer AlgoTN

L’application nécessite **Python 3** et **PyQt5**. Si PyQt5 manque, installez-le depuis un terminal.

```powershell
python -m pip install PyQt5
```

Ouvrez le terminal dans le dossier qui contient les fichiers `.py` et `.ui`, puis exécutez **l’un des deux lanceurs**.

```powershell
python "inter menu.py"
```

ou

```powershell
python "inter list.py"
```

Si votre archive contient un seul lanceur nommé `inter.py`, utilisez `python inter.py`.

Dans la fenêtre de démarrage, sélectionnez **2ᵉ année**, puis cliquez sur **Continuer**. Saisissez votre algorithme dans l’éditeur et cliquez sur **Exécuter**.

## Écrire un algorithme

- **Majuscules et minuscules.** Les mots-clés et les noms de variables ou de fonctions sont insensibles à la case. Par exemple, `DEBUT`, `debut` et `Debut` sont équivalents. Le texte entre guillemets conserve sa casse.
- **Indentation.** Comme dans les algorithmes écrits en classe, les retraits sont facultatifs. Les mots-clés délimitent les blocs. Vous pouvez indenter les instructions pour rendre le code plus lisible.
- **Symboles.** Le menu **Insérer** donne accès aux symboles utilisés en classe, comme `←`, `≠`, `≥` et `≤`. Pour indiquer le pas d’une boucle `POUR`, écrivez par exemple `PAS 2`.

Cet exemple affiche `Bonjour !`, avec ou sans retrait devant `ecrire`.

```text
debut
    Si 2 < 3 Alors
        ecrire("Bonjour !")
    fin si
fin
```

## Auteurs

AlgoTN a été créé par **Youssef Halim Ajmi** et **Mouhamed Taib Kramti**, élèves de la même classe au **Lycée pilote de Béja**, promotion du **baccalauréat 2027**.

- **Youssef Halim Ajmi** s’est principalement occupé du développement du code.
- **Mouhamed Taib Kramti** s’est principalement occupé de l’interface graphique.

Tous deux ont contribué au code et à l’interface.
