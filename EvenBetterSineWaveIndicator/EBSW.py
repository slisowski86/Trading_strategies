from Strategy import Strategy
import pandas as pd
import numpy as np
import math
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import typing as tt
from itertools import product

class EBSW(Strategy):

    def __init__(self,data):

        self.data=data
        self.possible_strats={'e_a_b_l':{'name':'ebsw_below_above_levels',
                           'positions':{'buy':'ebsw_above_down_level','sell':'ebsw_below_up_level'},
                           'strategy_desc':'Strategy EBSW (EvenBetterSineWaveIndicator by J.Ehlers) change position above below given levels',
                            'pos_columns':{}}}

        self.params_range={'duration':[20,30,40,50],
                      'up_level':[0.5,0.65,0.8],
                      'down_level':[-0.8,-0.65,-0.5]}

                      
 
        

    def create_params_combs(self):

        return list(product(*self.params_range.values()))

        

    def sine(self,x:float)->float:

        return np.sin(np.radians(x))

    def cosine(self,x:float)->float:

        return np.cos(np.radians(x))

        

    def calc_indicator(self, duration)->tt.List:
        self.calc_col_name=f'Wave_dur_{duration}'
        self.duration=duration

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

        self.data[self.calc_col_name]=wave_arr
        

    def calc_position(self,up_level:float=0.8, down_level:float=-0.8)->pd.Series:

        
        df=self.data.copy()
       
        
        for k in self.possible_strats.keys():
            if k=='e_a_b_l':
                keys=[]
                vals=[]
                
                col_name_pos_ch=f'pos_ch_{k}_up_{up_level}_dn_{down_level}_dur_{self.duration}'
                col_name_pos=f'pos_{k}_up_{up_level}_dn_{down_level}_dur_{self.duration}'
                df[col_name_pos_ch]=np.nan
                df[col_name_pos_ch]=np.where((df[self.calc_col_name]>down_level)&(df[self.calc_col_name].shift()<down_level),1,df[col_name_pos_ch])
                df[col_name_pos_ch]=np.where((df[self.calc_col_name]<up_level)&(df[self.calc_col_name].shift()>up_level),-1,df[col_name_pos_ch])
                df[col_name_pos]=df[col_name_pos_ch].ffill()
                self.data[col_name_pos]=df[col_name_pos]
                self.data[col_name_pos_ch]=df[col_name_pos_ch]
                col_name_pos_ch_string=f'buy when EBSW going above {down_level}, sell when EBSW going below {up_level} and duration is {self.duration}'
                col_name_pos_string=f'buy when EBSW is above {down_level}, sell when EBSW is below {up_level} and duration is {self.duration}'
                #keys.append(col_name_pos_ch)
                #keys.append(col_name_pos)
                #vals.append(col_name_pos_ch_string)
                #vals.append(col_name_pos_string)
                self.possible_strats[k]['pos_columns'][col_name_pos_ch]=col_name_pos_ch_string
                self.possible_strats[k]['pos_columns'][col_name_pos]=col_name_pos_string
                #print(dict(zip(keys,vals)))
                
                                              
                

   

        

        

    def plot_pos_chart(self, n_candles:int=400):

        col_pos_to_plot=None
        col_wave_to_plot=None

        for c in self.data.columns:

            if 'Wave' in c:
                col_wave_to_plot=c
                break

        for c in self.data.columns:

            if 'pos_ch' in c:
                col_pos_to_plot=c
                break

        df_plot=self.data.iloc[:n_candles].copy()
        df_plot=df_plot.loc[:,['o','h','l','c',col_wave_to_plot,col_pos_to_plot]]

        

        

        
            

        y_color_sell=df_plot[df_plot[ col_pos_to_plot]==-1]['h']*1.0002
        y_color_sell_index=df_plot[df_plot[ col_pos_to_plot]==-1].index
        y_color_buy=df_plot[df_plot[ col_pos_to_plot]==1]['l']*0.9998
        y_color_buy_index=df_plot[df_plot[ col_pos_to_plot]==1].index

    
       
        figure = make_subplots(rows=2, cols=1, row_heights=[0.7,0.3], shared_xaxes=True,vertical_spacing=0.01)
        figure.update_layout(height=800, width=1200, title_text=self.possible_pos['e_a_b_l'][col_pos_to_plot])
        
    
        figure.add_trace(go.Candlestick(x=df_plot.index,
                                        open=df_plot['o'],
                                        high=df_plot['h'],
                                        low=df_plot['l'],
                                        close=df_plot['c'],
                                        name='price'), row=1, col=1)
        figure.add_trace(go.Scatter(x=df_plot.index,y=df_plot[col_wave_to_plot],mode='lines',line_color='green',name=col_wave_to_plot),col=1,row=2 )
        figure.add_trace(go.Scatter(x=y_color_sell_index, y=y_color_sell, mode='markers', marker_symbol='arrow-down', marker_color='red', name='sell', marker_size=10), col=1, row=1)
        figure.add_trace(go.Scatter(x=y_color_buy_index, y=y_color_buy, mode='markers', marker_symbol='arrow-up', marker_color='green', name='buy', marker_size=10), col=1, row=1)

        
       
    
        figure.update_layout(xaxis_rangeslider_visible=False)
        figure.update_xaxes(
        rangebreaks=[
            dict(bounds=["sat", "mon"])]
    )
        figure.show()
        

        