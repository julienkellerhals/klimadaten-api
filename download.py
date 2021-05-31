import requests


def getRequest(url, cookies=None, params=None):
    """ Get request wrapper

    Args:
        url (str): URL
        cookies (cookieJar, optional): Cookies. Defaults to None.
        params (str, optional): Params. Defaults to None.

    Returns:
        response: Return get response
    """

    r = None
    reqError = True
    errorCode = None
    try:
        r = requests.get(
            url=url,
            cookies=cookies,
            params=params,
            timeout=210
        )
        r.raise_for_status()
        reqError = False
    except requests.exceptions.Timeout as e:
        print("request timed-out")
        print(e)
    except requests.exceptions.ConnectionError as e:
        print("connection error")
        print(e)
    except requests.exceptions.HTTPError as e:
        errorCode = r.status_code
        print(e)
    except requests.exceptions.ChunkedEncodingError as e:
        print("connection error")
        print(e)
    return r, reqError, errorCode


def postRequest(url, cookies, data):
    """ Post request wrapper

    Args:
        url (str): URL
        cookies (cookieJar): Cookies.
        data (str): Data to send.

    Returns:
        response: Return post response
    """

    r = None
    reqError = True
    errorCode = None
    try:
        r = requests.post(
            url,
            cookies=cookies,
            data=data,
            timeout=210
        )
        r.raise_for_status()
        reqError = False
    except requests.exceptions.Timeout as e:
        print("request timed-out")
        print(e)
    except requests.exceptions.ConnectionError as e:
        print("connection error")
        print(e)
    except requests.exceptions.HTTPError as e:
        errorCode = r.status_code
        print(e)
    except requests.exceptions.ChunkedEncodingError as e:
        print("connection error")
        print(e)
    return r, reqError, errorCode
