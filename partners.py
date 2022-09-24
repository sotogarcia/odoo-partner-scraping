import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

base_url = 'https://www.odoo.com'
index_url = 'es_ES/partners/country/espana-{cc}/page/{page}'

AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
PARTNERS_XML = '''{prolog}<partners>

{content}

</partners>
'''

PARTNER_XML = '''{prolog}    <partner>
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

        return self._name

    @property
    def type(self):
        if not self._type and self._content:
            attrs = {'id': 'partner_name'}
            item = self._content.find('h1', attrs=attrs)
            item = item.find_next_sibling('h3').find('span')
            self._type = item.text if item else ''

        return self._type

    @property
    def address(self):
        if not self._address:
            self._update_address()

        return self._address

    @property
    def zip(self):
        if not self._address:
            self._update_address()

        return self._zip

    @property
    def city(self):
        if not self._address:
            self._update_address()

        return self._city

    @property
    def state(self):
        if not self._address:
            self._update_address()

        return self._state

    @property
    def phone(self):
        if not self._phone and self._content:
            attrs = {'itemprop': 'telephone'}
            item = self._content.find('span', attrs=attrs)
            self._phone = item.text if item else ''

        return self._phone

    @property
    def web(self):
        if not self._web and self._content:
            attrs = {'itemprop': 'website'}
            span = self._content.find('span', attrs=attrs)
            if span:
                link = span.find_parent('a')
                if link:
                    self._web = link['href']

        return self._web

    @property
    def email(self):
        if not self._email and self._content:
            attrs = {'itemprop': 'email'}
            item = self._content.find('span', attrs=attrs)
            self._email = item.text if item else ''

        return self._email

    @property
    def vocation(self):
        if not self._vocation and self._content:
            attrs = {'class': 'badge badge-secondary'}
            item = self._content.find('span', attrs=attrs)
            self._vocation = item.text if item else ''

        return self._vocation

    @property
    def description(self):
        if not self._description and self._card:
            attrs = {'class': 'row'}
            parent = self._card.find_parent('div', attrs=attrs)
            attrs = {'class': 'col-lg-8 mt32'}
            item = parent.find('div', attrs=attrs).find('div')
            self._description = item.text if item else ''

        return self._description

    @property
    def logo(self):
        if not self._description and self._card:
            attrs = {'class': 'col-lg-4'}
            parent = self._card.find_parent('div', attrs=attrs)
            item = parent.find('img')
            self._logo = item['src'] if item else ''

        return self._logo

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
        return self.__repr__()

    def __repr__(self):
        rep = dict(
            name=self.name,
            type=self.type,
            address=self.address,
            zip=self.zip,
            city=self.city,
            phone=self.phone,
            web=self.web,
            email=self.email,
            vocation=self.vocation,
            logo=bool(self.logo),
            description=bool(self.description),
        )

        return str(rep)

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
            description=self.description
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
        prolog_line = '<?xml version="1.0" encoding="UTF-8"?>\n\n'

        return PARTNERS_XML.format(
            prolog=prolog_line if prolog else '',
            content='\n\n'.join(self._nodes)
        )

    def save(self, path, file_format='xml'):
        if file_format == 'xml':
            with open(path, 'w', encoding='utf-8') as f:
                f.write(self.toXML())

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        partners = []
        for partner in self._partners:
            partners.append(partner.name)

        return str(partners)


app = App(country=67, page_limit=2, verbose=True)

app.save('partners.xml')
