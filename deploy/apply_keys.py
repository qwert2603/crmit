keys_file = open('keys.txt')
lines = keys_file.read().splitlines()

secret_key = lines[1]
db_password = lines[3]
access_token_salt = lines[5]

keys_file.close()

path_to_config = '../cgi/config.py'

config_file_read = open(path_to_config)
config_file_content = config_file_read.read()
config_file_read.close()

config_file_content = config_file_content \
    .replace('<param_secret_key>', secret_key) \
    .replace('<param_db_password>', db_password) \
    .replace('<param_access_token_salt>', access_token_salt)

config_file_write = open(path_to_config, 'w')
config_file_write.write(config_file_content)
config_file_write.close()
