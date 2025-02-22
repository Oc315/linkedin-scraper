#%%
import time
import csv
import os
import json
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

#%%
# Step 1: Scrape the URLs with key word
# Loged in too many times and LinkedIn ask for verification now
class LinkedInScraper:
    def __init__(self, username=None, password=None):
        self.username = username
        self.password = password
        chromedriver_path = ""
        service = Service(chromedriver_path)
        options = Options()
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self):
        """Log in to LinkedIn."""
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(2) 

        username_input = self.driver.find_element(By.NAME, 'session_key')
        password_input = self.driver.find_element(By.NAME, 'session_password')

        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)

        time.sleep(5) 

    def search(self, keywords, page, location='United States'):
        """Perform a search on LinkedIn and navigate to a specific page."""
        geo_urns = {
            'United States': '103644278',
        }
        geo_urn = geo_urns.get(location, '103644278') 
        search_url = f'https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=GLOBAL_SEARCH_HEADER&page={page}&geoUrn=%5B%22{geo_urn}%22%5D'
        self.driver.get(search_url)
        time.sleep(5) 

    def get_profile_links(self):
        """Parse the search results and get profile links."""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        profile_links = []
        for link in soup.find_all('a', href=True):
            url = link['href']
            if 'linkedin.com/in/' in url:
                full_url = f"https://www.linkedin.com{url}" if url.startswith('/') else url
                profile_links.append(full_url)

        return profile_links

    def scrape(self, keywords, num_pages=10):
        """Main method to perform login, search, and get profile links."""
        self.login()

        all_profile_links = []

        for page in range(1, num_pages + 1):
            self.search(keywords, page)
            profile_links = self.get_profile_links()
            all_profile_links.extend(profile_links)

        # Remove duplicates
        all_profile_links = list(set(all_profile_links))

        self.driver.quit()
        return all_profile_links

#%%
# Getting URLs 
if __name__ == "__main__":
    linkedin_username = ''
    linkedin_password = ''  

    keyword = 'Procurement Officer at University'
    scraper = LinkedInScraper(linkedin_username, linkedin_password)
    profile_links = scraper.scrape(keyword, num_pages=10)

    profile_links = list(set(profile_links))

    output_dir = ''
    output_file = os.path.join(output_dir, f"{keyword.replace(' ', '_')}_profile_links.csv")

    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Linkedin Profile URL'])  
        for profile_link in profile_links:
            csvwriter.writerow([profile_link])

    print(f"Profile links have been saved to {output_file}")

#%%
# Step 1: Alternative Approach: Manual Log in
class LinkedInScraper:
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=service, options=options)

    def manual_login(self):
        """Perform manual login to handle verification."""
        self.driver.get('https://www.linkedin.com/login')
        input("Please log in manually and press Enter here once logged in...")
        cookies = self.driver.get_cookies()
        with open('cookies.pkl', 'wb') as file:
            pickle.dump(cookies, file)
        print("Cookies have been saved.")
#%%
# Usage
if __name__ == "__main__":
    scraper = LinkedInScraper()
    scraper.manual_login()
#%%
class LinkedInScraper:
    def __init__(self):
        service = Service(ChromeDriverManager().install())
        options = Options()
        # options.add_argument("--headless")  # Run in headless mode
        self.driver = webdriver.Chrome(service=service, options=options)

    def load_cookies(self):
        """Load cookies from file."""
        self.driver.get('https://www.linkedin.com')
        with open('cookies.pkl', 'rb') as file:
            cookies = pickle.load(file)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.refresh()
        time.sleep(5)  # Wait for the page to load

    def search(self, keywords, page, location='United States'):
        """Perform a search on LinkedIn and navigate to a specific page."""
        geo_urn = '103644278'  # United States geoUrn
        search_url = f'https://www.linkedin.com/search/results/people/?keywords={keywords}&origin=GLOBAL_SEARCH_HEADER&page={page}&geoUrn=%5B%22{geo_urn}%22%5D'
        self.driver.get(search_url)
        time.sleep(5)  # Wait for the search results to load

    def get_profile_links(self):
        """Parse the search results and get profile links."""
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        profile_links = []
        for link in soup.find_all('a', href=True):
            url = link['href']
            if 'linkedin.com/in/' in url:
                full_url = f"https://www.linkedin.com{url}" if url.startswith('/') else url
                profile_links.append(full_url)

        return profile_links

    def scrape(self, keywords, num_pages=3):
        """Main method to perform login, search, and get profile links."""
        self.load_cookies()

        all_profile_links = []

        for page in tqdm(range(1, num_pages + 1), desc="Scraping pages", unit="page"):
            self.search(keywords, page)
            profile_links = self.get_profile_links()
            all_profile_links.extend(profile_links)

        # Remove duplicates
        all_profile_links = list(set(all_profile_links))

        self.driver.quit()
        return all_profile_links
#%%
# Usage
if __name__ == "__main__":
    scraper = LinkedInScraper()
    scraper.load_cookies()  # Load cookies to reuse the session

    # Proceed with scraping using the saved cookies
    profile_links = scraper.scrape('procurement officer at University', num_pages=3)

    profile_links = list(set(profile_links))

    keyword = 'Procurement Officer at University'
    output_dir = ''
    output_file = os.path.join(output_dir, f"{keyword.replace(' ', '_')}_profile_links.csv")

    os.makedirs(output_dir, exist_ok=True)

    with open(output_file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Linkedin Profile URL'])
        for profile_link in tqdm(profile_links, desc="Saving profiles", unit="profile"):
            csvwriter.writerow([profile_link])

    print(f"Profile links have been saved to {output_file}")

#%%
# Step 2: Scrape the profiles for all URLs scraped
class LinkedInProfileScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        # Setup ChromeDriver using ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        options = Options()
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self):
        """Log in to LinkedIn."""
        self.driver.get('https://www.linkedin.com/login')
        time.sleep(2)  # Wait for the page to load

        username_input = self.driver.find_element(By.NAME, 'session_key')
        password_input = self.driver.find_element(By.NAME, 'session_password')
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)  

    def scrape_profile(self, url):
        """Scrape details from a LinkedIn profile."""
        self.driver.get(url)
        time.sleep(5)  

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        def get_text_or_none(soup_element):
            return soup_element.get_text(strip=True) if soup_element else None

        # Extract details from the profile
        name = get_text_or_none(soup.find('h1'))
        first_name = name.split()[0] if name else None
        last_name = ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else None
        location = get_text_or_none(soup.find('span', {'class': 'text-body-small inline t-black--light break-words'}))
        current_job = get_text_or_none(soup.find('div', {'class': 'text-body-medium break-words'}))
        
        num_followers = get_text_or_none(soup.find('span', {'class': 't-bold'}))

        # Extract experiences
        experiences = []
        experience_sections = soup.find_all('section', {'id': 'experience-section'})
        for section in experience_sections:
            for exp in section.find_all('div', {'class': 'pv-entity__position-group-pager'}):
                title = get_text_or_none(exp.find('h3', {'class': 't-16 t-black t-bold'}))
                company = get_text_or_none(exp.find('p', {'class': 'pv-entity__secondary-title t-14 t-black t-normal'}))
                experiences.append({'title': title, 'company': company})
        experiences = '; '.join([f"{exp['title']} at {exp['company']}" for exp in experiences])

        # Extract education
        education = []
        education_sections = soup.find_all('section', {'id': 'education-section'})
        for section in education_sections:
            for edu in section.find_all('div', {'class': 'pv-entity__degree-info'}):
                school = get_text_or_none(edu.find('h3', {'class': 'pv-entity__school-name t-16 t-black t-bold'}))
                degree = get_text_or_none(edu.find('span', {'class': 'pv-entity__comma-item'}))
                education.append({'school': school, 'degree': degree})
        education = '; '.join([f"{edu['school']} - {edu['degree']}" for edu in education])
        

        return {
            'Name': name,
            'FirstName': first_name,
            'LastName': last_name,
            'Location': location,
            'Current Job': current_job,
            'Number of Followers': num_followers,
            'Experiences': experiences,
            'Education': education,
            'Profile URL': url
        }

    def scrape_profiles(self, profile_links):
        """Scrape multiple LinkedIn profiles and save to a CSV file."""
        scraped_data = []
        for url in tqdm(profile_links, desc="Scraping profiles", unit="profile"):
            data = self.scrape_profile(url)
            scraped_data.append(data)

        # Define the output directory and file path
        keyword = 'procurement officer'
        output_dir = ''
        output_file = os.path.join(output_dir, f"{keyword.replace(' ', '_')}_profiles.csv")

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Save the scraped data to a CSV file
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['Name', 'FirstName', 'LastName', 'Location', 'Current Job', 'Number of Followers', 'Experiences', 'Education', 'Profile URL']
            csvwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            csvwriter.writeheader()
            for data in scraped_data:
                csvwriter.writerow({
                    'Name': data['Name'],
                    'FirstName': data['FirstName'],
                    'LastName': data['LastName'],
                    'Location': data['Location'],
                    'Current Job': data['Current Job'],
                    'Number of Followers': data['Number of Followers'],
                    'Experiences': data['Experiences'],
                    'Education': data['Education'],
                    'Profile URL': data['Profile URL']
                })

        print(f"Profile data has been saved to {output_file}")
        self.driver.quit()

#%%
# Usage for scraping profile details
if __name__ == "__main__":
    linkedin_username = ''
    linkedin_password = ''  

    profile_links_file = ''

    profile_links = []
    with open(profile_links_file, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header row
        for row in csvreader:
            profile_links.append(row[0])

    profile_scraper = LinkedInProfileScraper(linkedin_username, linkedin_password)
    profile_scraper.login()
    profile_scraper.scrape_profiles(profile_links)

# %%
