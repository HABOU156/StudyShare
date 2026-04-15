from app.repositories import collection_repository


def creer_collection(eid, nom):
    if not nom or not nom.strip():
        return None, "Le nom de la collection est requis."
    if len(nom.strip()) > 100:
        return None, "Le nom ne doit pas dépasser 100 caractères."
    col_id = collection_repository.creer_collection(eid, nom.strip())
    if col_id:
        return col_id, "Collection créée avec succès."
    return None, "Erreur lors de la création de la collection."


def lister_collections(eid):
    return collection_repository.lister_collections(eid)


def obtenir_collection(col_id, eid):
    col = collection_repository.get_collection(col_id, eid)
    if not col:
        return None, "Collection introuvable ou accès refusé."
    return col, "Succès."


def ajouter_fichier(col_id, fid, eid):
    return collection_repository.ajouter_fichier(col_id, fid, eid)
