from fourmi import Fourmiliere
import sys


def charger_fichier(path):
    """
    Charge une fourmilière depuis un fichier texte.
    """
    nb_fourmis = 0
    salles = []
    tunnels = []

    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # nombre de fourmis
            if line.startswith("f="):
                nb_fourmis = int(line.split("=")[1].strip())
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
    fourmiliere = Fourmiliere(nb_fourmis)
    for nom, cap in salles:
        fourmiliere.ajouter_salle(nom, cap)
    for s1, s2 in tunnels:
        fourmiliere.ajouter_tunnel(s1, s2)

    return fourmiliere


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <fichier_fourmiliere.txt>")
        sys.exit(1)

    path = sys.argv[1]
    fourmiliere = charger_fichier(path)


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