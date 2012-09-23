import bs4

def title(source):
    soup = bs4.BeautifulSoup(source)
    return soup.find('title').text

def body(source):
    soup = bs4.BeautifulSoup(source)
    return soup.find('body').renderContents()

def attributes(source):
    return []
