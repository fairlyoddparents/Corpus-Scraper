from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By

import time
from random import random
import re

import xlsxwriter


data = {'verbo': 'ABALANZAR',
        'voz': None,
        'tam': None,
        'perifrasis': None,
        'h_genero': None,
        'h_procedencia': None,
        'h_num_argumentos': None,
        'FUNCION_S1': None,
        'unidad1': None,
        'animacion1': None,
        'orden1': None,
        'FUNCION_S2': None,
        'unidad2': None,
        'animacion2': None,
        'orden2': None,
        'FUNCION_S3': None,
        'unidad3': None,
        'animacion3': None,
        'orden3': None,
        }

def clean_html(html_text):
    #Toma el html code del parrafo con la oracion y cambia primero las etiquetas que rodean a la palabra por FOONT
    #Despues elimina todas las etiquetas restantes y regresa el parrafo limpio
    paragraph_sin_font = re.sub(r'<.*?u>', "FOONT", html_text)
    paragraph_sin_html = re.sub(r'<.*?>', "", paragraph_sin_font)

    return paragraph_sin_html

def check_field_not_empty(value):
    if value != None and value != "" and value != "Menu":
        if value.strip() != "":
                return True

def write_values_on_web_page(driver, field, value):
    if check_field_not_empty(value):
    #Eliminar espacios innecesarios en verbo y perifrasis
        if field == "verbo" or field == "perifrasis":
            value = value.strip()
    #Seleccionar los valores en los menus en la pagina
        (Select(driver.find_element_by_css_selector(f'select[name="{field}"]'))).select_by_visible_text(value)

def get_all_example_s_urls_in_page(driver, url_list, labels=None):
    #Busca en la pagina todos los <a> elementos y obtiene sus urls y los append en url_list
    try:
        urls = driver.find_elements_by_css_selector("a[title='Pincha para ver la ficha de este ejemplo']")
        for url in urls:
            url_link = url.get_attribute('href')
            url_list.append(url_link)
    except:
        labels[3].text = "Bad coding, no se encontraron los urls en la pagina"

def go_to_the_next_pages_extracting_urls(driver, url_list, number_of_examples, seconds, labels=None):
    try:
    #Determina si hay mas de una pagina con 200 ejemplos y si sí, pica siguiente
    #y descarga los urls de todas las paginas y si no regresa la misma lista
        if number_of_examples > 200:
            number_of_pages = number_of_examples//200
            for i in range(number_of_pages):
                driver.find_element_by_css_selector('img.next').click()
                get_all_example_s_urls_in_page(driver, url_list, labels)
                time.sleep((5+(random()*5)))
        return url_list
    except:
        labels[3].text = "Bad coding, no se encontró el botón para ir a página siguiente"

def get_all_urls_by_going_page_by_page(driver, seconds, number_of_examples):
    #identify the number of pages with 200 examples
    (Select(driver.find_element_by_css_selector('select.pagesize'))).select_by_visible_text("200")

    #Click next and get all the urls and append them to url_list (first page) and then to final_url_list (todas las paginas)
    url_list = []
    get_all_example_s_urls_in_page(driver, url_list)
    final_url_list = go_to_the_next_pages_extracting_urls(driver, url_list, number_of_examples, seconds)
    return final_url_list

def download_all_info(driver, url_list, verbo, seconds, labels=None, limited_number=0):
    #Create excel file to save the info on
    workbook = xlsxwriter.Workbook(f'{verbo}_{str(seconds)[-5:]}_data.xlsx')
    worksheet = workbook.add_worksheet('sentences')

    #add headers
    headers = ['Sentence', 'Url', 'ID', 'Author', 'Text source', 'Publication']
    header_format = workbook.add_format({'bold':True})
    worksheet.write_row('A1', headers, header_format)

    #Create formats
    general_format = workbook.add_format({'text_wrap':1, 'valign':'top'})
    url_format = workbook.add_format({'valign':'top'})
    year_format = workbook.add_format({'text_wrap':1, 'align':'left', 'valign':'top'})
    concept_format = workbook.add_format({'bold':True, 'font_color':'#8b1728', 'italic':True, 'underline':True})

    #Set column with formats
    worksheet.set_column('A:A', 50, general_format)
    worksheet.set_column('E:E', 20, general_format)
    worksheet.set_column('G:G', 20, general_format)
    worksheet.set_column('F:F', 25, general_format)

    #Limit the number of downloads according to the number provided by the user
    if limited_number == 0:
        list_to_iterate = url_list
    else:
        list_to_iterate = url_list[:limited_number]

    #Get all the info
    row_number = 1
    for active_url in list_to_iterate:
        row_number += 1
        driver.get(active_url)

    #Locate all the data we need
        text_id = driver.find_element_by_xpath('//*[@id="referencias"]/tbody/tr[1]/td[2]').text
        autor = driver.find_element_by_xpath('//*[@id="referencias"]/tbody/tr[2]/td[2]').text
        obra = driver.find_element_by_xpath('//*[@id="referencias"]/tbody/tr[3]/td[2]/i').text
        publicacion = driver.find_element_by_xpath('//*[@id="referencias"]/tbody/tr[4]/td[2]').text
        texto = driver.find_element_by_xpath('//*[@id="referencias"]/tbody/tr[5]/td[2]').get_attribute('innerHTML')

    #Write info on excel file
    #Separate texto to add bold letters to target word before writing it on the excel file
        paragraph_sin_html = clean_html(texto)
        paragraph_divided = paragraph_sin_html.split("FOONT")


        if paragraph_divided[0] == "": ####TESTING
            paragraph_divided[0] = " " ####TESTING

        if paragraph_divided[2] == "": ####TESTING
            paragraph_divided[2] = " " ####TESTING

        worksheet.write_rich_string(f'A{row_number}', paragraph_divided[0], concept_format, paragraph_divided[1], paragraph_divided[2])
        worksheet.write_string(f'B{row_number}', active_url, url_format)
        worksheet.write(f'C{row_number}', text_id, year_format)
        worksheet.write(f'D{row_number}', autor, general_format)
        worksheet.write(f'E{row_number}', obra, general_format)
        worksheet.write(f'F{row_number}', publicacion, general_format)

        time.sleep((5+(random()*5)))

    workbook.close()

    labels[1].text = "Listo."
    labels[2].text = "Listo."
    labels[3].text = 'Listo.'
    labels[0].text = "Terminado."
    labels[4].text = f"Busca el archivo {verbo}_{str(seconds)[-5:]}_data.xlsx en tu computadora."

def realizar_busqueda(data, limited_number=0, labels=None):
    #Use headless webdriver to fetch webpage
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('http://adesse.uvigo.es/data/avanzado.php')
    driver_wait = driver.implicitly_wait(25)

    seconds = random() * 5

    #Write data on the webpage
    try:
        for field, value in data.items():
            write_values_on_web_page(driver, field, value)
        driver.find_element_by_css_selector("input[type='submit'][name='buscar']").click()
        time.sleep((5+(random()*5)))

    #Determine the total number of sentences
        try:
            number_of_examples = int(driver.find_element_by_css_selector("form[id='busca_ejemplos']").text[:25].split()[1])
            if number_of_examples != 0:
    #A veces hay que picar un boton antes de ver los ejemplos pero no PASSa nada si no aparece
                try:
                    driver.find_element_by_css_selector("input[value='ejemplos']").click()
                except:
                    pass #No pasa nada si no aparece el boton de EJEMPLOS

    #Obtener todos los urls, picando siguiente y siguiente
                try:
                    url_list = get_all_urls_by_going_page_by_page(driver, seconds, number_of_examples)
    #Acceder cada url en url_list y extraer info y guardarla en excel
                    try:
                        download_all_info(driver=driver, url_list=url_list, verbo=data['verbo'], seconds=seconds, labels=labels, limited_number=limited_number)
    #Manage exceptions
                    except:
                        labels[1].text = "No hemos podido descargar sus oraciones."
                        labels[2].text = "Conection error or bad coding. Tuvimos problemas al entrar a las paginas para descargar las oraciones."
                except:
                    labels[1].text = "No hemos podido descargar sus oraciones."
                    labels[2].text = "Conection error or bad coding. Tuvimos problemas al conseguir la lista de links para descargar las oraciones."
            else:
                labels[1].text = "Se encontraron 0 ejemplos para tu búsqueda."
        except:
            labels[1].text = "Conection error or bad coding! Trata de nuevo!"
    except:
    #Manage exceptions with the mistakes in the input
        if field == "verbo" or field == "perifrasis":
            labels[1].text = "No hemos podido descargar sus oraciones."
            labels[2].text = "Revise que el verbo y el verbo auxiliar estén bien escritos."
        else:
            labels[1].text = "No hemos podido descargar sus oraciones."
            labels[2].text = f"Error when trying to select option '{value}' from the '{field}' menu."

    driver.quit()


if __name__ == "__main__":
    realizar_busqueda(data)
