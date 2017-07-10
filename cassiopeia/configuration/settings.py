import os
import logging


from ..data import Region, Platform
from .load import config


logging.basicConfig(format='%(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.WARNING)


def create_default_pipeline(api_key, verbose=False):
    from datapipelines import DataPipeline
    from ..datastores.riotapi import RiotAPI
    from ..datastores.datadragon import DataDragonService
    from ..transformers.staticdata import StaticDataTransformer
    from ..transformers.champion import ChampionTransformer
    from ..transformers.championmastery import ChampionMasteryTransformer
    from ..transformers.summoner import SummonerTransformer
    from ..transformers.match import MatchTransformer

    services = [
        RiotAPI(api_key=api_key),
        DataDragonService()
    ]
    riotapi_transformers = [
        StaticDataTransformer(),
        ChampionTransformer(),
        ChampionMasteryTransformer(),
        SummonerTransformer(),
        MatchTransformer()
    ]
    pipeline = DataPipeline(services, riotapi_transformers)

    if verbose:
        for service in services:
            for p in service.provides:
                print("Provides:", p)
        for transformer in riotapi_transformers:
            for t in transformer.transforms.items():
                print("Transformer:", t)
        print()

    return pipeline


class Settings(object):
    def __init__(self, settings):
        self.__key = settings["Riot API"]["key"]
        self.__default_region = Region(settings["Riot API"]["region"].upper())
        self.__pipeline = None
        for name in ["default", "core"]:
            logger = logging.getLogger(name)
            level = settings["logging"].get(name, logging.WARNING)  # Set default logging level to WARNING.
            logger.setLevel(level)
            for handler in logger.handlers:
                handler.setLevel(level)

    def set_pipeline(self, pipeline):
        self.__pipeline = pipeline

    def set_region(self, region):
        self.__default_region = region

    @property
    def pipeline(self):
        if self.__pipeline is None:
            if not self.__key.startswith("RGAPI"):
                self.__key = os.environ[self.__key]
            self.__pipeline = create_default_pipeline(api_key=self.__key, verbose=False)
        return self.__pipeline

    @property
    def default_region(self):
        return self.__default_region

    @property
    def default_platform(self):
        return Platform[self.__default_region.name]


settings = Settings(config)