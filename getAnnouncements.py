#!/usr/bin/env python
# -*- coding: utf-8 -*-

#git init
#git add FILE
#git commit -m ''
#git remote add origin git@github.com:epistimos/INEX.git
#git push origin master -gia anevasma
#git pull oriogin master -gia katevasma

import io,os,glob,sys,re,time,codecs
from datetime import datetime
import socket
import urllib2

#me to RSS page xanoume to eidos tis anakoinwsis kai tin akrivi wra apo ton html
#code alla glitwnoume to next page xamaliki

def downloadRSS(directory,url):
	enc = ''
	print ("--> Searching..."+url)

	try:
		opener = urllib2.build_opener()
		opener.addheaders = [('User-agent', 'Chromium/13.0.782.215')]
		instream = opener.open(url)
	except urllib2.URLError as u:
		print (url+'\t'+"URL error")

	except urllib2.HTTPError as h:
		print(url+'\t'+"HTTP error")

	try: code = instream.read()
	except socket.timeout as s:
		print(url+'\t'+"TIMEOUT error")
	
	if code.lower().find('=iso-8859-7')>0:
		enc = 'iso-8859-7'
	elif code.lower().find('=windows-1253')>0:
		enc = 'windows-1253'
	else:
		enc = 'utf-8'

	return code
	
def parseRSS(directory,hosp,sourcecode,today):
	#<description>
	#<b>Θέμα:   </b>... <br/>
	#<b>Ημ/νια: </b>xx/xx/xxxx<br/>
	#<b>Φορέας: </b> ... <br/>
	#<b>ΑΔΑ:    </b>...<br/> #!!!!http://static.diavgeia.gov.gr/doc/
	#</description>

	buf = open(directory+"rss_"+str(today).replace('/','_')+".txt",'a')
	
	start = '<description>'
	end = '</description>'
	
	while sourcecode.find(start)>0 and sourcecode.find(end)>0:
		a = sourcecode.find(start)
		b = sourcecode.find(end)

		if b>a:
			trap = sourcecode[a+len(start):b]
			if trap.startswith('Αποφάσεις'):
				sourcecode = sourcecode[b+len(end):]
				continue
			else:
				#announcement = trap.usplit('&#13;')#<br/>
				#announcement=re.compile("(&#13;)",re.UNICODE).split(unicode(trap,'utf-8'))
				trap = trap.replace('&lt;br/&gt;','\n')
				trap = trap.replace('&lt;b&gt;','')
				trap = trap.replace('&lt;/b&gt;','')
				original = trap
				
				annName = trap[trap.index('Θέμα: ')+len('Θέμα: '):trap.index('\n')]
				trap = trap[trap.index('\n')+1:]
				annDate = trap[trap.index('Ημ/νια: ')+len('Ημ/νια: '):trap.index('\n')]
				if annDate==today:
					trap = trap[trap.index('\n')+1:]
					annHosp = trap[trap.index('Φορέας: ')+len('Φορέας: '):trap.index('\n')]
					trap = trap[trap.index('\n')+1:]
					annDoc = trap[trap.index('ΑΔΑ: ')+len('ΑΔΑ: '):trap.index('\n')]
					annURL = hosp[:-3]+'ada/'+annDoc
					annDocURL = 'http://static.diavgeia.gov.gr/doc/'+annDoc
					
					#print '%s\n%s\n%s\n%s\n\n' % (annName,annDate,annHosp,annDocURL)
					buf.write('%s\n%s\n%s\n%s\n%s\n%s\n\n' % (annHosp,hosp,annDate,annName,annURL,annDocURL))
				else:
					pass
			
			sourcecode = sourcecode[b+len(end):]
		else:
			sourcecode = sourcecode[b+len(end):]

	#print("--> Total number of available links: ", self.numOfUrls)
	
if __name__=='__main__':
	start_time = time.time()
	
	now = datetime.now()
	today = now.strftime("%d/%m/%Y")
	
	directory=sys.argv[1]
	rssURLs = sys.argv[2]
	hosp_links = open(directory+rssURLs,'r',).readlines()
	for hosp in hosp_links:
		sc = downloadRSS(directory,hosp.strip())
		
		#check current date vs. announcements page status!
		ddate = sc[sc.find('<lastBuildDate>')+15:sc.find('</lastBuildDate>')]
		d = datetime.strptime(ddate[5:-6],"%d %b %Y %H:%M:%S")
		rssDate = d.strftime('%d/%m/%Y')

		if today==rssDate:
			print 'NEW ANNOUNCEMENTS FOUND...'
			parseRSS(directory,hosp.strip(),sc,today)
		else:
			print 'NOTHING NEW FOUND...'

	end_time = time.time()
	elapsed_time = (end_time - start_time)/60
	print ('... time elapsed: ', '%3.2f' %elapsed_time,' minute(s)')
