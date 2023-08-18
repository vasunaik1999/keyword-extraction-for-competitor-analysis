from fpdf import FPDF
import requests, lxml, json, time, tldextract
from bs4 import BeautifulSoup

# Specifying User Agent
headers = {
"User-Agent":
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3538.102 Safari/537.36 Edge/18.19582"
}

#pdf object declaration
fpdf = FPDF()
fpdf.add_page()
fpdf.set_font("Arial",size=12,)


#List of Keywords, for which it gonna search
#NOTE: AS PER MY OBSERVATION, GOOGLES ADS ARE NOT ALWAYS SHOWN, SO IT MIGHT GIVE EMPTY RESULTS SOMETIMES, IF ITS GIVING EMPTY THAN INCREASE NO OF TIMES
listOfKeywords = [
  "Dinner Cruise Goa",
  "Dinner Cruise Panjim",
  "Best Dinner Cruise Goa",
]
#No of times it gonna search for one keyword
numberOfTimes = 5
resultDict = {}

#To store the respective data scraped
totalCompany = ""
totalTitles = ""
totalDescription = ""

for keyword in listOfKeywords:
  companyList = []
  numOfTopAds = 0
  resultDict[keyword] = {}
  absolute_top = 0
  countIteration = 0

  print(keyword)
  fpdf.cell(0, 5, "", ln=1)
  fpdf.cell(0, 5, "Searched Keyword : "+keyword, ln=1)
  fpdf.cell(0, 5, txt="", ln=1)

  for _ in range(numberOfTimes):
    payload = {'q': keyword}
    html = requests.get("https://www.google.com/search?q=",params=payload,headers=headers)
    status_code = html.status_code

    if status_code == 200:
      response = html.text
      soup = BeautifulSoup(response, 'lxml')

      with open("output.html","w", encoding="utf-8") as file:
        file.write(str(soup))

      topAds = soup.find(id='main')
      if (topAds):
        countIteration = countIteration + 1
        print('---------------- Paid Ads ----------------')
        print("----------- Ads in Search No. ",countIteration, " ----------- ")

        fpdf.cell(0, 5, txt="---------------------------------------------------------- Paid Ads -------------------------------------------------------------" , ln=1)
        test = "---------------------------------------------------- Ads in Search No. "+ str(countIteration)+" ----------------------------------------------------"
        fpdf.cell(0, 5, test , ln=1)
        fpdf.cell(0, 5, "", ln=1)

        if len(topAds.findAll('div',class_='uEierd')) > 0:
          numOfTopAds += 1
        absolute_top = 0
        for container in topAds.findAll('div',class_='uEierd'):
          try:
            advertisementTitle = container.find('div', class_='CCgQ5 MUxGbd v0nnCb aLF0Z OSrXXb').span.text
          except:
            advertisementTitle = 'N/A'
          try:
            company = container.find('span', class_='ob9lvb').text
            company = tldextract.extract(company).domain
          except:
            company = 'N/A'

          if company not in companyList:
            companyList.append(company)
            if absolute_top == 0:
              resultDict[keyword][company] = {'absolute-top':1, 'top':0, 'bottom':0}
            else:
              resultDict[keyword][company] = {'absolute-top':0, 'top':1, 'bottom':0}
          else:
            if absolute_top == 0:
              resultDict[keyword][company]['absolute-top'] += 1
            else:
              resultDict[keyword][company]['top'] += 1

          try:
            productDescription = container.find('div', class_='MUxGbd yDYNvb lyLwlc lEBKkf').text
          except:
            #productDescription = container.find('div', class_='CCgQ5 MUxGbd v0nnCb aLF0Z OSrXXb').span.text
            productDescription = "N/A"


          print("Ads Titles :",advertisementTitle)
          totalTitles = " ".join([totalTitles, advertisementTitle])
          print("Competitor Name :",company)
          totalCompany = " ".join([totalCompany, company])
          print("Ads Description :",productDescription)
          totalDescription = " ".join([totalDescription, productDescription])
          print()

          fpdf.cell(0, 5, txt="Ads Titles : "+advertisementTitle.encode('latin-1', 'replace').decode('latin-1'), ln=1)
          fpdf.cell(0, 5, txt="Competitor Name : "+company.encode('latin-1', 'replace').decode('latin-1'), ln=1)
          fpdf.multi_cell(w=190, h=5, txt="Ads Description : "+productDescription.encode('latin-1', 'replace').decode('latin-1'))
          fpdf.cell(0, 5, txt="", ln=1)

          absolute_top += 1
      time.sleep(1)
      print('------------------------------------------')

      with open("output.html","w", encoding="utf-8") as file:
        file.write(str(soup))

  keys = list(resultDict[keyword].keys())
  for name in ['bottom','top','absolute-top']:
    keys.sort(key=lambda k: resultDict[keyword][k][name],reverse=True)

  resultDict[keyword]['top performers'] = keys
  resultDict[keyword]['total ads'] = numOfTopAds

print(json.dumps(resultDict,indent=4))

print("--------------------------------------------------")
print("--------------------------------------------------")
print("Total Companies Ads: \n", totalCompany)
print("All Combined Titles: \n", totalTitles)
print("ALl Combined Description: \n", totalDescription)

#pdf for Total Titles
fpdf1 = FPDF()
fpdf1.add_page()
fpdf1.set_font("Arial",size=12, )
fpdf1.cell(0, 5,txt="----------------------------------------------------- Compititor Titles --------------------------------------------------------",ln=1)
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.multi_cell(w=190, h=5, txt=totalTitles.encode('latin-1', 'replace').decode('latin-1'))
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.cell(0, 5,txt="-------------------------------------------------- Compititor Description -----------------------------------------------------",ln=1)
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.multi_cell(w=190, h=5, txt=totalDescription.encode('latin-1', 'replace').decode('latin-1'))
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.cell(0, 5,txt="------------------------------------------------------- Compititors ----------------------------------------------------------",ln=1)
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.multi_cell(w=190, h=5, txt=totalCompany.encode('latin-1', 'replace').decode('latin-1'))
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.cell(0, 5, txt="", ln=1)
fpdf1.output("Ads_Paragraph.pdf")

fpdf.output("Ads_Output.pdf")
###########################################################
############################ KEYBERT FOR KEYWORD EXTRACTION
###########################################################

#pdf for Keywords
fpdf2 = FPDF()
fpdf2.add_page()
fpdf2.set_font("Arial",size=12, )
fpdf2.cell(0, 5,txt="--------------------------------------------------------- Keywords ------------------------------------------------------------",ln=1)
fpdf2.cell(0, 5, txt="", ln=1)

from keybert import KeyBERT

fpdf2.cell(0, 5,txt="----------------------------------- Keywords generated from competitors Title --------------------------------------",ln=1)
fpdf2.cell(0, 5, txt="", ln=1)

docTitle = totalTitles
kw_model = KeyBERT()
titleKeyWords = kw_model.extract_keywords(docTitle, keyphrase_ngram_range=(3, 7), stop_words='english', use_mmr=True, diversity=0.6, top_n=15)
print("Keywords generated from competitors Title :\n")
for kws in titleKeyWords:
  for kw in kws:
    print(kw, end=", ")
    try:
      fpdf2.cell(100, 5, txt=kw.encode('latin-1', 'replace').decode('latin-1'))
    except:
      fpdf2.cell(0, 5, txt=str(kw), ln=1)
      continue
  print()

fpdf2.cell(0, 5, txt="", ln=1)
fpdf2.cell(0, 5,txt="------------------------------- Keywords generated from competitors Description ----------------------------------",ln=1)
fpdf2.cell(0, 5, txt="", ln=1)

docTitle = totalDescription
descriptionKeyWords = kw_model.extract_keywords(docTitle, keyphrase_ngram_range=(3, 3), stop_words='english', use_mmr=True, diversity=0.7, top_n=15)
print("Keywords generated from competitors Description :\n")
for kws in descriptionKeyWords:
  for kw in kws:
    print(kw, end=", ")
    try:
      fpdf2.cell(100, 5, txt=kw.encode('latin-1', 'replace').decode('latin-1'))
    except:
      fpdf2.cell(0, 5, txt=str(kw), ln=1)
      continue
  print()

fpdf2.output("Ads_Keywords.pdf")

