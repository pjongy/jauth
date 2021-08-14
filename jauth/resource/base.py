import abc

from aiohttp.web_urldispatcher import UrlDispatcher


class BaseResource(abc.ABC):
    @abc.abstractmethod
    def route(self, router: UrlDispatcher):
        raise NotImplemented('Implement route')
