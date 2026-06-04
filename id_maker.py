from random import randrange

collision = 0

""" 与えられたIDリストに被らないようランダムなIDを生成 """
def make_id(id_list=[]):
    global collision
    client_id = hex(randrange(2**28,2**32))[2:]
    while client_id in id_list:
        collision += 1
        client_id = hex(randrange(2**28,2**32))[2:]
    return client_id

""" IDを生成し、IDリストに追加 """
def append_id(id_list):
    global collision
    client_id = hex(randrange(2**28,2**32))[2:]
    while client_id in id_list:
        collision += 1
        client_id = hex(randrange(2**28,2**32))[2:]
    id_list.append(client_id)
    return client_id

if __name__=="__main__":
    ids = []
    for t in range(10000):
        append_id(ids)
    print(make_id())
    print(collision)