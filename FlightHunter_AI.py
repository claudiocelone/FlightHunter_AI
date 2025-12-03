from openai import OpenAI
from dotenv import load_dotenv
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import (
    By,
)
from selenium.webdriver.common.keys import (
    Keys,
)
import time as t


from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from enum import Enum


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

dati_finali = {}


def cerca_voli(luogo_p, data_p, data_r, passeggeri):
    luogo_p = Sigle[luogo_p.upper()].value
    URL = f"https://it.trip.com/flights/explore?dcity={luogo_p}&ddate={data_p}&rdate={data_r}&triptype=rt&class=y&quantity={passeggeri}&searchboxarg=t&nonstoponly=off&locale=it-IT&curr=EUR"

    driver = webdriver.Chrome()
    driver.get(URL)
    t.sleep(2)

    cookie_button = driver.find_element(By.ID, "ibu-cookie-banner-btn-decline")
    cookie_button.click()
    t.sleep(2)

    voli_dict = {}

    lista_voli = driver.find_elements(By.CLASS_NAME, "top-list-flight")
    lista_voli = lista_voli[:5]

    for index, voli in enumerate(lista_voli):
        prezzo = voli.find_element(By.CLASS_NAME, "price").text
        luogo_destinazione = voli.find_element(
            By.CLASS_NAME, "top-list-flight__infoCity"
        ).text
        data_partenza_arrivo = voli.find_element(By.CLASS_NAME, "date").text
        data_partenza = data_partenza_arrivo.split(" - ")[0]
        data_arrivo = data_partenza_arrivo.split(" - ")[1]

        voli_dict[index] = {
            "destinazione": luogo_destinazione,
            "data_arrivo": data_arrivo,
            "data_partenza": data_partenza,
            "passeggeri": passeggeri,
            "prezzo": prezzo,
        }

    t.sleep(2)

    print(voli_dict)

    voli_json = json.dumps(voli_dict, ensure_ascii=False)

    prompt_valutazione = f"Questi sono i voli trovati dal sito:\n{voli_json}\nScegli i migliori 5 voli con il prezzo più basso. Rispondi SOLO con una lista JSON di 5 elementi, ordinati dal più economico al più costoso."

    response = client.responses.create(model="gpt-4.1-nano", input=prompt_valutazione)

    print("Classifica voli migliori:")
    print(response.output_text)


risposta = ""

history = [
    {
        "role": "system",
        "content": (
            "Aiutami a scegliere un volo, chattando devi ottenere queste informazioni: data partenza,data ritorno, luogo partenza, numero passeggeri."
            "Una volta ottenuti questi dati, transformali in un dizionario con campi: data_p, data_r, luogo_p, passeggeri, rispondi SOLO con questo dizionario."
            "Le date devono essere scritte in formato: yyyy-mm-dd."
        ),
    }
]


class Sigle(Enum):
    VENEZIA = "VCE"
    CATANIA = "CTA"
    TORINO = "TRN"
    NAPOLI = "NAP"
    BARI = "BRI"
    PALERMO = "PMO"
    GENOVA = "GOA"
    ALGHERO = "AHO"
    ROMA = "ROM"
    MILANO = "MIL"
    ANCONA = "AOI"
    BERGAMO = "BGY"
    BRINDISI = "BDS"
    CAGLIARI = "CAG"
    CUNEO = "CUF"
    FIRENZE = "FLR"
    LAMEZIA = "SUF"
    OLBIA = "OLB"
    PISA = "PSA"
    REGGIO_CALABRIA = "REG"
    RIMINI = "RMI"
    TRAPANI = "TPS"
    TREVISO = "TSF"
    TRIESTE = "TRS"
    VERONA = "VRN"
    BOLOGNA = "BLQ"


while True:
    response = client.responses.create(model="gpt-4.1-nano", input=history)
    output = response.output_text.strip()

    print("------------------------")
    print(f"Assistant: {output}")
    print("------------------------")

    try:
        dati_finali = json.loads(output)
        print(dati_finali)
        if (
            not dati_finali["luogo_p"]
            or not dati_finali["data_p"]
            or not dati_finali["data_r"]
            or not dati_finali["passeggeri"]
        ):
            print("dati mancanti")
        else:
            print("Dati finali trovati!")
            break
    except:
        pass

        risposta = input("Rispondi: ")
        history.append({"role": "user", "content": risposta})
        history.append({"role": "assistant", "content": output})
    continue


cerca_voli(
    dati_finali["luogo_p"],
    dati_finali["data_p"],
    dati_finali["data_r"],
    dati_finali["passeggeri"],
)
