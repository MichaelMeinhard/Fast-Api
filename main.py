from fastapi import FastAPI, HTTPException
from scrip import scrape_series
from pydantic import BaseModel
import orjson

scrape_series()


class Series(BaseModel):
    name: str
    rating: str
    description: str
    runtime: str
    genre: str
    stars: list
    years: str

    @staticmethod
    def from_dict(data: dict):
        record = Series(**data)
        return record


class Problem(BaseModel):
    detail: str


class Database:
    def __init__(self):
        self._data: list = []

    def load_from_filename(self, filename: str):
        with open(filename, "rb") as f:
            data = orjson.loads(f.read())
            for record in data:
                obj = Series.from_dict(record)
                self._data.append(obj)

    def delete(self, id_serie: int):
        if 0 < id_serie >= len(self._data):
            return
        self._data.pop(id_serie)

    def add(self, serie: Series):
        self._data.append(serie)

    def get(self, id_serie: int):
        if 0 < id_serie >= len(self._data):
            return
        return self._data[id_serie]

    def get_all(self) -> list[Series]:
        return self._data

    def update(self, id_serie: int, serie: Series):
        if 0 < id_serie >= len(self._data):
            return
        self._data[id_serie] = serie

    def count(self) -> int:
        return len(self._data)


db = Database()
db.load_from_filename('series.json')

app = FastAPI(title="Top Serialy", version="0.1", docs_url="/docs")

app.is_shutdown = False


@app.get("/series", response_model=list[Series], description="Vrátí seznam seriálů")
async def get_series():
    return db.get_all()


@app.get("/series/{id_serie}", response_model=Series)
async def get_serie(id_serie: int):
    return db.get(id_serie)


@app.post("/series", response_model=Series, description="Přidáme seriál do DB")
async def post_series(serie: Series):
    db.add(serie)
    return serie


@app.delete("/series/{id_serie}", description="Sprovodíme seriál ze světa", responses={
    404: {'model': Problem}
})
async def delete_serie(id_serie: int):
    serie = db.get(id_serie)
    if serie is None:
        raise HTTPException(404, "Seriál neexistuje")
    db.delete(id_serie)
    return {'status': 'smazano'}


@app.patch("/series/{id_serie}", description="Aktualizujeme seriál do DB", responses={
    404: {'model': Problem}
})
async def update_serie(id_serie: int, updated_serie: Series):
    serie = db.get(id_serie)
    if serie is None:
        raise HTTPException(404, "Seriál neexistuje")
    db.update(id_serie, updated_serie)
    return {'old': serie, 'new': updated_serie}
