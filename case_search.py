# def get_register_url(status_soup) -> str:
#     link_tag = status_soup.find(style="color: blue")
#     relative_link = link_tag.get("href")
#     return "https://odysseypa.traviscountytx.gov/JPPublicAccess/" + relative_link


# def get_status_and_type(status_soup) -> str:
#     tds = status_soup.find_all("td")
#     divs = tds[-1].find_all("div")
#     status, casetype = divs[1].text, divs[0].text
#     return status, casetype

import re
# def get_register_url(status_soup) -> str:
#     print("Debug: get_register_url() in case_search.py")
#     link_tag = status_soup.find(style="color: blue")

#     relative_link = link_tag.get("href")
    
#     return "https://odysseypa.traviscountytx.gov/JPPublicAccess/" + relative_link

def get_register_url(status_soup) -> str:
    print("Debug: get_register_url() in case_search.py")
    link_tag = status_soup.find(style="color: blue")
    
    if link_tag is None:
        print("ERROR: No link found with style='color: blue'")
        # Try alternative selectors
        link_tag = status_soup.find("a", href=re.compile(r"CaseDetail"))
        if link_tag is None:
            print("ERROR: No case detail link found at all")
            return None  # Return None instead of crashing
    
    relative_link = link_tag.get("href")
    if relative_link is None:
        print("ERROR: Link found but no href attribute")
        return None
    
    return "https://odysseypa.traviscountytx.gov/JPPublicAccess/" + relative_link


def get_status_and_type(status_soup) -> str:
    print("Debug: get_status_and_type() in case_search.py")
    
    try:
        tds = status_soup.find_all("td")
        if not tds:
            print("ERROR: No td elements found")
            return None, None
        
        divs = tds[-1].find_all("div")
        if len(divs) < 2:
            print(f"ERROR: Expected at least 2 divs, found {len(divs)}")
            return None, None
        
        status, casetype = divs[1].text, divs[0].text
        return status, casetype
    except Exception as e:
        print(f"ERROR in get_status_and_type: {e}")
        return None, None
