print("---------")

from selenium.webdriver import Firefox
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
import time
import requests
import pandas as pd
import json
from datetime import datetime
from datetime import timedelta
import sys

def search_slot(url):
    opts = Options()
    opts.headless = True

    browser = Firefox(options=opts)
    browser.get(url)
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

def import_last_metadata(dep_min):
    try:
        with open("data/output/temp/metadata{}.json".format(dep_min), "r") as f:
            dict_json = json.load(f)
    except:
        print("Metada not found. Starting from empty dict.")
        dict_json = {"last_dep_updated": "no"}

    if(len(dict_json)==0):
        dict_json = {"last_dep_updated": "no"}

    return dict_json

def export_data(dep, slots, urls, noms, departements, departements_noms, dep_min):
    dict_json = {}
    dict_json = {"slots": slots, "urls": urls, "noms": noms, "scan_time": (datetime.now() + timedelta(seconds=2*3600)).strftime("%d/%m/%Y à %Hh%M")}
    dict_json["last_dep_updated"] = dep

    with open("data/output/temp/{}.json".format(dep), "w+") as outfile:
        outfile.write(json.dumps(dict_json))

    dict_metadata = {"last_dep_updated": dep}
    with open("data/output/temp/metadata{}.json".format(dep_min), "w+") as outfile:
        outfile.write(json.dumps(dict_metadata))

def get_last_updated_dep(dep_min):
    dict_json = import_last_metadata(dep_min)

    return dict_json["last_dep_updated"]

def import_departements():
    df = pd.read_csv('data/input/departements-france.csv')
    return df.code_departement.astype(str).to_list(), df.nom_departement.astype(str).to_list()

def main():
    dep_min = int(sys.argv[1])
    dep_max = int(sys.argv[2])

    print("Starting...")
    fetch_centres()
    print("Centres fetched")
    df = pd.read_csv('data/input/centres-vaccination.csv', sep=";", dtype={'com_cp': 'object'})

    df["com_cp"] = df["com_cp"].astype("str")
    df = df[df.rdv_site_web.str.match(r'(.*doctolib.*)')==True]
    departements_all, departements_noms = import_departements()

    departements = departements_all[max(0, dep_min) : min(len(departements_all)-1, dep_max)]

    last_updated_dep = get_last_updated_dep(dep_min)
    if(last_updated_dep=="no"):
        id_last_updated = dep_min
    else:
        id_last_updated = departements_all.index(last_updated_dep) + 1

    if(id_last_updated+dep_min > dep_max):
        id_last_updated = dep_min

    for dep in [departements_all[id_last_updated]]:
        print("DEP ======", dep)

        df_dep = df[df.com_cp.str.match(r'(^{}.*)'.format(dep))==True]
        print("nb centres :", len(df_dep))

        slots=[]
        urls=[]
        noms=[]
        for (idx, url) in enumerate(df_dep["rdv_site_web"].values):
            print("Centre n°", idx)
            try:
                slot = search_slot(url)
                slots += [slot]
                urls += [url]
                noms += [df_dep["nom"].values[idx]]
                print(slot)
            except:
                print("not found")

        export_data(dep, slots, urls, noms, departements, departements_noms, dep_min)

main()