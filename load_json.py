from TwitterStatsLib import TwitterJsonLoader

json_loader = TwitterJsonLoader()
json_loader.create_db()

with open('tweets/tweet.js', 'rb') as file_handle:
    json_loader.read_json_to_db(file_handle)
