import records

if __name__ == '__main__':
    db = records.Database('sqlite:///data.db')
    db.query('CREATE TABLE suggestions (word text, date text, query text, rank int, suggestion_raw text, suggestion text)')
