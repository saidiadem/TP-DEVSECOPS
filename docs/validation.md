# Bilan de validation — 29 octobre 2026

## Preuves GitHub Actions

| Version | Référence | Résultat |
| --- | --- | --- |
| Application initiale sûre | [Run main](https://github.com/saidiadem/TP-DEVSECOPS/actions/runs/40883544121) | Pipeline vert après configuration du secret Snyk et relance |
| XSS volontaire | [PR #1](https://github.com/saidiadem/TP-DEVSECOPS/pull/1), [run](https://github.com/saidiadem/TP-DEVSECOPS/actions/runs/40883638151) | ZAP détecte deux alertes High : XSS réfléchie (40012) et XSS DOM (40026) |
| XSS corrigée | [PR #2](https://github.com/saidiadem/TP-DEVSECOPS/pull/2), [run du correctif](https://github.com/saidiadem/TP-DEVSECOPS/actions/runs/40883884921) | Les cinq jobs réussissent : build-test, sast, sca, dast et security-gate |

La PR #2 rétablit l'échappement Jinja et la CSP, puis ajoute un test de
non-régression. Le run vert ci-dessus valide le correctif ; le dernier run de la
PR valide aussi les éventuelles mises à jour documentaires ultérieures.

Les artefacts `sast-report`, `sca-report` et `dast-report` sont téléchargeables dans
les runs. Le rapport DAST contient `zap.html`, `zap.json` et les logs de l'application.
Le premier lancement a révélé un secret Snyk absent ; après configuration, Snyk
passe sans modification ni désactivation du seuil de sécurité.

## Vérifications locales

- 9 tests unitaires réussis dans la version corrigée.
- Le test XSS échoue sur la variante vulnérable et réussit sur la correction.
- Bandit 1.8.6 : code 0 sur l'application corrigée ; le patch SAST supplémentaire
  déclenche B201 High et retourne 1.
- Construction Docker réussie, avec un utilisateur applicatif non root.
- Syntaxe Bash, compilation Python et dépendances (`pip check`) vérifiées.
- Workflow validé par actionlint 1.7.12, sans ShellCheck.

## Blocage effectif

La branche `main` exige une pull request et le contrôle `security-gate`, y compris
pour les administrateurs. Chaque résultat requis doit être `success` ; échec,
annulation ou job ignoré empêchent la validation. Les force-pushs et suppressions
sont désactivés sur `main`.

Le scan actif vise uniquement l'application éphémère du TP dans un réseau Docker
isolé. Aucun port n'est publié sur l'hôte. Les conteneurs et le réseau sont supprimés
à la fin du scan. Aucun déploiement de production n'est créé.

## Interprétation et limites

- Le résultat vert signifie qu'aucune alerte n'atteint les seuils bloquants ; il ne
  signifie pas que tous les rapports sont vides ou qu'aucune vulnérabilité n'existe.
- Le rapport ZAP du code sûr conserve notamment une alerte Medium `HTTP Only Site`
  sur l'environnement éphémère HTTP, ainsi que des alertes Low sur certains en-têtes.
  Ces alertes restent visibles ; elles ne sont pas masquées par une exclusion.
- Le scan DAST est non authentifié. L'application ne possède pas de zone connectée.
- Bandit analyse `app.py`, unique module applicatif. Étendre sa cible si le projet grandit.
- Snyk analyse les dépendances d'exécution directes et transitives figées dans
  `requirements.txt`. Les outils de développement sont hors de ce périmètre SCA.
- Les images et versions majeures des actions peuvent évoluer. Figer aussi leurs
  SHA/digests si une reproductibilité stricte est nécessaire.
- La PR vulnérable sert uniquement de preuve et ne doit pas être fusionnée.
  Les PR sont laissées disponibles pour évaluation ; aucune fusion n'a été effectuée.
