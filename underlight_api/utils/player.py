import string
import random

# Constants
ACCT_ADMIN = 'A'
ACCT_KILLED = 'K'
ACCT_LOCKED = 'L'
ACCT_MONSTER = 'M'
ACCT_PLAYER = 'P'
ACCT_PMARE = 'S'
ACCT_ADMIN_EXPIRED = 'E'
ACCT_PLAYER_EXPIRED = 'X'

# Type to text
STATUS_DESCRIPTIONS = {
    ord(ACCT_ADMIN[0]): 'admin',
    ord(ACCT_KILLED[0]): 'killed',
    ord(ACCT_LOCKED[0]): 'locked',
    ord(ACCT_MONSTER[0]): 'agent',
    ord(ACCT_PLAYER[0]): 'player',
    ord(ACCT_PMARE[0]): 'pmare',
    ord(ACCT_ADMIN_EXPIRED[0]): 'expired_admin',
    ord(ACCT_PLAYER_EXPIRED[0]): 'expired_player',
}

def birth_arts_for_player(acct_type = ACCT_PLAYER, focus = None):
    if acct_type != ACCT_PMARE:
        return [
            'Join_Party',
            'Random',
            'Meditation',
            'Drain_Essence',
            'Trail',
            'Know',
            'Locate_Avatar',
            'Give', 
            'Show_Talisman',
            'Sense_Dreamers'
        ] + list(focal_birth_arts_for_player(focus))
    else:
        return [
            'Drain_Essence',
            'Show_Talisman',
            'Sense_Dreamers',
            'Shatter'
            # Abjure? I don't remember what else...
        ]

def focal_birth_arts_for_player(focus):
    if focus not in range(1,5):
        raise ValueError('Focus must be in range 1..4')
        
    if focus == 1:
        return ('Gatekeeper', 'Gatesmasher')
    elif focus == 2:
        return ('Dreamseer', 'Dreamblade')
    elif focus == 3:
        return ('Soulmaster', 'Soulreaper')
    elif focus == 4:
        return ('Fatesender', 'Fateslayer')

def birth_stats_for_player(focus):
    if focus not in range(1,5):
        raise ValueError('Focus must be in range 1..4')    
    stats = [10] * 5
    stats[0] = 20
    stats[focus] = 20
    return stats

def make_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))