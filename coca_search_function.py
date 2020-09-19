from selenium import webdriver
from selenium.common.exceptions import WebDriverException

from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait

import time
from random import random
import re

import xlsxwriter

"""falta:
5. revisar que funcione"""

log_in_info = {'email': '',
        'password': '',}

sectionsLabel_data = {'p': 'pencil',
                      'sec1': '',
                      'sec2': ''}

sortLabel_data = {'sortBy': '',
                  'minfreq1': '',
                  'limfreq1': "",
                  'freq1': ""}

optionsLabel_data = {'numhits': "",
                'kh': '',
                'groupBy': '',
                'whatshow': '',
                'saveList': ""}

data = [sectionsLabel_data, sortLabel_data, optionsLabel_data]

def clean_html(html_text, concept_format):
    #Toma el html code del parrafo con la oracion y cambia primero las etiquetas que rodean a la palabra por FOONT
    #Despues elimina todas las etiquetas restantes y regresa el parrafo limpio
    paragraph_sin_font = re.sub(r'<.?b>', "FOONT", html_text)
    paragraph_sin_html = re.sub(r'<.*?>', "", paragraph_sin_font)

    paragraph = paragraph_sin_html.split('FOONT')

    txt = []

    #Crea una lista colocando las partes de paragraph alternando entre elementos
    #y concept format para usarlo en rich string
    for i, part in enumerate(paragraph):
        if i == 1:
            txt.append(concept_format)
        elif i != 0 and i/2 != i//2 and paragraph[i] != paragraph[-1]:
            txt.append(concept_format)
        if part == "": ###TESTING
            part = " "###TESTING
        txt.append(part)

    return txt

def check_field_not_empty(field, value):
    if value == True:
        return True
    elif value != None and value != "Menu" and value != "" and value != False:
        if value.strip() != "":
            if field == "limfreq1":
                if value.strip() != "10":
                    return True
            if field == "numhits":
                if value.strip() != "100":
                    return True
            else:
                return True

def fill_textinput_on_webpage(driver, field, value, seconds):
    element = driver.find_element_by_id(field)
    element.clear()
    element.send_keys(value)
    time.sleep(seconds)

def select_option_from_dropdown_menu(driver, field, value, seconds):
    #Sec1 and sec2 have one option already selected that's why we need to deselect it first
    if field == "sec1" or field == "sec2":
        select = Select(driver.find_element_by_id(field))
        select.deselect_all()
        select.select_by_visible_text(value)
    else:
        (Select(driver.find_element_by_id(field))).select_by_visible_text(value)
    time.sleep(seconds)

def fill_fields_on_webpage(driver, data, seconds):
    sectionsLabel_data = data[0]
    sortLabel_data = data[1]
    optionsLabel_data = data[2]

    #First: fill all the fields in the main and sectionsLabel sections
    driver.switch_to.default_content()
    driver.switch_to.frame('x1')
    driver.find_element_by_id('sectionsLabel').click()
    time.sleep(seconds)

    both_secs_active = []
    for field, value in sectionsLabel_data.items():
        if check_field_not_empty(field, value) == True:
            if field == "p":
                fill_textinput_on_webpage(driver, field, value, seconds)
            elif field == "sec1" or field == "sec2":
                select_option_from_dropdown_menu(driver, field, value, seconds)
                both_secs_active.append(True)

    #Second: fill all the fields in the sortLabel section
    if len(both_secs_active) == 2:
        pass
    else:
        driver.find_element_by_id('sortLabel').click()
        time.sleep(seconds)
    for field, value in sortLabel_data.items():
        if field == "limfreq1":
            if value == False:
                if sortLabel_data["sortBy"] == "RELEVANCE" or sortLabel_data['minfreq1'] == "MUT INFO":
                    driver.find_element_by_id('limfreq1').click() #When you choose RELEVANCE/MUT INFO this checkbox gets automatically checked
            else:
                if sortLabel_data["sortBy"] != "RELEVANCE" and sortLabel_data['minfreq1'] != "MUT INFO":
                    driver.find_element_by_id('limfreq1').click() #When you choose RELEVANCE/MUT INFO this checkbox gets automatically checked
            time.sleep(seconds)
        else:
            if check_field_not_empty(field, value) == True:
                if field == "freq1":
                    fill_textinput_on_webpage(driver, field, value, seconds)
                else:
                    select_option_from_dropdown_menu(driver, field, value, seconds)


    #Third: fill all the fields in the optionsLabel section
    driver.find_element_by_id('optionsLabel').click()
    time.sleep(seconds)
    for field, value in optionsLabel_data.items():
        if check_field_not_empty(field, value) == True:
            if field == "numhits":
                fill_textinput_on_webpage(driver, field, value, seconds)
            else:
                select_option_from_dropdown_menu(driver, field, value, seconds)

def log_in_function(driver, log_in_info, seconds):
    #Determine whether the user wants to log in
    complete_fields = []
    for field, value in log_in_info.items():
        complete_fields.append(check_field_not_empty(field, value))
    if complete_fields[0] == True and complete_fields[1] == True:
    #Click the button to enter the log in page
        driver.switch_to.frame('x1')
        driver.find_element_by_id('w_logged').click()

    #We switch to the frame that contains the texinputs
        driver.switch_to.default_content()
        driver.switch_to.frame('x4')

    #We write our log in information on the texinputs
        for field, value in log_in_info.items():
            element = driver.find_element_by_css_selector(f'input[name="{field}"]')
            element.clear()
            element.send_keys(value)
            time.sleep(seconds)

    #We click the send button
        driver.find_element_by_css_selector('input[name="B1"]').click()
        driver.switch_to.default_content()
        driver.switch_to.frame('controller')
        driver.find_element_by_id('link1').click()
        time.sleep(seconds)

def write_info_on_webpage_and_click_to_see_number_of_sentences(driver, log_in_info, data, seconds):
    #Log in
    log_in_function(driver, log_in_info, seconds)

    #Write data on webpage
    fill_fields_on_webpage(driver, data, seconds)
    driver.switch_to.default_content()
    driver.switch_to.frame('x1')
    driver.find_element_by_id("submit1").click()
    time.sleep(seconds)

    #Check whether we have to skip questions/surveys before moving to the result page
    driver.switch_to.default_content()
    driver.switch_to.frame('x2')
    try:
    #Check whether you can see the number of examples or whether we have to click other buttons first
        driver.find_element_by_xpath('//*[@id="zabba"]/table[2]/tbody/tr[2]/td[4]/font')
    except:
    #Sometimes we have to answer a survey before seeing the examples
        try:
        #Answer the questions
            driver.find_element_by_xpath('//*[@id="zabba"]/div/table/tbody/tr/td/p[3]/a[2]').click()
            time.sleep(seconds)
            driver.find_element_by_xpath('//*[@id="zabba"]/div/table/tbody/tr/td/p[3]/a').click()
            time.sleep(seconds)
            driver.find_element_by_xpath('//*[@id="zabba"]/div/table/tbody/tr/td/p[3]/a[1]').click()
            time.sleep(seconds)

        #Click search again
            driver.switch_to.default_content()
            driver.switch_to.frame('x1')
            driver.find_element_by_id("submit1").click()
            time.sleep(seconds)
        except:
            pass
        #Sometimes we have to skip the ad about premium accounts
        ##TESTING no recuerdo si esto es en frame x2 pero si si hay que ponerle que cambie a ese frame
        try:
            driver.find_element_by_xpath('//*[@id="showLink"]/td/a').click()
            time.sleep(seconds)
        except:
            pass

def determine_number_of_pages_to_scrape(number_of_examples, start_sentence_number):
    total_pages = number_of_examples//100
    start_page = 0

    if start_sentence_number != 1 and start_sentence_number != 0 and number_of_examples >= start_sentence_number:
        start_page += ((start_sentence_number//100)*1)
        start_sentence_number -= ((start_page*100) - 1)
    else:
        start_sentence_number = 0
    """If start_sentence_number > number_of_examples print(We started downloading from sentence 1 since the sentence you wanted did't exist)"""#TESTING

    return start_page, start_sentence_number

def click_to_see_next_page(driver, seconds):
    try:
    #Click next
        driver.switch_to.default_content()
        driver.switch_to.frame('x3')
        next_button = driver.find_element_by_css_selector('#resort > table > tbody > tr > td > a:nth-child(11)').click()
        time.sleep((5+(random()*5)))
    #If we cannot do it
    except:
    #Click FREQUENCY
        driver.switch_to.default_content()
        driver.switch_to.frame('controller')
        driver.find_element_by_id('link2').click()
        driver.switch_to.default_content()
        time.sleep(seconds)

    #Click again the button to see examples to reload the page
        driver.switch_to.default_content()
        driver.switch_to.frame('x2')
        driver.find_element_by_xpath('//*[@id="zabba"]/table[2]/tbody/tr[2]/td[3]/a').click()
        time.sleep(seconds)

    #Try to click next again
        driver.switch_to.default_content()
        driver.switch_to.frame('x3')
        next_button = driver.find_element_by_css_selector('#resort > table > tbody > tr > td > a:nth-child(11)').click()
        time.sleep((5+(random()*5)))

def create_excel_file(verbo, seconds):
    #Create excel file to save the info on
    workbook = xlsxwriter.Workbook(f'{verbo}_{str(seconds)[-5:]}_data.xlsx')
    worksheet = workbook.add_worksheet('sentences')

    #add headers
    headers = ['Sentence', 'Year', 'Author', 'Title', 'Source', 'Publication info']
    header_format = workbook.add_format({'bold':True})
    worksheet.write_row('A1', headers, header_format)

    #Create formats
    general_format = workbook.add_format({'text_wrap':1, 'valign':'top'})
    url_format = workbook.add_format({'valign':'top'})
    year_format = workbook.add_format({'text_wrap':1, 'align':'left', 'valign':'top'})
    concept_format = workbook.add_format({'bold':True, 'font_color':'#8b1728', 'italic':True, 'underline':True})

    formats = [general_format, url_format, year_format, concept_format]

    #Set column with formats
    worksheet.set_column('A:A', 70, general_format)
    worksheet.set_column('D:D', 20, general_format)
    worksheet.set_column('E:E', 20, general_format)
    worksheet.set_column('F:F', 25, general_format)

    return workbook, worksheet, formats

def download_all_info(driver, seconds, excel, start_page, start_sentence_number, verbo):
    workbook = excel[0]
    worksheet = excel[1]
    formats = excel[2]
    row_number = excel[3]

    for i in range(start_page):
        click_to_see_next_page(driver, seconds)

    for page in range(2):
    #Get all the links on page
        driver.implicitly_wait(35)
        driver.switch_to.default_content()
        driver.switch_to.frame('x3')
        time.sleep(10)
        all_elements_in_page = driver.find_elements_by_xpath("//td[contains(@id,'showCell_1_')]")

        for element in all_elements_in_page[start_sentence_number:]:
    #Click the link to see the example
            #We are willing to wait up to 35 seconds for the sentence
            driver.implicitly_wait(35)
            driver.switch_to.default_content()
            driver.switch_to.frame('x3')
            url_element = element.find_element_by_css_selector('a')
            url_element.click()
            time.sleep((5+(random()*5)))

    #Download the info
            driver.switch_to.default_content()
            driver.switch_to.frame('x4')

            paragraph = driver.find_element_by_xpath('/html/body/p[2]').get_attribute('innerHTML')

            #We reduce the amount of time we are willing to wait because some of this element may not appear and that's OK
            driver.implicitly_wait(1)
            try:
                year = driver.find_element_by_xpath('//*[@id="w_date"]//ancestor::td/following-sibling::td').text
            except:
                year = ""
            try:
                publication = driver.find_element_by_xpath('//*[@id="w_pubInfo"]//ancestor::td/following-sibling::td').text
            except:
                publication = ""
            try:
                title = driver.find_element_by_xpath('//*[@id="w_title"]//ancestor::td/following-sibling::td').text
            except:
                title = ""
            try:
                author = driver.find_element_by_xpath('//*[@id="w_author"]//ancestor::td/following-sibling::td').text
            except:
                author = ""
            try:
                source = driver.find_element_by_xpath('//*[@id="w_source"]//ancestor::td/following-sibling::td').text
            except:
                source = ""

            information = [paragraph, year, author, title, source, publication]

    #Save the info in an excel file
            save_info_in_excel_file(seconds, workbook, worksheet, formats, row_number, information)
            row_number += 1

    #Return to the list of examples to click the next one
            driver.switch_to.default_content()
            driver.switch_to.frame('controller')
            return_button = driver.find_element_by_xpath('//*[@id="link3"]').click()
            time.sleep((random()*5))

    #Go to the next page
        click_to_see_next_page(driver, seconds)
    labels[1].text = "Listo."
    labels[2].text = "Listo."
    labels[3].text = 'Listo.'
    labels[0].text = "Terminado."
    labels[4].text = f"Busca el archivo {verbo}_data.xlsx en tu computadora."

def save_info_in_excel_file(seconds, workbook, worksheet, formats, row_number, information):
    general_format = formats[0]
    url_format = formats[1]
    year_format = formats[2]
    concept_format = formats[3]

    html_text = information[0]
    year = information[1]
    author = information[2]
    title = information[3]
    source = information[4]
    publication = information[5]

    #Separate html_text to add bold letters to target word before writing it on the excel file
    txt = clean_html(html_text, concept_format)

    #Write info on excel file
    #worksheet.write_string(f'A{row_number}', paragraph, general_format)
    worksheet.write_rich_string(f'A{row_number}', *txt)
    worksheet.write(f'B{row_number}', year, year_format)
    worksheet.write(f'C{row_number}', author, general_format)
    worksheet.write(f'D{row_number}', title, general_format)
    worksheet.write(f'E{row_number}', source, general_format)
    worksheet.write(f'F{row_number}', publication, general_format)

def find_matching_strings(data=None, log_in_info=None, labels=None, start_sentence_number=0):
    #Use browser to fetch webpage
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://www.english-corpora.org/coca/')
    driver_wait = driver.implicitly_wait(25)

    seconds = random() * 5
    time.sleep(10)

    try:
        write_info_on_webpage_and_click_to_see_number_of_sentences(driver, log_in_info, data, seconds)

        try:
        #Determine the total number of examples, pages, and pages to scrape
            driver.switch_to.default_content()
            driver.switch_to.frame('x2')
            number_of_examples = int(driver.find_element_by_xpath('//*[@id="zabba"]/table[2]/tbody/tr[2]/td[4]/font').text)
            start_page, start_sentence_number = determine_number_of_pages_to_scrape(number_of_examples, start_sentence_number)

        #Click a button to see the list with sentences
            driver.find_element_by_xpath('//*[@id="zabba"]/table[2]/tbody/tr[2]/td[3]/a').click()
            time.sleep(10)

        #Create excel file
            workbook, worksheet, formats = create_excel_file(data[0]['p'], seconds)
            row_number = 2
            excel = [workbook, worksheet, formats, row_number]

        #Download info
            try: ####TESTING
                download_all_info(driver, seconds, excel, start_page, start_sentence_number, data[0]['p']) ####TESTING
            except:####TESTING
                try:
                    driver.switch_to.default_content()
                    driver.switch_to.frame('x4')
                    driver.find_element_by_xpath("/html/body[contains(text(), 'copyright')]")
                    labels[1].text = "Has alcanzado tu limite de descarga de 200 oraciones por día en este corpus. Intenta mañana."
                    labels[2].text = 'Incompleto.'
                    labels[3].text = f"Revisa el archivo {data[0]['p']}_{str(seconds)[-5:]}_data.xlsx para ver las oraciones que logramos descargar."
                except:
                    labels[1].text = "Hubo un error en la página. El administrador del corpus ha sido notificado. Intente de nuevo."
                    labels[2].text = "Incompleto."
                    labels[3].text = f"Revisa el archivo {data[0]['p']}_{str(seconds)[-5:]}_data.xlsx para ver las oraciones que logramos descargar"
            finally:
                workbook.close()####TESTING
                driver.quit()####TESTING
        except:
        #Maybe there are no results
            labels[1].text = "Oops! No hay resultados para tu búsqueda!"
            driver.quit()####TESTING
    except:
        labels[1].text = "Error al realizar tu búsqueda. Esto se puede deber a problemas de conexión de internet o bad coding."
        driver.quit()####TESTING


if __name__ == "__main__":
    find_matching_strings(data, log_in_info, None, 0)
