import json

DATA_LIST = [
    ['blansko/blansko', 'blansko/monitorBlansko'],
    ['brno-mesto/brnenskaDrbna', 'brno-mesto/brnenskyDennik'],
    'breclav',
    'brnoVenkov',
    'hodonin',
    'vyskov',
    'znojmo'
]


class Reader:
    words = []
    links = []

    def __init__(self):
        self._read_links_and_words()

    @classmethod
    def _read_links_and_words(cls):
        with open('links_words.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
            cls.words = data['key_words']
            cls.links = data['links']

    def read_data(self, path):
        with open('data/{}.{}'.format(path, 'json')) as json_file:
            data = json.load(json_file)
            medias = []
            region_name = ''
            for media_ in data:
                medias.append(Media(media_))
                for region in self.links:
                    for name, links in region.items():
                        if media_['pageUrl'] in links:
                            region_name = name
                            break
        return District(region_name, data, medias)


class Media:
    def __init__(self, data):
        self.raw_data = data
        self.name = data['title']
        self.link = data['pageUrl']
        self.total_topics = 0
        self.covid_topics = 0
        self.total_reactions = 0
        self.covid_reactions = 0

        self._count_topics()

    def _count_topics(self):
        self.total_topics = len(self.raw_data['posts'])
        for post in self.raw_data['posts']:
            self.total_reactions += post['postStats']['reactions']
            for word in Reader.words:
                if word in post['postText']:
                    self.covid_reactions += post['postStats']['reactions']
                    self.covid_topics += 1
                    break

    def get_info(self):
        return {
            'name': self.name,
            'link': self.link,
            'covid_topics': self.covid_topics,
            'total_topics': self.total_topics,
            'total_reactions': self.total_reactions,
            'covid_reactions': self.covid_reactions
        }


class District:
    def __init__(self, name, raw_data, medias):
        self.name = name
        self.raw_data = raw_data
        self.medias = medias
        self.covid_topics = 0
        self.total_topics = 0
        self.total_reactions = 0
        self.covid_reactions = 0

        self._process_data()

    def _process_data(self):
        for media_ in self.medias:
            self.total_topics += media_.total_topics
            self.covid_topics += media_.covid_topics
            self.total_reactions += media_.total_reactions
            self.covid_reactions += media_.covid_reactions

    def get_info(self):
        output = {
            'district_name': self.name,
            'covid_topics': self.covid_topics,
            'total_topics': self.total_topics,
            'total_reactions': self.total_reactions,
            'covid_reactions': self.covid_reactions
        }
        for media_ in self.medias:
            output.setdefault('media', []).append(media_.get_info())

        return output

    def merge(self, district):
        self.total_topics += district.total_topics
        self.covid_topics += district.covid_topics
        self.total_reactions += district.total_reactions
        self.covid_reactions += district.covid_reactions
        self.medias.extend(district.medias)


if __name__ == '__main__':
    reader = Reader()
    districts = []
    for data_f in DATA_LIST:
        if isinstance(data_f, list):
            objs = []
            for file in data_f:
                obj = reader.read_data(file)
                objs.append(obj)
            original = objs[0]
            objs.pop(0)
            for obj in objs:
                original.merge(obj)
            del objs
            obj = original
        else:
            obj = reader.read_data(data_f)
        districts.append(obj)

    with open('out.json', 'w', encoding='utf-8') as outfile:
        json.dump(districts, outfile, default=lambda dist_obj: dist_obj.get_info(), ensure_ascii=False)
