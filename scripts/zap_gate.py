"""Échec sur risque High ZAP (3), rapport vide/invalide ou cible absente."""
import json
import sys
from pathlib import Path


def evaluate(report):
    sites = report["site"]
    if not isinstance(sites, list) or not sites:
        raise ValueError("Aucune cible dans le rapport ZAP")
    blocking = []
    for site in sites:
        alerts = site["alerts"]
        if not isinstance(alerts, list):
            raise ValueError("Liste d'alertes ZAP invalide")
        for alert in alerts:
            risk = int(alert["riskcode"])
            if risk not in range(5):
                raise ValueError("Risque ZAP inconnu")
            if risk >= 3:
                blocking.append(alert["name"])
    return blocking


def main():
    try:
        blocking = evaluate(json.loads(Path(sys.argv[1]).read_text()))
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print(f"DAST impossible à valider : {exc}", file=sys.stderr)
        return 2
    if blocking:
        print("DAST bloqué : " + ", ".join(blocking))
        return 1
    print("DAST : aucune alerte High ou supérieure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
