import bs4

def extract_body(source):
    soup = bs4.BeautifulSoup(source)
    return soup.find('body').renderContents()
