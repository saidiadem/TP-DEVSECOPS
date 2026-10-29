# Bilan de validation — 29 octobre 2026

## Vérifié localement

- 8 tests unitaires réussis : application et règles de blocage du rapport ZAP.
- Test de non-régression fourni pour la PR corrigée : réussi séparément.
- Bandit 1.8.6 sur l'application corrigée : code 0, aucune alerte High.
- Patch SAST appliqué dans un dossier temporaire : B201 High, code 1.
- Patch XSS appliqué dans un dossier temporaire : la réponse contient le script
  non échappé et ne contient plus de CSP. Dans la version corrigée, le script est
  échappé. Cette vérification utilise le client de test Flask ; ce n'est pas un scan DAST.
- Syntaxe Bash et lecture YAML vérifiées ; workflow validé par actionlint 1.7.12
  (sans ShellCheck) ; dépendances Python cohérentes (`pip check`).
- Les deux patches sont applicables à la version livrée.
- Construction de l'image `tp2-app` : réussie après ouverture des accès Docker.
- Authentification GitHub : confirmée pour `saidiadem`.

## Reste à vérifier dans un environnement disposant des accès

- Scan ZAP réel : en cours de validation ; aucune détection ZAP réelle n'est encore revendiquée.
- Scan Snyk : non exécuté, jeton Snyk à configurer. La version des dépendances ne
  constitue pas une preuve d'absence de vulnérabilité.
- Exécution GitHub Actions, protection de `main` et deux PR : à valider.
  Le dépôt distant était vide ; une copie locale a été initialisée avec le remote demandé.

## Limites et décisions

- Analyse DAST non authentifiée de cette petite application uniquement.
- Bandit analyse `app.py`, unique fichier applicatif. Étendre sa cible si le code
  est réparti dans d'autres modules.
- Snyk analyse les dépendances d'exécution, y compris les dépendances transitives
  figées dans `requirements.txt`. Les outils de développement ne sont pas inclus
  dans ce périmètre SCA.
- Les versions majeures des actions, l'image Python et l'image ZAP stable peuvent
  évoluer. Pour une reproductibilité stricte, figer aussi leurs SHA/digests après
  une première exécution vérifiée.
- Une première exécution verte, puis les deux PR, restent nécessaires pour rendre
  la preuve complète demandée dans le TP.
