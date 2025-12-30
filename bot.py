import os
import json
import tweepy
from dune_client.client import DuneClient
from dotenv import load_dotenv

# Charger les clés du fichier .env
load_dotenv()

# Configuration
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
QUERY_ID = 6440532  # Ton nouvel ID
DB_FILE = "data.json"

def format_num(num):
    try:
        # Formatage avec espace pour les milliers
        return "{:,}".format(int(num)).replace(",", " ")
    except:
        return "0"

def run():
    print(f"⏳ Récupération du dernier résultat pour la query {QUERY_ID}...")
    dune = DuneClient(DUNE_API_KEY)
    
    try:
        # Utilisation de get_latest_result comme demandé
        query_result = dune.get_latest_result(QUERY_ID)
        today_data = query_result.result.rows[0]
        print("✅ Données Dune récupérées.")
    except Exception as e:
        print(f"❌ Erreur Dune : {e}")
        return

    # --- IDENTIFICATION DE LA COLONNE ---
    # Le SQL que nous avons fait ensemble utilise 'total_vapes'
    vapes_now = today_data.get('total_vapes', 0)

    # --- GESTION DE LA MÉMOIRE ---
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                prev_data = json.load(f)
            except:
                prev_data = {"vapes": vapes_now}
        print(f"📖 Mémoire chargée : {prev_data.get('vapes')} vapes hier.")
    else:
        prev_data = {"vapes": vapes_now}
        print("🆕 Première exécution : création de la mémoire.")

    # Calcul de la différence
    vapes_diff = vapes_now - prev_data.get("vapes", vapes_now)

    # --- PRÉPARATION DU TWEET ---
    tweet_text = (
        f"🚨 PUFFPAW SALE UPDATE 🚨\n\n"
        f"💨 Total Vapes in circulation: {format_num(vapes_now)} (+{format_num(vapes_diff)})\n\n"
    )

    print(f"📝 Tweet prêt :\n{tweet_text}")

    # --- ENVOI SUR X ---
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
        )
        client.create_tweet(text=tweet_text)
        print("🚀 Tweet envoyé sur X !")

        # Mise à jour de la mémoire pour demain
        with open(DB_FILE, "w") as f:
            json.dump({"vapes": vapes_now}, f)
        print("💾 data.json mis à jour.")
            
    except Exception as e:
        print(f"❌ Erreur Twitter : {e}")

if __name__ == "__main__":
    run()