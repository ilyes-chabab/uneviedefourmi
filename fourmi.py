# ants.py
from collections import deque, defaultdict
import networkx as nx
import itertools

class Fourmi:
    """
    Représente une fourmi individuelle.
    """
    def __init__(self, id_, emplacement="Sv"):
        self.id = id_                  # Identifiant unique
        self.emplacement = emplacement # Salle actuelle (nom de salle)
        self.historique = []           # Historique des déplacements (utile pour log)
        # attributs de simulation (initialisés dans Fourmiliere.simuler)
        self.chemin = None
        self.index = None

    def deplacer(self, nouvelle_salle):
        """
        Déplace la fourmi vers une nouvelle salle.
        """
        self.historique.append((self.emplacement, nouvelle_salle))
        self.emplacement = nouvelle_salle

    def __repr__(self):
        return f"Fourmi({self.id}, dans={self.emplacement})"


class Salle:
    """
    Représente une salle de la fourmilière.
    """
    def __init__(self, nom, capacite=1):
        self.nom = nom
        self.capacite = capacite       # Nombre max de fourmis (float('inf') pour Sv et Sd)
        self.file = deque()            # File FIFO de fourmis présentes

    def est_libre(self):
        """
        Vérifie si la salle peut accueillir une nouvelle fourmi.
        """
        if self.capacite == float("inf"):
            return True
        return len(self.file) < self.capacite

    def ajouter_fourmi(self, fourmi):
        """
        Place une fourmi dans la salle si la capacité le permet.
        Retourne True si ok, False sinon.
        """
        if self.est_libre():
            self.file.append(fourmi)
            return True
        return False

    def retirer_fourmi(self, fourmi):
        """
        Retire une fourmi de la salle.
        """
        try:
            self.file.remove(fourmi)
            return True
        except ValueError:
            return False

    def __repr__(self):
        cap = "inf" if self.capacite == float("inf") else str(self.capacite)
        return f"Salle({self.nom}, cap={cap}, occ={len(self.file)})"


class Fourmiliere:
    """
    Représente la fourmilière entière sous forme de graphe.
    """
    def __init__(self, nb_fourmis=0):
        self.nb_fourmis = nb_fourmis
        self.salles = {}              # {nom: Salle}
        self.tunnels = defaultdict(list)  # Graphe d’adjacence

        # Création du vestibule et du dortoir
        self.salles["Sv"] = Salle("Sv", capacite=float("inf"))
        self.salles["Sd"] = Salle("Sd", capacite=float("inf"))

        # Création des fourmis
        self.fourmis = [Fourmi(i + 1, "Sv") for i in range(nb_fourmis)]
        for f in self.fourmis:
            self.salles["Sv"].ajouter_fourmi(f)

    def ajouter_salle(self, nom, capacite=1):
        """
        Ajoute une salle dans la fourmilière.
        """
        if nom not in self.salles:
            self.salles[nom] = Salle(nom, capacite)

    def ajouter_tunnel(self, s1, s2):
        """
        Ajoute une connexion bidirectionnelle entre deux salles.
        """
        self.tunnels[s1].append(s2)
        self.tunnels[s2].append(s1)

    def voisins(self, salle_nom):
        """
        Retourne les voisins accessibles d’une salle.
        """
        return self.tunnels[salle_nom]

    def toutes_au_dortoir(self):
        """
        Vérifie si toutes les fourmis sont arrivées dans Sd.
        """
        return all(f.emplacement == "Sd" for f in self.fourmis)

    def construire_graphe(self):
        """
        Construit un graphe NetworkX à partir des tunnels.
        """
        G = nx.Graph()
        for s1, voisins in self.tunnels.items():
            for s2 in voisins:
                G.add_edge(s1, s2)
        return G

    def chemins_vers_dortoir(self):
        """
        Retourne tous les plus courts chemins Sv -> Sd (liste de listes de salles).
        """
        G = self.construire_graphe()
        return list(nx.all_shortest_paths(G, source="Sv", target="Sd"))

    def simuler(self):
        """
        Simule le déplacement de toutes les fourmis vers Sd en dispatchant sur plusieurs chemins.
        Retourne la liste des logs d'étapes.
        """
        tous_chemins = self.chemins_vers_dortoir()
        if not tous_chemins:
            raise RuntimeError("Aucun chemin Sv -> Sd trouvé!")

        logs = []
        etape = 1

        # Dispatcher les fourmis sur les chemins disponibles (round-robin)
        cycle_chemins = itertools.cycle(tous_chemins)
        for f in self.fourmis:
            f.chemin = list(next(cycle_chemins))
            f.index = 0  # position dans le chemin

        # Boucle de simulation
        while not self.toutes_au_dortoir():
            # Calculer occupation actuelle et places disponibles
            occ = {nom: len(s.file) for nom, s in self.salles.items()}
            available = {}
            for nom, s in self.salles.items():
                if s.capacite == float("inf"):
                    available[nom] = float("inf")
                else:
                    available[nom] = s.capacite - occ[nom]

            # Construire liste de candidats (ant, prochaine salle, distance restante)
            candidats = []
            for f in self.fourmis:
                if f.emplacement == "Sd":
                    continue
                # sécurité : si chemin mal initialisé
                if f.chemin is None or f.index is None or f.index + 1 >= len(f.chemin):
                    continue
                prochaine = f.chemin[f.index + 1]
                remaining = (len(f.chemin) - 1) - f.index  # nb d'étapes restantes pour Sd
                candidats.append((remaining, f.id, f, prochaine))

            # Prioriser les fourmis les plus proches du dortoir (remaining ASC)
            candidats.sort(key=lambda x: (x[0], x[1]))

            # Planifier les mouvements en respectant les capacités via réservation
            mouvements_planifies = []
            for remaining, _, f, prochaine in candidats:
                # si la cible a au moins une place réservable on planifie
                if available[prochaine] > 0:
                    mouvements_planifies.append((f, f.emplacement, prochaine))
                    # mise à jour des places disponibles :
                    # départ sera libéré => on augmente available[depart] (sauf Sv inf)
                    if available[f.emplacement] != float("inf"):
                        available[f.emplacement] += 1
                    # arrivée consomme une place
                    if available[prochaine] != float("inf"):
                        available[prochaine] -= 1
                # sinon on ne planifie pas cette fourmi ce tour-ci

            # Exécution des mouvements planifiés (simultanés)
            if not mouvements_planifies:
                # Aucun mouvement possible mais pas encore toutes au dortoir => deadlock
                # Dans des cas normaux bien formés ce ne doit pas arriver.
                raise RuntimeError(
                    "Deadlock détecté : aucune fourmi ne peut se déplacer cette étape. "
                    "Vérifie la topologie / capacités. Si tu veux, envoie-moi le fichier pour debug."
                )

            # retirer d'abord (pour simuler simultané)
            for f, depart, arrivee in mouvements_planifies:
                self.salles[depart].retirer_fourmi(f)
            # puis ajouter / mettre à jour les fourmis
            for f, depart, arrivee in mouvements_planifies:
                ok = self.salles[arrivee].ajouter_fourmi(f)
                if not ok:
                    # Cela ne devrait pas arriver grâce à la réservation, mais on le gère proprement
                    raise RuntimeError(f"Erreur: impossible d'ajouter f{f.id} dans {arrivee} malgré la réservation.")
                f.deplacer(arrivee)
                f.index += 1

            # log de l'étape
            log = [f"+++ E{etape} +++"]
            for f, dep, arr in mouvements_planifies:
                log.append(f"f{f.id} - {dep} - {arr}")
            logs.append("\n".join(log))
            etape += 1

        return logs

    def __repr__(self):
        return f"Fourmiliere({len(self.salles)} salles, {len(self.fourmis)} fourmis)"
