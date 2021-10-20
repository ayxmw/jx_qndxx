import json
import logging
import os
import random
import re
import string
import time
from logging import StreamHandler, FileHandler
from urllib.parse import urlencode
import requests
from faker import Faker


class Config:
    '''
    配置类
    '''
    # 存放需要完成的青年大学习的学生信息
    NAME_TXT = "qn_names.txt"
    LOG_DIR = os.getcwd()
    # 当天运行的日志目录
    TODAY_DIR = os.path.join(os.path.join(LOG_DIR, 'log'), time.strftime("%Y%m%d"))
    # 日志格式
    FORMAT = logging.Formatter('%(asctime)s : %(message)s')


class Logger:
    '''
    日志类
    '''

    def __init__(self):
        # ---- 日志相关的，逻辑无关，不重要

        self._init_log_dir()
        self._set_fh_logger()
        self._set_sh_logger()
        self._init_logger()

    def _init_log_dir(self):
        '''
        初始化日志文件
        :return:
        '''
        if os.path.exists(Config.TODAY_DIR) == False:
            os.makedirs(Config.TODAY_DIR)
        self._log_file = Config.TODAY_DIR + os.sep + time.strftime("%H_%M_%S") + ".log"

    def _set_fh_logger(self):
        '''
        设置文件输出日志
        :return:
        '''
        self._fh = FileHandler(self._log_file, encoding='utf8', mode='a')
        self._fh.setFormatter(Config.FORMAT)
        self._fh.setLevel(logging.INFO)

    def _set_sh_logger(self):
        '''
        设置控制台日志
        :return:
        '''
        self._sh = StreamHandler()
        self._sh.setLevel(logging.INFO)
        self._sh.setFormatter(Config.FORMAT)

    def _init_logger(self):
        '''
        设置logger
        :return:
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(self._fh)
        self.logger.addHandler(self._sh)
        self.logger.setLevel(logging.INFO)


def gen_rand_str(len):
    '''
    随机生成一个字符串(即用户的openId)
    一个openId代表一个唯一的用户
    :param len:
    :return:
    '''
    return ''.join(random.sample(string.ascii_letters + string.digits, random.randint(10, len)))


def get_current_course_id(token):
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
        logger.info('获取课程id出错')
        return None
    else:
        return {
            'course_id': course_id,
            'title': title
        }


def onepost(access_token, course_id, nid, class_name, username):
    '''

    :param access_token:
    :param course_id: 课程id
    :param nid: 团委id
    :param class_name: 班级
    :param username: 学生姓名
    :return:
    '''

    post_data = {
        "course": course_id,
        "nid": nid,
        "subOrg": class_name,
        "cardNo": username
    }

    # 发送请求url post
    try:
        post_url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/user-api/course/join?accessToken="
        res = requests.post(url=post_url + access_token, data=json.dumps(post_data))
        if res.status_code == 200:
            if class_name is not None:
                msg = res.json().get('message')
                if msg and msg == '选定的课程已结束学习':
                    return "OVER"
                logger.info(username + " 已经完成青年大学习！" + "token:" + access_token + " 团委id:" + nid + " 班级:" + class_name)
            else:
                logger.info(username + " 已经完成青年大学习！" + "token:" + access_token + " 团委id:" + nid + "团委为四级不用班级")
    except:
        logger.info('发送请求出错！')


def get_records(access_token):
    # 获取记录 get
    records_url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/user-api/course/records/v2?accessToken="

    # 获取记录
    res_record = requests.get(records_url + access_token)
    if res_record.status_code == 200:
        res_json = res_record.json()

        result = res_json['result']
        result_list = result['list']
        first_list = result_list[0]['list']
        username = first_list[0].get('cardNo')


def get_token():
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

        logger.info('获取token出错')
        return None
    else:
        return token


def generate_fake_data(nid, count):
    '''
    根据团委id生成count数量个的请求，灌水
    :param nid: 团委id
    :param count: 伪造的数量
    :return:
    '''
    faker = Faker('zh_CN')
    access_tokens = []
    for i in range(count):
        token = get_token()
        if token:
            access_tokens.append(token)
    course_res = get_current_course_id(get_token())
    if not course_res:
        logger.info('获取course_id出错')
        return
    course_id = course_res.get('course_id')
    course_title = course_res.get('title')
    class_name = "班级"  # 注: 四级团委组织请将class_name修改为None,三级的自行填写班级名称
    for token in access_tokens:
        try:
            class_name = random.choice(class_name)
            username = faker.name()
            onepost(token, course_id, nid, class_name, username)
            get_records(token)
        except:
            continue


def main():
    '''
    根据配置的txt文件批量完成青年大学习
    :return:
    '''
    course_res = get_current_course_id(get_token())
    if not course_res:
        logger.info('获取course_id出错')
        return
    course_id = course_res.get('course_id')
    course_title = course_res.get('title')
    logger.info("-" * 100)
    logger.info(course_title)
    logger.info("-" * 100)

    with open(Config.NAME_TXT, 'r', encoding='utf8') as f:
        lines = f.readlines()
    for i in lines:
        if not i.strip():
            continue
        info = re.split('\s', i.strip())
        nid = info[2]
        class_name = info[0]
        username = info[1]
        token = get_token()
        if class_name == '4级':
            class_name = None
        postres = onepost(token, course_id, nid, class_name, username)

        if postres == 'OVER':
            logger.error("选定的课程结束！")
            break


if __name__ == '__main__':
    logger = Logger().logger
    try:
        main()
    except Exception as e:
        logger.error("发生错误！")
