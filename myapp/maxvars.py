# max vars for both web forms and database 
# sqlite doesn't care about the max var length, but left it here incase the database is changed from sqlite

class MaxVars():
    MAX_NAME: int = 100
    MAX_EMPLOYEE: int = 50
    MAX_EMAIL: int = 100
    MAX_PASS_HASH:int = 200
    MAX_PASS_STR:int = 100
    MIN_PASS_STR:int = 4

    MAX_SET_COMP_NAME:int = 20
    MAX_SET_EMAIL_SERVER:int = 50
    MAX_SET_EMAIL_SEND:int = 40
    MAX_SET_EMAIL_USER:int = 40
    MAX_SET_EMAIL_PASS:int = 40
    MAX_SET_EMAIL_PORT:int = 5

    MAX_PUNCH_NOTE:int = 50
    MAX_LAST_PUNCHES:int = 20

    MESSAGE: int = 100