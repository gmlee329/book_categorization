# url 수집
from bs4 import BeautifulSoup
import urllib.request as req

class BookInfo():
    def __init__(self):
        self.category_numbers = {'경제/경영' : '001001025', 
                    '사회/정치' : '001001022', 
                    '시/소설' : '001001046', 
                    '어린이' : '001001016', 
                    '역사' : '001001010', 
                    '인문' : '001001019', 
                    '과학' : '001001002'}
        self.yes24_url = 'http://www.yes24.com/'
        self.resource = '24/Category/More/'
        self.query = '?ElemNo=104&ElemSeq=1&ParamSortTp=05&FetchSize=20&PageNumber='
    
    def get_books_url_dict(self, total_page):
        url_dict = {}
        for category, category_number in self.category_numbers.items():
            for page_number in range(1, total_page+1):
                res = req.urlopen(f'{self.yes24_url}{self.resource}{category_number}{self.query}{page_number}')
                res = res.read()
                soup = BeautifulSoup(res, "html.parser")

                div = soup.find_all('div',{'class':'goods_name'})
                url_dict[category] = [self.yes24_url + href.find_all('a')[0].attrs['href'] for href in div]
        
        return url_dict

    def get_books_title_and_img(self, url_dict, count):
        error_msg = '제목을 불러 올 수 없습니다.'
        error_url = 'http://image.yes24.com/sysimage/renew/gnb/logoN2.png'
        error_link = self.yes24_url
        contents_dict = {}

        for category, url_list in url_dict.items():
            contents_list = []
            for url in url_list[:count]:
                try:
                    res = req.urlopen(url)
                    res = res.read()
                    soup = BeautifulSoup(res, "html.parser")

                    title = soup.find('h2', {'class':'gd_name'}).text
                    img_url = soup.find('em',{'class':'imgBdr'}).find('img').attrs['src']
                    link = url

                    contents_list.append([title, img_url, link])
                except:
                    contents_list.append([error_msg, error_url, error_link])
                    pass
            contents_dict[category] = contents_list
        
        return contents_dict

if __name__ == '__main__':
    #test
    total_page = 1
    count = 3

    book_info = BookInfo()
    url_dict = book_info.get_books_url_dict(total_page)
    contents_dict = book_info.get_books_title_and_img(url_dict, count)

    print(contents_dict)