import pycurl
import stem.process
import io

SOCKS_PORT = 9050


output = io.BytesIO()

curl = pycurl.Curl()
curl.setopt( pycurl.URL, 'http://www.example.com' )
curl.setopt( pycurl.PROXY, 'localhost' )
curl.setopt( pycurl.PROXYPORT, SOCKS_PORT )
curl.setopt( pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5 )
curl.setopt( pycurl.WRITEFUNCTION, output.write)
curl.setopt(pycurl.HTTPHEADER, ['X-Requested-With: XMLHttpRequest', 'referer: http://www.meendo.net/?partner=13026'])
#curl.set_option(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36")
curl.setopt(pycurl.FOLLOWLOCATION, 1)

curl.perform()

print("RESULT : " + output.getvalue().decode('ascii'))
output.close() # free used memory