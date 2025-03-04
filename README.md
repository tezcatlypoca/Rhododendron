# 🤖 Crew AI Locale

Un système d'agents AI collaboratifs exécutés entièrement en local pour le développement de petits projets logiciels.

📂 [Voir la structure du projet](docs/Architecture%20dossier%20du%20projet.md)

## 🔍 Vue d'ensemble

Ce projet implémente une équipe d'agents d'intelligence artificielle (manager, développeur, testeur) qui collaborent pour concevoir, créer et tester des projets logiciels. Contrairement aux solutions basées sur le cloud, tous les composants s'exécutent localement sur votre machine.

### ✨ Caractéristiques principales

- 🏠 **100% Local** : Aucune dépendance aux API externes
- 🧠 **Agents spécialisés** : Manager, développeur et testeur travaillant ensemble
- 📊 **Dashboard** : Interface utilisateur pour suivre et gérer les agents
- 🛠️ **Adaptable** : Fonctionne avec des contraintes matérielles raisonnables

## 🏗️ Architecture

Notre système est structuré en couches:

| Couche | Composants | Rôle |
|--------|------------|------|
| **UI** | Streamlit, FastAPI | Interface utilisateur et API |
| **Agents** | Manager, Developer, Tester | Rôles spécialisés pour différentes tâches |
| **Orchestration** | LangChain, CrewAI | Gestion des workflows et interactions |
| **Modèles** | Llama 3, CodeLlama, Mistral | Modèles de fondation pour les agents |
| **Hardware** | GPU, CPU, RAM | Ressources matérielles |

## 💻 Prérequis matériels

### Configuration minimale
- CPU: 6 cœurs / 12 threads
- RAM: 16 GB (32 GB recommandé)
- GPU: 8 GB VRAM (NVIDIA préféré)
- Stockage: SSD 1 TB

### Configuration idéale
- CPU: 8+ cœurs
- RAM: 32-64 GB
- GPU: NVIDIA RTX 3060+ (12GB+ VRAM)
- Stockage: SSD NVMe 2 TB

## 🚀 Installation

```bash
# Cloner le dépôt
git clone https://github.com/tezcatlypoca/Rhododendron.git
cd Rhododendron

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer le dashboard
streamlit run app.py
```

### Installation du model Ollama

- Se rendre sur [Ollama](https://ollama.ai/)
- Télécharger Ollama, puis run la commande suivante:
  
```bash
ollama pull codellama:7b-instruct-q4_0
```


## 📦 Technologies

- **Modèles**: [Llama 3](https://ai.meta.com/llama/), [CodeLlama](https://github.com/facebookresearch/codellama), [Mistral](https://mistral.ai/)
- **Orchestration**: [LangChain](https://www.langchain.com/), [CrewAI](https://www.crewai.io/)
- **Exécution**: [ollama](https://ollama.ai/), [vLLM](https://github.com/vllm-project/vllm)
- **Interface**: [Streamlit](https://streamlit.io/), [FastAPI](https://fastapi.tiangolo.com/)

## 📝 Feuille de route

- [x] Conception de l'architecture
- [ ] Configuration de l'environnement de base
- [ ] Implémentation de l'agent Manager
- [ ] Implémentation de l'agent Developer
- [ ] Implémentation de l'agent Tester
- [ ] Orchestration inter-agents
- [ ] Développement du dashboard
- [ ] Tests et optimisations

## 🤝 Contribution

Les contributions sont les bienvenues! Consultez [CONTRIBUTING.md](CONTRIBUTING.md) pour les détails.

## 📄 Licence

Ce projet est sous licence [MIT](LICENSE).

## 📚 Ressources

- [Documentation LangChain](https://python.langchain.com/en/latest/)
- [Guide de quantification des modèles](https://huggingface.co/docs/transformers/main/en/quantization)
- [Tutoriel CrewAI](https://www.crewai.io/docs/tutorials/getting-started)
