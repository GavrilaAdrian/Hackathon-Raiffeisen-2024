import os
import openai
import speech_recognition as sr
from pydub import AudioSegment
from fpdf import FPDF

def convert_mp3_to_wav(mp3_file_path):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(mp3_file_path)
    wav_file_path = mp3_file_path.replace(".mp3", ".wav")
    # Export the file as WAV
    audio.export(wav_file_path, format="wav")
    return wav_file_path

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            # Set the language to Romanian
            text = recognizer.recognize_google(audio_data, language="ro-RO")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return ""

def summarize_text(prompt):
    openai.api_key = ""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ești un asistent bancar specializat care extrage informații esențiale din conversațiile cu clienții. Răspunde structurat, incluzând doar detalii relevante."},
            {"role": "user", "content": ("Analizează următoarea conversație și asigura-te ca extragi toate informațiile esențiale atat despre client cat si despre problema acestuia raportata la banca, inclusiv numele clientului si alte detalii personale relevante, tipul cererii, "
                                         "detalii despre cont sau alte informații de identificare și alte operațiuni menționate: informații despre soldul contului,"
                                         "deschiderea unui cont de economii, modificarea limitei cardului de credit, rambursarea anticipată a unui credit, detalii despre transferuri internaționale"
                                         "blocarea unui card pierdut sau furat, actualizarea datelor personale, activarea sau dezactivarea serviciului de internet banking"
                                         "refinanțarea unui credit existent, programele de loialitate sau puncte de recompensă si multe atele. Informatiile trebuie sa fie scrise cat mai"
                                         "concis, adica in sa contina keyword-urile din domeniul banking. Am nevoie de 2 campuri la iesire, unul cu numele complet de forma Nume complet: si unul cu lista numerotata a problemelor clientului de forma Probleme:." 
                                         "Daca clientul nu are defapt nicio problema sau intrebare legata de banca, se va afisa un mesaj de genul: Acest tip de problema nu intra in expertiza bancii Raiffeisen."+ prompt)}
        ],
        temperature= 0.1
    )
    generated_text = response.choices[0].message.content
    return generated_text
    # with open("generated_text.txt", "w", encoding="utf-8") as file:
    #     file.write(generated_text)
    
    # pdf = FPDF()
    # pdf.add_page()
    # pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    # pdf.set_font("DejaVu", size=12)
    # pdf.multi_cell(0, 10, generated_text)
    # pdf.output("summary.pdf")
    # print("Summary saved to summary.pdf")

if __name__ == "__main__":
    mp3_file = "./audio/mesaj.mp3"
    # Convert MP3 to WAV
    wav_file = convert_mp3_to_wav(mp3_file)
    # Transcribe the WAV file
    prompt = transcribe_audio(wav_file)
    if prompt:
        # Send the transcription to OpenAI for summarization
        summarize_text(prompt)
