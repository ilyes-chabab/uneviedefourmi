from fourmi import Fourmiliere
import sys

FILE="four\\fourmiliere_quatre.txt"

def charger_fichier(path ,nb_fourmis,nb_fourmi_boolean):
    """
    Charge une fourmilière depuis un fichier texte.
    """
    
    salles = []
    tunnels = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # nombre de fourmis
            if line.startswith("f="):
                nb_fourmis_f = int(line.split("=")[1].strip())
                continue

            # tunnel
            if "-" in line:
                s1, s2 = [x.strip() for x in line.split("-")]
                tunnels.append((s1, s2))
                continue

            # salle
            if "{" in line:
                nom, cap = line.split("{")
                nom = nom.strip()
                cap = int(cap.strip(" }"))
                salles.append((nom, cap))
            else:
                salles.append((line, 1))

    # construction de la fourmilière
    if nb_fourmi_boolean :
        fourmiliere = Fourmiliere(nb_fourmis)
    else :
        fourmiliere = Fourmiliere(nb_fourmis_f)
    for nom, cap in salles:
        fourmiliere.ajouter_salle(nom, cap)
    for s1, s2 in tunnels:
        fourmiliere.ajouter_tunnel(s1, s2)

    return fourmiliere


if __name__ == "__main__":

    nb_fourmis = 10
    path = FILE
    fourmiliere = charger_fichier(path, nb_fourmis)


    print(f"=== Simulation pour {path} ===")
    logs = fourmiliere.simuler()
    for l in logs:
        print(l)

    """
    print("\nSalles :")
    for nom, salle in fourmiliere.salles.items():
        print(f"  {salle}")

    print("\nTunnels :")
    for s1, voisins in fourmiliere.tunnels.items():
        print(f"  {s1} -> {voisins}")

    print("\nFourmis :")
    for f in fourmiliere.fourmis:
        print(f)
    """