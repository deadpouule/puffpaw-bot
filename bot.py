import os
import json
import tweepy
from datetime import datetime, timezone
from dune_client.client import DuneClient
from dotenv import load_dotenv

# Charger le .env seulement si on n'est pas sur GitHub Actions
if not os.getenv("GITHUB_ACTIONS"):
    load_dotenv()

# --- Configuration ---
DUNE_API_KEY = os.getenv("DUNE_API_KEY")
QUERY_ID = 6440532
DB_FILE = "data.json"

def format_num(num):
    """Formate les nombres avec un espace pour les milliers (ex: 103 955)"""
    try:
        return "{:,}".format(int(num)).replace(",", " ")
    except (ValueError, TypeError):
        return "0"

def run():
    print(f"⏳ Récupération du dernier résultat pour la query {QUERY_ID}...")
    
    # Initialisation du client Dune
    if not DUNE_API_KEY:
        print("❌ Erreur : DUNE_API_KEY manquante.")
        return
        
    dune = DuneClient(DUNE_API_KEY)
    
    try:
        # Récupération des données (dernière exécution en cache)
        query_result = dune.get_latest_result(QUERY_ID)
        today_data = query_result.result.rows[0]
        print("✅ Données Dune récupérées.")
    except Exception as e:
        print(f"❌ Erreur Dune : {e}")
        print("Astuce : Allez sur Dune et cliquez sur 'Run' manuellement une fois.")
        return

    # Extraction de la valeur actuelle (colonne 'total_vapes')
    vapes_now = today_data.get('total_vapes', 0)

    # --- GESTION DE LA MÉMOIRE (data.json) ---
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try:
                prev_data = json.load(f)
                vapes_yesterday = prev_data.get("vapes", vapes_now)
            except Exception:
                vapes_yesterday = vapes_now
    else:
        vapes_yesterday = vapes_now

    vapes_diff = vapes_now - vapes_yesterday

    # --- DATE ET HEURE UTC (Format propre sans Warning) ---
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%d/%m/%Y - %H:%M")

    # --- PRÉPARATION DU TWEET ---
    tweet_text = (
        f"🚨 PUFFPAW SALE UPDATE 🚨\n\n"
        f"💨 Total Vapes in circulation: {format_num(vapes_now)} (+{format_num(vapes_diff)})\n\n"
        f"📅 {date_str} UTC"
    )

    print(f"📝 Tweet prêt :\n{tweet_text}")

    # --- ENVOI SUR X (API v2) ---
    try:
        client = tweepy.Client(
            consumer_key=os.getenv("X_API_KEY"),
            consumer_secret=os.getenv("X_API_SECRET"),
            access_token=os.getenv("X_ACCESS_TOKEN"),
            access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET")
        )
        
        client.create_tweet(text=tweet_text)
        print("🚀 Tweet envoyé sur X !")

        # Mise à jour de la mémoire pour le calcul de demain
        with open(DB_FILE, "w") as f:
            json.dump({"vapes": vapes_now}, f)
        print("💾 data.json mis à jour avec succès.")
            
    except Exception as e:
        print(f"❌ Erreur Twitter : {e}")

# Lancement du script
if __name__ == "__main__":
    run()