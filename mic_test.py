import speech_recognition as sr

def boot_audio_receptors():
    # Initialize the recognizer
    recognizer = sr.Recognizer()
    
    # Tap into the default Windows microphone
    with sr.Microphone() as source:
        print("\n[AUDIO PROTOCOL] Calibrating to background room noise. Please wait 2 seconds...")
        # This listens to the room and adjusts the threshold so it ignores fan noise
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("[AUDIO PROTOCOL] Calibration complete.")
        
        print("\n[FRIDAY] Microphone is live. Say something, sir...")
        
        try:
            # Listen for your voice (it will timeout if you say nothing for 5 seconds)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("[FRIDAY] Audio captured. Processing neural translation...")
            
            # For the quick test, we will use Google's lightning-fast web STT
            # Later, we can upgrade this to a local Whisper model to keep it 100% offline
            text = recognizer.recognize_google(audio)
            
            print(f"\n[SYSTEM DETECTED]: \"{text}\"")
            print("[AUDIO PROTOCOL] SUCCESS! The microphone is fully operational.")
            
        except sr.WaitTimeoutError:
            print("\n[ERROR] I didn't hear anything. Is your mic plugged in and unmuted?")
        except sr.UnknownValueError:
            print("\n[ERROR] I heard noise, but couldn't understand the words. Speak clearer.")
        except Exception as e:
            print(f"\n[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    boot_audio_receptors()