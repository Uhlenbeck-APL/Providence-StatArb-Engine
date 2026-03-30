import alpaca_trade_api as tradeapi
import yfinance as yf
import pandas as pd
import time
from datetime import datetime


API_KEY = "PKQYAQ2XY4EAOFZODYC76JMOSW"
SECRET_KEY = "GCj4nvapihCxJeBchnVFuYx79fAxcTx94DB1dK4jpPrL"
BASE_URL = "https://paper-api.alpaca.markets"

# Connexion à Alpaca
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')


# LA GÂCHETTE
def executer_trade_arbitrage(z_score, ticker_a, ticker_b):
    quantite = 10 

    if z_score > 2.0:
        print(f">>> EXÉCUTION : Vente {ticker_a} / Achat {ticker_b}")
        api.submit_order(symbol=ticker_a, qty=quantite, side='sell', type='market', time_in_force='gtc')
        api.submit_order(symbol=ticker_b, qty=quantite, side='buy', type='market', time_in_force='gtc')
        
    elif z_score < -2.0:
        print(f">>> EXÉCUTION : Achat {ticker_a} / Vente {ticker_b}")
        api.submit_order(symbol=ticker_a, qty=quantite, side='buy', type='market', time_in_force='gtc')
        api.submit_order(symbol=ticker_b, qty=quantite, side='sell', type='market', time_in_force='gtc')

# LE CERVEAU 
ticker_a, ticker_b = 'NVDA', 'AMD'

print(f"[{datetime.now().strftime('%H:%M:%S')}] DÉMARRAGE DU SERVEUR PROVIDENCE V3.0 (PRODUCTION)")
print(f"Statut : Connecté à Alpaca | Surveillance active sur {ticker_a}/{ticker_b}")
print("-" * 60)

try:
    while True:
        # Aspiration des données fraîches
        donnees = yf.download([ticker_a, ticker_b], period="5d", interval="1m", progress=False)['Close']
        
        if donnees.empty or len(donnees) < 2:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Données inaccessibles. Nouvelle tentative...")
            time.sleep(30)
            continue
            
        donnees = donnees.dropna()
        
        # Calcul de la tension 
        ratio = donnees[ticker_a] / donnees[ticker_b]
        z_score = (ratio.iloc[-1] - ratio.mean()) / ratio.std()
        
        # Vérification du portefeuille
        positions = {p.symbol: p for p in api.list_positions()}
        
        # Logique d'exécution
        if abs(z_score) > 2.0 and ticker_a not in positions:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 ANOMALIE STATISTIQUE (Z={z_score:.2f})")
            executer_trade_arbitrage(z_score, ticker_a, ticker_b)
            
        elif abs(z_score) < 0.5 and (ticker_a in positions or ticker_b in positions):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ RETOUR À LA NORMALE. Clôture des positions.")
            api.close_all_positions()
            
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Radar actif. Z-Score : {z_score:.2f} | Aucun trade requis.")

        # Le rythme du serveur (1 scan par minute)
        time.sleep(60)

except Exception as e:
    print(f"ERREUR CRITIQUE DU SERVEUR : {e}")
