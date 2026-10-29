"""SeoForge — native SEO/AEO/GEO crawler and evidence toolkit."""

__version__ = "0.2.1"
__all__ = ["Config", "Crawler", "__version__"]


def __getattr__(name):
    if name == "Config":
        from seoforge.crawl.network import Config

        return Config
    if name == "Crawler":
        from seoforge.crawl.engine import Crawler

        return Crawler
    raise AttributeError(name)
