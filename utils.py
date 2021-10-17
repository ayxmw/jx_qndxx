import re
import string
import random
import time
from urllib.parse import urlencode
import requests
from faker import Faker


def gen_rand_str(len):
    return ''.join(random.sample(string.ascii_letters + string.digits, random.randint(10, len)))

class Util:
    @staticmethod
    def get_token():
        '''
        获取一个token，以便通过请求
        :return:
        '''
        url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/login/we-chat/callback?callback=https%3A%2F%2Fjxtw.h5yunban.cn%2Fjxtw-qndxx%2FsignUp.php&scope=snsapi_userinfo&appid=wxe9a08de52d2723ba&openid={}&{}&headimg=https://thirdwx.qlogo.cn/mmopen/vi_32/I7gbHHRj903RFibtlB4jrz1T1jTJ3eCWsCJwibQIT5hLRXO25ib9AHeqUjsPGmwhtiaBuzhQfhEZ6ibBdGbyZuM72LA/132&time={}&source=common&t={}"
        try:
            faker = Faker('zh_CN')
            openid = gen_rand_str(28)

            nickname = urlencode({'j': faker.name()})
            newurl = url.format(openid, nickname, "%d" % time.time(), "%d" % time.time())

            res = requests.get(newurl)
            text = res.text

            token = re.findall("<script>localStorage.setItem\('accessToken', '(.*?)'\)", text)
            if token:
                token = token[0]
        except:

            print('获取token出错')
            return None
        else:
            return token

    @staticmethod
    def get_current_course_id(token):
        '''
        获取课程id
        :param token:
        :return:
        '''
        if not token:
            return None
        # 获取当前课程的url地址
        current_url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/common-api/course/current?accessToken="
        new_current_url = current_url + token
        course_id = None
        try:
            res = requests.get(new_current_url)
            if res.status_code == 200:
                res_json = res.json()
                if res_json.get('status') != 200:
                    return None
                result = res_json['result']
                course_id = result.get('id')
                title = result.get('title')

        except:
            print('获取课程id出错')
            return None
        else:
            return {
                'course_id': course_id,
                'title': title
            }

    @staticmethod
    def print_org(item=None):
        '''
        获取团委的信息
        :param item:
        :return:
        '''
        print(item)
        url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/common-api/organization/children?pid="
        if item == None:
            url = url + 'N'
        else:
            url = url + item.get('id')
        res = requests.get(url)
        if res.status_code != 200:
            print('请求失败')
            return
        # 获取返回的 json数据
        res_json = res.json()
        # 获取团委列表
        result_list = res_json.get('result')
        # 如果团委列表为空，则 return
        if not result_list:
            print('该团委没有下级团委了')
            print('您的最终团委id: ' + item.get('id') + '    您的团委是第%s级' % item.get('level'))
            return None
        print('找到以下团委列表:')
        for index, item in enumerate(result_list):
            print(str(index + 1) + '、团委id:' + item.get('id') + '\t团委名字: ' + item.get('title'))

        index = int(input('请选择以下第几个团委(输入 1、2、3 等数字):'))
        if index > len(result_list) or index < 0:
            print('你所选的下标越界! 退出！')
            return
        # 递归查找
        return Util.print_org(result_list[index - 1])


if __name__ == '__main__':
    Util.print_org()
