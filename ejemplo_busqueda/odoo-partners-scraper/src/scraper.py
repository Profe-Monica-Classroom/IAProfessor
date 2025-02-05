import requests
from bs4 import BeautifulSoup
import pandas as pd

def fetch_partners_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_countries_data(html):
    soup = BeautifulSoup(html, 'html.parser')
    countries_data = {}
    
    for country_section in soup.find_all('a', class_='dropdown-item'):
        try:
            # Extract the country name and number of partners
            country_name = country_section.contents[0].strip()
            country_number_span = country_section.find('span', class_='badge')
            
            if country_number_span:
                country_number = country_number_span.text.strip()
                countries_data[country_name] = country_number
            else:
                print(f"Warning: No badge found for {country_name}")
        
        except Exception as e:
            print(f"Error processing section: {country_section}")
            print(e)

    return countries_data

def save_to_excel(data, filename):
    df = pd.DataFrame(list(data.items()), columns=['Country', 'Number'])
    df.to_excel(filename, index=False)

def main():
    url = 'https://www.odoo.com/partners'  # Replace with the actual URL
    html = fetch_partners_data(url)
    countries_data = parse_countries_data(html)
    
    for country, number in countries_data.items():
        print(f'{country}: {number}')
    
    save_to_excel(countries_data, 'countries_data.xlsx')
    print('Data saved to countries_data.xlsx')

if __name__ == '__main__':
    main()