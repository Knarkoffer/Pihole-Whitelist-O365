# PiholeWhitelistO365
Script to grab the DNS names associated with Office 365 (from https://docs.microsoft.com/en-us/microsoft-365/enterprise/urls-and-ip-address-ranges?view=o365-worldwide) and add them to the Pi-Hole whitelist.

Inspired by the excellent (and much neater written) whitelist script by Anudeep found here: [anudeepND/whitelist](https://github.com/anudeepND/whitelist)

### Completed:
- [x] Remove old entries added by this script before any new whitelisting

### Left to do:

- [ ] Flags/switches with argparse (i.e. to allow non-required domains)
- [ ] Debug_print functions (with --verbose mode)
- [ ] Handle wildcard-domains (like *-files.sharepoint.com)

###### _Internal name: Project922-PYTHON-Generate_O365_Whitelist_