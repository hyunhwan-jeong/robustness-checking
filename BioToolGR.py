# Made by Garam Factory

# This program is made for ease of data access on python environment.
# Users are recommended to run this program on ipython

import pandas as pd
import numpy as np
import random
from pandas import DataFrame

class BioToolGR:
    # This function parses a raw file from UC SANTA CRUZ("https://genome-cancer.ucsc.edu")
    # The format of files from UC SANTA CRUZ is usually text file
    # that numbers are separated by '\t' character.
    # Therefore, if you have a raw file not separted by '\t',
    # this function might not be useful.
    def parse(self,filename,header=None,index_col=None):
        return pd.read_csv(open(filename),sep='\t',index_col = index_col,header=header)
           
    # This function drops rows whose column name is parameter "name",
    # if the value of the column is NaN.
    def dropnabycolumn(self,data,name):
        return data[data[name].notnull()]

    def build_target_kernel(self,kernel,original,target_gene):
        filtered_kernel = pd.DataFrame()
        
        k = 0
        for index,row in original.iterrows():
            if not row.values[0] == target_gene.loc[k].values[0]:
                continue

            filtered_kernel = filtered_kernel.append(kernel.loc[index])
            k += 1
            if k == len(target_gene):
                break
            
        return filtered_kernel
    
    def write_csv(self,dataframe,filename):
        dataframe.to_csv(filename,sep='\t')

    def pick_random_columns(self,kernel,outcome,k,duplicated=True):
        num = 0
        bucket = []
        new_kernel = pd.DataFrame()
        new_outcome = pd.DataFrame(dtype=int)
        column_len = len(kernel.columns)
        
        while num < k:
            r = random.randint(0,column_len-1)
            if not duplicated:
                if r in bucket:
                    continue
                bucket.append(r)

            new_kernel = new_kernel.append(kernel.iloc[:,r])
            new_outcome = new_outcome.append(outcome.loc[r])
            num += 1
        
        return new_kernel,new_outcome
            

    # This function builds dataset for the program 'Net-Cox' 
    # 'genomicMatrix' and 'clinical_data' files are required for this function call
    # Data, SampleName,and GeneName are extracted from the file 'genomicMatrix'
    # d, and Times are extracted from the file 'clinical_data'
    # Also, the rows whose deviation is 0 are removed
    def build_netcox_dataset(self,output):
        data = self.parse('genomicMatrix')
        SampleName = data.columns[1:]
        GeneName = data['sample']
        Data = data.drop('sample',1)

        data = self.parse('clinical_data')

        d = []
        Times = []
        s = SampleName
        for i in s:
            k = data[data['sampleID'] == i]
            if np.isnan(k['_OS_IND'].values[0]) or np.isnan(k['_TIME_TO_EVENT'].values[0]):
                Data = Data.drop(i,1)
                SampleName = SampleName.drop(i)
            else:
                d.append(k['_OS_IND'].values[0])
                Times.append((k['_TIME_TO_EVENT'].values[0])/30)

        Data = Data[Data.std(1) > 0.0]

        Times = DataFrame(Times,index=SampleName)
        d = DataFrame(d,index=SampleName)
        
        # Sorting GenemicMatrix in order of Times
        Data = Data.append(Times.T,ignore_index=True)
        Data = Data.append(d.T,ignore_index=True)
        Data = Data.T
        Data = Data.sort_index(by=[len(Data.columns) - 1])
        Data = Data.T

        d = Data[-1:]
        d = d.T
        
        Data = Data[0:-1]

        Times = Data[-1:]
        Times = Times.T

        Data = Data[0:-1]

        SampleName = Data.columns
 
        import scipy.io 
        scipy.io.savemat(output,mdict={'Data':np.array(Data), 'GeneName':np.array(GeneName),'SampleName':np.array(SampleName), 'Times': np.array(Times), 'd': np.array(d)})
        return [Data,GeneName,SampleName,Times,d]
    #------------------------------------------------------------------------------


    # This is the process of what I have done for the Hyun-Hwan's order.
    # 2015-1-27
    def HyunOrder1(self,data):
        t = self.parse('clinical_data','sampleID')
        self.dropnabycolumn(t,'_OS_IND')
        data = data[((data['_OS_IND'] == 0) & (data['_OS'] > 1080)) | (data['_OS_IND'] == 1)]

    # This is the process of what I have done for the Hyun-Hwan's order.
    # 2015 2-23
    # This is the process of what I have done for the Hyun-Hwan's order.
    # Dataset is the file genomicMatrix from UC SANTA CRUZ("https://genome-cancer.ucsc.edu")
    # The purpose of this function is to build the dataset for fitting in 'Net-Cox' Program
    # 'Net-Cox' is Matlab Program, which requires a .mat file containing
    # m*n genomic matrix in the name of 'Data',
    # m*1 matrix of gene names in the name of 'GeneName',
    # n*1 matrix of sample names in the name of 'SampleName',
    # n*1 matrix of survival times in the name of 'Times',
    # n*1 matrix of survival indicator in the name of 'd',
    # In the .mat file, all the given variables must be set to run the program.
    # Therefore, HyunOrder2 builds the appropriate file with the dataset from
    # UC SANTA CRUZ.
    # And run the Net-Cox Program with the file
    def HyunOrder2(self,output):
        self.build_nextcox_set(output)

    # 2015 6-8
    def HynOrder3(self):
        METH = self.parse('METH.txt')
        CNA = self.parse('CNA.txt')
        mRNA = self.parse('mRNA.txt')
        sym = self.parse('sym.txt')
        target_gene = self.parse('target_gene.txt')
        outcome = pd.read_csv('clinical.txt',header=None)
        
        METH_filtered = self.build_target_kernel(METH,sym,target_gene)
        CNA_filtered = self.build_target_kernel(CNA,sym,target_gene)
        mRNA_filtered = self.build_target_kernel(mRNA,sym,target_gene)

        METH_name = "METH_filtered_random"
        CNA_name = "CNA_filtered_random"
        mRNA_name = "mRNA_filtered_random"
        clinical_name = "clinical"
        for i in range(100):
            METH_filtered_random,new_outcome = self.pick_random_columns(METH_filtered,outcome,int(len(CNA.columns)*9/10.0),False)
            CNA_filtered_random,new_outcome = self.pick_random_columns(CNA_filtered,outcome,int(len(CNA_filtered.columns)*9/10.0),False)
            mRNA_filtered_random,new_outcome = self.pick_random_columns(mRNA_filtered,outcome,int(len(mRNA_filtered.columns)*9/10.0),False)

            METH_filtered_random = METH_filtered_random.transpose()
            CNA_filtered_random = CNA_filtered_random.transpose()
            mRNA_filtered_random = mRNA_filtered_random.transpose()
        
            METH_filtered_random.to_csv(METH_name + str(i) + '.txt',sep='\t',index=False,header=False)
            CNA_filtered_random = CNA_filtered_random.astype(int)
            CNA_filtered_random.to_csv(CNA_name + str(i) + '.txt',sep='\t',index=False,header=False)
            mRNA_filtered_random.to_csv(mRNA_name + str(i) + '.txt',sep='\t',index=False,header=False)
        
            new_outcome = new_outcome.astype(int)
            new_outcome.to_csv(clinical_name + str(i) + '.txt',index=False,header=False)
