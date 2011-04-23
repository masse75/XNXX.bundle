import re, time, random

NAME = 'XNXX'
randomArt = random.randint(1,3)
ART = 'artwork-'+str(randomArt)+'.jpg'
ICON = 'icon-default.png'

XNXX_BASE = 'http://www.xnxx.com'
XNXX_VIDEO = 'http://video.xnxx.com'
XNXX_NEW = 'http://video.xnxx.com/new/%s/'
XNXX_BESTOF = 'http://video.xnxx.com/best/%s/'
XNXX_HOT = 'http://video.xnxx.com/hot/%s/'
XNXX_HITS = 'http://video.xnxx.com/hits/%s/'
XNXX_SEARCH = 'http://video.xnxx.com/?k=%s&p=%s'

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'


####################################################################################################

def Start():
	Plugin.AddPrefixHandler('/video/xnxx', MainMenu, NAME, ICON, ART)
	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
	Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')

	MediaContainer.title1 = NAME
	MediaContainer.art = R(ART)

	DirectoryItem.thumb = R(ICON)
	VideoItem.thumb = R(ICON)

	HTTP.CacheTime = 3600
	HTTP.Headers['User-Agent'] = USER_AGENT


####################################################################################################

def Thumb(url):
	try:
		data = HTTP.Request(url).content
		return DataObject(data, 'image/jpeg')
	except:
		return Redirect(R(ICON))


####################################################################################################

def MainMenu():
	dir = MediaContainer()
	dir.Append(Function(DirectoryItem(MovieList, L('Most Viewed')), url=XNXX_BASE, mainTitle='Most Viewed', pageFormat='homepage'))
	dir.Append(Function(DirectoryItem(MovieList, L('New Videos')), url=XNXX_NEW, mainTitle='New Videos'))
	dir.Append(Function(DirectoryItem(MovieList, L('Best Of')), url=XNXX_BESTOF, mainTitle='Best Of'))
	dir.Append(Function(DirectoryItem(MovieList, L('Hot!')), url=XNXX_HOT, mainTitle='Hot!', pageFormat='hot'))
	dir.Append(Function(DirectoryItem(MovieList, L('Hits')), url=XNXX_HITS, mainTitle='Hits'))
	dir.Append(Function(DirectoryItem(CategoriesMenu, L('Categories'))))
	dir.Append(Function(InputDirectoryItem(Search, L('Search'), L('Search'), thumb=R(ICON)), url=XNXX_SEARCH))
	return dir

def CategoriesMenu(sender):
	dir = MediaContainer(title2 = sender.itemTitle)
	pageContent = HTML.ElementFromURL(XNXX_BASE)
	for categoryItem in pageContent.xpath('//table/tr/td/p[@style="font-size:17px;"]/a[contains(@href, "video.xnxx.com")]'):
		categoryItemTitle = categoryItem.text.strip()
		categoryItemUrl = categoryItem.get('href')
		if categoryItemUrl.count('tags') > 0:
			pageFormat = 'tags'
			categoryItemUrl = categoryItemUrl+'/%s/'
		else:
			pageFormat = 'categories'
			categoryItemUrl = categoryItemUrl.replace('/c/','/c/%s/')
		if categoryItemTitle.count('More...') == 0:
			dir.Append(Function(DirectoryItem(MovieList, L(categoryItemTitle)), url=categoryItemUrl, mainTitle=categoryItemTitle, pageFormat=pageFormat))
	return dir

def MovieList(sender,url,mainTitle='',searchQuery='',pageFormat='normal',page=0):
	pageShow = page+1
	searchQueryNice = searchQuery.replace('+',' ').capitalize()
	catTags = ['tags','categories']
	xpathInitGroup = ['tags','search']

	if page > 0:
		if pageFormat in catTags:
			dir = MediaContainer(title2 = 'Category: '+mainTitle+' | Page: '+str(pageShow), replaceParent=(page>0))
		elif pageFormat == 'search':
			dir = MediaContainer(title2 = mainTitle+': '+searchQueryNice+' | Page: '+str(pageShow), replaceParent=(page>0))
		else:
			dir = MediaContainer(title2 = mainTitle+' | Page: '+str(pageShow), replaceParent=(page>0))
	else:
		if pageFormat in catTags:
			dir = MediaContainer(title2 = 'Category: '+mainTitle)
		elif pageFormat == 'search':
			dir = MediaContainer(title2 = mainTitle+': '+searchQueryNice)
		else:
			dir = MediaContainer(title2 = mainTitle)

	if pageFormat == 'hot':
		if page < 1:
			url = url.replace('%s/','')
			pageContent = HTML.ElementFromURL(url)
		else:
			pageContent = HTML.ElementFromURL(url % str(page))
	elif pageFormat == 'homepage':
		pageContent = HTML.ElementFromURL(url)
	elif pageFormat == 'search':
		try:
			pageContent = HTML.ElementFromURL(url % (searchQuery, str(page)))
		except:
			pageContent = HTML.ElementFromURL(url % str(page))
	else:
		pageContent = HTML.ElementFromURL(url % str(page))

	if page > 0:
		pageM = page-1
		if len(pageContent.xpath('//div[@id="pag"]/a[@class="nP"]')) > 0:
			prvUrl = XNXX_VIDEO+pageContent.xpath('//div[@id="pag"]/a[@class="nP"]')[0].get('href')
			if pageFormat == 'search':
				prvUrl = prvUrl.replace('?k='+searchQuery,'?k=%s')
				prvUrl = prvUrl.replace('&p='+str(pageM),'&p=%s')
			else:
				prvUrl = prvUrl.replace('/'+str(pageM),'/%s')
			dir.Append(Function(DirectoryItem(MovieList, L('+++Previous Page ('+str(pageM)+')+++')), url=prvUrl, searchQuery=searchQuery, mainTitle=mainTitle, pageFormat=pageFormat, page=pageM))

	if pageFormat in xpathInitGroup:
		initialXpath = '//td[@width="183"]'
	else:
		initialXpath = '//div[@align="center"]/span[@style="font-size:12px"]'
	for videoItem in pageContent.xpath(initialXpath):
		if pageFormat == 'homepage':
			if len(videoItem.xpath('div[@class="t_all"]/span')) > 0:
				videoItemTitle = videoItem.xpath('div[@class="t_all"]/span')[0].text.strip()
			else:
				videoItemTitle = 'SORRY! No Title for this Video!'
			if len(videoItem.xpath('a[@class="miniature"]')) > 0:
				videoItemLink  = videoItem.xpath('a[@class="miniature"]')[0].get('href')
			else:
				videoItemLink = ''
			if len(videoItem.xpath('a[@class="miniature"]/img')) > 0:
				videoItemThumb = videoItem.xpath('a[@class="miniature"]/img')[0].get('src')
			else:
				videoItemThumb = ''
			if len(videoItem.xpath('div[@class="t_all"]/font')) > 0:
				videoItemExtra = videoItem.xpath('div[@class="t_all"]/font')[0].text.strip().replace('min sex rated ','')
				videoItemExtraA = videoItemExtra.split(' ')
				if len(videoItemExtraA) == 2:
					videoItemDuration = int(videoItemExtraA[0])*60
					videoItemDurationTxt = str(videoItemExtraA[0])+':00'
					videoItemRating = round((float(videoItemExtraA[1].strip('%'))/10),2)
				elif len(videoItemExtraA) == 3:
					videoItemDuration = int(videoItemExtraA[0].strip('h'))*3600+int(videoItemExtraA[1])*60
					videoItemDurationTxt = str(videoItemExtraA[0].strip('h'))+':'+str(videoItemExtraA[1])+':00'
					videoItemRating = round((float(videoItemExtraA[2].strip('%'))/10),2)
				else:
					videoItemDuration = 0
					videoItemDurationTxt = 'n/a'
					videoItemRating = 0
			else:
				videoItemDuration = 0
				videoItemDurationTxt = 'n/a'
				videoItemRating = 0
			videoItemSummary = 'Duration: ' + str(videoItemDurationTxt)+' in sec: '+str(videoItemDuration)
			videoItemSummary += '\r\nRating: ' + str(videoItemRating)
		else:
			if len(videoItem.xpath('a/span')) > 0:
				videoItemTitle = videoItem.xpath('a/span')[0].text.strip()
			else:
				videoItemTitle = videoItem.xpath('span[contains(@style, "text-decoration:underline;")]')[0].text.strip()
			if len(videoItem.xpath('a[@class="miniature"]')) > 0:
				videoItemLink  = videoItem.xpath('a[@class="miniature"]')[0].get('href')
			else:
				videoItemLink = videoItem.xpath('script')[0].text.strip()
				videoItemLink = re.compile('<a href=\"(.+?)\"').findall(videoItemLink, re.DOTALL)
				videoItemLink = videoItemLink[0]
			if len(videoItem.xpath('a[@class="miniature"]/img')) > 0:
				videoItemThumb = videoItem.xpath('a[@class="miniature"]/img')[0].get('src')
			else:
				videoItemThumb = videoItem.xpath('script')[0].text.strip()
				videoItemThumb = re.compile('<img src=\"(.+?)\"').findall(videoItemThumb, re.DOTALL)
				videoItemThumb = videoItemThumb[0]
			if len(videoItem.xpath('a/font')) > 0:
				videoItemExtra = videoItem.xpath('a/font')[0].text.strip().replace('min sex rated ','')
				videoItemExtraA = videoItemExtra.split(' ')
				if len(videoItemExtraA) == 2:
					videoItemDuration = int(videoItemExtraA[0])*60
					videoItemDurationTxt = str(videoItemExtraA[0])+':00'
					videoItemRating = round((float(videoItemExtraA[1].strip('%'))/10),2)
				elif len(videoItemExtraA) == 3:
					videoItemDuration = int(videoItemExtraA[0].strip('h'))*3600+int(videoItemExtraA[1])*60
					videoItemDurationTxt = str(videoItemExtraA[0].strip('h'))+':'+str(videoItemExtraA[1])+':00'
					videoItemRating = round((float(videoItemExtraA[2].strip('%'))/10),2)
				else:
					videoItemDuration = 0
					videoItemDurationTxt = 'n/a'
					videoItemRating = 0
			else:
				videoItemDuration = 0
				videoItemDurationTxt = 'n/a'
				videoItemRating = 0
			videoItemSummary = 'Duration: ' + str(videoItemDurationTxt)+' in sec: '+str(videoItemDuration)
			videoItemSummary += '\r\nRating: ' + str(videoItemRating)
		dir.Append(Function(VideoItem(PlayVideo, title=videoItemTitle, summary=videoItemSummary, duration=videoItemDuration, rating=videoItemRating, thumb=Function(Thumb, url=videoItemThumb)), url=videoItemLink))
	#Get nextPagination
	pageP = page+1
	if len(pageContent.xpath('//div[@id="pag"]/a[@class="nP"]')) > 1:
		nxtUrl = XNXX_VIDEO+pageContent.xpath('//div[@id="pag"]/a[@class="nP"]')[1].get('href')
		if pageFormat == 'search':
			nxtUrl = nxtUrl.replace('?k='+searchQuery,'?k=%s')
			nxtUrl = nxtUrl.replace('&p='+str(pageP),'&p=%s')
		else:
			nxtUrl = nxtUrl.replace('/'+str(pageP),'/%s')
		dir.Append(Function(DirectoryItem(MovieList, L('+++Next Page ('+str(pageP)+')+++')), url=nxtUrl, searchQuery=searchQuery, mainTitle=mainTitle, pageFormat=pageFormat, page=pageP))
	return dir

def Search(sender,url,query='',mainTitle='Search', pageFormat='search'):
	dir = MediaContainer()
	searchQueryCorrect = query.replace(' ','+')
	dir = MovieList(sender=None, url=url, searchQuery=searchQueryCorrect, mainTitle=mainTitle, pageFormat=pageFormat)
	return dir


####################################################################################################

def PlayVideo(sender, url):
	content = HTTP.Request(url).content
	vidurl = re.compile('&amp;flv_url=(.+?)&amp;').findall(content, re.DOTALL)
	if len(vidurl) > 0:
		gotovidurl = String.Unquote(vidurl[0])
		Log(gotovidurl)
		return Redirect(gotovidurl)
	else:
		return None
