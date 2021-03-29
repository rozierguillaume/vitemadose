print("ok")

from selenium.webdriver import Firefox
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
import time
import requests
import pandas as pd
import json

def search_slot(url):
    opts = Options()
    opts.headless = True
    #assert opts.headless  # Operating in headless mode
    browser = Firefox(options=opts)
    browser.get(url)
    #browser.get('https://partners.doctolib.fr/hopital-public/albertville/centre-de-vaccination-covid-maison-de-sante-d-albertville?speciality_id=5494&enable_cookies_consent=1')
    #browser.get('https://partners.doctolib.fr/centre-de-sante/faverges/centre-de-vaccination-de-faverges-seythenex?pid=practice-179054&enable_cookies_consent=1')

    browser.implicitly_wait(1)

    # Bouton Cookies
    btn = browser.find_elements_by_xpath("//button[contains(.,'Accepter & Fermer')]")
    btn[0].click()

    # Sélectionner motif
    select_element = browser.find_element_by_id("booking_motive")
    select_object = (Select(select_element))

    text_select = select_object.options[1].text
    select_object.select_by_visible_text(text_select)

    time.sleep(1)

    # Bouton prochaines dispos
    try:
        btn = browser.find_elements_by_xpath("//button[contains(.,'Prochain RDV')]")
        btn[0].click()
    except:
        print("Pas de bouton Prochain RDV")

    time.sleep(0)

    # Premier slot dispo
    slots = browser.find_elements_by_class_name("availabilities-slot")
    slot = slots[0].get_attribute("title")

    browser.close()
    return slot

def fetch_centres():
    url = "https://www.data.gouv.fr/fr/datasets/r/5cb21a85-b0b0-4a65-a249-806a040ec372"
    data = requests.get(url)

    with open('data/input/centres-vaccination.csv', 'wb') as f:
          f.write(data.content)

def import_last_output():
    try:
        with open("data/output/slots_dep.json", "r") as f:
            dict_json = json.load(f)
    except:
        print("Last output not found. Starting from empty dict.")
        dict_json = {}
    return dict_json

def export_data(dep, slots, urls):
    dict_json = import_last_output()

    dict_json[dep] = {"slots": slots, "urls": urls}

    with open("data/output/slots_dep.json", "w") as outfile:
        outfile.write(json.dumps(dict_json))

def import_departements():
    df = pd.read_csv('data/input/departements-france.csv')
    return df.code_departement.astype(str).values

def main():
    print("Starting...")
    fetch_centres()
    print("Centres fetched")
    df = pd.read_csv('data/input/centres-vaccination.csv', sep=";", dtype={'com_cp': 'object'})

    df["com_cp"] = df["com_cp"].astype("str")
    df = df[df.rdv_site_web.str.match(r'(.*doctolib.*)')==True]
    departements = import_departements()

    for dep in departements:
        print("DEP ======", dep)

        df_dep = df[df.com_cp.str.match(r'(^{}.*)'.format(dep))==True]
        #print(df_dep)

        slots=[]
        urls=[]
        for url in df_dep["rdv_site_web"].values:
            #print(url)
            try:
                slot = search_slot(url)
                slots += [slot]
                urls += [url]
            except:
                print("not found")

        export_data(dep, slots, urls)

main()