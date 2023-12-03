'''
En terminar crear ambiente virtual:
- mkdir nombre_carpeta
- cd nombre_carpeta
- python3 venv -m env
- pip install requests
- pip install beautifulsoup4
- source env/bin/activate
- code.
'''

import requests
from bs4 import BeautifulSoup
import re
import csv
import pandas as pd
import json

'''
1. Obtener maqueteo HTML
    - Si el archivo html no existe de forma local, procedemos a crearlo 
    - Si el archivo html existe de forma local, procedemos a usarlo obteniedo su contenido
2. Obtener información
    - Nombre
    - Categoría
    - Reparto
    - Fecha Estreno
3. Generar archivo CSV
'''

# Crear objeto URL

url = 'https://www.imdb.com/chart/top/?ref_=nv_mv_250'

'''Función que realiza la petición al sitio web y Obtiene el maquetado'''
def get_page_content():
    headers = {
        'User-Agent':'Mozila/5.0'
    }
    response = requests.get(url, headers = headers)
    # Si respuesta de requerimiento es 200 debe retornar el maquetado de la página
    if response.status_code == 200:
        return response.text
    return None

'''Función que Crea el archivo local que guardará el contenido de la petición'''
def create_page_file_local(content):
    try:
        with open('imdb.html', 'w') as file:
            file.write(content)
    except:
        pass


'''Función que Leer el contenido del maquetado html de forma local'''
def get_page_file_local():
    content = None
    try:
        with open('imdb.html', 'r') as file:
            content = file.read()
    except:
        pass

    return content

'''Función que Obtiene el maquetado del sitio web, ya sea de forma local o del servidor'''
def get_local_page_contect():
    content = get_page_file_local()
    # Si el archivo existe, lo retorna
    if content:
        return content
    # Invoca función que realiza petición al sitio
    content = get_page_content()
    # Invoca función de guardado de contenido
    create_page_file_local(content)

    return content


def create_movies(li_tag):
    div_title = li_tag.find('div', 
                          {'class':'ipc-metadata-list-summary-item__tc'})
    title = div_title.div.a.text
    ranking = re.search(r'\d+', title).group()
    movie = re.sub(r'\d+\.\s+', '', title)

    div_features = div_title.div.find_all('span', 
                          {'class':'sc-479faa3c-8 bNrEFi cli-title-metadata-item'})
            

    # Crear una lista para almacenar los resultados de una película
    movie_info = [ranking, movie]

    # Agregar información de div_features a la lista
    for i, columna in enumerate(['año', 'duracion', 'espectador']):
        try:
            valor = div_features[i].text
        except IndexError:
            valor = f"Sin Información detectada"

        movie_info.append(valor)

    return movie_info

'''Función para guardar archivos en csv'''
def create_csv_file(movies):
    with open('movies.csv', 'w') as file:
            writer = csv.writer(file, delimiter="|")
            writer.writerow(['Ranking', 'Título', 'Año', 'Duración', 'Espectador'])

            for movie in movies:
                writer.writerow([
                    movie[0], # Ranking
                    movie[1], # Título
                    movie[2], # Año
                    movie[3], # Duración
                    movie[4], # Espectador
                ])


'''Función para guardar archivos en xlsx'''
def create_xlsx_file(movies):
    df = pd.DataFrame(movies, columns = ['Ranking', 'Título', 'Año', 'Duración', 'Espectador'])
    df.to_excel('movies.xlsx', index=False)


'''Función para guardar archivos en json'''
def create_json_file(movies):
    movies_list = [
        {
            'Ranking':movie[0], # Ranking
            'Título':movie[1], # Título
            'Año':movie[2], # Año
            'Duración':movie[3], # Duración
            'Espectador':movie[4] # Espectador
        }
        for movie in movies
    ]
    
    with open('movies.json', 'w', encoding = 'utf-8') as file:
        json.dump(movies_list, file, indent=4, ensure_ascii=False)

'''Función ejecutadora de la función anterior'''
def main():
    # Ejecutar la respuesta y maquetado. Guardarlo en objeto content
    content = get_local_page_contect()
    
    # Parsear el maquetado
    soup = BeautifulSoup(content,'html.parser')
    # Obtener la información de la etiqueta li, creando un diccionario por los atributos que tengan
    li_tags = soup.find_all('li', 
                  {'class':'ipc-metadata-list-summary-item sc-59b6048d-0 cuaJSp cli-parent'})

    # Crear una lista vacia para capturar resultados
    movies = []

    # Iterar li_tags obtenido y aplicar función de extracción de informaciòn
    for li_tag in li_tags:
        movies.append(create_movies(li_tag))

    # Generar archivo xlsx usando un dataframe
    create_xlsx_file(movies)

    # Generar archivo csv usando funcion with open
    create_csv_file(movies)

    # Generar archivo json 
    create_json_file(movies)
        

if __name__ == '__main__':
    main()
