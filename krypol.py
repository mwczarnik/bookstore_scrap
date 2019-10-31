import csv
import requests
from bs4 import BeautifulSoup

import os


def main():
    page = BeautifulSoup(requests.get(
        f'https://wydawnictwo.krytykapolityczna.pl/2-katalog?page=1').content, 'html.parser')

    # one before last 'li' element is directing to last site
    last_page_nr = int(page.find(
        'ul', 'page-list clearfix text-center').find_all('li')[-2].get_text().strip())
    books_data = [['Title', 'Author', 'Description',
                   'Publishment_year', 'Num_of_pages', 'Bio-description']]

    for i in range(1, last_page_nr+1):
        page = requests.get(
            f'https://wydawnictwo.krytykapolityczna.pl/2-katalog?page={i}')
        soup = BeautifulSoup(page.content, 'html.parser')
        books = soup.find_all('div', 'product-description')
        for i in books:
            # removing spaces in case off multiple authors
            author = list(map(lambda x: x.strip(), i.find(
                'div', 'book-authors').get_text().split(',')))
            title = i.find('h3', 'h3 product-title').get_text()
            # link to description page
            descr_page = requests.get(
                i.find('h3', 'h3 product-title').find('a')['href'])
            # Searching another page with description in it
            descr_soup = BeautifulSoup(descr_page.content, 'html.parser')

            descr_tags = descr_soup.find(
                'div', 'product-description').find_all('div', 'rte-content')
            description = ''.join([line.get_text().replace('\n', ' ')
                                   for line in descr_tags])

            product_features = descr_soup.find(descr_soup.find(
                'flex-row data-sheet')).find_all('div', 'col-12 col-sm-6 col-md-4 col-lg-3 item')

            num_of_pages = [
                tag for tag in product_features if 'Liczba stron' in str(tag)]
            if num_of_pages:
                num_of_pages = num_of_pages[0].find('div', 'value').get_text()
            else:
                num_of_pages = 0
            # zero if year or number of pages isn't on site
            publishment_year = [
                tag for tag in product_features if 'Rok wydania' in str(tag)]
            if publishment_year:
                publishment_year = publishment_year[0].find(
                    'div', 'value').get_text()
            else:
                publishment_year = 0

            try:
                bio_descryption_scrap = descr_soup.find(
                    'section', 'product-brand-section block-section').find_all('div', 'manufacturer-description')
                # formatting author/authors and his bio description as [[author,bio],[author2,bio2].....]
                bio_descryption_normalized = [i.get_text().replace('\n', '').replace(u'\xa0', u'').split(' – ', 1)
                                              for i in bio_descryption_scrap]
            # if book is missing bio description empty list is created
            except AttributeError:
                bio_descryption_normalized = []

            books_data.append(
                [title, author, description, publishment_year, num_of_pages, bio_descryption_normalized])
            print(title)

    # Saving data to csv
    dir_path = os.path.dirname(__file__)
    books_file = open(dir_path+'/books_data.csv', 'w', encoding="utf8")
    with books_file:
        writer = csv.writer(books_file)
        writer.writerows(books_data)
        books_file.close()


if __name__ == '__main__':
    main()
