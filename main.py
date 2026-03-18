import alpaca_trade_api as tradeapi
import yfinance as yf
import time
from datetime import datetime

import yfinance as yf
import pandas as pd

# 1. Verrouillage de la cible
cible = "NVDA" 
entite = yf.Ticker(cible)

print(f"Initialisation de l'extraction sur le réseau de {cible}...")

# 2. Aspiration des données (les 6 derniers mois)
donnees_brutes = entite.history(period="6mo")

# 3. Affichage des 5 derniers jours pour confirmer la capture
print("Extraction réussie. Voici les dernières fluctuations du marché :")
print(donnees_brutes[['Open', 'High', 'Low', 'Close', 'Volume']].tail())

# 1. Calcul de la moyenne mobile du volume sur 20 jours
# La machine apprend ce qu'est un comportement "normal"
donnees_brutes['Volume_Moyen_20j'] = donnees_brutes['Volume'].rolling(window=20).mean()

# 2. Définition de l'anomalie
# On cherche les jours où le volume est au moins 1.5 fois supérieur à la moyenne
seuil_alerte = 1.5
donnees_brutes['Anomalie_Volume'] = donnees_brutes['Volume'] > (donnees_brutes['Volume_Moyen_20j'] * seuil_alerte)

# 3. Isolement des données suspectes
jours_anormaux = donnees_brutes[donnees_brutes['Anomalie_Volume'] == True]

print("Scan terminé. Voici les jours où le marché a subi un choc de volume suspect :")
# On affiche la date, le prix de clôture, le volume réel et le volume normal attendu
print(jours_anormaux[['Close', 'Volume', 'Volume_Moyen_20j']].tail(10))

# 1. Calcul de la variation quotidienne du prix en pourcentage
donnees_brutes['Variation_Prix_%'] = donnees_brutes['Close'].pct_change() * 100

# 2. Application du filtre sur nos anomalies précédentes
jours_impact = donnees_brutes[donnees_brutes['Anomalie_Volume'] == True]

# 3. Formatage pour une lecture claire
pd.options.display.float_format = '{:.2f}'.format

print("Évaluation de l'impact terminée. Voici la direction et la violence du choc :")
print(jours_impact[['Close', 'Volume', 'Variation_Prix_%']].tail(10))

import numpy as np

# 1. Paramétrage de la machine prédictive
jours_a_simuler = 30
nombre_de_scenarios = 10000

# 2. Analyse de l'ADN financier de l'actif (moyenne et volatilité)
rendements = donnees_brutes['Variation_Prix_%'].dropna() / 100
mu = rendements.mean()
sigma = rendements.std()
prix_actuel = donnees_brutes['Close'].iloc[-1]

print(f"Lancement de la simulation Monte-Carlo : {nombre_de_scenarios} scénarios générés...")

# 3. Création de la matrice des futurs possibles (Mouvement Brownien Géométrique)
resultats_futurs = np.zeros((jours_a_simuler, nombre_de_scenarios))
resultats_futurs[0] = prix_actuel

for t in range(1, jours_a_simuler):
    # Z représente l'imprévu, le chaos du marché
    choc_aleatoire = np.random.normal(0, 1, nombre_de_scenarios)
    resultats_futurs[t] = resultats_futurs[t-1] * np.exp((mu - 0.5 * sigma**2) + sigma * choc_aleatoire)

# 4. Extraction du verdict stratégique
prix_finaux = resultats_futurs[-1]
scenarios_rentables = len(prix_finaux[prix_finaux > prix_actuel])
probabilite_succes = (scenarios_rentables / nombre_de_scenarios) * 100

print("-" * 50)
print("VERDICT DE L'INTELLIGENCE STRATÉGIQUE :")
print(f"Probabilité mathématique que l'investissement soit rentable dans 30 jours : {probabilite_succes:.2f}%")
print(f"Pire scénario simulé (Crash total) : {prix_finaux.min():.2f} $")
print(f"Meilleur scénario simulé (Explosion à la hausse) : {prix_finaux.max():.2f} $")

# 1. Calcul du RSI (L'indicateur psychologique du marché)
delta = donnees_brutes['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
perte = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / perte
donnees_brutes['RSI'] = 100 - (100 / (1 + rs))

# 2. L'Intelligence d'Exécution (Génération des ordres)
# 1 = Ordre d'Achat, -1 = Ordre de Vente (Short), 0 = Ne rien faire
donnees_brutes['Signal'] = 0
donnees_brutes.loc[donnees_brutes['RSI'] < 30, 'Signal'] = 1  
donnees_brutes.loc[donnees_brutes['RSI'] > 70, 'Signal'] = -1 

# 3. Calcul de la rentabilité (Le Backtest temporel)
# Le robot calcule ses gains/pertes en décalant le signal d'un jour (on achète à la clôture, on subit la variation du lendemain)
donnees_brutes['Rendement_Marche'] = donnees_brutes['Variation_Prix_%'] / 100
donnees_brutes['Rendement_Strategie'] = donnees_brutes['Rendement_Marche'] * donnees_brutes['Signal'].shift(1)

# 4. Le Verdict Financier Implacable
capital_initial = 10000

# Calcul des intérêts composés cumulés
donnees_propres = donnees_brutes.dropna() # On nettoie les jours sans données suffisantes
capital_final_marche = capital_initial * (1 + donnees_propres['Rendement_Marche']).cumprod().iloc[-1]
capital_final_algo = capital_initial * (1 + donnees_propres['Rendement_Strategie']).cumprod().iloc[-1]

print("=" * 50)
print("RAPPORT D'EXÉCUTION DE L'ALGORITHME PROVIDENCE :")
print(f"Capital d'amorçage : {capital_initial} €")
print(f"Stratégie Humaine (Acheter et ne rien faire) : {capital_final_marche:.2f} €")
print(f"Stratégie Machine (Trading Automatisé RSI) : {capital_final_algo:.2f} €")
print("=" * 50)

import matplotlib.pyplot as plt

# 1. Calcul de l'évolution quotidienne exacte du capital
evolution_marche = capital_initial * (1 + donnees_propres['Rendement_Marche']).cumprod()
evolution_algo = capital_initial * (1 + donnees_propres['Rendement_Strategie']).cumprod()

# 2. Paramétrage du style visuel (Dark Mode / Terminal de Trading)
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#111111') # Fond très sombre, presque noir
ax.set_facecolor('#111111')

# 3. Tracé des courbes (La preuve visuelle)
# La ligne grise terne représente l'humain passif
ax.plot(evolution_marche.index, evolution_marche, color='#555555', linewidth=2, label='Stratégie Humaine (Buy & Hold)')
# La ligne vert néon représente la machine active
ax.plot(evolution_algo.index, evolution_algo, color='#00FF41', linewidth=2.5, label='Algorithme Providence (Trading RSI)')

# 4. Personnalisation esthétique (Titres et grilles)
ax.set_title("PROVIDENCE ALGORITHM : EXÉCUTION QUANTITATIVE vs MARCHÉ (NVDA)", fontsize=14, color='white', pad=20, fontweight='bold')
ax.set_ylabel("Capital (Euros)", fontsize=12, color='white')
ax.grid(color='#333333', linestyle='--', linewidth=0.5) # Grille discrète
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#555555')
ax.spines['left'].set_color('#555555')
ax.tick_params(colors='white')
ax.legend(loc='upper left', frameon=False, fontsize=11, labelcolor='white')

# 5. Affichage final
plt.show()

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

print("Initialisation du module d'Arbitrage Statistique (Delta-Neutre)...")

# 1. Extraction des deux entités co-intégrées
tickers = ['NVDA', 'AMD']
donnees = yf.download(tickers, period="1y")['Close']
donnees = donnees.dropna()

# 2. Calcul du Spread (La différence de prix normalisée)
# Pour simplifier dans ce premier modèle, on utilise le ratio des prix
donnees['Ratio'] = donnees['NVDA'] / donnees['AMD']

# 3. Calcul de la moyenne mobile et de l'écart-type sur 20 jours
moyenne_20j = donnees['Ratio'].rolling(window=20).mean()
ecart_type_20j = donnees['Ratio'].rolling(window=20).std()

# 4. Calcul du Z-Score (La tension de l'élastique)
donnees['Z_Score'] = (donnees['Ratio'] - moyenne_20j) / ecart_type_20j

# 5. Visualisation du Radar Quantitatif
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 6))
fig.patch.set_facecolor('#111111')
ax.set_facecolor('#111111')

ax.plot(donnees.index, donnees['Z_Score'], color='#00FF41', linewidth=1.5, label='Z-Score (Tension NVDA/AMD)')

# Les lignes de déclenchement (Les anomalies statistiques)
ax.axhline(2, color='red', linestyle='--', linewidth=2, label='Seuil VENTE (NVDA trop chère)')
ax.axhline(-2, color='blue', linestyle='--', linewidth=2, label='Seuil ACHAT (NVDA trop bon marché)')
ax.axhline(0, color='white', linestyle='-', linewidth=1, label='Moyenne Historique (L\'équilibre)')

ax.set_title("RADAR D'ARBITRAGE : Z-SCORE NVDA / AMD", color='white', fontweight='bold')
ax.set_ylabel("Z-Score (Déviation Standard)", color='white')
ax.legend(loc='upper left', frameon=False, labelcolor='white')
ax.grid(color='#333333', linestyle='--', linewidth=0.5)

plt.show()

import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# 1. Paramétrage du radar en temps réel
ticker_a = 'NVDA'
ticker_b = 'AMD'
frequence_scan = 60 # Le robot scanne le marché toutes les 60 secondes

print(f"[{datetime.now().strftime('%H:%M:%S')}] DÉMARRAGE DU MOTEUR PROVIDENCE EN TEMPS RÉEL...")
print("Surveillance de l'élastique NVDA/AMD activée. Attente d'une anomalie (Z-Score > 2 ou < -2).")
print("-" * 60)

# 2. La Boucle Infinie (Le cœur du système)
# ATTENTION : Ce code tourne à l'infini jusqu'à ce que tu l'arrêtes manuellement.
for i in range(5): # Pour ce test sur Colab, on le limite à 5 scans (5 minutes) pour ne pas bloquer la machine
    
    try:
        # Aspiration des données les plus récentes (aujourd'hui, minute par minute)
        # On utilise une courte période pour la réactivité
        donnees = yf.download([ticker_a, ticker_b], period="5d", interval="1m", progress=False)['Close']
        donnees = donnees.dropna()
        
        # Calcul de la tension immédiate
        ratio = donnees[ticker_a] / donnees[ticker_b]
        moyenne_courante = ratio.mean()
        ecart_type_courant = ratio.std()
        
        # Le prix exact à cette seconde
        ratio_actuel = ratio.iloc[-1]
        z_score_live = (ratio_actuel - moyenne_courante) / ecart_type_courant
        
        heure_actuelle = datetime.now().strftime('%H:%M:%S')
        
        # 3. Le Déclencheur (Prêt à envoyer l'ordre à la banque)
        if z_score_live > 2.0:
            print(f"[{heure_actuelle}] 🔴 ALERTE CRITIQUE : Z-Score = {z_score_live:.2f} | ACTION : VENDRE NVDA / ACHETER AMD")
        elif z_score_live < -2.0:
            print(f"[{heure_actuelle}] 🟢 ALERTE CRITIQUE : Z-Score = {z_score_live:.2f} | ACTION : ACHETER NVDA / VENDRE AMD")
        else:
            print(f"[{heure_actuelle}] Statut normal. Z-Score = {z_score_live:.2f}. Aucun trade justifié.")
            
    except Exception as e:
        print(f"Erreur de connexion aux serveurs boursiers : {e}")
        
    # Le robot se met en veille avant le prochain scan
    time.sleep(frequence_scan)

print("-" * 60)
print("FIN DU CYCLE DE TEST.")

!pip install alpaca-trade-api

import alpaca_trade_api as tradeapi

# 1. Tes identifiants de connexion (À REMPLACER PAR TES VRAIES CLÉS)
API_KEY = "PKQYAQ2XY4EAOFZODYC76JMOSW"
SECRET_KEY = "GCj4nvapihCxJeBchnVFuYx79fAxcTx94DB1dK4jpPrL"
BASE_URL = "https://paper-api.alpaca.markets" # URL pour l'argent virtuel

# 2. Connexion à l'infrastructure de trading
api = tradeapi.REST(API_KEY, SECRET_KEY, BASE_URL, api_version='v2')

def executer_trade_arbitrage(z_score, ticker_a, ticker_b):
    """
    Cette fonction appuie sur la gâchette. 
    Elle achète l'un et vend l'autre simultanément.
    """
    quantite = 10 # Nombre d'actions à chaque trade (à ajuster selon ton capital)

    if z_score > 2.0:
        print(">>> EXÉCUTION : Vente NVDA / Achat AMD")
        # Ordre de vente à découvert (Short) sur la cible surévaluée
        api.submit_order(symbol=ticker_a, qty=quantite, side='sell', type='market', time_in_force='gtc')
        # Ordre d'achat sur la cible sous-évaluée
        api.submit_order(symbol=ticker_b, qty=quantite, side='buy', type='market', time_in_force='gtc')
        
    elif z_score < -2.0:
        print(">>> EXÉCUTION : Achat NVDA / Vente AMD")
        api.submit_order(symbol=ticker_a, qty=quantite, side='buy', type='market', time_in_force='gtc')
        api.submit_order(symbol=ticker_b, qty=quantite, side='sell', type='market', time_in_force='gtc')

# Pour l'intégrer, il suffira d'appeler cette fonction dans ta boucle infinie précédente.

import yfinance as yf
import time
from datetime import datetime

# --- PARAMÈTRES DU MOTEUR ---
ticker_a, ticker_b = 'NVDA', 'AMD'

print(f"[{datetime.now().strftime('%H:%M:%S')}] DÉMARRAGE DU SCANNER PROVIDENCE V2.1")
print(f"Statut : Connecté à Alpaca | Surveillance active sur {ticker_a}/{ticker_b}")
print("-" * 60)

try:
    while True:
        # 1. Récupération des données fraîches
        donnees = yf.download([ticker_a, ticker_b], period="5d", interval="1m", progress=False)['Close']
        
        # Sécurité anti-crash : on vérifie que Yahoo nous a bien répondu
        if donnees.empty or len(donnees) < 2:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Données manquantes. Nouvelle tentative...")
            time.sleep(30)
            continue
            
        donnees = donnees.dropna()
        
        # 2. Calcul de la tension de l'élastique (Z-Score)
        # Formule : $Z = \frac{Ratio_t - \mu}{\sigma}$
        ratio = donnees[ticker_a] / donnees[ticker_b]
        z_score = (ratio.iloc[-1] - ratio.mean()) / ratio.std()
        
        # 3. Surveillance des positions actuelles sur Alpaca
        positions = {p.symbol: p for p in api.list_positions()}
        
        # 4. LE DÉCLENCHEUR
        # Si on dépasse les limites et qu'on n'a pas encore de position ouverte
        if abs(z_score) > 2.0 and ticker_a not in positions:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚨 ANOMALIE DÉTECTÉE !")
            # ON APPELLE TA FONCTION DÉFINIE PLUS HAUT
            executer_trade_arbitrage(z_score, ticker_a, ticker_b)
            
        # Si le marché revient à la normale, on ferme pour encaisser
        elif abs(z_score) < 0.5 and (ticker_a in positions or ticker_b in positions):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ ÉQUILIBRE ATTEINT. Encaissement des gains.")
            api.close_all_positions()
            
        else:
            # Affichage de routine pour confirmer que le robot "respire"
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Scan OK. Z-Score : {z_score:.2f} | En attente...")

        # Pause d'une minute pour respecter les limites des serveurs
        time.sleep(60)

except Exception as e:
    print(f"ERREUR SYSTÈME : {e}")
except KeyboardInterrupt:
    print("\n[OFF] Système Providence mis en veille par l'utilisateur.")
