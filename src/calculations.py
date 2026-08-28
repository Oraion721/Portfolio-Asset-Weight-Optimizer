import numpy as np
import pandas as pd
import yfinance as yf
from typing import Literal
 
class EF_calc:
    def __init__(self,PF_data:pd.DataFrame,PF_data_type:Literal['normal','log','returns','log_returns'],
                 PF_data_interval:Literal['daily','weekly','monthly'],transform_data_type:Literal['log','returns','log_returns'],
                 index_data:pd.DataFrame,transform:bool=True,contain_index:bool=True):
        """ Required i/p:
                ~ PF_data:pd.DatarFrame -> assets price data
                ~ PF_data_type:Literal['normal','log','returns','log-returns'] -> type of PF_data
                ~ PF_data_interval:Literal['daily','weekly','yearly'] -> interval of PF_data
                ~ transform_data_type:Literal['log','returns','log_returns'] -> transform data into which type?
                ~ index_data:pd.DataFrame -> index funds's data
                ~ transform:bool=False -> Do you want to transform the data? (default=False) 
                ~ contain_index:bool=True -> index funds are included?
            O/P:
                return {'mean(daily)':[],'mean(yearly)':[],
                        'std(daily)':[],'std(yearly)':[], 
                        'var(daily)':[],'var(yearly)':[]    }  """
        self.data=PF_data
        self.pf_data_type=PF_data_type
        self.data_interval=PF_data_interval
        self.tf_data_type=transform_data_type
        self.tf=transform
        self.index_data=index_data
        self.contain_index=contain_index

        # ============ Validate dataframes =============
        if not isinstance(self.data,pd.DataFrame):
            raise TypeError("Data must be pd.DataFrame")
        if self.data.empty:
            raise ValueError("Data is empty")
        if self.data.shape[1]<2:
            raise ValueError(f"EF_Calc requires >=2 TS, got {self.data.shape[1]}")
        if not isinstance(self.index_data,pd.DataFrame):
            raise TypeError('Index data must be pd.DataFrame')
        if self.index_data.empty:
            raise ValueError('Index data is empty')
        if self.index_data.shape[1]<1:
            raise ValueError(f"EF_Calc requires len(index_data)>2, got {self.index_data.shape[1]}")
        if self.data.shape[0]!=self.index_data.shape[0]:        # making both asset and index dataframe same rows size
            print(f"PF_data rows:{self.data.shape[0]} != index_data rows:{self.index_data.shape[0]}\n removing extra rows!")
            if self.data.shape[0]>self.index_data.shape[0]:
                self.data=self.data[self.data.index.isin(self.index_data.index)]
                if self.data.shape[0]==self.index_data.shape[0]:
                    print(f"Converted both dataset into same rows: (PF_data,index_data) = {self.data.shape[0],self.index_data.shape[0]}")
                else:
                    print(f"Can not make same size rows of assets and index. Try with better data!")
            else:
                self.index_data=self.index_data[self.index_data.index.isin(self.data.index)]
                if self.data.shape[0]==self.index_data.shape[0]:
                    print(f"Converted both dataset into same rows: (PF_data,index_data)=({self.data.shape[0],self.index_data.shape[0]})")
                else:
                    raise ValueError("Can not make same size rows of assets and index. Try with same period & interval data!")
        
        # =========== Validate i/p =============
        if self.pf_data_type not in ['normal','log','returns','log_returns']:
            raise ValueError(f"PF_data_type must be from ['normal','log','returns','log-returns'], but got {self.pf_data_type}")
        if self.data_interval not in ['daily','weekly','monthly']:
            raise ValueError(f"PF_data_interval should be one of ['daily','weekly','monthly'], but got {self.data_interval}")
        if self.tf_data_type not in ['log','returns','log_returns']:
            raise ValueError(f"transform_data_type should be one of ['log','returns','log_returns'], but got {self.tf_data_type}")
        if not isinstance(self.tf,bool):
            raise TypeError(f"transform should be bool, but got {self.tf}")
        if not isinstance(self.contain_index,bool):
            raise TypeError(f"contain_index should be bool, but got {self.contain_index}")

        # ========== Apply transformation & declare attributes ==============
        if self.tf:
            self.assets_prepared_data,self.index_prepared_data=self._transform_data()
            self.asset_cols=self.assets_prepared_data.columns.tolist()        # asset_data columns name list
            self.index_cols=self.index_prepared_data.columns.tolist()            # index_data columns name list
            self.T=len(self.assets_prepared_data)                 # number of rows in prepared data
            self.m=self.assets_prepared_data.shape[1]        # number of columns in prepared data
            # self.Hedge_ratio=self.calc_hedge_ratio()
        if self.data_interval=='daily':
            self._trading_days=252
        elif self.data_interval=='weekly':
            self._trading_days=52
        else:
            self._trading_days=12

    def __repr__(self):
        date_start=self.assets_prepared_data.index[0].date()
        date_end=self.assets_prepared_data.index[-1].date()
        return (f"EF_Calc(assets={self.m}, obs={self.T},type='{self.pf_data_type}->{self.tf_data_type}',interval='{self.data_interval}',dates='{date_start} to {date_end}')")
    
    def _transform_data(self):
        if self.tf and self.contain_index:
            asset_df=self.data.copy().ffill()
            index_df=self.index_data.copy().ffill()
            if self.tf_data_type=='log':
                if (asset_df<=0).any().any() or (index_df<=0).any().any():
                    raise ValueError("transform='log': requires all values > 0\n found non-positive values in data")
                asset_df=np.log(asset_df)
                index_df=np.log(index_df)
            elif self.tf_data_type=='log_returns':
                if (asset_df<=0).any().any() or (index_df<=0).any().any():
                    raise ValueError("transform='log_returns': All Dataframe values should be > 0.\nFound non-positive values in data.")
                asset_df=np.log(asset_df/asset_df.shift(1))
                index_df=np.log(index_df/index_df.shift(1))
            elif self.tf_data_type=='returns':
                if (asset_df<=0).any().any() or (index_df<=0).any().any():
                    raise ValueError("transform='returns': All DataFrame values should be > 0 \nFound non-postive values in data.")
                asset_df=(asset_df/asset_df.shift(1))-1
                index_df=(index_df/index_df.shift(1))-1
            else:
                print("Can not transform the data in required type.")

            asset_df=asset_df.replace([np.inf,-np.inf],np.nan).dropna()
            index_df=index_df.replace([np.inf,-np.inf],np.nan).dropna()
            if asset_df.empty or index_df.empty:
                raise ValueError('Data is Empty after removal of NaN values')
            if asset_df.shape[0]!=index_df.shape[0]:
                print(f"Converting transformed data in same rows size.")
                combined=pd.concat([asset_df,index_df],axis=1).dropna()
                asset_df=combined[asset_df.columns]
                index_df=combined[index_df.columns]

            return asset_df,index_df 
        
        elif self.tf and not self.contain_index:
            raise ValueError("Got only assets data\nAdd index data with same period & interval for transformation!")
        else:
            raise ValueError("Invalid transformation selected.\nEF_calc.transform & EF_calc.contain_index both should be True")

    def base_calculations(self):
        if not self.contain_index:
            raise ValueError(f"contain_index should be True, calculations are perfomed on index references.")
        else:
            if self.pf_data_type=='normal' and self.tf_data_type=='returns' and self.data_interval=='daily':
                self.asset_mean_daily=self.assets_prepared_data.mean()
                self.index_mean_daily=self.index_prepared_data.mean()
                self.asset_var_daily=self.assets_prepared_data.var()
                self.index_var_daily=self.index_prepared_data.var()
                self.asset_std_daily=self.assets_prepared_data.std()
                self.index_std_daily=self.index_prepared_data.std()
                self.asset_mean_annual=(self.assets_prepared_data.add(1).prod()).pow(self._trading_days/len(self.assets_prepared_data)).sub(1)
                self.index_mean_annual=(self.index_prepared_data.add(1).prod()).pow(self._trading_days/len(self.index_prepared_data)).sub(1)
                self.asset_var_annual=self.asset_var_daily*self._trading_days
                self.index_var_annual=self.index_var_daily*self._trading_days
                self.asset_std_annual=self.asset_std_daily*np.sqrt(self._trading_days)
                self.index_std_annual=self.index_std_daily*np.sqrt(self._trading_days)
                asset_res={'Daily Mean':self.asset_mean_daily,'Annual Mean':self.asset_mean_annual,
                        'Daily Var':self.asset_var_daily,'Annual Var':self.asset_var_annual,
                        'Daily Std':self.asset_std_daily,'Annual Std':self.asset_std_annual}
                index_res={'Daily Mean':self.index_mean_daily,'Annual Mean':self.index_mean_annual,
                        'Daily Var':self.index_var_daily,'Annual Var':self.index_var_annual,
                        'Daily Std':self.index_std_daily,'Annual Std':self.index_std_annual }
                asset_res_df=pd.DataFrame(asset_res)
                index_res_df=pd.DataFrame(index_res)
                return asset_res_df,index_res_df
            else:
                raise ValueError(f"Only arithmatic transformation are required for calculations. \nPF_data_type={self.pf_data_type} and tf_data_type={self.tf_data_type} are invalid for arithmetic calculations,\nUse PF_data_type='normal' & tf_data_type='returns'    ")

    def calc_covariance(self):
        self.covariance=self.assets_prepared_data.cov()
        self.inv_covariance=pd.DataFrame(np.linalg.inv(self.covariance.values),index=self.covariance.index,columns=self.covariance.columns)
        return self.covariance, self.inv_covariance

    def calc_hedge_ratio(self):      # hedge_ratio (β) = covariance(stock_returns,index_returns) / var(index_returns)
        if self.assets_prepared_data.shape[0]==self.index_prepared_data.shape[0]:
            res={}
            for i in self.index_cols:
                beta={}
                for j in self.asset_cols:
                    cov=self.assets_prepared_data[j].cov(self.index_prepared_data[i])
                    var=self.index_prepared_data[i].var()
                    beta[j]=cov/var
                res[i]=beta
            hedge_ratio_df=pd.DataFrame(res)
            return hedge_ratio_df
        else:
            raise ValueError(f"assets data {self.assets_prepared_data.shape} != index data {self.index_prepared_data.shape}\nMake sure asset & index data have same rows before calling EF_calc.calc_hedge_ration()")

    def expected_daily_returns(self,rfr:float):
        # expected_daily_returns (E_{ri}) = (risk_free_rate) + [asset_hedge_ratio*(asset_daily_return - risk free rate)]
        if not hasattr(self, 'asset_mean_daily'):
            raise RuntimeError("Call base_calculations() before expected_daily_returns()")
        if not isinstance(rfr,float):
            raise ValueError(f"{rfr} is not float, please provide float value < 0.001")
        if rfr<0 or rfr>0.0008:
            raise ValueError(f"rfr={rfr} is looks unreasonable. Expected small value e.g. 0.000268 ")
        E_rf={}
        hedge_ratio=self.calc_hedge_ratio()
        for i in self.index_cols:
            res={}
            for j in self.asset_cols:
                E_ri=rfr+hedge_ratio.loc[f"{j}",f"{i}"]*(self.index_mean_daily.loc[i]-rfr)
                res[j]=E_ri
            E_rf[i]=res
        expected_returns=pd.DataFrame(E_rf)
        return expected_returns


if __name__=="__main__":
    asset_df=yf.download(tickers=['AXISBANK.NS','BAJAJ-AUTO.NS','BAJAJFINSV.NS','BEL.NS','BSE.NS','BHEL.NS','HAL.NS','SBIN.NS'],period='3y',interval='1d',auto_adjust=True)['Close']
    index_df=yf.download(tickers=['^NSEI','^BSESN'],period='3y',interval='1d',auto_adjust=True)['Close']
    a=EF_calc(PF_data=asset_df,index_data=index_df,PF_data_type='normal',PF_data_interval='daily',
              transform_data_type='returns',contain_index=True,transform=True)
    print(a.assets_prepared_data.shape,a.index_prepared_data.shape)
    print(a.base_calculations())
    print(a.calc_hedge_ratio())
    print(a.expected_daily_returns(rfr=0.0001428))
