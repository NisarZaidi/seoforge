"""SeoForge — native SEO/AEO/GEO crawler and evidence toolkit."""

__version__ = "0.2.1"
__all__ = ["Config", "Crawler", "projects", "__version__"]


def __getattr__(name):
    if name == "Config":
        from seoforge.crawl.network import Config

        return Config
    if name == "Crawler":
        from seoforge.crawl.engine import Crawler

        return Crawler
    if name == "projects":
        from seoforge.cli import projects

        return projects
    raise AttributeError(name)
