# Schémas des différents états de la BD

Les attributs soulignés sont les clés primaires.

Les clés étrangères sont indiquées sous les tables. Soit une table **X** dont l'attribut **a** est une clé étrangère vers l'attribut **b** de la table **Y**:
a -> Y.b

## État initial

### Universite

| **<ins>uid</ins>**: int | **nom**: varchar(50) |
| --- | --- |


### Cours

| **<ins>cid</ins>**: int | **sigle**: varchar(8) | **uid**: int |
| --- | --- | --- |

uid -> Universite.uid

...
