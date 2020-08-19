"""
    some function tools
"""
import sys
import traceback
import urllib

def quote(s):
    return s.replace('@', '%AT%').replace('.', '%DOT%').replace(' ', '%SPACE%')

def unquote(s):
    return s.replace('%AT%', '@').replace('%DOT%', '.').replace('%SPACE%', ' ')

def parse_query_string(s):
    s = urllib.request.unquote(s)
    s = unquote(s)
    if s[0] == '?':
        s = s[1:]
    s = s.split('&')
    s = map(lambda x: x.split('='), s)
    ret = {}
    for item in s:
        ret[item[0]] = item[1]
    return ret

def gen_query_string(d):
    s = '?'
    for k in d:
        v = d[k]
        k = quote(urllib.request.quote(str(k)))
        v = quote(urllib.request.quote(str(v)))
        s += (k+'='+v + '&')
    if s.endswith('&'):
        s = s[:-1]
    return s

if __name__ == '__main__':
    d={}
    d['name'] = 'software'
    d['age'] = 20
    d['mail'] = 'software@gmail.com'
    parse_query_string(gen_query_string(d))
