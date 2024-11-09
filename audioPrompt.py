import os
import openai
import speech_recognition as sr

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="ro-RO")
            return text
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
            return ""
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))
            return ""

def prompt_openai(prompt):

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ești un profesor despre Inteligența Artificială."},
            {"role": "user", "content": prompt + "Informatiile trebuie sa fie corecte si scurte."}
        ]
    )

    generated_text = response.choices[0].message.content
    print(generated_text)

if __name__ == "__main__":
    audio_file = "output.wav"
    prompt = transcribe_audio(audio_file)
    if prompt:
        prompt_openai(prompt)
