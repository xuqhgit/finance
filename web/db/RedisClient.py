# coding:utf-8
import redis
from web.utils import ConfigUtils

# redis 配置参数
config = {
    'host': ConfigUtils.get("redis", "host"),
    'port': int(ConfigUtils.get("redis", "port")),
    'password': ConfigUtils.get("redis", "password"),
    'db': int(ConfigUtils.get("redis", "db"))
}
pool = redis.ConnectionPool(host=config['host'], port=config['port'], db=config['db'], password=config['password'])


class RedisClient(object):
    """
    redis客户端类
    此类不提供相应的redis 命令操作接口 请自行查阅相关文档
    http://redisdoc.com/index.html
    """

    @staticmethod
    def get_client():
        return redis.Redis(connection_pool=pool)



if __name__ == '__main__':
    client = RedisClient.get_client()

    print client.get('THS:2016:10:13:LAST:603999')
    pass
