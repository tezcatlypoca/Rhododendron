import streamlit as st
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import time
import json
from pathlib import Path
import asyncio

# Gestion de la boucle asyncio pour éviter les erreurs d'exécution
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Configuration des chemins d'importation
# Remonter au répertoire parent du répertoire parent de ce fichier (à partir de src/ui)
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
root_dir = os.path.dirname(src_dir)
sys.path.append(root_dir)  # Pour accéder à settings.py

# Import des modules
try:
    from settings import PATH_CONFIG
except ImportError:
    st.error("Impossible d'importer 'settings'. Assurez-vous que le fichier settings.py est bien dans le répertoire racine du projet.")
    PATH_CONFIG = {
        'base': root_dir,
        'data': os.path.join(root_dir, 'data'),
        'projets': os.path.join(root_dir, 'data', 'projets'),
        'documentation': os.path.join(root_dir, 'data', 'documentation'),
        'vector_db': os.path.join(root_dir, 'data', 'vector_db'),
    }
    st.warning(f"Utilisation de chemins par défaut: {PATH_CONFIG}")

# Importer Vectorisation après avoir défini les chemins
try:
    from src.vectorisation import Vectorisation
except ImportError:
    st.error("Impossible d'importer 'Vectorisation'. Vérifiez que le fichier src/vectorisation.py existe.")
    st.stop()

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Vectorisation Tester",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_vectorisation():
    """Initialise et retourne l'instance de Vectorisation"""
    return Vectorisation(
        vector_db_dir=PATH_CONFIG['vector_db'],
        data_dir=PATH_CONFIG['data']
    )

def visualize_statistics(stats):
    """Visualise les statistiques de la base vectorielle"""
    if "extensions" in stats and stats["extensions"]:
        # Dataframe des extensions
        extensions_df = pd.DataFrame({
            'Extension': list(stats["extensions"].keys()),
            'Nombre': list(stats["extensions"].values())
        }).sort_values('Nombre', ascending=False)
        
        # Visualisation des extensions
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(extensions_df['Extension'], extensions_df['Nombre'])
        
        # Ajouter les étiquettes
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f'{height}',
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
        
        ax.set_title('Distribution des fichiers par extension')
        ax.set_ylabel('Nombre de fichiers')
        st.pyplot(fig)
    
    # Afficher les sources principales si disponibles
    if "top_sources" in stats and stats["top_sources"]:
        st.subheader("Sources principales")
        sources_df = pd.DataFrame({
            'Source': list(stats["top_sources"].keys()),
            'Nombre': list(stats["top_sources"].values())
        }).sort_values('Nombre', ascending=False)
        st.dataframe(sources_df)

def main():
    st.title("🔍 Testeur de Vectorisation")
    
    # Vérifier la structure des répertoires
    for key, path in PATH_CONFIG.items():
        if not os.path.exists(path) and key != 'vector_db':  # vector_db peut ne pas exister encore
            os.makedirs(path, exist_ok=True)
            st.info(f"Répertoire créé: {path}")
    
    # Barre latérale
    with st.sidebar:
        st.header("Configuration")
        st.markdown(f"""
        **Chemins configurés**:
        - Base: `{PATH_CONFIG['base']}`
        - Données: `{PATH_CONFIG['data']}`
        - Projets: `{PATH_CONFIG['projets']}`
        - Documentation: `{PATH_CONFIG['documentation']}`
        - Base vectorielle: `{PATH_CONFIG['vector_db']}`
        """)
        
        # Options
        st.subheader("Options")
        force_recreate = st.checkbox("Forcer la recréation de la base", value=False)
        
        # Extensions
        st.subheader("Extensions")
        default_extensions = [".dart", ".java", ".kt", ".gradle", ".xml", ".yaml", ".json", ".md", ".txt"]
        extensions = st.multiselect(
            "Extensions à inclure",
            options=[".dart", ".java", ".kt", ".gradle", ".xml", ".yaml", ".json", ".md", ".txt", ".properties"],
            default=default_extensions
        )
        
        # Dossiers exclus
        st.subheader("Dossiers exclus")
        excluded_dirs = st.text_area(
            "Dossiers à exclure (un par ligne)",
            value="node_modules\n.git\n.idea\nbuild\ndist\n.dart_tool\n.pub-cache"
        ).split("\n")
        excluded_dirs = [d.strip() for d in excluded_dirs if d.strip()]
    
    # Onglets principaux
    tabs = st.tabs(["État de la base", "Test de recherche", "Gestion de la base"])
    
    # Initialiser l'instance de Vectorisation
    try:
        vectorisation = get_vectorisation()
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation de la Vectorisation: {str(e)}")
        st.stop()
    
    # Onglet 1: État de la base
    with tabs[0]:
        st.header("État de la base vectorielle")
        
        base_exists = os.path.exists(os.path.join(PATH_CONFIG['vector_db'], "chroma"))
        
        if base_exists:
            st.markdown("<div class='success-box'>✅ Base vectorielle existante détectée</div>", unsafe_allow_html=True)
            
            # Charger la base et afficher les statistiques
            try:
                if vectorisation.load_vectordb():
                    stats = vectorisation.get_statistics()
                    
                    if stats["status"] == "ok":
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Documents totaux", stats["document_count"])
                        with col2:
                            st.metric("Sources uniques", stats.get("unique_sources", "N/A"))
                        with col3:
                            last_update = stats.get("last_update", "Inconnue")
                            if isinstance(last_update, str) and len(last_update) > 10:
                                last_update = last_update[:10]  # Juste la date
                            st.metric("Dernière mise à jour", last_update)
                        
                        # Visualiser les statistiques
                        visualize_statistics(stats)
                    else:
                        st.markdown(f"<div class='error-box'>⚠️ Erreur: {stats.get('message', 'Inconnue')}</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='error-box'>⚠️ Erreur: Impossible de charger la base vectorielle</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Erreur lors du chargement de la base: {str(e)}")
        else:
            st.markdown("<div class='warning-box'>⚠️ Aucune base vectorielle existante détectée</div>", unsafe_allow_html=True)
            st.markdown("Veuillez créer une base vectorielle dans l'onglet 'Gestion de la base'.")
            
            # Ajouter un bouton pour créer rapidement une base
            if st.button("Créer une base vectorielle maintenant"):
                st.session_state.switch_tab = "Gestion de la base"
                st.rerun()
    
    # Onglet 2: Test de recherche
    with tabs[1]:
        st.header("Test de recherche")
        
        if not base_exists:
            st.markdown("<div class='warning-box'>⚠️ Aucune base vectorielle existante. Veuillez d'abord créer une base.</div>", unsafe_allow_html=True)
        else:
            try:
                vectorisation.load_vectordb()
                
                # Interface de recherche
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    query = st.text_input("Recherche dans la base vectorielle", 
                                        placeholder="Ex: Comment implémenter la navigation dans Flutter",
                                        label_visibility="collapsed")
                
                with col2:
                    k_results = st.slider("Nombre de résultats", 1, 10, 3)
                
                # Filtrage optionnel par extension
                use_filter = st.checkbox("Filtrer par extension")
                filter_ext = None
                
                if use_filter:
                    filter_ext = st.selectbox(
                        "Extension",
                        options=["dart", "java", "kt", "gradle", "xml", "yaml", "json", "md"]
                    )
                
                # Bouton de recherche
                if st.button("🔍 Rechercher", type="primary", disabled=not query):
                    with st.spinner("Recherche en cours..."):
                        start_time = time.time()
                        
                        try:
                            if use_filter and filter_ext:
                                context, results = vectorisation.filter_by_extension(filter_ext, query, k=k_results)
                            else:
                                if hasattr(vectorisation, 'search_similar'):
                                    context, results = vectorisation.search_similar(query, k=k_results)
                                else:
                                    context, results = vectorisation.search_context(query, k=k_results)
                            
                            end_time = time.time()
                            duration = end_time - start_time
                            
                            if results:
                                st.success(f"Recherche effectuée en {duration:.2f} secondes")
                                
                                for i, res in enumerate(results):
                                    source = os.path.basename(res["source"]) if "source" in res and res["source"] else "Inconnue"
                                    score = f" (Score: {res['score']:.4f})" if "score" in res else ""
                                    
                                    with st.expander(f"Résultat {i+1} - {source}{score}"):
                                        st.code(res.get("contenu", res.get("content", "")))
                                        st.markdown(f"Source complète: `{res['source']}`")
                            else:
                                st.warning("Aucun résultat trouvé.")
                        except Exception as e:
                            st.error(f"Erreur lors de la recherche: {str(e)}")
                
                # Section pour les tests prédéfinis
                with st.expander("Tests prédéfinis"):
                    st.subheader("Exécuter des requêtes de test")
                    
                    # Quelques requêtes prédéfinies
                    predefined_queries = [
                        "page de connexion Flutter",
                        "navigation Android",
                        "gestion d'état BLoC",
                        "API REST",
                        "interface adaptative"
                    ]
                    
                    # Bouton pour chaque requête prédéfinie
                    for query in predefined_queries:
                        if st.button(query):
                            with st.spinner(f"Recherche pour: '{query}'"):
                                try:
                                    context, results = vectorisation.search_context(query, k=3)
                                    
                                    if results:
                                        for i, res in enumerate(results):
                                            source = os.path.basename(res["source"]) if "source" in res and res["source"] else "Inconnue"
                                            with st.expander(f"Résultat {i+1} - {source}"):
                                                st.code(res.get("contenu", res.get("content", "")))
                                    else:
                                        st.warning("Aucun résultat trouvé.")
                                except Exception as e:
                                    st.error(f"Erreur lors de la recherche: {str(e)}")
            except Exception as e:
                st.error(f"Erreur lors de l'utilisation de la base vectorielle: {str(e)}")
    
    # Onglet 3: Gestion de la base
    with tabs[2]:
        st.header("Gestion de la base vectorielle")
        
        # Source des documents
        st.subheader("Source des documents")
        source_options = ["Projets", "Documentation", "Les deux"]
        source_choice = st.radio("Sélectionnez la source des documents", source_options)
        
        source_mapping = {
            "Projets": PATH_CONFIG['projets'],
            "Documentation": PATH_CONFIG['documentation'],
            "Les deux": None  # Géré spécialement
        }
        
        selected_source = source_mapping[source_choice]
        
        # Uploader des fichiers pour les tests
        with st.expander("Ajouter des fichiers de test"):
            st.subheader("Uploader des fichiers pour tester")
            uploaded_files = st.file_uploader("Choisissez des fichiers", accept_multiple_files=True)
            
            if uploaded_files:
                save_dir = PATH_CONFIG['projets'] if source_choice in ["Projets", "Les deux"] else PATH_CONFIG['documentation']
                
                # Créer un sous-dossier pour les fichiers uploadés
                upload_dir = os.path.join(save_dir, "uploaded_files")
                os.makedirs(upload_dir, exist_ok=True)
                
                files_saved = []
                for uploaded_file in uploaded_files:
                    # Sauvegarder le fichier
                    file_path = os.path.join(upload_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    files_saved.append(uploaded_file.name)
                
                if files_saved:
                    st.success(f"{len(files_saved)} fichiers enregistrés dans {upload_dir}")
                    st.write("Fichiers enregistrés :", ", ".join(files_saved))
        
        # Bouton pour créer ou mettre à jour la base
        if st.button("Créer/Mettre à jour la base vectorielle", type="primary"):
            with st.spinner("Traitement en cours..."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Fonction de rappel pour mettre à jour la progression
                def update_progress(current, total, message=""):
                    progress = float(current) / float(total)
                    progress_bar.progress(progress)
                    if message:
                        status_text.markdown(f"<div class='info-box'>{message}</div>", unsafe_allow_html=True)
                
                try:
                    # Charger les documents selon la source choisie
                    if source_choice == "Les deux":
                        # Charger à la fois les projets et la documentation
                        update_progress(0.1, 1, "Chargement des projets...")
                        code_docs = vectorisation.load_documents(PATH_CONFIG['projets'], extensions)
                        
                        update_progress(0.3, 1, "Chargement de la documentation...")
                        doc_docs = vectorisation.load_documents(PATH_CONFIG['documentation'], extensions)
                        
                        update_progress(0.5, 1, "Combinaison des documents...")
                        all_docs = code_docs + doc_docs
                        
                        update_progress(0.6, 1, f"Création de la base vectorielle avec {len(all_docs)} documents...")
                        success = vectorisation.create_vectordb(all_docs, force_recreate=force_recreate)
                    else:
                        # Charger depuis une seule source
                        update_progress(0.2, 1, f"Chargement depuis {source_choice}...")
                        docs = vectorisation.load_documents(selected_source, extensions)
                        
                        update_progress(0.6, 1, f"Création de la base vectorielle avec {len(docs)} documents...")
                        success = vectorisation.create_vectordb(docs, force_recreate=force_recreate)
                    
                    # Finaliser
                    if success:
                        update_progress(1.0, 1, "Base vectorielle créée avec succès!")
                        st.success("Base vectorielle créée avec succès!")
                        st.balloons()
                        
                        # Recharger les statistiques
                        vectorisation.load_vectordb()
                        stats = vectorisation.get_statistics()
                        if stats["status"] == "ok":
                            st.json(stats)
                    else:
                        update_progress(1.0, 1, "Erreur lors de la création de la base vectorielle.")
                        st.error("Erreur lors de la création de la base vectorielle.")
                except Exception as e:
                    update_progress(1.0, 1, f"Erreur: {str(e)}")
                    st.error(f"Erreur: {str(e)}")
        
        # Option pour supprimer la base existante
        with st.expander("Options avancées"):
            st.warning("Ces actions sont irréversibles. Procédez avec prudence.")
            
            if st.button("Supprimer la base vectorielle existante", type="secondary"):
                if os.path.exists(os.path.join(PATH_CONFIG['vector_db'], "chroma")):
                    try:
                        import shutil
                        shutil.rmtree(os.path.join(PATH_CONFIG['vector_db'], "chroma"))
                        st.success("Base vectorielle supprimée avec succès!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de la suppression de la base: {str(e)}")
                else:
                    st.info("Aucune base vectorielle à supprimer.")

    # Si demandé, basculer vers un onglet spécifique
    if 'switch_tab' in st.session_state:
        tab_index = source_options.index(st.session_state.switch_tab) if st.session_state.switch_tab in source_options else 2
        # Réinitialiser après le changement
        st.session_state.switch_tab = None

if __name__ == "__main__":
    main()