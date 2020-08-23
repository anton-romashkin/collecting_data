import scrapy
import re
import json
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from copy import deepcopy
from ig_subs.items import InstagramItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    login = 'McParser'
    password = '#PWD_INSTAGRAM_BROWSER:10:1598196067:AelQAO7xgaMrvQl2/b8+SPk5c6Bps7W+ICsQzQdriXX+nJQFXwkPxwAEe+jz3G5JX5EOP98Ga49jDONHn0YQ/lLi6Twxeu9EBjQo5opYXp84q1i3j8xJaE7F47HMcFutcULrkOhIjSJAr5kU63ZdmQ=='
    start_link = 'https://www.instagram.com/accounts/login/ajax/'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    query_hash_followers = 'c76146de99bb02f6415203be841dd25a'
    query_hash_following = 'd04b0a864b4b54837c0d870b0e77e076'
    users = ['jayanta3383', 'soumentmc']

    def parse(self, response: HtmlResponse):
        csrf_token = self.csrf_token(response.text)
        yield scrapy.FormRequest(
            self.start_link,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.login,
                      'enc_password': self.password},
            headers={'X-CSRFToken': csrf_token}
        )

    def user_parse(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for person in self.users:
                yield response.follow(
                    f'/{person}',
                    callback=self.collect_data,
                    cb_kwargs={'username': person}
                )

    def collect_data(self, response: HtmlResponse, username):
        user_id = self.id_user(response.text, username)
        variables = {'id': user_id,
                     'include_reel': 'true',
                     'fetch_mutual': 'false',
                     'first': '21'}

        followers_link = f'{self.graphql_url}query_hash={self.query_hash_followers}&{urlencode(variables)}'
        following_link = f'{self.graphql_url}query_hash={self.query_hash_following}&{urlencode(variables)}'

        yield response.follow(
            followers_link,
            callback=self.followers_pages,
            cb_kwargs={'username': username,
                       'userID': user_id,
                       'variables': deepcopy(variables)
                       })

        yield response.follow(
            following_link,
            callback=self.following_pages,
            cb_kwargs={'username': username,
                       'userID': user_id,
                       'variables': deepcopy(variables)
                       })

    def followers_pages(self, response: HtmlResponse, username, userID, variables):
        j_data = response.json()
        page = j_data.get('data').get('user').get('edge_followed_by')
        next_page = page.get('page_info').get('has_next_page')
        if next_page:
            variables['after'] = page.get('page_info').get('end_cursor')
            url_followers = f'{self.graphql_url}query_hash={self.query_hash_followers}&{urlencode(variables)}'

            yield response.follow(url_followers,
                                  callback=self.followers_pages,
                                  cb_kwargs={'username': username,
                                             'userID': userID,
                                             'variables': deepcopy(variables)
                                             })

            followers = page.get('edges')
            for follower in followers:
                item = InstagramItem(
                    source_user=username,
                    name=follower.get('node').get('full_name'),
                    user_id=follower.get('node').get('id'),
                    photo=follower.get('node').get('profile_pic_url'),
                    status='follower'
                )

                yield item

    def following_pages(self, response: HtmlResponse, username, userID, variables):
        j_data = response.json()
        page = j_data.get('data').get('user').get('edge_follow')
        next_page = page.get('page_info').get('has_next_page')
        if next_page:
            variables['after'] = page.get('page_info').get('end_cursor')
            url_following = f'{self.graphql_url}query_hash={self.query_hash_following}&{urlencode(variables)}'

            yield response.follow(
                url_following,
                callback=self.following_pages,
                cb_kwargs={'username': username,
                           'userID': userID,
                           'variables': deepcopy(variables)
                           })

            following = page.get('edges')
            for person in following:
                item = InstagramItem(
                    source_user=username,
                    name=person.get('node').get('full_name'),
                    user_id=person.get('node').get('id'),
                    photo=person.get('node').get('profile_pic_url'),
                    status='following'
                )
                yield item

    def csrf_token(self, text):
        token = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return token.split(':').pop().replace(r'"', '')

    def id_user(self, text, username):
        uid = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text).group()
        return json.loads(uid).get('id', username)
