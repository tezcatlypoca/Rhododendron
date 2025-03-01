# Configuration et recommandation de modèles LLM

## Configuration Hardware
- **CPU** : Intel Xeon E5-2420V2 (6 cœurs, 12 threads)
  - Processus de gestion : suffisant pour gérer les processus, surtout avec un modèle optimisé pour GPU.
- **GPU** : 2x **RX Vega 64** 
  - Limitation de bande passante PCIe (x16 et x8) qui peut impacter la communication avec les modèles plus grands.
- **RAM** : 32-64 Go
  - Suffisant pour des modèles de taille moyenne. Éviter les modèles trop volumineux.
- **Stockage** : SSD 2To
  - Idéal pour stocker de grands modèles et assurer des chargements rapides.

## Modèles LLM recommandés

### 1. **Mistral 7B ou 12B (quantifié)**
- **Pourquoi ?**
  - **Mistral 7B** : modèle plus léger, optimisé pour limiter l'utilisation mémoire GPU, version quantifiée (Q4_0 ou Q8_0) pour éviter de saturer la bande passante PCIe.
  - **Mistral 12B** : pour des **prompts complexes**, mais nécessite des optimisations pour éviter la surcharge des ressources.
- **Exécution multi-GPU** : Utilisation avec des frameworks tels que **DeepSpeed**, **Accelerate**, ou **Hugging Face** pour gérer deux **Vega 64**. Le slot PCIe x8 peut limiter un peu les performances.

### 2. **CodeLlama (7B ou 13B) en version quantifiée**
- **Pourquoi ?**
  - **CodeLlama 7B** : léger et performant pour des tâches de programmation ou de génération de code, bien adapté pour des tâches simples à moyennement complexes.
  - **Version quantifiée (Q4_0 ou Q8_0)** pour optimiser la mémoire et la vitesse.
  
### 3. **Llama 2 (7B ou 13B)**
- **Pourquoi ?**
  - **Llama 2 7B** : bonne option pour des tâches relativement complexes tout en limitant la charge GPU.
  - **Llama 2 13B** : à optimiser avec quantification pour éviter de saturer la bande passante PCIe du GPU en x8.

## Stratégie de gestion des ressources
- **Quantification des modèles** : Pour optimiser l'utilisation de tes **Vega 64**, utilise des versions quantifiées (Q4_0 ou Q8_0) des modèles pour réduire l'utilisation de la mémoire GPU et alléger la bande passante PCIe.
- **Exécution multi-GPU** : Configure avec **DeepSpeed** ou **Accelerate** pour utiliser au mieux les deux **Vega 64**, tout en gardant en tête la bande passante PCIe x8.

## Conclusion
Pour une **bonne qualité de réponse** et **optimisation des ressources matérielles** de ton serveur :
- **Modèles recommandés** : **Mistral 7B** (quantifié) ou **CodeLlama 7B/13B** (quantifié).
- Si tu veux un modèle plus grand : **Mistral 12B** pourrait être envisagé, mais il faudra bien optimiser le modèle pour gérer la mémoire GPU et la bande passante PCIe.
