# Non richiedono installazione
import os
import base64
from email.message import EmailMessage
from datetime import date, datetime, timedelta
import datetime
import mimetypes
import zipfile
import json
import shutil

# Richiedono installazione
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup
from oauth2client.service_account import ServiceAccountCredentials
import xlwings as xw

# Moduli

# Funzione per cercare i messaggi con una certa etichetta in base alla descrizione
def search_messages_with_label_description(label_description):
    label_mapping = get_label_mapping()
    label_id = None
    for id, description in label_mapping.items():
        if description == label_description:
            label_id = id
            break
    if label_id:
        response = service_gmail.users().messages().list(userId = mail_credenziali, labelIds = [label_id]).execute()
        messages = response.get('messages', [])

        sorted_messages = []

        for message in messages:
            # Ottieni l'ID del messaggio
            message_id = message['id']
            # Ottieni il messaggio completo
            full_message = service_gmail.users().messages().get(userId = mail_credenziali, id = message_id).execute()
            # Estrai la data interna del messaggio
            internal_date = int(full_message.get('internalDate', '0'))
            # Aggiungi il messaggio alla lista ordinata
            sorted_messages.append((message_id, internal_date))

        # Ordina i messaggi in base alla data interna
        sorted_messages.sort(key=lambda x: x[1])
        
        return [message[0] for message in sorted_messages]  # Restituisci solo gli ID dei messaggi

    else:
        print(f"Etichetta con descrizione '{label_description}' non trovata.")
        return []
# Funzione per ottenere la mappatura tra labelIds e descrizioni delle etichette
def get_label_mapping():
    response = service_gmail.users().labels().list(userId = mail_credenziali).execute()
    labels = response.get('labels', [])
    label_mapping = {}
    for label in labels:
        label_mapping[label['id']] = label['name']
    return label_mapping
# Funzione per ottenere il corpo della mail
def get_email_body(payload):
    parts = payload.get('parts', [])
    if not parts:
        return payload.get('body', {}).get('data', '')
    
    for part in parts:
        if part['mimeType'] == 'text/plain':
            body = part['body'].get('data', '')
            return urlsafe_b64decode(body).decode('utf-8')
        elif part['mimeType'] == 'text/html':
            body = part['body'].get('data', '')
            return BeautifulSoup(urlsafe_b64decode(body).decode('utf-8'), 'html.parser').get_text()
    return ''
# Funzione per creare la cartella fisica dell'offerta
def crea_cartella_offerta():

    folder_path = f"P:\\VENDITE\\OFFERTE CLIENTI\\{anno_messaggio}\\{cliente}"

    # Controllo se la cartella anno_messaggio esiste, altrimenti la creo
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Estrai le ultime due cifre dall'anno
    #OLD ultime_due_cifre_anno = str(anno_messaggio)[-2:]

    # Definisci il nome della cartella per le offerte
    #OLD nome_cartella_offerta = f"O{ultime_due_cifre_anno}{progressivo_offerta:05d}"
    nome_cartella_offerta = f"O{progressivo_offerta}"

    # Definisci il percorso completo della cartella offerta
    percorso_cartella_offerta = os.path.join(folder_path, nome_cartella_offerta)

    # Crea la cartella se non esiste già
    if not os.path.exists(percorso_cartella_offerta):
        os.makedirs(percorso_cartella_offerta)

    print(f"Cartella offerta creata: {percorso_cartella_offerta}")
    return nome_cartella_offerta
# Funzione per scaricare una mail in formato .eml
def save_message_as_eml(message_id, cartella_salvataggio_mail):
    msg = service_gmail.users().messages().get(userId = mail_credenziali, id = message_id, format = 'raw').execute()
    raw_msg = base64.urlsafe_b64decode(msg['raw'].encode('UTF-8'))
    eml_filename = os.path.join(cartella_salvataggio_mail, f"{filename} {cliente}.eml")
    with open(eml_filename, 'wb') as eml_file:
        eml_file.write(raw_msg)
# Funzione per scaricare e salvare i file allegati di una mail (contiene la funzione verifica_3d)
def save_attachments(message_id, cartella_salvataggio_mail):
    global campo_item_da_allegati
    msg = service_gmail.users().messages().get(userId = mail_credenziali, id=message_id).execute()

    # Cerca il campo "Subject" tra le intestazioni del messaggio
    subject_header = next((header for header in msg['payload']['headers'] if header['name'] == 'Subject'), None)

    # Se il campo "Subject" è stato trovato, ottieni il suo valore
    if subject_header:
        oggetto_mail = subject_header['value']
    else:
        # Se il campo "Subject" non è presente, impostiamo un valore predefinito
        oggetto_mail = 'Oggetto non disponibile'

    # Cerca il campo "From" tra le intestazioni del messaggio
    from_header = next((header for header in msg['payload']['headers'] if header['name'] == 'From'), None)

    # Se il campo "From" è stato trovato, ottieni il suo valore
    if from_header:
        mittente_mail = from_header['value'].split('<', 1)[0].strip()
    else:
        # Se il campo "From" non è presente, impostiamo un valore predefinito
        mittente_mail = 'Mittente non disponibile'

    if 'payload' in msg:
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part.get('filename'):
                    if 'data' in part['body']:
                        data = part['body']['data']
                    else:
                        att_id = part['body']['attachmentId']
                        att = service_gmail.users().messages().attachments().get(userId = mail_credenziali, messageId = message_id, id=att_id).execute()
                        data = att['data']
                    
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    file_path = os.path.join(cartella_salvataggio_mail, part['filename'])
                    
                    # Exclude certain file extensions
                    excluded_extensions = ['.exe', '.bat', '.cmd', '.vbs', '.js', '.jse', '.scr', '.png', '.jpg']
                    if not any(file_path.endswith(ext) for ext in excluded_extensions):
                        # Save the attachment
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                    
                        print(f"Allegato {part['filename']} scaricato e salvato.")
                    else:
                        print(f"!!!!! ALLEGATO {part['filename']} IGNORATO A CAUSA DI UN'ESTENSIONE POTENZIALMENTE DANNOSA. !!!!!")
            campo_item_da_allegati = verifica_3d(oggetto_mail, mittente_mail)
# Funzione per verificare che ci sia un file 3D negli allegati della mail
def verifica_3d(oggetto_mail, mittente_mail):
    global campo_item_da_allegati
    # Controllo se c'è un file .step o .stp nella cartella di salvataggio delle email
    step_presente = False
    for file_name in os.listdir(cartella_salvataggio_mail):
        if file_name.endswith('.step') or file_name.endswith('.stp'):
            step_presente = True
        if file_name.lower().endswith(('.pdf', '.tif')):
            campo_item_da_allegati += file_name[:-4]
            campo_item_da_allegati += " \n"

    # Se c'è un file .step o .stp, invia un messaggio
    if step_presente:
        print(f"Il file 3D è presente nella mail: {mittente_mail} - {oggetto_mail}")
    else:
        # Se non c'è un file .step o .stp, controlla se c'è un file .zip
        zip_presente = False
        for file_name in os.listdir(cartella_salvataggio_mail):
            if file_name.endswith('.zip'):
                zip_presente = True
                break
        
        # Se non c'è un file .zip, invia un messaggio
        if not zip_presente:
            print(f"!!!!! MANCA IL FILE 3D NELLA MAIL: {mittente_mail} - {oggetto_mail} !!!!!   ")
        else:
            # Se c'è un file .zip, controlla i file all'interno
            with zipfile.ZipFile(os.path.join(cartella_salvataggio_mail, file_name), 'r') as zip_ref:
                step_presente = False
                for file_name in zip_ref.namelist():
                    if file_name.endswith('.step') or file_name.endswith('.stp'):
                        step_presente = True
                    if file_name.endswith('.pdf'):
                        campo_item_da_allegati += file_name[:-4]
                        campo_item_da_allegati += " \n"
                
                # Se c'è un file .step o .stp all'interno dello zip, invia un messaggio
                if step_presente:
                    print(f"Il file 3D è presente nella mail: {mittente_mail} - {oggetto_mail}")
                else:
                    # Se non c'è un file .step o .stp all'interno dello zip, invia un messaggio
                    print(f"!!!!! MANCA IL FILE 3D NELLA MAIL: {mittente_mail} - {oggetto_mail} !!!!!")
    return campo_item_da_allegati
# Funzione per copiare un file excel perr creare un preventivo da 0
def copia_M48():
    # Definisci il percorso del file da copiare
    # DA MODIFICARE SE SI CAMBIA IL NOME DEL FILE
    file_da_copiare = r"P:\VENDITE\OFFERTE CLIENTI\29.03.2024__M48_Calcolo preventivo.xlsm"

    # Definisci il percorso di destinazione dove copiare il file
    percorso_destinazione = cartella_salvataggio_mail

    # Copia il file nella cartella di destinazione
    shutil.copy(file_da_copiare, percorso_destinazione)

    # Apri l'applicazione Excel
    app = xw.App(visible=False)  # Puoi impostare visible=True se desideri aprire Excel visibile
    # Apri il file Excel
    # DA MODIFICARE SE SI CAMBIA IL NOME DEL FILE
    file_path = percorso_destinazione + "\\29.03.2024__M48_Calcolo preventivo.xlsm"
    wb = app.books.open(file_path)
    # Seleziona il foglio di lavoro su cui desideri lavorare
    sheet = wb.sheets['COMMERCIALE']
    # Ora puoi modificare il contenuto del foglio di lavoro come preferisci
    # Ad esempio, scriviamo "TAGLIO" nella cella B65
    sheet.range('D1').value = progressivo_offerta
    sheet.range('E1').value = data_messaggio

    # Salva le modifiche al file Excel
    wb.save(file_path)
    # Chiudi il file Excel
    wb.close()
    # Chiudi l'applicazione Excel
    app.quit()

    print(f"File {file_da_copiare} copiato con successo in {percorso_destinazione}.")
# Funzione per compilare item e oggetto mail
def compila_campo_item_e_oggetto_mail(service_google_fogli, spreadsheet_id, campo_item):
    # Nome del foglio
    sheet_name = 'OFFERTA'
    # Esegui la richiesta per ottenere il contenuto del foglio
    result = service_google_fogli.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()

    # Ottieni i valori dal risultato
    values = result.get('values', [])

    if not values:
        print('Nessun dato trovato.')
    else:
        empty_row_index = i

        if empty_row_index is not None:

            riga_offerta = 1
                        
            # Trova il valore nella colonna B della riga corrispondente
            progressivo_offerta = int(values[empty_row_index-1][1])+1  # Assumendo che B corrisponda all'indice 1
            progressivo_offerta = int(progressivo_offerta)

            for riga_offerta in range(numero_righe_offerta):

                # Compila le colonne N, O nella stessa riga
                #body1 = {
                #    'values': [[progressivo_offerta, riga_offerta+1]]
                #}
                #update_range1 = f"{sheet_name}!N{empty_row_index + 1}:O{empty_row_index + 1}"
                #result = service_google_fogli.spreadsheets().values().update(
                #    spreadsheetId=spreadsheet_id, range=update_range1,
                #    valueInputOption='USER_ENTERED', body=body1).execute()

                # Compila le colonne N, O nella stessa riga
                if riga_offerta == 0:
                    body = {
                        'values': [[campo_item, oggetto_mail]]
                    }
                else:
                    body = {
                    'values': [["", oggetto_mail]]
                }

                update_range = f"{sheet_name}!N{empty_row_index + 1}:O{empty_row_index + 1}"
                result = service_google_fogli.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id, range=update_range,
                    valueInputOption='USER_ENTERED', body=body).execute()
                
                riga_offerta = riga_offerta + 1
                empty_row_index = empty_row_index + 1

            print("Riga aggiornata correttamente.")

    # Nome del foglio
    sheet_name2 = 'INFO OFFERTE X COMMERCIALE'
    # Esegui la richiesta per ottenere il contenuto del foglio
    result = service_google_fogli.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name2).execute()

    # Ottieni i valori dal risultato
    values = result.get('values', [])

    if not values:
        print('Nessun dato trovato.')
    else:
        empty_row_index = i

        if empty_row_index is not None:

            riga_offerta = 1

            # Trova il valore nella colonna B della riga corrispondente
            progressivo_offerta = int(values[empty_row_index-1][1])+1  # Assumendo che B corrisponda all'indice 1
            progressivo_offerta = int(progressivo_offerta)

            for riga_offerta in range(numero_righe_offerta):

                # Compila la colonna B,C nella stessa riga
                update_range1 = f"{sheet_name2}!B{empty_row_index + 1}:C{empty_row_index + 1}"
                body1 = {
                    'values': [[progressivo_offerta, riga_offerta+1]]
                }
                result = service_google_fogli.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id, range=update_range1,
                    valueInputOption='USER_ENTERED', body=body1).execute()
                # Compila la colonna F, G, H nella stessa riga
                update_range2 = f"{sheet_name2}!F{empty_row_index + 1}:H{empty_row_index + 1}"
                body2 = {
                    'values': [["IN LAVORO", "", oggetto_mail]]
                }
                result = service_google_fogli.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id, range=update_range2,
                    valueInputOption='USER_ENTERED', body=body2).execute()
                
                riga_offerta = riga_offerta + 1
                empty_row_index = empty_row_index + 1

            print("Righe aggiornate correttamente.")

# Funzione per ottenere gli id delle etichette delle e-mail
def get_label_id(label_description):
    label_mapping = get_label_mapping()
    for label_id, description in label_mapping.items():
        if description == label_description:
            return label_id
    return None
# Funzione per modificare l'etichetta dei messaggi su Gmail
def change_label_of_messages(message_ids, add_labels=None, remove_labels=None):
    body = {}
    
    if remove_labels:
        body['removeLabelIds'] = remove_labels
    if add_labels:
        body['addLabelIds'] = add_labels
 
    for message_id in message_ids:
        service_gmail.users().messages().modify(userId=mail_credenziali, id=message_id, body=body).execute()

campo_item = ""
campo_item_ferrari = ""
campo_item_da_allegati = ""

# Definisci le credenziali
SCOPES_GMAIL = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']
creds_gmail = None
# DA MODIFICARE inserire userId relativo alle credenziali
mail_credenziali = "commerciale@benozzi.com"
# Se le credenziali esistono già, caricalle dal file token.json
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')

# Se non ci sono credenziali valide, richiedi l'autorizzazione
if not creds_gmail or not creds_gmail.valid:
    if creds_gmail and creds_gmail.expired and creds_gmail.refresh_token:
        creds_gmail.refresh(Request())
    else:
        # DA MODIFICARE (Per ogni account gmail a cui si vuole fare l'accesso)
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_1059705213571-phs9gre2lktqp530bf13t906r13a6p1o.apps.googleusercontent.com.json', # sostituisci con il percorso del tuo file client_secret.json
            SCOPES_GMAIL
        )
        creds_gmail = flow.run_local_server(port=0)
    
    # Salva le credenziali nel file token.json per le esecuzioni successive
    with open('token.json', 'w') as token:
        token.write(creds_gmail.to_json())

# Inizializza l'API Gmail
service_gmail = build('gmail', 'v1', credentials=creds_gmail)

# Descrizione dell'etichetta da cercare
# DA MODIFICARE con i nomi delle etichette che si vogliono utilizzare
label_description_10 = "1-RICHIESTA_D'OFFERTA"
label_description_11 = "2-OFFERTE_DA_GESTIRE"

# Cerca i messaggi con l'etichetta specificata dalla descrizione
labeled_messages_10 = search_messages_with_label_description(label_description_10)

if not labeled_messages_10:
    print(f"Non sono state trovate mail etichettate con {label_description_10}.")
else:    
    # Per ogni mail trovata, archivia la mail in formato EML
    for message_id in labeled_messages_10:
        
        full_message = service_gmail.users().messages().get(userId = mail_credenziali, id=message_id).execute()
        payload = full_message.get('payload', {})
        headers = payload.get('headers', [])

        data_messaggio = None
        mittente = None

        for header in headers:
            if header['name'] == 'Date':
                data_messaggio = header['value']
            elif header['name'] == 'From':
                mittente = header['value']
                mittente_da_dominio = "@" + mittente.split('@')[-1].split('>')[0]
        
        # DA MODIFICARE PER GESTIRE LE ECCEZIONI (CLIENTI DIVERSI CON STESSO DOMINIO)
        if mittente_da_dominio in ["@stevanatogroup.com", "@vdletg.com", "@gmail.com", "@libero.it", "@hotmail.com", "@outlook.com", "@zoppas.com"]:
            mittente_da_dominio = mittente.split('<')[-1].split('>')[0]

        if data_messaggio:
            data_messaggio = datetime.datetime.strptime(data_messaggio, '%a, %d %b %Y %H:%M:%S %z')
            # Aggiungi 2 ore
            data_messaggio += timedelta(hours=2)
            data_messaggio = data_messaggio.strftime("%d/%m/%Y %H.%M.%S")
            # Estrai l'anno dalla data del messaggio
            anno_messaggio = datetime.datetime.strptime(data_messaggio, '%d/%m/%Y %H.%M.%S').year

        # Estrai il corpo della mail
        body = get_email_body(payload)

        # Estrazione dei caratteri specificati dal corpo della mail
        start_idx = 0
        while True:
            start_idx = body.find("- ", start_idx)
            if start_idx == -1:
                break
            end_idx = body.find(":", start_idx)
            if end_idx == -1:
                break
            extracted_string = body[start_idx + 2:end_idx].strip()
            if len(extracted_string) <= 15 and not extracted_string in campo_item_ferrari:
                if campo_item_ferrari:
                    campo_item_ferrari += " \n"
                campo_item_ferrari += extracted_string
            start_idx = end_idx + 1

        # Definisci il percorso del file JSON contenente le credenziali del tuo account di servizio
        # DA MODIFICARE con file json dell'account di servizio
        cred_json_path = 'P:\\SCAMBIO\\12-Commerciale\\Python\\download-mail-415815-918c43726b5d.json'

        # Definisci le autorizzazioni
        scope_google_fogli = ['https://www.googleapis.com/auth/spreadsheets']

        # Ottieni le credenziali dal file JSON
        creds_google_fogli = ServiceAccountCredentials.from_json_keyfile_name(cred_json_path, scope_google_fogli)

        # Autentica l'accesso
        service_google_fogli = build('sheets', 'v4', credentials=creds_google_fogli)

        # ID del foglio di lavoro
        # DA MODIFICARE con l'id del file di google fogli definitivo
        spreadsheet_id = '1p6GbUAqvbiPtwpwXyhWTbjo7pDzj934lHQ0uakL4vvc'

        # Definisci il nome del foglio "INFO"
        sheet_name_info = 'INFO'

        # Esegui la richiesta per ottenere il contenuto del foglio "INFO"
        result_info = service_google_fogli.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name_info).execute()

        # Ottieni i valori dal risultato
        values_info = result_info.get('values', [])

        if not values_info:
            print('Nessun dato trovato nel foglio "INFO".')
        else:
            cliente = None
            for row_info in values_info:
                if len(row_info) >= 4 and mittente_da_dominio in row_info[3]: 
                    cliente = row_info[1]  # Ottieni il valore corrispondente dalla colonna B
                    break

            if cliente:
                
                while True:
                    # Leggi il valore delle righe dell'offerta come stringa
                    numero_righe_offerta_str = input(f"Quante righe ha l'offerta di {cliente} del {data_messaggio}? ")

                    # Prova a convertire l'input a un intero
                    try:
                        numero_righe_offerta = int(numero_righe_offerta_str)
                        # Esci dal ciclo se la conversione ha successo
                        break
                    except ValueError:
                        # Stampa un messaggio di errore e chiedi di inserire di nuovo l'input
                        print("Il valore inserito non è un numero intero valido. Per favore, inserisci un numero intero.") 

                cliente = cliente

                # Nome del foglio
                sheet_name = 'OFFERTA'

                # Esegui la richiesta per ottenere il contenuto del foglio
                result = service_google_fogli.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=sheet_name).execute()

                # Ottieni i valori dal risultato
                values = result.get('values', [])

                if not values:
                    print('Nessun dato trovato.')
                else:
                    empty_row_index = None
                    for i, row in enumerate(values):
                        if len(row) < 5 or not row[4]:  # Se la cella in colonna D della riga è vuota
                            empty_row_index = i
                            print(f"empty_row_index={empty_row_index}")
                            break

                    if empty_row_index is not None:

                        riga_offerta = 1

                        # Calcola la riga corrente (in Google Sheets le righe iniziano da 1)
                        current_row = empty_row_index + 1 + i

                        # Calcola il numero di offerta successiva
                        progressivo_offerta = int(values[empty_row_index-1][1])+1  # Assumendo che B corrisponda all'indice 1
                        print(f"progressivo offerta={progressivo_offerta}")
                        progressivo_offerta = int(progressivo_offerta)

                        for riga_offerta in range(numero_righe_offerta):

                            # Compila la riga
                            body1 = {
                                'values': [[progressivo_offerta , riga_offerta+1]]
                            }
                            update_range1 = f"{sheet_name}!B{empty_row_index + 1}:C{empty_row_index + 1}"
                            result1 = service_google_fogli.spreadsheets().values().update(
                                spreadsheetId=spreadsheet_id, range=update_range1,
                                valueInputOption='USER_ENTERED', body=body1).execute()
                            
                            # Compila la riga
                            body2 = {
                                'values': [[data_messaggio, cliente, "", "", "Da esaminare", "Da esaminare", "Da esaminare", "Da esaminare", "IN LAVORO"]]
                            }
                            update_range2 = f"{sheet_name}!E{empty_row_index + 1}:O{empty_row_index + 1}"
                            result2 = service_google_fogli.spreadsheets().values().update(
                                spreadsheetId=spreadsheet_id, range=update_range2,
                                valueInputOption='USER_ENTERED', body=body2).execute()
                            
                            riga_offerta = riga_offerta + 1
                            empty_row_index = empty_row_index + 1
                            
                    else:
                        print("Non ci sono righe con la cella corrispettiva in D vuota.")

                nome_cartella_offerta = crea_cartella_offerta()

                # Cartella dove salvare i file
                cartella_salvataggio_mail = f"P:\\VENDITE\\OFFERTE CLIENTI\\{anno_messaggio}\\{cliente}\\{nome_cartella_offerta}"

                # Definisce il nome del file EML
                filename = f"Richiesta offerta Nr. {progressivo_offerta}"

                msg = service_gmail.users().messages().get(userId = mail_credenziali, id = message_id).execute()

                # Cerca il campo "Subject" tra le intestazioni del messaggio
                subject_header = next((header for header in msg['payload']['headers'] if header['name'] == 'Subject'), None)

                # Se il campo "Subject" è stato trovato, ottieni il suo valore
                if subject_header:
                    oggetto_mail = subject_header['value']
                else:
                    # Se il campo "Subject" non è presente, impostiamo un valore predefinito
                    oggetto_mail = 'Oggetto non disponibile'

                save_message_as_eml(message_id, cartella_salvataggio_mail)
                print(f"Mail dell'{filename} archiviata con successo nella cartella {cartella_salvataggio_mail}.")
                save_attachments(message_id, cartella_salvataggio_mail)
                copia_M48()
                if cliente == "FERRARI SPA":
                    campo_item = campo_item_ferrari
                else:
                    campo_item = campo_item_da_allegati
                compila_campo_item_e_oggetto_mail(service_google_fogli, spreadsheet_id, campo_item)
                
                # Azzera le variabili per le prossime elaborazioni
                campo_item = ""
                campo_item_ferrari = ""
                campo_item_da_allegati = ""

                # Ottieni l'ID dell'etichetta "11-Offerte archiviate"
                label_id_11 = get_label_id(label_description_11)
                label_id_10 = get_label_id(label_description_10)

                # Cambia l'etichetta della mail su Gmail
                if label_id_11 and label_id_10:
                    change_label_of_messages([message_id], remove_labels=[label_id_10], add_labels=[label_id_11])
                    print("Etichetta '1-RICHIESTA_D'OFFERTA' rimossa con successo.")
                    print("Etichetta '2-OFFERTE_DA_GESTIRE' aggiunta con successo.")
                else:   
                    print("Una delle etichette non è stata trovata.")

            else:
                msg = service_gmail.users().messages().get(userId = mail_credenziali, id=message_id).execute()
                
                # Cerca il campo "Subject" tra le intestazioni del messaggio
                subject_header = next((header for header in msg['payload']['headers'] if header['name'] == 'Subject'), None)
                
                # Se il campo "Subject" è stato trovato, ottieni il suo valore
                if subject_header:
                    oggetto_mail = subject_header['value']
                else:
                    # Se il campo "Subject" non è presente, impostiamo un valore predefinito
                    oggetto_mail = 'Oggetto non disponibile'

                # Cerca il campo "From" tra le intestazioni del messaggio
                from_header = next((header for header in msg['payload']['headers'] if header['name'] == 'From'), None)

                # Se il campo "From" è stato trovato, ottieni il suo valore
                if from_header:
                    mittente_mail = from_header['value'].split('<', 1)[0].strip()
                else:
                    # Se il campo "From" non è presente, impostiamo un valore predefinito
                    mittente_mail = 'Mittente non disponibile'    

                print(f"!!!!! IL CLIENTE CORRISPONDENTE DELLA MAIL: \"{mittente_mail} - {oggetto_mail}\"   NON È STATO TROVATO. !!!!!")
                print("!!!!! AGGIUNGERE CLIENTE E DOMINIO NEL FOGLIO 'INFO' di REGISTRO OFFERTE_NUMERATE_REV.02_2024 E RILANCIARE IL PROGRAMMA. !!!!!")

input("PREMI DOPPIO INVIO per chiudere il programma...")