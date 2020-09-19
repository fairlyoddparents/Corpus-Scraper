import kivy
kivy.require('1.10.1')

from kivy.app import App
from kivy.lang import Builder

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown
from kivy.clock import Clock
from functools import partial

from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from kivy.properties import NumericProperty

from crea_make_consulta_function import make_consulta
from adesse_buscar_function import realizar_busqueda
from coca_search_function import find_matching_strings

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition

with open("corpus_scraper_kivy_file.kv", encoding='utf8') as f:
    Builder.load_string(f.read())

class CapitalInput(TextInput):
    def insert_text(self, substring, from_undo=False):
        s = substring.upper()
        return super(CapitalInput, self).insert_text(s, from_undo=from_undo)

class ScrollableLabel(ScrollView):
    text = StringProperty('')

class DudasPopup(Popup):
    pass

class MenuSectionsCOCA(BoxLayout):
    pass

class ProgressScreenCREA(Screen):
    my_dudas_popup = DudasPopup()

    def make_search(self, *args):
        data={'texto': self.manager.ids.main_layout.ids.consulta.text,
              'autor': self.manager.ids.main_layout.ids.autor.text,
              'ano1': self.manager.ids.main_layout.ids.year1.text,
              'ano2': self.manager.ids.main_layout.ids.year2.text,
              'titulo': self.manager.ids.main_layout.ids.obra.text,
              'medio': self.manager.ids.main_layout.ids.todos.text,
              'pais': self.manager.ids.main_layout.ids.todos_paises.text,
              'tema': self.manager.ids.main_layout.ids.todos_temas.text
              }

        """if self.manager.ids.main_layout.ids.numero_de_oraciones_checkbox.active == True:
            limited_number = int(self.manager.ids.main_layout.ids.number_of_sentences.text)
        else:
            limited_number = None"""

        limited_number = int(self.manager.ids.main_layout.ids.number_of_sentences.text)
        progress_screen_all_labels = self.manager.ids.progress_screen_CREA.ids
        label_0 = progress_screen_all_labels.terminado_label

        label_1 = progress_screen_all_labels.links_result_label
        label_2 = progress_screen_all_labels.oraciones_result_label
        label_3 = progress_screen_all_labels.guardar_result_label
        label_4 = progress_screen_all_labels.terminado_result_label


        labels = [label_0, label_1, label_2, label_3, label_4]
        make_consulta(data=data, limited_number=limited_number, labels=labels)

    def on_enter(self):
        Clock.schedule_once(self.make_search, 0.5)

class ProgressScreenCOCA(Screen):
    my_dudas_popup = DudasPopup()

    def make_search(self, *args):
        log_in_info = {'email': self.manager.ids.COCA_login.ids.login_email.text,
                'password': self.manager.ids.COCA_login.ids.login_password.text}

        sectionsLabel_data = {'p': self.manager.ids.main_layout_coca.ids.consulta_COCA.text,
                              'sec1': self.manager.ids.main_layout_coca.ids.menu_1.ids.menu_2_button.text,
                              'sec2': self.manager.ids.main_layout_coca.ids.menu_3.ids.menu_2_button.text}

        sortLabel_data = {'sortBy': self.manager.ids.main_layout_coca.ids.sorting_menu_button.text,
                          'minfreq1': self.manager.ids.main_layout_coca.ids.minimum_menu_button.text,
                          'limfreq1': self.manager.ids.main_layout_coca.ids.minimum_checkbox.active,
                          'freq1': self.manager.ids.main_layout_coca.ids.minimum_number.text}

        optionsLabel_data = {'numhits': self.manager.ids.main_layout_coca.ids.hits_number.text,
                        'kh': self.manager.ids.main_layout_coca.ids.KWIC_menu_button.text,
                        'groupBy': self.manager.ids.main_layout_coca.ids.group_menu_button.text,
                        'whatshow': self.manager.ids.main_layout_coca.ids.display_menu_button.text,
                        'saveList': self.manager.ids.main_layout_coca.ids.save_menu_button.text}

        data = [sectionsLabel_data, sortLabel_data, optionsLabel_data]

        start_sentence_number = int(self.manager.ids.main_layout_coca.ids.start_coca.text)

        progress_screen_all_labels = self.manager.ids.progress_screen_COCA.ids
        label_0 = progress_screen_all_labels.terminado_label

        label_1 = progress_screen_all_labels.links_result_label
        label_2 = progress_screen_all_labels.oraciones_result_label
        label_3 = progress_screen_all_labels.guardar_result_label
        label_4 = progress_screen_all_labels.terminado_result_label


        labels = [label_0, label_1, label_2, label_3, label_4]
        find_matching_strings(data=data, log_in_info=log_in_info, labels=labels, start_sentence_number=start_sentence_number)

    def on_enter(self):
        Clock.schedule_once(self.make_search, 0.5)

class ProgressScreenADESSE(Screen):
    my_dudas_popup = DudasPopup()

    def make_search(self, *args):
        data = {'verbo': self.manager.ids.main_layout_adesse.ids.consulta_adesse.text,
                'voz': self.manager.ids.main_layout_adesse.ids.voz_menu_button.text,
                'tam': self.manager.ids.main_layout_adesse.ids.conjugacion_menu_button.text,
                'perifrasis': self.manager.ids.main_layout_adesse.ids.auxiliar_menu.text,
                'h_genero': self.manager.ids.main_layout_adesse.ids.tipo_texto_menu_adesse_button.text,
                'h_procedencia': self.manager.ids.main_layout_adesse.ids.pais_menu_adesse_button.text,
                'h_num_argumentos': self.manager.ids.main_layout_adesse.ids.actantes_menu_button.text,
                'FUNCION_S1': self.manager.ids.main_layout_adesse.ids.actantes_1.ids.funcion_sint_menu_button.text,
                'unidad1': self.manager.ids.main_layout_adesse.ids.actantes_1.ids.categoria_sint_menu_button.text,
                'animacion1': self.manager.ids.main_layout_adesse.ids.actantes_1.ids.animacion_menu_button.text,
                'orden1': self.manager.ids.main_layout_adesse.ids.actantes_1.ids.posicion_adesse_menu_button.text,
                'FUNCION_S2': self.manager.ids.main_layout_adesse.ids.actantes_2.ids.funcion_sint_menu_button.text,
                'unidad2': self.manager.ids.main_layout_adesse.ids.actantes_2.ids.categoria_sint_menu_button.text,
                'animacion2': self.manager.ids.main_layout_adesse.ids.actantes_2.ids.animacion_menu_button.text,
                'orden2': self.manager.ids.main_layout_adesse.ids.actantes_2.ids.posicion_adesse_menu_button.text,
                'FUNCION_S3': self.manager.ids.main_layout_adesse.ids.actantes_3.ids.funcion_sint_menu_button.text,
                'unidad3': self.manager.ids.main_layout_adesse.ids.actantes_3.ids.categoria_sint_menu_button.text,
                'animacion3': self.manager.ids.main_layout_adesse.ids.actantes_3.ids.animacion_menu_button.text,
                'orden3': self.manager.ids.main_layout_adesse.ids.actantes_3.ids.posicion_adesse_menu_button.text,
                }

        limitar_numero_adesse_checkbox = self.manager.ids.main_layout_adesse.ids.numero_de_oraciones_checkbox_adesse
        if limitar_numero_adesse_checkbox.active == True:
            limited_number = int(self.manager.ids.main_layout_adesse.ids.limitar_numero_adesse.text)
        else:
            limited_number = 0

        progress_screen_all_labels = self.manager.ids.progress_screen_ADESSE.ids
        label_0 = progress_screen_all_labels.terminado_label

        label_1 = progress_screen_all_labels.links_result_label
        label_2 = progress_screen_all_labels.oraciones_result_label
        label_3 = progress_screen_all_labels.guardar_result_label
        label_4 = progress_screen_all_labels.terminado_result_label


        labels = [label_0, label_1, label_2, label_3, label_4]
        realizar_busqueda(data=data, limited_number=limited_number, labels=labels)

    def on_enter(self):
        Clock.schedule_once(self.make_search, 0.5)

class HomeScreen(Screen):
    my_dudas_popup = DudasPopup()

class CREAScreen(Screen):
    my_dudas_popup = DudasPopup()

class COCA_LoginScreen(Screen):
    pass

class COCAScreen(Screen):
    pass

class Actantes(BoxLayout):
    pass

class ADESSEScreen(Screen):
    pass

class ScreenManagement(ScreenManager):
#Testing fuctions
    def lets_print_sth(self, consulta):
        print(consulta)

    def lets_print_more(self, consulta_2):
        print(consulta_2)

    def lets_inform(self, my_label):
        my_label.text += " ya vamos avanzando"

#Limpiar fuctions
    def make_another_search(self, terminado_label, links_result_label, oraciones_result_label, guardar_result_label, terminado_result_label):
        self.current = "home"

        terminado_label.text = ""
        links_result_label.text = "Procesando..."
        oraciones_result_label.text = ""
        guardar_result_label.text = ""
        terminado_result_label.text = ""

    def clean_textinput_fields(self, *argv):
        for arg in argv:
            arg.text = ""

    def clean_menus(self, *argv):
        for arg in argv:
            arg.text= "Menu"

    def reset_limitar_numbero_oraciones_option(self, my_number, my_checkbox):
        my_number.text = "200"
        my_checkbox.active = True

    def reset_start_from_sentence_option(self, my_number):
        my_number.text = "1"

    def reset_checkbox_min_freq_coca(self, my_checkbox):
        my_checkbox.active = False

    def reset_hits_minimum_number_textbox_coca(self, minimum, hits):
        minimum.text = "0"
        hits.text = "100"

screen_manager = ScreenManagement()

class CorpusScraper_Beta(App):
    def build(self):
        return screen_manager

if __name__ == '__main__':
    CorpusScraper_Beta().run()
