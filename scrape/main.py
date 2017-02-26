import scraper

def main():

    classObject = scraper.TestFIUSearchPage()

    # removeExistingFile = classObject.removeExistingFile()

    scrape = classObject.scrape()

main()
