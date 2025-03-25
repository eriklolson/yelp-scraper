import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def scrape_yelp_to_joplin_md(url):
    # Set up Selenium with headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    time.sleep(5)  # Wait for JavaScript to render

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Business name
    name_tag = soup.find('h1')
    name = name_tag.get_text(strip=True) if name_tag else 'Unknown'

    # Address
    address = soup.find('address')
    address_text = address.get_text(separator=', ', strip=True) if address else 'No address found'

    # Star rating & review count
    rating_tag = soup.select_one('[aria-label*="star rating"]')
    review_count_tag = soup.find('span', string=lambda s: s and 'reviews' in s.lower())
    rating = rating_tag['aria-label'] if rating_tag else 'N/A'
    reviews = review_count_tag.get_text(strip=True) if review_count_tag else 'N/A'

    # Price & category
    category = soup.select_one('span.css-1fdy0l5')  # usually shows $ and category
    category_text = category.get_text(strip=True) if category else 'N/A'

	# Business photos (images with class "y-css-3xip89")
	image_tags = soup.select('img.y-css-3xip89')
	photos = []
	for img in image_tags:
	    src = img.get('src')
	    alt = img.get('alt', 'Yelp photo')
	    if src and src.startswith('https://'):
	        photos.append(f"![{alt}]({src})")
	    if len(photos) >= 10:
	        break


    # Hours
    hours_md = ""
    hours_table = soup.find('table')
    if hours_table:
        rows = hours_table.find_all('tr')
        for row in rows:
            cols = row.find_all(['th', 'td'])
            if len(cols) >= 2:
                day = cols[0].get_text(strip=True)
                hours = cols[1].get_text(strip=True)
                hours_md += f"**{day}**: {hours}\n"

    # Google Maps link
    google_maps_url = f"https://www.google.com/maps/search/?api=1&query={address_text.replace(' ', '+')}"

    # Markdown output
    md = f"""# {name}

{google_maps_url}

{rating} [{reviews}](#reviews)

{category_text}

## Photos
""" + '\n'.join(photos) + """

## What’s the vibe?


## Location & Hours

**Address**: {address_text}  


### Hours
{hours_md}
"""

    driver.quit()
    return md


if __name__ == "__main__":
    yelp_url = input("Enter the Yelp business URL: ").strip()
    markdown_output = scrape_yelp_to_joplin_md(yelp_url)

    with open("yelp_business_note.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print("✅ Joplin markdown note saved as 'yelp_business_note.md'")
