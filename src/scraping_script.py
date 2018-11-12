import requests
import ast
from bs4 import BeautifulSoup
import pandas as pd
import builtwith
import whois

# INIT params
base_url = "https://www.mediamarkt.es"
source_url_smartphones = 'https://www.mediamarkt.es/es/category/_smartphones-701189.html'
source_url_computers = 'https://www.mediamarkt.es/es/category/_port%C3%A1tiles-de-14-a-16-9-701422.html'

# Nos da INFO de cómo está hecho el sitio web
response_built = builtwith.builtwith(base_url)
print("Response built: \n {}".format(response_built))

# Nos da INFO del propietario
response_whois = whois.whois(base_url)
print("Response WHOIS: \n {}".format(response_whois))

# Operación de scrapping 
def scrape_data(file_out, url):
    # params
    item_list = []

    # Obtengo el html de la url
    url_data = requests.get(url).text
    
    # Creo objeto BeautifulSoup para facilitar el procesado de los datos html
    soup_object = BeautifulSoup(url_data, 'html.parser')
    
    # Por cada una de las paginas se realiza una peticion para obtener los datos
    for page in range(1, num_pages(soup_object) + 1):
        url_aux_data = requests.get(url + '?page=' + str(page)).text
        
        # Se vuelve a almacenar en un objeto BeautifulSoup
        soup = BeautifulSoup(url_aux_data, 'html.parser')
        scripts = soup.find_all('script')
        for element in scripts:
            if element.text.startswith('var product'):
                # Se añaden los elementos con informacion contenidos dentro de 'script'
                aux_var = ast.literal_eval(element.text.split(' = ')[1].strip(';'))
                item_list.append(aux_var)
                aux_var = {}
                    
    # Creacion del data frame a partir de los datos guardados en la lista item_list
    product_data_frame = pd.DataFrame(item_list)
    product_data_frame['price'] = pd.to_numeric(product_data_frame['price'], errors='coerce')
    
    # Pasar el dataframe de Pandas a CSV
    product_data_frame.to_csv(file_out, index=False)

    print('[OK] - {} registros guardados en el archivo de salida: {}'.format(product_data_frame.shape[0],file_out))

# Obtiene el numero de paginas (necesario debido a la paginacion de la web)
def num_pages(soup_object):
    pag = []
    for page_number in soup_object.find_all('div', {'class': 'pagination-wrapper cf'}):
        pag.append(page_number.find_all('a'))
    return int(str(pag[0]).split(', ')[-2].strip('</a>').split('>')[-1])

# Funcion principal
def main():
    # Define los archivos de salida
    data_path_1 = '../result_data_phones.csv'
    data_path_2 = '../result_data_computers.csv'
    try:
        print("Collecting data...")
        scrape_data(data_path_1, source_url_smartphones)
        print("Collecting data...")
        scrape_data(data_path_2, source_url_computers)
    except Exception as e:
        print("[ERROR] - Failure obtaining the data - \n {}".format(str(e)))

if __name__ == "__main__":
    main()
