import re
import json
import os
from dotenv import load_dotenv
from urllib.parse import quote
from copy import deepcopy
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    load_dotenv()
    username = os.getenv("username")
    enc_password = os.getenv("enc_password")
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    followers_hash = '5aefa9893005572d237da5068082d8d5'
    subscriptions_hash = '3dec7e2c57367ef3da3d987d89f9dbc8'

    def parse(self, response: HtmlResponse):
        yield scrapy.FormRequest(
            self.login_url,
            callback=self.user_login,
            method="POST",
            formdata={"username": self.username, "enc_password": self.enc_password},
            headers={"X-CSRFToken": self.fetch_csrf_token(response.text)}
        )

    def user_login(self, response: HtmlResponse):
        json_data = response.json()
        users = input('Введите имена пользователей, разделенные пробелами: ').split()
        if json_data["user"] and json_data["authenticated"]:
            for self.user_to_scrape in users: 
                self.user_id = json_data["userId"]
                user_to_scrape_url = f"/{self.user_to_scrape}"
                yield response.follow(
                    user_to_scrape_url,
                    callback=self.user_data_parse,
                    cb_kwargs={"username": self.user_to_scrape}
                    )


    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {"id": user_id, "first": 12}
        str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
        url = self.graphql_url + \
            f"query_hash={self.subscriptions_hash}&variables={str_variables}"
        yield response.follow(
            url,
            callback=self.parse_subscriptions,
            cb_kwargs={
                "username": username,
                "user_id": user_id,
                "variables": deepcopy(variables)
            },
        )
        url = self.graphql_url + \
            f"query_hash={self.followers_hash}&variables={str_variables}"
        yield response.follow(
            url,
            callback=self.parse_followers,
            cb_kwargs={
                "username": username,
                "user_id": user_id,
                "variables": deepcopy(variables)
            },
        )


    def parse_followers(self, response: HtmlResponse, username, user_id, variables):
        data = response.json()
        data = data["data"]["user"]["edge_followed_by"]
        page_info = data.get("page_info", None)
        if page_info["has_next_page"]:
            variables["after"] = page_info["end_cursor"]
            str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
            url = self.graphql_url + \
                f"query_hash={self.followers_hash}&variables={str_variables}"
            yield response.follow(
                url,
                callback=self.parse_followers,
                cb_kwargs={
                    "username": username,
                    "user_id": user_id,
                    "variables": deepcopy(variables)
                }
            )
        posts = data["edges"]
        for post in posts:
            tmp = post["node"]
            item = InstaparserItem(
                user=username,
                follower=True,
                user_id=tmp["id"],
                photo=tmp["profile_pic_url"],
                name=tmp["full_name"],
            )
            yield item

    def parse_subscriptions(self, response: HtmlResponse, username, user_id, variables):
        data = response.json()
        data = data["data"]["user"]["edge_follow"]
        page_info = data.get("page_info", None)
        if page_info["has_next_page"]:
            variables["after"] = page_info["end_cursor"]
            str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
            url = self.graphql_url + \
                f"query_hash={self.subscriptions_hash}&variables={str_variables}"
            print(url)
            yield response.follow(
                url,
                callback=self.parse_subscriptions,
                cb_kwargs={
                    "username": username,
                    "user_id": user_id,
                    "variables": deepcopy(variables)
                }
            )
        rows = data["edges"]
        for row in rows:
            tmp = row["node"]
            item = InstaparserItem(
                user=username,
                subs=True,
                user_id=tmp["id"],
                photo=tmp["profile_pic_url"],
                name=tmp["full_name"],
            )
            yield item


    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
