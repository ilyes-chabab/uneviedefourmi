# ants.py
from collections import deque, defaultdict
import networkx as nx
import itertools

class Fourmi:
    """
    Représente une fourmi individuelle.
    """
    def __init__(self, id_, emplacement="Sv"):
        self.id = id_                  
        self.emplacement = emplacement 
        self.historique = []           
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
        self.capacite = capacite     
        self.file = deque()   

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
        self.salles = {}
        self.tunnels = defaultdict(list)

        self.salles["Sv"] = Salle("Sv", capacite=float("inf"))
        self.salles["Sd"] = Salle("Sd", capacite=float("inf"))

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


    def simuler(self):
        """
        Simule le déplacement de toutes les fourmis vers Sd en dispatchant sur plusieurs chemins.
        Retourne la liste des logs d'étapes.
        Cette version tente de recalculer un chemin alternatif (parmi les plus courts)
        pour une fourmi si sa prochaine salle prévue est indisponible.
        """
        # construit le graphe NetworkX une seule fois (il ne change pas pendant la sim)
        G = self.construire_graphe()
        # vérif basique
        if not nx.has_path(G, "Sv", "Sd"):
            raise RuntimeError("Aucun chemin Sv -> Sd trouvé!")

        logs = []
        etape = 1

        # Dispatcher les fourmis sur les chemins disponibles (round-robin) — optionnel ici
        tous_chemins = list(nx.all_shortest_paths(G, source="Sv", target="Sd"))
        if not tous_chemins:
            raise RuntimeError("Aucun chemin Sv -> Sd trouvé!")
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
                # sécurité : si chemin mal initialisé ou si on est déjà au bout
                if f.chemin is None or f.index is None or f.index + 1 >= len(f.chemin):
                    # tenter de (re)calculer un plus court chemin depuis la position courante
                    try:
                        # récupérer un chemin le plus court
                        p = next(nx.all_shortest_paths(G, source=f.emplacement, target="Sd"))
                        f.chemin = list(p)
                        f.index = 0
                    except (nx.NetworkXNoPath, StopIteration):
                        continue
                prochaine = f.chemin[f.index + 1]
                remaining = (len(f.chemin) - 1) - f.index  # nb d'étapes restantes pour Sd
                candidats.append((remaining, f.id, f, prochaine))

            # Prioriser les fourmis les plus proches du dortoir (remaining ASC)
            candidats.sort(key=lambda x: (x[0], x[1]))

            # Planifier les mouvements en respectant les capacités via réservation
            mouvements_planifies = []
            for remaining, _, f, prochaine in candidats:
                # Si la cible prévue est disponible on garde la planification
                if available.get(prochaine, 0) > 0:
                    mouvements_planifies.append((f, f.emplacement, prochaine))
                    # libère la place au départ (sauf Sv inf)
                    if available[f.emplacement] != float("inf"):
                        available[f.emplacement] += 1
                    # consomme la place arrivée
                    if available[prochaine] != float("inf"):
                        available[prochaine] -= 1
                    continue

                # sinon : essayer de trouver un autre chemin le plus court depuis la position courante
                # dont le premier saut est disponible (évite d'attendre s'il y a une alternative)
                trouve_alt = False
                try:
                    for path in nx.all_shortest_paths(G, source=f.emplacement, target="Sd"):
                        if len(path) < 2:
                            continue
                        alt_next = path[1]
                        if available.get(alt_next, 0) > 0:
                            # on adopte ce chemin alternatif pour cette fourmi
                            f.chemin = list(path)
                            f.index = 0
                            mouvements_planifies.append((f, f.emplacement, alt_next))
                            # mise à jour des disponibilités comme plus haut
                            if available[f.emplacement] != float("inf"):
                                available[f.emplacement] += 1
                            if available[alt_next] != float("inf"):
                                available[alt_next] -= 1
                            trouve_alt = True
                            break
                except nx.NetworkXNoPath:
                    pass

                # si pas d'alternative trouvée, on ne planifie pas cette fourmi ce tour-ci

            # Exécution des mouvements planifiés (simultanés)
            if not mouvements_planifies:
                # Aucun mouvement possible mais pas encore toutes au dortoir => deadlock
                raise RuntimeError(
                    "Deadlock détecté : aucune fourmi ne peut se déplacer cette étape. "
                    "Vérifie la topologie / capacités."
                )

            # retirer d'abord (pour simuler simultané)
            for f, depart, arrivee in mouvements_planifies:
                self.salles[depart].retirer_fourmi(f)
            # puis ajouter / mettre à jour les fourmis
            for f, depart, arrivee in mouvements_planifies:
                ok = self.salles[arrivee].ajouter_fourmi(f)
                if not ok:
                    raise RuntimeError(f"Erreur: impossible d'ajouter f{f.id} dans {arrivee} malgré la réservation.")
                f.deplacer(arrivee)
                # avancer l'index dans le chemin courant : on suppose que f.chemin[0] == f.emplacement
                # trouver où on se situe dans le chemin (pour gérer chemins alternatifs adoptés)
                # le plus simple : remettre index à l'indice correspondant au nouvel emplacement
                try:
                    f.index = f.chemin.index(arrivee)
                except ValueError:
                    # cas improbable : on est arrivé dans une salle qui n'est pas dans le chemin => reset
                    f.index = 0

            # log de l'étape
            log = [f"+++ E{etape} +++"]
            for f, dep, arr in mouvements_planifies:
                log.append(f"f{f.id} - {dep} - {arr}")
            logs.append("\n".join(log))
            etape += 1

        return logs

    def __repr__(self):
        return f"Fourmiliere({len(self.salles)} salles, {len(self.fourmis)} fourmis)"
