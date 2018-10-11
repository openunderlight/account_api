'''
Monthly guild drain script.
Should be added to crontab to run on the 1st of every month.
Released under the MIT License by the Open Underlight Project.
'''

from mysql.connector.cursor import MySQLCursorPrepared
from collections import defaultdict
from underlight_api.database import UnderlightDatabase

BASE_DRAIN = 100000
DRAIN_DISCOUNTS = [5000,3000,1000]
def get_guild_drains(db):
    cxn = db.connect(db = 'ul_player')    
    # count all players of type acct 80 (non-GMs) that don't have multi-guild membership
    # group them by rank
    stmt = '''select count(guildplayer.player_id),guild_id,rank from 
        guildplayer,player where 
            guildplayer.player_id = player.player_id and 
            player.acct_type=65 and 
            guildplayer.player_id not in (
                select distinct g1.player_id from guildplayer g1,guildplayer g2 where 
                    g1.player_id = g2.player_id and 
                    g1.guild_id != g2.guild_id
                ) 
            group by guild_id,rank
    '''
    cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
    cursor.execute(stmt)
    all = cursor.fetchall()    
    drains = defaultdict(lambda: BASE_DRAIN)
    # calculate the drain as BASE - discounts.
    for (cnt,guild,rank) in all:
        drains[guild] -= DRAIN_DISCOUNTS[rank - 1]
    return drains

def get_prime_info(db):
    cxn = db.connect(db = 'ul_item')
    # select all primes (prime type is 0xA, i.e. META_ESSENCE_FUNCTION)
    stmt = 'select item_id,item_name,x,y,owner_id,item_state1,item_state2,item_state3 from item where (item_state1 & 0x00FF00) >> 8 = 0xA'
    cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
    cursor.execute(stmt)
    all = cursor.fetchall()    
    ret = defaultdict(list)
    for (id,name,x,y,owner_or_level,s1,s2,s3) in all:
        # interpret the strings as hex, left padded to 32 bits with 0s
        state_strings = ["{0:0{1}x}".format(s,8) for s in [s1,s2,s3]]
        # flip the bytes around.
        strength_string = state_strings[1][6:] + state_strings[0][0:2] + state_strings[1][2:6]
        ess_string = state_strings[2][6:] + state_strings[1][0:2] + state_strings[2][2:6]
        guild = int(state_strings[0][2:4],16) & 0x0F
        ret[guild].append({
            'item_id': id,
            'name': name,
            'strength': int(strength_string, 16),
            'essences': int(ess_string, 16),
            'guild': guild,
            'state_strings': state_strings,            
        })        
    return ret

def write_primes(db,primes,drains):
    # we're only gonna bother with strength
    cxn = db.connect(db = 'ul_item')
    for guild,drain in drains.items():
        prime_list = primes.get(guild, None)
        if prime_list is None:
            print('ERROR: No prime found for guild %d' % guild)
            continue
        elif len(prime_list) > 1:
            print('WARN: More then one prime found for guild %d - draining from all!' % guild)
        
        for prime in prime_list:
            s = prime.get('strength', 0)
            s -= drain
            if s < 0:
                print('WARN: Prime %s (id: %d) for guild %d will underflow: setting to 0!' % (prime['name'], prime['item_id'], guild))
                s = 0
            strength_string = "{0:0{1}x}".format(s,8)
            state_strings = prime['state_strings']
            s0 = list(state_strings[0])
            s1 = list(state_strings[1])
            s1[6:] = strength_string[0:2]
            s0[0:2] = list(strength_string[2:4])
            s1[2:6] = list(strength_string[4:])
            state_strings[0] = ''.join(s0)
            state_strings[1] = ''.join(s1)
            print('INFO: Draining %s (old=%d;drain=%d;new=%d)' % (prime['name'], prime['strength'], drain, s))
            stmt = '''update item set item_state1=0x%s, item_state2=0x%s where item_id=%d''' % (state_strings[0], state_strings[1], prime['item_id'])
            print('EXECUTING: %s' % stmt)
            cursor = cxn.cursor(cursor_class=MySQLCursorPrepared)
            cursor.execute(stmt)
            cxn.commit()
            cursor.close()

if __name__ == '__main__':
    db = UnderlightDatabase.get()
    house_primes = get_prime_info(db)
    drains = get_guild_drains(db)
    write_primes(db,house_primes,drains)