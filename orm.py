#!/usr/bin/python2.4

import psycopg2
import datetime

class DB():
  class __DB():
    def __init__(self):
      dbname = 'name_extractor'
      host = 'localhost'
      user = 'postgres'
      password = '136452'
      self.conn = psycopg2.connect(
        "dbname='%s' user='%s' host='%s' password='%s'" 
        % (dbname, user, host, password)
      )
      self.cur = self.conn.cursor()

  instance = None
  def __init__(self):
    if not DB.instance:
      DB.instance = DB.__DB()

  def select_all(self, table_name):
    DB.instance.cur.execute('SELECT * FROM %s' % (table_name))
    rows = DB.instance.cur.fetchall()
    return rows

  def execute(self, query):
    DB.instance.cur = DB.instance.conn.cursor()
    DB.instance.cur.execute(query)
    DB.instance.conn.commit()

  def fetch(self):
    return DB.instance.cur.fetchall()

  def last_inserted_id(self, table_name):
    DB.instance.cur.execute("SELECT currval('" + table_name + "_id_seq')")
    rows = DB.instance.cur.fetchall()
    return int(rows[0][0])

class Entity():
  def __init__(self, values):
    self.values = values
    # for key in self.values:
    #   self.values[key] = self.values[key] or None
    if not 'id' in self.values:
      self.values['id'] = None

  @staticmethod
  def escape(text):
    return text.replace("'", "''")

  @classmethod
  def all(cls):
    field_str = ', '.join(cls.fields)
    DB().execute('SELECT (id, ' + field_str + ') FROM %s' % (cls.table_name))

    objs = []
    rows = DB().fetch()
    for row in rows:
      values = {}
      row = row[0][1:-1].split(',')
      for i in range(0, len(cls.fields)):
        values[cls.fields[i]] = row[i + 1] if row[i + 1] != '' else None
      obj = cls(values)
      obj.values['id'] = int(row[0])
      objs.append(obj)
    return objs

  @classmethod
  def create(cls, values):
    values_ = []
    for f in cls.fields:
      if not f in values or values[f] == None: 
        values_.append('NULL')
      else:
        values_.append("'" + Entity.escape(str(values[f])) + "'")

    field_str = ', '.join(cls.fields)
    value_str = ', '.join(values_)

    query = "INSERT INTO " + cls.table_name + " (" + field_str + ") VALUES (" + value_str + ")"
    DB().execute(query)
    obj = cls(values)
    obj.values['id'] = DB().last_inserted_id(cls.table_name)
    return obj

  @classmethod
  def find(cls, id):
    DB().execute('SELECT * FROM %s WHERE id = %d' % (cls.table_name, id))
    return DB().fetch()

  def update(self):
    if self.values['id'] == None:
      self.__class__.create(self.values)
      return

    values = []
    for f in self.__class__.fields:
      if not f in self.values or self.values[f] == None: 
        values.append(f + ' = NULL')
      else:
        values.append(f + " = '" + Entity.escape(str(self.values[f])) + "'")
    values = ", ".join(values)
    query = "UPDATE " + self.__class__.table_name + " SET " + values + ' WHERE id = ' + str(self.values['id'])
    DB().execute(query)

  def destroy(self):
    if self.values['id'] == None: return
    query = "DELETE FROM " + self.__class__.table_name + ' WHERE id = ' + str(self.values['id'])
    DB().execute(query)

  def __repr__(self):
    return str(self.values)

  def __str__(self):
    return str(self.values)

class DblpResearcher(Entity):
  table_name = 'dblp_researchers'
  fields = ['name', 'research_group_names']

  @staticmethod
  def find_by_name(name):
    field_str = ', '.join(DblpResearcher.fields)
    query = "SELECT (id, " + field_str + ") FROM " + DblpResearcher.table_name + " WHERE name = '" + Entity.escape(name) + "'"
    DB().execute(query)

    objs = []
    row = DB().fetch()
    if len(row) == 0: return None
    values = {}
    row = row[0][0][1:-1].split(',')
    for i in range(0, len(DblpResearcher.fields)):
      values[DblpResearcher.fields[i]] = row[i + 1] if row[i + 1] != '' else None
    obj = DblpResearcher(values)
    obj.values['id'] = int(row[0])
    return obj

class Researcher(Entity):
  table_name = 'researchers'
  fields = ['name', 'web_page_id', 'dblp_researcher_id']

class ResearchGroup(Entity):
  table_name = 'research_groups'
  fields = ['name', 'country', 'url']

  @staticmethod
  def find_by_url(url):
    field_str = ', '.join(ResearchGroup.fields)
    query = "SELECT (id, " + field_str + ") FROM " + ResearchGroup.table_name + " WHERE url = '" + Entity.escape(url) + "'"
    DB().execute(query)

    objs = []
    row = DB().fetch()
    if len(row) == 0: return None
    values = {}
    row = row[0][0][1:-1].split(',')
    for i in range(0, len(ResearchGroup.fields)):
      values[ResearchGroup.fields[i]] = row[i + 1] if row[i + 1] != '' else None
    obj = ResearchGroup(values)
    obj.values['id'] = int(row[0])
    return obj

class Url(Entity):
  table_name = 'urls'
  fields = ['url', 'scheduled_time', 'crawled', 'download_time', 'failed', 'domain', 'research_group_id']

  @staticmethod
  def find_by_url(url):
    field_str = ', '.join(Url.fields)
    query = "SELECT (id, " + field_str + ") FROM " + Url.table_name + " WHERE url = '" + Entity.escape(url) + "'"
    DB().execute(query)

    objs = []
    row = DB().fetch()
    if len(row) == 0: return None
    values = {}
    row = row[0][0][1:-1].split(',')
    for i in range(0, len(Url.fields)):
      values[Url.fields[i]] = row[i + 1] if row[i + 1] != '' else None
    obj = Url(values)
    obj.values['id'] = int(row[0])
    return obj

  @staticmethod
  def get_next_uncrawled_url():
    timestamp = str(datetime.datetime.utcnow())[:-7]

    field_str = ', '.join(Url.fields)
    query = "SELECT (id, " + field_str + ") FROM " + Url.table_name + \
            " WHERE crawled = FALSE AND (scheduled_time < TIMESTAMP '" + timestamp + \
            "' OR scheduled_time IS NULL) ORDER BY LENGTH(url) ASC LIMIT 1"
    DB().execute(query)

    objs = []
    rows = DB().fetch()
    for row in rows:
      values = {}
      row = row[0][1:-1].split(',')
      for i in range(0, len(Url.fields)):
        values[Url.fields[i]] = row[i + 1] if row[i + 1] != '' else None
      obj = Url(values)
      obj.values['id'] = int(row[0])
      objs.append(obj)

    if len(objs) > 0:
      return objs[0]
    else: 
      return None

class WebPage(Entity):
  table_name = 'web_pages'
  fields = ['content', 'is_faculty_repo', 'url_id']

  @staticmethod
  def find_by_url(url):
    field_str = ', '.join(WebPage.fields)
    query = "SELECT (web_pages.id, " + field_str + ") FROM " + WebPage.table_name + \
            " INNER JOIN urls ON (urls.id = web_pages.url_id) WHERE urls.url = '" + Entity.escape(url) + "'"
    DB().execute(query)

    objs = []
    row = DB().fetch()
    if len(row) == 0: return None
    values = {}
    row = row[0][0][1:-1].split(',')
    for i in range(0, len(WebPage.fields)):
      values[WebPage.fields[i]] = row[i + 1] if row[i + 1] != '' else None
    obj = WebPage(values)
    obj.values['id'] = int(row[0])
    return obj
