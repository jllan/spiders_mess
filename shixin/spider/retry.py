import requests
from proxy import get_proxy_available


# 定义一个重试修饰器，默认重试一次
def retry(num_retries=1):
    # 用来接收函数
    def wrapper(func):
        # 用来接收函数的参数
        def wrapper(*args, **kwargs):
            # 为了方便看抛出什么错误定义一个错误变量
            last_exception = None
            # 循环执行包装的函数
            for _ in range(num_retries):
                try:
                    # 如果没有错误就返回包装的函数，这样跳出循环
                    return func(*args, **kwargs)
                except Exception as e:
                    # 捕捉到错误不要return，不然就不会循环了
                    last_exception = e
                    print('error')
                    # 如果要看抛出错误就可以抛出
                    # raise last_exception
        return wrapper

    return wrapper

@retry(3)
def print_page(url):
    proxy = get_proxy_available()
    proxies = {proxy.split(':')[0]: proxy}
    print('使用代理: {}'.format(proxy))
    response = requests.get(url, proxies=proxies)
    print("access!")
    # raise_for_status(),如果不是200会抛出HttpProcessingError错误
    response.raise_for_status()
    body = response.text()
    print(body)
    return body


if __name__ == '__main__':
    print_page('http://jlan.me')