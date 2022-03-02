# coding:utf:8

import re
import urllib.parse
import urllib.request


class YtbRequests:
    error = 0

    @staticmethod
    def SearchInYtbChannel (url):
        final = []
        verif = False
        error = 0

        htm_content = urllib.request.urlopen (url + "/video")
        txt = htm_content.read ().decode ()

        while verif is False:
            # channel avatar
            try:
                results = []
                pattern = re.compile (r'channel-header-profile-image" src="(.{90,96})"')
                matches = pattern.finditer (txt)
                for match in matches:
                    coordonees = match.span ()
                    results.append (txt [coordonees [0]:coordonees [1]])
                thumb = (results [0]).split ('"')
                verif = True
                final.append (thumb [2])
            except:
                final.append('N/A')
                YtbRequests.error += 1
            # channel name
            try:
                results = []
                pattern = re.compile (r'"name": "(.{1,16})"')
                matches = pattern.finditer (txt)
                for match in matches:
                    coordonees = match.span ()
                    results.append (txt [coordonees [0]:coordonees [1]])
                name = (results [0]).split ('"')
                final.append (name [3])
            except:
                YtbRequests.error += 1
            # folower count
            try:
                pattern = re.compile (r'subscribed yt-uix-tooltip" title="(.{10,30})"')
                matches = pattern.finditer (txt)
                results = []
                for match in matches:
                    coordonees = match.span ()
                    results.append (txt [coordonees [0]:coordonees [1]])
                folow = (results [0]).split ('"')
                final.append (folow [2])
            except:
                YtbRequests.error += 1
            # vurl
            try:
                pattern = re.compile (r'href="/watch\?v=(.{11})"')
                matches = pattern.finditer (txt)
                results = []
                for match in matches:
                    coordonees = match.span ()
                    results.append (txt [coordonees [0]:coordonees [1]])
                try:
                    vurl = (results [1]).split ('"')
                    final.append ("https://www.youtube.com" + vurl [1])
                except:
                    final.append("N/A")
            except:
                YtbRequests.error += 1

            url = url.split ("/")
            final.append (url [4])
            return final

    @staticmethod
    def SearchYtbVideo (search):
        verif = False
        while verif is False:
            try:
                query_string = search.replace (" ", "+")
                htm_content = urllib.request.urlopen (
                    'https://www.youtube.com/results?search_query=' + query_string
                )
                search_results = re.findall ('href=\"\\/watch\\?v=(.{11})', htm_content.read ().decode ())
                verif = True
                return "https://www.youtube.com{}".format (search_results [0])
            except:
                YtbRequests.error += 1

    @staticmethod
    def SearchYtbChannel (search):
        query_string = search.replace (" ", "+")
        htm_content = urllib.request.urlopen (
            'https://www.youtube.com/results?search_query={}&sp=CAMSAhAC'.format (query_string)
        )
        search_resultS = re.findall ('href="\\/(.{32})', htm_content.read ().decode ())
        try:
            search_results = search_resultS [32]
            search_results = search_results.split (" ", 1)
            search_results = str (search_results [0])
            search_results = search_results.split ('"', 1)
            result = "https://www.youtube.com/{}".format (search_results [0])
        except:
            search_results = search_resultS [32]
            result = "https://www.youtube.com/{}".format (search_results)
        return str (result)

