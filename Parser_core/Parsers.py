import re
from bs4 import BeautifulSoup


def return_parser(source):
    if source == 'PMC':
        parser = PMC_parser()
    elif source == 'PubMed':
        parser = PubMed_parser()
    return parser


class PubMed_parser:
    def __init__(self):
        self.record = Data_record(ID=None, TI=None, AB=None, AU=None, AD=None)

    def parce(self, page, page_id):
        """Парсим страницу PubMed"""
        self.record.clear()
        html = BeautifulSoup(page.text, 'lxml')

        self.record['ID'] = page_id

        # получаем основной текст записи
        full_text = ''
        abstract = html.find('div', class_='abstract')
        if abstract:
            if abstract.find('p'):
                for line in abstract.getText().splitlines():
                    line = line.encode('ascii', 'ignore').decode()
                    full_text = f'{full_text}{line.rstrip()} '
        if full_text != '':
            self.record['AB'] = full_text

        # Сохраняем title и авторов если они существуют
        for meta in html.find_all('meta'):
            try:
                if meta['name'] == 'citation_title':
                    self.record['TI'] = meta['content'].rstrip()
            except:
                pass
            try:
                if meta['name'] == 'citation_authors':
                    self.record['AU'] = [author for author in meta['content'].split(';') if author != '']
            except:
                pass

        # cохраняем все места проведения исследований
        places_html = html.find('div', class_='affiliations')
        if places_html:
            places_html = places_html.find_all('li')
            if len(places_html) != 0:
                try:
                    places = [self.get_place(place) for place in places_html]
                    self.record['AD'] = places
                except Exception as e:
                    print('Ошибка при нахождении мест', e)
        return self.record

    # обрабатываем поля с местом исследований
    def get_place(self, place):
        """Обрабатываем данные с местом"""
        place = ''.join(place.getText().splitlines())
        try:
            if place[0] == ' ':
                place = place[1:]
            else:
                int(place[0])
                place = place[1:]
        except:
            pass
        finally:
            return place.rstrip()


class PMC_parser:
    def __init__(self):
        self.record = Data_record()

    def parce(self, page, page_id):
        self.record.clear()
        html = BeautifulSoup(page.text, 'lxml')

        self.record['ID'] = page_id

        # получаем основной текст записи
        full_text = ''
        information = html.find_all('p', id=re.compile('__p[0-9]*'))
        if len(information) != 0:
            for p in information:
                for line in p.getText().splitlines():
                    line = line.encode('ascii', 'ignore').decode()
                    full_text = f'{full_text}{line.rstrip()} '

        if full_text != '':
            self.record['AB'] = full_text

        # Сохраняем title и авторов если они существуют
        for meta in html.find_all('meta'):
            try:
                if meta['name'] == 'citation_title':
                    self.record['TI'] = meta['content'].rstrip()
            except:
                pass
            try:
                if meta['name'] == 'citation_authors':
                    self.record['AU'] = [author for author in meta['content'].split(',')]
            except:
                pass

        # cохраняем все места проведения исследований
        places_html = html.find_all('div', class_='fm-affl')
        if len(places_html) != 0:
            try:
                places = [self.get_place(place) for place in places_html]
                self.record['AD'] = places
            except Exception as e:
                print('Ошибка при нахождении мест', e)

        return self.record

    # обрабатываем поля с местом исследований
    def get_place(self, place):
        """Обрабатываем данные с местом"""
        place = ''.join(place.getText().splitlines())
        try:
            int(place[0])
            place = place[1:]
        except:
            pass
        finally:
            return place.rstrip()


class Data_record(dict):
    """Словарь для сохранения полей"""