from scrapy.item import Item, Field


class Game(Item):
    team1 = Field()
    team2 = Field()
    alias_team1 = Field()
    alias_team2 = Field()
    date = Field()
    date_time = Field()
    place = Field()
    group = Field()
    round = Field()
