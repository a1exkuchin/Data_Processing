import scrapy
from scrapy.http import HtmlResponse
import re
import json
from urllib.parse import quote
from copy import deepcopy
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    username = "dedparser"
    enc_password = "#PWD_INSTAGRAM_BROWSER:10:1616865878:AZlQADP6pk/5VnFe5bKuY6T9kfTDmBUXYn9qdQB7m7meM6h2CgQb4HSz0pHmNBOnRMjPK0Ahzgub9y7qT+cttle277sc8E7/1xPlM1SnjAw+nGDpITS23K3IzDB1G1Sqz+IOdnnaLmTfNAZu/nojpEw="
    login_url = "https://www.instagram.com/accounts/login/ajax/"
    user_to_scrape = "ai_machine_learning"

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = '003056d32c2554def87228bc3fd9668a'

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
        if json_data["user"] and json_data["authenticated"]:
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
        # сравните с оригинальной строкой из запроса от сайта
        str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
        url = self.graphql_url + f"query_hash={self.posts_hash}&variables={str_variables}"
        yield response.follow(
            url,
            callback=self.parse_posts,
            cb_kwargs={
                "username": username,
                "user_id": user_id,
                "variables": deepcopy(variables)
            },
        )

 
    def parse_posts(self, response: HtmlResponse, username, user_id, variables):
        data = response.json()
        data = data["data"]["user"]["edge_owner_to_timeline_media"]
        page_info = data.get("page_info", None)
        if page_info["has_next_page"]:
            variables["after"] = page_info["end_cursor"]
            # сравните с оригинальной строкой из запроса от сайта
            str_variables = quote(str(variables).replace(" ", "").replace("'", '"'))
            url = self.graphql_url + f"query_hash={self.posts_hash}&variables={str_variables}"
            yield response.follow(
                url,
                callback=self.parse_posts,
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
                user_id=user_id,
                photo=tmp["display_url"],
                likes=tmp["edge_media_preview_like"]["count"],
                post_data=tmp
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
