import os
import json
import tweepy
from datetime import datetime
from dune_client.client import DuneClient
from dune_client.query import Query # <-- NOUVEL IMPORT
from dotenv import load_dotenv

# Charger les clés
load_dotenv()

# Configuration
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
QUERY_ID = 6440532
DB_FILE = "data.json"

def format_num(num):
    try:
        return "{:,}".format(int(num)).replace(",", " ")
    except:
        return "0"

def run():
    print("🔄 Récupération des données sur Dune...")
    dune = DuneClient(DUNE_API_KEY)
    
    try:
        # On crée un objet Query au lieu de passer juste le chiffre
        query = Query(query_id=QUERY_ID)
        query_result = dune.run_query(query)
        
        today_data = query_result.result.rows[0]
        print("✅ Données Dune récupérées.")
    except Exception as e:
        print(f"❌ Erreur Dune : {e}")
        return

    vapes_now = today_data.get('total_vapes', 0)

    # --- GESTION DE LA MÉMOIRE ---
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                prev_data = json.load(f)
            except:
                prev_data = {"vapes": vapes_now}
    else:
        prev_data = {"vapes": vapes_now}

    vapes_diff = vapes_now - prev_data.get("vapes", vapes_now)

    # --- RÉCUPÉRATION DE LA DATE ET L'HEURE ---
    now = datetime.utcnow()
    date_str = now.strftime("%d/%m/%Y - %H:%M")

    # --- PRÉPARATION DU TWEET UNIQUE ---
    tweet_text = (
        f"🚨 PUFFPAW SALE UPDATE 🚨\n\n"
        f"💨 Total Vapes in circulation: {format_num(vapes_now)} (+{format_num(vapes_diff)})\n\n"
        f"📅 {date_str} UTC"
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

        # Mise à jour de la mémoire
        with open(DB_FILE, "w") as f:
            json.dump({"vapes": vapes_now}, f)
        print("💾 data.json mis à jour.")
            
    except Exception as e:
        print(f"❌ Erreur Twitter : {e}")

if __name__ == "__main__":
    run()