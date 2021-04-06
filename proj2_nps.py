#################################
##### Name: Sushmitha Rao
##### Uniqname: sushrao
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

#CACHE_FILENAME = "cache.json"
CACHE_DICT = {}

key = secrets.MAPQUEST_API_KEY
class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return(f'{self.name} ({self.category}): {self.address} {self.zipcode}') #info method can be called on the class instances


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    dictionary = {} #empty dictionary to store state name and link
    f = requests.get("https://www.nps.gov/index.htm") #homepage url
    html_text = f.text
    soup = BeautifulSoup(html_text, 'html.parser')
    # accessing dropdown section of html
    drop_down_items = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
    #finding all the list items within dropdown menu
    link_state_list = drop_down_items.find_all('li')
    #looping through each list item to find link and state name
    #followed by constructing dictionary
    for link_state in link_state_list:
        tag = link_state.find('a')
        state = link_state.string
        link = f"https://www.nps.gov{tag.get('href',None)}"
        dictionary[state] = link
    return dictionary

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    f = requests.get(site_url)
    html_text = f.text
    soup = BeautifulSoup(html_text, 'html.parser')
    #extracting national site location information via beautifulsoup
    name_header = soup.find('div', class_='Hero-titleContainer').find('a')
    category_header = soup.find('span', class_='Hero-designation')
    address_footer = f"{soup.find('span', itemprop='addressLocality').string}, {soup.find('span', itemprop='addressRegion').string}"
    #extracting string information from html code
    category = category_header.string #.contents[0].strip()
    name = name_header.string
    address = address_footer #f'{}'
    zipcode = soup.find('span', itemprop='postalCode').string.strip()
    phone = soup.find('span', itemprop='telephone').string.strip()
    
    #returning a national site instance
    return(NationalSite(category, name, address, zipcode, phone))


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    f = requests.get(state_url)
    html_text = f.text
    soup = BeautifulSoup(html_text, 'html.parser')
    #finding h3 info where all the park information lies
    list_of_parks = soup.find(id='list_parks').find_all('h3')
    list_of_park_instances = []

    #creating a list of site instances by calling get_site_instance on every site url called
    for park in list_of_parks:
        park_tag = park.find('a')
        park_link = f"https://www.nps.gov{park_tag.get('href',None)}"
        #list_string = f"[{count+1}] {get_site_instance(park_link).info()}"
        list_of_park_instances.append(get_site_instance(park_link))
    
    return(list_of_park_instances)

def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    #creating api call url
    base_url = f"http://www.mapquestapi.com/search/v2/radius"
    parameter_dictionary = {'key': key, 'radius': 10, 'maxMatches': 10, 'origin': site_object.zipcode, 'ambiguities': "ignore",'outFormat': "json"}
    
    #requesting info from url
    response = requests.get(base_url, parameter_dictionary)
    
    #loading json file as dict to be passed as return. 
    #this is the point se can store into a cache of state: instance dictionary
    json_str = response.text #cache?
    dict_of_mq_res = json.loads(json_str)

    return dict_of_mq_res


if __name__ == "__main__":
    dictionary = build_state_url_dict()
    dictionary = {k.lower(): v for k, v in dictionary.items()}

    while True:
        #user input for state
        state = input('\nEnter a state name (e.g. Michigan, michigan) or "exit": ')
        #empty list to append site information display
        park_list = []
        ''' cache psuedo code
        cache_dict = json.loads(cache_filename)
        if CACHE_DICT:
            if state in cache_dict
            for count, i in enumerate(cache_dict[state]):
                print ("Using Cache")
                park_list.append(f"[{count+1}] {i.info()}")
        print(park_list)
        '''
        if state.lower() in dictionary:
            for count, i in enumerate(get_sites_for_state(dictionary[state.lower()])):
                #signifies that website is being crawled for populating list instead of cache
                print("Fetching")
                park_list.append(f"[{count+1}] {i.info()}")
            print("\n--------------------------------------------")
            print(f"List of national sites in {state}")
            print("--------------------------------------------")
            #print site information in terminal
            [print(i) for i in park_list]
            while True:
                print("--------------------------------------------")
                #input a number for the 10 nearby places display
                number = input('Choose the number for detail search or "exit" or "back: ')
                if number == "exit" :
                    print("\nGoodbye!")
                    exit()
                elif number == "back":
                    continue
                elif number.isnumeric() and (int(number)-1) in range(len(get_sites_for_state(dictionary[state.lower()]))): #list of instances #state.lower() in dictionary:
                    #access dictionary for site url corresponding to input state
                    site_url = get_sites_for_state(dictionary[state.lower()])[int(number)-1]
                    #calling get nearby places jsontodict return
                    dict_of_mq_res = get_nearby_places(site_url)
                    nearby_list = []
                    #extract name of national park which is called
                    site_name = get_sites_for_state(dictionary[state.lower()])[int(number)-1].name
                    print("\nFetching")
                    print("--------------------------------------------")
                    print(f"Pleaces near {site_name}")
                    print("--------------------------------------------")
                    #loop over the list of dictionaries to find the 10 closest spot to selected site
                    for i in dict_of_mq_res['searchResults']:
                        name = i['fields']['name']
                        if i['fields']['group_sic_code_name']:
                            category = i['fields']['group_sic_code_name']
                        else: category = "no category"
                        if i['fields']['address']:
                            street_address = i['fields']['address']
                        else: street_address = "no address"
                        if i['fields']['city']:
                            street_address = i['fields']['address']
                        else: street_address = "no city"
                        #name_list.append(f"- {name} ({category}) : {street_address}")
                        nearby_list.append(f"- {name} ({category}) : {street_address}")
                    [print(i) for i in nearby_list]
                else:
                    print("[Error] Invalid Input")
        elif state == "exit" :
            print("\nGoodbye!")
            exit()
        else:
            print("\n[Error] Enter proper state name")
        