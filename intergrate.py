import paho.mqtt.client as mqtt
import firebase_admin 
from firebase_admin import db 
import datetime
import speech_recognition as sr

#########################################
cred_obj = firebase_admin.credentials.Certificate("smarthome-d91d1-firebase-adminsdk-p9xh1-bb1055139e.json")
default_app = firebase_admin.initialize_app(cred_obj, {
    "databaseURL": "https://smarthome-d91d1-default-rtdb.asia-southeast1.firebasedatabase.app/"
})
##########################################
def on_message(client, userdata, message):
    data = str(message.payload.decode("utf-8"))
    data = message.payload.decode("utf-8").split(":")
    # print("a:", data[0])
    # print("b:", data[1])
    # print("c:", data[2])
    # print("d:", data[3])
    now = datetime.datetime.now()
    time_str = now.strftime("%d/%m/%Y %H:%M:%S")

    result = db.reference("/Sensor/Temperature").push(float(data[0]))
    result = db.reference("/Sensor/Humidity").push(float(data[1]))
    result = db.reference("/Sensor/Light").push(float(data[2]))
    result = db.reference("/Sensor/Fire").push(float(data[3]))
    result = db.reference("/Sensor/time").push((time_str))

mqttBroker = "test.mosquitto.org"
client = mqtt.Client("")
client.connect(mqttBroker)

client.loop_start()
client.subscribe("/topic/test3")
client.on_message = on_message

############################################

client2 = mqtt.Client("")
client2.connect(mqttBroker)

r = sr.Recognizer()
mic = sr.Microphone()
while True:
    led = db.reference("/Device/Bulb").get()
    if led == 1:
        client2.publish("/topic/test2", 1)
    elif led == 0:
        client2.publish("/topic/test2", 0)
    isTalking = db.reference("/Voice").get()
    if isTalking == 1:
        print("Please talk!")
        with mic as source:
            # print("Adjusting noise ")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Recording for 3 seconds")
            audio = r.listen(source, phrase_time_limit=3)
            print("Done recording")
        try:
            text = r.recognize_google(audio, language="en-US")
            print("Bạn nói: " + text)
            if text == "turn on":
                db.reference("/Device/Bulb").set(int(1))
                print("Đã bật bóng đèn")
                client2.publish("/topic/test2", 1)
            elif text == "turn off":
                db.reference("/Device/Bulb").set(int(0))
                print("Đã tắt bóng đèn")
                client2.publish("/topic/test2", 0)
            elif text == "turn on the dehumidifier":
                db.reference("/Device/Dehumidifiers").set(int(1))
                print("Đã bật máy hút ẩm")

            elif text == "turn off the dehumidifier":
                db.reference("/Device/Dehumidifiers").set(int(0))
                print("Đã tắt máy hút ẩm")

            elif text == "turn on the fan":
                db.reference("/Device/Fan").set(int(1))
                print("Đã bật quạt")
 
            elif text == "turn off the fan":
                db.reference("/Device/Fan").set(int(0))
                print("Đã tắt quạt")

            else:
                print("Lệnh không hợp lệ")
        except sr.UnknownValueError:
            print("Không nhận dạng được giọng nói")
    else:
        pass
    
#####################################################

