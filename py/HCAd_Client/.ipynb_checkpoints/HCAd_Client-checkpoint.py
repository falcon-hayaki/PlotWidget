#!/usr/bin/env python3 
# -*- coding: utf-8 -*-

' a module for HCAd dataset client V1.4'

import pandas as pd
import numpy as np
import tablestore
import os
import json
import re

__author__ = 'Yixin Chen'



# 设置搜索条件用的函数
def priority(x):
    if x=='!':
        return 0
    elif x=='&&':
        return 1
    elif x =='||':
        return 2
    else:
        return 3
    
def standardize_seq(seq):
    # 删除空格
    seq = re.sub('\s*!\s*','!',seq)
    seq = re.sub('\s*\(\s*','(',seq)
    seq = re.sub('\s*\)\s*',')',seq)
    seq = re.sub('\s*&&\s*','&&',seq)
    seq = re.sub('\s*\|\|\s*','||',seq)   
    seq = re.sub('\s*==\s*','==',seq)
    seq = re.sub('\s*<>\s*','<>',seq)
    seq = re.sub('\s*>\s*','>',seq)
    seq = re.sub('\s*<\s*','<',seq)
    seq = re.sub('\s*>=\s*','>=',seq)
    seq = re.sub('\s*<=\s*','<=',seq)
    return seq

def forward2afterward(forward_seq):
    afterward_seq = []
    stack = []    
    for word in forward_seq:
        if word == '(':
            stack.append(word)
        elif word == ')':
            while(len(stack)!=0 and stack[-1]!='('):
                afterward_seq.append(stack.pop())
            if len(stack)!= 0:
                stack.pop()
            elif stack_top=='(':
                print("Bracket mismatch!")
                break
        elif word in ['||','&&','!']:
            while(len(stack)!=0 and priority(stack[-1])<=priority(word)):
                afterward_seq.append(stack.pop())
            stack.append(word)
        else:
            afterward_seq.append(word)
    while(len(stack)!=0):
        afterward_seq.append(stack.pop()) 
    return afterward_seq

def seq2boolquery_simple(seq):
    querys = []
    seq = standardize_seq(seq)
    constraints = re.split('&&',seq)
    for c in constraints:
        c_pair = c.split("==")
        querys.append(tablestore.TermQuery(c_pair[0], c_pair[1]))
    return tablestore.BoolQuery(must_queries=querys)


def seq2boolquery(metadata_condition):
    # 规范化表达式
    forward_seq = standardize_seq(metadata_condition)
    # 分词
    forward_seq = np.array(re.split('(\(|\)|\&&|\|\||!)',forward_seq))
    forward_seq = forward_seq[forward_seq!='']
    # 中序转后序
    afterward_seq = forward2afterward(forward_seq)
    # 后续转bool_query
    stack = []
    for word in afterward_seq:
        if word not in ['||','&&','!']:
            if "==" in word:
                w_pair = word.split("==")
                stack.append(tablestore.TermQuery(w_pair[0], w_pair[1]))
            elif "<>" in word:
                w_pair = word.split("<>")
                stack.append(tablestore.BoolQuery(must_not_queries=[tablestore.TermQuery(w_pair[0], w_pair[1])]))
        elif word =='!':
            stack.append(tablestore.BoolQuery(must_not_queries=[stack.pop()]))
        elif word =="&&":
            stack.append(tablestore.BoolQuery(must_queries=[stack.pop(),stack.pop()]))
        else:
            stack.append(tablestore.BoolQuery(should_queries=[stack.pop(),stack.pop()],minimum_should_match=1))
    return stack.pop()

def seq2filter(gene_condition):
    # 规范化表达式
    forward_seq = standardize_seq(gene_condition)
    # 分词
    forward_seq = np.array(re.split('(\(|\)|\&&|\|\||!)',forward_seq))
    forward_seq = forward_seq[forward_seq!='']
    # 中序转后序
    afterward_seq = forward2afterward(forward_seq)
    # 后续转bool_query
    stack = []
    for word in afterward_seq:
        if word not in ['||','&&','!']:
            if "==" in word:
                w_pair = word.split("==")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.EQUAL,pass_if_missing=False))
            elif "<>" in word:
                w_pair = word.split("<>")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.NOT_EQUAL,pass_if_missing=False))
            elif ">=" in word:
                w_pair = word.split(">=")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.GREATER_EQUAL,pass_if_missing=False))
            elif "<=" in word:
                w_pair = word.split("<=")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.LESS_EQUAL,pass_if_missing=False))
            elif ">" in word:
                w_pair = word.split(">")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.GREATER_THAN,pass_if_missing=False))
            elif "<" in word:
                w_pair = word.split("<")
                stack.append(tablestore.SingleColumnCondition(w_pair[0], float(w_pair[1]),tablestore.ComparatorType.LESS_THAN,pass_if_missing=False))
        elif word =='!':
            f = tablestore.CompositeColumnCondition(tablestore.LogicalOperator.NOT)
            f.add_sub_condition(stack.pop())
            stack.append(f)
        elif word =="&&":
            f = tablestore.CompositeColumnCondition(tablestore.LogicalOperator.AND)
            f.add_sub_condition(stack.pop())
            f.add_sub_condition(stack.pop())
            stack.append(f)
        else:
            f = tablestore.CompositeColumnCondition(tablestore.LogicalOperator.OR)
            f.add_sub_condition(stack.pop())
            f.add_sub_condition(stack.pop())
            stack.append(f)
    return stack.pop()



class HCAd_Client:
    _Ali_client = None
    
    def __init__(self):
        _client_setup = False
    
    def Setup_Client(self,endpoint, access_key_id, access_key_secret, instance_name, table_name):
        self._tablename = table_name 
        self._Ali_client =  tablestore.OTSClient(endpoint, access_key_id, access_key_secret, instance_name, logger_name = "table_store.log", retry_policy = tablestore.WriteRetryPolicy())
        self._client_setup = True
        
        try:
            describe_response = self._Ali_client.describe_table(self._tablename)
            print("Connected to the server, find the table.")
            
            print (table_name)
            print ('TableName: %s' % describe_response.table_meta.table_name)
            print ('PrimaryKey: %s' % describe_response.table_meta.schema_of_primary_key)
            print ('Reserved read throughput: %s' % describe_response.reserved_throughput_details.capacity_unit.read)
            print ('Reserved write throughput: %s' % describe_response.reserved_throughput_details.capacity_unit.write)
            print ('Last increase throughput time: %s' % describe_response.reserved_throughput_details.last_increase_time)
            print ('Last decrease throughput time: %s' % describe_response.reserved_throughput_details.last_decrease_time)
            print ('table options\'s time to live: %s' % describe_response.table_options.time_to_live)
            print ('table options\'s max version: %s' % describe_response.table_options.max_version)
            print ('table options\'s max_time_deviation: %s' % describe_response.table_options.max_time_deviation)
        except Exception as e:
            print(e)
    
    def _Cell2Row(self, sample, meta):
        # build the attribute columns part(metadata)
        attribute_columns =[]
        attribute_columns.append(('organ',str(meta['organ'])))
        attribute_columns.append(('region',str(meta['region'])))
        attribute_columns.append(('subregion',str(meta['subregion'])))
        attribute_columns.append(('seq_tech',str(meta['seq_tech'])))
        attribute_columns.append(('sample_status',str(meta['sample_status'])))
        attribute_columns.append(('donor_id',str(meta['donor_id'])))
        attribute_columns.append(('donor_gender',str(meta['donor_gender'])))
        attribute_columns.append(('donor_age',str(meta['donor_age'])))
        attribute_columns.append(('cluster_name',str(meta['original_name'])))
        attribute_columns.append(('cl_name',str(meta['cl_name'])))
        attribute_columns.append(('hcad_name',str(meta['hcad_name'])))
        # build the attribute columns part(gene)
        for i in range(sample.shape[0]):
            attribute_columns.append((sample.index[i],sample[i]))
        # build the primary_key part 
        primary_key = [('study_id',str(meta['study_id'])), ('cell_id',str(meta['cell_id'])),('user_id',int(meta['user_id']))]
        # the maxium number of attribute columns in each writing operation is 1024, so we split a row into blocks
        row_blocks = []
        for i in range(len(attribute_columns)//1024+1): # the maxium number of attribute columns in each writing operation is 1024
            if i==0:
                row_blocks.append(tablestore.Row(primary_key,attribute_columns[i*1024:min(i*1024+1024,len(attribute_columns))]))
            else:
                row_blocks.append(tablestore.Row(primary_key,{'PUT':attribute_columns[i*1024:min(i*1024+1024,len(attribute_columns))]}))
        return row_blocks
    
    
    def _insert_row(self,row):
        condition = tablestore.Condition(tablestore.RowExistenceExpectation.IGNORE)
        for i in range(len(row)):
            try :
                if (i==0):
                    consumed, return_row = self._Ali_client.put_row(self._tablename, row[i], condition)
                else:
                    consumed, return_row = self._Ali_client.update_row(self._tablename, row[i], condition)
            except tablestore.OTSClientError as e:
                print (e.get_error_message())
                return -1
            except tablestore.OTSServiceError as e:
                print (e.get_error_message())
                return -1
        return 0
        
    
    def insert_matrix(self, df_expression, df_annotation, genenum_chk=True, start_row = 0):
        if genenum_chk and df_expression.shape[0] != 43878:
            print("Gene number error.")
            return -1
        
        
        if sum([x in df_annotation.columns for x in ['user_id', 'study_id', 'cell_id', 'organ', 'region', 'subregion',
       'seq_tech', 'sample_status', 'donor_id', 'donor_gender', 'donor_age', 'original_name', 'cl_name', 'hcad_name']]) != 14:
            print("Metadata number error.")
            return -1
        
        if df_expression.shape[1]!=df_annotation.shape[0]:
            print("Cell number doesn't match.")
            return -1
        
        if (df_expression.columns!=df_annotation.index).any():
            print("Cell names or orders doesn't match.")
            return -1
        
        nrow = df_annotation.shape[0]-start_row
        nrow_slice = 10000
        
        for i in range(nrow // nrow_slice + 1):
            for j in range(nrow_slice):
                if nrow_slice * i + j == nrow:
                    break
                row = self._Cell2Row(df_expression.iloc[:,start_row + nrow_slice * i + j],df_annotation.iloc[start_row + nrow_slice * i + j,:])
                insert_stat = self._insert_row(row)
                if insert_stat == -1:
                    print(
                        "Error uploading data. An Error Occurred.\nCurrent row: {0}; Private Key: [('study_id', '{1}'), ('cell_id', '{2}'), ('user_id', '{3}')]"
                        .format(
                            nrow_slice * i + j,
                            df_annotation.iloc[start_row + nrow_slice * i + j, "study_id"],
                            df_annotation.iloc[start_row + nrow_slice * i + j, "cell_id"],
                            df_annotation.iloc[start_row + nrow_slice * i + j, "user_id"]
                        )
                    )
                    return -1*(start_row + nrow_slice * i + j)
                if nrow_slice * i + j % 50 == 0:
                    print('\rUploading：{0}{1}%'.format('▉'*(nrow_slice * i + j*30//df_annotation.shape[0]),(nrow_slice * i + j*100//df_annotation.shape[0])), end='')
        print('\rUploading：{0}{1}%'.format('▉'*(30),(100)), end='')    
        print("\r\n Upload finished. %d rows uploaded." % df_annotation.shape[0])
        return 1
        
        
        
    def build_index(self):
        index_list = self._Ali_client.list_search_index(self._tablename)
        if index_list and ('SampleTable', 'metadata')  in index_list:
            print("index already exist.")
        else:
            # create index
            field_uid = tablestore.FieldSchema('user_id',tablestore.FieldType.LONG, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_sid = tablestore.FieldSchema('study_id',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_organ = tablestore.FieldSchema('organ',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_region = tablestore.FieldSchema('region',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_subr = tablestore.FieldSchema('subregion',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_st = tablestore.FieldSchema('seq_tech',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_ss = tablestore.FieldSchema('sample_status',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_did = tablestore.FieldSchema('donor_id',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_did = tablestore.FieldSchema('donor_gender',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_da = tablestore.FieldSchema('donor_age',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_on = tablestore.FieldSchema('original_name',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_cn = tablestore.FieldSchema('cl_name',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)
            field_hn = tablestore.FieldSchema('hcad_name',tablestore.FieldType.KEYWORD, is_array = False, index = True, enable_sort_and_agg = True, store = True)

            fields = [field_uid, field_sid, field_organ, field_region, field_subr, field_st, field_ss, field_did, field_da, field_on, field_cn, field_hn]

            index_meta = tablestore.SearchIndexMeta(fields)
            self._Ali_client.create_search_index(self._tablename, "metadata", index_meta)
    
    
    def query_cells(self, metadata_conditions):
        
        query = seq2boolquery(metadata_conditions)
        
        # 查找主键
        results = []
        next_token = None
        total_cells = 0

        rows, next_token, total_count, is_all_succeed = self._Ali_client.search(
            self._tablename, "metadata", 
            tablestore.SearchQuery(query, next_token=next_token, limit=100, get_total_count=True), 
            tablestore.ColumnsToGet(return_type=tablestore.ColumnReturnType.NONE)
        )
        results += rows
        total_cells += total_count

        while next_token:# if not finished
            rows, next_token, total_count, is_all_succeed = self._Ali_client.search(
            self._tablename, "metadata", 
            tablestore.SearchQuery(query, next_token=next_token, limit=100, get_total_count=True), 
            tablestore.ColumnsToGet(return_type=tablestore.ColumnReturnType.NONE)  
            )
            results += rows
            total_cells += total_count
        print("%d cells found" %total_count)
        
        # 用主键获取行
        rows_to_get = [x[0] for x in results]
        
        return rows_to_get
    
    def get_columnsbycell(self,rows_to_get,cols_to_get=None,col_filter=None):
        request = tablestore.BatchGetRowRequest()
        df = []
        colnames = None
        for i in range(len(rows_to_get)//100+1):
            request.add(tablestore.TableInBatchGetRowItem(self._tablename, rows_to_get[i*100:i*100+99],cols_to_get,col_filter,1))
            try:
                got_rows = self._Ali_client.batch_get_row(request).get_succeed_rows()
                for row in got_rows:
                    if not row.row is None:
                        if colnames == None:
                            colnames = [x[0] for x in row.row.primary_key] + [x[0] for x in row.row.attribute_columns]
                        df.append([x[1] for x in row.row.primary_key] + [x[1] for x in row.row.attribute_columns])
            except tablestore.OTSClientError as e:
                print(e)
            except tablestore.OTSServiceError as e:
                print(e)
        if len(df)==0:
                print("no cell satisfy")
        else:
            df = pd.DataFrame(df)
            df.columns = colnames
            return df
        
    def get_column_set(self, col_to_get, col_filter=None):
        if(len(col_to_get) == 1):
            rows = self.get_all_rows(col_to_get)
            s = set()
            for row in rows:
                if len(row[1]):
                    s.add(row[1][0][1])
            return s
        else:
            print('ParameterLenthError: col_to_get must be a lenth 1 list.')
            return None
    
    def get_all_rows(self, cols_to_get = []):
        query = tablestore.MatchAllQuery()
        all_rows = []
        next_token = None
        col_return_type = tablestore.ColumnReturnType.ALL
        if cols_to_get:
            col_return_type = tablestore.ColumnReturnType.SPECIFIED

        while not all_rows or next_token:
            rows, next_token, total_count, is_all_succeed = self._Ali_client.search(self._tablename, 'metadata',
                tablestore.SearchQuery(query, next_token=next_token, limit=100, get_total_count=True),
                columns_to_get=tablestore.ColumnsToGet(cols_to_get, col_return_type))
            all_rows.extend(rows)

        print("%d cells found" %len(all_rows))

        return all_rows
    
    def update_row(self, primary_key, update_data):
    # primary_key 是主键，如[('study_id','10.1038/s41467-019-10756-2'), ('cell_id','human_control-AAACCTGAGCTGAAAT'),('user_id',3)]
    # updtae_data 是待更新的列的list，[(col1,val1),(col2,val2)]
        try:
            consumed, return_row, next_token = self._Ali_client.get_row(self._tablename, primary_key,columns_to_get=['donor_gender'])
            if return_row == None:
                print("Error! This row doesn't exist in the table.")
            else:
                # convert update data to blockes
                row = []
                for i in range(len(update_data)//1024+1): # the maxium number of attribute columns in each writing operation is 1024
                    row.append(tablestore.Row(primary_key,{'PUT':update_data[i*1024:min(i*1024+1024,len(update_data))]}))

                # try to update data
                condition = tablestore.Condition(tablestore.RowExistenceExpectation.IGNORE)
                for i in range(len(row)):
                    try :
                        consumed, return_row = self._Ali_client.update_row(self._tablename, row[i], condition)
                    except tablestore.OTSClientError as e:
                        print (e.get_error_message())
                    except tablestore.OTSServiceError as e:
                        print (e.get_error_message())

        except tablestore.OTSClientError as e:
            print (e.get_error_message()) 
        except tablestore.OTSServiceError as e:
            print (e.get_error_message())
            
            
    
    def update_batch(self, rows_to_update, update_sets):
        for i in range(len(rows_to_update)):
            primary_key = rows_to_update[i]
            update_data = update_sets[i] 
            self.update_row(primary_key, update_data)
