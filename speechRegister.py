import pyttsx3
import speech_recognition as sr
import pymongo
import re
import json
from bson import ObjectId
import os

mongourl = "mongodb://localhost:27017/register"

client = pymongo.MongoClient(mongourl)

database = client["register"]

collection = database["users"]


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.say(text)
    engine.runAndWait()


def get_user_input(prompt,try_count = 0,max_tries = 3):
    if try_count >= max_tries:
        speak("Sorry, maximum number of attempts reached. Please try again later.")
        return None

    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source,duration=0.2)
        speak(prompt)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        user_input = r.recognize_google(audio, language="en-in")

        user_input = user_input.replace("at the rate", "@")
        user_input = user_input.replace(" ", "")

        return user_input
    except sr.UnknownValueError as e:
        print(e)
        speak("Cant Understand Try Again")
        return get_user_input(prompt,try_count + 1,max_tries)


def validate_email(email):
    regex = r"^[\w\.-]+@([\w-]+\.)+[\w-]{2,4}$"
    return re.match(regex, email)


def create_user_folder():
    folder_name = "user data"
    os.makedirs(folder_name, exist_ok=True)
    return folder_name


def storedata(data):
    collection.insert_one(data)
    speak("Registration successful!")

    if "_id" in data and isinstance(data["_id"], ObjectId):
        data["_id"] = str(data["_id"])

    user_folder = create_user_folder()

    user_file_path = f"{user_folder}/user{collection.count_documents({})}.json"

    with open(user_file_path, "w") as jsonFile:
        json.dump(data, jsonFile)


def speechdata(first_name, last_name, email):
    speak("Your Fistname is {}".format(first_name))
    speak("Your Lastname is {}".format(last_name))
    speak("Your email is {}".format(email))


def main():
    speak("Hello! What's up? Hope you are fine!")
    speak("Welcome to the Thanos app.")
    speak("For registration, please provide the following information:")
    first_name = get_user_input("What is your first name?")
    print(first_name)

    if first_name:
        last_name = get_user_input("What is your last name?")
        print(last_name)

        if last_name:
            email = get_user_input("What is your email address?")
            print(email)

            while not email or not validate_email(email):
                speak("Invalid Email Format. Please provide valid email address")
                email = get_user_input("What is your email address?")
                print(email)

            if email:
                if validate_email(email):
                    user_data = {
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                    }

                    speak("Please validate your data")
                    speechdata(first_name, last_name, email)
                    speak("Is this valid data?")
                    confirmation = get_user_input("Please say yes or no.")

                    print(confirmation)

                    while confirmation.lower() not in ["yes", "no"]:
                        speak("Please say yes or no.")
                        confirmation = get_user_input("Please say yes or no.")

                    if confirmation.lower() == "yes":
                        print(confirmation.lower())

                        storedata(user_data)
                    elif confirmation.lower() == "no":
                        print(confirmation.lower())
                        change_info = get_user_input(
                            "What information would you like to change? First name, last name, or email?"
                        )

                        print(change_info.lower())

                        if change_info.lower() == "email":
                            newEmail = get_user_input("What is your email address?")
                            print(newEmail)

                            if validate_email(newEmail):
                                user_data["email"] = newEmail
                                speak("Email updated successfully!")

                            storedata(user_data)
                            speak("Great! Changes have been applied to your account.")
                            speechdata(first_name, last_name, newEmail)

                        elif change_info.lower() == "firstname":
                            new_first_name = get_user_input("What is your firstname?")
                            print(new_first_name)
                            user_data["first_name"] = new_first_name
                            print("data", user_data)
                            speak("firstname updated successfully!")
                            storedata(user_data)
                            speak("Great! Changes have been applied to your account.")
                            speechdata(new_first_name, last_name, email)

                        elif change_info.lower() == "lastname":
                            new_last_name = get_user_input("What is your lastname?")
                            print(new_last_name)

                            user_data["last_name"] = new_last_name
                            speak("lastname updated successfully!")
                            storedata(user_data)
                            speak("Great! Changes have been applied to your account.")
                            speechdata(first_name, new_last_name, email)

                        else:
                            speak("Sorry, I couldn't understand.")
                    else:
                        speak("Please Say Yes Or No")

                else:
                    speak("Invalid Email Format. Please provide valid email address")


if __name__ == "__main__":
    main()