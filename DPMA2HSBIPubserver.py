from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import getpass
import time

#
#   Script to scrape DPMA and import found data to HSBI PubServer
#

# first type in terminal: safaridriver --enable

options = webdriver.SafariOptions()
driver = webdriver.Safari(options=options)
timeout = 20

DEPATIS_URL         = "https://depatisnet.dpma.de/DepatisNet/depatisnet?action=basis"
HSBI_LOGIN_URL      = "https://www.hsbi.de/login?target=https://www.hsbi.de/publikationsserver/login"
HSBI_PATENT_ADD_URL = "https://www.hsbi.de/publikationsserver/librecat/record/new?type=patent"

#search parameters on DPMA
RESEARCHER = "Philip Wette"
DATE_FROM  = "2024-01-01"
DATE_TO    = "2025-01-01"

#get user login to HSBI
user     =           input("HSBI Username: ")
password = getpass.getpass("HSBI Password: ")


def waitForElementToBeLoaded(id : str = None, name : str = None, delay: int = 1):
    by = By.ID
    value = id
    if name is not None:
        by = By.NAME
        value = name

    element_present = EC.presence_of_element_located((by, value))
    WebDriverWait(driver, timeout).until(element_present)
    time.sleep(delay)


def typeInValue(id : str = None, name : str = None, text : str = None):
    by = By.ID
    value = id
    if name is not None:
        by = By.NAME
        value = name

    input_name = driver.find_element(by=by, value=value)
    input_name.send_keys(text)


def setValue(id : str = None, text : str = None):
    driver.execute_script(f'document.getElementById({id}).value = "{text}"')


def click(id: str = None):
    element = driver.find_element(by=By.ID, value=id)
    driver.execute_script("arguments[0].click();", element)


#
#   PARSE DATA FROM DPMA
#


#get data from dpma
driver.get(DEPATIS_URL)
waitForElementToBeLoaded(id='rechercheStarten')

typeInValue(id="b_Pa", text=RESEARCHER)

#click on radio button
click("inlineRadioBwt1")

setValue("pub_von", DATE_FROM)
setValue("pub_bis", DATE_TO)

#submit form
submit_button = driver.find_element(by=By.ID, value="rechercheStarten")
submit_button.submit()




#wait for values to be submited
waitForElementToBeLoaded(id='blaetter_aktuelle_seite')

#configure values
click("a_trefferliste_einblenden")
click("Icm")
click("Pub")

button = driver.find_element(by=By.ID, value="blaetter_aktuelle_seite")
button.submit()


#wait for page to reload
waitForElementToBeLoaded(id="trefferliste", delay=5)

#parse data from table
patents = []
table =  driver.find_element(by=By.ID, value="trefferliste")
for row in table.find_elements(by=By.XPATH, value=".//tr"):
    cells = [td.text for td in row.find_elements(by=By.XPATH, value=".//td")]
    if len(cells) > 5:
        no = cells[2].strip()
        date = cells[3].strip()
        ipc = cells[4].strip().split("\n")[0]
        title = cells[5].strip()

        patents.append( [no, date, ipc, title] ) 

print("Found Patents:")
print(patents)



#
# fill in data into pubserver
#

driver.get(HSBI_LOGIN_URL)
waitForElementToBeLoaded(name="loginButton2", delay=1)

input_username = driver.find_element(by=By.ID, value="username")
input_password = driver.find_element(by=By.ID, value="password")
submit_button  = driver.find_element(by=By.NAME, value="loginButton2")


input_username.send_keys(user)
input_password.send_keys(password)
submit_button.submit()

#wait for cookies to be set
time.sleep(5)


for patent in patents:
    #click the add-button
    driver.get(HSBI_PATENT_ADD_URL)

    #wait for page to be loaded
    waitForElementToBeLoaded(name="finalSubmit", delay=1)

    title = driver.find_element(by=By.ID, value="id_title")
    year = driver.find_element(by=By.ID, value="id_year")
    date = driver.find_element(by=By.ID, value="id_publication_date")
    patentno = driver.find_element(by=By.ID, value="id_ipn")
    ipc = driver.find_element(by=By.ID, value="id_ipc")

    title.send_keys(patent[3])
    year.send_keys(patent[1].split(".")[2])
    date.send_keys(patent[1])
    patentno.send_keys(patent[0])
    ipc.send_keys(patent[2])

    button = driver.find_element(by=By.NAME, value="finalSubmit")
    button.submit()

    #wait for dataset to be stored in database
    time.sleep(5)





driver.quit()