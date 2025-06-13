import os
import sys
import time
import json
import threading
import pygame
import speech_recognition as sr
from gtts import gTTS
from datetime import datetime
import pyjokes
import wikipedia
from wikipedia.exceptions import DisambiguationError
import requests
import webbrowser
import psutil
import phonenumbers
from deep_translator import GoogleTranslator
from phonenumbers import geocoder, carrier
import random
import subprocess
import openai






# Initialize pygame for soundly
pygame.init()
pygame.mixer.init()
# Set volume

is_muted = False

reminders = []  # Each reminder will be a tuple: (text, time)

facts = [
    "The speed of light is approximately 299,792 kilometers per second.",
    "Water boils at 100 degrees Celsius at standard atmospheric pressure.",
    "The human brain contains about 86 billion neurons.",
    "Pi is an irrational number, approximately equal to 3.14159.",
    "Honey never spoils."
]

quotes = [
    "The best way to get started is to quit talking and begin doing. – Walt Disney",
    "Success is not in what you have, but who you are. – Bo Bennett",
    "The only limit to our realization of tomorrow is our doubts of today. – Franklin D. Roosevelt"
]

AFFIRMATIONS = [
    "You are creative and resilient.",
    "Your ideas matter.",
    "You have overcome challenges before, and you will again."
]

print("Available microphones:")
for i, mic_name in enumerate(sr.Microphone.list_microphone_names()):
    print(f"{i}: {mic_name}")

def get_fact():
    return random.choice(facts)

def get_quote():
    return random.choice(quotes)

def recall_affirmation():
    speak(random.choice(AFFIRMATIONS))

def encouragement():
    messages = [
        "Keep going, you're doing great!",
        "Remember to celebrate small wins.",
        "Progress, not perfection."
    ]
    speak(random.choice(messages))



def translate_text(text, dest_lang):
    try:
        translated = GoogleTranslator(source='auto', target=dest_lang).translate(text)
        return translated
    except Exception as e:
        return "Sorry, I couldn't translate that."

def add_reminder(text, reminder_time=None):
    if reminder_time is None:
        speak("When should I remind, sir?")
        # For voice mode, use listen() instead of input()
        reminder_time = listen()
        if not reminder_time:
            reminder_time = input("Please enter the time for the reminder (e.g., 05:30 PM): ").strip()
    reminders.append((text, reminder_time))
    speak(f"Reminder added: {text} at {reminder_time}")

def list_reminders():
    if not reminders:
        speak("You have no reminders.")
    else:
        speak("Here are your reminders:")
        for rem, rem_time in reminders:
            if rem_time:
                speak(f"{rem} at {rem_time}")
            else:
                speak(rem)
def speak(text):
    global is_muted
    if is_muted:
        return
    print(f"LYRA: {text}")
    try:
        tts = gTTS(text=text, lang='en')
        tts.save("lyra.mp3")
        pygame.mixer.music.load("lyra.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except Exception as e:
        print(f"(Voice error: {e})")

def listen():
    recognizer = sr.Recognizer()
    mic_index = 2# Set this to your correct mic index
    with sr.Microphone(device_index=mic_index) as source:
        print("Listening for your command, sir...")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        try:
            audio = recognizer.listen(source, phrase_time_limit=6)
        except Exception as e:
            speak("Sorry, I couldn't access the microphone.")
            return ""
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is unavailable.")
        return ""

def print_lyra_logo():
    logo = r"""
      ██╗      ██    ██╗    ███████         ████████
      ██║       ██████      ██   ███        ██    ██
      ██║         ██║       ██ ███          ████████
      ██║         ██║       ██   ██         ██    ██
      ███████╗    ██        ██    ██        ██    ██
      ╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═╝

      Learning Your Requests Assistant
    """
    print(logo)

def get_weather(city="Kakinada"):
    api_key = "9d480630f1aa0407c1c8d6647a6a8e45"  # Replace with your API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] != 200:
            speak(f"Weather API error: {data.get('message', 'Unknown error')}")
            return "Weather service is currently unavailable."
        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {city} is {weather} with a temperature of {temp}°C."
    except Exception as e:
        print(f"Weather exception: {e}")  # <-- Add this line
        return "Weather service is currently unavailable."

def track_number(number):
    try:
        parsed_number = phonenumbers.parse(number, None)
        country = geocoder.description_for_number(parsed_number, "en")
        sim_carrier = carrier.name_for_number(parsed_number, "en")
        number_type = phonenumbers.number_type(parsed_number)
        type_str = phonenumbers.PhoneNumberType._VALUES_TO_NAMES.get(number_type, "Unknown")
        return f"The number is registered in {country} with carrier {sim_carrier}. Type: {type_str}."
    except Exception as e:
        return "Sorry, I couldn't track that number."

def search_location(place):
    try:
        url = f"https://nominatim.openstreetmap.org/search"
        params = {
            "q": place,
            "format": "json",
            "limit": 1
        }
        headers = {"User-Agent": "JARVIS-Assistant"}
        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        if not data:
            return "Sorry, I couldn't find that location."
        result = data[0]
        address = result.get("display_name", "Unknown location")
        lat = result.get("lat", "N/A")
        lon = result.get("lon", "N/A")
        return f"{address}. Latitude: {lat}, Longitude: {lon}."
    except Exception as e:
        return "Sorry, I couldn't search for that location."

def get_news():
    api_key = "72dd748e423a478795602603d5135dbc"  # Get from https://newsapi.org/
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])[:5]
        if not articles:
            return "Sorry, I couldn't fetch the news."
        headlines = [article["title"] for article in articles]
        return "Here are the top news headlines: " + "; ".join(headlines)
    except Exception:
        return "Sorry, I couldn't fetch the news."

def get_latest_news_about(topic):
    api_key = "6829c67cfda607deee245eb4"  # Replace with your NewsAPI key
    url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=publishedAt&apiKey={api_key}&language=en"
    try:
        response = requests.get(url)
        articles = response.json().get("articles", [])
        if not articles:
            return f"Sorry, I couldn't find any recent news about {topic}."
        headline = articles[0]["title"]
        summary = articles[0].get("description", "")
        return f"Latest on {topic}: {headline}. {summary}"
    except Exception:
        return "Sorry, I couldn't fetch the latest news right now."

def convert_currency(amount, from_currency, to_currency):
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = requests.get(url)
        rates = response.json().get("rates", {})
        rate = rates.get(to_currency.upper())
        if rate:
            converted = float(amount) * rate
            return f"{amount} {from_currency.upper()} is {converted:.2f} {to_currency.upper()}."
        else:
            return "Sorry, I couldn't convert that currency."
    except Exception:
        return "Sorry, I couldn't convert that currency."

def get_meaning(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        data = response.json()
        meaning = data[0]['meanings'][0]['definitions'][0]['definition']
        return f"The meaning of {word} is: {meaning}"
    except Exception:
        return "Sorry, I couldn't find the meaning of that word."

def open_app(app_name):
    try:
        subprocess.run(["open", "-a", app_name])
        
    except Exception as e:
        speak(f"Sorry, I couldn't open {app_name}.")

def close_app(app_name):
    try:
        subprocess.run(["osascript", "-e", f'quit app "{app_name}"'])
        
    except Exception as e:
        speak(f"Sorry, I couldn't close {app_name}.")

def show_notification(message):
    script = f'display notification "{message}" with title "LYRA"'
    subprocess.run(["osascript", "-e", script])

def periodic_reminder_alert():
    def alert():
        already_alerted = set()
        while True:
            now = datetime.now().strftime("%I:%M%p")  # e.g., 05:30PM
            for reminder, reminder_time in reminders:
                if reminder_time:
                    try:
                        reminder_time_norm = datetime.strptime(reminder_time, "%I:%M%p").strftime("%I:%M%p")
                    except ValueError:
                        continue  # Skip invalid time formats
                    if reminder_time_norm == now and (reminder, reminder_time) not in already_alerted:
                        speak(f"Hey! It's time to {reminder}. The time is {reminder_time}.")
                        already_alerted.add((reminder, reminder_time))
                else:
                    if (reminder, reminder_time) not in already_alerted:
                        speak(f"Reminder: {reminder}")
                        already_alerted.add((reminder, reminder_time))
            time.sleep(60)
    t = threading.Thread(target=alert, daemon=True)
    t.start()

def show_clock():
    try:
        print("Press Ctrl+C to exit the clock.\n")
        while True:
            now = datetime.now().strftime("%I:%M:%S %p")
            sys.stdout.write(f"\rCurrent Time: {now}   ")
            sys.stdout.flush()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting clock display.")
        speak("Exited clock display.")

def get_flights(origin, destination):
    api_key = "418ed30cdeb3c986ddf4b0836379737b"  # Replace with your Aviationstack API key
    url = f"http://api.aviationstack.com/v1/flights"
    params = {
        "access_key": api_key,
        "dep_iata": origin,
        "arr_iata": destination,
        "limit": 3  # Number of results to fetch
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        flights = data.get("data", [])
        if not flights:
            return "Sorry, I couldn't find any flights for that route."
        results = []
        for flight in flights:
            airline = flight.get("airline", {}).get("name", "Unknown Airline")
            flight_num = flight.get("flight", {}).get("iata", "N/A")
            dep_time = flight.get("departure", {}).get("scheduled", "N/A")
            arr_time = flight.get("arrival", {}).get("scheduled", "N/A")
            results.append(f"{airline} flight {flight_num}: departs at {dep_time}, arrives at {arr_time}")
        return "Here are some flights I found: " + " | ".join(results)
    except Exception as e:
        return "Sorry, I couldn't fetch flight information right now."

def solve_problem(query):
    # Simple math and logic reasoning
    try:
        # Try to evaluate as a math expression
        result = eval(query, {"__builtins__": {}})
        return f"The answer is {result}."
    except Exception:
        pass

    # Simple decision making
    if "should I" in query or "what should I do" in query:
        options = ["Absolutely, go for it!", "Maybe think it over.", "It's your call, but I say yes!", "I'd recommend caution, sir."]
        return random.choice(options)

    # Simple yes/no reasoning
    if query.strip().endswith("?"):
        options = ["Yes.", "No.", "Possibly.", "I don't have enough information, sir."]
        return random.choice(options)

    return "Sorry, I can't solve that problem yet, but I'm learning!"

def ai_solve_problem(query):
    openai.api_key = "sk-proj-4TVyl7blhxjyD5XsH2hXHYbPTT1_CXUW1xw3uarKFv8NVC5ri-0ZnpxfRtsBC5Vq1KDPVCrCfGT3BlbkFJZQqRauHzD0lJ4WmxWfLBvLEV6u7UeIV_PZMwAZFnqVULehH5cbXIRrYCvaYGGEJsN6ISUI-O0"  # Replace with your key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": query}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        answer = response.choices[0].message['content'].strip()
        return answer
    except Exception as e:
        return "Sorry, I couldn't solve that problem right now."
FOCUS_LOG_FILE = "focus_log.json"

def log_focus_task(task, completed=None):
    log_entry = {
        "task": task,
        "start_time": datetime.now().isoformat(),
        "completed": completed
    }

    try:
        with open(FOCUS_LOG_FILE, "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []

    logs.append(log_entry)

    with open(FOCUS_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)

# # === Focus Session ===
# def start_focus_session():
#     speak("What is your one focus task for the next 60 minutes?")
#     task = listen()

#     speak(f"Got it. I'll check in with you in 60 minutes about: {task}")
#     log_focus_task(task)

#     # 60-minute timer
#     def check_in():
#         time.sleep(60 * 60)
#         speak(f"Time's up. Did you complete your focus task: {task}? Say yes or no.")
#         response = listen().lower()
#         completed = response in ["yes", "i did", "done"]
#         log_focus_task(task, completed=completed)
#         speak("Logged. Well done either way.")

#     threading.Thread(target=check_in).start()

def get_location():
    try:
        url = "https://api.ipinfo.io/lite/8.8.8.8?token=cf4c724a75a7ee"
        response = requests.get(url)
        data = response.json()
        city = data.get("city", "Unknown")
        region = data.get("region", "Unknown")
        country = data.get("country", "Unknown")
        return f"You are in {city}, {region}, {country}."
    except Exception as e:
        return "Sorry, I couldn't determine your location."

def get_location_info():
    try:
        url = "https://api.ipinfo.io/lite/8.8.8.8?token=cf4c724a75a7ee"
        response = requests.get(url)
        data = response.json()
        city = data.get("city", "Unknown")
        region = data.get("region", "Unknown")
        country = data.get("country", "Unknown")
        return f"You are in {city}, {region}, {country}."
    except Exception as e:
        return "Sorry, I couldn't determine your location."

JOURNAL_FILE = "journal_log.json"

def log_journal(entry, mood=None):
    log_entry = {
        "entry": entry,
        "mood": mood,
        "time": datetime.now().isoformat()
    }
    try:
        with open(JOURNAL_FILE, "r") as f:
            logs = json.load(f)
    except FileNotFoundError:
        logs = []
    logs.append(log_entry)
    with open(JOURNAL_FILE, "w") as f:
        json.dump(logs, f, indent=4)

def start_journal_session():
    speak("How are you feeling right now?")
    mood = listen()
    speak("Would you like to add any thoughts or notes?")
    entry = listen()
    log_journal(entry, mood)
    speak("Journal entry saved. Remember, your feelings matter.")

def energy_check():
    speak("On a scale of 1 to 10, how is your energy right now?")
    level = listen()
    speak(f"Energy level {level} noted. Take a break if you need to recharge.")

def break_reminder():
    speak("Time for a quick break! Stretch, breathe, and come back refreshed.")

def respond(command):
    # Emotional support and empathy
    emotional_keywords = {
        "sad": "I'm here for you, sir. Remember, it's okay to feel sad sometimes. Would you like to hear an affirmation or a joke?",
        "stressed": "I'm sorry you're feeling stressed. Maybe a deep breath or a short break would help. Want to hear something uplifting?",
        "anxious": "Anxiety can be tough, but you're not alone. Would you like a calming affirmation or a breathing exercise?",
        "happy": "That's wonderful to hear! Keep shining, sir. Would you like to celebrate with a fun fact or a quote?",
        "angry": "It's okay to feel angry. If you want, I can help you calm down or distract you with something positive.",
        "lonely": "You're not alone, sir. I'm always here to listen. Would you like to journal your thoughts or hear an affirmation?",
        "tired": "Rest is important. Maybe a short break or some gentle encouragement would help. Would you like a motivational quote?",
        "overwhelmed": "Take it one step at a time, sir. You're doing your best. Would you like some encouragement or a reminder of your strengths?"
    }
    for feeling, response in emotional_keywords.items():
        if feeling in command:
            speak(response)
            # Listen for a follow-up "yes" or preference
            follow_up = listen()
            if "affirmation" in follow_up:
                recall_affirmation()
            elif "joke" in follow_up:
                speak(pyjokes.get_joke())
            elif "breath" in follow_up or "breathing" in follow_up:
                speak("Let's take a deep breath together. Inhale... hold... and exhale slowly. Feel a bit better?")
            elif "quote" in follow_up:
                speak(get_quote())
            elif "fact" in follow_up:
                speak(get_fact())
            elif "yes" in follow_up:
                # Default to affirmation if user just says "yes"
                recall_affirmation()
            else:
                speak("I'm here if you need anything else, sir.")
            return


    if "how are you" in command:
        speak("I'm doing well  sir. How about you?")
    elif "mute" in command:
        is_muted = True
        speak("Muted. Let me know when to unmute.")
    elif "unmute" in command:
        is_muted = False
        speak("Unmuted. Ready to assist you, sir.")
    elif "your name" in command or "who am i speaking with" in command or "who are you" in command:
        speak("You are speaking with LYRA, your personal AI assistant—think of me as your digital JARVIS, always at your service, sir.")
    elif "time" in command:
        now = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {now}, sir.")
    elif "date" in command:
        today = datetime.now().strftime("%A, %B %d, %Y")
        speak(f"Today is {today}. Another busy day ahead, sir?")
    elif "day" in command:
        today = datetime.now().strftime("%A")
        speak(f"Today is {today}.")
    elif "joke" in command:
        joke = pyjokes.get_joke()
        speak(joke)
    elif "fact" in command:
        fact = get_fact()
        speak(fact)
    elif "quote" in command:
        speak(get_quote())
    elif "affirmation" in command:
        recall_affirmation()
    elif "remind me who i am" in command or "affirmation" in command:
        recall_affirmation()
    elif "encourage me" in command or "motivate me" in command:
        encouragement()
    elif "who is" in command or "what is" in command:
        try:
            topic = command.replace("who is", "").replace("what is", "").strip()
            summary = wikipedia.summary(topic, sentences=2)
            speak(summary)
        except DisambiguationError as e:
            speak(f"Your query is ambiguous. Did you mean: {', '.join(e.options[:3])}?")
        except Exception:
            speak("Sorry, I couldn't find information on that.")
    elif "search" in command and "wikipedia" in command:
        try:
            topic = command.replace("search", "").replace("wikipedia", "").strip()
            summary = wikipedia.summary(topic, sentences=2)
            speak(summary)
        except Exception:
            speak("Sorry, I couldn't find information on that topic.")
    elif "weather" in command:
        city = "Kakinada"
        if "in" in command:
            city = command.split("in", 1)[1].strip().title()
        weather_info = get_weather(city)
        speak(weather_info)
    elif "add reminder" in command:
        reminder_text = command.replace("add reminder", "").strip()
        # Try to extract time from the command
        import re
        match = re.search(r'at (\d{1,2}:\d{2}\s*[apAP][mM])', reminder_text)
        if match:
            reminder_time = match.group(1).strip().upper().replace(' ', '')
            reminder_text = reminder_text.replace(f'at {match.group(1)}', '').strip()
            add_reminder(reminder_text, reminder_time)
        else:
            add_reminder(reminder_text)
    elif "remind me to" in command:
        task = command.split("remind me to")[-1].strip()
        # Try to extract time from the command
        import re
        match = re.search(r'at (\d{1,2}:\d{2}\s*[apAP][mM])', task)
        if match:
            reminder_time = match.group(1).strip().upper().replace(' ', '')
            task = task.replace(f'at {match.group(1)}', '').strip()
            add_reminder(task, reminder_time)
        else:
            add_reminder(task)
    elif "reminders" in command:
        list_reminders()
    elif "list reminders" in command:
        list_reminders()
    elif "calculate" in command:
        try:
            expr = command.split("calculate", 1)[1]
            result = eval(expr, {"__builtins__": {}})
            speak(f"The result is {result}")
        except Exception:
            speak("Sorry, I couldn't calculate that.")
    elif "open" in command:
        try:
            app_name = command.split("open", 1)[1].strip()
            if app_name:
                if app_name.lower().startswith("safari"):
                    # Example: "open safari apple stock price"
                    search_query = app_name[6:].strip()  # Remove "safari"
                    open_app("Safari")
                    if search_query:
                        import urllib.parse
                        url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
                        webbrowser.open(url)
                        speak(f"Opening Safari and searching for {search_query}")
                    else:
                        speak("Opening Safari.")
                elif app_name.lower().startswith("whatsapp"):
                    open_app("WhatsApp")
                    # WhatsApp desktop app does not provide message reading via automation.
                    # For WhatsApp Web, you can open it in browser:
                    speak("Opening WhatsApp . Please check your messages there.")
                    # Reading messages automatically is not supported due to WhatsApp's security.
                else:
                    open_app(app_name)
                    speak(f"Opening {app_name}")
            else:
                speak("Please specify the app to open.")
        except Exception:
            speak("Sorry, I couldn't open that app.")
    elif "open" in command and "website" in command:
        try:
            site = command.split("open", 1)[1].replace("website", "").strip()
            url = f"https://{site}"
            webbrowser.open(url)
            speak(f"Opening {site}")
        except Exception:
            speak("Sorry, I couldn't open that website.")
    elif "battery" in command:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            speak(f"Battery is at {percent} percent.")
        else:
            speak("Sorry, I couldn't get the battery status.")
    elif "track number" in command:
        # Example: "track number +14155552671"
        try:
            number = command.split("track number", 1)[1].strip()
            info = track_number(number)
            speak(info)
        except Exception:
            speak("Sorry, I couldn't track that number.")
    elif "search location" in command:
        place = command.split("search location", 1)[1].strip()
        if not place:
            speak("Please specify a place to search for.")
        else:
            info = search_location(place)
            speak(info)
    elif "translate" in command:
        try:
            # Example: "translate hello to french"
            parts = command.split("translate", 1)[1].strip()
            if " to " in parts:
                text, lang = parts.split(" to ", 1)
                text = text.strip()
                lang = lang.strip().lower()
                # Map common language names to codes
                lang_map = {
                    "french": "fr", "spanish": "es", "german": "de", "hindi": "hi","telugu": "te",
                    "kannada": "kn", "marathi": "mr", "malayalam": "ml", "punjabi": "pa",
                    "urdu": "ur", "swahili": "sw", "turkish": "tr", "dutch": "nl", "korean": "ko",
                    "vietnamese": "vi", "thai": "th", "filipino": "tl", "swedish": "sv",
                    "norwegian": "no", "danish": "da", "finnish": "fi", "czech": "cs",
                    "hungarian": "hu", "bulgarian": "bg", "greek": "el", "hebrew": "iw",
                    "indonesian": "id", "malay": "ms", "romanian": "ro", "slovak": "sk",
                    "ukrainian": "uk", "croatian": "hr", "serbian": "sr", "slovenian": "sl",
                    "estonian": "et", "latvian": "lv", "lithuanian": "lt", "icelandic": "is",
                    "irish": "ga", "welsh": "cy", "catalan": "ca", "basque": "eu",
                    "galician": "gl", "albanian": "sq", "armenian": "hy", "azerbaijani": "az",
                    "georgian": "ka", "kazakh": "kk", "uzbek": "uz", "tajik": "tg",
                    "italian": "it", "chinese": "zh-cn", "japanese": "ja", "russian": "ru",
                    "arabic": "ar", "portuguese": "pt", "bengali": "bn", "tamil": "ta"
                }
                lang_code = lang_map.get(lang, lang)
                translated = translate_text(text, lang_code)
                speak(f"The translation is: {translated}")
            else:
                speak("Please specify the language to translate to, for example: translate hello to french.")
        except Exception:
            speak("Sorry, I couldn't translate that.")
    elif "news" in command:
        news = get_news()
        speak(news)
    elif "latest news about" in command:
        topic = command.split("latest news about", 1)[1].strip()
        if not topic:
            speak("Please specify a topic to search for.")
        else:
            news = get_latest_news_about(topic)
            speak(news)
    elif "latest on" in command or "news about" in command or "update on" in command:
        # Example: "latest on virat kohli", "news about india pakistan war"
        topic = command.replace("latest on", "").replace("news about", "").replace("update on", "").strip()
        if topic:
            news = get_latest_news_about(topic)
            speak(news)
        else:
            speak("Please specify a topic you want the latest news about.")
    elif "convert" in command and "to" in command:
        try:
            parts = command.replace("convert", "").split("to")
            amount_currency = parts[0].strip().split()
            amount = amount_currency[0]
            from_currency = amount_currency[1]
            to_currency = parts[1].strip()
            result = convert_currency(amount, from_currency, to_currency)
            speak(result)
        except Exception:
            speak("Sorry, I couldn't process your currency conversion.")
    elif "close" in command:
        try:
            app_name = command.split("close", 1)[1].strip()
            if app_name:
                close_app(app_name)
                speak(f"Closing {app_name}")
            else:
                speak("Please specify the app to close.")
        except Exception:
            speak("Sorry, I couldn't close that app.")
                
    elif "meaning of" in command:
        word = command.split("meaning of", 1)[1].strip()
        meaning = get_meaning(word)
        speak(meaning)
    elif "open app" in command:
        app_name = command.split("open app", 1)[1].strip()
        open_app(app_name)
    elif "close app" in command:
        app_name = command.split("close app", 1)[1].strip()
        close_app(app_name)
    elif "open messages" in command or "check messages" in command:
        open_app("Messages")
    elif "open whatsapp" in command:
        try:
            open_app("WhatsApp")
        except Exception:
            webbrowser.open("https://web.whatsapp.com")
            speak("Opening WhatsApp Web.")
    elif "clock" in command or "show clock" in command:
        show_clock()
    elif "flights" in command:
        try:
            parts = command.split("flights", 1)[1].strip()
            if "from" in parts and "to" in parts:
                origin = parts.split("from", 1)[1].split("to", 1)[0].strip().upper()
                destination = parts.split("to", 1)[1].strip().upper()
                flight_info = get_flights(origin, destination)
                speak(flight_info)
            else:
                speak("Please specify the origin and destination, for example: flights from JFK to LAX.")
        except Exception:
            speak("Sorry, I couldn't fetch flight information.")
    elif "get flights" in command or "flight tickets" in command:
        import re
        # Example: "get flights from JFK to LHR" or "flight tickets from Delhi to Mumbai"
        match = re.search(r'from ([a-zA-Z ]+) to ([a-zA-Z ]+)', command)
        if match:
            origin = match.group(1).strip().upper()
            destination = match.group(2).strip().upper()
            speak("Fetching flight information, please wait.")
            info = get_flights(origin, destination)
            speak(info)
        else:
            speak("Please specify the origin and destination, for example: get flights from JFK to LHR.")
    elif "solve" in command or "problem" in command or "decide" in command or "reason" in command:
        query = command.replace("solve", "").replace("problem", "").replace("decide", "").replace("reason", "").strip()
        if not query:
            speak("Please state your problem or question, sir.")
        else:
            # Use AI for advanced reasoning
            answer = ai_solve_problem(query)
            speak(answer)
    elif "exit" in command or "stop" in command or "goodbye" in command:
        speak("Shutting down. Have a great day sir.")
        sys.exit()
    elif "location" in command:
        location_info = get_location()
        speak(location_info)
    elif "location info" in command:    
        location_info = get_location_info()
        speak(location_info)
    elif "journal" in command or "log mood" in command:
        start_journal_session()
    elif "energy check" in command:
        energy_check()
    elif "break reminder" in command:
        break_reminder()
    else:
        speak("I'm afraid I didn't understand that  sir.")
    
        

def text_mode():
    print_lyra_logo()
    speak("Text mode activated. Type your commands below, sir.")
    while True:
        command = input("You: ").lower()
        if not command:
            continue
        if command in ["exit", "stop", "goodbye"]:
            speak("Shutting down. Have a great day, sir.")
            sys.exit()
        if command == "switch to voice":
            speak("Switching to voice mode, sir.")
            main_mode('voice')
            return
        if command.strip() == "track number":
            number = input("Please enter the phone number (with country code, e.g., +14155552671): ").strip()
            info = track_number(number)
            speak(info)
            continue
        respond(command)

def voice_mode():
    global is_muted
    print_lyra_logo()
    print("Say 'Lyra ' to wake me up sir.")
    awake = False
    while True:
        command = listen()
        if not command:
            continue
        if command in ["exit", "stop", "goodbye"]:
            speak("Shutting down. Have a great day sir.")
            sys.exit()
        if "activate text mode" in command:
            speak("activating to text mode, sir.")
            main_mode('text')
            return
        if "activate voice mode" in command:
            speak("activating to voice mode, sir.")
            main_mode('voice')
            return

        # Wake word logic
        if not awake or is_muted:
            if "hey lyra" in command or "lyra" in command or "hello" in command or "hi" in command:
                # Wake word detected
                awake = True
                is_muted = False
                # Friendly greeting with a wish and a question about you
                hour = datetime.now().hour
                if hour < 12:
                    greeting = "Good morning"
                elif hour < 18:
                    greeting = "Good afternoon"
                else:
                    greeting = "Good evening"
                speak(f"{greeting} sir! LYRA here. How are you feeling today?")
            else:
                print("...waiting for wake word...")
            continue

        if "go to sleep" in command or "mute" in command:
            is_muted = True
            awake = False
            speak("Going to sleep sir. Say 'Lyra' if you need me again.")
            continue

        respond(command)

def main_mode(mode):
    if mode == "text":
        text_mode()
    else:
        voice_mode()

if __name__ == "__main__":
    try:
        periodic_reminder_alert()
        voice_mode()
    except KeyboardInterrupt:
        speak("System interrupted. Goodbye, sir.")