import streamlit as st
import os
import sys
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Ajout du répertoire parent au PYTHONPATH pour trouver le module settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import PATH_CONFIG

# Configuration
BASE_DIR = PATH_CONFIG['base']
GENERATED_DIR = PATH_CONFIG['generated_prompt']

# Créer le dossier pour les fichiers générés
os.makedirs(GENERATED_DIR, exist_ok=True)

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Flutter/Java Code Generator",
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
    .info-box {
        background-color: #e1f5fe;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour charger le modèle LLM
def charger_llm(model_name, temperature):
    """Charge le modèle LLM avec Ollama."""
    return Ollama(model=model_name, temperature=temperature)

# Templates de prompt avec contexte
PROMPT_TEMPLATES = {
    "general": """
Tu es un expert en développement Flutter et Java pour applications Android.
Ta tâche est de générer du code selon les spécifications.

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
    st.title("🚀 Générateur de Code Flutter/Java (Version simple)")
    st.markdown(
        """
        <div class="info-box">
        Cet outil utilise CodeLlama pour générer du code Flutter/Java de haute qualité.
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Barre latérale pour les paramètres
    with st.sidebar:
        st.header("⚙️ Paramètres")
        
        # Sélection du modèle
        model_options = {
            "codellama:7b-instruct-q4_0": "CodeLlama 7B (Recommandé pour le code)"
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
        
        # Type de projet
        st.subheader("Type de projet")
        project_type = st.radio(
            "Plateforme cible",
            ["Flutter", "Java Android", "Les deux"]
        )

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
        else:
            st.info("Le code généré apparaîtra ici après la génération.")

    # Logique de génération du code
    if gen_button and cahier_charges:
        with st.spinner("Génération du code en cours..."):
            try:
                # Préparer le prompt
                template = PROMPT_TEMPLATES["general"]
                
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
                    input_variables=["cahier_charges"]
                )
                
                # Charger le LLM
                llm = charger_llm(model_name, temperature)
                
                # Créer la chaîne
                chain = LLMChain(llm=llm, prompt=prompt)
                
                # Générer le code
                response = chain.run(cahier_charges=cahier_charges)
                
                # Sauvegarder le résultat dans la session
                st.session_state.generated_code = response
                st.session_state.cahier_charges = cahier_charges
                st.session_state.project_title = project_title
                
                # Recharger la page pour afficher le résultat
                st.rerun()
                
            except Exception as e:
                st.error(f"Erreur lors de la génération du code: {str(e)}")
                st.error("Vérifiez que Ollama est bien installé et que le modèle est disponible.")

# Fonction principale
if __name__ == "__main__":
    main()