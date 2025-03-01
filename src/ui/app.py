import streamlit as st
import os, tempfile, zipfile, io, json, time
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from settings import PATH_CONFIG

# Configuration - MISE À JOUR DU CHEMIN POUR VOTRE 
BASE_DIR = PATH_CONFIG['base']
GENERATED_DIR = PATH_CONFIG['generated_prompt']
VECTORDB_DIR = PATH_CONFIG['vector_db']

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
</style>
""", unsafe_allow_html=True)

# Fonction pour charger la base vectorielle
@st.cache_resource
def charger_base_vectorielle():
    """Charge la base vectorielle pour la recherche."""
    embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)
    
    # Vérifier si la base vectorielle existe
    if not os.path.exists(f"{VECTORDB_DIR}/chroma"):
        st.error("Base vectorielle non trouvée. Veuillez la créer d'abord.")
        st.stop()
    
    # Charger la base
    vectordb = Chroma(
        persist_directory=f"{VECTORDB_DIR}/chroma",
        embedding_function=embeddings
    )
    
    return vectordb

# Fonction pour charger le modèle LLM
@st.cache_resource
def charger_llm(model_name, temperature):
    """Charge le modèle LLM avec Ollama."""
    return Ollama(model=model_name, temperature=temperature)

# Fonction pour la recherche de contexte
def rechercher_contexte(query, vectordb, k=5):
    """Recherche du contexte pertinent dans la base vectorielle."""
    documents = vectordb.similarity_search(query, k=k)
    
    # Extraire le contenu et les métadonnées
    resultats = []
    for doc in documents:
        resultats.append({
            "contenu": doc.page_content,
            "source": doc.metadata.get("source", "Inconnue")
        })
    
    # Formatter le contexte
    contexte = ""
    for i, res in enumerate(resultats):
        source = os.path.basename(res["source"]) if isinstance(res["source"], str) else "Inconnue"
        contexte += f"--- Document {i+1} (Source: {source}) ---\n"
        contexte += res["contenu"] + "\n\n"
    
    return contexte, resultats

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

# Application Streamlit
def main():
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
        else:
            st.info("Aucune génération dans l'historique.")

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
            height=300,
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
            
            if len(code_parts) > 1:
                # Extraction des blocs de code
                code_blocks = []
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
        else:
            st.info("Le code généré apparaîtra ici après la génération.")

    # Logique de génération du code
    if gen_button and cahier_charges:
        with st.spinner("Génération du code en cours..."):
            try:
                # 1. Charger la base vectorielle
                vectordb = charger_base_vectorielle()
                
                # 2. Rechercher du contexte pertinent
                contexte, resultats = rechercher_contexte(
                    cahier_charges, 
                    vectordb, 
                    k=k_documents
                )
                
                # Sauvegarder les résultats pour l'affichage
                st.session_state.context_results = resultats
                
                # 3. Préparer le prompt avec le contexte
                template = PROMPT_TEMPLATES.get(template_type, PROMPT_TEMPLATES["general"])
                
                # Ajouter des instructions spécifiques
                if include_tests:
                    template += "\nInclus également des tests unitaires pour le code généré."
                if include_docs:
                    template += "\nInclus une documentation complète avec des exemples d'utilisation."
                if include_dependencies:
                    template += "\nListe toutes les dépendances nécessaires avec leurs versions."
                
                # Ajouter des instructions sur le type de projet
                if project_type == "Flutter":
                    template += "\nUtilise uniquement Flutter/Dart pour l'implémentation."
                elif project_type == "Java Android":
                    template += "\nUtilise uniquement Java pour l'implémentation Android native."
                
                prompt = PromptTemplate(
                    template=template,
                    input_variables=["contexte", "cahier_charges"]
                )
                
                # 4. Charger le LLM
                llm = charger_llm(model_name, temperature)
                
                # 5. Créer la chaîne
                chain = LLMChain(llm=llm, prompt=prompt)
                
                # 6. Générer le code
                response = chain.run(
                    contexte=contexte, 
                    cahier_charges=cahier_charges
                )
                
                # 7. Sauvegarder le résultat dans la session
                st.session_state.generated_code = response
                st.session_state.cahier_charges = cahier_charges
                st.session_state.project_title = project_title
                
                # 8. Recharger la page pour afficher le résultat
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur lors de la génération du code: {str(e)}")
                st.error("Vérifiez que Ollama est bien installé et que le modèle est disponible.")

# Fonction principale
if __name__ == "__main__":
    # Initialiser l'historique s'il n'existe pas
    if "history" not in st.session_state:
        st.session_state.history = []
    
    main()