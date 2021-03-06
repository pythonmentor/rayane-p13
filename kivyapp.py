from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior 
from kivy.uix.image import Image  
from kivy.properties import ObjectProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.togglebutton import ToggleButton
from kivy.app import App
from functools import partial
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.network.urlrequest import UrlRequest
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
import urllib.parse
import functools
from kivy.uix.popup import Popup
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import json

class ViewManager(Screen):
    PAGE = 0
    REQUEST_REGION = ""
    REQUEST_MATCHES = ""
    USER = None
    MONEY = None
    SPORT_CHOSEN = ""
    def __init__(self, **kwargs):
        super(ViewManager, self).__init__(**kwargs)
        self.sport_page = None
        self.region_page = None
        self.league_page = None
        self.match_page = None
        self.bet_page = None
        self.winner_page = None
        self.submit = None
        self.backward = None
        self.create_view(None)

    def create_view(self, choice):
        if ViewManager.PAGE == 0:
            self.update_money()
            self.backward = GoBackward(self.previous_view)
            self.sport_page = SportPage(self.create_view, self.bets_view, self.winners_view)
            self.ids.pages.add_widget(self.sport_page)
            ViewManager.PAGE += 1
        elif ViewManager.PAGE == 1:
            self.ids.pages.remove_widget(self.sport_page)
            self.region_page = RegionPage(choice)
            self.submit = SubmitButton(self.create_view)
            self.ids.pages.add_widget(self.region_page)
            self.ids.bottom.add_widget(self.submit)
            self.ids.bottom.add_widget(self.backward)
            ViewManager.PAGE += 1
        elif ViewManager.PAGE == 2 and self.REQUEST_REGION != "":
            self.ids.pages.remove_widget(self.region_page)
            self.league_page = LeaguePage()
            self.ids.pages.add_widget(self.league_page)
            ViewManager.PAGE += 1
        elif ViewManager.PAGE == 2 and self.REQUEST_REGION == "":
            pop = Popup(title='Invalid Request',
                  content=Label(text='Choisissez au moins une région'),
                  size_hint=(None, None), size=(250, 250))
            pop.open()
        elif ViewManager.PAGE == 3 and self.REQUEST_MATCHES != "":
            self.ids.pages.remove_widget(self.league_page)
            self.ids.bottom.remove_widget(self.submit)
            match_manager = MatchPage()
            self.match_page = match_manager.create_grid_matches()
            self.ids.pages.add_widget(self.match_page)
            ViewManager.PAGE += 1
        elif ViewManager.PAGE == 3 and self.REQUEST_MATCHES == "":
            pop = Popup(title='Invalid Request',
                  content=Label(text='Choisissez au moins un championnat'),
                  size_hint=(None, None), size=(250, 250))
            pop.open()
        elif ViewManager.PAGE == 5:
            self.ids.pages.remove_widget(self.sport_page)
            self.bet_page = BetPage()
            self.ids.pages.add_widget(self.bet_page)
            self.ids.bottom.add_widget(self.backward)
        elif ViewManager.PAGE == 6:
            self.ids.pages.remove_widget(self.sport_page)
            self.winner_page = WinnerPage()
            self.ids.pages.add_widget(self.winner_page)
            self.ids.bottom.add_widget(self.backward)


    def previous_view(self):
        if ViewManager.PAGE == 2:
            self.ids.pages.remove_widget(self.region_page)
            self.ids.bottom.remove_widget(self.submit)
            self.ids.bottom.remove_widget(self.backward)
            self.ids.pages.add_widget(self.sport_page)
            ViewManager.REQUEST_REGION = ""
            ViewManager.PAGE -= 1
        elif ViewManager.PAGE == 3:
            self.ids.pages.remove_widget(self.league_page)
            self.ids.pages.add_widget(self.region_page)
            ViewManager.REQUEST_MATCHES = ""
            ViewManager.PAGE -= 1
        elif ViewManager.PAGE == 4:
            self.ids.pages.remove_widget(self.match_page)
            self.ids.pages.add_widget(self.league_page)
            self.ids.bottom.add_widget(self.submit)
            ViewManager.PAGE -= 1
        elif ViewManager.PAGE == 5:
            self.ids.pages.remove_widget(self.bet_page)
            self.ids.pages.add_widget(self.sport_page)
            self.ids.bottom.remove_widget(self.backward)
            ViewManager.PAGE = 1
        elif ViewManager.PAGE == 6:
            self.ids.pages.remove_widget(self.winner_page)
            self.ids.pages.add_widget(self.sport_page)
            self.ids.bottom.remove_widget(self.backward)
            ViewManager.PAGE = 1

    def bets_view(self):
        ViewManager.PAGE = 5
        self.create_view(None)

    def winners_view(self):
        ViewManager.PAGE = 6
        self.create_view(None)

    def update_money(self):
        self.ids.amount.text = "Solde: " + str(ViewManager.MONEY)

    def logout(self):
        BookMarket.DISPLAY.current = "login"
        while self.PAGE != 1:
            self.previous_view()


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class SelectableLabel(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SelectableLabel, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if ViewManager.PAGE == 2:
            arg_to_add = "region=" + urllib.parse.quote(rv.data[index]["text"])
            if is_selected:
                ViewManager.REQUEST_REGION += arg_to_add + "&"
                print(ViewManager.REQUEST_REGION)

            else:
                args = ViewManager.REQUEST_REGION.split("&")
                for arg in args:
                    if arg_to_add == arg:
                        args.remove(arg)
                ViewManager.REQUEST_REGION = "&".join(args)
        elif ViewManager.PAGE == 3:
            arg_to_add = "competition=" + urllib.parse.quote(rv.data[index]["text"])
            if is_selected:
                ViewManager.REQUEST_MATCHES += arg_to_add + "&"
                print(ViewManager.REQUEST_MATCHES)

            else:
                args = ViewManager.REQUEST_MATCHES.split("&")
                for arg in args:
                    if arg_to_add == arg:
                        args.remove(arg)
                ViewManager.REQUEST_MATCHES = "&".join(args)

class SubmitButton(ButtonBehavior, Image):
    def __init__(self, next_view, **kwargs):
        super(SubmitButton, self).__init__(**kwargs)
        self.next_view = next_view

    def on_press(self):
        self.next_view(None)

class GoBackward(ButtonBehavior, Image):
    def __init__(self, previous_view, **kwargs):
        super(GoBackward, self).__init__(**kwargs)
        self.previous_view = previous_view

    def on_press(self):
        self.previous_view()

class Disconnect(ButtonBehavior, Image):
    pass

class WinnerPage(GridLayout):
    def __init__(self,**kwargs):
        super(WinnerPage, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        request_bets = UrlRequest("http://127.0.0.1:5000/winners", self.parse_json)

    def parse_json(self, req, result):
        place = 1
        for value in result["winners"]:
            description = value["nom"] + " est " + str(place) + " avec un total de " + str(value["argent"])
            winner = Label(text=description, size_hint_y= None)
            self.add_widget(winner)
            place += 1

class Bet(GridLayout):
    def __init__(self, color, **kwargs):
        self.color = color
        super(Bet, self).__init__(**kwargs)


class BetPage(GridLayout):
    def __init__(self,**kwargs):
        super(BetPage, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        request_bets = UrlRequest("http://127.0.0.1:5000/{}/bets".format(ViewManager.USER), self.parse_json)

    def parse_json(self, req, result):
        for value in result["bets"]:
            team_chosen = "Domicile" if value["equipe_pariee"] == 1 else ("Exterieur" if value["equipe_pariee"] == 2 else "Nul")
            if value["match_infos"]["resultat_id"] == 1:
                result = value["equipe_domicile"]
            if value["match_infos"]["resultat_id"] == 2:
                result = value["equipe_exterieure"]
            if value["match_infos"]["resultat_id"] == 3:
                result = "Nul"
            else:
                result = "Match pas encore joué"

            if value["match_infos"]["resultat_id"] != value["equipe_pariee"] and value["verifie"] == 1:
                bet = Bet((0.6, 0, 0, 1))
                bet.ids.earning.text = "   Pertes: -" + str(value["mise"])
            elif value["verifie"] == 1:
                bet = Bet((0, 0.6, 0, 1))
                bet.ids.earning.text = "  Gains: +" + str(value["mise"]*float(value["cote"]))
            else:
                bet = Bet((0.500, 0.500, 0.500, 1))
                bet.ids.earning.text = "   Gains potentiels: +" + str(value["mise"]*float(value["cote"]))

            bet.ids.title.text = value["match_infos"]["equipe_domicile"] + " vs " + value["match_infos"]["equipe_exterieure"]
            bet.ids.date.text = "   Date match: " + value["match_infos"]["date_affrontement"]
            bet.ids.bet.text = "   Pari: " + str(value["mise"]) + " parié sur " + team_chosen + " avec une cote de " + str(value["cote"])
            bet.ids.result.text = "   " + result

            self.add_widget(bet)

class Match(GridLayout):
    def bet(self, button_text):
        if button_text == "Domicile":
            input_amount = self.ids.input_home.text
            odd = self.ids.bet_home.text.split()[0]
            team_selected = 1
        elif button_text =="Extérieur":
            input_amount = self.ids.input_away.text
            odd = self.ids.bet_away.text.split()[0]
            team_selected = 2
        elif button_text == "Nul":
            input_amount = self.ids.input_draw.text
            odd = self.ids.bet_draw.text.split()[0]
            team_selected = 3
        
        if input_amount:
            if input_amount.isdigit():
                input_amount = int(input_amount)
                if ViewManager.MONEY >= input_amount:
                    headers = {"Content-Type": "application/json"}
                    params = json.dumps({"bet": input_amount, "odd":odd, "user_id": ViewManager.USER, "match_id": self.id, "team_selected": team_selected})
                    req = UrlRequest('http://127.0.0.1:5000/bets', on_success=self.update_player,
                req_body=params, req_headers=headers)
                else:   
                    self.bet_too_high()
            else:
                self.not_a_number()
        else:
            self.empty_input()

    def update_player(self, req, result):
        if "succes_message" in result:
            ViewManager.MONEY -= result["bet"]
            LoginWindow.PM.update_money()
            self.request_answer(result["succes_message"])
        elif "error_message" in result:
            self.request_answer(result["error_message"])

    def request_answer(self, message):
        pop = Popup(title='Invalid Form',
                      content=Label(text=message),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

    def bet_too_high(self):
        pop = Popup(title='Invalid Form',
                      content=Label(text="Argent insuffisant"),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

    def not_a_number(self):
        pop = Popup(title='Invalid Form',
                      content=Label(text="La mise doit être un nombre"),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

    def empty_input(self):
        pop = Popup(title='Invalid Form',
                      content=Label(text="Champ vide"),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

class MatchPage(GridLayout):
    def __init__(self,**kwargs):
        super(MatchPage, self).__init__(**kwargs)
        self.bind(minimum_height=self.setter('height'))
        
    def add_to_view(self, req, result):
        for value in result["matches"]:
            tv = value["tv"] if value["tv"] != None else ""
            match = Match()
            match.id = value["id"]
            match.ids.title.text = value["competition"] + "  " + value["date"] + "  " + tv
            match.ids.bet_home.text = value["cote_dom"] + " " + value["domicile"]
            match.ids.bet_draw.text = value["cote_nul"] + " Nul"
            match.ids.bet_away.text = value["cote_ext"] + " " + value["exterieur"]
            if value["cote_nul"] == "None":
                match.remove_widget(match.ids.draw)
            self.add_widget(match)

    def create_grid_matches(self):
        print(ViewManager.REQUEST_MATCHES)
        requestMatches = UrlRequest('http://127.0.0.1:5000/rencontres?' + ViewManager.REQUEST_MATCHES, self.add_to_view)
        return self

class LeaguePage(RecycleView):
    def __init__(self, **kwargs):
        super(LeaguePage, self).__init__(**kwargs)
        self.data = []
        requestLeagues = UrlRequest("http://127.0.0.1:5000/rencontres/{}/competitions?".format(ViewManager.SPORT_CHOSEN) + ViewManager.REQUEST_REGION, self.parse_json)

    def parse_json(self, req, result):
        self.data = []
        for value in result["competitions"]:
            self.data.append({"text" : value})

class RegionPage(RecycleView):
    def __init__(self, sport, **kwargs):
        super(RegionPage, self).__init__(**kwargs)
        self.data = []
        ViewManager.REQUEST_REGION = ""
        ViewManager.SPORT_CHOSEN = sport
        requestRegions = UrlRequest('http://127.0.0.1:5000/rencontres/{}/regions'.format(sport), self.parse_json)


    def parse_json(self, req, result):
        self.data = []
        for value in result["regions"]:
            self.data.append({"text": value, "on_press": functools.partial(self.add_arg_to_request, value)})
            self.url_request_regions = req.url

    def add_arg_to_request(self, req_arg):
        #print(self.view_adapter.get_visible_view(5))
        arg_to_search = "region="
        """
        elif self.PAGE == 3:
            arg_to_search = "competition="
        """

        req_arg = urllib.parse.quote(req_arg) 
        if req_arg in ViewManager.REQUEST_REGION:
            args = ViewManager.REQUEST_REGION.split("&")
            for arg in args:
                if req_arg in arg:
                    args.remove(arg)
            ViewManager.REQUEST_REGION = "&".join(args)
        else:
            if ViewManager.REQUEST_REGION:
                ViewManager.REQUEST_REGION += "&" + arg_to_search + req_arg
            else:
                ViewManager.REQUEST_REGION += arg_to_search + req_arg
        print(ViewManager.REQUEST_REGION)


class SportPage(RecycleView):
    def __init__(self, next_view, bets_view, winners_view, **kwargs):
        super(SportPage, self).__init__(**kwargs)
        self.data = []
        self.next_view = next_view
        self.bets_view = bets_view
        self.winners_view = winners_view
        self.request_json(None)

    def request_json(self, arg):
        requestCompetition = UrlRequest('http://127.0.0.1:5000/sports', self.parse_json)

    def parse_json(self, req, result):
        self.data = []
        for value in result["sports"]:
            self.data.append({"text" : value['nom'],"name" : value["nom"], "on_press" : functools.partial(self.next_view, value['nom'])})
            self.url_request_sport = req.url
        self.data.append({"text" : "Historique paris", "name" : "historique", "on_press" : functools.partial(self.bets_view)})
        self.data.append({"text" : "Plus gros gagnants", "name" : "gagnants", "on_press" : functools.partial(self.winners_view)})

class LoginWindow(Screen):
    PM = None

    def login(self):
        username = self.ids.name.text.strip()
        password= self.ids.password.text.strip()
        if not username or not password:
            self.invalid_form()     
        else:
            params = json.dumps({"username": username, "password": password})
            headers = {"Content-Type": "application/json"}
            req = UrlRequest('http://127.0.0.1:5000/login', on_success=self.connected,
                on_failure=self.wrong_request, req_body=params, req_headers=headers)

    def connected(self, req, result):
        ViewManager.PAGE = 0
        ViewManager.USER = result["user_id"]
        ViewManager.MONEY = result["money"]
        LoginWindow.PM = ViewManager(name="bets")
        BookMarket.DISPLAY.add_widget(LoginWindow.PM)
        self.ids.name.text = ""
        self.ids.password.text = ""
        BookMarket.DISPLAY.current = "bets"


    def wrong_request(self, req, result):
        pop = Popup(title='Invalid Form',
                      content=Label(text=result["error_message"]),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

    def register(self):
        self.ids.name.text = ""
        self.ids.password.text = ""
        BookMarket.DISPLAY.current = "register"

    def invalid_form():
        pop = Popup(title='Invalid Form',
                      content=Label(text='Veuillez remplir tous les champs'),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

class RegisterWindow(Screen):
    def create_account(self):
        username = self.ids.name.text.strip()
        password= self.ids.password.text.strip()
        if not username or not password:
            self.invalid_form()
        else:
            params = json.dumps({"username": username, "password": password})
            headers = {"Content-Type": "application/json"}
            req = UrlRequest('http://127.0.0.1:5000/users', on_success=self.display_message,
                on_failure=self.display_message, req_body=params, req_headers=headers)

    def display_message(self, req, result):
        if "succes_message" in result:
            self.request_answer(result["succes_message"])
        elif "error_message" in result:
            self.request_answer(result["error_message"])

    def login(self):
        self.ids.name.text = ""
        self.ids.password.text = ""
        BookMarket.DISPLAY.current = "login"

    def invalid_form(self):
        pop = Popup(title='Invalid Form',
                      content=Label(text='Veuillez remplir tous les champs'),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

    def request_answer(self, message):
        pop = Popup(title='Invalid Form',
                      content=Label(text=message),
                      size_hint=(None, None), size=(250, 250))

        pop.open()

class WindowManager(ScreenManager):
    pass

class BookMarket(App):
    DISPLAY = WindowManager()
    def build(self):
        screens = [LoginWindow(name="login"), RegisterWindow(name="register")]
        for screen in screens:
            BookMarket.DISPLAY.add_widget(screen)
        BookMarket.DISPLAY.current = "login" 
        return BookMarket.DISPLAY
 
BookMarket().run()