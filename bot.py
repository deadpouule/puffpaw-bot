import os
import json
import tweepy
from dune_client.client import DuneClient
from dotenv import load_dotenv

# Charger les clés
load_dotenv()

# Configuration
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
QUERY_ID = 6427346
DB_FILE = "data.json"

def format_num(num):
    try:
        # Formatage avec espace pour les milliers
        return "{:,}".format(int(num)).replace(",", " ")
    except:
        return "0"

def run():
    print("🔄 Forçage du rafraîchissement des données sur Dune...")
    dune = DuneClient(DUNE_API_KEY)
    
    try:
        # Lance la requête et attend le résultat frais
        query_result = dune.run_query(query_id=QUERY_ID)
        today_data = query_result.result.rows[0]
        print("✅ Données Dune récupérées avec succès.")
    except Exception as e:
        print(f"❌ Erreur Dune : {e}")
        return

    # --- IDENTIFICATION DE LA COLONNE ---
    # On cherche le chiffre actuel (vapes/devices)
    vapes_now = today_data.get('total_devices', today_data.get('vapes', 0))

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
        print("🆕 Pas de mémoire trouvée, création du fichier.")

    # Calcul de la différence avec hier
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