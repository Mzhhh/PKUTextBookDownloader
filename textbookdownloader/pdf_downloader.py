import os, sys
from .url_handler import page_url_iter
import requests
from requests import Timeout
from io import BytesIO
from PIL import Image
from tqdm import tqdm


def download_pictures(meta_url, target_path='./', start=1, end=None, timeout=None, name_fmt='{:03d}', **kwargs):
    (title, num_pages), url_iter = page_url_iter(meta_url, **kwargs)
    title = '<unknown>' if not title else title
    print('URL decode succeeded. Ready to download {}.'.format(title))
    os.makedirs(target_path + title, exist_ok=True)
    image_path = target_path + title + '/'
    start = max(start, 1) if start else 1
    end = num_pages if not end else end
    assert end >= start
    try:
        with tqdm(total=num_pages) as process_counter:
            for pid, url in url_iter:
                if pid < start:
                    continue
                r = requests.get(url, timeout=timeout)
                img = Image.open(BytesIO(r.content))
                img.save(image_path+name_fmt.format(pid)+'.png', 'PNG')
                img.close
                process_counter.update(1)
                if pid >= end:
                    break
    except (Exception, KeyboardInterrupt) as e:
        print('Oops, {} has occurred. Files stored in {}.'.format(repr(e).split('(')[0], target_path+title))
        sys.exit(0)
    print('Download succeeded. Files stored in {}.'.format(target_path + title))


def download_pdf(meta_url, target_path='./', start=1, end=None, timeout=None, **kwargs):
    (title, num_pages), url_iter = page_url_iter(meta_url, **kwargs)
    title = '<unknown>' if not title else title
    print('URL decode succeeded. Ready to download {}.'.format(title))
    os.makedirs(target_path, exist_ok=True)
    book_path = target_path + title + '.pdf'
    start = max(start, 1) if start else 1
    end = num_pages if not end else end
    assert end >= start
    images = []
    try: 
        with tqdm(total=end-start+1) as process_counter:
            for pid, url in url_iter:
                if pid < start:
                    continue
                r = requests.get(url, timeout=timeout)
                images.append(Image.open(BytesIO(r.content)).convert('RGB'))
                process_counter.update(1)
                if pid >= end:
                    break
    except (Exception, KeyboardInterrupt) as e:
        print('Oops, {} has occurred. Converting data to PDF.'.format(repr(e).split('(')[0], book_path))
        images[0].save(book_path, 'PDF', save_all = True, quality=100, append_images = images[1:])
        print('Convert succeeded. File stored as {}.'.format(book_path))
        for img in images:
            img.close()
        sys.exit(0)
    print('Download succeeded. Converting data to PDF.')
    images[0].save(book_path, 'PDF', save_all = True, quality=100, append_images = images[1:])
    print('Convert succeeded. File stored as {}.'.format(book_path))
    for img in images:
            img.close()