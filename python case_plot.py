# -*- coding: utf-8 -*-
"""
Created on Mon Apr 25 19:13:30 2022

@author: bdgcx
"""
#====================================================
#病历创建
#====================================================

#创建病历
import time
date=print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
date=input('就诊时间：')
department=input('科室：')
name=input('姓名：')
gender=input('性别：')
age=input('年龄：')
id_number=input('门诊号：')
complaint=input('主诉：')
history=input('既往史：')
examination=input('体格检查：')
diagnosis=input('初步诊断：')
treatment=input('处理：')
doctor_signature=input('医师签名：')
#存储为字典
patient_info={
    '就诊时间：':date,
    '科室：':department,
    '姓名：':name,
    '性别：':gender,
    '年龄：':age,
    '门诊号：':id_number,
    '主诉：':complaint,
    '既往史：':history,
    '体格检查：':examination,
    '初步诊断：':diagnosis,
    '处理：':treatment,
    '医师签名：':doctor_signature
    }
print(patient_info)

#写循环，简化上述代码
info_item= ('就诊时间：','科室：','姓名：','性别：','年龄：',
            '门诊号：','主诉：','既往史：','体格检查：','初步诊断：',
            '处理：','医师签名：')
patient_info={}
for info in info_item:
    value=input(info)
    patient_info[info]=value

print(patient_info)

#多个患者
import pandas as pd
patients=('Lily','Candy','Bob','John')
info_item= ('就诊时间','科室','姓名','性别','年龄',
            '门诊号','主诉','既往史','体格检查','初步诊断',
            '处理','医师签名')
patient_info={}
for patient_name in patients:
    for info in info_item:
        value=input(info)
        if info not in patient_info:
            patient_info[info]=[value]
        else:
            patient_info[info].append(value)
patient_info=pd.DataFrame(patient_info)
print(patient_info)

#====================================================
#数据整理
#====================================================

import pandas as pd
from pathlib import Path

#获取目标文件夹下的所有文件列表
file_path=Path('./exercise_2')
df=pd.DataFrame()

for index,file in enumerate(file_path.rglob('*.csv')):
    #print(index,file.name)
    data=pd.read_csv(file,na_values=' ')
    if df.empty:
        df=data
    else:
        df=pd.merge(df, data,how='outer')
        #批量重命名
        newname='dataset'+str(index+1)+'.csv'
        file.rename(file.parent/newname)
    
print(df.tail())

#数据排序
df.sort_values(by='id', inplace=True)
#数据缺失值处理
df.dropna(how='all', inplace=True)
#how='all'当列或行的所有值都缺失时删除缺失值，不指明how默认只要有缺失值就删除
df.fillna(value=df.mean(), inplace=True)#缺失值填充
#数据重复值处理
df.drop_duplicates(inplace=True)
#数据提取
ages=df['Age']
#面元分切
age_bins=[0,18,30,50,100]
age_labels=['<18','18-30','31-50','>50']
df['Group']=pd.cut(ages, age_bins,labels=age_labels)
#分组变换
df_div_group=pd.get_dummies(df,columns='Group',prefix='G')
#写入到文件
df_div_group.to_csv('./alldata.csv',index=False) 


#=====================================================
#绘图
#=====================================================
'''                     
基线表
'''
from tableone import TableOne
import pandas as pd
#载入需要处理的数据
df=pd.read_csv('./tableone_sample.csv',encoding='ansi')
#csv的编码方式不是默认的utf-8,而是ansi
print(df.tail())
#整个数据的描述汇总
table=TableOne(df)
#设置缺失值列省略和整体列省略
table=TableOne(df,missing=False,overall=False)
#设置mean(SD),n(%)等信息的省略
table=TableOne(df,label_suffix=False)
#设置需要描述汇总的变量信息（哪些变量需要进行汇总，显示的顺序设置）
var_name=['age','gender','status','survival','path_level','T','N','M','AJCC']
table=TableOne(df,columns=var_name)
#将年龄分层，即面元分切形成新的年龄分组
ages=df['age']
#面元分切
age_bins=[0,18,30,50,100]
age_labels=['<18','18-30','31-50','>50']
df['age_group']=pd.cut(ages, age_bins,labels=age_labels)
#指定分类变量及分类变量值的显示顺序
table=TableOne(df,
               categorical=['status'],#必须使用中括号，因为该参数接受的是列表型数据
               order={'status':['live','dead']})
#设置非正态分布的变量,不使用mean(SD),而使用median [Q1,Q3]进行描述
table=TableOne(df,nonnormal=['age','survival'])
#设置需要描述最大最小值的变量
table=TableOne(df,
               nonnormal=['age','survival'],
               min_max=['age']#可以是正态/非正态分布连续变量
               )
#设置分组统计
table=TableOne(df,groupby='status')
#计算p值，SMD(标准化均数差)的值
table=TableOne(df,
               missing=False,
               overall=False,
               nonnormal=['age','survival'],
               groupby='status',
               pval=True,
               htest_name=True,#显示检验方式
               smd=True)

#变量的排序,即便设置了变量顺序，还是会按照sort排序
var_name=['age','gender','status','survival','path_level','T','N','M','AJCC']
table=TableOne(df,
               missing=False,
               overall=False,
               columns=var_name,
               groupby='status',
               pval=True,
               sort='P-Value'
               )
#变量的重命名
table=TableOne(df,
               missing=False,
               overall=False,
               nonnormal=['age','survival'],
               groupby='status',
               pval=True,
               htest_name=True,#显示检验方式
               smd=True,
               rename={'age':'Age','status':'Status'}
               )
#变量的输出
print(table.tableone)#这样就可以只显示基线表不显示多余的冗余信息
print(table.tabulate(tablefmt='fancy_grid'))#可以完整显示表格
table.to_excel('./result.xlsx')
#还可以自定义检验方法及输出格式等需要自己摸索
'''
创建画布
'''
import matplotlib.pyplot as plt
plt.figure(figsize=[10,10])#设置画布的大小
'''
折线图
'''
import matplotlib.pyplot as plt

#基本折线图的绘制
alice_temp=[36.8, 37.2, 38.5, 38.2, 38.0, 37.5, 37.6]
plt.plot(alice_temp)
#指定x轴的折线图的绘制
data=[1,3,5,7,9,11,13]
plt.plot(data, alice_temp)
#折线图线条颜色、线条，标记字符
plt.plot(data, 
         alice_temp,
         color='r',
         linestyle='--',
         marker='*')
#以下设置不要关闭绘图窗口
#x轴、y轴范围的设置
plt.xlim(2,25)
plt.ylim(35.0, 42.0)
#x-y轴标签的设置
plt.xlabel('Data')
plt.ylabel('Temperature')
#Title的设置
plt.title("Alice's temp report")
#x轴、y轴坐标刻度的设置
plt.xticks(data)
data_ch=['8月1日','8月3日','8月5日','8月7日',
         '8月9日','8月11日','8月13日']
plt.rcParams['font.family']='FangSong'#有中文时设置中文字体
plt.xticks(data,data_ch,color='b',rotation=60)

plt.yticks([36,38,40,42])

#多条折线图的绘制与图例的设置
alice_temp=[36.8, 37.2, 38.5, 38.2, 38.0, 37.5, 37.6]
bob_temp=[38.1, 38.5, 39, 39.2, 38.5, 38.5, 38.6]
plt.plot(data, 
         alice_temp,
         c='r',
         ls='--',
         marker='*',
         label='Alice')
#不要关闭绘图窗口接着画
plt.plot(data, 
         bob_temp,
         c='b',
         ls='-',
         marker='o',
         label='Bob')
plt.legend()#显示图例

#图形显示
plt.show()

'''
散点图
'''
import matplotlib.pyplot as plt

#基本散点图的绘制
x=[0.1, 0.3, 0.3, 0.5, 0.9, 0.1, 0.6, 0.7, 0.8, 0.9]
y=[0.8, 0.6, 0.7, 0.2, 0.6, 0.1, 0.3, 0.8, 0.5, 0.9]
plt.scatter(x, y)
#散点大小的设置
plt.scatter(x, y, s=200)#统一设置点的大小

yy=[val*150 for val in y]#由于y值太小，先扩大150倍
plt.scatter(x, y, s=yy)#点的大小随y值的大小变化

#散点形状的设置
plt.scatter(x, y, s=yy, marker='s')

#颜色与透明度设置
plt.scatter(x, y, s=yy, marker='s',c='b')#颜色统一

plt.scatter(x, y, s=yy, marker='s',
            c=y, cmap='rainbow',alpha=0.5)#颜色映射，根据y值改变

#x轴、y轴范围的设置
plt.xlim(0,1.5)
plt.ylim(0,1.5)
#x,y轴坐标刻度的设置
scale=[0, 0.3, 0.6, 0.9, 1.2, 1.5]
plt.xticks(scale,color='b',rotation=60)
plt.yticks(scale)
#x-y轴标签的设置
plt.xlabel('variables x')
plt.ylabel('variables y')
#Title的设置
plt.title('Scatter')

#多组散点图的绘制与图例的设置
x2=[0.3, 0.5, 0.5, 0.7, 0.3, 0.2, 0.7, 0.6, 0.3, 0.5]
y2=[0.6, 0.4, 0.5, 0.4, 0.3, 0.8, 0.5, 0.7, 0.6, 0.8]
plt.scatter(x, y, s=100, marker='s',
            c=y, cmap='rainbow',alpha=0.5,label='x1')

plt.scatter(x2, y2, s=50, marker='^',
            c='k',alpha=0.5,label='x2')
plt.legend(loc='upper right')
#图形显示

'''
柱状图
'''
import matplotlib.pyplot as plt
import numpy as np
x=[0,1,2,3,4,5,6,7]#每个柱状数据的x轴坐标
data=[1,5,2,3,7,5,9,2]#每个柱状数据的y坐标，与x坐标数一致
#基础柱状图绘制
plt.bar(x, data, width=0.3)#width=0.3每个柱状图的宽度，默认为0.8
plt.show()
#颜色设置
#可以是颜色首字母缩写，也可以是十六进制颜色值，可以一次设置多种颜色
plt.bar(x, data, width=0.3,color=['c','r'])
#描边设置
plt.bar(x, data, width=0.3,
        edgcolor='k',#描边颜色
        linewidth=2,#描边粗细
        linestyle='--'#描边风格
        )
#填充设置
#'/' '\' '|' '-' '+' 'X' 'o' 'O' '.' '*'
plt.bar(x, data, width=0.3,hatch='/')
#x-y轴标签的设置
plt.xlabel('Group')
plt.ylabel('Data')
#Title与图例标签的设置
plt.bar(x, data,label='data')
plt.title('Figure2')
plt.legend()

#刻度设置
x=np.arange(8)
data=[1,5,2,3,7,5,9,2]
plt.bar(x, data)
plt.show()
#不要关闭绘图窗口
x_label=['A','B','C','D','E','F','G','H']
plt.xticks(x, x_label)

#标签设置 plt.text()
#zip函数将对象中对应的元素打包成元组
#a,b说明标签添加的位置
#b说明标签的内容
#verticalalignment表示数据标签与柱状图顶端垂直对齐方式：'center' 'top' 'bottom' 'baseline'
#horizotalalignment表示数据边框与柱状图之间的水平对齐方式：'center' 'right' 'left'
x=np.arange(8)
data=[1,5,2,3,7,5,9,2]
plt.bar(x, data)
for a,b in zip(x,data):
    plt.text(a, b, 
             b, 
             fontsize=10,#标签字体大小
             color='r',
             verticalalignment='bottom',
             horizotalalignment='center')
#柱状图误差设置
#yerr参数用于表示垂直误差，正向误差=负向误差：[误差] 正向误差≠负向误差：[(正向误差),(负向误差)]
#error_kw参数设置误差记号的相关属性
std_err=[(0.1, 0.2, 0.5, 0.2, 0.2, 0.1, 1, 0.3),
         (0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3,0.3)]
error_params=dict(elinewidth=3, #线型粗细
                  ecolor='r',#颜色
                  capsize=5)#设置顶部横线大小
plt.bar(x, data, yerr=std_err, error_kw=error_params)

#堆叠柱状图的绘制
#绘制时除了底层不需要参数bottom,其余每一层的bottom参数均为下面所有柱体的高度之和
x=np.arange(8)
data1=[1,5,2,3,7,5,9,2]
data2=[4,6,3,5,9,7,1,7]
data3=[2,1,4,4,8,6,5,5]
plt.bar(x, data1,color='b',label='data1')
plt.bar(x, data2,bottom=data1,color='gray',label='data2')
plt.bar(x, data3,bottom=data2,color='r',label='data3')
plt.legend()

#并列柱状图的绘制
x=np.arange(8)
data1=[1,5,2,3,7,5,9,2]
data2=[4,6,3,5,9,7,1,7]
data3=[2,1,4,4,8,6,5,5]
bar_width=0.3
plt.bar(x, data1,width=bar_width,color='b',label='data1')
plt.bar(x+bar_width,data2,width=bar_width,color='gray',label='data2')
plt.bar(x+bar_width*2,data3,width=bar_width,color='r',label='data3')
plt.legend()
#设置x轴刻度标签位置
plt.xticks(x+bar_width,x)

#横向柱状图的绘制
#plt.yticks(y,y_label)重命名y轴刻度
#xerr参数，用于表示水平型误差
y=np.arange(8)
data1=[1,5,2,3,7,5,9,2]
plt.barh(y,data1,height=0.3)

'''
饼图
'''
import matplotlib.pyplot as plt
label=['vivo','huawei','oppo','mi','apple']
values=[10,200,20,300,250]
colors=['green','r','c','orange','gray']
#基础饼图绘制
plt.pie(values,labels=label,colors=colors)
#参数设置
plt.pie(values,labels=label,colors=colors,
        shadow=True,#阴影
        explode=(0,0,0,0,0.1),#饼图分离
        startangle=45,#饼图旋转,逆时针旋转
        autopct='%1.1f%%',#比例显示
        pctdistance=0.8,#比例显示位置
        radius=0.5#饼图大小
        )

#autopct='%1.2f%%'：3.80%
#autopct='%5.1f%%'：3.8%
#autopct='%05.1f%%'：003.8%
#第一个%表示要将得到的数据进行格式化
#f：float代表浮点型数据,用于储存小数的数据类型
#小数点后的数字表示保留几位小数，小数点前表示总位数，05.表示总位数小于5则在前边加0补齐到5位
#后边两个%中第一个%是对第二个%进行转义，代表要在得到的数据后边添加一个%

#空心饼图设置
plt.pie(values,labels=label,colors=colors,
        shadow=True,#阴影
        explode=(0,0,0,0,0.1),#饼图分离
        startangle=45,#饼图旋转,逆时针旋转
        autopct='%1.1f%%',#比例显示
        pctdistance=0.8,#比例显示位置
        radius=0.5,#饼图大小
        wedgeprops=dict(width=0.2)
        )

#图例设置
plt.legend(label, loc='upper left')


'''
箱线图
'''
import matplotlib.pyplot as plt
import numpy as np
data1=[8,3,15,12,14,56,40,36,27,10,110]
data2=np.random.random_integers(4,60,11)
data3=np.random.random_integers(5,55,11)
#基础箱线图绘制
plt.boxplot(data1)
plt.show()
#多组箱线图绘制
plt.boxplot([data1,data2,data3])
#修改x坐标刻度
label_name=['data1','data2','data3']
plt.boxplot([data1,data2,data3],labels=label_name)
#显示中位数的置信区间
plt.boxplot([data1,data2,data3],
            labels=label_name,
            notch=True)
#异常值形状的设置
plt.boxplot([data1,data2,data3],
            labels=label_name,
            sym='^')
#如果不需要显示异常值
plt.boxplot([data1,data2,data3],
            labels=label_name,
            showfliers=False)
#四分位框内填充颜色
plt.boxplot([data1,data2,data3],
            labels=label_name,
            patch_artist=True)
#自定义设置四分位框
plt.boxplot([data1,data2,data3],
            labels=label_name,
            patch_artist=True,
            boxprops={'color':'black','facecolor':'blue'})
#每个四分位框各自上色
box=plt.boxplot([data1,data2,data3],
            labels=label_name,
            patch_artist=True,
            boxprops={'color':'black'})
colors=['pink','lightblue','lightgreen']
for box,color in zip(box['boxes'],colors):
    box.set_facecolor(color)
#boxplot的返回值是一个字典，包含六个key值
#'boxes'箱体 'medians'中位数线段 'whiskers'数值线条 'flier'异常值 'means'均值点 'caps'上下边缘线

#显示x轴、y轴与图名称
plt.xlabel('Group')
plt.ylabel('Data')
plt.title('Figure')
#网格设置,默认的grid函数会把横纵轴的网格线都绘制出来
plt.grid(axis='y',linestyle='--',color='lightgray')
#水平箱线图绘制
box=plt.boxplot([data1,data2,data3],
            labels=label_name,
            patch_artist=True,
            boxprops={'color':'black'},
            vert=False)
'''
多图组合
'''
import matplotlib.pyplot as plt
#创建画布
plt.figure()
#定位绘制区域进行绘制
ax1=plt.subplot(2,2,1)
#第一个参数为画布被分成的行数，第二个参数为画布分成的列数，第三个参数为当前正在绘制的子图索引号
x=[0.1, 0.3, 0.3, 0.5, 0.9, 0.1, 0.6, 0.7, 0.8, 0.9]
y=[0.8, 0.6, 0.7, 0.2, 0.6, 0.1, 0.3, 0.8, 0.5, 0.9]
x2=[0.3, 0.5, 0.5, 0.7, 0.3, 0.2, 0.7, 0.6, 0.3, 0.5]
y2=[0.6, 0.4, 0.5, 0.4, 0.3, 0.8, 0.5, 0.7, 0.6, 0.8]
ax1.scatter(x, y, s=20, marker='s',
            c=y, cmap='rainbow',alpha=0.5,label='x1')
ax1.scatter(x2, y2, s=20, marker='^',
            c='k',alpha=0.5,label='x2')
ax1.legend(loc='upper right')
ax1.set_title('Left figure')#设置对应Axes的子标题

ax2=plt.subplot(2,2,2)
x=np.arange(8)
data=[1,5,2,3,7,5,9,2]
ax2.bar(x, data)
ax2.set_xticks(np.arange(8))
x_label=['A','B','C','D','E','F','G','H']
ax2.set_xticklabels(x_label)
ax2.set_title('Right figure')

ax3=plt.subplot(2,1,2)
data1=[8,3,15,12,14,56,40,36,27,10,110]
data2=np.random.random_integers(4,60,11)
data3=np.random.random_integers(5,55,11)
box=ax3.boxplot([data1,data2,data3],
            labels=label_name,
            patch_artist=True,
            boxprops={'color':'black'})
colors=['pink','lightblue','lightgreen']
for box,color in zip(box['boxes'],colors):
    box.set_facecolor(color)
ax3.set_title('Bottom figure')

plt.suptitle('Figure')#设置图像的总标题
plt.tight_layout()
plt.show()

#子图标签设置
ax1.set_xlabel('X1')
ax1.set_ylabel('Y1')
#子图图例设置
ax1.legend
#子图区间设置
ax1.set_xlim(0,10)
ax1.set_ylim(0,15)
#子图刻度设置
ax2.set_xticks(np.arange(8))#设置显示刻度的位置
x_label=['A','B','C','D','E','F','G','H']
ax2.set_xticklabels(x_label)#设置刻度内容及相关颜色、字体、旋转

#子图布局的设置
plt.tight_layout()
#自动调整函数，使之填充整个图像区域，可以解决多个plots出现的重叠现象
plt.tight_layout(rect=[0,0.05,1,0.95]) 
#rect参数前两位是绘制的其实坐标，后两位是长和宽
#pad参数设置绘图区边缘与画布边缘的距离
#w_pad设置绘图区之间的水平距离
#h_pad设置绘图区之间的垂直距离

#多图组合的另一种方法
plt.subplot2grid()
ax1=plt.subplot2grid((3,3), (0,0), colspan=3,rowspan=1)
ax2=plt.subplot2grid((3,3), (1,0), colspan=2,rowspan=1)
ax3=plt.subplot2grid((3,3), (1,2), colspan=1,rowspan=2)
ax4=plt.subplot2grid((3,3), (2.0), colspan=1,rowspan=1)
ax5=plt.subplot2grid((3,3), (2.1), colspan=1,rowspan=1)
#第一个参数表示分成几行几列
#第二个参数表示绘图开始的位置
#colspan表示子图列跨度
#rowspan表示子图行跨度

'''
多图叠加
'''
import matplotlib.pyplot as plt
#不同类型的多个图形x轴和y轴一致，叠加时同相同类型的多个图形叠加
data1=np.random.randint(30,60,8)
data2=np.random.randint(3,30,8)
plt.plot(data1)
plt.bar(range(len(data2)),data2)

#当坐标轴不同时，设置双坐标轴
data1=np.random.randint(3,30,8)
data2=np.random.randint(300,600,8)
plt.figure()
ax1=plt.subplot(1,1,1)
ax1.bar(range(len(data1)),data1)
ax1.set_xlabel('Group')
ax1.set_ylabel('Data1')

ax2=ax1.twinx()#表示共享x轴，twiny表示共享y轴
ax2.plot(data2,color='r')
ax2.set_ylabel('Data2')
plt.suptitle('Figure')
plt.show()

#=================================================
'''
自然语言处理(NLP)实现病历结构化
'''
#=================================================
'''
基于机器学习的方法
'''
# 对病历内容的深度语义理解
# 指定领域中需要抽取的知识本体
# 为每一个目标知识点，标注足够的训练数据
# 使用学习的方法基于训练数据，训练出识别模型，自动学习模式，处理新的病历文档

'''
基于规则提取的方法
'''             
# 对病历内容不进行理解
# 很多文本内容有很多显著的规律可循
# 通过手动构建有规律的逻辑表达形式，从表格中、文本中把相关的信息提取出来
# 多采用正则表达式(regular expression)对规则进行描述

'''
正则表达式语法
1.字符匹配
. :除换行符以外任意字符
\w :任意字母、数字、汉字和下划线
\s :任意空白字符、Tab
\d :任意数字
\W :非字母、数字和汉字
\S :非空白字符、Tab
\D :非数字
2.数量匹配
* ：>=0次
? :0次或1次
+ :>=1次
{n} :n次
{n,} :>=n次
{n,m} :重复n到m次，包括n和m
3.位置匹配
^ :匹配字符串开始位置
$ :匹配字符串结束位置
\b :匹配一个位置，这个位置前后字符不全为\w，单词边界，python里用\\b
4.特殊字符
[] :匹配括号中的任意一个字符
() :将正则表达式的一部分括起来组成一个单元，可以对整个单元使用数量限定符
\  :转义符号，想使用任何一个有含义的字符时，前面需要使用转义符号
|  :“或”语义，竖线前后任一正则满足即可
例： key1:{0,1}(.*)key2
key1:?(.*)key2均为提取key1:和key2之间的任意字符
'''
#=================================================
'''
电子病历结构化python代码实现
'''
#=================================================
'''
病历文件读入
'''
#txt文档
from pathlib import Path
file=Path('./xx.txt')
content=Path.read_text(file,encoding='utf-8')

#docx文件
from pathlib import Path
import docx2txt
file=Path('./xx.docx')
content=docx2txt.process(file)

#pdf文档
from pathlib import Path
import pdfplumber
file=Path('./xx.pdf')
with pdfplumber.open(file) as pdf:
    pages=pdf.pages
    content=''
    for pg in pages:
        content= content+ pg.extract_text()
print(content)
'''
病历结构表示
'''
#构建病历结构的方法
#1.手动输入，同本文档最开始
#2.网站https://www.sojson.com/editor.html
'''
json是一种轻量级的数据交换格式
采用完全独立于编程语言的文本格式来储存和表示数据
易于人阅读和编写，同时也易于机器解析和生成
类似于XML，但比它更小、更快、更容易解析
与python字典相似，以key：value的形式存储信息
但与字典不同的是key的类型只能是字符串，且字符串只能用双引号
使用json构建病历结构是因为其与字典相似，且双引号也可以被python正确识别
'''

'''
病历结构提取
'''
#实现python的正则表达式功能
import re
#re.compile()函数生成一个正则表达式(pattern)对象
#参数pattern是匹配模式
#参数flags是标志位，re.I：匹配忽略大小写区别 re.S:使.匹配包括换行符在内的所有字符
#re.M:多行匹配，印象^和$ re.L:做本地化识别匹配，由当前语言区域决定\w,\W,\b,\B和大小写敏感匹配
#re.U:根据Unicode字符集解析字符，这个标志影响\w,\W,\b,\B
#re.X:通过给予你更灵活的格式以便你将正则表达式写得更易于理解
content='a李雷bA韩梅梅B'
pat=re.compile('a(.*?)b',re.I)

#re.findall()函数：正则表达式在字符串中所有匹配结果的列表
content='a李雷bA韩梅梅B'
pat=re.compile('a(.*?)b',re.I)
names=re.findall(pat, content)
print(names)

content='a李雷bA韩梅梅B'
names=re.findall('a(.*?)b', content, re.I)

#通过循环结构获取字典中key的列表
#构建字典
info_item= ('就诊时间','科室','姓名','性别','年龄',
            '门诊号','主诉','既往史','体格检查','初步诊断',
            '处理','医师签名')
patient_info={}
for info in info_item:
    value=input(info)
    patient_info[info]=value
print(patient_info)

#获取字典中key的列表
keylist=[]
for key in patient_info.keys():
    keylist.append(key)
print(keylist)

#最后一个key值的终止位置应该是文本结束位置
#采用正则表达式的位置匹配：$匹配字符串结尾，最后一个key提取的时候应该以$作为作为结束位置
#循环前keylist.append('$')
keylist=[]
for key in patient_info.keys():
    keylist.append(key)
keylist.append('$')
print(keylist)

#利用列表的索引位置提取任意key
for n in range(len(keylist)-1):
    key_n=keylist[n]
    key_next=keylist[n+1]
    
#python中使用+连接两个字符串
#re.compile('现病史:{0,1}(.*?)既往史'，re.I)
#使用循环结构后key_n与key_next不再是固定的字符串，而是一个存储字符串的变量
for n in range(len(keylist)-1):
    key_n=keylist[n]
    key_next=keylist[n+1]

key_n+':{0,1}(.*?)'+key_next

#遍历所有的key
#定义一个函数
def read_all_keys(obj_d):
    for key,value in obj_d.items():
        if isinstance(value,dict):#也可以写成if type(value)==dict:
            read_all_keys(value)
        print(key)
#函数返回某些值的定义方法
keylist=[]
def read_all_keys(obj_d):
    for key,value in obj_d.items():
        keylist.append(key)
        if isinstance(value,dict):#也可以写成if type(value)==dict:
            read_all_keys(value)
    return keylist
        
d={'key1':'value1',
   'key2':'value2',
   'key3':{'key3-1':'value3-1',
           'key3-2':{'key3-2-1':'value3-2-1',
                     'key3-2-2':'value3-2-2'
                     }
           }
   } 
l=read_all_keys(d)
print(l)

#循环获得key_n和key_next
for n in range(len(keylist)):
    print(n,keylist[n],keylist[n+1])

#==================================================
'''
实操
'''
#==================================================
#读入病历
from pathlib import Path
import docx2txt
file=Path('./xx.docx')
content=docx2txt.process(file)
#定义函数
def read_all_keys(patient_info,content):
    keylist=[]
    for key in patient_info.keys():
        keylist.append(key)
    
    keylist.append('$')
    #print(keylist)
    
    for n in range(len(keylist)-1):
        key_n=keylist[n]
        key_next=keylist[n+1]
        # print(key_n,key_next)
        
        pat=re.compile(key_n+ ':{0,1}(.*?)'+key_next,re.S)
        #print(key_n+ ':{0,1}(.*?)'+key_next)
        matchs=re.findall(pat, content)
        key_content=''.join(matchs)
        #print(key_n,matchs)
        
        if isinstance(patient_info[key_n],dict):
            read_all_keys(patient_info[key_n], key_content)
        else:    
            patient_info[key_n]=key_content
        
#创建病历字典patient_info                           
info_item= ('就诊时间','科室','姓名','性别','年龄',
            '门诊号','主诉','既往史','体格检查','初步诊断',
            '处理','医师签名')
patient_info={}
for info in info_item:
    value=input(info)
    patient_info[info]=value
#调用函数
read_all_keys(patient_info, content)
print(patient_info)
#复制到so json网站左边栏，然后点击解析json,可以在右边栏看提取内容是否正确

#==================================================
'''
数据的综合处理
'''
#==================================================
'''
提取子节点
'''
d={
    "病案号": 1000123,
    "姓名": "杨某某",
    "职业": "职工",
    "性别": "男",
    "实验室检查": {
        "心电图": "窦性心律，各导联无异常",
        "血常规": "白细胞60.5×109/L",
        "血生化": "无"
    },
    "体格检查": {
        "体温": "40℃",
        "呼吸": "26次/分",
        "血压": "170/70mmHg"
    },
    "入院诊断": "高血压",
    "医生签名": "王某某"
}
#判断某个key是否存在于字典中
'实验室检查' in d
#获取某个无子结构的key的value
d['入院诊断']
#获取某个有子结构的key的value
#需要声明所有上层节点的key值才能提取
d['实验室检查']['血常规']
#使用循环获得嵌套字典中子结构的key的value
#将多层的结构使用'.'将层节点隔开，如'实验室检查.血常规'
#使用split()函数将其化为列表类型，如['实验室检查','血常规']
#使用循环结构循环获取指定子节点内容，并逐层获得目标子节点的内容，如第一次先获得'实验室检查'的值，第二次再获得'血常规'的值

name1='实验室检查.血常规'
name_list1=name1.split('.')
obj=d
for current_key in name_list1:
    #print(current_key)
    obj=obj[current_key]
    print(current_key, obj)

name2='体格检查.血压'
name_list2=name2.split('.')
obj2=d
for current_key2 in name_list2:
    #print(current_key)
    obj2=obj2[current_key2]
    print(current_key2, obj2)

names=['实验室检查.血常规','体格检查.血压']
for name in names:
    name_list=name.split('.')
    obj=d
    for current_key in name_list:
        obj=obj[current_key]
    
    print(current_key, obj)#只输出最后层级的的key和value
            
names=['实验室检查.血常规','体格检查.血压']
for name in names:
    name_list=name.split('.')
    obj=d
    for current_key in name_list:
        obj=obj[current_key]
        print(current_key, obj)#输出全部keyz和value


# 基于关键字的目标病历筛选

# 1.基于pandas字符串模糊匹配方法
# 匹配固定关键字，如心脏病
# 将所有数据写入DataFrame后进行匹配
df[df['入院诊断'].str.contains('心脏病|高血压')]

# 2.基于正则表达式匹配，根据匹配结果数量进行判断
# 灵活匹配关键字，如'心 脏 病'
# 支持一边进行结构化一边进行匹配，也支持全部进行结构化后进行匹配
# 构建正则表达式，使用re.findall()函数，获得所有匹配的结果列表
# matchs=re.findall(r'高\s*学\s*压',…… )，返回匹配的字符串列表
# 使用len()函数进行判断，len(manchs)==0,即不包含筛选的关键字
hbp='高血压'
#hbp='高\s*血\s*压'
#list(hbp)
#'\s*'.join(list(hbp))
pat_hbp=re.compile(r''+hbp,re.S)
mark=[]
for index in range(len(df)):
    record=df.ilco[index]
    #print(record)
    content=record['入院诊断']
    match=re.findall(pat_hbp, content)
    if len(match) !=0:
        mark.append(True)
    else:
        mark.append(False)
print(df[mark])
       
        
# 对提取的结果的进行数据类型转换
# ''.join()将列表类型转换为字符串类型
# list(map(类型, 列表))：将列表中的每个元素均转换为特定类型
# int()将字符串转换为整数型类型
# float()将字符串转换为浮点型
# pd.to_datetime():将日期字符串转换为日期

# 正则表达式举例：日期匹配
# 2020/3/17  2019-10-8
# \d{4}[/-]\d{1,2}[/-]\d{1,2} 
# [/-]代表匹配[]中的任意一个字符，如果要匹配多个字符则使用(),如(否定|不)

# 3天前  二十三天前
# \w{1,3}天前

# 2015年3月18日  2013年2月  2020年
# \d{4}年(?:\d{1,2}月)?(?:\d{1,2}日)?
# ():分组，将括号内看作一个整体，在re.findall()函数中，如果有分组就仅返回分组中的内容
# ?:出现0次或1次，等同于{0,1}
# (?:):将括号内视为一个整体，但返回时返回所有匹配内容

# 匹配单一模式的正则表达式
# pat=re.compile(r'(?:体温|T)\W*(\d{2}.?\d?)(?:℃|度)',……)
# 建议在正则表达式字符串前加上r,raw的缩写，不进行转义，直接使用原生字符串，即按照字面意思来使用

# 匹配多种模式的正则表达式
# 多个条件的‘或’关系：模式1|模式2|模式3……
# 将所有模式的正则表达式以字符串的形式放入列表，然后采用'|'.join()将各个模式的正则表达式字符串连接成一个字符串
# pat_list=['模式1','模式2','模式3']
# pat_str='|'.join(pat_list)
# pat=re.compile(r"+pat_str,……)
# matchs=re.findall(pat,……)

# [\u4e00-\u9fa5]:匹配所有中文字符
# [^...]:表示不匹配集合中的字符

#=====================================================
'''
电子病历批量结构化
'''
#=====================================================
#导入所需模块
from pathlib import Path
import pandas as pd
import re
import docx2txt

#Mac在终端：pip install docx2txt
#anaconda的windows prompt: pip install docx2txt

#结构分析，标注key,构建structure,可使用so json网站
struct={
    "病案号": 1000123,
    "姓名": "杨某某",
    "职业": "职工",
    "性别": "男",
    "实验室检查": {
        "心电图": "窦性心律，各导联无异常",
        "血常规": "白细胞60.5×109/L",
        "血生化": "无"
    },
    "体格检查": {
        "体温": "40℃",
        "呼吸": "26次/分",
        "血压": "170/70mmHg"
    },
    "入院诊断": "高血压",
    "医生签名": "王某某"
}
#定义结构化病历所需的函数
def read_all_keys(struct,content):
    #获取同一层次的所有key的列表
    keylist=[]
    for key in struct.keys():
        keylist.append(key)
    #添加终止符$为最后一个key值
    keylist.append('$')
    #循环每一个key值
    for n in range(len(keylist)-1):
        #获取当前key的内容
        key_n=keylist[n]
        key_with_space='\s*'.join(list(key_n))
        #判断当前key是否存在，如果不存在就不需要寻找key的value，直接将value设置为空
        key_current=re.findall(key_with_space, content)
        if len(key_current) ==0:
            struct[key_n]=''
            continue
        #如果key存在，应该取寻找下一个key值作为终止符
        for next_n in range(n+1,len(keylist)):
            key_next=keylist[next_n]
            key_next_with_space='\s*'.join(list(key_next))
            key_next_current=re.findall(key_next_with_space, content)
            #判断如果下一个值不是终止符，也没有存在于病历中，就再寻找下一个key
            if len(key_next_current) ==0 and key_next !='$':
                continue
            #找到了邻近的key_n和key_next,采用正则表达式提取内容作为key的value值        
            pat=re.compile(key_with_space+ '[:：]{0,1}(.*?)'+key_next_with_space,re.S)
            matchs=re.findall(pat, content)
            key_content=''.join(matchs)
            #判断当前key是否包含层级结构，如果包含，获得的内容再次使用子key进行拆解提取
            if isinstance(struct[key_n],dict):
                read_all_keys(struct[key_n], key_content)
            else:    
                struct[key_n]=key_content
            break
    return None

#按照最终需要的excel表头，提取相关的信息并存入DataFrame
cols=['文件名','病案号','姓名','职业','性别','实验室检查','体格检查','入院诊断','医生签名']
df=pd.DataFrame(columns=cols)
#用rglob获取所有病历文件
folder=Path('C:/Users/bdgcx/OneDrive/python/sample')
#用rglob获取所有病历文件，注意循环的层级关系，不要随意缩进  
for file in folder.rglob('*.docx'):
    #读入每个病历文档
    content=docx2txt.process(file)
    #调用read_all_keys函数，依次读取每个key值
    read_all_keys(struct, content)
    record={}
    for c in cols:
        if c =='文件名':
            record[c]=file.name
        else:
            record[c]=struct
    df=df.append(record, ignore_index=True)
#所有病历获取结束后，将DataFrame的值写入到excel中
df.to_excel('C:/Users/bdgcx/OneDrive/python/sample/result.xlsx')   
            
#=====================================================
'''
特定描述的病历数据提取
'''
#=====================================================        
#读取子结构里的key值对应的value然后导入excel中单独一列，例如实验室检查里的血常规
#导入所需模块
from pathlib import Path
import pandas as pd
import re
import docx2txt

#Mac在终端：pip install docx2txt
#anaconda的windows prompt: pip install docx2txt

#结构分析，标注key,构建structure,可使用so json网站
struct={
    "病案号": 1000123,
    "姓名": "杨某某",
    "职业": "职工",
    "性别": "男",
    "现病史": " ",
    "既往史": " ",
    "个人史": " ",
    "实验室检查": {
        "心电图": "窦性心律，各导联无异常",
        "血常规": "白细胞60.5×109/L",
        "血生化": "无"
    },
    "体格检查": {
        "体温": "40℃",
        "呼吸": "26次/分",
        "血压": "170/70mmHg"
    },
    "入院诊断": "高血压",
    "医生签名": "王某某"
}
#定义结构化病历所需的函数
def read_all_keys(struct,content):
    #获取同一层次的所有key的列表
    keylist=[]
    for key in struct.keys():
        keylist.append(key)
    #添加终止符$为最后一个key值
    keylist.append('$')
    #循环每一个key值
    for n in range(len(keylist)-1):
        #获取当前key的内容
        key_n=keylist[n]
        key_with_space='\s*'.join(list(key_n))
        #判断当前key是否存在，如果不存在就不需要寻找key的value，直接将value设置为空
        key_current=re.findall(key_with_space, content)
        if len(key_current) ==0:
            struct[key_n]=''
            continue
        #如果key存在，应该取寻找下一个key值作为终止符
        for next_n in range(n+1,len(keylist)):
            key_next=keylist[next_n]
            key_next_with_space='\s*'.join(list(key_next))
            key_next_current=re.findall(key_next_with_space, content)
            #判断如果下一个值不是终止符，也没有存在于病历中，就再寻找下一个key
            if len(key_next_current) ==0 and key_next !='$':
                continue
            #找到了邻近的key_n和key_next,采用正则表达式提取内容作为key的value值        
            pat=re.compile(key_with_space+ '[:：]{0,1}(.*?)'+key_next_with_space,re.S)
            matchs=re.findall(pat, content)
            key_content=''.join(matchs)
            #判断当前key是否包含层级结构，如果包含，获得的内容再次使用子key进行拆解提取
            if isinstance(struct[key_n],dict):
                read_all_keys(struct[key_n], key_content)
            else:    
                struct[key_n]=key_content
            break
    return None

#按照最终需要的excel表头，提取相关的信息并存入DataFrame
cols=['文件名','病案号','姓名','职业','性别',
      '实验室检查.血常规','体格检查','入院诊断']
df=pd.DataFrame(columns=cols)
#编辑datafilters中要获取指标的正则表达式
date_pat=['\d{4}[/-]\d{1,2}[/-]\d{1,2}']
ctnt_pat=['cTnT.*?[,，；;。]']
drug_pat=['\w*氯吡格雷\w*','\w*阿司匹林\w*']

hist_pat=[]
smoking_pat=[]

temp_pat=[]
pulse_pat=[]
resp_pat=[]
bp_pat=[]

datafilters={'现病史':{
                 '日期':date_pat,
                 '指标情况':ctnt_pat,
                 '特殊用药':drug_pat},
             '既往史':{'既往情况':hist_pat},
             '个人史':{'烟酒史':smoking_pat},
             '体格检查':{
                 '体温':temp_pat,
                 '脉搏':pulse_pat,
                 '呼吸':resp_pat,
                 '血压':bp_pat}
             }

#用rglob获取所有病历文件
folder=Path('C:/Users/bdgcx/OneDrive/python/sample')
#用rglob获取所有病历文件，注意循环的层级关系，不要随意缩进  
for file in folder.rglob('*.docx'):
    #读入每个病历文档
    content=docx2txt.process(file)
    #调用read_all_keys函数，依次读取每个key值
    read_all_keys(struct, content)
    record={}
    
    for c in cols:
        if c =='文件名':
            record[c]=file.name
        else:
            # record[c]=struct
            name_levels=c.split('.')
            
            current_value=struct
            name1='实验室检查.血常规'
            for nl in name_levels:
                #print(current_key)
                current_value=current_value[nl]
            record[c]=current_value
        #如果要对datafilters中的项目进行进一步的筛选    
        if c in datafilters:
            filter_items=datafilters[c]
            for item_name,item_rule in filter_items.items():
                # print(item_name,item_rule)
                item_rule_str='|'.join(item_rule)
                item_data=re.findall(r''+item_rule_str, record[c], re.I|re.S)
                
                if len(item_data) !=0:
                    record[item_name]='\n'.join(item_data)
                else:
                    record[item_name]='无'
                
    df=df.append(record, ignore_index=True)
     
#所有病历获取结束后，将DataFrame的值写入到excel中
df.to_excel('C:/Users/bdgcx/OneDrive/python/sample/result.xlsx')   
            


















