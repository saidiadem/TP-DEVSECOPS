# TP 2 — Intégration de la sécurité dans un pipeline CI/CD

Application Flask et pipeline GitHub Actions pour le dépôt
https://github.com/saidiadem/TP-DEVSECOPS.
Le dépôt distant était vide au démarrage. Cette application sert de support au TP 2.
Le TP 1 n'est pas réalisé ici ; Bandit et Snyk sont les outils choisis parmi ceux proposés.

## Pipeline

| Job | Travail réalisé | Condition d'échec |
| --- | --- | --- |
| `build-test` | Compilation Python, tests unitaires, construction Docker | Compilation, test ou build en erreur |
| `sast` | Bandit sur le code applicatif | Sévérité High, ou erreur du scanner |
| `sca` | Snyk sur les dépendances Python installées | High/Critical, jeton absent ou erreur du scanner |
| `dast` | Application dans un réseau Docker temporaire, scan actif ZAP | Alerte High, rapport absent/invalide, application indisponible ou erreur du scanner |
| `security-gate` | Agrégation des quatre résultats | Tout résultat différent de `success`, y compris skipped/cancelled |

ZAP utilise les risques 0 à 3 : High est son niveau maximal habituel. Bloquer dès High
couvre donc le seuil critique demandé par le sujet. Les codes de sortie 1 et 2 de ZAP
sont interprétés à partir du rapport JSON ; les erreurs techniques restent bloquantes.
Les rapports sont conservés comme artefacts même en cas d'échec.

Le déploiement éphémère sert au scan et est détruit en fin de job, même si ZAP échoue.
Aucun port applicatif n'est publié sur l'hôte. Aucun déploiement de production n'est ajouté.
Tout futur job de livraison devra dépendre de `security-gate` sans contourner son résultat.

## Installation et exécution locale

Prérequis : Python 3.12, Git, Docker accessible, Node.js pour Snyk.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
mkdir -p reports
bandit -r app.py --severity-level high -f json -o reports/bandit.json
npm install --global snyk
snyk auth
snyk test --file=requirements.txt --package-manager=pip --command=python --severity-threshold=high --json-file-output=reports/snyk.json
docker build -t tp2-app .
bash scripts/dast.sh
```

Pour consulter l'application sans Docker :

```bash
gunicorn --bind 127.0.0.1:8000 app:app
```

## Activation sur GitHub

1. Ajouter le jeton Snyk dans **Settings → Secrets and variables → Actions → New repository secret**, nom `SNYK_TOKEN`. Ne jamais le committer.
2. Publier les fichiers dans `main` et attendre le premier passage réussi du pipeline.
3. Protéger `main` avec une règle exigeant une pull request et le contrôle `security-gate`. Le pipeline seul ne bloque pas une fusion manuelle si ce contrôle n'est pas rendu obligatoire.
4. Effectuer les deux PR décrites ci-dessous depuis des branches du même dépôt. Les PR provenant de forks n'ont pas accès au secret Snyk et sont donc bloquées. Ne pas utiliser `pull_request_target` pour contourner cela.

Publication initiale depuis ce dossier, une fois GitHub authentifié :

```bash
git add .
git commit -m "Add TP2 DevSecOps application and security pipeline"
git push -u origin main
```

## Démonstration : PR vulnérable puis nouvelle PR corrigée

Les correctifs inverses de démonstration sont des fichiers `.patch` inactifs. Ils ne
modifient l'application qu'après `git apply`. Les utiliser uniquement dans ce TP.

### PR 1 : XSS réfléchie

```bash
git switch -c demo/xss
git apply demo/xss.patch
git add app.py
git commit -m "Demonstrate reflected XSS for TP2"
git push -u origin demo/xss
gh pr create --base main --head demo/xss --title "TP2 : démonstration XSS" --body "Le filtre safe désactive l'échappement et la CSP est retirée. Le scan actif ZAP doit bloquer la PR. Ne pas fusionner."
```

Le champ `name` est découvert par le formulaire de la page d'accueil. La variante
utilise `{{ name | safe }}` et retire la CSP ; du HTML fourni par l'utilisateur est
alors renvoyé sans échappement. Les tests fonctionnels ordinaires passent encore :
c'est le scan DAST qui doit détecter la faille. Résultat attendu, à confirmer dans
Actions : alerte XSS High et `security-gate` rouge. Télécharger `dast-report` et
conserver l'URL de la PR et du run. Ne pas fusionner cette PR.

### PR 2 : correction

```bash
# Partir de la branche vulnérable pour conserver le commit de démonstration.
git switch demo/xss
git switch -c fix/xss
git apply -R demo/xss.patch
# Ajouter un test de non-régression propre à la correction.
cp demo/test_xss.py.txt tests/test_xss.py
git add app.py tests/test_xss.py
git commit -m "Fix reflected XSS and add regression test"
git push -u origin fix/xss
gh pr create --base main --head fix/xss --title "TP2 : correction XSS" --body "Rétablit l'échappement Jinja et la CSP, et ajoute un test de non-régression. Vérifier les rapports SAST, SCA et DAST et le contrôle security-gate."
```

Cette nouvelle PR a un changement réel par rapport à `main` grâce au test ajouté.
Attendre la réussite effective de tous les scans avant de conclure. Fermer ensuite
la PR vulnérable sans la fusionner. Si Snyk signale une nouvelle faille, mettre à
jour la dépendance concernée et relancer ; ne pas masquer le résultat.

### Démonstration SAST supplémentaire

Sur une branche distincte issue de `main`, appliquer `demo/sast-debug.patch` puis
lancer Bandit avec la même commande que le pipeline. L'ajout de `app.run(debug=True)`
déclenche B201, sévérité High, code de sortie 1. Annuler avec
`git apply -R demo/sast-debug.patch` : le scan doit retourner 0.

## Éléments à rendre

- Le dépôt et `.github/workflows/ci.yml`.
- Les liens des deux PR et de leurs exécutions Actions.
- Les rapports SAST/SCA/DAST et captures du contrôle rouge puis vert.
- Une explication : le SAST inspecte le code, le SCA compare les dépendances à une
  base de vulnérabilités, le DAST attaque l'application temporaire en fonctionnement.
- Le bilan vérifié et les limites dans [docs/validation.md](docs/validation.md).

## Références

- [Bandit : options et seuils](https://bandit.readthedocs.io/en/latest/man/bandit.html)
- [Snyk test : seuils et codes de sortie](https://docs.snyk.io/developer-tools/snyk-cli/commands/test)
- [ZAP Full Scan : scan actif et rapports](https://www.zaproxy.org/docs/docker/full-scan/)
- [GitHub : protection des branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
