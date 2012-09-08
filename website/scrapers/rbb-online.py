from . import *

class RbbOnlineArticle(Article):
    SUFFIX = ''
    domain = 'www.rbb-online.de'
    fetcher_url = 'http://www.tagesschau.de/newsticker.rdf'

    @classmethod
    def fetch_urls(self):
        ''' Article urls for a single website. '''
        import feedparser
        feed = feedparser.parse(self.fetcher_url)
        urls = [e.link for e in feed.entries if 'www.rbb-online.de' in e.link]
        return urls


    def _parse(self, html):
        import bs4
        soup = bs4.BeautifulSoup(html)

        # extract the important text of the article into self.document #
        # select the one article
        article = soup.select('div.articleA')
        # this
        if not article:
            self.real_article = False
            return
        article = article[0]
        
        self.title = soup.find('h1').get_text().strip()
        
        # TODO self.date is unused, isn't it? but i still fill it here
        date = soup.select("div.archiveDisclaimer")
        try:
            date = (x for x in date[0].descendants if 'Stand' in x).next()
            self.date = date.strip()
        except Exception:
            self.date = ''
        
        # removing comments
        for x in list(article.descendants):
            if isinstance(x, bs4.Comment):
                x.extract()
        # removing elements which don't provide content
        for selector in ('div').split(' '):
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
        # strip multiple newlines away
        import re
        article = re.subn('\n\n+', '\n\n', article.get_text())[0]
        # important text is now extracted into self.document
        self.document = article

        self.byline = "nicht genannt"

    def __unicode__(self):
        return self.document

