from bs4 import BeautifulSoup
import requests


def get_top_holdings(etf):

	url = 'https://www.spdrs.com/product/fund.seam?ticker={0}'

	r = requests.get(url.format(etf))

	soup = BeautifulSoup(r.text).find('div', class_='sect fund_top_holdings')

	holdings = soup.find_all('td', class_='label')

	holding_dict = {i: holdings[i].contents[0] for i in range(len(holdings))}

	data = soup.find_all('td', class_='data')

	weight_dict = {i/2 : float(data[i].contents[0].rstrip('%')) for i in range(0, len(data), 2)}

	shares_dict = {(i-1)/2 : int(data[i].contents[0].replace(',','')) for i in range(1, len(data), 2)}

	top_holdings = {'holding' : holding_dict, 'weight' : weight_dict, 'shares' : shares_dict}

	print top_holdings

	return top_holdings


def get_country_weights(etf):

	url = 'https://www.spdrs.com/product/fund.seam?ticker={0}'

	r = requests.get(url.format(etf))

	soup = BeautifulSoup(r.text).find('div', id='FUND_COUNTRY_WEIGHTS')

	if soup is None:
		return None

	names = soup.find_all('td', class_='label')

	values = soup.find_all('td', class_='data')

	country_names = {i: names[i].contents[0] for i in range(len(names))}

	country_data = {i: float(values[i].contents[0].rstrip('%')) for i in range(len(values))}

	country_weights = {'country' : country_names, 'weight' : country_data}

	print country_weights

	return country_weights


def get_sector_weights(etf):

	url = 'https://www.spdrs.com/product/fund.seam?ticker={0}'

	r = requests.get(url.format(etf))

	soup = BeautifulSoup(r.text).find('div', id='SectorsAllocChart')

	chart_xml = soup.find('div', style="display: none").contents[0]

	xml_soup = BeautifulSoup(chart_xml, 'xml')

	names = xml_soup.find_all('label')

	values = xml_soup.find_all('value')

	sector_names = {i: names[i].contents[0] for i in range(len(names))}

	sector_data = {i: float(values[i].contents[0].rstrip('%')) for i in range(len(values))}

	sector_weights = {'sector' : sector_names, 'weight' : sector_data}

	print sector_weights

	return sector_weights
    

def main():

    get_top_holdings('SPY')

    get_sector_weights('GMF')

    get_country_weights('GMF')


if __name__ == "__main__":
    main()
