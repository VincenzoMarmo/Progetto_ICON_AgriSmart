% =====================================================================
% KNOWLEDGE BASE: AgriSmart - Sistema di Supporto Decisionale Agricolo
% =====================================================================

% Questi fatti sono dinamici: verranno inseriti da Python in tempo reale
% in base all'output del Machine Learning e ai dati dei "sensori".
:- dynamic coltura_prevista/2.  % es. coltura_prevista(campo_1, rice).
:- dynamic umidita_rilevata/2.  % es. umidita_rilevata(campo_1, bassa).

% 1. CONOSCENZA DI DOMINIO: Fabbisogno idrico delle colture
% Classifichiamo le colture del nostro dataset in base a quanta acqua richiedono.
necessita_acqua(rice, alta).
necessita_acqua(jute, alta).
necessita_acqua(cotton, media).
necessita_acqua(maize, media).
necessita_acqua(lentil, bassa).
necessita_acqua(chickpea, bassa).
necessita_acqua(mothbeans, bassa).

% Caso di fallback per tutte le altre colture non specificate sopra
necessita_acqua(Coltura, media) :- 
    \+ member(Coltura, [rice, jute, cotton, maize, lentil, chickpea, mothbeans]).

% 2. REGOLE INFERENZIALI (Backward Chaining)
% Il sistema decide l'intervento incrociando la coltura raccomandata e l'umidità.

% Regola 1: Coltura molto esigente ma terreno secco -> Emergenza
azione_consigliata(Campo, 'EMERGENZA IDRICA: Attivare irrigazione massima e inviare drone pompa') :-
    coltura_prevista(Campo, Coltura),
    necessita_acqua(Coltura, alta),
    umidita_rilevata(Campo, bassa).

% Regola 2: Coltura normale e terreno secco -> Intervento standard
azione_consigliata(Campo, 'INTERVENTO STANDARD: Avviare irrigazione moderata di routine') :-
    coltura_prevista(Campo, Coltura),
    necessita_acqua(Coltura, media),
    umidita_rilevata(Campo, bassa).

% Regola 3: Terreno già umido -> Nessuna irrigazione, a prescindere dalla coltura
azione_consigliata(Campo, 'MONITORAGGIO: Terreno sufficientemente umido, nessun intervento idrico necessario') :-
    umidita_rilevata(Campo, alta).

% Regola 4: Coltura che odia troppa acqua (rischio ristagni/funghi)
azione_consigliata(Campo, 'PREVENZIONE FUNGHI: Coltura a basso fabbisogno idrico, inviare drone per ispezione visiva') :-
    coltura_prevista(Campo, Coltura),
    necessita_acqua(Coltura, bassa).