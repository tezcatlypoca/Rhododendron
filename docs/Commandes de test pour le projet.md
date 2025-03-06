# Commandes de test pour le projet

## Exécution de base

### Tous les tests
```bash
pytest
```

### Tests d'un module spécifique
```bash
pytest run dto
pytest run services
```

### Tests de plusieurs modules
```bash
pytest run dto services
pytest run dto dto_role
```

## Options avancées

### Mode verbeux
```bash
pytest run dto -v
pytest run services -v
```

### Rapport de couverture de code
```bash
pytest run dto --cov
pytest run services --cov
```

### Combinaison d'options
```bash
pytest run dto services -v --cov
pytest run dto dto_role -v --cov
```

## Options complémentaires pytest

### Arrêter après le premier échec
```bash
pytest -x
```

### Afficher les print/logs
```bash
pytest -s
```

### Ré-exécuter les tests qui ont échoué
```bash
pytest --lf  # Last Fail
pytest --ff  # Failed First
```

## Conseils

- Les commandes `pytest run` permettent de cibler facilement des modules spécifiques
- Combinez les options selon vos besoins
- Utilisez `-v` pour plus de détails
- `--cov` génère un rapport de couverture de code