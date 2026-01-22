import os
import requests
import xml.etree.ElementTree as ET

# Configuration
API_KEY = "3c42cd0ea40c450a8f565805c5e1ee0a"
SITEMAP_FILE = "sitemap.xml"
INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
KEY_LOCATION_FILENAME = f"{API_KEY}.txt"

def get_urls_from_sitemap(sitemap_path):
    """Parses the sitemap.xml and returns a list of URLs."""
    if not os.path.exists(sitemap_path):
        print(f"Error: {sitemap_path} not found.")
        return []

    urls = []
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        
        # Namespace map usually needed for sitemaps
        # The root tag is usually {http://www.sitemaps.org/schemas/sitemap/0.9}urlset
        # We can just iterate and find 'loc' text irrespective of namespace or handle it properly
        
        for url in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc"):
            urls.append(url.text.strip())
            
        # Fallback if namespace matching fails (some sitemaps might not have it or have different ones)
        if not urls:
             for url in root.findall(".//loc"):
                urls.append(url.text.strip())
                
    except Exception as e:
        print(f"Error parsing sitemap: {e}")
        return []
    
    return urls

def submit_to_indexnow(urls):
    """Submits the list of URLs to IndexNow."""
    if not urls:
        print("No URLs to submit.")
        return

    # Extract host from the first URL
    first_url = urls[0]
    from urllib.parse import urlparse
    parsed_uri = urlparse(first_url)
    host = parsed_uri.netloc
    
    key_location = f"{parsed_uri.scheme}://{host}/{KEY_LOCATION_FILENAME}"

    payload = {
        "host": host,
        "key": API_KEY,
        "keyLocation": key_location,
        "urlList": urls
    }

    print(f"Submitting {len(urls)} URLs for host: {host}...")
    print(f"Key Location: {key_location}")

    try:
        response = requests.post(INDEXNOW_ENDPOINT, json=payload)
        
        if response.status_code == 200:
            print("Success! URLs submitted successfully.")
        elif response.status_code == 202:
             print("Success! Request accepted (202).")
        else:
            print(f"Failed. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error sending request: {e}")

if __name__ == "__main__":
    print("--- IndexNow Auto-Submitter ---")
    extracted_urls = get_urls_from_sitemap(SITEMAP_FILE)
    
    if extracted_urls:
        print(f"Found {len(extracted_urls)} URLs in {SITEMAP_FILE}")
        # for u in extracted_urls:
        #     print(f" - {u}")
        submit_to_indexnow(extracted_urls)
    else:
        print("No URLs found or sitemap is empty.")
