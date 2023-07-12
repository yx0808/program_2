# 接口文档中的第一组（1.5.2-1）
# 加密方法（请求头中+时间戳+加密算法）
from time import time
from common.handle_sign import HandleSign

# 时间戳获取
t=int(time())

# 签名获取
token='eyJhbGciOiJIUzUxMiJ9.eyJtZW1iZXJfaWQiOjEyMDY4MiwiZXhwIjoxNjg4MjI0Nzc2fQ.W-THO2bYle-zeDvDCITw_VTc3WdWA4xyE5_W3niR0dpVc6IgopPceP7DUiPY4_4KfYcPSpB8WxkJOiXvN2orGw'
# 获取前50位(切片)
data=token[:50]+str(t)
hs=HandleSign()
# 调用HandleSign()函数中定义的加密算法encrypt
res=hs.encrypt(data)
# print(res)

# 组成数据
params={"timestamp": t, "sign": res}

# ---------------------------------------------------------------------
# 接口文档中的第二、三组（1.5.2-2/3）
# 加密方法（请求体中+时间戳+加密算法）
# 在准备请求数据时：
# # from common.handle_sign import HandleSign        # 开始部分：导入封装的加密算法模块
# par_sign=HandleSign.generate_sign(self.token)    # 使用HandleSign中封装的generate_sign方法
#                                 # self.token：token在user_login已保存为类属性，实例对象可通过self调用
# # 将par_sign加入到参数params中（字典添加，调用update方法）
# params.update(par_sign)