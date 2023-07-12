# lenmoban v.3 加密


# 导入rsa库，用于生pubkey和privkey
import rsa
# 导入base64库：
import base64

from time import time


# 定义一个类用来保存加密方法
class HandleSign:
    # 接口文档中的秘钥 # 定义服务器公钥, 往往可以存放在公钥文件中
    server_pub = """
            -----BEGIN PUBLIC KEY-----
            MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQENQujkLfZfc5Tu9Z1LprzedE
            O3F7gs+7bzrgPsMl29LemonPYvIG8C604CprLittlenJpnhWu2lGirlWZyLq6sBr
            tuPorOc42+gInFfyhJAwdZB6Sqlove7bW+jNe5youDtU7very6Gx+muchGo8Dg+S
            kKlZFc8Br7SHtbL2tQIDAQAB
            -----END PUBLIC KEY-----
            """
    # 加密算法(不同项目加密算法不一样，需要重写，可让开发编写)
    @classmethod
    # 定义encrypt方法，msg即需要加密的字符串
    def encrypt(cls, msg, pub_key=None):
        """
        非对称加密
        :param msg: 待加密字符串或者字节
        :param pub_key: 公钥
        :return: 密文
        """
        if isinstance(msg, str):  # 如果msg为字符串, 则转化为字节类型
            msg = msg.encode('utf-8')
        elif isinstance(msg, bytes):  # 如果msg为字节类型, 则无需处理
            pass
        else:  # 否则抛出异常
            raise TypeError('msg必须为字符串或者字节类型!')

        if not pub_key:  # 如果pub_key为空, 则使用全局公钥
            pub_key = cls.server_pub.encode("utf-8")
        elif isinstance(pub_key, str):  # 如果pub_key为字符串, 则转化为字节类型
            pub_key = pub_key.encode('utf-8')
        elif isinstance(pub_key, bytes):  # 如果msg为字节类型, 则无需处理
            pass
        else:  # 否则抛出异常
            raise TypeError('pub_key必须为None、字符串或者字节类型!')

        # 创建PublicKey秘钥对象
        public_key_obj = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key)
        # 生成加密文件
        cryto_msg = rsa.encrypt(msg, public_key_obj)
        # 将加密文件文本转化为base64编码
        cipher_base64 = base64.b64encode(cryto_msg)
        # 将字节类型的base64编码转化为字符串类型
        return cipher_base64.decode()


    # 生成时间戳
    @classmethod
    def generate_sign(cls, token):
        """
        生成sign
        :param timestamp: 当前秒级时间戳, 为int类型
        :param token: token, 为str类型
        :return: 时间戳和sign组成的字典
        """
        # 获取当前的时间戳
        timestamp = int(time())
        # 获取token前50位
        prefix_50_token = token[:50]
        # 将token前50位与时间戳字符串进行拼接
        message = prefix_50_token + str(timestamp)
        # 生成sign
        sign = cls.encrypt(message)
        return {"timestamp": timestamp, "sign": sign}



if __name__=='__main__':
    token = ''
    cryto_info = HandleSign.encrypt(msg=token)
    print(cryto_info)
