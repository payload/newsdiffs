from . import *

class SwrArticle(Article):
    SUFFIX = ''
    domain = 'www.swr.de'
    fetcher_url = 'http://www.tagesschau.de/newsticker.rdf'

    @classmethod
    def fetch_urls(self):
        ''' Article urls for a single website. '''
        import feedparser
        feed = feedparser.parse(self.fetcher_url)
        urls = [e.link for e in feed.entries if 'www.swr.de' in e.link]
        return urls


    def _parse(self, html):
        import bs4
        soup = bs4.BeautifulSoup(html)

        # extract the important text of the article into self.document #
        # select the one article
        article = soup.select('div.beitrag')
        # this
        if not article:
            self.real_article = False
            return
        article = article[0]
        # removing comments
        for x in list(article.descendants):
            if isinstance(x, bs4.Comment):
                x.extract()
        # removing elements which don't provide content
        for selector in ('.teaser-row .clearing').split(' '):
            for x in article.select(selector):
                x.extract()
        # put hrefs into text form cause hrefs are important content
        for x in article.select('a'):
            x.append(" ["+x.get('href','')+"]")
        # ensure proper formating for later use of get_text()
        for x in article.select('li'):
            x.append("\n")
        for tag in 'p h1 h2 h3 h4 h5 ul div'.split(' '):
            for x in article.select(tag):
                x.append("\n\n")
                
        self.title = article.find('h1').get_text().strip()
                
        # strip multiple newlines away
        import re
        article = re.subn('\n\n+', '\n\n', article.get_text())[0]
        # important text is now extracted into self.document
        self.document = article

        self.byline = "nicht genannt"

        # TODO self.date is unused, isn't it? but i still fill it here
        date = soup.select("p.aenderung")
        self.date = date and date[0].get_text() or ''

    def __unicode__(self):
        return self.document

