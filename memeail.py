import datetime
import email
import imaplib
import os
from email.header import decode_header

import bs4
import requests
from discord.ext import commands, tasks


class ProblemOfTheDay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.email_account = os.getenv("BENSONBOT_EMAIL_ADDRESS")
        self.email_password = os.getenv("BENSONBOT_EMAIL_PASSWORD")
        self.hcti_user = os.getenv("BENSONBOT_HCTI_USER")
        self.hcti_token = os.getenv("BENSONBOT_HCTI_TOKEN")

        self.general_channel = 612329169011081219

        self.check_and_post.start()

    @tasks.loop(minutes=10.0)
    async def check_and_post(self):
        """Check for a problem of the day and post it if possible"""
        print("Checking for emails at {}".format(datetime.datetime.now()))

        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(self.email_account, self.email_password)

        status, messages = imap.select("INBOX")
        N = len(imap.search(None, 'UnSeen')[1][0].split())
        messages = int(messages[0])

        if N > 0:
            print("Unread message in inbox at {}".format(datetime.datetime.now()))
        else:
            return

        for i in range(messages, messages - N, -1):
            res, msg = imap.fetch(str(i), "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    subject = decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                    from_ = msg.get("From")
                    print("From: {} | Subject: {}".format(from_, subject))
                    if from_.lower() in [
                        "daily coding problem <founders@dailycodingproblem.com>"] and subject.startswith(
                        "Daily Coding Problem: Problem #"):
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            print(content_type)
                            try:
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass

                            if content_type == "text/html":
                                soup = bs4.BeautifulSoup(body, features="html.parser")

                                # find main table
                                main_table = soup.find("table")
                                almost = main_table.find("tr").find("td").find("table")
                                almost.find("table").extract()
                                childs = almost.find("tr").find("td").find("table")
                                hr = childs.find("hr")
                                hr_sibs = hr.find_next_siblings()
                                for h in hr_sibs:
                                    h.extract()
                                hr.extract()

                                soup2 = childs.wrap(soup.new_tag("div", attrs={"width": "500px"}))

                                image = requests.post(url="https://hcti.io/v1/image",
                                                      data={'html': '{}'.format(soup2.prettify())},
                                                      auth=(self.hcti_user, self.hcti_token))
                                print("got response from API at {}: {}".format(datetime.datetime.now(), image.json()))
                                await self.bot.get_channel(self.general_channel).send(image.json()["url"])

        imap.close()
        imap.logout()

    @check_and_post.before_loop
    async def before_check_and_post(self):
        await self.bot.wait_until_ready()
