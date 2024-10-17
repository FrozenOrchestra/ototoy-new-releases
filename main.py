import requests
import datetime
import json
import smtplib
import os

from bs4 import BeautifulSoup
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from new_release import NewRelease


# gets number of days since last time script ran
def get_script_delta():
    last_line = ''
    with open('log', 'rb') as f:
        try:  # catch OSError in case of a one line file 
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b'\n':
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
    ld = last_line.split(",")[0].split("-")
    last_date = datetime.date(int(ld[0]), int(ld[1]), int(ld[2]))
    return (datetime.date.today() - last_date).days - 1
    

# gets the new music releases for any given date
def get_new_release(date, new_releases, artists):
    # gets the webpage for the previous days' releases
    date_str = str.replace(str(date), "-", "")
    url = f"https://ototoy.jp/newreleases/date/{date_str}/genre/gall"
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    # gets the urls for all pages of the releases
    release_pages = soup.find_all("a", class_="page")
    del release_pages[round(len(release_pages) / 2) - 1:len(release_pages)]
    release_pages = ["https://ototoy.jp" + r.get('href') 
                     for r in release_pages]
    release_pages.insert(0, url)
    # loop trhough each page and create a list of releases
    for link in release_pages:
        soup = BeautifulSoup(requests.get(link).content, "html.parser")
        for release in soup.find_all("div", class_="package-content"):
            try:
                artist = release.h2.a.get_text()
                album = release.h3.a.get_text()
                url = "https://ototoy.jp" + release.h3.a['href']
                new_releases.append(NewRelease(artist, album, url))
            except:
                next
    # remove duplicates from list of new releases
    new_releases = list(set(new_releases))
    # remove all releases that aren't in artists
    return [r for r in new_releases if r.artist in artists]


# get new releases for every day the script hasn't run
new_releases = []
artists = json.load(open("artists.json"))
delta = get_script_delta()
date = datetime.date.today()
while delta > 0:
    date = datetime.date.today() - datetime.timedelta(days=delta)
    new_releases = get_new_release(date, new_releases, artists)
    delta -= 1

if len(new_releases) == 0:
    print(f"{date},No new releases")
    quit()

# send email containing new releases
email_details = json.load(open("email_details.json"))
username = email_details["sender_address"]
password = email_details["sender_password"]
to = email_details["receiver_address"]
subject = f"Daily Music Releases {date}"
msg = MIMEMultipart('alternative')
msg['Subject'] = subject
msg['From'] = username
msg['To'] = to

# plaintext messge body
msg_text = "Your new music releases:\n"
# html message body
msg_html = """\
<html>
    <head><b>New Music Releases:</b></head>
    <body>
        <ul>
"""
for release in new_releases:
    msg_text += str(release) + "\n"
    msg_html += f'<li>{release.to_html()}</li>\n'
msg_html += """\
        </ul>
    </body>
</html>
"""
# Record and attach the MIME types of both parts - text/plain and text/html.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(MIMEText(msg_text, 'plain'))
msg.attach(MIMEText(msg_html, 'html'))

try:
    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(username, password)
    server.sendmail(username, to, msg.as_string())
    server.quit()
    print(f"{date},Message sent succesfully")
except:
    print(f"{date},Error sending message")
