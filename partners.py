import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import pandas as pd
import json

base_url = 'https://www.odoo.com'
index_url = 'partners/country/{cc}/page/{page}'

AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
DTD = 'https://raw.githubusercontent.com/sotogarcia/odoo_partner_scraping/main/partners.dtd'
PARTNERS_XML = '''{prolog}<partners>

{content}

</partners>
'''

PARTNER_XML = '''{prolog}    <partner src="{src}">
        <name>{name}</name>
        <type>{type}</type>
        <address><![CDATA[{address}]]></address>
        <zip>{zip}</zip>
        <city>{city}</city>
        <state>{state}</state>
        <phone>{phone}</phone>
        <web>{web}</web>
        <email>{email}</email>
        <vocation>{vocation}</vocation>
        <logo>{logo}</logo>
        <description><![CDATA[{description}]]></description>
    </partner>'''

states = [
    '', 'Álava', 'Albacete', 'Alicante', 'Almería', 'Ávila', 'Badajoz',
    'Baleares', 'Barcelona', 'Burgos', 'Cáceres', 'Cádiz', 'Castellón',
    'Ciudad Real', 'Córdoba', 'La Coruña', 'Cuenca', 'Gerona', 'Granada',
    'Guadalajara', 'Guipúzcoa', 'Huelva', 'Huesca', 'Jaén', 'León', 'Lérida',
    'La Rioja', 'Lugo', 'Madrid', 'Málaga', 'Murcia', 'Navarra', 'Orense',
    'Asturias', 'Palencia', 'Las Palmas', 'Pontevedra', 'Salamanca',
    'Santa Cruz de Tenerife', 'Cantabria', 'Segovia', 'Sevilla', 'Soria',
    'Tarragona', 'Teruel', 'Toledo', 'Valencia', 'Valladolid', 'Vizcaya',
    'Zamora', 'Zaragoza', 'Ceuta', 'Melilla'
]


class Partner:

    def __init__(self, url):
        headers = {'User-Agent': AGENT}

        self._url = url

        self._page = requests.get(self._url, headers=headers)
        self._content = BeautifulSoup(self._page.text, 'lxml')
        self._card = self._content.find('address')

        self._name = None
        self._type = None
        self._address = None
        self._zip = None
        self._city = None
        self._state = None
        self._phone = None
        self._web = None
        self._email = None
        self._vocation = None
        self._description = None
        self._logo = None

    @property
    def name(self):
        if not self._name and self._content:
            attrs = {'id': 'partner_name'}
            item = self._content.find('h1', attrs=attrs)
            self._name = item.text if item else ''

        return self._name or ''

    @property
    def type(self):
        if not self._type and self._content:
            attrs = {'id': 'partner_name'}
            item = self._content.find('h1', attrs=attrs)
            item = item.find_next_sibling('h3').find('span')
            self._type = item.text if item else ''

        return self._type or ''

    @property
    def address(self):
        if not self._address:
            self._update_address()

        return self._address or ''

    @property
    def zip(self):
        if not self._address:
            self._update_address()

        return self._zip or ''

    @property
    def city(self):
        if not self._address:
            self._update_address()

        return self._city or ''

    @property
    def state(self):
        if not self._address:
            self._update_address()

        return self._state or ''

    @property
    def phone(self):
        if not self._phone and self._content:
            attrs = {'itemprop': 'telephone'}
            item = self._content.find('span', attrs=attrs)
            self._phone = item.text if item else ''

        return self._phone or ''

    @property
    def web(self):
        if not self._web and self._content:
            attrs = {'itemprop': 'website'}
            span = self._content.find('span', attrs=attrs)
            if span:
                link = span.find_parent('a')
                if link:
                    self._web = link['href']

        return self._web or ''

    @property
    def email(self):
        if not self._email and self._content:
            attrs = {'itemprop': 'email'}
            item = self._content.find('span', attrs=attrs)
            self._email = item.text if item else ''

        return self._email or ''

    @property
    def vocation(self):
        if not self._vocation and self._content:
            attrs = {'class': 'badge badge-secondary'}
            item = self._content.find('span', attrs=attrs)
            self._vocation = item.text if item else ''

        return self._vocation or ''

    @property
    def description(self):
        if not self._description and self._card:
            attrs = {'class': 'row'}
            parent = self._card.find_parent('div', attrs=attrs)
            attrs = {'class': 'col-lg-8 mt32'}
            item = parent.find('div', attrs=attrs).find('div')
            self._description = item.text if item else ''

        return self._description or ''

    @property
    def logo(self):
        if not self._logo and self._card:
            attrs = {'class': 'col-lg-4'}
            parent = self._card.find_parent('div', attrs=attrs)
            item = parent.find('img')
            if item:
                parsed = urlparse(self._url)
                self._logo = '{}:{}'.format(parsed.scheme, item['src'])

        return self._logo or ''

    @property
    def src(self):
        return self._url

    def _update_address(self):
        attrs = {'itemprop': 'streetAddress'}
        item = self._content.find('span', attrs=attrs)

        if item:
            lines = item.decode_contents().split('<br/>')
            self._address = ' '.join(lines)

            for line in lines:
                match = re.search(r'\b[0-9]{5}\b', line)
                if match:
                    self._zip = match.group()
                    self._state = states[int(self._zip[:2])]

                    city = re.sub(r'\b[0-9]{5}\b', '', line) or ''
                    self._city = city.strip()

                    break

    def __str__(self):
        return str(self._to_dict(logo=False, desc=False))

    def to_dict(self, logo=True, desc=False):
        return dict(
            name=self.name,
            type=self.type,
            address=self.address,
            zip=self.zip,
            city=self.city,
            phone=self.phone,
            web=self.web,
            email=self.email,
            vocation=self.vocation,
            logo=self.logo if logo else bool(self.logo),
            description=self.description if desc else bool(self.description),
            src=self.src
        )

    def toXML(self, prolog=True):
        prolog_line = '<?xml version="1.0" encoding="UTF-8"?>\n\n'

        return PARTNER_XML.format(
            prolog=prolog_line if prolog else '',
            name=self.name,
            type=self.type,
            address=self.address,
            city=self.city,
            zip=self.zip,
            state=self.state,
            phone=self.phone,
            web=self.web,
            email=self.email,
            vocation=self.vocation,
            logo=self.logo,
            description=self.description,
            src=self.src
        )


class App():

    def __init__(self, country, page_limit=1, verbose=False):
        headers = {'User-Agent': AGENT}
        attrs = {'class', 'media-body o_partner_body'}
        url_pattern = urljoin(base_url, index_url)

        self._debug = verbose

        self._partners = []
        self._nodes = []

        for page_index in range(1, page_limit + 1):
            url = url_pattern.format(cc=country, page=page_index)
            page = requests.get(url, headers=headers)
            content = BeautifulSoup(page.text, 'lxml')

            for item in content.find_all('div', attrs=attrs):
                a = item.find('a')
                if not a:
                    continue

                url = urljoin(base_url, a['href'])
                partner = Partner(url)

                self._verbose(partner.name)

                self._partners.append(partner)
                self._nodes.append(partner.toXML(prolog=False))

    def _verbose(self, msg):
        if self._debug:
            print(msg)

    def toXML(self, prolog=True):
        if prolog:
            prolog_line = '<?xml version="1.0" encoding="UTF-8"?>\n'
            prolog_line += '<!DOCTYPE partners SYSTEM "{}">\n\n'.format(DTD)
        else:
            prolog_line = ''

        return PARTNERS_XML.format(
            prolog=prolog_line,
            content='\n\n'.join(self._nodes)
        )

    def toJSON(self, prolog=True):
        partners = []

        for partner in self._partners:
            partners.append(partner.to_dict())

        return json.dumps(partners)

    def _data_frame(self):
        data = {
            'name': [partner.name for partner in self._partners],
            'type': [partner.type for partner in self._partners],
            'address': [partner.address for partner in self._partners],
            'city': [partner.city for partner in self._partners],
            'zip': [partner.zip for partner in self._partners],
            'state': [partner.state for partner in self._partners],
            'phone': [partner.phone for partner in self._partners],
            'web': [partner.web for partner in self._partners],
            'email': [partner.email for partner in self._partners],
            'vocation': [partner.vocation for partner in self._partners],
            'logo': [partner.logo for partner in self._partners],
        }

        return pd.DataFrame(data)

    def save(self, path, file_format='xml'):
        if file_format == 'xml':
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.toXML())
        elif file_format == 'csv':
            df = self._data_frame()
            df.to_csv(path, sep=',', encoding='utf-8')
        elif file_format == 'xlsx':
            df = self._data_frame()
            df.to_excel(path)
        elif file_format == 'json':
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.toJSON())
        else:
            raise Exception('Unknown file format')

    def __str__(self):
        partners = []
        for partner in self._partners:
            partners.append(partner.name)

        return str(partners)


app = App(country=67, page_limit=2, verbose=True)

app.save('partners.xml', file_format='xml')
app.save('partners.csv', file_format='csv')
app.save('partners.xlsx', file_format='xlsx')
app.save('partners.json', file_format='json')
