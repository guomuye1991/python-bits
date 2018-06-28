# 中国采购招标
# 功能板，待优化
import requests, bs4,logging.handlers

LOG_FILE = r'./log/quanminzhaobiao_net.log'

handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5, encoding='utf-8')
fmt = '%(asctime)s - %(levelname)s - %(message)s'

formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger = logging.getLogger('全名招标网')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def get_records(domain, page):
    """ 抓取列表 """
    logger.info('抓取第[%s]页' % page)
    with requests.get(page) as res:
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text)
        # 原生数据
        records = soup.select('#page_wraper > div.page_left_div > div.modular_div > dl.bottom_border')
        # 处理数据
        datas = []
        for item in records:
            href = domain + item.select('a')[0].attrs['href']
            title = item.select('a')[0].text.replace('\r\n', '').lstrip()
            time = item.select('dd')[1].text[1:11]
            datas.append({'href': href, 'title': title, 'time': time})
        return datas


def get_record_detail(record):
    """ 抓取详情 """
    detail_href = record['href']
    logger.info('抓取href[%s] 开始' % detail_href)
    with requests.get(detail_href) as res:
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text)
        bid_content_div = soup.select('#bid_content_div')  # 格式一
        czfxfontzoom = soup.select('#czfxfontzoom')  # 格式二

        p_list = []
        if bid_content_div:
            p_list += bid_content_div[0].select('p')
        if czfxfontzoom:
            p_list += czfxfontzoom[0].select('p')
        p_data_list = []

        if len(p_list) == 0:
            logger.info('详情href[%s] 没有抓取到数据' % detail_href)

        for p in p_list:
            p_data_list.append(p.text)

        record['detail'] = p_data_list
        logger.info('抓取href[%s] 完毕' % detail_href)


def run_job():
    """ 抓取记录列表数据 """
    domain = 'http://qmzhaobiao.com'
    page_num = 1
    records = []
    logger.info('抓取记录列表开始')
    try:
        while True:
            page = domain + '/bidding/zbgg/page' + str(page_num)
            records += get_records(domain, page)
            page_num += 1
    except IndexError:
        logger.info('end')

    logger.info('本次抓取记录列表总数[%d]' % len(records))
    """ 抓取记录详情 """
    logger.info('抓取详情开始')
    for record in records:
        get_record_detail(record)

    logger.info('抓取详情完毕')


run_job()
