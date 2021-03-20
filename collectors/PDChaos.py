import requests
from json import loads
from termcolor import colored
from configparser import RawConfigParser


def init(domain):
	PDCH = []

	print(colored("[*]-Searching Project Discovery Chaos API...", "yellow"))

	parser = RawConfigParser()
	parser.read("config.ini")
	CHAOS_KEY = parser.get("Chaos", "CHAOS_KEY")

	if CHAOS_KEY == "":
		print("  \__", colored("No Project Discovery Chaos API token configured", "red"))
		return []

	headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36", "Authorization": CHAOS_KEY}
	url = "https://dns.projectdiscovery.io/dns/{0}/subdomains".format(domain)

	try:
		response = requests.get(url, headers=headers).text
		hostnames = [result.split(",")[0] for result in response.split("\n")]
		
		for hostname in hostnames:
			if hostname:
				PDCH.append(hostname)



		PDCH = set(PDCH)

		print("  \__ {0}: {1}".format(colored("Subdomains found", "cyan"), colored(len(PDCH), "yellow")))
		return PDCH

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
