from bs4 import BeautifulSoup
import requests
from datetime import datetime
from database import engine, Entry, create_db_and_tables, Session
from sqlmodel import select
## Handle scraping

# This snippet of HTML is how each apprenticeship is diplayed on the website
example = """
<article data-v-f5e192ae="" data-v-56121e7b="" class="card elevation-low link-container" tidy-header="false" link-container="false" use-lazy-load="true">
    <!---->
    <header data-v-f5e192ae="" class="card__section card__content"><h2 data-v-f5e192ae="">
        <a data-v-f5e192ae="" href="link_here" class="link-container__link">Degree Apprenticeship - BSc Digital Technology</a></h2>
        </header>
    <section data-v-f5e192ae="" class="card__section">
        <div data-v-dd39ebba="" data-v-56121e7b="" class="apprenticeship-display">
            <p data-v-dd39ebba="" class="apprenticeship-display__employer">EMPOLYER </p>
            <p data-v-dd39ebba="" class="apprenticeship-display__location icon icon--info-location">London</p>
            <dl data-v-dd39ebba="" class="grid grid--columns-1 grid--columns-2-from-small">
                <div data-v-dd39ebba="">
                    <dt data-v-dd39ebba="">Apprenticeship level</dt>
                    <dd data-v-dd39ebba="">England - Degree Apprenticeship - Level 6</dd>
                </div>
                <div data-v-dd39ebba="">
                    <dt data-v-dd39ebba="">Salary</dt>
                    <dd data-v-dd39ebba="">27,000 a year</dd>
                </div>
                <div data-v-dd39ebba="">
                    <dt data-v-dd39ebba="">Industry</dt>
                    <dd data-v-dd39ebba="">Digital and IT</dd>
                </div><div data-v-dd39ebba="">
                    <dt data-v-dd39ebba="">Apply by | Start date</dt>
                    <dd data-v-dd39ebba="">xx/xx/2026 | xx/xx/xxxx</dd>
                </div>
            </dl>
        </div>
    </section>
    <!---->
</article>"""

def scrape():
    url = "https://www.ucas.com/explore/search/apprenticeships?query=&refinementList%5BLevel.ApprenticeshipType%5D%5B0%5D=Degree%20Apprenticeship&refinementList%5BIndustry%5D%5B0%5D=Digital%20and%20IT"
    response = requests.get(url)

    print(response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all("article", class_="card elevation-low link-container")

    date_format = '%d/%m/%Y'
    create_db_and_tables()

    for article in articles:
        title = article.header.a.text
        link = article.header.a['href']
        employer = article.find("p", class_="apprenticeship-display__employer").text
        location = article.find("p", class_="apprenticeship-display__location").text
        
        # 1. Find the <dt> tag that contains the word "Apply by | Start date"
        apply_start_label = article.find('dt', string=lambda t: t and 'Apply by | Start date' in t) # error on this line where it was soup. so all the dates were the same
        if apply_start_label:
            apply_value, start_value = apply_start_label.find_next_sibling('dd').get_text().split(" | ")
            #print(f"{apply_value} -- {start_value}")
            clean_apply_value = datetime.strptime(apply_value, date_format).date()
            clean_start_value = datetime.strptime(start_value, date_format).date()


        
        # Add to database
        
        with Session(engine) as session:
            # Look to see if it already exists using an Upsert pattern
            statement = select(Entry).where(Entry.link == link) # The link is unlikely to change so check if it exists using it.
            existing_entry = session.exec(statement).first()

            if existing_entry:
                # Update
                existing_entry.title = title
                existing_entry.apply_date = clean_apply_value
                existing_entry.start_date = clean_start_value

                print(f"Updating: {title}")
            
            else:
                # Its new so add it
                new_entry = Entry(title=title, link=link, employer=employer, location=location, 
                                apply_date=clean_apply_value, start_date=clean_start_value)

                session.add(new_entry)
                print(f"Adding {title}")
            session.commit()


    print("Scrape complete")
        #print(f"{title} -- \033[0;32m{link} -- \033[0;34m{employer} -- \033[1;35m{location}\033[0m -- {apply_value} -- {start_value}")