import streamlit as st
import pandas as pd
from PIL import Image
import random
import os

# Configuration de la page
st.set_page_config(
    page_title="Rhododendron - Orchestration",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation de la session state pour la navigation
if 'page' not in st.session_state:
    st.session_state.page = 'home'
if 'selected_orchestra' not in st.session_state:
    st.session_state.selected_orchestra = None

# Fonction pour générer des données fictives d'orchestres
def generate_sample_orchestras(num_orchestras=5):
    orchestra_types = ["Développement", "Communication", "Design", "Marketing", "Recherche"]
    orchestra_names = [f"Orchestre {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Omega', 'Nova', 'Stellar', 'Quantum', 'Phoenix', 'Nebula'])} {i+1}" for i in range(num_orchestras)]
    
    orchestras = []
    for i in range(num_orchestras):
        orch_type = random.choice(orchestra_types)
        
        # Définir les instruments en fonction du type d'orchestre
        if orch_type == "Développement":
            instruments = [
                {"name": "Développeur", "description": "Code les fonctionnalités"},
                {"name": "Testeur", "description": "Vérifie la qualité du code"},
                {"name": "Manageur", "description": "Organise les priorités"},
                {"name": "Architecte", "description": "Conçoit la structure technique"}
            ]
        elif orch_type == "Communication":
            instruments = [
                {"name": "Rédacteur", "description": "Crée le contenu écrit"},
                {"name": "Designer", "description": "Conçoit les visuels"},
                {"name": "Community Manager", "description": "Gère les réseaux sociaux"},
                {"name": "Stratège", "description": "Planifie les campagnes"}
            ]
        elif orch_type == "Design":
            instruments = [
                {"name": "UX Designer", "description": "Crée l'expérience utilisateur"},
                {"name": "UI Designer", "description": "Conçoit les interfaces"},
                {"name": "Graphiste", "description": "Produit les éléments graphiques"},
                {"name": "Prototypeur", "description": "Teste les concepts"}
            ]
        elif orch_type == "Marketing":
            instruments = [
                {"name": "Analyste", "description": "Étudie les données du marché"},
                {"name": "Contenu", "description": "Crée les supports marketing"},
                {"name": "SEO", "description": "Optimise la visibilité"},
                {"name": "Croissance", "description": "Développe l'audience"}
            ]
        else:  # Recherche
            instruments = [
                {"name": "Chercheur", "description": "Explore de nouveaux domaines"},
                {"name": "Analyste de données", "description": "Traite les informations"},
                {"name": "Documentaliste", "description": "Organise les connaissances"},
                {"name": "Expérimentateur", "description": "Teste les hypothèses"}
            ]
        
        # Créer des projets fictifs pour cet orchestre
        num_projects = random.randint(1, 3)
        projects = []
        for j in range(num_projects):
            project_status = random.choice(["En cours", "Planifié", "Terminé", "En pause"])
            project_names = [
                "Refonte du site", "Application mobile", "Campagne Q2", "Étude utilisateurs",
                "Intégration API", "Restructuration", "Automatisation", "Analyse de données"
            ]
            projects.append({
                "name": random.choice(project_names) + f" {j+1}",
                "status": project_status,
                "progress": random.randint(0, 100) if project_status != "Planifié" else 0,
                "assigned_instruments": random.sample([instr["name"] for instr in instruments], random.randint(1, len(instruments)))
            })
        
        # Date de création aléatoire
        date_created = f"{random.randint(1, 28)}/{random.randint(1, 12)}/2024"
        
        # Statut aléatoire
        status = random.choice(["Actif", "En pause", "Archivé", "En préparation"])
        
        orchestras.append({
            "name": orchestra_names[i],
            "type": orch_type,
            "instruments": instruments,
            "projects": projects,
            "date_created": date_created,
            "status": status
        })
    
    return orchestras

# Styles CSS personnalisés
st.markdown("""
<style>
    .orchestra-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
    }
    .orchestra-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }
    .orchestra-title {
        color: #1E3A8A;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .orchestra-type {
        color: #4B5563;
        font-size: 16px;
        margin-bottom: 5px;
    }
    .orchestra-date {
        color: #6B7280;
        font-size: 14px;
        margin-bottom: 15px;
    }
    .instrument-tag {
        background-color: #E5E7EB;
        border-radius: 15px;
        padding: 5px 10px;
        margin-right: 5px;
        margin-bottom: 5px;
        display: inline-block;
        font-size: 12px;
    }
    .status-tag {
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
    }
    .status-active {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .status-paused {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .status-archived {
        background-color: #F3F4F6;
        color: #4B5563;
    }
    .status-prep {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    .add-btn {
        background-color: #1E3A8A;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
        margin-top: 20px;
        font-weight: bold;
    }
    .centered {
        display: flex;
        justify-content: center;
    }
    .back-btn {
        display: inline-flex;
        align-items: center;
        color: #1E3A8A;
        font-weight: 500;
        margin-bottom: 20px;
        cursor: pointer;
    }
    .section-title {
        margin-top: 30px;
        margin-bottom: 15px;
        color: #1E3A8A;
        font-size: 20px;
        font-weight: 600;
    }
    .btn-primary {
        background-color: #1E3A8A;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
    }
    .btn-secondary {
        background-color: #E5E7EB;
        color: #4B5563;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
    }
    /* Personnaliser les boutons Streamlit pour qu'ils soient visibles et attrayants */
    .stButton>button {
        background-color: #1E3A8A !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
        border-radius: 0.375rem !important;
        margin-top: 0.5rem !important;
        width: 100% !important;
        display: block !important;
    }
    .stButton>button:hover {
        background-color: #1e4cba !important;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour afficher la page d'accueil
def show_home_page():
    st.title("🎵 Rhododendron - Orchestration")
    st.markdown("### Bienvenue dans votre plateforme d'orchestration")
    st.markdown("---")
    
    # Générer des orchestres fictifs
    orchestras = generate_sample_orchestras(6)
    
    # Filtres et contenu de la page d'accueil...
    return orchestras

# Fonction pour afficher la page de détail d'un orchestre
def show_orchestra_detail(orchestra):
    # Bouton de retour explicite
    back_btn = st.button("← Retour aux orchestres", key="back_btn")
    if back_btn:
        st.session_state.page = "home"
        st.session_state.selected_orchestra = None
        st.rerun()
    
    # Affichage du titre et des informations de l'orchestre
    st.title(f"Orchestre: {orchestra['name']}")
    
    # En-tête avec les informations générales
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Type**: {orchestra['type']}")
    with col2:
        st.markdown(f"**Créé le**: {orchestra['date_created']}")
    with col3:
        status_class = ""
        if orchestra["status"] == "Actif":
            status_color = "green"
        elif orchestra["status"] == "En pause":
            status_color = "orange"
        elif orchestra["status"] == "Archivé":
            status_color = "gray"
        else:
            status_color = "blue"
        st.markdown(f"**Statut**: <span style='color:{status_color};'>{orchestra['status']}</span>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Affichage des instruments
    st.markdown("### 🎻 Instruments")
    
    # Création de tabs pour organiser l'affichage
    tabs = st.tabs(["Instruments", "Projets", "Performance"])
    
    with tabs[0]:
        # Affichage des instruments
        if len(orchestra['instruments']) > 0:
            # Calculer le nombre de colonnes en fonction du nombre d'instruments
            num_cols = min(4, len(orchestra['instruments']))
            instruments_cols = st.columns(num_cols)
            
            for i, instrument in enumerate(orchestra['instruments']):
                with instruments_cols[i % num_cols]:
                    st.markdown(f"""
                    <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 15px;">
                        <h4>{instrument['name']}</h4>
                        <p style="color: #666;">{instrument['description']}</p>
                        <button class="btn-secondary">Configurer</button>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Bouton pour ajouter un instrument
            st.markdown("""
            <div style="border: 1px dashed #1E3A8A; border-radius: 8px; padding: 15px; text-align: center; cursor: pointer; margin-top: 15px;">
                <h4 style="color: #1E3A8A;">+ Ajouter un instrument</h4>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Aucun instrument n'est associé à cet orchestre.")
            st.button("+ Ajouter votre premier instrument")
    
    with tabs[1]:
        # Affichage des projets
        if len(orchestra['projects']) > 0:
            # Afficher les projets sous forme de cartes
            for project in orchestra['projects']:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### {project['name']}")
                    st.markdown(f"**Statut**: {project['status']}")
                    st.progress(project['progress'])
                with col2:
                    st.markdown("**Instruments assignés:**")
                    for instrument in project['assigned_instruments']:
                        st.markdown(f"- {instrument}")
                st.markdown("---")
            
            # Bouton pour ajouter un projet
            st.button("+ Ajouter un nouveau projet")
        else:
            st.info("Aucun projet n'est associé à cet orchestre.")
            st.button("+ Créer votre premier projet")
    
    with tabs[2]:
        # Affichage des métriques de performance
        st.markdown("### Métriques de l'orchestre")
        
        # Métriques fictives
        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric(label="Projets complétés", value=random.randint(3, 12))
        with metric_cols[1]:
            st.metric(label="Taux d'achèvement", value=f"{random.randint(60, 95)}%")
        with metric_cols[2]:
            st.metric(label="Temps moyen par projet", value=f"{random.randint(10, 30)} jours")
        
        st.markdown("### Activité récente")
        activity_data = [
            {"date": "02/03/2025", "event": "Nouveau projet ajouté", "user": "Alice"},
            {"date": "28/02/2025", "event": "Instrument Développeur configuré", "user": "Bob"},
            {"date": "25/02/2025", "event": "Projet Refonte terminé", "user": "Charlie"}
        ]
        
        for activity in activity_data:
            st.markdown(f"**{activity['date']}** - {activity['event']} par {activity['user']}")
            st.markdown("---")

# Fonction pour afficher la page de création d'orchestre
def show_create_orchestra():
    # Bouton de retour explicite
    back_btn = st.button("← Retour aux orchestres", key="back_btn_create")
    if back_btn:
        st.session_state.page = "home"
        st.rerun()
    
    st.title("Créer un nouvel orchestre")
    
    # Formulaire de création d'orchestre
    with st.form("new_orchestra_form"):
        st.text_input("Nom de l'orchestre", key="new_orchestra_name")
        selected_type = st.selectbox("Type d'orchestre", 
                    options=["Développement", "Communication", "Design", "Marketing", "Recherche"],
                    key="new_orchestra_type")
        
        st.text_area("Description", key="new_orchestra_description", 
                   placeholder="Décrivez l'objectif et la mission de cet orchestre...")
        
        # Choix des instruments initiaux
        st.markdown("### Instruments initiaux")
        st.markdown("Sélectionnez les instruments à inclure dès la création de l'orchestre")
        
        # Affichage dynamique des instruments en fonction du type choisi
        if selected_type == "Développement":
            cols = st.columns(4)
            with cols[0]:
                dev = st.checkbox("Développeur", value=True)
                if dev:
                    st.text_input("Description", value="Code les fonctionnalités", key="dev_desc")
            with cols[1]:
                test = st.checkbox("Testeur", value=True)
                if test:
                    st.text_input("Description", value="Vérifie la qualité du code", key="test_desc")
            with cols[2]:
                manager = st.checkbox("Manageur")
                if manager:
                    st.text_input("Description", value="Organise les priorités", key="manager_desc")
            with cols[3]:
                architect = st.checkbox("Architecte")
                if architect:
                    st.text_input("Description", value="Conçoit la structure technique", key="architect_desc")
        
        elif selected_type == "Communication":
            cols = st.columns(4)
            with cols[0]:
                writer = st.checkbox("Rédacteur", value=True)
                if writer:
                    st.text_input("Description", value="Crée le contenu écrit", key="writer_desc")
            with cols[1]:
                designer = st.checkbox("Designer", value=True)
                if designer:
                    st.text_input("Description", value="Conçoit les visuels", key="designer_desc")
            with cols[2]:
                cm = st.checkbox("Community Manager")
                if cm:
                    st.text_input("Description", value="Gère les réseaux sociaux", key="cm_desc")
            with cols[3]:
                strategist = st.checkbox("Stratège")
                if strategist:
                    st.text_input("Description", value="Planifie les campagnes", key="strategist_desc")
        
        else:
            st.markdown("Sélectionnez d'abord un type d'orchestre pour voir les instruments disponibles.")
        
        # Ajouter un premier projet (optionnel)
        st.markdown("### Premier projet (optionnel)")
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nom du projet", key="first_project_name")
        with col2:
            st.selectbox("Statut initial", options=["Planifié", "En cours"], key="first_project_status")
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            cancel_btn = st.form_submit_button("Annuler")
        with col2:
            create_btn = st.form_submit_button("Créer l'orchestre")
        
        if create_btn:
            st.success("Orchestre créé avec succès!")
            # Redirection vers la page d'accueil après 2 secondes
            st.session_state.page = "home"
            st.rerun()
        
        if cancel_btn:
            st.session_state.page = "home"
            st.rerun()

# Routage principal en fonction de la page actuelle
if st.session_state.page == "home":
    orchestras = show_home_page()
elif st.session_state.page == "orchestra_detail":
    show_orchestra_detail(st.session_state.selected_orchestra)
    orchestras = []  # Pas besoin d'orchestres sur cette page
elif st.session_state.page == "create_orchestra":
    show_create_orchestra()
    orchestras = []  # Pas besoin d'orchestres sur cette page
else:
    st.session_state.page = "home"
    orchestras = show_home_page()

# Barre latérale avec filtres (uniquement sur la page d'accueil)
if st.session_state.page == "home":
    st.sidebar.title("Filtres")
    status_filter = st.sidebar.multiselect(
        "Statut",
        options=["Actif", "En pause", "Archivé", "En préparation"],
        default=["Actif", "En préparation"]
    )

    type_filter = st.sidebar.multiselect(
        "Type d'orchestre",
        options=["Développement", "Communication", "Design", "Marketing", "Recherche"],
        default=[]
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Actions rapides")
    if st.sidebar.button("Rafraîchir les orchestres"):
        st.rerun()
else:
    # Affichage d'informations contextuelles dans la barre latérale pour les autres pages
    st.sidebar.title("Rhododendron")
    st.sidebar.markdown("### Navigation")
    if st.sidebar.button("Retour à l'accueil"):
        st.session_state.page = "home"
        st.session_state.selected_orchestra = None
        st.rerun()
    
    if st.session_state.page == "orchestra_detail":
        # Informations supplémentaires sur l'orchestre sélectionné
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Informations")
        st.sidebar.markdown(f"**Orchestre**: {st.session_state.selected_orchestra['name']}")
        st.sidebar.markdown(f"**Type**: {st.session_state.selected_orchestra['type']}")
        st.sidebar.markdown("### Outils rapides")
        st.sidebar.button("Exporter les données")
        st.sidebar.button("Générer un rapport")

# Filtrage des orchestres (seulement sur la page d'accueil)
if st.session_state.page == "home":
    filtered_orchestras = orchestras
    if status_filter:
        filtered_orchestras = [o for o in filtered_orchestras if o["status"] in status_filter]
    if type_filter:
        filtered_orchestras = [o for o in filtered_orchestras if o["type"] in type_filter]
else:
    filtered_orchestras = []  # Pas besoin sur les autres pages

# Si nous sommes sur la page d'accueil, afficher le contenu normal
if st.session_state.page == "home":
    # Affichage du bouton "Créer un nouvel orchestre"
    col_btn = st.columns([3, 6, 3])
    with col_btn[1]:
        # Bouton explicite pour créer un nouvel orchestre
        create_btn = st.button("+ Créer un nouvel orchestre", key="create_orchestra_btn")
        if create_btn:
            st.session_state.page = "create_orchestra"
            st.rerun()

    st.markdown("---")

    # Affichage des orchestres en grille
    st.subheader(f"Vos orchestres ({len(filtered_orchestras)})")

    # Créer 3 colonnes pour afficher les orchestres
    cols = st.columns(3)

    # Distribuer les orchestres dans les colonnes
    for i, orchestra in enumerate(filtered_orchestras):
        with cols[i % 3]:
            # Définir la classe de statut
            status_class = ""
            if orchestra["status"] == "Actif":
                status_class = "status-active"
            elif orchestra["status"] == "En pause":
                status_class = "status-paused"
            elif orchestra["status"] == "Archivé":
                status_class = "status-archived"
            else:
                status_class = "status-prep"
            
            # Contenu de la carte avec un lien cliquable
            orchestra_id = i  # Utiliser l'index comme ID temporaire
            
            # Obtenir le nombre d'instruments et de projets pour affichage
            num_instruments = len(orchestra["instruments"])
            num_projects = len(orchestra["projects"])
            
            # Créer un conteneur avec style cliquable
            st.markdown(f"""
            <div class="orchestra-card" id="orchestra-{orchestra_id}">
                <div class="orchestra-title">{orchestra["name"]}</div>
                <div class="orchestra-type">Type: {orchestra["type"]}</div>
                <div class="orchestra-date">Créé le: {orchestra["date_created"]}</div>
                <span class="status-tag {status_class}">{orchestra["status"]}</span>
                <hr>
                <div style="margin-top: 10px; display: flex; justify-content: space-between;">
                    <div><strong>{num_instruments}</strong> instruments</div>
                    <div><strong>{num_projects}</strong> projets</div>
                </div>
                <div style="margin-top: 10px;">
                    {''.join([f'<span class="instrument-tag">{instrument["name"]}</span>' for instrument in orchestra["instruments"][:2]])}
                    {f'<span class="instrument-tag">+{num_instruments - 2} autres</span>' if num_instruments > 2 else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Bouton explicite pour cliquer sur l'orchestre - ce sera visible et fonctionnel
            if st.button(f"Voir les détails de {orchestra['name']}", key=f"btn_orchestra_{orchestra_id}"):
                st.session_state.selected_orchestra = orchestra
                st.session_state.page = "orchestra_detail"
                st.rerun()

# Afficher la suite uniquement sur la page d'accueil
if st.session_state.page == "home":
    # Afficher un message si aucun orchestre ne correspond aux filtres
    if not filtered_orchestras:
        st.info("Aucun orchestre ne correspond aux critères de filtre sélectionnés.")

    # Afficher la pagination (fictive pour le moment)
    if len(filtered_orchestras) > 0:
        st.markdown("---")
        cols_paginate = st.columns([4, 1, 1, 1, 1, 4])
        with cols_paginate[1]:
            st.markdown('<div style="text-align: center;">1</div>', unsafe_allow_html=True)
        with cols_paginate[2]:
            st.markdown('<div style="text-align: center; color: #888;">2</div>', unsafe_allow_html=True)
        with cols_paginate[3]:
            st.markdown('<div style="text-align: center; color: #888;">3</div>', unsafe_allow_html=True)
        with cols_paginate[4]:
            st.markdown('<div style="text-align: center; color: #888;">→</div>', unsafe_allow_html=True)