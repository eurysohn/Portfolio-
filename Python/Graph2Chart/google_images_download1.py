from google_images_download import google_images_download 

response = google_images_download.googleimagesdownload() 
search_queries = ['pareto chart'] 

def downloadimages(query): 
        chromedriver = r"C:\Users\Desktop\trafficSimulator-main\src\tests\chromedriver_win32\chromedriver.exe"
        output_dir = r"C:\Users\Desktop\TIPA\images\pareto_chart"
        arguments = {"keywords": query, 
                     "limit": 1,
                     "print_urls": True, 
                     "size": "medium",
                     "output_directory": output_dir,
                     "chromedriver": chromedriver} 

        try: 
            response.download(arguments) 
        except: 
            pass

for query in search_queries: 
    downloadimages(query) 
    print()
