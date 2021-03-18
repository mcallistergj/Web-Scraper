from clinic import Clinic
import csv
import re
import requests
from bs4 import BeautifulSoup





def get_cities(state_url, state_info):
    """Get the list of cities with clinics for state.
    """
    cur_state_cities = []

    content = requests.get(state_url)
    soup = BeautifulSoup(content.text, "html.parser")
    split_content = soup.text.split("\n")
    

    state_abbrev = state_info.split("-")[0]

    for line in split_content:
        if line.rstrip().endswith(", {}".format(state_abbrev)):
            formatted_city = line.split(",")[0].replace(" ", "-")
            cur_state_cities.append(formatted_city)


    return cur_state_cities

def clean_clinic_data(clinic):
    """Removes extra data from Clinic info.

    Args:
        clinic(Clinic): Current Clinic with data to be cleaned.

    Returned:
        Clinic: Clinic with cleaned info.
    """

    clinic.address = clinic.address.lstrip()
    clinic.zip = clinic.address.split(" ")[-1]
    # Split the string to get the miles separated, then rejoin with only the name.
    temp_list = clinic.name.split(" ")
    # The miles will always be the last 2 items in the list.
    temp_list = temp_list[:-2]
    space = " "
    clinic.name = space.join(temp_list)
    return clinic

def get_city_clinic_data(city_url):
    """Get the data for the clinics listed given the url for current city.

    Args:
        city_url(str): URL with clinic data for a given city.
    
    Returns:
        list: Human readable data from passed in URL.
    """

    city_clinics_raw = requests.get(city_url)
    city_soup = BeautifulSoup(city_clinics_raw.text, "html.parser")
    city_data = city_soup.text.split("\n")
    return city_data

if __name__ == "__main__":

    output_headers = ["Clinic Name", "Address", "State", "Zip Code", "Phone"]
    clinic_name_pattern = re.compile(r".*\(* miles\)")
    phone_patern = re.compile(r"\([0-9]{3}\) [0-9]{3}-[0-9]{4}")
    stop_text = "Tell us about your experience"


    base_url = "https://www.healthyhearing.com/hearing-aids/"

    with open("state_output.txt", "r") as state_fh:
        states = state_fh.readlines()

    for state in states:
        current_state = state.rstrip("\n")
        cur_state_url = "{}{}".format(base_url, current_state)
        cities = get_cities(cur_state_url, current_state)
        for city in cities:
            cur_city_url = "{}{}/{}".format(base_url, current_state, city)
            city_data = get_city_clinic_data(cur_city_url)
            cur_city_clinics = []
            line_index = 0
            while stop_text not in city_data[line_index]:
                name = re.search(clinic_name_pattern, city_data[line_index])
                phone = re.search(phone_patern, city_data[line_index])
                if name:
                    cur_clinic = Clinic()
                    cur_clinic.state = current_state.split("-")[-1]
                    cur_clinic.name = name.string
                elif phone:
                    cur_clinic.phone = phone.string
                elif "View clinic details" in city_data[line_index]:
                    cur_clinic.address = city_data[line_index - 1]
                    cur_city_clinics.append(cur_clinic)
                    test = 1
                line_index += 1
            
            for clinic in cur_city_clinics:
                cleaned_clinic = clean_clinic_data(clinic)

