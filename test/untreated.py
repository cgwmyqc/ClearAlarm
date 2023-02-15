import json


a = 0

with open('../warningInfo.json', 'r', encoding="utf-8") as f:

    warningInfo = json.load(f)

amountAll = warningInfo['total']
amountUntreated = 0


# warningInfo.json文件说明
# state-处理状态（0-未处理; 14-已处理）
for item in warningInfo['rows']:
    if item['state'] == 0 and item['type'] == 1:
        a = a+1
        print(item['vin'])

print('总数：' + str(a))



