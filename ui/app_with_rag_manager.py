import streamlit as st
import os, tempfile, zipfile, io, json, time, sys
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration des chemins d'importation
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)  # Pour accéder à settings.py
sys.path.append(os.path.dirname(root_dir))  # Pour accéder au dossier contenant src

# Import des modules locaux
from settings import PATH_CONFIG
from src.rag_manager import RAGManager

# Configuration - MISE À JOUR DU CHEMIN POUR VOTRE
BASE_DIR = PATH_CONFIG['base']
GENERATED_DIR = PATH_CONFIG['generated_prompt']
VECTORDB_DIR = PATH_CONFIG['vector_db']
DATA_DIR = PATH_CONFIG['data']
PROJETS_DIR = PATH_CONFIG['projets']
DOC_DIR = PATH_CONFIG['documentation']

# Créer le dossier pour les fichiers générés
os.makedirs(GENERATED_DIR, exist_ok=True)

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Flutter/Java RAG Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .stTextArea textarea {
        font-family: monospace;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #e1f5fe;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1rem;
        margin-bottom: 0px;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour charger le RAG Manager
@st.cache_resource
def get_rag_manager():
    """Initialise et retourne une instance de RAGManager"""
    return RAGManager(
        vector_db_dir=VECTORDB_DIR,
        data_dir=DATA_DIR
    )

# Fonction pour charger le modèle LLM
@st.cache_resource
def charger_llm(model_name, temperature):
    """Charge le modèle LLM avec Ollama."""
    return Ollama(
        model=model_name, 
        temperature=temperature,
        num_ctx=4096,        # Contexte plus large
        num_predict=2048,    # Sortie plus longue
        timeout=120,         # Timeout plus long (2 minutes)
        stop=["```end"],     # Token de fin optionnel
    )
# Templates de prompt avec contexte
PROMPT_TEMPLATES = {
    "composant_ui": """
Tu es un expert en développement Flutter et Java pour applications Android.
Tu dois générer un composant d'interface utilisateur selon les spécifications.

Voici du code de projets similaires qui pourrait t'aider:
------------------------
{contexte}
------------------------

Cahier des charges: {cahier_charges}

Génère le code complet du composant UI avec:
1. Le code source bien structuré et commenté
2. Des explications sur les choix d'implémentation
3. Les dépendances nécessaires
4. Des conseils pour l'intégration

Utilise les meilleures pratiques Flutter/Dart et assure-toi que le composant est:
- Réutilisable
- Performant
- Accessible
- Compatible avec les différentes tailles d'écran
""",

    "authentification": """
Tu es un expert en développement Flutter et Java pour applications Android.
Tu dois générer un système d'authentification selon les spécifications.

Voici du code de projets similaires qui pourrait t'aider:
------------------------
{contexte}
------------------------

Cahier des charges: {cahier_charges}

Génère le code complet du système d'authentification avec:
1. Le code source bien structuré et commenté
2. La gestion des états d'authentification
3. Les validations de formulaires
4. La gestion des erreurs
5. Les dépendances nécessaires

Utilise les meilleures pratiques de sécurité et d'architecture.
""",

    "architecture": """
Tu es un expert en développement Flutter et Java pour applications Android.
Tu dois générer l'architecture d'un projet selon les spécifications.

Voici du code de projets similaires qui pourrait t'aider:
------------------------
{contexte}
------------------------

Cahier des charges: {cahier_charges}

Génère une architecture complète avec:
1. La structure des dossiers
2. Les fichiers principaux
3. Les patterns d'architecture recommandés (MVC, MVVM, BLoC, etc.)
4. Les dépendances nécessaires
5. Des explications sur les choix d'architecture

Utilise les meilleures pratiques d'architecture et de développement.
""",

    "api_integration": """
Tu es un expert en développement Flutter et Java pour applications Android.
Tu dois générer du code pour intégrer une API selon les spécifications.

Voici du code de projets similaires qui pourrait t'aider:
------------------------
{contexte}
------------------------

Cahier des charges: {cahier_charges}

Génère le code complet d'intégration API avec:
1. Les modèles de données
2. Les services/repositories
3. La gestion des erreurs et timeouts
4. La mise en cache (si nécessaire)
5. Les dépendances nécessaires

Utilise les meilleures pratiques d'intégration API et de développement.
""",

    "general": """
Tu es un expert en développement Flutter et Java pour applications Android.
Ta tâche est de générer du code selon les spécifications.

Voici du code de projets similaires qui pourrait t'aider:
------------------------
{contexte}
------------------------

Cahier des charges: {cahier_charges}

Génère le code complet avec:
1. Le code source bien structuré et commenté
2. Des explications sur les choix d'implémentation
3. Les dépendances nécessaires
4. Des conseils pour l'utilisation et l'intégration

Utilise les meilleures pratiques Flutter/Dart/Java et assure-toi que le code soit performant et bien structuré.
"""
}

# Fonctions d'utilitaires
def extract_code_blocks(markdown_text):
    """Extrait les blocs de code d'un texte markdown"""
    code_blocks = []
    lines = markdown_text.split('\n')
    in_block = False
    current_lang = ""
    current_block = []
    
    for line in lines:
        if line.startswith('```') and not in_block:
            in_block = True
            current_lang = line[3:].strip()
            continue
        elif line.startswith('```') and in_block:
            in_block = False
            code_blocks.append((current_lang, '\n'.join(current_block)))
            current_block = []
            continue
        
        if in_block:
            current_block.append(line)
    
    return code_blocks

def clean_language_tag(lang):
    """Nettoie et normalise les tags de langage"""
    lang = lang.lower().strip()
    if lang in ('dart', 'yaml', 'json', 'xml', 'md', 'markdown'):
        return lang
    elif lang == 'yaml':
        return 'yaml'
    elif lang == 'markdown':
        return 'markdown'
    elif lang == 'json':
        return 'json'
    return ''

# Application Streamlit
def main():
    # Initialiser le RAG Manager
    rag_manager = get_rag_manager()
    
    # Structure des pages/onglets
    st.sidebar.title("🚀 Flutter/Java RAG Generator")
    
    pages = {
        "Générateur de Code": "generator",
        "Gestion RAG": "rag_management",
        "Visualisation": "visualization"
    }
    
    selected_page = st.sidebar.radio("Navigation", list(pages.keys()))
    
    # En fonction de la page sélectionnée
    if pages[selected_page] == "generator":
        show_generator_page(rag_manager)
    elif pages[selected_page] == "rag_management":
        show_rag_management_page(rag_manager)
    elif pages[selected_page] == "visualization":
        show_visualization_page(rag_manager)
def show_generator_page(rag_manager):
    st.title("🚀 Générateur de Code Flutter/Java avec RAG")
    st.markdown(
        """
        <div class="info-box">
        Cet outil utilise un système RAG (Retrieval-Augmented Generation) pour générer du code Flutter/Java 
        de haute qualité en utilisant votre base de connaissances personnelle.
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Barre latérale pour les paramètres
    with st.sidebar:
        st.header("⚙️ Paramètres")
        
        # Sélection du modèle
        model_options = {
            "codellama:7b-instruct-q4_0": "CodeLlama 7B (Recommandé pour le code)",
            "mistral:7b-instruct-q4_0": "Mistral 7B (Alternative, bon équilibre)",
            "phi2:q4_0": "Phi-2 (Plus léger, moins précis)"
        }
        model_name = st.selectbox(
            "Modèle LLM", 
            list(model_options.keys()),
            format_func=lambda x: model_options[x]
        )
        
        # Paramètres de génération
        st.subheader("Paramètres de génération")
        temperature = st.slider("Température", 0.0, 1.0, 0.2, 0.1, 
                              help="Plus la valeur est basse, plus la génération est déterministe")
        
        k_documents = st.slider("Nombre de documents à récupérer", 2, 15, 5,
                              help="Nombre de documents à utiliser comme contexte")
        
        # Filtrage par extension
        st.subheader("Filtrage")
        filter_by_ext = st.checkbox("Filtrer par extension", value=False)
        
        extension_filter = None
        if filter_by_ext:
            extensions = ["dart", "java", "kt", "xml", "yaml", "json", "md"]
            extension_filter = st.selectbox("Extension", extensions)
        
        # Type de projet
        st.subheader("Type de projet")
        project_type = st.radio(
            "Plateforme cible",
            ["Flutter", "Java Android", "Les deux"]
        )
        
        # Template de prompt
        st.subheader("Template de prompt")
        template_type = st.selectbox(
            "Type de génération",
            ["general", "composant_ui", "authentification", "architecture", "api_integration"],
            format_func=lambda x: {
                "general": "Général",
                "composant_ui": "Composant UI",
                "authentification": "Authentification",
                "architecture": "Architecture",
                "api_integration": "Intégration API"
            }[x]
        )
        
        # Histoire des générations
        st.subheader("Historique")
        if "history" in st.session_state and st.session_state.history:
            for i, item in enumerate(st.session_state.history):
                if st.button(f"{item['title'][:25]}...", key=f"history_{i}"):
                    st.session_state.cahier_charges = item["cahier_charges"]
                    st.session_state.generated_code = item["code"]

    # Interface principale
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Cahier des charges")
        
        # Titre du projet
        project_title = st.text_input(
            "Titre du projet ou composant",
            value=st.session_state.get("project_title", ""),
            help="Un titre court et descriptif pour votre projet ou composant"
        )
        
        # Cahier des charges
        cahier_charges = st.text_area(
            "Décrivez les fonctionnalités souhaitées",
            height=400,  # Augmenté à 400 pour plus d'espace
            value=st.session_state.get("cahier_charges", ""),
            help="Soyez précis dans votre description pour obtenir un meilleur résultat",
            placeholder="""Exemple: 
Créer une page de connexion Flutter avec les fonctionnalités suivantes:
- Champs email et mot de passe avec validation
- Bouton de connexion avec indicateur de chargement
- Option "Mot de passe oublié"
- Connexion via Google et Facebook
- Navigation vers la page d'inscription
- Stockage du token JWT après connexion
- Compatible dark/light mode
"""
        )
        
        # Options avancées
        with st.expander("Options avancées"):
            include_tests = st.checkbox("Générer des tests", value=False)
            include_docs = st.checkbox("Inclure la documentation", value=True)
            include_dependencies = st.checkbox("Lister les dépendances", value=True)
        
        # Bouton de génération
        gen_button = st.button("🔮 Générer le code", type="primary", use_container_width=True)
        
        # Aperçu du contexte
        if "context_results" in st.session_state:
            with st.expander("Aperçu du contexte récupéré"):
                for i, res in enumerate(st.session_state.context_results):
                    source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
                    st.markdown(f"**Document {i+1}** - Source: `{source}`")
                    st.code(res["contenu"][:300] + "..." if len(res["contenu"]) > 300 else res["contenu"])
    
    with col2:
        st.header("💻 Code généré")
        
        # Affichage du code généré
        if "generated_code" in st.session_state:
            generated_code = st.session_state.generated_code
            
            # Onglets pour différentes parties du code
            code_parts = generated_code.split("```")
            code_blocks = []  # Initialisation de code_blocks ici
            
            if len(code_parts) > 1:
                # Extraction des blocs de code
                for i in range(1, len(code_parts), 2):
                    if i < len(code_parts):
                        lang = code_parts[i].split("\n")[0].strip()
                        code = "\n".join(code_parts[i].split("\n")[1:])
                        code_blocks.append((lang, code))
                
                # S'il y a des blocs de code
                if code_blocks:
                    tabs = st.tabs([f"Fichier {i+1}" for i in range(len(code_blocks))])
                    
                    for i, (tab, (lang, code)) in enumerate(zip(tabs, code_blocks)):
                        with tab:
                            st.code(code, language=lang if lang in ["dart", "java", "kotlin", "yaml", "xml", "json"] else None)
                
                # Afficher les explications
                for i in range(0, len(code_parts), 2):
                    if code_parts[i].strip():
                        st.markdown(code_parts[i])
            else:
                # Pas de blocs de code, afficher comme un seul bloc
                st.code(generated_code)
            
            # Boutons d'action
            col_download, col_save = st.columns(2)
            
            with col_download:
                # Créer un zip avec tous les fichiers
                if st.button("📦 Télécharger en ZIP", use_container_width=True):
                    # Extraire les fichiers du code généré
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w") as zf:
                        # Créer un fichier pour chaque bloc de code
                        for i, (lang, code) in enumerate(code_blocks):
                            # Déterminer l'extension de fichier
                            ext = {
                                "dart": ".dart",
                                "java": ".java",
                                "kotlin": ".kt",
                                "yaml": ".yaml",
                                "xml": ".xml",
                                "json": ".json"
                            }.get(lang, ".txt")
                            
                            file_name = f"file_{i+1}{ext}"
                            zf.writestr(file_name, code)
                    
                    # Proposer le téléchargement
                    zip_buffer.seek(0)
                    project_name = project_title.replace(" ", "_") if project_title else "generated_code"
                    st.download_button(
                        "⬇️ Télécharger ZIP",
                        zip_buffer,
                        file_name=f"{project_name}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )
            
            with col_save:
                # Sauvegarder dans l'historique
                if st.button("💾 Enregistrer dans l'historique", use_container_width=True):
                    if "history" not in st.session_state:
                        st.session_state.history = []
                    
                    # Ajouter à l'historique
                    st.session_state.history.append({
                        "title": project_title if project_title else "Sans titre",
                        "cahier_charges": cahier_charges,
                        "code": generated_code,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    
                    st.success("Sauvegardé dans l'historique!")
                    # Recharger la page pour mettre à jour l'historique
                    st.rerun()
        elif "generated_files" in st.session_state and st.session_state.generated_files:
            # Afficher les fichiers générés individuellement
            file_names = list(st.session_state.generated_files.keys())
            
            # Organiser les fichiers par type
            config_files = [f for f in file_names if f.endswith('.yaml') or f.endswith('.json')]
            dart_files = [f for f in file_names if f.endswith('.dart')]
            doc_files = [f for f in file_names if f.endswith('.md')]
            other_files = [f for f in file_names if f not in config_files + dart_files + doc_files]
            
            # Créer des onglets principaux
            main_tabs = st.tabs(["Code", "Configuration", "Documentation", "Tous les fichiers"])
            
            # Onglet Code (fichiers Dart)
            with main_tabs[0]:
                if dart_files:
                    for file in sorted(dart_files):
                        with st.expander(file):
                            file_data = st.session_state.generated_files[file]
                            st.code(file_data['content'], language=file_data['language'])
                else:
                    st.info("Aucun fichier de code généré.")
            
            # Onglet Configuration
            with main_tabs[1]:
                if config_files:
                    for file in sorted(config_files):
                        with st.expander(file):
                            file_data = st.session_state.generated_files[file]
                            st.code(file_data['content'], language=file_data['language'])
                else:
                    st.info("Aucun fichier de configuration généré.")
            
            # Onglet Documentation
            with main_tabs[2]:
                if doc_files:
                    for file in sorted(doc_files):
                        with st.expander(file):
                            file_data = st.session_state.generated_files[file]
                            st.markdown(file_data['content'])
                else:
                    st.info("Aucune documentation générée.")
            
            # Onglet Tous les fichiers
            with main_tabs[3]:
                for file in sorted(file_names):
                    with st.expander(file):
                        file_data = st.session_state.generated_files[file]
                        if file_data['language'] == 'markdown':
                            st.markdown(file_data['content'])
                        else:
                            st.code(file_data['content'], language=file_data['language'])
            
            # Bouton de téléchargement
            if st.button("📦 Télécharger le projet complet", use_container_width=True):
                # Créer un zip avec tous les fichiers
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w") as zf:
                    for file_name, file_data in st.session_state.generated_files.items():
                        zf.writestr(file_name, file_data['content'])
                
                zip_buffer.seek(0)
                project_name = project_title.replace(" ", "_") if project_title else "generated_project"
                st.download_button(
                    "⬇️ Télécharger ZIP",
                    zip_buffer,
                    file_name=f"{project_name}.zip",
                    mime="application/zip",
                    use_container_width=True
                )
        else:
            st.info("Le code généré apparaîtra ici après la génération.")

    # Logique de génération du code
    if gen_button and cahier_charges:
        with st.spinner("Planification de la génération de code..."):
            try:
                # 1. Rechercher du contexte pertinent
                if filter_by_ext and extension_filter:
                    contexte, resultats = rag_manager.filter_by_extension(
                        extension_filter, 
                        cahier_charges, 
                        k=k_documents
                    )
                else:
                    contexte, resultats = rag_manager.search_context(
                        cahier_charges, 
                        k=k_documents
                    )
                
                # Sauvegarder les résultats pour l'affichage
                st.session_state.context_results = resultats
                
                # 2. Étape 1 : Demander la liste des fichiers nécessaires
                prompt_fichiers = f"""
                Tu es un expert en développement de jeux Flutter, spécialisé dans les jeux de type Shoot'em up.

                Basé sur les spécifications suivantes:
                {cahier_charges}

                Liste exhaustive des fichiers nécessaires pour développer ce projet de jeu Shoot'em up, un par ligne.
                Format de réponse: chemin/nom_du_fichier.extension

                Conseils pour la décomposition :
                - Décompose le projet en composants logiques et réutilisables
                - Crée des fichiers séparés pour chaque responsabilité distincte
                - Inclus tous les fichiers nécessaires à une implémentation complète de jeu
                - Priorise la modularité et la performance
                - N'hésite pas à créer plusieurs fichiers pour gérer différents aspects du jeu
                """
                
                llm = charger_llm(model_name, temperature=0.3)  # Légèrement plus créatif mais structuré
                
                # Utiliser directement l'appel à Ollama pour cette première étape
                st.write("🔍 Détermination des fichiers nécessaires...")
                liste_fichiers_raw = llm.invoke(prompt_fichiers)
                
                # Nettoyer la sortie et extraire les noms de fichiers
                liste_fichiers = [f.strip() for f in liste_fichiers_raw.strip().split('\n') 
                                if f.strip() and not f.startswith('#') and not f.startswith('```')]
                
                # Filtrer les lignes non pertinentes
                liste_fichiers = [f for f in liste_fichiers if '.' in f and len(f) > 3]
                
                # Afficher la progression
                st.write(f"📂 {len(liste_fichiers)} fichiers identifiés:")
                fichiers_placeholder = st.empty()
                fichiers_placeholder.write(", ".join(liste_fichiers))
                
                # Initialiser le stockage des fichiers générés
                st.session_state.generated_files = {}
                
                # 3. Étape 2 : Générer chaque fichier individuellement
                progress_bar = st.progress(0)
                
                combined_code = ""
                
                for i, fichier in enumerate(liste_fichiers):
                    fichier_progress = st.empty()
                    fichier_progress.write(f"⚙️ Génération de {fichier}...")
                    
                    # Prompt spécifique pour chaque fichier
                    prompt_fichier = f"""
                    Tu es un expert en développement Flutter/Dart, spécialisé dans les jeux mobiles.
                    
                    CONTEXTE:
                    {contexte[:1500]}  # Limiter la taille du contexte pour chaque fichier
                    
                    SPECIFICATIONS DU PROJET:
                    {cahier_charges}
                    
                    TÂCHE:
                    Génère uniquement le code pour le fichier `{fichier}` du projet.
                    
                    IMPORTANT:
                    - Ton code doit être complet et fonctionnel
                    - Utilise les meilleures pratiques pour Flutter et Dart
                    - Ne génère que le contenu de ce fichier spécifique, sans explications externes
                    
                    Fournis seulement le code du fichier, sans commentaires externes, dans un bloc de code markdown.
                    """
                    
                    # Ajuster la température selon le type de fichier
                    file_temp = 0.2
                    if fichier.endswith('.md'):
                        file_temp = 0.7  # Plus de créativité pour les fichiers README
                    elif fichier.endswith('.yaml'):
                        file_temp = 0.1  # Précision pour les fichiers de configuration
                    
                    file_llm = charger_llm(model_name, file_temp)
                    
                    try:
                        file_content = file_llm.invoke(prompt_fichier)
                        
                        # Nettoyer la sortie
                        clean_content = file_content
                        if "```" in file_content:
                            # Extraire le contenu entre les délimiteurs de code
                            parts = file_content.split("```")
                            if len(parts) >= 3:
                                # Récupérer le type de langage à partir de la première ligne après ```
                                lang_line = parts[1].strip().split('\n')[0]
                                code_content = '\n'.join(parts[1].strip().split('\n')[1:])
                                clean_content = code_content
                        
                        # Stocker le fichier généré
                        extension = fichier.split('.')[-1]
                        language = {
                            'dart': 'dart',
                            'yaml': 'yaml',
                            'md': 'markdown',
                            'json': 'json',
                            'xml': 'xml',
                        }.get(extension, '')
                        
                        st.session_state.generated_files[fichier] = {
                            'content': clean_content,
                            'language': language
                        }
                        
                        # Ajouter au code combiné pour l'affichage global
                        combined_code += f"\n\n## {fichier}\n\n```{language}\n{clean_content}\n```\n"
                        
                    except Exception as e:
                        st.warning(f"Erreur lors de la génération de {fichier}: {str(e)}")
                        combined_code += f"\n\n## {fichier}\n\n```\nErreur lors de la génération: {str(e)}\n```\n"
                    
                    # Mettre à jour la progression
                    progress_bar.progress((i + 1) / len(liste_fichiers))
                    fichier_progress.write(f"✅ {fichier} généré")
                
                # 4. Stockage du résultat final
                st.session_state.generated_code = combined_code
                st.session_state.cahier_charges = cahier_charges
                st.session_state.project_title = project_title
                
                # 5. Recharger la page pour afficher le résultat
                st.success("Génération terminée! Affichage des résultats...")
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur lors de la génération du code: {str(e)}")
                st.error("Vérifiez que Ollama est bien installé et que le modèle est disponible.")

def valider_structure_projet(liste_fichiers, cahier_charges):
    """Optionnel : Valider que la structure de fichiers couvre bien les besoins"""
    prompt_validation = f"""
    Vérifie si la liste de fichiers {liste_fichiers} couvre complètement 
    les spécifications : {cahier_charges}
    
    Si incomplet, propose des fichiers additionnels.
    """
    # Logique de validation/raffinement

def show_rag_management_page(rag_manager):
    st.title("🧠 Gestion de la Base de Connaissances RAG")
    
    # Vérifier si la base vectorielle est chargée
    if not rag_manager.vectordb:
        loaded = rag_manager.load_vectordb()
        if not loaded:
            st.warning("La base vectorielle n'a pas pu être chargée ou n'existe pas encore.")
    
    # Onglets pour la gestion RAG
    tabs = st.tabs(["Statistiques", "Mise à jour", "Tests", "Configuration"])
    
    # Onglet Statistiques
    with tabs[0]:
        st.header("📊 Statistiques de la base vectorielle")
        
        stats = rag_manager.get_statistics()
        
        if stats["status"] == "ok":
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Nombre de documents", stats["document_count"])
                st.metric("Sources uniques", stats["unique_sources"])
                
                # Tableau des extensions
                st.subheader("Extensions de fichiers")
                extensions_df = pd.DataFrame({
                    "Extension": list(stats["extensions"].keys()),
                    "Nombre": list(stats["extensions"].values())
                })
                st.dataframe(extensions_df, use_container_width=True)
                
                # Visualisation des extensions
                if not extensions_df.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sns.barplot(data=extensions_df, x="Extension", y="Nombre", ax=ax)
                    ax.set_title("Distribution des extensions de fichiers")
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
                    st.pyplot(fig)
            
            with col2:
                st.subheader("Top 10 des sources")
                sources_df = pd.DataFrame({
                    "Source": list(stats["top_sources"].keys()),
                    "Nombre": list(stats["top_sources"].values())
                })
                st.dataframe(sources_df, use_container_width=True)
                
                # Visualisation des sources
                if not sources_df.empty:
                    fig, ax = plt.subplots(figsize=(10, 6))
                    sources_plot = sources_df.head(10)  # Limiter à 10 sources pour la lisibilité
                    sns.barplot(data=sources_plot, x="Source", y="Nombre", ax=ax)
                    ax.set_title("Top 10 des sources les plus fréquentes")
                    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
                    st.pyplot(fig)
        else:
            st.error(f"Erreur lors de la récupération des statistiques: {stats.get('message', 'Erreur inconnue')}")

    # Onglet Mise à jour
    with tabs[1]:
        st.header("🔄 Mise à jour de la base vectorielle")
        
        st.markdown("""
        <div class="info-box">
        Vous pouvez mettre à jour la base vectorielle en ajoutant de nouveaux documents ou en recréant complètement la base.
        </div>
        """, unsafe_allow_html=True)
        
        # Choix du dossier
        update_dir = st.text_input("Chemin du dossier à ajouter", value=PROJETS_DIR)
        
        # Extensions à inclure
        all_extensions = ["dart", "java", "kt", "gradle", "xml", "yaml", "json", "md", "txt", "properties"]
        selected_extensions = st.multiselect("Extensions à inclure", all_extensions, default=all_extensions)
        
        # Options de mise à jour
        recreate = st.checkbox("Recréer complètement la base", value=False, 
                               help="Si coché, la base existante sera supprimée et une nouvelle sera créée")
        
        # Bouton de mise à jour
        if st.button("Mettre à jour la base vectorielle", type="primary"):
            with st.spinner("Mise à jour en cours..."):
                success = rag_manager.update_from_directory(
                    directory=update_dir,
                    extensions=selected_extensions,
                    recreate=recreate
                )
                
                if success:
                    st.success("Base vectorielle mise à jour avec succès!")
                else:
                    st.error("Erreur lors de la mise à jour de la base vectorielle.")

    # Onglet Tests
    with tabs[2]:
        st.header("🧪 Tester la base vectorielle")
        
        # Requêtes de test
        default_queries = [
            "Comment créer une page de connexion dans Flutter",
            "Comment implémenter une liste déroulante avec recherche",
            "Comment gérer l'authentification avec Firebase",
            "Comment créer une interface adaptative pour différentes tailles d'écran"
        ]
        
        # Éditeur de requêtes
        st.subheader("Requêtes de test")
        test_queries = []
        
        # Utiliser des sessions pour stocker les requêtes
        if "test_queries" not in st.session_state:
            st.session_state.test_queries = default_queries.copy()
        
        # Afficher les requêtes existantes
        for i, query in enumerate(st.session_state.test_queries):
            cols = st.columns([4, 1])
            with cols[0]:
                st.session_state.test_queries[i] = st.text_input(f"Requête {i+1}", value=query, key=f"query_{i}")
            with cols[1]:
                if st.button("Supprimer", key=f"del_{i}"):
                    st.session_state.test_queries.pop(i)
                    st.rerun()
        
        # Ajouter une nouvelle requête
        if st.button("+ Ajouter une requête"):
            st.session_state.test_queries.append("")
            st.rerun()
        
        # Bouton pour exécuter les tests
        if st.button("Lancer les tests", type="primary"):
            with st.spinner("Exécution des tests..."):
                results = rag_manager.test_search(st.session_state.test_queries)
                
                # Afficher les résultats
                if results:
                    st.subheader("Résultats des tests")
                    
                    for query, docs in results.items():
                        st.markdown(f"**Requête:** _{query}_")
                        
                        for i, doc in enumerate(docs):
                            with st.expander(f"Résultat {i+1} - {os.path.basename(doc['source'])}"):
                                st.code(doc["full_content"])
                        
                        st.markdown("---")
                else:
                    st.error("Aucun résultat trouvé ou erreur lors de l'exécution des tests.")
    
    # Onglet Configuration
    with tabs[3]:
        st.header("⚙️ Configuration")
        
        # Afficher les répertoires configurés
        st.subheader("Répertoires configurés")
        
        st.markdown(f"""
        - **Base de données vectorielle:** `{VECTORDB_DIR}`
        - **Données:** `{DATA_DIR}`
        - **Projets:** `{PROJETS_DIR}`
        - **Documentation:** `{DOC_DIR}`
        - **Fichiers générés:** `{GENERATED_DIR}`
        """)
        
        # Afficher les dossiers exclus
        st.subheader("Dossiers exclus")
        
        excluded_dirs = rag_manager.excluded_dirs
        st.write(", ".join(excluded_dirs))
        
        # Option pour modifier les dossiers exclus
        with st.expander("Modifier les dossiers exclus"):
            new_excluded = st.text_area(
                "Dossiers à exclure (un par ligne)", 
                value="\n".join(excluded_dirs)
            )
            
            if st.button("Appliquer"):
                rag_manager.excluded_dirs = [d.strip() for d in new_excluded.split("\n") if d.strip()]
                st.success("Liste des dossiers exclus mise à jour.")

def show_visualization_page(rag_manager):
    st.title("📊 Visualisation des données RAG")
    
    # Charger les statistiques
    stats = rag_manager.get_statistics()
    
    if stats["status"] != "ok":
        st.error("Impossible de charger les données pour la visualisation.")
        return
    
    st.header("Explorer la base de connaissances")
    
    # Interface de recherche
    query = st.text_input("Recherche dans la base de connaissances", 
                        placeholder="Ex: Flutter authentification, Java liste, etc.")
    
    k_results = st.slider("Nombre de résultats", 1, 20, 5)
    
    # Bouton de recherche
    if st.button("Rechercher", type="primary") and query:
        with st.spinner("Recherche en cours..."):
            _, results = rag_manager.search_context(query, k=k_results)
            
            if results:
                st.subheader(f"Résultats pour: '{query}'")
                
                for i, res in enumerate(results):
                    source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
                    
                    with st.expander(f"Document {i+1} - {source}"):
                        st.code(res["contenu"])
            else:
                st.warning("Aucun résultat trouvé.")
    
    # Visualisation de la distribution des données
    st.header("Distribution des données")
    
    # Distribution par extension
    extensions_data = stats["extensions"]
    if extensions_data:
        # Créer un DataFrame
        ext_df = pd.DataFrame({
            "Extension": list(extensions_data.keys()),
            "Nombre": list(extensions_data.values())
        })
        
        # Afficher le graphique
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=ext_df, x="Extension", y="Nombre", ax=ax)
        ax.set_title("Distribution des documents par extension")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
        st.pyplot(fig)
    
    # Afficher quelques métriques
    if "document_count" in stats:
        st.subheader("Métriques de la base vectorielle")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Documents totaux", stats["document_count"])
        
        with col2:
            st.metric("Sources uniques", stats["unique_sources"])
        
        with col3:
            # Calculer les extensions les plus fréquentes
            top_ext = max(stats["extensions"].items(), key=lambda x: x[1])[0] if stats["extensions"] else "N/A"
            st.metric("Extension la plus fréquente", top_ext)

# Fonction principale
if __name__ == "__main__":
    # Initialiser l'historique s'il n'existe pas
    if "history" not in st.session_state:
        st.session_state.history = []
    
    main()