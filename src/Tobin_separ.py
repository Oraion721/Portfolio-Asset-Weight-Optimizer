import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import yfinance as yf
from typing import Literal
from calculations import EF_calc

class Tobin_sep(EF_calc):
    def __init__(self,PF_data,PF_data_type,PF_data_interval,transform_data_type,index_data,transform=True,contain_index=True):
        super().__init__(PF_data,PF_data_type,PF_data_interval,transform_data_type,index_data,transform,contain_index)
        self.base_calculations()
        self.calc_covariance() 

    def weight_calc(self,rfr:float,idx_name:str):
        self.rfr=rfr
        self.idx_name=idx_name
        once_vec=np.ones(len(self.inv_covariance))
        exp_rtr=self.expected_daily_returns(rfr)
        self.E=exp_rtr[self.idx_name].values
        b_weight=(self.inv_covariance.values@once_vec)/np.sum(self.inv_covariance@once_vec)
        self.baseline_weight=pd.Series(b_weight,index=self.inv_covariance.index)
        h1=self.inv_covariance.values@self.E
        self.h1=pd.Series(h1,index=self.covariance.index)
        h2=(np.sum(h1)/np.sum(self.inv_covariance.values@once_vec))*(self.inv_covariance.values@once_vec)
        self.h2=pd.Series(h2,index=self.covariance.index)
        self.esc_weight=self.h1-self.h2
        return self.baseline_weight,self.esc_weight 

    def c_calc(self,target_ret_range:tuple):
        tar_ret=np.linspace(target_ret_range[0],target_ret_range[1],550).tolist()
        tar_ret_series=pd.Series(tar_ret)
        self.c=(tar_ret_series-(self.baseline_weight.T@self.E))/(self.esc_weight.T@self.E)
        return self.c

    def pf_weight(self,c:float):      # c is individually selected from self.c
        w=self.baseline_weight+(c*self.esc_weight)
        return pd.Series(w,index=self.baseline_weight.index)

if __name__=="__main__":
    asset_df=yf.download(tickers=['AXISBANK.NS','BAJAJ-AUTO.NS','BAJAJFINSV.NS','BDL.NS','BEL.NS','BSE.NS','BHEL.NS','EICHERMOT.NS','FEDERALBNK.NS','HAL.NS','SBIN.NS'],period='3y',interval='1d',auto_adjust=True)['Close']
    index_df=yf.download(tickers=['^NSEI','^BSESN'],period='3y',interval='1d',auto_adjust=True)['Close']
    a=Tobin_sep(PF_data=asset_df,PF_data_type='normal',PF_data_interval='daily',transform_data_type='returns',index_data=index_df,transform=True,contain_index=True)
    b=Tobin_sep(PF_data=asset_df,PF_data_type='normal',PF_data_interval='daily',transform_data_type='returns',index_data=index_df,transform=True,contain_index=True)
    print(a.weight_calc(rfr=0.0001428,idx_name='^BSESN'))
    print(f"b_weight={a.baseline_weight.sum()},esc_weight={a.esc_weight.sum()}")
    # print(f"b_weight={b.baseline_weight.sum()},esc_weight={b.esc_weight.sum()}")
    print(a.c_calc(target_ret_range=(0.0001,0.001))); print(type(a.c))
    print(a.pf_weight(c=-6.519421)); print(a.pf_weight(-6.519421).sum())
