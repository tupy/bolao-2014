
import re

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.contrib.spiders import Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor

from ..items import Game

WIDGET_UUID = 'c36d99dd-918a-459f-bf0c-648dec5773af'
URL_SCHEME = 'http://globoesporte.globo.com/servico/esportes_campeonato/widget-uuid/%(uuid)s/fases/fase-grupos-copa-do-mundo-2014/grupo/%(group_id)s/rodada/%(round)s/jogos.html'

GROUPS = [
  ('A', 1069),
  ('B', 1069),
  ('C', 1071),
  ('D', 1072),
  ('E', 1073),
  ('F', 1074),
  ('G', 1075),
  ('H', 1166)
]

GROUP_MAP = {v2:v1 for v1,v2 in GROUPS}

def start_urls():
  for group, group_id in GROUPS:
    for i in range(1, 4):
      data = dict(uuid=WIDGET_UUID, group_id=group_id, round=i)
      url = URL_SCHEME % data
      yield url


class GloboEsporteSpider(Spider):
    name = "globoesporte"
    allowed_domains = ["globoesporte.com"]
    start_urls = start_urls()

    rules = (    
        # Extract links matching 'jogos.html' and parse them with the spider's method parse_game
        Rule(SgmlLinkExtractor(allow=('jogos\.html', )), callback='parse_games', follow=False),
    )

    def parse(self, response):

        p = re.compile('.+/grupo/(?P<group>.+)/rodada/(?P<round>.+)/jogos.html')
        m = p.match(response.url)
        group = GROUP_MAP[int(m.group('group'))]
        round = int(m.group('round'))

        hxs = Selector(response)
        games = hxs.xpath('//li')
        items = []

        for game in games:
            item = Game()
            item['round'] = round
            item['group'] = group
            item['team1'] = game.xpath('.//div[contains(@class, "equipe-mandante")]/meta/@content').extract()[0]
            item['alias_team1'] = game.xpath('.//div[contains(@class, "equipe-mandante")]/span[@class="nome-equipe"]/text()').extract()[0]
            item['team2'] = game.xpath('.//div[contains(@class, "equipe-visitante")]/meta/@content').extract()[0]
            item['alias_team2'] = game.xpath('.//div[contains(@class, "equipe-visitante")]/span[@class="nome-equipe"]/text()').extract()[0]
            item['date'] = game.xpath('.//div[@class="data-local"]//meta/@content').extract()[0]
            item['date_time'] = game.xpath('.//div[@class="data-local"]//span[1]/text()').extract()[0]
            item['place'] = game.xpath('.//div[@class="data-local"]/span[2]/text()').extract()[0]
            #item['time'] = game.select('a/@href').extract()[0]
            #item['description'] = site.select('text()').re('-\s([^\n]*?)\\n')
            items.append(item)

        return items
