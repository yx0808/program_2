# 正则方法替换用例表内的数据
# 注意：
# 1.已写定需要替换数据的格式：#xxx#，所以除替换的数据外不可再存在此（#xxx#）格式的数据（主要注意随意输入的地方）
# 2.因为replace_data(data,cls)中需要从 ‘类方法’ 中取 ‘替换进去的数据’ ，
#   所以在取 ’替换进去的数据‘ 保存时，需保存为 ’类属性‘，
#   且保存的 ‘参数名’ 应与用例表中 ‘标识的名称’ 一致（存在映射关系）
#   例：test_recharge的用例中被替换的数据：#member_id#
#      ①替换进去的数据：jsonpath(res,'$..id')[0]
#      ②存的 ‘参数名’：member_id
#      ③将其保存为 类属性：cls.member_id=jsonpath(res,'$..id')[0]
# 3.表格中替换的标识不可以用*、$，应为他们在正则表达中有其他含义，会出错


# 导入re模块
import re

# 封装为一个方法：replace_data，需要返回数据（return，函数调用完后需要一个返回值）
# 需要的参数：data    --需要替换的数据
#           cls     --测试类，因data需要从类中找
# def replace_data(data, cls):
#     当能在data里找到#..#格式的数据时进入循环
#     while re.search('#(.+?)#',data):
#         使用re.search()获取单个目标对象
#         //（将找到的结果赋值给res1，此时res为一个对象<...>）
#         res = re.search('#(.+?)#', data)
#         获取替换对象
#         //（从res提取匹配对象中的内容，赋值给item，为'#id#'形式，即用例中需要替换的对象）
#         item=res.group()
#         获取参数名
#         //（提取匹配对象中的内容，并清除格式，赋值给res2，此时为'id'形式数据，即接口返回内容中的参数名）
#         attr=res.group(1)
#         获取参数值
#         //（使用getattr动态获取（依次获取）类中参数对应的值（如：'id'对应的具体值））
#         value=getattr(cls,attr)
#         使用replace将用例表中的数据替换为上一步获取的参数值（replace的格式需均为str）
#         data=data.replace(item,str(value))
#     返回数据需在循环结束后，否则只能替换一个数据
#     return data


# 升级版：可在配置文件、测试类中查找替换数据（先在类中找，找不到再去配置文件中找）
# 导入配置文件操作模块
from common.handle_conf import conf

def replace_data(data,cls):
    while re.search('#(.+?)#', data):
        res = re.search('#(.+?)#', data)
        item = res.group()
        attr = res.group(1)
        # 如果在类属性中找不到，会报错
        try:
            value = getattr(cls, attr)
        # 报错则捕获异常(属性错误异常，非断言异常)
        except AttributeError:
            # 报错则到配置文件中，提取attr代表的属性名对应的属性值
            value = conf.get('test_data',attr)
        data = data.replace(item, str(value))

    return data













