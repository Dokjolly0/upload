import os
from googletrans import Translator
import pysrt
from concurrent.futures import ThreadPoolExecutor

def translate_srt(input_file_path, output_file_path, dest_language, chunk_size=1):
    # Inizializza il traduttore
    translator = Translator()
    try:
        # Apri il file SRT e leggine il contenuto
        subs = pysrt.open(input_file_path, encoding='utf-8')
    except Exception as e:
        print(f"Problema nell'apertura del file {input_file_path}: {e}")
        return

    # Funzione per tradurre pezzi di sottotitoli
    def translate_chunk(sub_chunk):
        translated_chunk = []
        for sub in sub_chunk:
            # Traduci il testo di ogni sottotitolo
            translated_text = translator.translate(sub.text, dest=dest_language)
            if translated_text and translated_text.text.strip():
                sub.text = translated_text.text
            else:
                print("La traduzione ha restituito Nessuno o una stringa vuota. Utilizzando il testo originale.")
            translated_chunk.append(sub)
        return translated_chunk

    # Dividi i sottotitoli in blocchi
    sub_chunks = [subs[i:i + chunk_size] for i in range(0, len(subs), chunk_size)]

    # Utilizza un ThreadPoolExecutor per tradurre blocchi in parallelo
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Elabora i blocchi dei sottotitoli in parallelo
        translated_chunks = list(executor.map(translate_chunk, sub_chunks))

    # Appiattisci l'elenco delle parti tradotte in un unico elenco di sottotitoli
    translated_subs = [sub for chunk in translated_chunks for sub in chunk]

    try:
        # Salva il file SRT tradotto
        pysrt.SubRipFile(translated_subs).save(output_file_path, encoding='utf-8')
        print(f"File tradotto salvato in {output_file_path}")
    except Exception as e:
        print(f"Problema durante il salvataggio del file: {e}")

def translate_srt_directory(input_dir, output_dir, dest_language, chunk_size=1):
    # Preparare l'elenco dei percorsi dei file per la traduzione
    file_paths = [
        (os.path.join(input_dir, file_name), os.path.join(output_dir, f"{file_name}.{dest_language}.srt"))
        for file_name in sorted(os.listdir(input_dir))
        if file_name.endswith('.srt')
    ]
    
    # Esegui la traduzione in parallelo utilizzando ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Invia attività di traduzione per ciascun file SRT
        futures = executor.map(lambda paths: translate_srt(*paths, dest_language, chunk_size), file_paths)
        # Convert the map object to a list to wait for all futures to complete
        list(futures)

# Directory di input e output
input_dir = os.path.abspath('upload')
output_dir = os.path.abspath('translated')
# Directory di input e output
dest_language = input("Inserire la lingua di destinazione (es. 'it' per l'italiano): ")

# Specificare la dimensione del blocco per la traduzione
chunk_size = 200

# Crea la directory di output se non esiste
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Chiama la funzione per tradurre tutti i file SRT nella directory di input
translate_srt_directory(input_dir, output_dir, dest_language, chunk_size)

input("Premere INVIO per chiudere il programma")
