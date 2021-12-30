#!/usr/bin/env python

import requests
import re
import urllib.parse
import bs4

class Scanner:
    def __init__(self, url, ignore_links):
        self.session = requests.Session()
        self.target_url = url
        self.list_of_links = []
        self.links_to_ignore = ignore_links

    def fetch_links(self, url):  # will fetch all links in the target page
        response = self.session.get(url)
        return re.findall('(?:href=")(.*?)"', response.content.decode(errors='ignore'))

    def crawl(self, url=None):
        if url == None:
            url = self.target_url
        links = self.fetch_links(url)
        for link in links:
            link = urllib.parse.urljoin(url, link)

            if '#' in link:
                link = link.split('#')[0]

            if self.target_url in link and link not in self.list_of_links and link not in self.links_to_ignore:
                self.list_of_links.append(link)
                print(link)
                self.crawl(link)

    def fetch_forms(self, url):
        response = self.session.get(url)
        parsed_html = bs4.BeautifulSoup(response.content, features="lxml")
        return parsed_html.findAll('form')

    def submit_forms(self, form, arguments, url):
        method = form.get('method')
        # print('[+] method >>', method)
        action = form.get('action')
        # print('[+] action >>', action, '\n')
        url = urllib.parse.urljoin(url, action)
        data_dictionary = {}

        input_list = form.findAll('input')
        for input in input_list:
            name = input.get('name')
            # print('[+] input_name >>', name)
            type = input.get('type')
            # print('[+] input_type >>', type)
            value = input.get('value')
            # print('[+] input_value >>', value, '\n')
            if type == 'text':
                value = arguments

            data_dictionary['target_host'] = value

        if method == 'post' or 'POST':
            return self.session.post(url, data=data_dictionary)
        return self.session.get(url, params=data_dictionary) # can also use params instead of 'data=...'

    def search_xss(self):
        for link in self.list_of_links:
            forms = self.fetch_forms(link)
            for form in forms:
                print('\n[+] Testing form inside >>', link)
                vuln_in = self.search_for_xss_in_form(form, link)
                if vuln_in:
                    print('\n[*] XSS-vulnerability found !! in form of >>', link, '\n')
                    print(form, '\n')

            if '=' in link:
                print('\n[+] Testing link >>', link)
                vuln_in = self.search_for_xss_in_link(link)
                if vuln_in:
                    print('\n[*] XSS-vulnerability found !! in >>', link, '\n')

    def search_for_xss_in_form(self, form, url):
        script = '<sCript>alert("hello")</scriPt>'
        response = self.submit_forms(form, script, url)
        return b'script' in response.content

    def search_for_xss_in_link(self, url):
        script = '<sCript>alert("hello")</scriPt>'
        url = url.replace('=', '=' + script)
        response = self.session.get(url)
        return b'script' in response.content