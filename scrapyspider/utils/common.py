import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()  # dab19e82e1f9a681ee73346d3e7a575e


if __name__ == '__main__':
    get_md5("www.baidu.com")