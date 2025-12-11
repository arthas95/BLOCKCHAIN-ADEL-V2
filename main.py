import hashlib
import time
from datetime import datetime
import random
import json
import os


# ------------------------------------------------------------
#  CLASS BLOCK
# ------------------------------------------------------------
class Block:
    def __init__(self, index, data, previous_hash, timestamp=None, given_hash=None):
        # position dans la blockchain
        self.index = index

        # timestamp du bloc
        if timestamp is None:
            self.timestamp = time.time()
        else:
            self.timestamp = timestamp

        # contenu du bloc (ici : hash du fichier log)
        self.data = data

        # hash du bloc précédent (chaînage)
        self.previous_hash = previous_hash

        # hash du bloc actuel
        if given_hash is None:
            self.hash = self.calc_hash()
        else:
            self.hash = given_hash

    def calc_hash(self):
        contenue = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(contenue.encode()).hexdigest()


# ------------------------------------------------------------
#  CLASS BLOCKCHAIN
# ------------------------------------------------------------
class Blockchain:
    def __init__(self):
        # toujours commencer par le bloc Genesis
        self.chain = [self.genesis()]

    def genesis(self):
        return Block(0, "Genesis", "0")

    def add_block(self, data):
        prev = self.chain[-1]
        new = Block(len(self.chain), data, prev.hash)
        self.chain.append(new)

    def verify(self):
        if len(self.chain) == 1:
            print("Blockchain valide (un seul bloc)")
            return True

        for i in range(1, len(self.chain)):
            cur = self.chain[i]
            old = self.chain[i - 1]

            if cur.previous_hash != old.hash:
                print(f"❌ Rupture du chaînage au bloc {i}")
                return False

            recalculated = cur.calc_hash()
            if recalculated != cur.hash:
                print(f"❌ Données modifiées dans le bloc {i}")
                print(f"Hash enregistré :   {cur.hash}")
                print(f"Hash recalculé :    {recalculated}")
                return False

        print("✅ Blockchain valide")
        return True

    def verify_file(self):
        base_dir = "logs_in"
        files = [f for f in sorted(os.listdir(base_dir))
                 if os.path.isfile(os.path.join(base_dir, f))]

        ok = True

        for i, filename in enumerate(files):
            # bloc 1 ↔ premier fichier
            if 1 + i >= len(self.chain):
                print(f"❌ Pas de bloc pour le fichier {filename}")
                ok = False
                continue

            block = self.chain[1 + i]

            path = os.path.join(base_dir, filename)
            # IMPORTANT : même façon de hasher que lors de la création
            with open(path, "r", encoding="utf-8") as file:
                file_hash = hashlib.sha256(file.read().encode()).hexdigest()

            if block.data != file_hash:
                print(f"❌ Données modifiées pour le fichier {filename} dans le bloc {block.index}.")
                print(f"   attendu : {block.data}")
                print(f"   actuel  : {file_hash}")
                ok = False
            else:
                print(f"✅ Fichier {filename} vérifié avec succès dans le bloc {block.index}.")

        if len(self.chain) - 1 > len(files):
            print(f"⚠️ Il y a {len(self.chain)-1} blocs pour seulement {len(files)} fichiers.")
            ok = False

        return ok


# identifiant unique pour logs (si tu en as besoin plus tard)
now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + random.choice(["A","B","C","D","E","F"])


# ------------------------------------------------------------
# UTILITAIRES : LOAD / SAVE
# ------------------------------------------------------------
def load_chain_from_json(filename):
    bc = Blockchain()
    bc.chain = []

    with open(filename, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)  # liste de dicts
        except json.JSONDecodeError:
            print("Erreur : le fichier JSON est invalide.")
            return Blockchain()

    for d in data:
        block = Block(
            index=d["index"],
            data=d["data"],
            previous_hash=d["previous_hash"],
            timestamp=d["timestamp"],
            given_hash=d["hash"],
        )
        bc.chain.append(block)

    return bc


def save_chain_to_json(blockchain, filename):
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

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ------------------------------------------------------------
# LOGS → BLOCS
# ------------------------------------------------------------
def send_to_create():
    LOG_IN = "logs_in"
    for filename in sorted(os.listdir(LOG_IN)):
        path = os.path.join(LOG_IN, filename)
        if not os.path.isfile(path):
            continue
        create_log_file(path)


def create_log_file(path):
    # hash du contenu texte du fichier (mode texte + utf-8)
    with open(path, "r", encoding="utf-8") as file:
        contenue = hashlib.sha256(file.read().encode()).hexdigest()
    bc.add_block(contenue)


json_file = "transactions.json"


# ------------------------------------------------------------
# PROGRAMME PRINCIPAL
# ------------------------------------------------------------
if __name__ == "__main__":

    if os.path.exists(json_file):
        bc = load_chain_from_json(json_file)
    else:
        bc = Blockchain()
        save_chain_to_json(bc, json_file)

        # contrôle optionnel du genesis
        with open(json_file, "r", encoding="utf-8") as f:
            chain = json.load(f)
        if (not isinstance(chain, list)) or (not chain) or chain[0].get("index") != 0:
            print("BLOC GENESIS MANQUANT OU INVALIDE : RECREATION DU FICHIER JSON")
            genesis = {
                "index": 0,
                "timestamp": time.time(),
                "data": "Genesis",
                "previous_hash": "0",
                "hash": Block(0, "Genesis", "0").hash,
            }
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump([genesis], f, indent=4)
            bc = load_chain_from_json(json_file)

    # Création des blocs à partir des fichiers dans logs_in
    send_to_create()

    # Sauvegarde de la blockchain
    save_chain_to_json(bc, json_file)

    # Vérification d’intégrité des fichiers
    bc.verify_file()
