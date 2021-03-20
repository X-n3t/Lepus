import requests
from bs4 import BeautifulSoup
from termcolor import colored


def init(domain):
	FSD = []

	print(colored("[*]-Searching FindSubdomains...", "yellow"))

	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"}
	url = "https://findsubdomains.com/subdomains-of/{}".format(domain)

	try:
		response = requests.get(url, headers=headers, verify=False)
		name_soup = BeautifulSoup(response.text, "html.parser")

		for link in name_soup.findAll("a", {"class": "aggregated-link"}):
			try:
				if link.string is not None:
					FSD.append(link.string.strip())

			except KeyError as errk:
				print("  \__", colored(errk, "red"))
				return []

		FSD = set(FSD)

		print("  \__ {0}: {1}".format(colored("Unique subdomains found", "cyan"), colored(len(FSD), "yellow")))
		return FSD

	except requests.exceptions.RequestException as err:
		print("  \__", colored(err, "red"))
		return []

	except requests.exceptions.HTTPError as errh:
		print("  \__", colored(errh, "red"))
		return []

	except requests.exceptions.ConnectionError as errc:
		print("  \__", colored(errc, "red"))
		return []

	except requests.exceptions.Timeout as errt:
		print("  \__", colored(errt, "red"))
		return []

	except Exception:
		print("  \__", colored("Something went wrong!", "red"))
		return []
