import requests
from lxml import etree
import urllib.parse
import os


class ScrapeGeniusLyrics():

    base_url = 'https://genius.com/'
    song_file = 'in.csv'
    lyrics = []
    
    def get_name_and_url(self):
        with open(self.song_file, 'r') as f:
            content = f.read()
            content = content.split('\n')
            for line in content:
                if ',' in line:
                    lyrics_name = str(line.split(',')[1])
                    lyrics_url = urllib.parse.urljoin(self.base_url, lyrics_name)
                    self.lyrics.append((lyrics_name, lyrics_url))
                    
    def start_request(self):
        for e in self.lyrics:
            lyrics_name = e[0]
            lyrics_url = e[1]
            response = requests.get(lyrics_url)
            html = etree.HTML(response.text)
            
            divs = html.xpath('//*[@id="lyrics-root"]/div[@class="Lyrics__Container-sc-1ynbvzw-1 kUgSbL"]')
            
            l_str = ""
            for div in divs:
                for x in div.itertext():
                    l_str = l_str + '\n' + x
                        
            file_name = f'{lyrics_name}.txt'
            if os.path.exists(file_name):
                os.remove(file_name)
            with open(file_name, 'w') as f:
                f.write(l_str)
    
    def run(self):
        print('\nHello, have a nice day!\n')
        self.get_name_and_url()
        self.start_request()

if __name__ == '__main__':
    spider = ScrapeGeniusLyrics()
    spider.run()
    