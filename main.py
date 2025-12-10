import hashlib, time
from datetime import datetime
import random
import json

# ------------------------------------------------------------
#  CLASS BLOCK
# ------------------------------------------------------------
class Block:
    def __init__(self, index, data, previous_hash):
        # index du bloc dans la chaîne (position dans la blockchain)
        self.index = index
        
        # timestamp = moment exact de la création du bloc
        # Ce timestamp participe au hash → donc impossible de reproduire le bloc
        self.timestamp = time.time()
        
        # data = contenu du bloc
        # Ici : texte, logs, transactions, etc.
        self.data = data
        
        # previous_hash = hash du bloc précédent
        # C'est le CHAÎNAGE CRYPTOGRAPHIQUE
        self.previous_hash = previous_hash
        
        # hash du bloc ACTUEL
        # calculé automatiquement à la création
        self.hash = self.calc_hash()
        
    def calc_hash(self):
        """
        Le hash du bloc est calculé à partir de :
        - index
        - timestamp
        - data
        - previous_hash
        
        Ce mélange rend le bloc IMMUTABLE :
        → si tu changes UNE lettre de data, le hash change complètement
        → et donc toute la blockchain devient invalide
        """
        contenue = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        
        # SHA-256 : fonction de hachage cryptographique
        return hashlib.sha256(contenue.encode()).hexdigest()


# ------------------------------------------------------------
#  CLASS BLOCKCHAIN
# ------------------------------------------------------------
class Blockchain:
    def __init__(self):
        # La blockchain est une LISTE ordonnée de blocs
        # Elle commence toujours par un bloc Genesis
        self.chain = [self.genesis()]
    
    def genesis(self):
        """
        Le premier bloc de l'histoire :
        - index = 0
        - data = "Genesis"
        - previous_hash = "0" car personne avant lui
        """
        return Block(0, "Genesis", "0")
    
    def add_block(self, data):
        """
        Ajoute un NOUVEAU bloc dans la blockchain :
        Etapes :
        1. On récupère le DERNIER bloc de la chaîne
        2. On crée un bloc avec :
           - index = taille de la chaîne
           - previous_hash = hash du dernier bloc
        3. On ajoute le bloc à la liste
        """
        prev = self.chain[-1]  # bloc précédent
        
        # nouveau bloc avec previous_hash = HASH du bloc précédent
        new = Block(len(self.chain), data, prev.hash)
        
        # on ajoute ce bloc dans la chaîne
        self.chain.append(new)
    
    def verify(self):
        """
        Vérifie l'intégrité TOTALE de la blockchain.
        
        Pour CHAQUE bloc à partir du 2e :
        - Vérifie que previous_hash == hash du bloc précédent
        - Recacule le hash et compare avec celui enregistré
        
        Si tout est bon → blockchain valide.
        """
        
        # Cas trivial : seulement Genesis → forcément valide
        if len(self.chain) == 1:
            print("Blockchain valide (un seul bloc)")
            return True

        # On commence à 1 car le bloc 0 n'a pas de précédent
        for i in range(1, len(self.chain)):
            cur = self.chain[i]    # bloc courant
            old = self.chain[i-1]  # bloc précédent
            
            # Vérification du chaînage : le maillon doit pointer vers le bon hash
            if cur.previous_hash != old.hash:
                print(f"❌ Rupture du chaînage au bloc {i}")
                return False
            
            # Vérification du hash interne (intégrité du bloc)
            recalculated = cur.calc_hash()
            if recalculated != cur.hash:
                print(f"❌ Données modifiées dans le bloc {i}")
                print(f"Hash enregistré :   {cur.hash}")
                print(f"Hash recalculé :    {recalculated}")
                return False
        
        print("✅ Blockchain valide")
        return True


# ------------------------------------------------------------
#  PROGRAMME PRINCIPAL
# ------------------------------------------------------------
if __name__ == "__main__":

    json_file = "transactions.json"
    bc = Blockchain()  # création de la blockchain
    
    # ⚠️ ATTENTION ⚠️
    # Ce code écrase ton fichier JSON et ne met QUE le Genesis dedans.
    # Je le laisse car tu veux comprendre, mais normalement tu le supprimes.
    with open(json_file,"w") as f:
        transactions = {
            "index": bc.chain[0].index,
            "timestamp": bc.chain[0].timestamp,
            "data": bc.chain[0].data,
            "previous_hash": bc.chain[0].previous_hash,
            "hash": bc.chain[0].hash
        }
        json.dump(transactions, f, indent=4)

    # Vérification simple de la blockchain actuelle
    bc.verify()


# ------------------------------------------------------------
# UTILITAIRES : LOAD / SAVE / LOG
# ------------------------------------------------------------

# identifiant unique pour logs (juste pour éviter collisions)
now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + random.choice(["A","B","C","D","E","F"])

def load_chain_from_json(filename):
    """
    Permet de reconstruire toute la blockchain
    à partir d'un fichier JSON.
    
    On recrée chaque bloc → même index, même data, même timestamp
    """
    bc = Blockchain()
    bc.chain = []  # on vide la blockchain actuelle
    
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)  # liste de dicts
    
    for d in data:
        # reconstitution d'un bloc
        block = Block(
            index=d["index"],
            data=d["data"],
            previous_hash=d["previous_hash"]
        )
        
        # On remet les valeurs EXACTES du fichier
        block.timestamp = d["timestamp"]
        block.hash = d["hash"]
        
        bc.chain.append(block)
    
    return bc


def save_chain_to_json(blockchain, filename):
    """
    Sauvegarde de toute la blockchain dans un fichier JSON.
    """
    data = []
    
    for b in blockchain.chain:
        block_data = {
            "index": b.index,
            "timestamp": b.timestamp,
            "data": b.data,
            "previous_hash": b.previous_hash,
            "hash": b.hash
        }
        data.append(block_data)
    
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def create_log_file():
    """
    1. Crée un petit fichier log
    2. Lit son contenu
    3. Ajoute un bloc dans la blockchain avec ces données
    """
    
    # nom du fichier log
    filename = f"log_{now}" + str(random.randint(1,3)) + ".txt"
    
    # on écrit le log (1 ligne)
    with open(filename, "w") as file:
        file.write("Log file created at " + now + "\n")
    
    # on relit le contenu → devient DATA du bloc
    with open(filename, "r", encoding="utf-8") as file:
        contenue = file.readlines()
        
        # chaque log crée un NOUVEAU bloc
        bc.add_block(contenue)



# ------------------------------------------------------------
# TESTS : AJOUT DE LOGS → SAUVEGARDE → RECHARGEMENT → VERIF
# ------------------------------------------------------------

# 2 logs = 2 blocs ajoutés
create_log_file()
time.sleep(5)
create_log_file()

# Sauvegarde JSON
save_chain_to_json(bc, json_file)

# Rechargement depuis le JSON
bc2 = load_chain_from_json(json_file)

# Vérification d'intégrité
bc2.verify()
