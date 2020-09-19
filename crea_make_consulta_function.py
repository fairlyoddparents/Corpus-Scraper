from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By

import time
from random import random
import re

import xlsxwriter

data = {'texto': 'canción',
        'autor': '',
        'ano1': '1984',
        'ano2': '',
        'titulo': '',
        'medio': '',
        'pais': 'España',
        'tema': ''
        }


def check_field_not_empty(value):
    if isinstance(value, int):
         return True
    elif value != None:
        if value.strip() != "" and value.strip().lower() != "menu":
            return True

def split_html(html_text):
    paragraph_sin_font = re.sub(r'<img.*?>', "FOONT", html_text)
    paragraph_sin_html = re.sub(r'<.*?>', "", paragraph_sin_font)

    return paragraph_sin_html

def create_excel_file(name, seconds):
    workbook = xlsxwriter.Workbook(f'{name}_{str(seconds)[-5:]}_data.xlsx')
    worksheet = workbook.add_worksheet('sentences')

    #add headers
    headers = ['Sentence', 'Url', 'Year', 'Author', 'Title', 'Country', 'Topic', 'Publication']
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
    worksheet.set_column('H:H', 25, general_format)

    formats = [general_format, url_format, year_format, concept_format]
    return workbook, worksheet, formats

def write_values_on_web_page(driver, field, value):
    if field == "medio" or field == "pais" or field == "tema":
        select = Select(driver.find_element_by_name(field))
        select.deselect_all()
        select.select_by_visible_text(value)
    else:
        element = driver.find_element_by_name(field)
        element.clear()
        element.send_keys(value)

def click_recuperar_to_see_sentences(driver, labels=None):
    try:
        number_of_sentences = driver.find_elements_by_css_selector("td[width='72%']")[1].text
        try:
            driver.find_element_by_css_selector("input[value='Recuperar']").click()
            try:
                generic_url = driver.find_element_by_css_selector("a[title*='1']").get_attribute('href')
                labels[1].text = "Listo"
                return generic_url, int(number_of_sentences.split()[0])
            except:
                labels[1].text = "Demasiados documentos. Sólo se pueden ver estadísticas. Refine su búsqueda."
                return False, False
        except:
            labels[1].text = "Demasiados documentos. No se pueden ver ni las estadísticas. Refine su búsqueda."
            return False, False
    except:
        labels[1].text = "No existen casos para esta consulta o tu consulta está vacía o tu conexión de internet está muy lenta."
        return False, False

def download_senteces_and_their_information(driver, active_url, labels=None):
    driver.get(active_url)

    #Get sentence
    try:
        try:
            paragraph = driver.find_element_by_xpath("//img[@alt='[Anterior]']/ancestor::p").get_attribute('innerHTML')
            paragraph_sin_html = split_html(paragraph)
        except:
            try:
                paragraph = driver.find_element_by_xpath("//img[@alt='[Anterior]']/ancestor::td").get_attribute('innerHTML')
                paragraph_sin_html = split_html(paragraph)
            except:
                labels[2].text = 'Bad coding, I couldnt find the paragraph!'
    except:
        labels[2].text = 'Bad coding, I couldnt find the paragraph!'

    #Get other information about sentence
    try:
        año = driver.find_element_by_xpath("/html/body/blockquote/table[3]/tbody/tr[1]/td[2]").text
        autor = driver.find_element_by_xpath("/html/body/blockquote/table[3]/tbody/tr[2]/td[2]").text
        titulo = driver.find_element_by_xpath("/html/body/blockquote/table[3]/tbody/tr[3]/td[2]").text
        pais = driver.find_element_by_xpath("/html/body/blockquote/table[3]/tbody/tr[4]/td[2]").text
        tema = driver.find_element_by_xpath("/html/body/blockquote/table[3]/tbody/tr[5]/td[2]").text
        publicacion = driver.find_element_by_xpath("/html/body/blockquote/table[3]/tbody/tr[6]/td[2]").text
    except:
        labels[2].text = 'Revisa que tu conexión de internet se encuentre estable.'

    sentence_information = [paragraph_sin_html, año, autor, titulo, pais, tema, publicacion, active_url]
    return sentence_information

def write_sentences_on_workbook(workbook, worksheet, formats, sentence_information, row_number):
    paragraph = sentence_information[0]
    año = sentence_information[1]
    autor = sentence_information[2]
    titulo = sentence_information[3]
    pais = sentence_information[4]
    tema = sentence_information[5]
    publicacion = sentence_information[6]
    active_url = sentence_information[7]

    general_format = formats[0]
    url_format = formats[1]
    year_format = formats[2]
    concept_format = formats[3]

    #Split paragraph in three to add format
    paragraph_divided = paragraph.split("FOONT")

    if paragraph_divided[0] == "": ####TESTING
        paragraph_divided[0] = " " ####TESTING

    if paragraph_divided[2] == "": ####TESTING
        paragraph_divided[2] = " " ####TESTING

    #Write everything in file
    worksheet.write_rich_string(f'A{row_number}', paragraph_divided[0], concept_format, paragraph_divided[1], paragraph_divided[2])
    worksheet.write_string(f'B{row_number}', active_url, url_format)
    worksheet.write(f'C{row_number}', año, year_format)
    worksheet.write(f'D{row_number}', autor, general_format)
    worksheet.write(f'E{row_number}', titulo, general_format)
    worksheet.write(f'F{row_number}', pais, general_format)
    worksheet.write(f'G{row_number}', tema, general_format)
    worksheet.write(f'H{row_number}', publicacion, general_format)

def make_consulta(data=None, limited_number=None, labels=None, *args):
    #open browser and fetch webpage
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('http://corpus.rae.es/creanet.html')
    driver_wait = driver.implicitly_wait(25)

    seconds = random()*5

    time.sleep(seconds)
    #use browser to write the values on the page's fields and click search
    for field, value in data.items():
        if check_field_not_empty(value):
            write_values_on_web_page(driver, field, value)
    time.sleep((5+(random()*5)))
    driver.find_element_by_css_selector("input[type='submit']").click()
    time.sleep((5+(random()*5)))
    #Click recuperar
    #1. Make sure that the button recuperar is there
    #2. Click it
    #3. Make sure that driver got to the page where sentences are listed

    #If these three things don't happen:
        #number_of_sentences == False
    #If everything goes according to plan we get the generic_url and the number of sentences available

    generic_url, number_of_sentences = click_recuperar_to_see_sentences(driver, labels)
    time.sleep((5+(random()*5)))
    #Download sentences and create excel file
    #This means that the driver was able to get to the page where all sentences are listed
    if number_of_sentences != False:
        if check_field_not_empty(limited_number) and limited_number < number_of_sentences:
            number_of_sentences = limited_number
        workbook, worksheet, formats = create_excel_file(data['texto'], seconds)

        row_number = 1


    #Go url by url fetching info and writing it on the worksheet
        try:
            for i in range(number_of_sentences):
                row_number += 1
                formated_string = f'iniItem={i}'
                active_url = generic_url.replace("iniItem=0", formated_string)
                sentence_information = download_senteces_and_their_information(driver, active_url, labels)
                write_sentences_on_workbook(workbook, worksheet, formats, sentence_information, row_number)
                time.sleep((5+(random()*5)))
            workbook.close()
            labels[2].text = "Listo"
            labels[3].text = 'Listo'
            labels[0].text = "Terminado"
            labels[4].text = f"Busca el archivo {data['texto']}_{str(seconds)[-5:]}_data.xlsx en tu computadora"
        except:
            labels[1].text = "Error. Comprueba tu conexión de internet!"
    driver.quit()





if __name__ == "__main__":
    make_consulta(data=data)
