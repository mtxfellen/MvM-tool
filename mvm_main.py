import requests # pip install requests
from random import randint
from datetime import timedelta

# function does requests.get.text on url with basic error-handling
def net_request(url,jsonOrText=None):
    while True:
        try:
            requestedPage = requests.get(url,timeout=11)
            requestedPage.raise_for_status()
        except requests.exceptions.ConnectionError:
            raise SystemExit("Requests Error: Could not connect to the client; is your connection down?.")
        except requests.exceptions.TooManyRedirects:
            raise SystemExit("Requests Error: Bad URL.")
        except requests.exceptions.HTTPError as err:
            err = "Requests Error: Client returned '" + str(err) + "'."
            raise SystemExit(err)
        except requests.exceptions.Timeout:
            print("Requests Error: Request timed out. Press RETURN to retry.")
            input()
        except requests.exceptions.RequestException:
            raise SystemExit("Requests Error: Unknown fatal error; possible bad URL format.")
        else:
            if jsonOrText == None or jsonOrText == 'text':
                requestedPage = requestedPage.text
            elif jsonOrText == 'json':
                requestedPage = requestedPage.json()
            else:
                raise SystemExit("Invalid specifier for request return type.")
            return requestedPage

# function is fed a list and returns the position in that list of the user's selection
def loop_input(possibleInputs,noSuchAs=None):
    inputLen = len(possibleInputs)
    while True:
        userSelection = input()
        if is_int(userSelection):
            for i in range(inputLen):
                if userSelection == possibleInputs[i]:
                    return i
        else:
            for i in range(inputLen):
                if userSelection.casefold() == possibleInputs[i].casefold():
                    return i
        if noSuchAs is not None:
            failStr = "Invalid input; please select only a valid option."
        else:
            failStr = "Invalid input; please select only a valid option, such as \"" + possibleInputs[randint(0,inputLen)] + "\"."
        print(failStr)
            
# function is fed a variable and returns true if it is an int
def is_int(intInput):
    try:
        intInput = int(intInput)
        return True
    except ValueError:
        return False

# there may be a preexisting method to do these more robustly, but
# they're currently unused anyway
# function takes a string and appends a forward slash to the end if absent
def append_fwd_slash(url):
    if url[-1] != '/':
        url += '/'
    return url
# function takes a string and appends https protocol if absent
def append_https(url):
    if url[0:8] != 'https://':
        url = 'https://' + url
    return url
# function takes a string and removes www if present
def remove_www(url):
    if url[8:12] == 'www.':
        url = url[0:8] + url[12:]
    elif url[0:4] == 'www.':
        url = url[4:]
    return url

# function is fed a root url then fetches 'url' & 'archive.url'
# returns only one if pages appear to be identical
# todo: update to use a proper html parse (if there's no api method) for robustness
def get_active_tours(root_url):
    root_url = remove_www(append_fwd_slash(append_https(root_url)))
    archive_root_url = root_url[0:8] + 'archive.' + root_url[8:]
    root_page = net_request(root_url)
    archive_root_page = net_request(archive_root_url)
    
    activeTitle = root_page[root_page.find('<title>')+17:]
    activeTitle = activeTitle[:activeTitle.find('</title>')]
    archiveTitle = archive_root_page[archive_root_page.find('<title>')+17:]
    archiveTitle = archiveTitle[:archiveTitle.find('</title>')]
    
    if activeTitle == archiveTitle:
        return [archiveTitle]
    else:
        return [activeTitle,archiveTitle]

# function converts a number to the appropraite difficulty string
def num_2_difficulty(difficulty):
    if difficulty == 0:
        difficulty = "Normal"
    elif difficulty == 1:
        difficulty = "Intermediate"
    elif difficulty == 2:
        difficulty = "Advanced"
    elif difficulty == 3:
        difficulty = "Expert"
    elif difficulty == 4:
        difficulty = "NIGHTMARE!"
    else:
        difficulty = "Unknown"
    return difficulty

# formats time for speedrun, timedelta had some issues handling edge cases
# todo: truncate leading 0s for same format automatically
def multi_format_time(listOfSeconds):
    for seconds in listOfSeconds:
        seconds = timedelta(seconds=seconds)
    return listOfSeconds

# textwrap is unreliable
def shorten_string(string, limit):
    return string[:limit-3] + (string[limit-3:], '...')[len(string) > limit]
