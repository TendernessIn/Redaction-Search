import pymysql
import re

class MysqlManager:

    #数据库连接配置初始化
    def __init__(self):
        self.host = 'localhost'
        self.user = 'root'
        self.password = '123456'
        self.database = 'reterial'
        self.db = None
        self.dbcursor = None

    # 打开数据库连接,配置连接参数
    def connect_db(self):
        db = pymysql.connect(
            host = self.host,
            user = self.user,
            password = self.password,
            database = self.database)
        # 使用cursor()操作游标
        self.db = db
        self.dbcursor = db.cursor()

    # 关闭数据库连接
    def close_db(self):
        self.db.close()

    # 根据 若干个关键词hash值 在表一中查询对应 若干个文件向量并使用向量内积计算出结果向量
    def get_file_list(self, keyword_hash_list):
        self.connect_db()
        ret_vector = self.query_filevector(keyword_hash_list)
        # print('查询文件为:', self.query_ciphertext(ret_vector))
        return self.query_filevector(keyword_hash_list)

    def query_ciphertext(self, ret_vector):
        self.connect_db()
        ciphertext_list = []
        #根据结果向量获取文件的索引列表并存入indices
        indices = [i.start() for i in re.finditer('1', ret_vector)]
        # print('结果向量文件索引为:',indices)
        #在表二中根据索引找出对应的密文文件
        for index in indices:
            sql_query_ciphertext = ("select ciphertext from key1k_file1000w_2 where `index` = %s" % (index))
            self.dbcursor.execute(sql_query_ciphertext)
            ciphertext = self.dbcursor.fetchone()[0]
            ciphertext_list.append((ciphertext))
        return ciphertext_list

    def query_filevector(self, keyword_hash_list):
        self.connect_db()
        sql_query_file_vector = "select file_vector from key1k_file1000w where key_hash = '" + keyword_hash_list[0] + "' "
        for hash_value in keyword_hash_list[1:]:
            sql_query_file_vector +=  "or key_hash = '" + hash_value + "' "
        # print("查询的sql语句:",sql_query_file_vector)
        self.dbcursor.execute(sql_query_file_vector)
        file_vector_list = self.dbcursor.fetchall()
        ret_vector = int('1'*1001000,2)
        for temp in file_vector_list:
            # print(temp)
            file_vector = int(temp[0].decode(),2)
            ret_vector = ret_vector & file_vector
        return '{:01001000b}'.format(ret_vector)

    def insert_table1(self, keyword_hash, index):
        self.connect_db()

        sql_query_keyword_hash = ("select file_vector from key1k_file1000w where key_hash = '%s'" % (keyword_hash))
        self.dbcursor.execute(sql_query_keyword_hash)
        file_vector = self.dbcursor.fetchone()
        if file_vector == None:
            file_vector = '0'*1001000
            sql_insert_table1 = ("insert ignore into key1k_file1000w values('%s','%s', 0);" % (keyword_hash, file_vector))
            try:
                self.dbcursor.execute(sql_insert_table1)
                self.db.commit()
            except:
                print("Error: 插入失败")
        else:
            file_vector = file_vector[0].decode()
        file_vector = file_vector[0:index] + "1" + file_vector[index+1:]
        sql_update_file_vector = ("update key1k_file1000w set file_vector = '" + file_vector + "' where key_hash = '" + keyword_hash + "';")
        self.dbcursor.execute(sql_update_file_vector)
        self.db.commit()

        self.close_db()

    def insert_table2(self, ciphertext):
        self.connect_db()

        sql_querycipher = ("select `index` from key1k_file1000w_2 where ciphertext = '%s';" % (ciphertext))
        self.dbcursor.execute(sql_querycipher)
        index = self.dbcursor.fetchone()
        if index != None:
            print("该密文已存在,无需再次插入!")
            return index[0]
        else:
            sql_insert_table2 = ("insert into key1k_file1000w_2 values(0, '%s', 0);" % (ciphertext))
            print(sql_insert_table2)
            try:
                self.dbcursor.execute(sql_insert_table2)
                self.db.commit()
            except:
                print("Error: 插入失败")

            self.dbcursor.execute("select `index` from key1k_file1000w_2 where ciphertext = '%s'" % (ciphertext))
        #查询密文文件的索引并返回,用于table1的插入接口
        return self.dbcursor.fetchone()[0]

