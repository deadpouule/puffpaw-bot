import os
import json
import tweepy
from dune_client.client import DuneClient
from dotenv import load_dotenv

# Charger les clés du fichier .env
load_dotenv()

# Configuration
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
QUERY_ID = 6427346
DB_FILE = "data.json"

def format_num(num):
    try:
        return "{:,}".format(int(num)).replace(",", " ")
    except:
        return "0"

def run():
    print("⏳ Récupération des données sur Dune...")
    dune = DuneClient(DUNE_API_KEY)
    
    try:
        query_result = dune.get_latest_result(QUERY_ID)
        # On récupère la ligne de données
        today_data = query_result.result.rows[0]
    except Exception as e:
        print(f"❌ Erreur Dune : {e}")
        return

    # --- IDENTIFICATION DE LA COLONNE ---
    # Ici, on cherche la colonne des vapes/devices. 
    # J'ai mis les noms les plus probables.
    vapes_now = today_data.get('total_devices', today_data.get('vapes', 0))

    # --- GESTION DE LA MÉMOIRE ---
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            prev_data = json.load(f)
        print("📖 Mémoire chargée.")
    else:
        # Initialisation si premier lancement
        prev_data = {"vapes": vapes_now}
        with open(DB_FILE, "w") as f:
            json.dump(prev_data, f)
        print("🆕 Premier lancement : mémoire créée.")

    # Calcul de la différence
    vapes_diff = vapes_now - prev_data.get("vapes", vapes_now)

    # --- PRÉPARATION DU TWEET ---
    # Format simple : Nombre de vapes + (augmentation)
    tweet_text = (
        f"🚨 PUFFPAW SALE UPDATE 🚨\n\n"
        f"💨 Total Vapes in circulation: {format_num(vapes_now)} (+{format_num(vapes_diff)})\n\n"
    )

    print(f"📝 Tweet prêt : {tweet_text}")

    # --- ENVOI SUR X ---
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
        )
        client.create_tweet(text=tweet_text)
        print("✅ Tweet envoyé !")

        # Mise à jour de la mémoire pour demain
        with open(DB_FILE, "w") as f:
            json.dump({"vapes": vapes_now}, f)
            
    except Exception as e:
        print(f"❌ Erreur Twitter : {e}")

if __name__ == "__main__":
    run()