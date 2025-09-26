import tkinter as tk
from tkinter import filedialog, messagebox
from main import charger_fichier
from visual import visualiser
import json
import os


class SimpleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Choisir un fichier et nb_fourmis")
        self.geometry("400x200")

        # Variables que l'on va utiliser 
        self.file_path = ""       # ici sera stocké le chemin du fichier
        self.nb_fourmis = 0       # nombre de fourmis

        # Tkinter variable juste pour l'affichage du champ texte
        self.nb_fourmis_var = tk.StringVar(value="10")
        self.nb_fourmi_check = tk.BooleanVar(value=False)

        # Interface
        tk.Button(self, text="Choisir un fichier", command=self.select_file).pack(pady=10)
        checkbox = tk.Checkbutton(
            self,
            text="Choisir le nombre de fourmis",
            variable=self.nb_fourmi_check,        # relie la case à la variable
            onvalue=True,              # valeur quand cochée
            offvalue=False             # valeur quand décochée
        )
        checkbox.pack(pady=10)

        self.file_label = tk.Label(self, text="Aucun fichier sélectionné", fg="blue", wraplength=380)
        self.file_label.pack()


        frame = tk.Frame(self)
        frame.pack(pady=10)
        tk.Label(frame, text="nb_fourmis :").pack(side=tk.LEFT, padx=5)
        self.nb_entry = tk.Entry(frame, textvariable=self.nb_fourmis_var, width=10)
        self.nb_entry.pack(side=tk.LEFT)

        tk.Button(self, text="OK", command=self.on_ok).pack(pady=10)

    def select_file(self):
        """Ouvrir une boîte de dialogue pour choisir un fichier et stocker son chemin dans self.file_path"""
        path = filedialog.askopenfilename(title="Choisir un fichier")
        if path:
            self.file_path = path   
            
            self.file_label.config(text=path)

    def on_ok(self):
        """Valider et sauvegarder"""
        if not self.file_path:
            messagebox.showerror("Erreur", "Veuillez choisir un fichier.")
            return

        nb_text = self.nb_fourmis_var.get().strip()
        if not nb_text.isdigit():
            messagebox.showerror("Erreur", "nb_fourmis doit être un entier positif.")
            return
        self.nb_fourmis = int(nb_text)
        self.destroy()  # fermer la fenêtre
        try:
            fourmiliere = charger_fichier(self.file_path , self.nb_fourmis,self.nb_fourmi_check.get())
            logs = fourmiliere.simuler()
            visualiser(fourmiliere, logs)
            # print(f"Fichier chargé : {self.file_path}, nb_fourmis = {self.nb_fourmis}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier : {e}")
        app = SimpleApp()
        app.mainloop()

if __name__ == "__main__":
    app = SimpleApp()
    app.mainloop()
