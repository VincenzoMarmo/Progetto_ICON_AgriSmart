import os
import pickle
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
from pyswip import Prolog
from constraint import Problem, AllDifferentConstraint


def main():
    cartella_progetto = r"C:\Users\VINCENZO\Desktop\Progetto_ICON"
    file_modello = os.path.join(cartella_progetto, "modello_agricolo.pkl")
    file_prolog = os.path.join(cartella_progetto, "regole.pl")
    
    print("=== AGRISMART: SISTEMA IBRIDO MULTI-PARADIGMA ===")
    
    # 1. CARICAMENTO MACHINE LEARNING (Argomento 3)
    try:
        with open(file_modello, 'rb') as f:
            modello, le_target = pickle.load(f)
    except FileNotFoundError:
        print("Errore: file del modello non trovato.")
        return

    # Simuliamo la lettura dei sensori per 3 campi agricoli diversi
    # Valori: [N, P, K, temperature, humidity, ph, rainfall]
    campi = {
        "Campo_Nord":  [90, 42, 43, 20.8, 18.0, 6.5, 202.9], # Terreno molto secco (bassa umidità)
        "Campo_Sud":   [10, 50, 50, 28.0, 85.0, 7.0, 150.0], # Terreno umido
        "Campo_Ovest": [60, 55, 40, 24.0, 20.0, 6.0, 100.0]  # Terreno secco
    }

    # 2. INIZIALIZZAZIONE PROLOG (Argomento 1)
    prolog = Prolog()
    percorso_prolog = file_prolog.replace("\\", "/")
    prolog.consult(percorso_prolog)
    
    azioni_campi = {}

    print("\n--- FASE 1 & 2: PREDIZIONE ML E RAGIONAMENTO LOGICO ---")
    for nome_campo, dati_sensori in campi.items():
        # A. Predizione con ML
        predizione_num = modello.predict([dati_sensori])[0]
        coltura_suggerita = le_target.inverse_transform([predizione_num])[0]
        
        # B. Dati estratti dai sensori per la logica
        livello_umidita = "bassa" if dati_sensori[4] < 40.0 else "alta"
        # Estraiamo l'Azoto (N), che è il primo parametro (indice 0)
        livello_azoto = "basso" if dati_sensori[0] < 50.0 else "ottimale"
        
        print(f"\n[{nome_campo}] Coltura ideale prevista dal ML: {coltura_suggerita.upper()}")
        print(f"[{nome_campo}] Umidità: {livello_umidita} | Azoto: {livello_azoto}")
        
        # C. Passaggio dati a Prolog
        nome_campo_pl = nome_campo.lower()
        prolog.retractall(f"coltura_prevista({nome_campo_pl}, _)")
        prolog.retractall(f"umidita_rilevata({nome_campo_pl}, _)")
        prolog.retractall(f"azoto_rilevato({nome_campo_pl}, _)")
        
        prolog.assertz(f"coltura_prevista({nome_campo_pl}, {coltura_suggerita})")
        prolog.assertz(f"umidita_rilevata({nome_campo_pl}, {livello_umidita})")
        prolog.assertz(f"azoto_rilevato({nome_campo_pl}, {livello_azoto})")
        
        # D. Inferenza Logica (Backward Chaining)
        query = f"azione_consigliata({nome_campo_pl}, Azione)"
        risultati = list(prolog.query(query))
        
        if risultati:
            azione = risultati[0]['Azione']
            if isinstance(azione, bytes):
                azione = azione.decode('utf-8')
            azioni_campi[nome_campo] = azione
            print(f">>> RISPOSTA SISTEMA ESPERTO: {azione}")

# 3. RISOLUZIONE DEI VINCOLI / CSP (Argomento 2)
    print("\n--- FASE 3: ALLOCAZIONE RISORSE (CSP) ---")
    problema = Problem()
    
    campi_da_coprire = ["Campo_Nord", "Campo_Sud", "Campo_Ovest"]
    
    # Definiamo la flotta aziendale e la relativa batteria residua (%)
    flotta_droni = {
        "Drone_Standard_1": 40,
        "Drone_Standard_2": 100,
        "Drone_Pompa_Pesante": 90,
        "Drone_Spargiconcime": 70
    }
    droni_disponibili = list(flotta_droni.keys())
    problema.addVariables(campi_da_coprire, droni_disponibili)
    
    # Vincolo 1: Univocità (Un drone non può sdoppiarsi)
    problema.addConstraint(AllDifferentConstraint(), campi_da_coprire)
    
    # Vincolo 2: Mapping Logico e Limite Energetico
    def vincolo_logistico(campo_nord, campo_sud, campo_ovest):
        assegnazioni = {"Campo_Nord": campo_nord, "Campo_Sud": campo_sud, "Campo_Ovest": campo_ovest}
        
        for campo, drone in assegnazioni.items():
            azione = azioni_campi.get(campo, "")
            
            # A. Determiniamo il costo energetico dell'azione
            costo_energia = 20 # Costo base per semplice monitoraggio visivo
            if "EMERGENZA TOTALE" in azione: 
                costo_energia = 80
            elif "EMERGENZA IDRICA" in azione: 
                costo_energia = 60
            elif "FERTILIZZAZIONE" in azione: 
                costo_energia = 50
                
            # B. Controlliamo se il drone ha abbastanza batteria
            if flotta_droni[drone] < costo_energia:
                return False
                
            # C. Controlliamo l'equipaggiamento (Hardware constraint)
            if "EMERGENZA IDRICA" in azione and drone != "Drone_Pompa_Pesante":
                return False
            if "FERTILIZZAZIONE" in azione and drone != "Drone_Spargiconcime":
                return False
            if "EMERGENZA TOTALE" in azione and drone not in ["Drone_Pompa_Pesante", "Drone_Spargiconcime"]:
                return False
                
        return True

    problema.addConstraint(vincolo_logistico, ["Campo_Nord", "Campo_Sud", "Campo_Ovest"])
    
    soluzioni = problema.getSolutions()
    
    if soluzioni:
            print("Trovata l'allocazione ottimale dei Droni nel rispetto dei vincoli hardware ed energetici:")
            miglior_soluzione = soluzioni[0] # Prendiamo la prima combinazione valida
            
            for campo, drone in miglior_soluzione.items():
                azione = azioni_campi.get(campo, "")
                
                # Ricalcoliamo il costo dell'azione per la stampa finale
                costo_energia = 20 # Costo base
                if "EMERGENZA TOTALE" in azione: 
                    costo_energia = 80
                elif "EMERGENZA IDRICA" in azione: 
                    costo_energia = 60
                elif "FERTILIZZAZIONE" in azione: 
                    costo_energia = 50
                    
                batteria_iniziale = flotta_droni[drone]
                batteria_rimanente = batteria_iniziale - costo_energia
                
                print(f" -> {campo}: assegnato a {drone} (Batteria fine missione: {batteria_rimanente}%)")
    else:
            print("CRITICITÀ LOGISTICA: Impossibile trovare un'allocazione. Ricaricare la flotta o aggiungere mezzi.")

if __name__ == "__main__":
    main()