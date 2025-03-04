import os
import sys
import logging
import shutil
import requests
import zipfile
import io
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, Text
import threading
from datetime import datetime

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from settings import PATH_CONFIG

# Configuration des chemins
BASE_DIR = PATH_CONFIG['base']
DATA_DIR = PATH_CONFIG['data']
PROJETS_DIR = PATH_CONFIG['projets']
DOC_DIR = PATH_CONFIG['documentation']

# Assurer l'existence des dossiers
os.makedirs(PROJETS_DIR, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

# Sources de documentation enrichies
DOC_SOURCES = {
    "Développement Mobile": [
        {
            "name": "Flutter Official",
            "url": "https://github.com/flutter/flutter/archive/refs/heads/master.zip",
            "description": "Documentation et exemples officiels Flutter"
        },
        {
            "name": "Android Jetpack Compose",
            "url": "https://github.com/android/compose-samples/archive/refs/heads/main.zip",
            "description": "Exemples de UI modernes avec Jetpack Compose"
        }
    ],
    "Architecture Logicielle": [
        {
            "name": "Clean Architecture Android",
            "url": "https://github.com/android/architecture-samples/archive/refs/heads/main.zip",
            "description": "Exemples d'architecture Android moderne"
        }
    ]
}

class DocumentLoaderUI:
    def __init__(self, master):
        self.master = master
        master.title("Gestionnaire de Documents RAG")
        master.geometry("1400x900")

        # Configuration du style
        style = ttk.Style()
        style.theme_use('clam')  # Thème moderne

        # Frame principal
        self.main_frame = tk.Frame(master, bg='white')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Création d'un layout avec deux colonnes
        self.left_frame = tk.Frame(self.main_frame, width=350, bg='#f0f0f0')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        self.left_frame.pack_propagate(False)

        self.right_frame = tk.Frame(self.main_frame, bg='white')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Arbre des dossiers
        self.create_directory_tree()

        # Onglets pour différentes vues
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Onglets
        self.create_project_view()
        self.create_documentation_view()
        self.create_download_view()

    def populate_projects_list(self):
        """Peuple la liste des projets"""
        # Vider la liste existante
        for i in self.projects_list.get_children():
            self.projects_list.delete(i)

        # Vérifier que le dossier existe
        if not os.path.exists(PROJETS_DIR):
            os.makedirs(PROJETS_DIR)
            return

        # Parcourir les dossiers de projets
        for project in os.listdir(PROJETS_DIR):
            project_path = os.path.join(PROJETS_DIR, project)
            if os.path.isdir(project_path):
                # Compter les fichiers
                file_count = sum([len(files) for r, d, files in os.walk(project_path)])
                
                # Dernière modification
                try:
                    last_modified = os.path.getmtime(project_path)
                    last_modified_str = datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    last_modified_str = "Date inconnue"

                self.projects_list.insert('', 'end', values=(
                    project, 
                    project_path, 
                    file_count, 
                    last_modified_str
                ))

    def populate_documentation_list(self):
        """Peuple la liste de documentation"""
        # Vider la liste existante
        for i in self.doc_list.get_children():
            self.doc_list.delete(i)

        # Vérifier que le dossier existe
        if not os.path.exists(DOC_DIR):
            os.makedirs(DOC_DIR)
            return

        # Parcourir les dossiers de documentation
        for doc in os.listdir(DOC_DIR):
            doc_path = os.path.join(DOC_DIR, doc)
            if os.path.isdir(doc_path):
                # Compter les fichiers
                file_count = sum([len(files) for r, d, files in os.walk(doc_path)])
                
                # Dernière modification
                try:
                    last_modified = os.path.getmtime(doc_path)
                    last_modified_str = datetime.fromtimestamp(last_modified).strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    last_modified_str = "Date inconnue"

                self.doc_list.insert('', 'end', values=(
                    doc, 
                    doc_path, 
                    file_count, 
                    last_modified_str
                ))

    def create_project_view(self):
        """Crée l'onglet de vue des projets"""
        projects_frame = tk.Frame(self.notebook)
        self.notebook.add(projects_frame, text="Projets Existants")

        # Frame pour les boutons
        btn_frame = tk.Frame(projects_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Bouton d'ajout de projet
        add_project_btn = tk.Button(btn_frame, text="Ajouter un projet", command=self.add_project)
        add_project_btn.pack(side=tk.LEFT, padx=5)

        # Liste des projets
        self.projects_list = ttk.Treeview(projects_frame, 
                                          columns=('name', 'path', 'files', 'last_modified'), 
                                          show='headings')
        self.projects_list.heading('name', text='Nom')
        self.projects_list.heading('path', text='Chemin')
        self.projects_list.heading('files', text='Fichiers')
        self.projects_list.heading('last_modified', text='Dernière modification')
        self.projects_list.pack(fill=tk.BOTH, expand=True)

        # Double-clic pour ouvrir le projet
        self.projects_list.bind('<Double-1>', self.open_project)

        # Peupler la liste des projets
        self.populate_projects_list()

    def create_documentation_view(self):
        """Crée l'onglet de vue des documentations"""
        doc_frame = tk.Frame(self.notebook)
        self.notebook.add(doc_frame, text="Documentation")

        # Frame pour les boutons
        btn_frame = tk.Frame(doc_frame)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        # Bouton d'ajout de documentation
        add_doc_btn = tk.Button(btn_frame, text="Ajouter de la documentation", command=self.add_documentation)
        add_doc_btn.pack(side=tk.LEFT, padx=5)

        # Liste des documentations
        self.doc_list = ttk.Treeview(doc_frame, 
                                     columns=('name', 'path', 'files', 'last_modified'), 
                                     show='headings')
        self.doc_list.heading('name', text='Nom')
        self.doc_list.heading('path', text='Chemin')
        self.doc_list.heading('files', text='Fichiers')
        self.doc_list.heading('last_modified', text='Dernière modification')
        self.doc_list.pack(fill=tk.BOTH, expand=True)

        # Double-clic pour ouvrir la documentation
        self.doc_list.bind('<Double-1>', self.open_documentation)

        # Peupler la liste de documentation
        self.populate_documentation_list()

    def add_project(self):
        """Ajoute un nouveau projet depuis un dossier existant"""
        project_path = filedialog.askdirectory(title="Sélectionnez un dossier de projet")
        if project_path:
            # Copier le projet dans le dossier de projets
            project_name = os.path.basename(project_path)
            dest_path = os.path.join(PROJETS_DIR, project_name)
            
            # Demander confirmation si le projet existe déjà
            if os.path.exists(dest_path):
                response = messagebox.askyesno("Projet existant", 
                                               f"Le projet {project_name} existe déjà. Voulez-vous le remplacer ?")
                if not response:
                    return
            
            # Copier le projet
            try:
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(project_path, dest_path)
                
                # Rafraîchir la liste des projets
                self.populate_projects_list()
                messagebox.showinfo("Succès", f"Projet {project_name} ajouté avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ajouter le projet : {str(e)}")

    def add_documentation(self):
        """Ajoute une nouvelle documentation depuis un dossier existant"""
        doc_path = filedialog.askdirectory(title="Sélectionnez un dossier de documentation")
        if doc_path:
            # Copier la documentation dans le dossier de documentation
            doc_name = os.path.basename(doc_path)
            dest_path = os.path.join(DOC_DIR, doc_name)
            
            # Demander confirmation si la documentation existe déjà
            if os.path.exists(dest_path):
                response = messagebox.askyesno("Documentation existante", 
                                               f"La documentation {doc_name} existe déjà. Voulez-vous la remplacer ?")
                if not response:
                    return
            
            # Copier la documentation
            try:
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(doc_path, dest_path)
                
                # Rafraîchir la liste des documentations
                self.populate_documentation_list()
                messagebox.showinfo("Succès", f"Documentation {doc_name} ajoutée avec succès")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ajouter la documentation : {str(e)}")

    def open_project(self, event):
        """Ouvre le projet sélectionné dans l'explorateur de fichiers"""
        selected_item = self.projects_list.selection()
        if selected_item:
            project_path = self.projects_list.item(selected_item)['values'][1]
            os.startfile(project_path)

    def open_documentation(self, event):
        """Ouvre la documentation sélectionnée dans l'explorateur de fichiers"""
        selected_item = self.doc_list.selection()
        if selected_item:
            doc_path = self.doc_list.item(selected_item)['values'][1]
            os.startfile(doc_path)

    def create_directory_tree(self):
        """Crée un arbre de répertoires style explorateur"""
        tree_frame = tk.Frame(self.left_frame, bg='#f0f0f0')
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Tree View
        self.directory_tree = ttk.Treeview(tree_frame, 
                                           yscrollcommand=tree_scroll.set, 
                                           selectmode='browse')
        self.directory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.config(command=self.directory_tree.yview)

        # Configuration des colonnes
        self.directory_tree['columns'] = ('fullpath', 'type', 'size')
        self.directory_tree.column('#0', width=200, stretch=tk.NO)
        self.directory_tree.column('fullpath', width=0, stretch=tk.NO)
        self.directory_tree.column('type', width=100, anchor='center')
        self.directory_tree.column('size', width=100, anchor='e')

        self.directory_tree.heading('#0', text='Répertoires')
        self.directory_tree.heading('fullpath', text='Chemin complet')
        self.directory_tree.heading('type', text='Type')
        self.directory_tree.heading('size', text='Taille')

        # Peupler l'arbre
        self.populate_directory_tree(BASE_DIR)

    def populate_directory_tree(self, path, parent=''):
        """Peuple l'arbre de répertoires"""
        try:
            # Ajouter le dossier racine
            if not parent:
                root_node = self.directory_tree.insert('', 'end', text=os.path.basename(path), 
                                                       values=(path, 'Dossier', ''))
                parent = root_node
            
            # Parcourir les sous-répertoires et fichiers
            for item in sorted(os.listdir(path)):
                full_path = os.path.join(path, item)
                
                # Ignorer certains dossiers
                if item in ['.git', '__pycache__', 'node_modules', 'build', 'dist', '.venv', 'venv']:
                    continue
                
                if os.path.isdir(full_path):
                    # Ajouter les dossiers
                    folder_node = self.directory_tree.insert(parent, 'end', text=item, 
                                                             values=(full_path, 'Dossier', ''))
                    # Récursivité pour les sous-dossiers
                    self.populate_directory_tree(full_path, folder_node)
                else:
                    # Ajouter les fichiers
                    try:
                        file_size = os.path.getsize(full_path)
                        self.directory_tree.insert(parent, 'end', text=item, 
                                                   values=(full_path,os.path.splitext(item)[1], 
                                                           f'{file_size/1024:.2f} Ko'))
                    except Exception:
                        # Ignorer les fichiers inaccessibles
                        pass
        except Exception as e:
            print(f"Erreur lors du parcours : {e}")

    def create_download_view(self):
        """Crée l'onglet de téléchargement de documentation"""
        download_frame = tk.Frame(self.notebook)
        self.notebook.add(download_frame, text="Télécharger Documentation")

        # Créer des frames pour chaque catégorie
        categories_frame = tk.Frame(download_frame)
        categories_frame.pack(fill=tk.X, padx=10, pady=10)

        # Variables pour suivre les sélections
        self.doc_selections = {}

        # Créer des checkboxes par catégorie
        for category, sources in DOC_SOURCES.items():
            # Frame pour la catégorie
            cat_frame = tk.LabelFrame(categories_frame, text=category, padx=5, pady=5)
            cat_frame.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.Y)

            # Variables de sélection pour cette catégorie
            self.doc_selections[category] = {}

            for source in sources:
                var = tk.BooleanVar(value=False)
                self.doc_selections[category][source['name']] = var
                
                chk = tk.Checkbutton(cat_frame, 
                                     text=source['name'], 
                                     variable=var, 
                                     wraplength=200, 
                                     justify=tk.LEFT)
                chk.pack(anchor=tk.W)

        # Bouton de téléchargement
        download_btn = tk.Button(download_frame, 
                                 text="Télécharger la documentation sélectionnée", 
                                 command=self.download_selected_docs)
        download_btn.pack(pady=10)

        # Zone de log
        self.log_text = Text(download_frame, height=10, width=100)
        self.log_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def download_selected_docs(self):
        """Télécharge les documentations sélectionnées"""
        def download_thread():
            self.log_text.delete('1.0', tk.END)
            os.makedirs(DOC_DIR, exist_ok=True)

            for category, sources in DOC_SOURCES.items():
                for source in sources:
                    name = source['name']
                    # Vérifier si la source est sélectionnée
                    if self.doc_selections[category][name].get():
                        try:
                            self.log_text.insert(tk.END, f"Téléchargement de {name}...\n")
                            self.master.update()

                            # Télécharger le zip
                            response = requests.get(source['url'])
                            response.raise_for_status()

                            # Extraire le zip
                            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                                # Créer un dossier pour la source
                                extract_path = os.path.join(DOC_DIR, name.lower().replace(" ", "_"))
                                os.makedirs(extract_path, exist_ok=True)
                                
                                # Extraire les fichiers de code source
                                for file in z.namelist():
                                    if (file.endswith('.dart') or 
                                        file.endswith('.java') or 
                                        file.endswith('.kt') or 
                                        file.endswith('.md') or
                                        file.endswith('.xml') or
                                        file.endswith('.json')):
                                        try:
                                            # Extraire en préservant la structure
                                            full_path = os.path.join(extract_path, file)
                                            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                                            with z.open(file) as source_file, open(full_path, 'wb') as target_file:
                                                shutil.copyfileobj(source_file, target_file)
                                        except Exception as extract_err:
                                            self.log_text.insert(tk.END, f"Erreur d'extraction: {extract_err}\n")

                            self.log_text.insert(tk.END, f"{name} téléchargé avec succès\n")
                            
                            # Mettre à jour la vue de documentation
                            self.master.after(0, self.populate_documentation_list)
                        
                        except Exception as e:
                            self.log_text.insert(tk.END, f"Erreur de téléchargement pour {name}: {str(e)}\n")

            self.log_text.insert(tk.END, "Téléchargement terminé.")

        # Lancer le téléchargement dans un thread séparé
        threading.Thread(target=download_thread, daemon=True).start()

def main():
    root = tk.Tk()
    
    # Configuration de la fenêtre
    root.title("Gestionnaire de Documents RAG")
    
    # Taille et position
    window_width = 1400
    window_height = 900
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    # Style moderne
    style = ttk.Style()
    style.theme_use('clam')  # Ou 'alt', 'default', selon votre préférence
    
    app = DocumentLoaderUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()