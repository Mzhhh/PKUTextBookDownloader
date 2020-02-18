from textbookdownloader.file_downloader import *
import json

def main():
    url = input('Enter URL (online reader): ')
    file_format = input('Download format (pdf[/png]): ').lower()
    with open('./config.json') as f:
        config = json.load(f)
    print('-'*75)
    if file_format == 'png':
        download_pictures(url, **config)
    else:
        download_pdf(url, **config)


if __name__ == '__main__':
    main()