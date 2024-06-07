# 載入必要函數
import indicator,sys,time,datetime,haohaninfo,order_Lo3_test4
from haohaninfo import MicroPlay
import lineTool
from haohaninfo.MicroTest import microtest_db
#import numpy as np

# 取得必要參數 券商代號 商品名稱
# Broker = sys.argv[1]
# Prod = sys.argv[2]
# KMinute= int(sys.argv[3])
# ShortMAPeriod= int(sys.argv[4])
# LongMAPeriod= int(sys.argv[5])
# StopLoss= int(sys.argv[6])


Broker = 'Test'
Prod = 'MXFH9'   ## 'MXFD1', 'MXFH7'
KMinute= 1
ShortMAPeriod=2
LongMAPeriod=3
Qty = '3'

## 下單或平倉口數的數量大於1者, 事實上還是 "逐口"進行交易
O_B_Qty = '3'
O_S_Qty = '3'
#C_S_Qty = '2'   ## 下列程式會以現有的在倉部位口數當作要出場交易的口數, C_S_Qty 為進場是多單, 出場要賣的口數
#C_B_Qty = '2'   ## 下列程式會以現有的在倉部位口數當作要出場交易的口數, C_B_Qty 為進場是空單, 出場要賣的口數
StopLoss = 30
StopLossPoint_B = 0
StopLossPoint_S = 100000000000
wait_O = 20 #單位: 秒
wait_C = 150  #單位: 秒
 
## Line token:
token='eCIbl5sLUTgHTHYXrkrS2CVaszxVXbOEiHMiL9dBWP2'



# 部位管理物件
RC=order_Lo3_test4.Record()


# K棒物件     
Today = '20190731'        ##Today = time.strftime('%Y%m%d')   Today = '20210331'; Today = '20170803'
KBar = indicator.KBar(Today,KMinute) 


a = MicroPlay.MicroPlayQuote()
lineTool.lineNotify(token,"程式交易開始")



#RSI 指標回測
for row in a.Subscribe(Broker, 'match', Prod):
    # 定義時間
    CTime = datetime.datetime.strptime(row[0],'%Y/%m/%d %H:%M:%S.%f')
    # 定義成交價、成交量
    CPrice=float(row[2])
    CQty=int(row[3])
    # 更新K棒 若新Kbar則判斷開始判斷策略
    if KBar.AddPrice(CTime,CPrice,CQty) == 1:
        CloseList= KBar.GetClose()
        HighList= KBar.GetHigh()
        LowList= KBar.GetLow()
        if len(CloseList) >=6 :
                RSI6= KBar.GetRSI(6)
                RSI12= KBar.GetRSI(12)
                ClosePrice= CloseList[-2]
                HighPrice= HighList[-2]
                LowPrice= LowList[-2]
                LastClosePrice=CloseList[-3]
                LastRsi6= RSI6[-3]
                LastRsi12= RSI12[-3]
                FirstRsi6= RSI6[-2]
                FirstRsi12= RSI12[-2]
                
                print('目前在倉部位口數:',RC.GetOpenInterest(),'目前成交報價資料時間:',CTime,'最新收盤價:',ClosePrice,'上一筆收盤價:',LastClosePrice,'最新RSI6:', LastRsi6,'上一筆RSI12:', LastRsi12,'最新RSI6:', FirstRsi6,'上一筆Rsi12:', FirstRsi12)
            
            # 判斷進場的部分
                if RC.GetOpenInterest() == 0:
                    # 黃金交叉 買進多單
                    if (FirstRsi6<25 and (HighPrice- ClosePrice)<(ClosePrice- LowPrice)) or (LastRsi6<20 and FirstRsi6>20):
                        # 透過上兩檔價委託多單(範圍市價單 委託三次 若未成交則當日不交易)
                        #OrderInfo=order.RangeMKTDeal(Broker,Prod,'B',Qty,'0','A',2,10)
                        OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'B',O_B_Qty,'0',2,wait_O)   ## OrderInfo: ['SNVS:113,N,MXFD1,Sell,16456,1,ROD,2021-03-31 10:30:55.11,T0001,1']
                        # 如果沒有成交則關閉程序
                        
                        if OrderInfo == False: 
                            #GO.EndSubscribe()
                            #a.EndSubscribe()
                            print("OrderBuyFalse")
                            continue
                        else:
                            for i in OrderInfo:
                                # 成交則寫入紀錄至部位管理物件 
                                OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                                OrderInfoPrice=float(i.split(',')[4])
                                OrderProd = i.split(',')[2]
                                OrderQty = i.split(',')[5]
                                RC.Order('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                                # 紀錄移動停損停利價位
                                StopLossPoint_B= max(OrderInfoPrice-StopLoss,StopLossPoint_B)  ## 還有小問題
                                print('交易編號:',i.split(',')[0] ,', 產品:', OrderProd,', 多單進場買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_B,', 多單成交買進口數:',OrderQty,', 多單委託買進口數:',O_B_Qty)
                                
                                msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 多單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 多單成交買進口數: '+str(OrderQty)+'; 多單委託買進口數: '+str(O_B_Qty)
                                lineTool.lineNotify(token,msg)
                                #GO.EndSubscribe()
                                #a.EndSubscribe()
                                print("OrderBuyTrue"+str(RC.GetOpenInterest()))
                                
                # 死亡交叉 買進空單
                    elif (LastRsi6>75 and FirstRsi6<75):   
                        # 透過下兩檔價委託空單(範圍市價單 委託三次 若未成交則當日不交易)
                        #OrderInfo=order_Lo2.RangeMKTDeal(Broker,Prod,'S',Qty,'0','A',2,10)
                        OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'S',O_S_Qty,'0',2,wait_O)
                        
                        # 如果沒有成交則關閉程序
                        if OrderInfo == False:
                            #GO.EndSubscribe()
                            #a.EndSubscribe()
                            print("OrderBuyFalse")
                            continue
                        else:
                            for i in OrderInfo:
                                # 成交則寫入紀錄至部位管理物件 
                                OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                                OrderInfoPrice=float(i.split(',')[4])
                                OrderProd = i.split(',')[2]
                                OrderQty = i.split(',')[5]
                                RC.Order('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                                # 紀錄移動停損停利價位
                                StopLossPoint_S= OrderInfoPrice+StopLoss  ## 還有小問題
                                print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 空單買進時間:',OrderInfoTime,', 買進價格:',OrderInfoPrice,', 停損價位:',StopLossPoint_S,', 空單成交買進口數:',OrderQty,', 空單委託買進口數:',O_S_Qty)
                                print()
                                msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 空單買進時間: '+str(OrderInfoTime)+'; 買進價格: '+str(OrderInfoPrice)+'; 空單成交買進口數: '+str(OrderQty)+'; 空單委託買進口數: '+str(O_S_Qty)
                                lineTool.lineNotify(token,msg)
                                #GO.EndSubscribe()
                                #a.EndSubscribe()
                                print("OrderSellTrue"+str(RC.GetOpenInterest()))
                                
                                # 判斷多單出場的部分
                elif RC.GetOpenInterest() > 0:    ## == 1
                    # 移動停損判斷
                    if ClosePrice-StopLoss > StopLossPoint_B:
                        StopLossPoint_B=ClosePrice-StopLoss 
                    elif ClosePrice <= StopLossPoint_B:
                            # 透過下兩檔價委託空單(範圍市價單 委託三次 若未成交則當日不交易)
                            #OrderInfo=order_Lo2.RangeMKTDeal(Broker,Prod,'S',Qty,'0','A',2,10)
                            C_S_Qty = RC.GetOpenInterest()   ## 以現有的在倉部位口數當作要出場交易的口數
                            OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'S',C_S_Qty,'0',2,wait_C)
                    
                        # 如果沒有成交則關閉程序
                            if OrderInfo == False:
                                #GO.EndSubscribe()
                                #a.EndSubscribe()
                                print("CoverSellFalse")
                                continue
                            else:
                                for i in OrderInfo:
                                    # 成交則寫入紀錄至部位管理物件 
                                    OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                                    OrderInfoPrice=float(i.split(',')[4])
                                    OrderProd = i.split(',')[2]
                                    OrderQty = i.split(',')[5]
                                    MicroTest_Qty = OrderQty
                                    RC.Cover('S',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                                    ## 紀錄移動停損停利價位
                                    #StopLossPoint= OrderInfoPrice-StopLoss
                                    print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 多單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 多單成交平倉口數:',OrderQty,', 多單委託平倉口數:',C_S_Qty)
                                    print()
                                    msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 多單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 多單成交平倉口數: '+str(OrderQty)+'; 多單委託平倉口數: '+str(C_S_Qty)
                                    lineTool.lineNotify(token,msg)
                                    #GO.EndSubscribe()
                                    #a.EndSubscribe()
                                    print("CoverSellTrue"+str(RC.GetOpenInterest()))
                                    # 判斷空單出場的部分
                elif RC.GetOpenInterest() < 0:     ## == -1
                    # 移動停損判斷
                    if ClosePrice+StopLoss < StopLossPoint_S:
                        StopLossPoint_S=ClosePrice+StopLoss 
                    elif ClosePrice+StopLoss >= StopLossPoint_S:
                            # 透過下兩檔價委託空單(範圍市價單 委託三次 若未成交則當日不交易)
                            #OrderInfo=order_Lo2.RangeMKTDeal(Broker,Prod,'B',Qty,'0','A',2,10)
                            C_B_Qty = -(RC.GetOpenInterest())   ## 以現有的在倉部位口數當作要出場交易的口數
                            OrderInfo=order_Lo3_test4.RangeMKTDeal(Broker,Prod,'B',C_B_Qty,'0',2,wait_C)
                            # 如果沒有成交則關閉程序
                            if OrderInfo == False:
                                #GO.EndSubscribe()
                                #a.EndSubscribe()
                                print("CoverBuyFalse")
                                continue
                            else:
                                for i in OrderInfo:
                                    # 成交則寫入紀錄至部位管理物件 
                                    OrderInfoTime=datetime.datetime.strptime(i.split(',')[7],'%Y-%m-%d %H:%M:%S.%f')
                                    OrderInfoPrice=float(i.split(',')[4])
                                    OrderProd = i.split(',')[2]
                                    OrderQty = i.split(',')[5]
                                    MicroTest_Qty = OrderQty
                                    RC.Cover('B',OrderProd,OrderInfoTime,OrderInfoPrice,OrderQty)
                                    ## 紀錄移動停損停利價位
                                    #StopLossPoint= OrderInfoPrice-StopLoss
                                    print('交易編號:',i.split(',')[0] ,', 產品:',OrderProd,', 空單平倉時間:',OrderInfoTime,', 平倉價格:',OrderInfoPrice,', 空單成交平倉口數:',OrderQty,', 空單委託平倉口數:',C_B_Qty)
                                    print()
                                    msg='交易編號: '+i.split(',')[0]+'; 產品: '+OrderProd+'; 空單平倉時間: '+str(OrderInfoTime)+'; 平倉價格: '+str(OrderInfoPrice)+'; 空單成交平倉口數: '+str(OrderQty)+'; 空單委託平倉口數: '+str(C_B_Qty)
                                    lineTool.lineNotify(token,msg)
                                    print("CoverBuyTrue"+str(RC.GetOpenInterest()))
                                    #GO.EndSubscribe()
                                    #a.EndSubscribe()
                                    

#print('交易紀錄:',RC.TradeRecord)
print('交易紀錄:',RC.GetTradeRecord())
print('在倉部位數量:',RC.GetOpenInterest())  
print('在倉部位清單:',RC.OpenInterest)
print('績效記錄清單:',RC.GetProfit())
print('淨交易績效:', RC.GetTotalProfit(), ', 平均每次交易績效(包含盈虧):',RC.GetAverageProfit(), ', 勝率(賺錢次數占總次數比例):',RC.GetWinRate(),', 最大連續虧損:', RC.GetAccLoss(), ', 最大資金(績效profit)回落(MDD):',RC.GetMDD(),', 平均每次獲利(只算賺錢的):',RC.GetAverEarn(),', 平均每次虧損(只算賠錢的):',RC.GetAverLoss())
print('最大回落區間', RC.GetMDD())
## 產出累積績效圖(包含盈虧):
RC.GeneratorProfitChart()


























