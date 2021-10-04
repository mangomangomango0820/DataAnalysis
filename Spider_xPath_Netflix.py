import requests
from lxml import etree

# 1. grab the content of page
url = "https://www.netflix.com/browse/genre/34399"       # target url
content = requests.get(url).content.decode('UTF-8')      # charset="utf-8"


# 2. use xPath to catch html content
etreeHtml = etree.HTML(content)
list = etreeHtml.xpath("//span")


# 3. loop through target patterns
# for i in range(len(list)):
for i in range(12):
    JD = {}
    # /html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][3]/h2[@class='nm-collections-row-name']/a[@class='nm-collections-link']/span[@class='nm-collections-row-name']
    # /html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][15]/h2[@class='nm-collections-row-name']/a[@class='nm-collections-link']/span[@class='nm-collections-row-name']
    # /html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][13]/h2[@class='nm-collections-row-name']/a[@class='nm-collections-link']/span[@class='nm-collections-row-name']
    tab = list[i].xpath("/html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][*]/h2[@class='nm-collections-row-name']/a[@class='nm-collections-link']/span[@class='nm-collections-row-name']")[i].text
    if not tab == None:
        print('*' * 5, i)
        JD['tab'] = tab
        print(JD)

for i in range(1124):
    JD = {}
    # /html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][14]/div[@class='nm-content-horizontal-row']/ul[@class='nm-content-horizontal-row-item-container']/li[@class='nm-content-horizontal-row-item'][1]/a[@class='nm-collections-title nm-collections-link']/span[@class='nm-collections-title-name']
    # /html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][15]/div[@class='nm-content-horizontal-row']/ul[@class='nm-content-horizontal-row-item-container']/li[@class='nm-content-horizontal-row-item'][2]/a[@class='nm-collections-title nm-collections-link']/span[@class='nm-collections-title-name']
    print('*' * 5, i)
    movie = list[i].xpath("/html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][*]/div[@class='nm-content-horizontal-row']/ul[@class='nm-content-horizontal-row-item-container']/li[@class='nm-content-horizontal-row-item'][*]/a[@class='nm-collections-title nm-collections-link']/span[@class='nm-collections-title-name']")[i].text
    JD['movie'] = movie
    url = list[i].xpath("/html/body/div[@id='appMountPoint']/div[@class='basicLayout browseTitlesGallery dark']/div[@class='nm-collections-page']/main[@class='nm-collections-container with-blur']/section[@class='nm-collections-row'][*]/div[@class='nm-content-horizontal-row']/ul[@class='nm-content-horizontal-row-item-container']/li[@class='nm-content-horizontal-row-item'][*]/a/@href")[i]
    JD['url'] = url
    print(JD)
