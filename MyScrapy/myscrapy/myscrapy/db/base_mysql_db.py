# -*- coding:utf-8 -*-
import logging
import pymysql
from DBUtils.PooledDB import PooledDB

from pymysql.converters import escape_string
from scrapy.utils.project import get_project_settings


class BaseMySQLDB(object):
    """ mysqldb 操作类"""

    def __init__(self):
        """ 数据库初始化 """
        settings = get_project_settings()
        self.host = str(settings.get("DB_HOST"))
        self.username = str(settings.get("DB_USER"))
        self.password = str(settings.get("DB_PASS"))
        self.database = str(settings.get("DB_NAME"))
        self.port = int(settings.get("DB_PORT"))
        self.log_sql = True

        self.connect()

    def connect(self):
        """ 链接数据库 """
        try:
            self.conn_pool = PooledDB(creator=pymysql,
                                      mincached=1,
                                      maxcached=2,
                                      maxconnections=4,
                                      blocking=True,
                                      user=self.username,
                                      passwd=self.password,
                                      db=self.database,
                                      host=self.host,
                                      port=self.port,
                                      charset="utf8mb4",
                                      cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            logging.error(e, exc_info=1)

    def close(self):
        """ 关闭数据库 """
        self.conn_pool.close()

    def selectAll(self, sql):
        """ 用于查询返回所有结果 """
        results = []
        conn = None
        cursor = None
        try:
            conn = self.conn_pool.connection()
            cursor = conn.cursor()
            if (self.log_sql):
                logging.debug(sql)
            cursor.execute(sql)
            results = cursor.fetchall()
        except Exception as e:
            logging.error(e, exc_info=1)
        finally:
            cursor.close()
            conn.close()

        return results

    def selectOne(self, sql):
        """ 查询一条结果 """
        result = None
        conn = None
        cursor = None
        try:
            conn = self.conn_pool.connection()
            cursor = conn.cursor()
            if (self.log_sql):
                logging.debug(sql)
            cursor.execute(sql)
            result = cursor.fetchone()
        except Exception as e:
            logging.error(e, exc_info=1)
        finally:
            cursor.close()
            conn.close()

        return result

    def _execute(self, sql, is_insert=False):
        """ 进行修改，插入，更新基本操作 """
        cursor = None
        conn = None
        rs = None;
        try:
            conn = self.conn_pool.connection()
            conn.begin()
            cursor = conn.cursor()
            if (self.log_sql):
                logging.debug(sql)
            cursor.execute(sql)
            if is_insert:
                cursor.execute("SELECT @@IDENTITY AS id")
                one = cursor.fetchone()
                rs = one['id']
            else:
                cursor.execute("SELECT row_count() AS count")
                one = cursor.fetchone()
                rs = one['count']
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(e, exc_info=1)
        finally:
            cursor.close()
            conn.close()

        return rs

    def insert(self, table, columns, replace=False):
        """ 执行插入mysql 操作 """
        functions = [
            'NOW()',
            'NULL'
        ]

        keys = columns.keys()

        data = []
        for key in keys:
            if columns[key] in functions:
                data.append(columns[key])
            else:
                data.append("'%s'" % escape_string(str(columns[key])))

        sql = "INSERT INTO"
        if replace:
            sql = "REPLACE INTO"

        sql = sql + " %s (%s) VALUES (%s)" % (table, ", ".join(keys), ", ".join(data))

        """ 执行插入mysql 操作 """
        return self._execute(sql, True)

    def replace(self, table, columns):
        self.insert(table, columns, True)

    def update(self, table, columns, where_sql):
        """ 执行更新mysql操作 """
        functions = [
            'NOW()',
            'NULL'
        ]

        keys = columns.keys()

        data = []
        for key in keys:
            if columns[key] in functions:
                data.append("%s = %s" % (key, columns[key]))
            else:
                data.append("%s = '%s'" % (key, escape_string(str(columns[key]))))

        sql = "UPDATE %s SET %s WHERE %s" % (table, ", ".join(data), where_sql)

        return self._execute(sql)

    def delete(self, sql):
        """ 执行删除mysql操作 """
        self._execute(sql)
