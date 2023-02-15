"""
    1、通过对request请求数据分析：
        i、数据提交的Request URL: https://cmsp.evsmc.cn/sysSafeMessage/alarmSort
        ii、数据提交的Method: POST
        iii、数据提交网页为弹窗格式，弹窗动态网址为格式为{静态网址+id} (可单独用浏览器打开此网址分析网页form表单，取出需要提交的数据格式)：
            eg. https://cmsp.evsmc.cn/sysSafeMessage/alarmType.html?ids=3c000dbca32a4d48aff424801a4f4256
        iiii、不知道是否有反爬机制，若有，模拟浏览提交数据的Request Headers 中的Refere值需要设置为上面的网址即{静态网址+id}，其中id不能写
            死，id为当前报警项的id值，具体可以查看json数据。设置Refere意图是假装提交数据前的页面是Refere的值所指网址。


    2、通过分析form表单数据，有3个input框数据需要提交，input的name字段决定了数据被送到服务器上的名称，以下面代码段为例，需要POST的数据有：
        i、报警id，{"idsStr":"3c000dbca32a4d48aff424801a4f4256"}，
        ii、报警类型单选框，(根据工程师对故障分类进行选择，此例子选择'其他原因'): {"alarm":"3"}
        iii、处理单据上传，{"file":"pdf文件"}


    <form id="ff" method="post" novalidate="novalidate" enctype="multipart/form-data" class="sui-form">
        <input type="hidden" id="ids" name="idsStr" value="3c000dbca32a4d48aff424801a4f4256">
        <div align="center" style="margin-top: 1px">
            <table class="table_edit" border="0">
                <tbody><tr>
                    <td class="td_input" colspan="3">
                        <input type="radio" name="alarm" value="0"> 单车偶发故障报警
                    </td>
                </tr>
                <tr>
                    <td class="td_input" colspan="3">
                        <input type="radio" name="alarm" value="1"> 多车偶发故障报警
                    </td>
                </tr>
                <tr>
                    <td class="td_input" colspan="3">
                        <input type="radio" name="alarm" value="2"> 车辆设计原因报警
                    </td>
                </tr>
                <tr>
                    <td class="td_input" colspan="3">
                        <input type="radio" name="alarm" value="5"> 电池故障报警
                    </td>
                </tr>
                <tr>
                    <td class="td_input" colspan="3">
                        <input type="radio" name="alarm" value="4"> 车辆部件导致的故障报警
                    </td>
                </tr>
                <tr>
                    <td class="td_input" colspan="3">
                        <input type="radio" name="alarm" value="3"> 其他原因
                    </td>
                </tr>
                <tr>
                    <td class="td_label"><label>选择文件</label></td>
                    <td class="td_input">
                        <input class="easyui-filebox filebox-f textbox-f" style="height: 26px; width: 380px; display: none;" data-options="required:true,editable:false" id="file" buttontext="选择" textboxname="file"><span class="textbox textbox-invalid filebox" style="width: 378.4px; height: 24.4px;"><a href="javascript:;" class="textbox-button textbox-button-right l-btn l-btn-small" group="" id="" style="height: 24px;"><span class="l-btn-left" style="margin-top: -3px;"><span class="l-btn-text">选择</span></span><label class="filebox-label" for="filebox_file_id_1"></label></a><input id="_easyui_textbox_input1" type="text" class="textbox-text validatebox-text validatebox-readonly validatebox-invalid textbox-prompt" autocomplete="off" tabindex="" readonly="readonly" placeholder="" style="margin: 0px 51px 0px 0px; padding-top: 0px; padding-bottom: 0px; height: 24.4px; line-height: 24.4px; width: 319.4px;" title=""><input type="file" class="textbox-value" id="filebox_file_id_1" name="file" accept=""></span>
                    </td>
                </tr>
                <tr>
                <td colspan="4" style="text-align: center;">
                        <span style="margin-right: 20px">
                            <input class="submit" type="submit" value="提交" style="width: 56px;height: 28px">
                            <a class="easyui-linkbutton l-btn l-btn-small" data-options="iconCls:'icon-cancel'" href="javascript:void(0)" onclick="cancel()" group="" id=""><span class="l-btn-left l-btn-icon-left"><span class="l-btn-text">取消</span><span class="l-btn-icon icon-cancel">&nbsp;</span></span></a>
                         </span>
                </td>
                </tr>
            </tbody></table>
        </div>
    </form>


"""

import requests
import os
import json

uploadURL = "https://cmsp.evsmc.cn/sysSafeMessage/alarmSort"

uploadHeader = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Referer":"https://cmsp.evsmc.cn/sysSafeMessage/alarmType.html?ids=3c000dbca32a4d48aff424801a4f4256"
}

pdfPath = os.path.join(os.path.abspath(".."), "../pdf")

files ={"file":open("./pdf/2023-02-03/LMVABEDX5KA000062国标三级报警故障处理20221112122129.pdf", 'rb')}


warningID = "3c000dbca32a4d48aff424801a4f4256"
#
datas = {"idsStr": "3c000dbca32a4d48aff424801a4f4256", "alarm":"3"}

# json_str = json.dumps(datas)
# print(json_str)

cookie = {"WEB_SESSION": "6DE126FB19213CC6AB7B4646C723D9D3"}

response = requests.post(url=uploadURL, headers=uploadHeader, cookies=cookie,data=datas, files=files)

print(response)
