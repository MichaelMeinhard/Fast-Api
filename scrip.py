import requests
from bs4 import BeautifulSoup
import orjson


def scrape_series():
    URL = 'https://www.imdb.com/list/ls070403259/'

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    series_name = soup.select('h3.lister-item-header>a')
    names = [tag.text for tag in series_name]
    series_rating = soup.select('div.ipl-rating-widget>div.ipl-rating-star>span.ipl-rating-star__rating')
    rating = [tag.text for tag in series_rating]
    series_desc = soup.select('div.lister-item-content>p[class = ""]')
    desc = [tag.text for tag in series_desc]
    series_runtime = soup.select('p>span.runtime')
    runtime = [tag.text for tag in series_runtime]
    series_genre = soup.select('p>span.genre')
    genre = [tag.text.strip() for tag in series_genre]
    paragraphs = soup.find_all('p', class_='text-muted text-small')
    series_years = soup.select('h3.lister-item-header>span.lister-item-year')
    years = [tag.text[1:-1] if "I" not in tag.text else tag.text[5:-1] for tag in series_years]

    stars_array = []
    for p in paragraphs:
        stars = []
        for a in p.find_all('a'):
            stars.append(a.string.strip())
        stars_array.append(stars)

    stars_array = [stars for stars in stars_array if stars != []]

    series = []
    for i in range(0, 20):
        serie = {'name': names[i],
                 'description': desc[i].strip(),
                 'rating': float(rating[i]),
                 'runtime': str(runtime[i]),
                 'genre': str(genre[i]),
                 'stars': stars_array[i],
                 'years': years[i]
                 }
        series.append(serie)

    with open('series.json', 'wb') as f:
        f.write(orjson.dumps(series))