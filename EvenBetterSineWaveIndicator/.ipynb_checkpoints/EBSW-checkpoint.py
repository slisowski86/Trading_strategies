from Strategy import Strategy
import pandas as pd
import numpy as np
import math
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import typing as tt

class EBSW(Strategy):

    def __init__(self,data):

        self.data=data
       

       

    def sine(self,x:float)->float:

        return np.sin(np.radians(x))

    def cosine(self,x:float)->float:

        return np.cos(np.radians(x))

        

    def calc_indicator(self, duration:int=40)->tt.List:

        alpha1=(1-self.sine(360/duration))/self.cosine(360/duration)
        a1=np.exp(-np.sqrt(2)*math.pi/10)
        b1=2*a1*self.cosine(np.sqrt(2)*180/10)
        c2=b1
        c3=-a1*a1
        c1=1-c2-c3
        df=self.data.copy()
        filt_arr=[]
        wave_arr=[]
        HP=0
        
        for i in range(len(df)):
            HP_1=HP
            Close=df['c'].iloc[i]
            Close_1=df['c'].iloc[i-1] if i-1>=0 else df['c'].iloc[0]
           
            Filt_1=filt_arr[i-1] if i-1>=0 else 0
            Filt_2=filt_arr[i-2] if i-2>=0 else 0
        
            HP=0.5*(1+alpha1)*(Close-Close_1)+alpha1*HP_1
            Filt=c1*(HP+HP_1)/2+c2*Filt_1+c3*Filt_2
        
            Wave=(Filt+Filt_1+Filt_2)/3
            Pwr=(Filt*Filt+Filt_1*Filt_1+Filt_2*Filt_2)/3
            Wave=Wave/np.sqrt(Pwr)
            
        
            
            filt_arr.append(Filt)
            wave_arr.append(Wave)

        self.data['Wave']=wave_arr

    def calc_position(self,up_level:float=0.8, down_level:float=-0.8)->pd.Series:

       
        df=self.data.copy()
        df['pos_ch']=np.nan
        df['pos_ch']=np.where((df['Wave']>down_level)&(df['Wave'].shift()<down_level),1,df['pos_ch'])
        df['pos_ch']=np.where((df['Wave']<up_level)&(df['Wave'].shift()>up_level),-1,df['pos_ch'])
        df['pos']=df['pos_ch'].ffill()
        self.data['pos']=df['pos']
        self.data['pos_ch']=df['pos_ch']

    def plot_pos_chart(self, n_candles:int=400):

        df_plot=self.data.iloc[:n_candles].copy()

        y_color_sell=df_plot[df_plot['pos_ch']==-1]['h']*1.0002
        y_color_sell_index=df_plot[df_plot['pos_ch']==-1].index
        y_color_buy=df_plot[df_plot['pos_ch']==1]['l']*0.9998
        y_color_buy_index=df_plot[df_plot['pos_ch']==1].index

    
       
        figure = make_subplots(rows=2, cols=1, row_heights=[0.7,0.3], shared_xaxes=True,vertical_spacing=0.01)
        figure.update_layout(height=800, width=1200, title_text="Even Better Sine Wave Indicator")
        
    
        figure.add_trace(go.Candlestick(x=df_plot.index,
                                        open=df_plot['o'],
                                        high=df_plot['h'],
                                        low=df_plot['l'],
                                        close=df_plot['c'],
                                        name='price'), row=1, col=1)
        figure.add_trace(go.Scatter(x=df_plot.index,y=df_plot['Wave'],mode='lines',line_color='green'),col=1,row=2 )
        figure.add_trace(go.Scatter(x=y_color_sell_index, y=y_color_sell, mode='markers', marker_symbol='arrow-down', marker_color='red', name='sell', marker_size=10), col=1, row=1)
        figure.add_trace(go.Scatter(x=y_color_buy_index, y=y_color_buy, mode='markers', marker_symbol='arrow-up', marker_color='green', name='buy', marker_size=10), col=1, row=1)

        
       
    
        figure.update_layout(xaxis_rangeslider_visible=False)
        figure.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"])]
    )
        figure.show()


    
        

        