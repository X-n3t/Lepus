import requests
from termcolor import colored
from configparser import RawConfigParser


def init(domain):
	DT = []

	print(colored("[*]-Searching DNSTrails...", "yellow"))

	parser = RawConfigParser()
	parser.read("config.ini")
	DNSTrails_API_KEY = parser.get("DNSTrails", "DNSTRAILS_API_KEY")

	if DNSTrails_API_KEY == "":
		print("  \__", colored("No DNSTrails API key configured", "red"))
		return []

	else:
		headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36", "content-type": "application/json", "APIKEY": DNSTrails_API_KEY}
		url = "https://api.securitytrails.com/v1/domain/{}/subdomains".format(domain)

		try:
			response = requests.get(url, headers=headers)

			if response.status_code == 429:
				print("  \__", colored("You've exceeded the usage limits for your account.", "red"))
				return []

			else:
				payload = response.json()

			for k, v in list(payload.items()):
				if v:
					for dnsvalue in v:
						DT.append(".".join([dnsvalue, domain]))

			DT = set(DT)

			print("  \__ {0}: {1}".format(colored("Subdomains found", "cyan"), colored(len(DT), "yellow")))
			return DT

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
