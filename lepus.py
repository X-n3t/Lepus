#!/usr/bin/env python3
# 3.3.2
# ZephrFish Patch
from argparse import ArgumentParser, FileType
from warnings import simplefilter
from termcolor import colored
from time import sleep
from gc import collect
import collectors.Censys
import collectors.CertSpotter
import collectors.CRT
import collectors.DNSTrails
import collectors.EntrustCertificates
import collectors.GoogleTransparency
import collectors.HackerTarget
import collectors.PassiveTotal
import collectors.ProjectSonar
import collectors.Riddler
import collectors.Shodan
import collectors.Spyse
import collectors.ThreatCrowd
import collectors.VirusTotal
import collectors.WaybackMachine
import submodules.Permutations
import submodules.PortScan
import submodules.ReverseLookups
import submodules.TakeOver
import utilities.DatabaseHelpers
import utilities.MiscHelpers
import utilities.ScanHelpers

simplefilter("ignore")
version = "3.3.2"


def printBanner():
	print(colored("         ______  _____           ______", "yellow"))
	print(colored(" |      |______ |_____) |     | (_____ ", "yellow"))
	print(colored(" |_____ |______ |       |_____| ______)", "yellow"))
	print(colored("                                v{0}".format(version), "cyan"))
	sleep(1)


if __name__ == "__main__":
	parser = ArgumentParser(prog="lepus.py", description="Infrastructure OSINT")
	parser.add_argument("domain", help="domain to search")
	parser.add_argument("-w", "--wordlist", action="store", dest="wordlist", help="wordlist with subdomains", type=FileType("r"))
	parser.add_argument("-hw", "--hide-wildcards", action="store_true", dest="hideWildcards", help="hide wildcard resolutions", default=False)
	parser.add_argument("-t", "--threads", action="store", dest="threads", help="number of threads [default is 100]", type=int, default=100)
	parser.add_argument("-nc", "--no-collectors", action="store_true", dest="noCollectors", help="skip passive subdomain enumeration", default=False)
	parser.add_argument("-zt", "--zone-transfer", action="store_true", dest="zoneTransfer", help="attempt to zone transfer from identified name servers", default=False)
	parser.add_argument("--permutate", action="store_true", dest="permutate", help="perform permutations on resolved domains", default=False)
	parser.add_argument("-pw", "--permutation-wordlist", dest="permutation_wordlist", help="wordlist to perform permutations with [default is lists/words.txt]", type=FileType("r"), default="lists/words.txt")
	parser.add_argument("--reverse", action="store_true", dest="reverse", help="perform reverse dns lookups on resolved public IP addresses", default=False)
	parser.add_argument("-r", "--ranges", action="store", dest="ranges", help="comma seperated ip ranges to perform reverse dns lookups on", type=str, default=None)
	parser.add_argument("--portscan", action="store_true", dest="portscan", help="scan resolved public IP addresses for open ports", default=False)
	parser.add_argument("-p", "--ports", action="store", dest="ports", help="set of ports to be used by the portscan module [default is medium]", type=str)
	parser.add_argument("--takeover", action="store_true", dest="takeover", help="check identified hosts for potential subdomain take-overs", default=False)
	parser.add_argument("-v", "--version", action="version", version="Lepus v{0}".format(version))
	args = parser.parse_args()

	if not utilities.MiscHelpers.checkArgumentValidity(parser, args):
		exit(1)

	printBanner()

	try:
		db = utilities.DatabaseHelpers.init()
		utilities.ScanHelpers.retrieveDNSRecords(db, args.domain)
		old_resolved, old_unresolved, old_takeovers = utilities.MiscHelpers.loadOldFindings(db, args.domain)
		utilities.MiscHelpers.purgeOldFindings(db, args.domain)

		if args.zoneTransfer:
			zt_subdomains = utilities.ScanHelpers.zoneTransfer(db, args.domain)

		else:
			zt_subdomains = None

		if args.noCollectors:
			collector_subdomains = None

		else:
			print()
			collector_subdomains = []
			collector_subdomains += collectors.Censys.init(args.domain)
			collector_subdomains += collectors.CertSpotter.init(args.domain)
			collector_subdomains += collectors.CRT.init(args.domain)
			collector_subdomains += collectors.DNSTrails.init(args.domain)
			collector_subdomains += collectors.EntrustCertificates.init(args.domain)
			collector_subdomains += collectors.GoogleTransparency.init(args.domain)
			collector_subdomains += collectors.HackerTarget.init(args.domain)
			collector_subdomains += collectors.PassiveTotal.init(args.domain)
			collector_subdomains += collectors.ProjectSonar.init(args.domain)
			collector_subdomains += collectors.Riddler.init(args.domain)
			collector_subdomains += collectors.Shodan.init(args.domain)
			collector_subdomains += collectors.Spyse.init(args.domain)
			collector_subdomains += collectors.ThreatCrowd.init(args.domain)
			collector_subdomains += collectors.VirusTotal.init(args.domain)
			collector_subdomains += collectors.WaybackMachine.init(args.domain)

		if args.wordlist:
			wordlist_subdomains = utilities.MiscHelpers.loadWordlist(args.domain, args.wordlist)

		else:
			wordlist_subdomains = None

		findings = utilities.MiscHelpers.cleanupFindings(args.domain, old_resolved, old_unresolved, zt_subdomains, collector_subdomains, wordlist_subdomains)

		del old_unresolved
		del zt_subdomains
		del collector_subdomains
		del wordlist_subdomains
		collect()

		if findings:
			utilities.ScanHelpers.identifyWildcards(db, findings, args.domain, args.threads)
			utilities.ScanHelpers.massResolve(db, findings, args.domain, args.hideWildcards, args.threads)

			del findings
			collect()

			if args.permutate:
				submodules.Permutations.init(db, args.domain, args.permutation_wordlist, args.hideWildcards, args.threads)

			if args.reverse:
				submodules.ReverseLookups.init(db, args.domain, args.ranges, args.threads)

			utilities.ScanHelpers.massRDAP(db, args.domain, args.threads)

			if args.portscan:
				submodules.PortScan.init(db, args.domain, args.ports, args.threads)

			if args.takeover:
				submodules.TakeOver.init(db, args.domain, old_takeovers, args.threads)

		utilities.MiscHelpers.exportFindings(db, args.domain, old_resolved)

	except KeyboardInterrupt:
		print(colored("\n[*]-Received keyboard interrupt! Shutting down...\n", "red"))
		exit(-1)
